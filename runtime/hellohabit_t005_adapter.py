#!/usr/bin/env python3
"""T005 / HelloHabit Android split adapter: evidence-only source registration.

T005 is a TESSERACT temporal-continuity lane, not proof of a HelloHabit
account integration. This adapter consumes the user-provided config.xxhdpi
manifest, validates its exact identity and models future device events
without inventing installed APKs, auth or personal habit data.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

BINDING="integrations/android/hellohabit/manifest.binding.json"
PACKAGE="com.studio.hellohabit"
SPLIT="config.xxhdpi"
VERSION=572

def inspect(root: Path)->dict:
    p=root/BINDING
    raw=p.read_bytes()
    binding=json.loads(raw.decode("utf-8"))
    manifest=binding["user_supplied_manifest"]["manifest"]
    app=binding["user_supplied_manifest"]["application"]
    meta=binding["user_supplied_manifest"]["meta_data"]
    assert manifest["package"]==PACKAGE, "PACKAGE_MISMATCH"
    assert manifest["split"]==SPLIT, "SPLIT_MISMATCH"
    assert manifest["versionCode"]==str(VERSION), "VERSION_MISMATCH"
    assert manifest["splitTypes"]=="base__density", "DENSITY_SPLIT_MISMATCH"
    assert app["hasCode"] is False, "CODE_MISMATCH"
    assert app["extractNativeLibs"] is False, "NATIVE_LIBRARY_MISMATCH"
    assert meta["name"]=="com.android.vending.derived.apk.id", "METADATA_MISMATCH"
    assert meta["value"]=="3", "METADATA_VALUE_MISMATCH"
    # Guard against upgrading a manifest pointer to an installed/API claim.
    assert binding["android_apk_installed"] is False
    assert binding["app_api_authenticated"] is False
    assert binding["habit_data_accessed"] is False
    return {
        "schema":"TESSERACT_T005_HELLOHABIT_BINDING_RECEIPT/1",
        "carrier":BINDING,
        "source_sha256":hashlib.sha256(raw).hexdigest(),
        "package":PACKAGE,
        "split":SPLIT,
        "version_code":VERSION,
        "has_code":False,
        "STAMP_OLD":"USER_DIRECT_MANIFEST_SOURCE_VERIFIED_IN_REPOSITORY",
        "STAMP_LIVE":"INDEPENDENT_CLOUD_CODE_VALIDATED_SPLIT_METADATA",
        "STAMP_BETA":"DEVICE_PACKAGE_MANAGER_AND_BASE_APK_REQUIRED_FOR_APP_INSTALL",
        "installed_on_android_proven":False,
        "T005_package_identity_registered":True,
        "real_habit_data_sync_proven":False,
        "provider_permissions_bypassed":False
    }

def main()->None:
    a=argparse.ArgumentParser()
    a.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    args=a.parse_args()
    print(json.dumps(inspect(args.root),ensure_ascii=False))

if __name__=="__main__":main()
