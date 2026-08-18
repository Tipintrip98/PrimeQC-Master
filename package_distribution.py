"""
PrimeQC Master - Universal Windows Distribution Packaging Suite.
Packages complete self-contained standalone installers, portable ZIP packages,
and documentation for deployment on any Windows 10 / 11 64-bit PC without prerequisites.
"""

import os
import sys
import shutil
import zipfile
import hashlib
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(BASE_DIR, "dist")
APP_DIR = os.path.join(DIST_DIR, "PrimeQC")


def compute_sha256(filepath):
    """Computes SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def create_portable_zip():
    """Packages the standalone application directory into a release portable ZIP."""
    if not os.path.isdir(APP_DIR):
        print(f"[FAIL] Error: {APP_DIR} not found. Run build.py first!")
        return None

    zip_filename = "PrimeQC_v2.5_Windows_Portable_x64.zip"
    zip_path = os.path.join(DIST_DIR, zip_filename)
    print(f"\nCreating Portable Release Package: {zip_path} ...")

    # Include a handy root batch launcher inside the zip
    launcher_bat_content = (
        "@echo off\r\n"
        "title PrimeQC Master - Amazon Prime Video QC Suite\r\n"
        "start \"\" \"%~dp0PrimeQC\\PrimeQC.exe\"\r\n"
        "exit\r\n"
    )
    launcher_temp = os.path.join(DIST_DIR, "Avvia_PrimeQC.bat")
    with open(launcher_temp, "w", encoding="utf-8") as f:
        f.write(launcher_bat_content)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        zf.write(launcher_temp, "Avvia_PrimeQC.bat")
        for root, dirs, files in os.walk(APP_DIR):
            for file in files:
                abs_p = os.path.join(root, file)
                rel_p = os.path.join("PrimeQC", os.path.relpath(abs_p, APP_DIR))
                zf.write(abs_p, rel_p)

    if os.path.isfile(launcher_temp):
        os.remove(launcher_temp)

    size_mb = os.path.getsize(zip_path) / (1024 * 1024)
    print(f"[OK] Portable ZIP created: {zip_filename} ({size_mb:.2f} MB)")
    return zip_path


def create_distribution_docs():
    """Creates clear instructions and release notes for other Windows users."""
    doc_path = os.path.join(DIST_DIR, "ISTRUZIONI_INSTALLAZIONE_WINDOWS.txt")
    content = (
        "===============================================================================\r\n"
        "     PRIMEQC MASTER v2.5 - SUITE QUALITY CONTROL AMAZON PRIME VIDEO           \r\n"
        "            GUIDA DI INSTALLAZIONE E DISTRIBUZIONE WINDOWS                     \r\n"
        "===============================================================================\r\n\r\n"
        "Questo pacchetto di distribuzione contiene tutto il necessario per eseguire il \r\n"
        "software PrimeQC Master su qualsiasi PC con Windows 10 o Windows 11 (64-bit).\r\n\r\n"
        "CARATTERISTICHE DELLA DISTRIBUZIONE:\r\n"
        "- 100% Autonomo (Self-Contained): Nessun bisogno di Python o codec esterni.\r\n"
        "- Motori FFmpeg 7.1 Broadcast integrati con filtri ITU-R BS.1770-4 ed EBU R128.\r\n"
        "- Interfaccia grafica nativa PySide6 Qt6 ad alta risoluzione (High-DPI).\r\n"
        "- Generatore di certificati PDF ufficiali e conformità Prime Video Direct / Studios.\r\n\r\n"
        "-------------------------------------------------------------------------------\r\n"
        "MODALITÀ DI INSTALLAZIONE:\r\n"
        "-------------------------------------------------------------------------------\r\n\r\n"
        "OPZIONE 1: INSTALLER AUTOMATICO GUIDATO (CONSIGLIATO)\r\n"
        "1. Fare doppio click sul file: PrimeQC_Setup.exe\r\n"
        "2. Seguire la procedura guidata (scegliere la cartella di destinazione).\r\n"
        "3. Verranno create automaticamente le icone sul Desktop e nel Menu Start.\r\n"
        "4. Avviare 'PrimeQC Master' direttamente dal Desktop.\r\n\r\n"
        "OPZIONE 2: VERSIONE PORTATILE (PORTABLE ZIP - SENZA INSTALLAZIONE)\r\n"
        "1. Estrarre il file 'PrimeQC_v2.5_Windows_Portable_x64.zip' in una cartella a piacere\r\n"
        "   (es. su C:\\, sul Desktop o su una chiavetta USB).\r\n"
        "2. Fare doppio click su 'Avvia_PrimeQC.bat' oppure su 'PrimeQC\\PrimeQC.exe'.\r\n\r\n"
        "-------------------------------------------------------------------------------\r\n"
        "REQUISITI DI SISTEMA:\r\n"
        "- Sistema Operativo: Windows 10 / Windows 11 (64-bit)\r\n"
        "- RAM: Minimo 4 GB (Consigliati 8 GB+ per video 4K)\r\n"
        "- Spazio su Disco: 600 MB liberi\r\n"
        "- Scheda Video: Qualsiasi GPU compatibile DirectX 11 / OpenGL 3.3+\r\n\r\n"
        "===============================================================================\r\n"
        "Sviluppato da: DECA VFX / Advanced Engineering Team\r\n"
        "Data di Rilascio: 18 Agosto 2026\r\n"
        "===============================================================================\r\n"
    )
    with open(doc_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[OK] Distribution guide written to: {doc_path}")
    return doc_path


def main():
    print("=================================================================")
    print("      PRIMEQC MASTER - UNIVERSAL WINDOWS DISTRIBUTION BUILDER    ")
    print("=================================================================")

    # 1. Build app and setup if not already built
    setup_exe = os.path.join(DIST_DIR, "PrimeQC_Setup.exe")
    app_exe = os.path.join(APP_DIR, "PrimeQC.exe")

    if not os.path.isfile(app_exe) or not os.path.isfile(setup_exe):
        print("Executables not found. Triggering full build.py ...")
        subprocess.run([sys.executable, os.path.join(BASE_DIR, "build.py")], check=True)

    # 2. Package Portable ZIP
    zip_path = create_portable_zip()

    # 3. Create distribution documentation
    doc_path = create_distribution_docs()

    # 4. Generate Checksums Manifest
    manifest_path = os.path.join(DIST_DIR, "RELEASE_CHECKSUMS_SHA256.txt")
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write("PrimeQC Master v2.5 - Windows Release Checksums (SHA-256)\n")
        f.write("=" * 60 + "\n\n")
        if os.path.isfile(setup_exe):
            f.write(f"{compute_sha256(setup_exe)}  PrimeQC_Setup.exe\n")
        if zip_path and os.path.isfile(zip_path):
            f.write(f"{compute_sha256(zip_path)}  {os.path.basename(zip_path)}\n")

    print(f"[OK] Release checksums generated at: {manifest_path}")

    print("\n=================================================================")
    print("          DISTRIBUTION PACKAGES GENERATED SUCCESSFULLY!          ")
    print("=================================================================")
    print(f"1. Setup Installer (Setup.exe): {setup_exe}")
    print(f"2. Portable Package (ZIP):      {zip_path}")
    print(f"3. Guida Distribuzione (TXT):   {doc_path}")
    print("=================================================================")


if __name__ == "__main__":
    main()
