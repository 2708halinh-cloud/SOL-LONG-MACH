# Unleashed Firmware — source archive tool

**SOURCE_DIRECT:** `unleashed-firmware-dev.zip`, uploaded by the user on 2026-10-17. This is the **Flipper Zero Unleashed Firmware** development-source snapshot (upstream `DarkFlippers/unleashed-firmware`), not a website editor or a ready-to-flash firmware image. The original archive is preserved separately in ChatGPT Library, in this exact tool directory.

## Executable entry point

Requires Python 3.10+ standard library; no network access, API token or authentication:

```sh
python unleashed_source.py /path/to/unleashed-firmware-dev.zip
python unleashed_source.py /path/to/unleashed-firmware-dev.zip --extract-to /new/empty/directory
```

The tool verifies SHA-256, ZIP CRC, member count and safe paths before optional extraction. It does **not** compile firmware, flash a device, or transmit/receive Sub-GHz signals.

## Source receipt

- ZIP SHA-256: `d0c5c75f790695ccc3b3fccb047a72b454d6694683625cc423114581c61be00f`
- Archive members (files + directories): `5482`
- Uncompressed size: `57,839,630` bytes; ZIP size: `20,245,387` bytes
- CRC: PASS; unsafe traversal paths: 0; symlink members: 0 (observed from provided ZIP)
- Top-level source folder: `unleashed-firmware-dev/`; contains `ReadMe.md`, `LICENSE` (GNU GPLv3), `fbt`, `fbt.cmd`, `.gitmodules` and firmware source code.
- The ZIP alone is not proof of a complete build environment: `fbt` expects Git submodules and a toolchain, and the source archive is not a running MCP/ChatGPT plugin.

**Carrier distinction:** GitHub stores this working inspection utility and provenance files. **The 20 MB source ZIP itself is held in the equivalent ChatGPT Library folder** and is identified by the SHA-256 above; the original binary has not been uploaded to GitHub. Keep attribution and upstream license when redistributing modified source. Integration with X-TiME-Web / `gambbrazil.fun` is **not implied**.
