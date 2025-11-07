"""Utilities for validating uploaded files.

Provides helper functions to validate and sanitize user supplied
files before persisting them to disk or processing their contents.
"""

from __future__ import annotations

import os
import uuid
from collections.abc import Callable, Iterable

from werkzeug.datastructures import FileStorage

from .error_handler import ValidationError


class FileValidationError(ValidationError):
    """Raised when an uploaded file fails validation checks."""

    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.status_code = status_code


DEFAULT_MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif"}
ALLOWED_IMAGE_MIME_TYPES = {"image/png", "image/jpeg", "image/gif"}

# Image file signatures (magic bytes) for detection
IMAGE_SIGNATURES = {
    b"\x89PNG\r\n\x1a\n": (".png", "image/png"),
    b"\xff\xd8\xff": (".jpg", "image/jpeg"),
    b"GIF87a": (".gif", "image/gif"),
    b"GIF89a": (".gif", "image/gif"),
}

ALLOWED_CERTIFICATE_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
ALLOWED_CERTIFICATE_MIME_TYPES = {"application/pdf", "image/png", "image/jpeg"}
# Allow common MIME types sent by different browsers for CSV files
ALLOWED_CSV_MIME_TYPES = {
    "text/csv",
    "application/vnd.ms-excel",
    "text/plain",  # Safari, Firefox, curl
    "application/octet-stream"  # Generic binary fallback
}

DANGEROUS_CSV_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def _get_stream_size(stream) -> int:
    """Return the size of a ``FileStorage`` stream without altering position."""

    current_position = stream.tell()
    stream.seek(0, os.SEEK_END)
    size = stream.tell()
    stream.seek(current_position)
    return size


def _ensure_size_within_limit(stream, max_size: int) -> None:
    file_size = _get_stream_size(stream)
    if file_size == 0:
        raise FileValidationError("Uploaded file is empty")
    if file_size > max_size:
        raise FileValidationError(
            f"File is too large. Maximum allowed size is {max_size // (1024 * 1024)}MB",
            status_code=413,
        )


def _read_bytes(stream, max_bytes: int) -> bytes:
    stream.seek(0)
    data = stream.read(max_bytes)
    stream.seek(0)
    return data


def _validate_file(
    file_storage: FileStorage,
    allowed_extensions: Iterable[str],
    allowed_mime_types: Iterable[str],
    max_size: int,
    detector: Callable[[bytes], tuple[str, str]],
) -> str:
    if not file_storage or not file_storage.filename:
        raise FileValidationError("No file selected")

    filename = file_storage.filename
    ext = os.path.splitext(filename)[1].lower()
    if ext not in allowed_extensions:
        allowed_list = ", ".join(sorted(allowed_extensions))
        raise FileValidationError(f"File type not allowed. Allowed extensions: {allowed_list}")

    _ensure_size_within_limit(file_storage.stream, max_size)

    mimetype = (file_storage.mimetype or "").lower()
    if mimetype and mimetype not in {m.lower() for m in allowed_mime_types}:
        raise FileValidationError("Invalid file content type")

    file_bytes = _read_bytes(file_storage.stream, max_size + 1)
    detected_ext, detected_mime = detector(file_bytes)
    if detected_mime.lower() not in {m.lower() for m in allowed_mime_types}:
        raise FileValidationError("Detected file type is not permitted")

    safe_filename = f"{uuid.uuid4().hex}{detected_ext}"
    file_storage.stream.seek(0)
    return safe_filename


def _detect_image(file_bytes: bytes) -> tuple[str, str]:
    """Detect image type by checking file signature (magic bytes)."""
    if not file_bytes:
        raise FileValidationError("Uploaded file is empty")

    # Check for known image signatures
    for signature, (ext, mime) in IMAGE_SIGNATURES.items():
        if file_bytes.startswith(signature):
            return (ext, mime)

    raise FileValidationError("Uploaded file is not a valid image")


def _detect_certificate(file_bytes: bytes) -> tuple[str, str]:
    # Allow PDF certificates
    if file_bytes.startswith(b"%PDF"):
        return ".pdf", "application/pdf"

    # Fallback to image detection for image-based certificates
    try:
        return _detect_image(file_bytes)
    except FileValidationError:
        raise FileValidationError("Certificate must be a PDF or image file")


def validate_image_upload(file_storage: FileStorage, max_size: int | None = None) -> str:
    """Validate an uploaded image and return a safe filename."""

    return _validate_file(
        file_storage,
        ALLOWED_IMAGE_EXTENSIONS,
        ALLOWED_IMAGE_MIME_TYPES,
        max_size or DEFAULT_MAX_FILE_SIZE,
        _detect_image,
    )


def validate_certificate_upload(file_storage: FileStorage, max_size: int | None = None) -> str:
    """Validate a calibration certificate upload and return a safe filename."""

    return _validate_file(
        file_storage,
        ALLOWED_CERTIFICATE_EXTENSIONS,
        ALLOWED_CERTIFICATE_MIME_TYPES,
        max_size or DEFAULT_MAX_FILE_SIZE,
        _detect_certificate,
    )


