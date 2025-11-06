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
