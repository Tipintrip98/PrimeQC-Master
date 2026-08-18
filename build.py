"""
Master Build and Distribution Orchestrator for PrimeQC Suite.
Runs tests, builds the standalone application, and generates the dedicated setup installer.
"""

import os
import sys
import subprocess


def main():
    print("=================================================================")
    print("        PRIMEQC MASTER - AMAZON PRIME VIDEO QC BUILDER           ")
    print("=================================================================")

    # 1. Run Unit Tests
    print("\n[1/3] Running Unit Test Suite...")
    test_proc = subprocess.run([sys.executable, "tests/test_engine.py"])
    if test_proc.returncode != 0:
        print("[FAIL] Unit tests failed! Aborting build.")
        sys.exit(1)
    print("[OK] Unit tests passed!")

    # 2. Build Standalone App (dist/PrimeQC)
    print("\n[2/3] Building Standalone Executable (PyInstaller)...")
    app_proc = subprocess.run([sys.executable, "build_exe.py"])
    if app_proc.returncode != 0:
        print("[FAIL] App build failed! Aborting.")
        sys.exit(1)

    # 3. Build Setup Installer (dist/PrimeQC_Setup.exe)
    print("\n[3/3] Building Dedicated Setup Installer (PrimeQC_Setup.exe)...")
    inst_proc = subprocess.run([sys.executable, "installer/build_installer.py"])
    if inst_proc.returncode != 0:
        print("[FAIL] Installer build failed! Aborting.")
        sys.exit(1)

    print("\n=================================================================")
    print("                   BUILD COMPLETE SUCCESSFULLY!                  ")
    print("=================================================================")
    print(f"1. Standalone Application Directory:  {os.path.abspath('dist/PrimeQC')}")
    print(f"2. Standalone Application EXE:        {os.path.abspath('dist/PrimeQC/PrimeQC.exe')}")
    print(f"3. Dedicated Setup Installer EXE:     {os.path.abspath('dist/PrimeQC_Setup.exe')}")
    print("=================================================================\n")


if __name__ == "__main__":
    main()