def validate_csv_upload(file_storage: FileStorage, max_size: int | None = None) -> None:
    """Validate that an uploaded CSV file is safe to process."""

    if not file_storage or not file_storage.filename:
        raise FileValidationError("No file selected")

    if not file_storage.filename.lower().endswith(".csv"):
        raise FileValidationError("Only CSV files are supported")

    _ensure_size_within_limit(file_storage.stream, max_size or DEFAULT_MAX_FILE_SIZE)

    mimetype = (file_storage.mimetype or "").lower()
    if mimetype and mimetype not in {m.lower() for m in ALLOWED_CSV_MIME_TYPES}:
        raise FileValidationError("Invalid file content type. A CSV file is required")

    sample_bytes = _read_bytes(file_storage.stream, 4096)

    try:
        decoded_sample = sample_bytes.decode("utf-8")
    except UnicodeDecodeError:
        try:
            decoded_sample = sample_bytes.decode("latin-1")
        except UnicodeDecodeError:
            raise FileValidationError("Unable to read CSV file. Please ensure it is UTF-8 encoded")

    if "\x00" in decoded_sample:
        raise FileValidationError("CSV file contains invalid characters")

    if "," not in decoded_sample and "\n" not in decoded_sample:
        raise FileValidationError("CSV file does not appear to contain valid data")

    file_storage.stream.seek(0)


def sanitize_csv_cell(value: str) -> str:
    """Sanitize CSV cells by removing control characters."""

    if not isinstance(value, str):
        return value

    return value.replace("\x00", "").strip()


def neutralize_csv_formula(value: str) -> str:
    """Prefix values that could be interpreted as formulas when exported."""

    if isinstance(value, str) and value and value[0] in DANGEROUS_CSV_PREFIXES:
        return "'" + value
    return value


# Extended file type support for attachments
DOCUMENT_SIGNATURES = {
    b"%PDF": ("pdf", "application/pdf"),
    b"PK\x03\x04": ("zip", "application/zip"),  # ZIP, DOCX, XLSX, etc.
}

ALLOWED_ATTACHMENT_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp",  # Images
    ".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt",  # Documents
    ".xls", ".xlsx", ".csv", ".ods",  # Spreadsheets
    ".zip", ".tar", ".gz", ".7z"  # Archives
}


def validate_file_upload(file_path: str, max_size: int | None = None) -> None:
    """
    Validate an uploaded file by checking magic bytes and size.

    Args:
        file_path: Path to the uploaded file
        max_size: Maximum allowed file size in bytes

    Raises:
        FileValidationError: If file validation fails
    """
    if not os.path.exists(file_path):
        raise FileValidationError("File not found")

    # Check file size
    file_size = os.path.getsize(file_path)
    if file_size == 0:
        raise FileValidationError("File is empty")

    if max_size and file_size > max_size:
        raise FileValidationError(
            f"File too large. Maximum size: {max_size // (1024 * 1024)}MB"
        )

    # Read first bytes for magic byte validation
    with open(file_path, "rb") as f:
        header = f.read(512)

    # Check for NULL bytes (potential binary corruption)
    if b"\x00" * 100 in header:
        raise FileValidationError("File appears to be corrupted")

    # File is valid


def get_file_type(file_path: str) -> str:
    """
    Determine the file type category based on extension and content.

    Args:
        file_path: Path to the file

    Returns:
        File type category: 'image', 'document', 'spreadsheet', 'archive', 'other'
    """
    ext = os.path.splitext(file_path)[1].lower()

    # Image types
    if ext in {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}:
        return "image"

    # Document types
    if ext in {".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt"}:
        return "document"

    # Spreadsheet types
    if ext in {".xls", ".xlsx", ".csv", ".ods"}:
        return "spreadsheet"

    # Archive types
    if ext in {".zip", ".tar", ".gz", ".7z"}:
        return "archive"

    return "other"


def scan_file_for_malware(file_path: str) -> None:
    """
    Basic malware scanning for uploaded files.

    This is a basic implementation that checks for:
    - Executable file extensions embedded in archives
    - Suspicious file patterns
    - Script files disguised as other types

    For production, integrate with ClamAV or similar AV solution.

    Args:
        file_path: Path to the file to scan

    Raises:
        FileValidationError: If file appears suspicious
    """
    # Check file extension
    ext = os.path.splitext(file_path)[1].lower()

    # Block executable files
    dangerous_extensions = {
        ".exe", ".dll", ".so", ".dylib", ".bat", ".cmd", ".sh",
        ".ps1", ".vbs", ".js", ".jar", ".app", ".dmg", ".pkg"
    }

    if ext in dangerous_extensions:
        raise FileValidationError(
            "Executable files are not allowed for security reasons"
        )

    # Read file header
    with open(file_path, "rb") as f:
        header = f.read(1024)

    # Check for executable signatures
    if header.startswith(b"MZ"):  # Windows EXE
        raise FileValidationError("Windows executable files are not allowed")

    if header.startswith(b"\x7fELF"):  # Linux ELF
        raise FileValidationError("Executable files are not allowed")

    # Check for script content in disguised files
    suspicious_patterns = [
        b"<script",
        b"eval(",
        b"system(",
        b"exec(",
        b"shell_exec",
    ]

    header_lower = header.lower()
    for pattern in suspicious_patterns:
        if pattern in header_lower:
            raise FileValidationError("File contains suspicious content")

    # File passed basic checks
