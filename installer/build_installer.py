"""
Automated Build Script for PrimeQC_Setup.exe Installer.
Compresses the standalone distribution into a payload and compiles a single-file Setup Executable.
"""

import os
import sys
import shutil
import zipfile
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INSTALLER_DIR = os.path.join(BASE_DIR, "installer")


def create_payload_zip():
    app_dir = os.path.join(BASE_DIR, "dist", "PrimeQC")
    if not os.path.isdir(app_dir):
        print(f"[FAIL] Error: Application dist folder not found at: {app_dir}")
        print("Run build_exe.py first!")
        sys.exit(1)

    payload_path = os.path.join(INSTALLER_DIR, "payload.zip")
    print(f"Compressing {app_dir} -> {payload_path} ...")

    with zipfile.ZipFile(payload_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for root, dirs, files in os.walk(app_dir):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, app_dir)
                zf.write(abs_path, rel_path)

    print(f"[OK] Payload compressed successfully ({os.path.getsize(payload_path) / (1024*1024):.2f} MB)")
    return payload_path


def build_setup_exe():
    print("==================================================")
    print("       BUILDING PRIMEQC_SETUP.EXE INSTALLER       ")
    print("==================================================")

    payload_zip = create_payload_zip()

    icon_path = os.path.join(BASE_DIR, "resources", "app_icon.ico")
    installer_script = os.path.join(INSTALLER_DIR, "installer_gui.py")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name", "PrimeQC_Setup",
        "--icon", icon_path,
        "--add-data", f"{payload_zip};.",
        "--add-data", f"{icon_path};resources",
        "--hidden-import", "PySide6",
        "--hidden-import", "PySide6.QtCore",
        "--hidden-import", "PySide6.QtWidgets",
        "--hidden-import", "PySide6.QtGui",
        installer_script
    ]

    print("Running PyInstaller with Python 3.14 for installer:")
    print(" ".join(cmd))

    proc = subprocess.run(cmd, cwd=BASE_DIR)
    if proc.returncode != 0:
        print("[FAIL] Installer compilation failed!")
        sys.exit(1)

    setup_exe = os.path.join(BASE_DIR, "dist", "PrimeQC_Setup.exe")
    print(f"\n[OK] Dedicated Installer generated successfully at:\n{setup_exe}")


if __name__ == "__main__":
    build_setup_exe()
