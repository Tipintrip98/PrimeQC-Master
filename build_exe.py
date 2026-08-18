"""
Automated Build Script for PrimeQC Master using PyInstaller.
Compiles the application into a standalone Windows distribution folder (dist/PrimeQC).
"""

import os
import sys
import shutil
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def build():
    print("==================================================")
    print("      BUILDING PRIMEQC STANDALONE EXECUTABLE      ")
    print("==================================================")

    # Ensure assets exist
    if not os.path.isfile(os.path.join(BASE_DIR, "resources", "app_icon.ico")):
        print("Generating assets...")
        subprocess.run([sys.executable, os.path.join(BASE_DIR, "generate_assets.py")], check=True)

    dist_dir = os.path.join(BASE_DIR, "dist")
    out_app_dir = os.path.join(dist_dir, "PrimeQC")

    print("Cleaning previous build directories...")
    if os.path.isdir(out_app_dir):
        shutil.rmtree(out_app_dir, ignore_errors=True)

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name", "PrimeQC",
        "--icon", os.path.join(BASE_DIR, "resources", "app_icon.ico"),
        "--add-data", f"{os.path.join(BASE_DIR, 'bin')};bin",
        "--add-data", f"{os.path.join(BASE_DIR, 'resources')};resources",
        "--hidden-import", "PySide6",
        "--hidden-import", "PySide6.QtCore",
        "--hidden-import", "PySide6.QtGui",
        "--hidden-import", "PySide6.QtWidgets",
        "--hidden-import", "reportlab",
        "--hidden-import", "cv2",
        "--hidden-import", "numpy",
        os.path.join(BASE_DIR, "src", "main.py")
    ]

    print("Running PyInstaller with Python 3.14:")
    print(" ".join(cmd))

    proc = subprocess.run(cmd, cwd=BASE_DIR)
    if proc.returncode != 0:
        print("[FAIL] Build failed!")
        sys.exit(1)

    print("\n[OK] PyInstaller build completed successfully!")
    print(f"Standalone executable located at: {os.path.join(out_app_dir, 'PrimeQC.exe')}")


if __name__ == "__main__":
    build()
