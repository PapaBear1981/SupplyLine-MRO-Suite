import base64
from datetime import datetime
from io import BytesIO

import pytest

from models import Tool, ToolCalibration

@pytest.fixture(scope='module')
def _sample_png_bytes():
    """Return bytes for a minimal 1x1 PNG image."""
    png_base64 = (
        'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8Xw8AArMB9VIAtYEAAAAASUVORK5CYII='
    )
    return base64.b64decode(png_base64)


def test_avatar_upload_rejects_non_image(client, auth_headers):
    data = {
        'avatar': (BytesIO(b'not-an-image'), 'avatar.jpg', 'image/jpeg')
    }

    response = client.post(
        '/api/user/avatar',
        headers=auth_headers,
        data=data,
        content_type='multipart/form-data'
    )

    assert response.status_code == 400
    body = response.get_json()
    assert body is not None and 'error' in body


def test_avatar_upload_rejects_large_image(client, auth_headers, _sample_png_bytes, monkeypatch):
    monkeypatch.setitem(client.application.config, 'MAX_AVATAR_FILE_SIZE', 10)

    data = {
        'avatar': (BytesIO(_sample_png_bytes), 'avatar.png', 'image/png')
    }

    response = client.post(
        '/api/user/avatar',
        headers=auth_headers,
        data=data,
        content_type='multipart/form-data'
    )

    assert response.status_code == 413
    body = response.get_json()
    assert body is not None and 'error' in body


def test_bulk_import_rejects_invalid_csv(client, auth_headers):
    data = {
        'file': (BytesIO(b'\x00\x00malicious'), 'tools.csv', 'text/csv')
    }

    response = client.post(
        '/api/tools/bulk-import',
        headers=auth_headers,
        data=data,
        content_type='multipart/form-data'
    )

    assert response.status_code == 400
    assert 'error' in response.get_json()


def test_bulk_import_sanitizes_formula_cells(client, auth_headers, db_session):
    csv_content = (
        'tool_number,serial_number,description,condition,location,category\n'
        "FORM1,SN1,=cmd|'#/c calc'!A1,good,Main,General\n"
    )
    data = {
        'file': (BytesIO(csv_content.encode('utf-8')), 'tools.csv', 'text/csv')
    }

    response = client.post(
        '/api/tools/bulk-import',
        headers=auth_headers,
        data=data,
        content_type='multipart/form-data'
    )

    assert response.status_code in (200, 207)

    # Verify the tool was created with sanitized description
    with client.application.app_context():
        tool = Tool.query.filter_by(tool_number='FORM1', serial_number='SN1').first()
        assert tool is not None
        assert tool.description.startswith("'")
        # The sanitized description strips dangerous quotes during schema validation
        # but preserves the prefixed formula guard.
        assert tool.description.lstrip("'") == "=cmd|#/c calc!A1"


def test_calibration_certificate_upload_and_download(
    client,
    auth_headers,
    db_session,
    sample_tool,
    admin_user,
    tmp_path,
    monkeypatch
):
    monkeypatch.setitem(client.application.config, 'CALIBRATION_CERTIFICATE_FOLDER', str(tmp_path))
    monkeypatch.setitem(client.application.config, 'MAX_CALIBRATION_CERTIFICATE_FILE_SIZE', 1024 * 1024)

    calibration = ToolCalibration(
        tool_id=sample_tool.id,
        calibration_date=datetime.utcnow(),
        performed_by_user_id=admin_user.id,
        calibration_status='completed'
    )
    db_session.add(calibration)
    db_session.commit()

    pdf_bytes = b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF'
    upload_data = {
        'certificate': (BytesIO(pdf_bytes), 'calibration.pdf', 'application/pdf')
    }

    upload_response = client.post(
        f'/api/calibrations/{calibration.id}/certificate',
        headers=auth_headers,
        data=upload_data,
        content_type='multipart/form-data'
    )

    assert upload_response.status_code == 201
    upload_body = upload_response.get_json()
    assert upload_body is not None
    assert 'certificate' in upload_body
    certificate_filename = upload_body['certificate']

    download_response = client.get(
        f'/api/calibrations/{calibration.id}/certificate',
        headers=auth_headers
    )

    assert download_response.status_code == 200
    assert download_response.data.startswith(b'%PDF')
    content_disposition = download_response.headers.get('Content-Disposition', '')
    assert certificate_filename in content_disposition


def test_calibration_certificate_rejects_invalid_file(
    client,
    auth_headers,
    db_session,
    sample_tool,
    admin_user,
    tmp_path,
    monkeypatch
):
    monkeypatch.setitem(client.application.config, 'CALIBRATION_CERTIFICATE_FOLDER', str(tmp_path))

    calibration = ToolCalibration(
        tool_id=sample_tool.id,
        calibration_date=datetime.utcnow(),
        performed_by_user_id=admin_user.id,
        calibration_status='completed'
    )
    db_session.add(calibration)
    db_session.commit()

    upload_data = {
        'certificate': (BytesIO(b'<script>alert(1)</script>'), 'calibration.pd', 'application/pdf')
    }

    response = client.post(
        f'/api/calibrations/{calibration.id}/certificate',
        headers=auth_headers,
        data=upload_data,
        content_type='multipart/form-data'
    )

    assert response.status_code == 400
    body = response.get_json()
    assert body is not None and 'error' in body

    # Verify the certificate was not uploaded by trying to download it
    download_response = client.get(
        f'/api/calibrations/{calibration.id}/certificate',
        headers=auth_headers
    )
    assert download_response.status_code == 404
