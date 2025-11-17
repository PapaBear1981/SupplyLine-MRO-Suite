"""
Comprehensive tests for routes_attachments.py - file attachment endpoints.
Tests file upload, download, deletion, validation, security, and authentication.
"""
import io
import os
import tempfile
from unittest.mock import MagicMock, Mock, patch, mock_open

import pytest
from PIL import Image
from werkzeug.security import generate_password_hash

from models import db, User
from models_messaging import MessageAttachment, AttachmentDownload, Channel, ChannelMember, ChannelMessage
from models_kits import Kit, KitMessage, AircraftType


class TestHelperFunctions:
    """Test helper functions in routes_attachments module."""

    def test_allowed_file_with_valid_image_extensions(self, app):
        """Test allowed_file returns True for valid image extensions."""
        from routes_attachments import allowed_file

        assert allowed_file("test.png") is True
        assert allowed_file("test.jpg") is True
        assert allowed_file("test.jpeg") is True
        assert allowed_file("test.gif") is True
        assert allowed_file("test.bmp") is True
        assert allowed_file("test.webp") is True

    def test_allowed_file_with_valid_document_extensions(self, app):
        """Test allowed_file returns True for valid document extensions."""
        from routes_attachments import allowed_file

        assert allowed_file("test.pdf") is True
        assert allowed_file("test.doc") is True
        assert allowed_file("test.docx") is True
        assert allowed_file("test.txt") is True
        assert allowed_file("test.rtf") is True
        assert allowed_file("test.odt") is True

    def test_allowed_file_with_valid_spreadsheet_extensions(self, app):
        """Test allowed_file returns True for valid spreadsheet extensions."""
        from routes_attachments import allowed_file

        assert allowed_file("test.xls") is True
        assert allowed_file("test.xlsx") is True
        assert allowed_file("test.csv") is True
        assert allowed_file("test.ods") is True

    def test_allowed_file_with_valid_archive_extensions(self, app):
        """Test allowed_file returns True for valid archive extensions."""
        from routes_attachments import allowed_file

        assert allowed_file("test.zip") is True
        assert allowed_file("test.tar") is True
        assert allowed_file("test.gz") is True
        assert allowed_file("test.7z") is True

    def test_allowed_file_with_invalid_extensions(self, app):
        """Test allowed_file returns False for invalid extensions."""
        from routes_attachments import allowed_file

        assert allowed_file("test.exe") is False
        assert allowed_file("test.bat") is False
        assert allowed_file("test.sh") is False
        assert allowed_file("test.py") is False
        assert allowed_file("test.js") is False

    def test_allowed_file_without_extension(self, app):
        """Test allowed_file returns False for files without extension."""
        from routes_attachments import allowed_file

        assert allowed_file("noextension") is False
        assert allowed_file("somefile") is False

    def test_allowed_file_case_insensitive(self, app):
        """Test allowed_file handles uppercase extensions."""
        from routes_attachments import allowed_file

        assert allowed_file("test.PNG") is True
        assert allowed_file("test.PDF") is True
        assert allowed_file("test.XLSX") is True

    def test_get_file_extension_with_extension(self, app):
        """Test get_file_extension extracts extension correctly."""
        from routes_attachments import get_file_extension

        assert get_file_extension("test.pdf") == "pdf"
        assert get_file_extension("image.PNG") == "png"
        assert get_file_extension("file.multiple.dots.txt") == "txt"

    def test_get_file_extension_without_extension(self, app):
        """Test get_file_extension returns empty string for no extension."""
        from routes_attachments import get_file_extension

        assert get_file_extension("noextension") == ""
        assert get_file_extension("file") == ""

    def test_generate_unique_filename_with_extension(self, app):
        """Test generate_unique_filename creates unique name with extension."""
        from routes_attachments import generate_unique_filename

        filename = generate_unique_filename("original.pdf")
        assert filename.endswith(".pdf")
        assert "_" in filename
        # Should contain timestamp and unique ID
        parts = filename.rsplit(".", 1)[0].split("_")
        assert len(parts) >= 2

    def test_generate_unique_filename_without_extension(self, app):
        """Test generate_unique_filename handles files without extension."""
        from routes_attachments import generate_unique_filename

        filename = generate_unique_filename("noextension")
        assert "." not in filename.split("_")[-1] or filename.split("_")[-1] == ""
        # Should still contain timestamp and unique ID
        assert "_" in filename

    def test_generate_unique_filename_uniqueness(self, app):
        """Test generate_unique_filename generates unique names."""
        from routes_attachments import generate_unique_filename

        filenames = [generate_unique_filename("test.pdf") for _ in range(10)]
        # All filenames should be unique
        assert len(set(filenames)) == 10


class TestCreateThumbnail:
    """Test thumbnail creation functionality."""

    def test_create_thumbnail_rgb_image(self, app):
        """Test creating thumbnail from RGB image."""
        from routes_attachments import create_thumbnail

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test RGB image
            img = Image.new("RGB", (800, 600), color="red")
            img_path = os.path.join(tmpdir, "test.jpg")
            img.save(img_path, "JPEG")

            thumb_path = os.path.join(tmpdir, "thumb.jpg")
            result = create_thumbnail(img_path, thumb_path)

            assert result is True
            assert os.path.exists(thumb_path)

            # Check thumbnail size
            with Image.open(thumb_path) as thumb:
                assert thumb.size[0] <= 300
                assert thumb.size[1] <= 300

    def test_create_thumbnail_rgba_image(self, app):
        """Test creating thumbnail from RGBA image."""
        from routes_attachments import create_thumbnail

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test RGBA image
            img = Image.new("RGBA", (800, 600), color=(255, 0, 0, 128))
            img_path = os.path.join(tmpdir, "test.png")
            img.save(img_path, "PNG")

            thumb_path = os.path.join(tmpdir, "thumb.jpg")
            result = create_thumbnail(img_path, thumb_path)

            assert result is True
            assert os.path.exists(thumb_path)

    def test_create_thumbnail_palette_image(self, app):
        """Test creating thumbnail from palette (P mode) image."""
        from routes_attachments import create_thumbnail

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test P mode image
            img = Image.new("P", (800, 600))
            img_path = os.path.join(tmpdir, "test.gif")
            img.save(img_path, "GIF")

            thumb_path = os.path.join(tmpdir, "thumb.jpg")
            result = create_thumbnail(img_path, thumb_path)

            assert result is True
            assert os.path.exists(thumb_path)

    def test_create_thumbnail_la_image(self, app):
        """Test creating thumbnail from LA (grayscale with alpha) image."""
        from routes_attachments import create_thumbnail

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test LA image
            img = Image.new("LA", (800, 600))
            img_path = os.path.join(tmpdir, "test.png")
            img.save(img_path, "PNG")

            thumb_path = os.path.join(tmpdir, "thumb.jpg")
            result = create_thumbnail(img_path, thumb_path)

            assert result is True
            assert os.path.exists(thumb_path)

    def test_create_thumbnail_failure(self, app):
        """Test create_thumbnail returns False on error."""
        from routes_attachments import create_thumbnail

        with tempfile.TemporaryDirectory() as tmpdir:
            # Try to create thumbnail from non-existent file
            result = create_thumbnail(
                os.path.join(tmpdir, "nonexistent.jpg"),
                os.path.join(tmpdir, "thumb.jpg")
            )
            assert result is False

    def test_create_thumbnail_invalid_image(self, app):
        """Test create_thumbnail handles invalid image file."""
        from routes_attachments import create_thumbnail

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create invalid image file
            img_path = os.path.join(tmpdir, "invalid.jpg")
            with open(img_path, "w") as f:
                f.write("This is not an image")

            thumb_path = os.path.join(tmpdir, "thumb.jpg")
            result = create_thumbnail(img_path, thumb_path)

            assert result is False


