import os
import sys
import platform
import requests
import tarfile
import zipfile
import shutil
import logging
from pathlib import Path
from platformdirs import user_data_dir
from .constants import APP_NAME, BIN_NAME, CLI_VERSION, BASE_URL

logger = logging.getLogger(__name__)

class CLIManager:
    """Manages the download and installation of the underlying CLI binary."""
    
    def __init__(self, app_name: str = APP_NAME, bin_name: str = BIN_NAME, version: str = CLI_VERSION):
        self.app_name = app_name
        self.bin_name = bin_name
        self.version = version
        self.data_dir = Path(user_data_dir(self.app_name))
        self.bin_dir = self.data_dir / "bin"
        self.bin_path = self.bin_dir / self.bin_name

    def get_platform_info(self):
        system = platform.system().lower()
        arch = platform.machine().lower()
        
        # Normalize linux architectures
        if system == "linux":
            if arch == "x86_64":
                arch = "x86_64"
            elif arch in ["aarch64", "arm64"]:
                arch = "aarch64"
        elif system == "darwin":
            system = "macos"
            arch = "universal2"
            
        return system, arch

    def get_download_url(self):
        system, arch = self.get_platform_info()
        ext = "tar.gz" if system == "linux" else "zip"
        
        # Example: sc-v0.1.0-linux-x86_64-gnu.tar.gz
        # Example: sc-v0.1.0-macos-universal2.zip
        fmt = f"{system}-{arch}-gnu" if system == "linux" else f"{system}-{arch}"
        filename = f"sc-{self.version}-{fmt}.{ext}"
        
        return f"{BASE_URL}/{self.version}/{filename}"

    def is_installed(self):
        return self.bin_path.exists() and os.access(self.bin_path, os.X_OK)

    def download_and_install(self):
        """Downloads and extracts the CLI binary."""
        self.bin_dir.mkdir(parents=True, exist_ok=True)
        url = self.get_download_url()
        
        logger.info(f"Downloading Scalable CLI from {url}...")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        tmp_archive = self.data_dir / f"download.{'tar.gz' if 'tar.gz' in url else 'zip'}"
        with open(tmp_archive, "wb") as f:
            shutil.copyfileobj(response.raw, f)
            
        logger.info("Extracting binary...")
        try:
            if tmp_archive.suffix == ".zip":
                with zipfile.ZipFile(tmp_archive, 'r') as zip_ref:
                    # In macOS zip, the binary might be inside a folder or root
                    # We look for the 'sc' file
                    for file in zip_ref.namelist():
                        if file.endswith("/sc") or file == "sc":
                            with zip_ref.open(file) as source, open(self.bin_path, "wb") as target:
                                shutil.copyfileobj(source, target)
                            break
            else:
                with tarfile.open(tmp_archive, "r:gz") as tar:
                    # Look for the 'sc' binary in the archive
                    member = next((m for m in tar.getmembers() if m.name.endswith("/sc") or m.name == "sc"), None)
                    if member:
                        member.name = os.path.basename(member.name) # Flatten structure
                        tar.extract(member, path=self.bin_dir)
                    else:
                        raise ValueError("Binary 'sc' not found in archive")

        finally:
            if tmp_archive.exists():
                tmp_archive.unlink()
            
        # Ensure it's executable
        self.bin_path.chmod(0o755)
        logger.info(f"Successfully installed to {self.bin_path}")

    def get_bin_path(self):
        if not self.is_installed():
            # In a real scenario, maybe auto-download or raise error
            return None
        return str(self.bin_path)
