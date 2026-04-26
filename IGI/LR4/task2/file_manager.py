"""
Program Purpose: File operations and Archiving
Lab4, Task2, Version 1.0
Author: Gorbachova Anna 453504
Date: 12.04.2026
"""

import zipfile
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


class BasicFile:
    """Base class for file operations."""
    def __init__(self, path: str):
        self._path = Path(path)

    def __str__(self) -> str:
        """Method for string representation."""
        return f"File: {self._path.name}"
    
    @property
    def path(self) -> Path:
        """Getter for file path."""
        return self._path


class TextFileHandler(BasicFile):
    """Handler for text file operations."""
    def read(self, encoding: str = 'utf-8') -> str:
        """Read text from file."""
        if not self._path.exists():
            raise FileNotFoundError(f"File {self._path} not found")
        with open(self._path, 'r', encoding=encoding) as f:
            return f.read()

    def write(self, content: str, encoding: str = 'utf-8') -> None:
        """Write text to file."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._path, 'w', encoding=encoding) as f:
            f.write(content)
        print(f"Saved to {self._path}")


class ArchiveHandler(TextFileHandler):
    """Handler for ZIP archive operations."""   
    def __init__(self, path: str, zip_name: str):
        """Initialize ArchiveHandler."""
        super().__init__(path)
        self._zip_name = Path(zip_name)
        if not self._zip_name.suffix == '.zip':
            self._zip_name = self._zip_name.with_suffix('.zip')

    def create_zip(self) -> str:
        """Create ZIP archive with the file."""
        if not self._path.exists():
            raise FileNotFoundError(f"Cannot archive: {self._path} not found")
        
        with zipfile.ZipFile(self._zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write(self._path, arcname=self._path.name)
        
        return self.get_archive_info_string()
    
    def get_archive_info(self) -> Dict[str, Any]:
        """Get detailed information about archived file."""
        if not self._zip_name.exists():
            raise FileNotFoundError(f"Archive {self._zip_name} not found")
        
        with zipfile.ZipFile(self._zip_name, 'r') as zf:
            info = zf.getinfo(self._path.name)
            return {
                "filename": info.filename,
                "file_size": info.file_size,
                "compress_size": info.compress_size,
                "compression_ratio": round(100 * (1 - info.compress_size / info.file_size), 2) if info.file_size > 0 else 0,
                "date_time": datetime(*info.date_time).strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def get_archive_info_string(self) -> str:
        """Get formatted archive information as string."""
        info = self.get_archive_info()
        return (f"Archived '{info['filename']}' | "
                f"Original: {info['file_size']} bytes | "
                f"Compressed: {info['compress_size']} bytes | "
                f"Ratio: {info['compression_ratio']}%")
    
    def print_archive_info(self) -> None:
        """Print formatted archive information to console."""
        print("\n" + "=" * 50)
        print("ARCHIVE INFORMATION")
        print("=" * 50)
        info = self.get_archive_info()
        print(f"File name: {info['filename']}")
        print(f"Original size: {info['file_size']} bytes")
        print(f"Compressed size: {info['compress_size']} bytes")
        print(f"Compression ratio: {info['compression_ratio']}%")
        print(f"Archive date: {info['date_time']}")
        print("=" * 50)