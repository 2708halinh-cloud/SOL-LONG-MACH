---
name: pcxt-bios-workbench
description: Inspect PC/XT BIOS 3.1 Assembly configuration and ROM image metadata with read-only Python, reporting checksums and compatibility limits; use for Intel 8088/NEC V20 BIOS investigation, never for automatic flashing.
compatibility: Python 3.9+ for source and ROM inspection. Real ROM build requires separately verified assembler and archive.
---
# PCXT BIOS Workbench — OS_WORK binding

Installed source skill: `skills://plugins/pcxt-bios-workbench/pcxt-bios-workbench/skill.md`.
Authoritative original source reference: `skills://plugins/pcxt-bios-workbench/pcxt-bios-workbench/references/pcxtbios.asm`.

## Operational workflow
1. Identify target (IBM 5150/5160 or clone), ROM source/image and action (inspection only by default).
2. Read `SOURCE_NOTES.md` and `pcxtbios.asm` from the installed plugin; do not invent a ROM file when absent.
3. Run local `scripts/inspect_rom.py <image.bin>` on a real supplied image when it exists. It measures size, SHA-256, modulo-256 byte sum and extension-ROM signature.
4. For BIOS configuration, use the installed `scripts/inspect_source.py` against a verified local copy of `pcxtbios.asm`.
5. Record image hashes and results. Passing a checksum does not establish bootability. Never write/flash EPROM or start emulation as a side effect of inspection.

## OAuth boundary
This BIOS analyzer has no Google OAuth dependency. The requested OAuth client file must NOT be copied here or used as an input.

## Self-test
`python3 scripts/selftest.py` uses synthetic data to test the ROM analyzer. It does **not** certify real BIOS execution or hardware compatibility.
