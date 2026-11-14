# Registry Editor → COMPUTER KHÍ / năm Stone

- UI node: `Computer` is a **virtual Registry Editor root**, not a Windows registry hive. In SOL this corresponds to `COMPUTER_KHÍ💜BRAIN_OS_POWER` (POWER 🟣).
- Under Windows Registry Editor are five visible standard hive roots: `HKEY_CLASSES_ROOT`, `HKEY_CURRENT_USER`, `HKEY_LOCAL_MACHINE`, `HKEY_USERS`, `HKEY_CURRENT_CONFIG`.
- Source for root insertion: [ReactOS regedit treeview.c lines 410–414](https://github.com/reactos/reactos/blob/master/base/applications/regedit/treeview.c#L410-L414); this is **open ReactOS source**, not Microsoft's Windows `regedit.exe` source.
- The five hive labels are mapped to five existing SOL Stone folders **as architectural links**, not registry writes. Avoid making five independent copies of underlying Windows registry storage: HKCR merges user and machine classes, HKCU aliases the active user's hive in HKU, HKCC reflects current hardware profile under HKLM.

| Hive | SOL Stone | Meaning in this registry map |
|---|---|---|
| HKCR | SPACE 🔵 | Classes, file type associations, COM namespace |
| HKCU | MIND 🟡 | Current-user preferences and context |
| HKLM | REALITY 🔴 | System-wide runtime and machine configuration |
| HKU | SOUL 🟠 | Loaded identity/profile hives and source/provenance |
| HKCC | TIME 🟢 | Configuration current at observation instant, NOT event history |

Canonical map: `COMPUTER_KHÍ💜BRAIN_OS_POWER/CORE_PLACES_INDEX_MÁU_🔴_HỎA_REALITY/WINDOWS_REGISTRY_EDITOR_HIVES_CURRENT.json`. Each of five SOL Stone folders has one `REGISTRY_HIVE_BINDING_CURRENT.json`. `registry_hive_router.py` resolves aliases for callers. No live Windows registry operation is claimed.

`@XIAOMI GHI CHÚ` is indexed in the two SOL Tools routers separately; Android ACTION_SEND was exercised against `com.miui.notes` and user supplied UI confirmation. It is not an HTTP REST API and database persistence is not inferred just from UI opening.

To test in the repository checkout: `python -m unittest discover -s 'CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/tools/Chuỗi công cụ/_Dụng cụ/Registry_Editor_SOL' -p 'test_registry_hive_router.py' -v`.