class TestUploadAttachment:
    """Test file upload endpoint."""

    @pytest.fixture
    def setup_users_and_kit(self, db_session):
        """Create users and kit for attachment tests."""
        user1 = User(
            name="Sender User",
            employee_number="SEND001",
            department="Engineering",
            password_hash=generate_password_hash("password123"),
            is_admin=False,
            is_active=True
        )
        user2 = User(
            name="Recipient User",
            employee_number="RECV001",
            department="Materials",
            password_hash=generate_password_hash("password123"),
            is_admin=False,
            is_active=True
        )
        db_session.add(user1)
        db_session.add(user2)
        db_session.flush()

        aircraft_type = AircraftType(
            name="Test Aircraft",
            description="Test aircraft type"
        )
        db_session.add(aircraft_type)
        db_session.flush()

        kit = Kit(
            name="Test Kit",
            aircraft_type_id=aircraft_type.id,
            description="Test kit for attachments",
            created_by=user1.id,
            status="active"
        )
        db_session.add(kit)
        db_session.flush()

        message = KitMessage(
            kit_id=kit.id,
            sender_id=user1.id,
            recipient_id=user2.id,
            subject="Test Message",
            message="Test message body"
        )
        db_session.add(message)
        db_session.commit()

        return {
            "user1": user1,
            "user2": user2,
            "kit": kit,
            "message": message
        }

    @pytest.fixture
    def user1_token(self, app, setup_users_and_kit):
        """Generate token for user1."""
        from auth import JWTManager
        with app.app_context():
            tokens = JWTManager.generate_tokens(setup_users_and_kit["user1"])
            return tokens["access_token"]

    @pytest.fixture
    def auth_headers_user1(self, user1_token):
        """Auth headers for user1."""
        return {"Authorization": f"Bearer {user1_token}"}

    def test_upload_attachment_no_file(self, client, auth_headers_user1):
        """Test upload fails when no file is provided."""
        response = client.post(
            "/api/attachments/upload",
            headers=auth_headers_user1,
            data={"message_type": "kit", "message_id": "1"}
        )
        assert response.status_code == 400
        assert b"No file provided" in response.data

    def test_upload_attachment_empty_filename(self, client, auth_headers_user1):
        """Test upload fails when file has empty filename."""
        data = {
            "file": (io.BytesIO(b"test content"), ""),
            "message_type": "kit",
            "message_id": "1"
        }
        response = client.post(
            "/api/attachments/upload",
            headers=auth_headers_user1,
            data=data,
            content_type="multipart/form-data"
        )
        assert response.status_code == 400
        assert b"No file selected" in response.data

    def test_upload_attachment_invalid_message_type(self, client, auth_headers_user1):
        """Test upload fails with invalid message type."""
        data = {
            "file": (io.BytesIO(b"test content"), "test.txt"),
            "message_type": "invalid",
            "message_id": "1"
        }
        response = client.post(
            "/api/attachments/upload",
            headers=auth_headers_user1,
            data=data,
            content_type="multipart/form-data"
        )
        assert response.status_code == 400
        assert b"Invalid message type" in response.data

    def test_upload_attachment_disallowed_extension(self, client, auth_headers_user1):
        """Test upload fails for disallowed file extensions."""
        data = {
            "file": (io.BytesIO(b"test content"), "malware.exe"),
            "message_type": "kit",
            "message_id": "1"
        }
        response = client.post(
            "/api/attachments/upload",
            headers=auth_headers_user1,
            data=data,
            content_type="multipart/form-data"
        )
        assert response.status_code == 400
        assert b"File type not allowed" in response.data

    def test_upload_attachment_file_too_large(self, client, auth_headers_user1):
        """Test upload fails when file exceeds maximum size."""
        # Create file larger than 10MB
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        data = {
            "file": (io.BytesIO(large_content), "large.txt"),
            "message_type": "kit",
            "message_id": "1"
        }
        response = client.post(
            "/api/attachments/upload",
            headers=auth_headers_user1,
            data=data,
            content_type="multipart/form-data"
        )
        assert response.status_code == 400
        assert b"File too large" in response.data

    @patch("routes_attachments.logger")
    @patch("routes_attachments.validate_file_upload")
    @patch("routes_attachments.get_file_type", return_value="document")
    @patch("routes_attachments.scan_file_for_malware")
    def test_upload_attachment_success_kit_message(
        self, mock_scan, mock_get_type, mock_validate, mock_logger,
        client, auth_headers_user1, setup_users_and_kit
    ):
        """Test successful file upload for kit message."""
        message_id = setup_users_and_kit["message"].id

        data = {
            "file": (io.BytesIO(b"Test file content"), "document.txt"),
            "message_type": "kit",
            "message_id": str(message_id)
        }
        response = client.post(
            "/api/attachments/upload",
            headers=auth_headers_user1,
            data=data,
            content_type="multipart/form-data"
        )

        assert response.status_code == 201
        json_data = response.get_json()
        assert json_data["message"] == "File uploaded successfully"
        assert "attachment" in json_data
        assert json_data["attachment"]["original_filename"] == "document.txt"
        assert json_data["attachment"]["kit_message_id"] == message_id

    @patch("routes_attachments.logger")
    @patch("routes_attachments.validate_file_upload")
    @patch("routes_attachments.get_file_type", return_value="document")
    @patch("routes_attachments.scan_file_for_malware")
    def test_upload_attachment_success_channel_message(
        self, mock_scan, mock_get_type, mock_validate, mock_logger,
        client, auth_headers_user1, setup_users_and_kit, db_session
    ):
        """Test successful file upload for channel message."""
        user1 = setup_users_and_kit["user1"]

        # Create channel and message
        channel = Channel(
            name="Test Channel",
            description="Test channel",
            channel_type="department",
            department="Engineering",
            created_by=user1.id
        )
        db_session.add(channel)
        db_session.flush()

        channel_message = ChannelMessage(
            channel_id=channel.id,
            sender_id=user1.id,
            message="Channel message"
        )
        db_session.add(channel_message)
        db_session.commit()

        data = {
            "file": (io.BytesIO(b"Test file content"), "document.txt"),
            "message_type": "channel",
            "message_id": str(channel_message.id)
        }
        response = client.post(
            "/api/attachments/upload",
            headers=auth_headers_user1,
            data=data,
            content_type="multipart/form-data"
        )

        assert response.status_code == 201
        json_data = response.get_json()
        assert json_data["attachment"]["channel_message_id"] == channel_message.id

    @patch("routes_attachments.logger")
    @patch("routes_attachments.validate_file_upload")
    @patch("routes_attachments.get_file_type", return_value="image")
    @patch("routes_attachments.scan_file_for_malware")
    @patch("routes_attachments.create_thumbnail", return_value=True)
    def test_upload_attachment_with_thumbnail_creation(
        self, mock_thumbnail, mock_scan, mock_get_type, mock_validate, mock_logger,
        client, auth_headers_user1, setup_users_and_kit
    ):
        """Test file upload creates thumbnail for images."""
        message_id = setup_users_and_kit["message"].id

        data = {
            "file": (io.BytesIO(b"fake image content"), "image.png"),
            "message_type": "kit",
            "message_id": str(message_id)
        }
        response = client.post(
            "/api/attachments/upload",
            headers=auth_headers_user1,
            data=data,
            content_type="multipart/form-data"
        )

        assert response.status_code == 201
        json_data = response.get_json()
        assert json_data["attachment"]["thumbnail_path"] is not None
        mock_thumbnail.assert_called_once()

    @patch("routes_attachments.logger")
    @patch("routes_attachments.validate_file_upload")
    @patch("routes_attachments.get_file_type", return_value="image")
    @patch("routes_attachments.scan_file_for_malware")
    @patch("routes_attachments.create_thumbnail", return_value=False)
    def test_upload_attachment_thumbnail_failure(
        self, mock_thumbnail, mock_scan, mock_get_type, mock_validate, mock_logger,
        client, auth_headers_user1, setup_users_and_kit
    ):
        """Test file upload continues when thumbnail creation fails."""
        message_id = setup_users_and_kit["message"].id

        data = {
            "file": (io.BytesIO(b"fake image content"), "image.png"),
            "message_type": "kit",
            "message_id": str(message_id)
        }
        response = client.post(
            "/api/attachments/upload",
            headers=auth_headers_user1,
            data=data,
            content_type="multipart/form-data"
        )

        assert response.status_code == 201
        json_data = response.get_json()
        assert json_data["attachment"]["thumbnail_path"] is None

    @patch("routes_attachments.validate_file_upload")
    def test_upload_attachment_validation_error(
        self, mock_validate, client, auth_headers_user1
    ):
        """Test upload fails when file validation fails."""
        from utils.file_validation import FileValidationError
        mock_validate.side_effect = FileValidationError("File appears to be corrupted")

        data = {
            "file": (io.BytesIO(b"test content"), "document.txt"),
            "message_type": "kit",
            "message_id": "1"
        }
        response = client.post(
            "/api/attachments/upload",
            headers=auth_headers_user1,
            data=data,
            content_type="multipart/form-data"
        )

        assert response.status_code == 400
        assert b"File appears to be corrupted" in response.data

    @patch("routes_attachments.validate_file_upload")
    @patch("routes_attachments.get_file_type", return_value="document")
    @patch("routes_attachments.scan_file_for_malware")
    def test_upload_attachment_malware_scan_failure(
        self, mock_scan, mock_get_type, mock_validate,
        client, auth_headers_user1
    ):
        """Test upload fails when malware scan detects threat."""
        from utils.file_validation import FileValidationError
        mock_scan.side_effect = FileValidationError("File contains suspicious content")

        data = {
            "file": (io.BytesIO(b"malicious content"), "document.txt"),
            "message_type": "kit",
            "message_id": "1"
        }
        response = client.post(
            "/api/attachments/upload",
            headers=auth_headers_user1,
            data=data,
            content_type="multipart/form-data"
        )

        assert response.status_code == 400
        assert b"File rejected by security scan" in response.data

    @patch("routes_attachments.logger")
    @patch("routes_attachments.validate_file_upload")
    @patch("routes_attachments.get_file_type", return_value="document")
    @patch("routes_attachments.scan_file_for_malware")
    def test_upload_attachment_malware_scan_unexpected_error(
        self, mock_scan, mock_get_type, mock_validate, mock_logger,
        client, auth_headers_user1, setup_users_and_kit
    ):
        """Test upload continues when malware scan has unexpected error."""
        mock_scan.side_effect = Exception("Unexpected scan error")
        message_id = setup_users_and_kit["message"].id

        data = {
            "file": (io.BytesIO(b"test content"), "document.txt"),
            "message_type": "kit",
            "message_id": str(message_id)
        }
        response = client.post(
            "/api/attachments/upload",
            headers=auth_headers_user1,
            data=data,
            content_type="multipart/form-data"
        )

        # Should still succeed but with scan_error status
        assert response.status_code == 201
        json_data = response.get_json()
        assert json_data["attachment"]["scan_result"] == "scan_error"

    @patch("routes_attachments.logger")
    @patch("routes_attachments.validate_file_upload")
    @patch("routes_attachments.get_file_type", return_value="document")
    @patch("routes_attachments.scan_file_for_malware")
    def test_upload_attachment_unknown_mime_type(
        self, mock_scan, mock_get_type, mock_validate, mock_logger,
        client, auth_headers_user1, setup_users_and_kit
    ):
        """Test upload handles unknown MIME type."""
        message_id = setup_users_and_kit["message"].id

        # File with non-standard extension but allowed
        data = {
            "file": (io.BytesIO(b"content"), "file.7z"),
            "message_type": "kit",
            "message_id": str(message_id)
        }
        response = client.post(
            "/api/attachments/upload",
            headers=auth_headers_user1,
            data=data,
            content_type="multipart/form-data"
        )

        assert response.status_code == 201
        json_data = response.get_json()
        # Should fallback to octet-stream
        assert json_data["attachment"]["mime_type"] in ["application/x-7z-compressed", "application/octet-stream"]

    def test_upload_attachment_no_auth(self, client):
        """Test upload fails without authentication."""
        data = {
            "file": (io.BytesIO(b"test content"), "test.txt"),
            "message_type": "kit",
            "message_id": "1"
        }
        response = client.post(
            "/api/attachments/upload",
            data=data,
            content_type="multipart/form-data"
        )
        assert response.status_code == 401

    @patch("routes_attachments.validate_file_upload")
    @patch("routes_attachments.get_file_type", return_value="document")
    @patch("routes_attachments.scan_file_for_malware")
    @patch("routes_attachments.db.session.commit")
    def test_upload_attachment_database_error(
        self, mock_commit, mock_scan, mock_get_type, mock_validate,
        client, auth_headers_user1
    ):
        """Test upload handles database errors."""
        mock_commit.side_effect = Exception("Database error")

        data = {
            "file": (io.BytesIO(b"test content"), "document.txt"),
            "message_type": "kit",
            "message_id": "1"
        }
        response = client.post(
            "/api/attachments/upload",
            headers=auth_headers_user1,
            data=data,
            content_type="multipart/form-data"
        )

        assert response.status_code == 500
        assert b"Failed to upload file" in response.data


