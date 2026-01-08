"""
File Handler Utility

Handles file uploads, validation, storage, and processing for the Sentry AI application.
Supports documents (PDF, DOCX, TXT), videos (MP4, AVI, MOV), audio (MP3, WAV), and images (PNG, JPG).
"""

import shutil
import mimetypes
from pathlib import Path
from typing import Optional, Tuple, List
from datetime import datetime
import hashlib


class FileHandler:
    """
    Centralized file handling utility for Sentry AI.

    Features:
    - File type validation
    - Secure file storage
    - File size limits
    - File metadata extraction
    - Duplicate detection
    """

    # Allowed file types and their extensions
    ALLOWED_EXTENSIONS = {
        'document': ['.pdf', '.docx', '.doc', '.txt', '.md'],
        'video': ['.mp4', '.avi', '.mov', '.mkv', '.webm'],
        'audio': ['.mp3', '.wav', '.m4a', '.ogg', '.flac'],
        'image': ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
    }

    # Maximum file sizes (in bytes)
    MAX_FILE_SIZES = {
        'document': 50 * 1024 * 1024,  # 50 MB
        'video': 500 * 1024 * 1024,     # 500 MB
        'audio': 100 * 1024 * 1024,     # 100 MB
        'image': 10 * 1024 * 1024       # 10 MB
    }

    # Default upload directory
    DEFAULT_UPLOAD_DIR = Path("uploads")

    def __init__(self, upload_dir: Optional[Path] = None):
        """
        Initialize FileHandler.

        Args:
            upload_dir: Directory for storing uploaded files (default: ./uploads)
        """
        self.upload_dir = upload_dir or self.DEFAULT_UPLOAD_DIR
        self._ensure_upload_dirs()

    def _ensure_upload_dirs(self):
        """Create upload directories if they don't exist."""
        for file_type in self.ALLOWED_EXTENSIONS.keys():
            dir_path = self.upload_dir / file_type
            dir_path.mkdir(parents=True, exist_ok=True)

    def get_file_type(self, file_path: str) -> Optional[str]:
        """
        Determine the type of file based on extension.

        Args:
            file_path: Path to the file

        Returns:
            File type ('document', 'video', 'audio', 'image') or None
        """
        extension = Path(file_path).suffix.lower()

        for file_type, extensions in self.ALLOWED_EXTENSIONS.items():
            if extension in extensions:
                return file_type

        return None

    def is_allowed_file(self, filename: str, file_type: Optional[str] = None) -> bool:
        """
        Check if a file is allowed based on extension.

        Args:
            filename: Name of the file
            file_type: Optional specific file type to check against

        Returns:
            True if file is allowed, False otherwise
        """
        extension = Path(filename).suffix.lower()

        if file_type:
            return extension in self.ALLOWED_EXTENSIONS.get(file_type, [])

        # Check against all allowed extensions
        all_extensions = []
        for extensions in self.ALLOWED_EXTENSIONS.values():
            all_extensions.extend(extensions)

        return extension in all_extensions

    def validate_file_size(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate file size against limits.

        Args:
            file_path: Path to the file

        Returns:
            Tuple of (is_valid, error_message)
        """
        file_size = Path(file_path).stat().st_size
        file_type = self.get_file_type(file_path)

        if not file_type:
            return False, "Unknown file type"

        max_size = self.MAX_FILE_SIZES.get(file_type)

        if file_size > max_size:
            max_size_mb = max_size / (1024 * 1024)
            actual_size_mb = file_size / (1024 * 1024)
            return False, f"File too large: {actual_size_mb:.2f}MB exceeds {max_size_mb:.2f}MB limit"

        return True, None

    def calculate_file_hash(self, file_path: str) -> str:
        """
        Calculate MD5 hash of file for duplicate detection.

        Args:
            file_path: Path to the file

        Returns:
            MD5 hash string
        """
        hash_md5 = hashlib.md5()

        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)

        return hash_md5.hexdigest()

    def get_file_metadata(self, file_path: str) -> dict:
        """
        Extract metadata from a file.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary with file metadata
        """
        path = Path(file_path)
        stat = path.stat()

        metadata = {
            'filename': path.name,
            'size': stat.st_size,
            'size_mb': round(stat.st_size / (1024 * 1024), 2),
            'extension': path.suffix.lower(),
            'file_type': self.get_file_type(file_path),
            'mime_type': mimetypes.guess_type(file_path)[0],
            'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'file_hash': self.calculate_file_hash(file_path)
        }

        return metadata

    def save_uploaded_file(
        self,
        source_path: str,
        original_filename: str,
        preserve_name: bool = False
    ) -> Tuple[bool, Optional[str], Optional[dict]]:
        """
        Save an uploaded file to the appropriate directory.

        Args:
            source_path: Path to the temporary uploaded file
            original_filename: Original name of the file
            preserve_name: Whether to preserve original filename or generate unique name

        Returns:
            Tuple of (success, saved_path, metadata)
        """
        # Validate file type
        if not self.is_allowed_file(original_filename):
            return False, None, {'error': 'File type not allowed'}

        # Validate file size
        is_valid, error_msg = self.validate_file_size(source_path)
        if not is_valid:
            return False, None, {'error': error_msg}

        # Determine file type and target directory
        file_type = self.get_file_type(original_filename)
        target_dir = self.upload_dir / file_type

        # Generate filename
        if preserve_name:
            filename = original_filename
        else:
            # Generate unique filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            extension = Path(original_filename).suffix
            base_name = Path(original_filename).stem
            filename = f"{base_name}_{timestamp}{extension}"

        # Full target path
        target_path = target_dir / filename

        # Handle duplicate filenames
        counter = 1
        while target_path.exists():
            if preserve_name:
                # If preserving name, add counter
                extension = Path(original_filename).suffix
                base_name = Path(original_filename).stem
                filename = f"{base_name}_{counter}{extension}"
                target_path = target_dir / filename
                counter += 1
            else:
                # Should not happen with timestamp, but just in case
                return False, None, {'error': 'File already exists'}

        try:
            # Copy file to target location
            shutil.copy2(source_path, target_path)

            # Get metadata
            metadata = self.get_file_metadata(str(target_path))
            metadata['saved_path'] = str(target_path)
            metadata['relative_path'] = str(target_path.relative_to(self.upload_dir))

            return True, str(target_path), metadata

        except Exception as e:
            return False, None, {'error': f'Failed to save file: {str(e)}'}

    def delete_file(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Delete a file from storage.

        Args:
            file_path: Path to the file to delete

        Returns:
            Tuple of (success, error_message)
        """
        try:
            path = Path(file_path)

            if not path.exists():
                return False, "File does not exist"

            # Ensure file is within upload directory (security check)
            if not str(path.resolve()).startswith(str(self.upload_dir.resolve())):
                return False, "Cannot delete files outside upload directory"

            path.unlink()
            return True, None

        except Exception as e:
            return False, f"Failed to delete file: {str(e)}"

    def list_files(self, file_type: Optional[str] = None) -> List[dict]:
        """
        List all uploaded files.

        Args:
            file_type: Optional filter by file type ('document', 'video', etc.)

        Returns:
            List of file metadata dictionaries
        """
        files = []

        if file_type:
            # List files in specific type directory
            if file_type not in self.ALLOWED_EXTENSIONS:
                return []

            dir_path = self.upload_dir / file_type
            if dir_path.exists():
                for file_path in dir_path.iterdir():
                    if file_path.is_file():
                        metadata = self.get_file_metadata(str(file_path))
                        files.append(metadata)
        else:
            # List all files
            for type_dir in self.ALLOWED_EXTENSIONS.keys():
                dir_path = self.upload_dir / type_dir
                if dir_path.exists():
                    for file_path in dir_path.iterdir():
                        if file_path.is_file():
                            metadata = self.get_file_metadata(str(file_path))
                            files.append(metadata)

        # Sort by modified date (newest first)
        files.sort(key=lambda x: x['modified_at'], reverse=True)

        return files

    def find_duplicates(self, file_path: str) -> List[str]:
        """
        Find duplicate files based on hash.

        Args:
            file_path: Path to the file to check

        Returns:
            List of paths to duplicate files
        """
        target_hash = self.calculate_file_hash(file_path)
        duplicates = []

        for file_info in self.list_files():
            if file_info['file_hash'] == target_hash:
                stored_path = self.upload_dir / file_info['file_type'] / file_info['filename']
                if str(stored_path) != file_path:
                    duplicates.append(str(stored_path))

        return duplicates

    def cleanup_old_files(self, days: int = 30) -> Tuple[int, int]:
        """
        Delete files older than specified days.

        Args:
            days: Number of days (files older than this will be deleted)

        Returns:
            Tuple of (files_deleted, errors)
        """
        cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
        deleted_count = 0
        error_count = 0

        for file_info in self.list_files():
            file_path = self.upload_dir / file_info['file_type'] / file_info['filename']

            if file_path.stat().st_mtime < cutoff_time:
                success, _ = self.delete_file(str(file_path))
                if success:
                    deleted_count += 1
                else:
                    error_count += 1

        return deleted_count, error_count


# Convenience function for quick file validation
def validate_file(file_path: str) -> Tuple[bool, Optional[str], Optional[dict]]:
    """
    Quick validation of a file.

    Args:
        file_path: Path to the file

    Returns:
        Tuple of (is_valid, error_message, metadata)
    """
    handler = FileHandler()

    if not Path(file_path).exists():
        return False, "File does not exist", None

    filename = Path(file_path).name

    if not handler.is_allowed_file(filename):
        return False, "File type not allowed", None

    is_valid, error = handler.validate_file_size(file_path)
    if not is_valid:
        return False, error, None

    metadata = handler.get_file_metadata(file_path)
    return True, None, metadata


if __name__ == "__main__":
    # Quick test
    handler = FileHandler()
    print("File Handler initialized")
    print(f"Upload directory: {handler.upload_dir}")
    print(f"Supported file types: {list(handler.ALLOWED_EXTENSIONS.keys())}")
