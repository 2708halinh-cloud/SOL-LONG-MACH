//! READ-ONLY measurements for the registered local runtime. No file contents or credentials.
use crate::{ensure_scoped, RuntimeState};
use serde_json::{json, Value};
use std::{
    collections::hash_map::DefaultHasher,
    env, fs,
    hash::{Hash, Hasher},
    path::Path,
    time::{SystemTime, UNIX_EPOCH},
};
use tauri::State;

const MAX_TOP_LEVEL_ENTRIES: usize = 512;

fn dir_summary(path: &Path) -> Value {
    if !path.is_dir() {
        return json!({"status":"UNAVAILABLE","entries":0});
    }
    let entries = match fs::read_dir(path) {
        Ok(items) => items,
        Err(_) => return json!({"status":"ACCESS_DENIED","entries":0}),
    };
    let mut fingerprints = Vec::new();
    let mut count = 0usize;
    let mut truncated = false;
    let mut errors = 0usize;
    for item in entries {
        if count >= MAX_TOP_LEVEL_ENTRIES { truncated = true; break; }
        match item {
            Ok(item) => {
                // The name is used only inside a local hash, never returned or persisted.
                let mut hasher = DefaultHasher::new();
                item.file_name().hash(&mut hasher);
                match fs::symlink_metadata(item.path()) {
                    Ok(meta) => {
                        meta.len().hash(&mut hasher);
                        meta.is_dir().hash(&mut hasher);
                        if let Ok(time) = meta.modified() {
                            if let Ok(delta) = time.duration_since(UNIX_EPOCH) {
                                delta.as_nanos().hash(&mut hasher);
                            }
                        }
                    }
                    Err(_) => { errors += 1; }
                }
                fingerprints.push(hasher.finish());
                count += 1;
            }
            Err(_) => { errors += 1; }
        }
    }
    fingerprints.sort_unstable();
    let mut hasher = DefaultHasher::new();
    fingerprints.hash(&mut hasher);
    json!({"status": if truncated {"PARTIAL"} else {"CONNECTED"},
           "entries":count, "fingerprint":format!("{:016x}",hasher.finish()),
           "errors":errors, "scope":"ONE_LEVEL_METADATA_ONLY"})
}

fn parse_linux_meminfo(raw: &str) -> Option<(u64,u64)> {
    let mut total = None;
    let mut available = None;
    for line in raw.lines() {
        let mut parts = line.split_ascii_whitespace();
        match parts.next()? {
            "MemTotal:" => total = parts.next().and_then(|v| v.parse::<u64>().ok()),
            "MemAvailable:" => available = parts.next().and_then(|v| v.parse::<u64>().ok()),
            _ => {}
        };
    }
    match (total,available) {
        (Some(t),Some(a)) if t > 0 && a <= t => Some((t,a)),
        _ => None
    }
}

fn ram_summary() -> Value {
    #[cfg(target_os="linux")]
    {
        if let Ok(raw) = fs::read_to_string("/proc/meminfo") {
            if let Some((total,available)) = parse_linux_meminfo(&raw) {
                return json!({"status":"CONNECTED", "total_kib": total,
                    "used_kib":total-available, "available_kib":available,
                    "scope":"HOST_MEMORY_AGGREGATE"});
            }
        }
    }
    json!({"status":"UNAVAILABLE","scope":"HOST_MEMORY_AGGREGATE"})
}

#[tauri::command]
pub(crate) fn ambient_snapshot(
    workspace: Option<String>,
    runtime: State<'_, RuntimeState>,
) -> Result<Value, String> {
    let scoped = match workspace {
        Some(ref w) if !w.is_empty() => Some(ensure_scoped(&runtime,w)?),
        _ => None
    };
    let workspace_data = scoped.as_ref()
        .map(|p| dir_summary(p))
        .unwrap_or_else(|| json!({"status":"NO_WORKSPACE"}));
    // This is the runtime host's /mnt/data, never automatically the assistant sandbox.
    let mnt_data = if Path::new("/mnt/data").is_dir() {
        dir_summary(Path::new("/mnt/data"))
    } else {
        json!({"status":"NOT_PRESENT_ON_THIS_HOST"})
    };
    let now = SystemTime::now().duration_since(UNIX_EPOCH)
        .map(|v| v.as_millis() as u64).unwrap_or_default();
    Ok(json!({
        "schema":"SOL_AMBIENT_SNAPSHOT/1.0","observed_at_ms":now,
        "ram":ram_summary(),
        "host_temp":dir_summary(&env::temp_dir()),
        "workspace":workspace_data,
        "mnt_data":mnt_data,
        "platform_memory":{"status":"UNCONNECTED","reason":"NO_PLATFORM_MEMORY_API"},
        "chrome_cdp":{"status":"UNCONNECTED","reason":"CDP_BRIDGE_NOT_CONFIGURED"},
        "policy":"LOCAL_READ_ONLY_METADATA_NO_CONTENT_NO_NETWORK"
    }))
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn meminfo_parser_requires_consistent_bounds() {
        assert_eq!(parse_linux_meminfo("MemTotal: 1024 kB\nMemAvailable: 512 kB\n"),Some((1024,512)));
        assert_eq!(parse_linux_meminfo("MemTotal: 4 kB\nMemAvailable: 10 kB\n"),None);
    }
    #[test]
    fn directory_summary_does_not_expose_filenames_or_file_contents() {
        let d=env::temp_dir().join(format!("ambient-test-{}",std::process::id()));
        let _=fs::remove_dir_all(&d);
        fs::create_dir(&d).expect("test folder");
        fs::write(d.join("SENSITIVE_FILENAME_token.txt"),"SECRET_VALUE").expect("test file");
        let result=dir_summary(&d).to_string();
        assert_eq!(serde_json::from_str::<Value>(&result).unwrap()["entries"],1);
        assert!(!result.contains("SENSITIVE_FILENAME"));
        assert!(!result.contains("SECRET_VALUE"));
        fs::remove_dir_all(d).expect("cleanup");
    }
}