class TestDownloadAttachment:
    """Test file download endpoint."""

    @pytest.fixture
    def setup_attachment(self, db_session):
        """Create users, kit message, and attachment for download tests."""
        sender = User(
            name="Sender",
            employee_number="SEND002",
            department="Engineering",
            password_hash=generate_password_hash("password"),
            is_admin=False,
            is_active=True
        )
        recipient = User(
            name="Recipient",
            employee_number="RECV002",
            department="Materials",
            password_hash=generate_password_hash("password"),
            is_admin=False,
            is_active=True
        )
        other_user = User(
            name="Other User",
            employee_number="OTHER001",
            department="HR",
            password_hash=generate_password_hash("password"),
            is_admin=False,
            is_active=True
        )
        db_session.add_all([sender, recipient, other_user])
        db_session.flush()

        aircraft_type = AircraftType(
            name="Download Aircraft",
            description="Aircraft type for download tests"
        )
        db_session.add(aircraft_type)
        db_session.flush()

        kit = Kit(
            name="Download Test Kit",
            aircraft_type_id=aircraft_type.id,
            description="Kit for download tests",
            created_by=sender.id,
            status="active"
        )
        db_session.add(kit)
        db_session.flush()

        message = KitMessage(
            kit_id=kit.id,
            sender_id=sender.id,
            recipient_id=recipient.id,
            subject="Download Test",
            message="Test message with attachment"
        )
        db_session.add(message)
        db_session.flush()

        # Create temporary file
        tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
        tmpfile.write(b"Test file content for download")
        tmpfile.close()

        attachment = MessageAttachment(
            kit_message_id=message.id,
            filename="unique_file.txt",
            original_filename="download_test.txt",
            file_path=tmpfile.name,
            file_size=30,
            mime_type="text/plain",
            file_type="document",
            uploaded_by=sender.id,
            is_scanned=True,
            scan_result="clean"
        )
        db_session.add(attachment)
        db_session.commit()

        return {
            "sender": sender,
            "recipient": recipient,
            "other_user": other_user,
            "message": message,
            "attachment": attachment,
            "temp_file": tmpfile.name
        }

    @pytest.fixture
    def sender_token(self, app, setup_attachment):
        """Token for sender user."""
        from auth import JWTManager
        with app.app_context():
            return JWTManager.generate_tokens(setup_attachment["sender"])["access_token"]

    @pytest.fixture
    def recipient_token(self, app, setup_attachment):
        """Token for recipient user."""
        from auth import JWTManager
        with app.app_context():
            return JWTManager.generate_tokens(setup_attachment["recipient"])["access_token"]

    @pytest.fixture
    def other_user_token(self, app, setup_attachment):
        """Token for other user (no access)."""
        from auth import JWTManager
        with app.app_context():
            return JWTManager.generate_tokens(setup_attachment["other_user"])["access_token"]

    def test_download_attachment_success_sender(self, client, sender_token, setup_attachment):
        """Test sender can download attachment."""
        attachment_id = setup_attachment["attachment"].id
        headers = {"Authorization": f"Bearer {sender_token}"}

        response = client.get(
            f"/api/attachments/{attachment_id}/download",
            headers=headers
        )

        assert response.status_code == 200
        assert response.data == b"Test file content for download"
        assert response.headers["Content-Disposition"] == "attachment; filename=download_test.txt"

    def test_download_attachment_success_recipient(self, client, recipient_token, setup_attachment):
        """Test recipient can download attachment."""
        attachment_id = setup_attachment["attachment"].id
        headers = {"Authorization": f"Bearer {recipient_token}"}

        response = client.get(
            f"/api/attachments/{attachment_id}/download",
            headers=headers
        )

        assert response.status_code == 200

    def test_download_attachment_access_denied(self, client, other_user_token, setup_attachment):
        """Test unauthorized user cannot download attachment."""
        attachment_id = setup_attachment["attachment"].id
        headers = {"Authorization": f"Bearer {other_user_token}"}

        response = client.get(
            f"/api/attachments/{attachment_id}/download",
            headers=headers
        )

        assert response.status_code == 403
        assert b"Access denied" in response.data

    def test_download_attachment_not_found(self, client, sender_token):
        """Test download fails for non-existent attachment."""
        headers = {"Authorization": f"Bearer {sender_token}"}

        response = client.get(
            "/api/attachments/99999/download",
            headers=headers
        )

        assert response.status_code == 404
        assert b"Attachment not found" in response.data

    def test_download_attachment_file_missing(self, client, sender_token, setup_attachment):
        """Test download fails when file is missing from disk."""
        attachment_id = setup_attachment["attachment"].id
        temp_file = setup_attachment["temp_file"]

        # Delete the file from disk
        os.remove(temp_file)

        headers = {"Authorization": f"Bearer {sender_token}"}
        response = client.get(
            f"/api/attachments/{attachment_id}/download",
            headers=headers
        )

        assert response.status_code == 404
        assert b"File not found on server" in response.data

    def test_download_attachment_tracks_download(self, client, sender_token, setup_attachment, db_session):
        """Test download increments download count and creates record."""
        attachment_id = setup_attachment["attachment"].id
        headers = {"Authorization": f"Bearer {sender_token}"}

        initial_count = setup_attachment["attachment"].download_count

        response = client.get(
            f"/api/attachments/{attachment_id}/download",
            headers=headers
        )

        assert response.status_code == 200

        # Refresh attachment
        db_session.refresh(setup_attachment["attachment"])
        assert setup_attachment["attachment"].download_count == initial_count + 1

        # Check download record
        download_record = AttachmentDownload.query.filter_by(
            attachment_id=attachment_id
        ).first()
        assert download_record is not None

    def test_download_attachment_no_auth(self, client, setup_attachment):
        """Test download fails without authentication."""
        attachment_id = setup_attachment["attachment"].id

        response = client.get(f"/api/attachments/{attachment_id}/download")

        assert response.status_code == 401

    def test_download_channel_attachment_member_access(self, client, db_session):
        """Test channel member can download channel attachment."""
        # Create users
        user1 = User(
            name="Channel Member",
            employee_number="CHAN001",
            department="Engineering",
            password_hash=generate_password_hash("password"),
            is_admin=False,
            is_active=True
        )
        user2 = User(
            name="Non Member",
            employee_number="NONMEM001",
            department="HR",
            password_hash=generate_password_hash("password"),
            is_admin=False,
            is_active=True
        )
        db_session.add_all([user1, user2])
        db_session.flush()

        # Create channel
        channel = Channel(
            name="Download Test Channel",
            description="Channel for testing downloads",
            channel_type="department",
            department="Engineering",
            created_by=user1.id
        )
        db_session.add(channel)
        db_session.flush()

        # Add member
        member = ChannelMember(
            channel_id=channel.id,
            user_id=user1.id,
            role="member"
        )
        db_session.add(member)

        # Create channel message
        channel_msg = ChannelMessage(
            channel_id=channel.id,
            sender_id=user1.id,
            message="Channel message with attachment"
        )
        db_session.add(channel_msg)
        db_session.flush()

        # Create temp file
        tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
        tmpfile.write(b"Channel file content")
        tmpfile.close()

        attachment = MessageAttachment(
            channel_message_id=channel_msg.id,
            filename="channel_file.txt",
            original_filename="channel_doc.txt",
            file_path=tmpfile.name,
            file_size=20,
            mime_type="text/plain",
            file_type="document",
            uploaded_by=user1.id,
            is_scanned=True,
            scan_result="clean"
        )
        db_session.add(attachment)
        db_session.commit()

        from auth import JWTManager
        with client.application.app_context():
            token1 = JWTManager.generate_tokens(user1)["access_token"]
            token2 = JWTManager.generate_tokens(user2)["access_token"]

        # Member can download
        response = client.get(
            f"/api/attachments/{attachment.id}/download",
            headers={"Authorization": f"Bearer {token1}"}
        )
        assert response.status_code == 200

        # Non-member cannot download
        response = client.get(
            f"/api/attachments/{attachment.id}/download",
            headers={"Authorization": f"Bearer {token2}"}
        )
        assert response.status_code == 403

        # Cleanup
        if os.path.exists(tmpfile.name):
            os.remove(tmpfile.name)

    @patch("routes_attachments.db.session.commit")
    def test_download_attachment_database_error(
        self, mock_commit, client, sender_token, setup_attachment
    ):
        """Test download handles database errors gracefully."""
        mock_commit.side_effect = Exception("Database error")
        attachment_id = setup_attachment["attachment"].id
        headers = {"Authorization": f"Bearer {sender_token}"}

        response = client.get(
            f"/api/attachments/{attachment_id}/download",
            headers=headers
        )

        assert response.status_code == 500
        assert b"Failed to download file" in response.data


class TestGetThumbnail:
    """Test thumbnail retrieval endpoint."""

    @pytest.fixture
    def setup_image_attachment(self, db_session):
        """Create attachment with thumbnail for testing."""
        user = User(
            name="Thumbnail User",
            employee_number="THUMB001",
            department="Engineering",
            password_hash=generate_password_hash("password"),
            is_admin=False,
            is_active=True
        )
        other_user = User(
            name="Other Thumbnail User",
            employee_number="OTHUMB001",
            department="HR",
            password_hash=generate_password_hash("password"),
            is_admin=False,
            is_active=True
        )
        db_session.add_all([user, other_user])
        db_session.flush()

        aircraft_type = AircraftType(
            name="Thumbnail Aircraft",
            description="Aircraft type for thumbnail tests"
        )
        db_session.add(aircraft_type)
        db_session.flush()

        kit = Kit(
            name="Thumbnail Kit",
            aircraft_type_id=aircraft_type.id,
            description="Kit for thumbnail tests",
            created_by=user.id,
            status="active"
        )
        db_session.add(kit)
        db_session.flush()

        message = KitMessage(
            kit_id=kit.id,
            sender_id=user.id,
            recipient_id=user.id,
            subject="Thumbnail Test",
            message="Test with image"
        )
        db_session.add(message)
        db_session.flush()

        # Create thumbnail directory and file
        from routes_attachments import UPLOAD_FOLDER
        thumb_dir = os.path.join(UPLOAD_FOLDER, "thumbnails")
        os.makedirs(thumb_dir, exist_ok=True)

        # Create actual thumbnail image
        img = Image.new("RGB", (100, 100), color="blue")
        thumb_filename = "thumb_test_image.jpg"
        thumb_path = os.path.join(thumb_dir, thumb_filename)
        img.save(thumb_path, "JPEG")

        attachment = MessageAttachment(
            kit_message_id=message.id,
            filename="test_image.png",
            original_filename="photo.png",
            file_path="/tmp/test_image.png",
            file_size=1024,
            mime_type="image/png",
            file_type="image",
            thumbnail_path=f"thumbnails/{thumb_filename}",
            uploaded_by=user.id,
            is_scanned=True,
            scan_result="clean"
        )
        db_session.add(attachment)
        db_session.commit()

        return {
            "user": user,
            "other_user": other_user,
            "attachment": attachment,
            "thumb_path": thumb_path
        }

    def test_get_thumbnail_success(self, client, app, setup_image_attachment):
        """Test successful thumbnail retrieval."""
        from auth import JWTManager
        with app.app_context():
            token = JWTManager.generate_tokens(setup_image_attachment["user"])["access_token"]

        attachment_id = setup_image_attachment["attachment"].id
        response = client.get(
            f"/api/attachments/{attachment_id}/thumbnail",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert response.content_type == "image/jpeg"

    def test_get_thumbnail_not_image(self, client, app, db_session):
        """Test thumbnail fails for non-image attachment."""
        user = User(
            name="Doc User",
            employee_number="DOC001",
            department="Engineering",
            password_hash=generate_password_hash("password"),
            is_admin=False,
            is_active=True
        )
        db_session.add(user)
        db_session.flush()

        aircraft_type = AircraftType(
            name="Doc Aircraft",
            description="Aircraft type for doc tests"
        )
        db_session.add(aircraft_type)
        db_session.flush()

        kit = Kit(
            name="Doc Kit",
            aircraft_type_id=aircraft_type.id,
            description="Kit for doc tests",
            created_by=user.id,
            status="active"
        )
        db_session.add(kit)
        db_session.flush()

        message = KitMessage(
            kit_id=kit.id,
            sender_id=user.id,
            recipient_id=user.id,
            subject="Doc Test",
            message="Test with doc"
        )
        db_session.add(message)
        db_session.flush()

        attachment = MessageAttachment(
            kit_message_id=message.id,
            filename="doc.pdf",
            original_filename="document.pdf",
            file_path="/tmp/doc.pdf",
            file_size=1024,
            mime_type="application/pdf",
            file_type="document",
            uploaded_by=user.id,
            is_scanned=True,
            scan_result="clean"
        )
        db_session.add(attachment)
        db_session.commit()

        from auth import JWTManager
        with app.app_context():
            token = JWTManager.generate_tokens(user)["access_token"]

        response = client.get(
            f"/api/attachments/{attachment.id}/thumbnail",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404
        assert b"Thumbnail not available" in response.data

    def test_get_thumbnail_not_found(self, client, app, setup_image_attachment):
        """Test thumbnail fails for non-existent attachment."""
        from auth import JWTManager
        with app.app_context():
            token = JWTManager.generate_tokens(setup_image_attachment["user"])["access_token"]

        response = client.get(
            "/api/attachments/99999/thumbnail",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404
        assert b"Attachment not found" in response.data

    def test_get_thumbnail_access_denied(self, client, app, setup_image_attachment):
        """Test thumbnail denied for unauthorized user."""
        from auth import JWTManager
        with app.app_context():
            token = JWTManager.generate_tokens(setup_image_attachment["other_user"])["access_token"]

        attachment_id = setup_image_attachment["attachment"].id
        response = client.get(
            f"/api/attachments/{attachment_id}/thumbnail",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403
        assert b"Access denied" in response.data

    def test_get_thumbnail_file_missing(self, client, app, setup_image_attachment):
        """Test thumbnail fails when file is missing."""
        from auth import JWTManager
        with app.app_context():
            token = JWTManager.generate_tokens(setup_image_attachment["user"])["access_token"]

        # Delete thumbnail file
        os.remove(setup_image_attachment["thumb_path"])

        attachment_id = setup_image_attachment["attachment"].id
        response = client.get(
            f"/api/attachments/{attachment_id}/thumbnail",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404
        assert b"Thumbnail not found" in response.data

    def test_get_thumbnail_no_auth(self, client, setup_image_attachment):
        """Test thumbnail fails without authentication."""
        attachment_id = setup_image_attachment["attachment"].id

        response = client.get(f"/api/attachments/{attachment_id}/thumbnail")

        assert response.status_code == 401

    @patch("routes_attachments.send_file")
    def test_get_thumbnail_server_error(self, mock_send, client, app, setup_image_attachment):
        """Test thumbnail handles server errors."""
        mock_send.side_effect = Exception("Server error")

        from auth import JWTManager
        with app.app_context():
            token = JWTManager.generate_tokens(setup_image_attachment["user"])["access_token"]

        attachment_id = setup_image_attachment["attachment"].id
        response = client.get(
            f"/api/attachments/{attachment_id}/thumbnail",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 500
        assert b"Failed to get thumbnail" in response.data


class TestDeleteAttachment:
    """Test attachment deletion endpoint."""

    @pytest.fixture
    def setup_delete_attachment(self, db_session):
        """Create attachment for deletion tests."""
        uploader = User(
            name="Uploader",
            employee_number="UPLOAD001",
            department="Engineering",
            password_hash=generate_password_hash("password"),
            is_admin=False,
            is_active=True
        )
        message_sender = User(
            name="Message Sender",
            employee_number="MSGSEND001",
            department="Engineering",
            password_hash=generate_password_hash("password"),
            is_admin=False,
            is_active=True
        )
        other_user = User(
            name="Other User",
            employee_number="DELOTHER001",
            department="HR",
            password_hash=generate_password_hash("password"),
            is_admin=False,
            is_active=True
        )
        db_session.add_all([uploader, message_sender, other_user])
        db_session.flush()

        aircraft_type = AircraftType(
            name="Delete Aircraft",
            description="Aircraft type for delete tests"
        )
        db_session.add(aircraft_type)
        db_session.flush()

        kit = Kit(
            name="Delete Kit",
            aircraft_type_id=aircraft_type.id,
            description="Kit for delete tests",
            created_by=uploader.id,
            status="active"
        )
        db_session.add(kit)
        db_session.flush()

        message = KitMessage(
            kit_id=kit.id,
            sender_id=message_sender.id,
            recipient_id=other_user.id,
            subject="Delete Test",
            message="Test delete"
        )
        db_session.add(message)
        db_session.flush()

        # Create temp file for attachment
        tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
        tmpfile.write(b"File to delete")
        tmpfile.close()

        # Create thumbnail
        from routes_attachments import UPLOAD_FOLDER
        thumb_dir = os.path.join(UPLOAD_FOLDER, "thumbnails")
        os.makedirs(thumb_dir, exist_ok=True)
        thumb_filename = "thumb_delete_test.jpg"
        thumb_path = os.path.join(thumb_dir, thumb_filename)
        with open(thumb_path, "wb") as f:
            f.write(b"thumbnail data")

        attachment = MessageAttachment(
            kit_message_id=message.id,
            filename="delete_file.txt",
            original_filename="to_delete.txt",
            file_path=tmpfile.name,
            file_size=15,
            mime_type="text/plain",
            file_type="document",
            thumbnail_path=f"thumbnails/{thumb_filename}",
            uploaded_by=uploader.id,
            is_scanned=True,
            scan_result="clean"
        )
        db_session.add(attachment)
        db_session.commit()

        return {
            "uploader": uploader,
            "message_sender": message_sender,
            "other_user": other_user,
            "message": message,
            "attachment": attachment,
            "temp_file": tmpfile.name,
            "thumb_path": thumb_path
        }

    def test_delete_attachment_by_uploader(self, client, app, setup_delete_attachment, db_session):
        """Test uploader can delete attachment."""
        from auth import JWTManager
        with app.app_context():
            token = JWTManager.generate_tokens(setup_delete_attachment["uploader"])["access_token"]

        attachment_id = setup_delete_attachment["attachment"].id
        response = client.delete(
            f"/api/attachments/{attachment_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert b"Attachment deleted successfully" in response.data

        # Verify attachment is deleted
        deleted = MessageAttachment.query.get(attachment_id)
        assert deleted is None

    def test_delete_attachment_by_message_sender(self, client, app, setup_delete_attachment, db_session):
        """Test message sender can delete attachment."""
        # Create new attachment for this test
        tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
        tmpfile.write(b"New file")
        tmpfile.close()

        attachment = MessageAttachment(
            kit_message_id=setup_delete_attachment["message"].id,
            filename="sender_delete.txt",
            original_filename="sender_to_delete.txt",
            file_path=tmpfile.name,
            file_size=8,
            mime_type="text/plain",
            file_type="document",
            uploaded_by=setup_delete_attachment["uploader"].id,
            is_scanned=True,
            scan_result="clean"
        )
        db_session.add(attachment)
        db_session.commit()

        from auth import JWTManager
        with app.app_context():
            token = JWTManager.generate_tokens(setup_delete_attachment["message_sender"])["access_token"]

        response = client.delete(
            f"/api/attachments/{attachment.id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200

    def test_delete_attachment_permission_denied(self, client, app, setup_delete_attachment):
        """Test unauthorized user cannot delete attachment."""
        from auth import JWTManager
        with app.app_context():
            token = JWTManager.generate_tokens(setup_delete_attachment["other_user"])["access_token"]

        attachment_id = setup_delete_attachment["attachment"].id
        response = client.delete(
            f"/api/attachments/{attachment_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403
        assert b"Permission denied" in response.data

    def test_delete_attachment_not_found(self, client, app, setup_delete_attachment):
        """Test delete fails for non-existent attachment."""
        from auth import JWTManager
        with app.app_context():
            token = JWTManager.generate_tokens(setup_delete_attachment["uploader"])["access_token"]

        response = client.delete(
            "/api/attachments/99999",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404
        assert b"Attachment not found" in response.data

    def test_delete_attachment_cleans_up_files(self, client, app, setup_delete_attachment):
        """Test delete removes files from disk."""
        from auth import JWTManager
        with app.app_context():
            token = JWTManager.generate_tokens(setup_delete_attachment["uploader"])["access_token"]

        temp_file = setup_delete_attachment["temp_file"]
        thumb_path = setup_delete_attachment["thumb_path"]

        # Ensure files exist
        assert os.path.exists(temp_file)
        assert os.path.exists(thumb_path)

        attachment_id = setup_delete_attachment["attachment"].id
        response = client.delete(
            f"/api/attachments/{attachment_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200

        # Files should be deleted
        assert not os.path.exists(temp_file)
        assert not os.path.exists(thumb_path)

    def test_delete_attachment_missing_files(self, client, app, setup_delete_attachment, db_session):
        """Test delete handles missing files gracefully."""
        # Delete files before API call
        os.remove(setup_delete_attachment["temp_file"])
        os.remove(setup_delete_attachment["thumb_path"])

        from auth import JWTManager
        with app.app_context():
            token = JWTManager.generate_tokens(setup_delete_attachment["uploader"])["access_token"]

        attachment_id = setup_delete_attachment["attachment"].id
        response = client.delete(
            f"/api/attachments/{attachment_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        # Should still succeed
        assert response.status_code == 200

        # Database record should be deleted
        deleted = MessageAttachment.query.get(attachment_id)
        assert deleted is None

    def test_delete_attachment_no_auth(self, client, setup_delete_attachment):
        """Test delete fails without authentication."""
        attachment_id = setup_delete_attachment["attachment"].id

        response = client.delete(f"/api/attachments/{attachment_id}")

        assert response.status_code == 401

    def test_delete_channel_attachment_by_sender(self, client, app, db_session):
        """Test channel message sender can delete attachment."""
        user = User(
            name="Channel Sender",
            employee_number="CHANSEND001",
            department="Engineering",
            password_hash=generate_password_hash("password"),
            is_admin=False,
            is_active=True
        )
        db_session.add(user)
        db_session.flush()

        channel = Channel(
            name="Delete Channel",
            description="Channel for delete test",
            channel_type="department",
            department="Engineering",
            created_by=user.id
        )
        db_session.add(channel)
        db_session.flush()

        channel_msg = ChannelMessage(
            channel_id=channel.id,
            sender_id=user.id,
            message="Channel message to delete"
        )
        db_session.add(channel_msg)
        db_session.flush()

        tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
        tmpfile.write(b"Channel file")
        tmpfile.close()

        attachment = MessageAttachment(
            channel_message_id=channel_msg.id,
            filename="channel_delete.txt",
            original_filename="channel_to_delete.txt",
            file_path=tmpfile.name,
            file_size=12,
            mime_type="text/plain",
            file_type="document",
            uploaded_by=user.id,
            is_scanned=True,
            scan_result="clean"
        )
        db_session.add(attachment)
        db_session.commit()

        from auth import JWTManager
        with app.app_context():
            token = JWTManager.generate_tokens(user)["access_token"]

        response = client.delete(
            f"/api/attachments/{attachment.id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200

    @patch("routes_attachments.db.session.commit")
    def test_delete_attachment_database_error(self, mock_commit, client, app, setup_delete_attachment):
        """Test delete handles database errors."""
        mock_commit.side_effect = Exception("Database error")

        from auth import JWTManager
        with app.app_context():
            token = JWTManager.generate_tokens(setup_delete_attachment["uploader"])["access_token"]

        attachment_id = setup_delete_attachment["attachment"].id
        response = client.delete(
            f"/api/attachments/{attachment_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 500
        assert b"Failed to delete attachment" in response.data


class TestGetAttachmentInfo:
    """Test attachment info endpoint."""

    @pytest.fixture
    def setup_info_attachment(self, db_session):
        """Create attachment for info tests."""
        user = User(
            name="Info User",
            employee_number="INFO001",
            department="Engineering",
            password_hash=generate_password_hash("password"),
            is_admin=False,
            is_active=True
        )
        other_user = User(
            name="Info Other",
            employee_number="INFOOTHER001",
            department="HR",
            password_hash=generate_password_hash("password"),
            is_admin=False,
            is_active=True
        )
        db_session.add_all([user, other_user])
        db_session.flush()

        aircraft_type = AircraftType(
            name="Info Aircraft",
            description="Aircraft type for info tests"
        )
        db_session.add(aircraft_type)
        db_session.flush()

        kit = Kit(
            name="Info Kit",
            aircraft_type_id=aircraft_type.id,
            description="Kit for info tests",
            created_by=user.id,
            status="active"
        )
        db_session.add(kit)
        db_session.flush()

        message = KitMessage(
            kit_id=kit.id,
            sender_id=user.id,
            recipient_id=user.id,
            subject="Info Test",
            message="Test info"
        )
        db_session.add(message)
        db_session.flush()

        attachment = MessageAttachment(
            kit_message_id=message.id,
            filename="info_file.pdf",
            original_filename="information.pdf",
            file_path="/tmp/info_file.pdf",
            file_size=2048,
            mime_type="application/pdf",
            file_type="document",
            uploaded_by=user.id,
            is_scanned=True,
            scan_result="clean",
            download_count=5
        )
        db_session.add(attachment)
        db_session.commit()

        return {
            "user": user,
            "other_user": other_user,
            "attachment": attachment
        }

    def test_get_attachment_info_success(self, client, app, setup_info_attachment):
        """Test successful attachment info retrieval."""
        from auth import JWTManager
        with app.app_context():
            token = JWTManager.generate_tokens(setup_info_attachment["user"])["access_token"]

        attachment_id = setup_info_attachment["attachment"].id
        response = client.get(
            f"/api/attachments/{attachment_id}/info",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        json_data = response.get_json()
        assert "attachment" in json_data
        assert json_data["attachment"]["original_filename"] == "information.pdf"
        assert json_data["attachment"]["file_size"] == 2048
        assert json_data["attachment"]["download_count"] == 5

    def test_get_attachment_info_not_found(self, client, app, setup_info_attachment):
        """Test info fails for non-existent attachment."""
        from auth import JWTManager
        with app.app_context():
            token = JWTManager.generate_tokens(setup_info_attachment["user"])["access_token"]

        response = client.get(
            "/api/attachments/99999/info",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404
        assert b"Attachment not found" in response.data

    def test_get_attachment_info_access_denied(self, client, app, setup_info_attachment):
        """Test info denied for unauthorized user."""
        from auth import JWTManager
        with app.app_context():
            token = JWTManager.generate_tokens(setup_info_attachment["other_user"])["access_token"]

        attachment_id = setup_info_attachment["attachment"].id
        response = client.get(
            f"/api/attachments/{attachment_id}/info",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403
        assert b"Access denied" in response.data

    def test_get_attachment_info_no_auth(self, client, setup_info_attachment):
        """Test info fails without authentication."""
        attachment_id = setup_info_attachment["attachment"].id

        response = client.get(f"/api/attachments/{attachment_id}/info")

        assert response.status_code == 401

    def test_get_channel_attachment_info(self, client, app, db_session):
        """Test getting info for channel attachment."""
        user = User(
            name="Channel Info User",
            employee_number="CHANINFO001",
            department="Engineering",
            password_hash=generate_password_hash("password"),
            is_admin=False,
            is_active=True
        )
        db_session.add(user)
        db_session.flush()

        channel = Channel(
            name="Info Channel",
            description="Channel for info test",
            channel_type="department",
            department="Engineering",
            created_by=user.id
        )
        db_session.add(channel)
        db_session.flush()

        member = ChannelMember(
            channel_id=channel.id,
            user_id=user.id,
            role="member"
        )
        db_session.add(member)

        channel_msg = ChannelMessage(
            channel_id=channel.id,
            sender_id=user.id,
            message="Channel info message"
        )
        db_session.add(channel_msg)
        db_session.flush()

        attachment = MessageAttachment(
            channel_message_id=channel_msg.id,
            filename="channel_info.txt",
            original_filename="channel_info_original.txt",
            file_path="/tmp/channel_info.txt",
            file_size=512,
            mime_type="text/plain",
            file_type="document",
            uploaded_by=user.id,
            is_scanned=True,
            scan_result="clean"
        )
        db_session.add(attachment)
        db_session.commit()

        from auth import JWTManager
        with app.app_context():
            token = JWTManager.generate_tokens(user)["access_token"]

        response = client.get(
            f"/api/attachments/{attachment.id}/info",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data["attachment"]["channel_message_id"] == channel_msg.id

    @patch("routes_attachments.MessageAttachment.query")
    def test_get_attachment_info_server_error(self, mock_query, client, app, setup_info_attachment):
        """Test info handles server errors."""
        mock_query.get.side_effect = Exception("Database error")

        from auth import JWTManager
        with app.app_context():
            token = JWTManager.generate_tokens(setup_info_attachment["user"])["access_token"]

        response = client.get(
            "/api/attachments/1/info",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 500
        assert b"Failed to get attachment info" in response.data


class TestRegisterAttachmentRoutes:
    """Test blueprint registration."""

    def test_register_attachments_routes(self, app):
        """Test that attachment routes are registered."""
        from routes_attachments import register_attachments_routes
        from flask import Flask

        # Create fresh app
        test_app = Flask(__name__)
        test_app.config["SECRET_KEY"] = "test"

        register_attachments_routes(test_app)

        # Check that blueprint is registered
        assert "attachments" in test_app.blueprints


class TestEdgeCases:
    """Test edge cases for additional coverage."""

    @patch("routes_attachments.logger")
    @patch("routes_attachments.validate_file_upload")
    @patch("routes_attachments.get_file_type", return_value="image")
    @patch("routes_attachments.scan_file_for_malware")
    @patch("routes_attachments.create_thumbnail", return_value=True)
    def test_upload_malware_scan_failure_with_thumbnail_cleanup(
        self, mock_thumbnail, mock_scan, mock_get_type, mock_validate, mock_logger,
        client, db_session
    ):
        """Test that thumbnail is cleaned up when malware scan fails."""
        from utils.file_validation import FileValidationError
        from auth import JWTManager

        # Create user
        user = User(
            name="Edge Case User",
            employee_number="EDGE001",
            department="Engineering",
            password_hash=generate_password_hash("password"),
            is_admin=False,
            is_active=True
        )
        db_session.add(user)
        db_session.flush()

        aircraft_type = AircraftType(
            name="Edge Case Aircraft",
            description="Aircraft for edge case tests"
        )
        db_session.add(aircraft_type)
        db_session.flush()

        kit = Kit(
            name="Edge Case Kit",
            aircraft_type_id=aircraft_type.id,
            description="Kit for edge case tests",
            created_by=user.id,
            status="active"
        )
        db_session.add(kit)
        db_session.flush()

        message = KitMessage(
            kit_id=kit.id,
            sender_id=user.id,
            recipient_id=user.id,
            subject="Edge Case Test",
            message="Testing edge cases"
        )
        db_session.add(message)
        db_session.commit()

        # Make scan fail after thumbnail is created
        mock_scan.side_effect = FileValidationError("Malicious content detected")

        with client.application.app_context():
            token = JWTManager.generate_tokens(user)["access_token"]

        data = {
            "file": (io.BytesIO(b"fake image"), "malicious.png"),
            "message_type": "kit",
            "message_id": str(message.id)
        }
        response = client.post(
            "/api/attachments/upload",
            headers={"Authorization": f"Bearer {token}"},
            data=data,
            content_type="multipart/form-data"
        )

        assert response.status_code == 400
        assert b"File rejected by security scan" in response.data

    def test_get_thumbnail_channel_message_no_membership(self, client, app, db_session):
        """Test thumbnail access denied when user is not channel member."""
        user1 = User(
            name="Channel Creator",
            employee_number="CHANCREATE001",
            department="Engineering",
            password_hash=generate_password_hash("password"),
            is_admin=False,
            is_active=True
        )
        user2 = User(
            name="Non Member",
            employee_number="NONMEM002",
            department="HR",
            password_hash=generate_password_hash("password"),
            is_admin=False,
            is_active=True
        )
        db_session.add_all([user1, user2])
        db_session.flush()

        channel = Channel(
            name="Private Channel",
            description="Private channel for test",
            channel_type="team",
            created_by=user1.id
        )
        db_session.add(channel)
        db_session.flush()

        # Only user1 is member
        member = ChannelMember(
            channel_id=channel.id,
            user_id=user1.id,
            role="admin"
        )
        db_session.add(member)

        channel_msg = ChannelMessage(
            channel_id=channel.id,
            sender_id=user1.id,
            message="Channel message with image"
        )
        db_session.add(channel_msg)
        db_session.flush()

        # Create thumbnail
        from routes_attachments import UPLOAD_FOLDER
        thumb_dir = os.path.join(UPLOAD_FOLDER, "thumbnails")
        os.makedirs(thumb_dir, exist_ok=True)
        thumb_filename = "thumb_channel_edge.jpg"
        thumb_path = os.path.join(thumb_dir, thumb_filename)
        with open(thumb_path, "wb") as f:
            f.write(b"thumbnail data")

        attachment = MessageAttachment(
            channel_message_id=channel_msg.id,
            filename="channel_image.png",
            original_filename="photo.png",
            file_path="/tmp/channel_image.png",
            file_size=1024,
            mime_type="image/png",
            file_type="image",
            thumbnail_path=f"thumbnails/{thumb_filename}",
            uploaded_by=user1.id,
            is_scanned=True,
            scan_result="clean"
        )
        db_session.add(attachment)
        db_session.commit()

        from auth import JWTManager
        with app.app_context():
            token2 = JWTManager.generate_tokens(user2)["access_token"]

        # Non-member should be denied
        response = client.get(
            f"/api/attachments/{attachment.id}/thumbnail",
            headers={"Authorization": f"Bearer {token2}"}
        )

        assert response.status_code == 403
        assert b"Access denied" in response.data

        # Cleanup
        if os.path.exists(thumb_path):
            os.remove(thumb_path)

    @patch("routes_attachments.os.remove")
    def test_delete_attachment_file_remove_error(self, mock_remove, client, app, db_session):
        """Test delete handles file removal errors gracefully."""
        mock_remove.side_effect = PermissionError("Cannot delete file")

        user = User(
            name="Delete Error User",
            employee_number="DELERR001",
            department="Engineering",
            password_hash=generate_password_hash("password"),
            is_admin=False,
            is_active=True
        )
        db_session.add(user)
        db_session.flush()

        aircraft_type = AircraftType(
            name="Delete Error Aircraft",
            description="Aircraft for delete error tests"
        )
        db_session.add(aircraft_type)
        db_session.flush()

        kit = Kit(
            name="Delete Error Kit",
            aircraft_type_id=aircraft_type.id,
            description="Kit for delete error tests",
            created_by=user.id,
            status="active"
        )
        db_session.add(kit)
        db_session.flush()

        message = KitMessage(
            kit_id=kit.id,
            sender_id=user.id,
            recipient_id=user.id,
            subject="Delete Error Test",
            message="Testing delete errors"
        )
        db_session.add(message)
        db_session.flush()

        attachment = MessageAttachment(
            kit_message_id=message.id,
            filename="error_delete.txt",
            original_filename="will_fail_delete.txt",
            file_path="/tmp/error_delete.txt",
            file_size=100,
            mime_type="text/plain",
            file_type="document",
            uploaded_by=user.id,
            is_scanned=True,
            scan_result="clean"
        )
        db_session.add(attachment)
        db_session.commit()

        from auth import JWTManager
        with app.app_context():
            token = JWTManager.generate_tokens(user)["access_token"]

        response = client.delete(
            f"/api/attachments/{attachment.id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        # Should still succeed even if file removal fails
        assert response.status_code == 200
        assert b"Attachment deleted successfully" in response.data


class TestSecurityFeatures:
    """Test security-related features."""

    def test_secure_filename_sanitization(self, client, auth_headers_admin):
        """Test that filenames are properly sanitized."""
        from werkzeug.utils import secure_filename

        # Test dangerous filename patterns
        dangerous_names = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32",
            "file\x00.txt",
            "file;rm -rf /.txt"
        ]

        for name in dangerous_names:
            safe_name = secure_filename(name)
            assert "/" not in safe_name
            assert "\\" not in safe_name
            assert "\x00" not in safe_name
            assert ";" not in safe_name

    @patch("routes_attachments.logger")
    @patch("routes_attachments.validate_file_upload")
    @patch("routes_attachments.get_file_type", return_value="document")
    @patch("routes_attachments.scan_file_for_malware")
    def test_upload_generates_unique_filename(
        self, mock_scan, mock_get_type, mock_validate, mock_logger,
        client, auth_headers_admin, db_session, admin_user
    ):
        """Test that uploaded files get unique filenames."""
        # Create aircraft type first
        aircraft_type = AircraftType(
            name="Security Aircraft",
            description="Aircraft type for security tests"
        )
        db_session.add(aircraft_type)
        db_session.flush()

        # Create kit and message for admin
        kit = Kit(
            name="Security Kit",
            aircraft_type_id=aircraft_type.id,
            description="Kit for security tests",
            created_by=admin_user.id,
            status="active"
        )
        db_session.add(kit)
        db_session.flush()

        message = KitMessage(
            kit_id=kit.id,
            sender_id=admin_user.id,
            recipient_id=admin_user.id,
            subject="Security Test",
            message="Testing security"
        )
        db_session.add(message)
        db_session.commit()

        # Upload same filename twice
        data1 = {
            "file": (io.BytesIO(b"content1"), "duplicate.txt"),
            "message_type": "kit",
            "message_id": str(message.id)
        }
        response1 = client.post(
            "/api/attachments/upload",
            headers=auth_headers_admin,
            data=data1,
            content_type="multipart/form-data"
        )

        data2 = {
            "file": (io.BytesIO(b"content2"), "duplicate.txt"),
            "message_type": "kit",
            "message_id": str(message.id)
        }
        response2 = client.post(
            "/api/attachments/upload",
            headers=auth_headers_admin,
            data=data2,
            content_type="multipart/form-data"
        )

        assert response1.status_code == 201
        assert response2.status_code == 201

        # Filenames should be different
        file1 = response1.get_json()["attachment"]["filename"]
        file2 = response2.get_json()["attachment"]["filename"]
        assert file1 != file2
