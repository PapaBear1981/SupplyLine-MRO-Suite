"""Contract tests that assert responses match the OpenAPI stub."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import schemathesis

SCHEMA_PATH = Path(__file__).resolve().parents[2] / "openapi.yaml"
schema = schemathesis.from_path(SCHEMA_PATH)


class DummyResponse:
    def __init__(self, status_code: int, json_body: dict | None = None, content_type: str = "application/json") -> None:
        self.status_code = status_code
        self.headers = {"Content-Type": content_type}
        self._json = json_body or {}
        self.text = json.dumps(self._json)

    def json(self):  # pragma: no cover - compatibility shim
        return self._json


@pytest.mark.contract
@pytest.mark.parametrize("status_code", [200])
def test_checkout_contract_valid_example(status_code):
    endpoint = schema["/checkout"]["post"]
    case = endpoint.make_case()
    case.body = {
        "toolId": "TL-100",
        "userId": "u-tech",
        "workOrder": "WO-123",
        "expectedReturn": "2024-01-10T12:00:00Z",
    }
    response = DummyResponse(
        status_code,
        json_body={
            "toolId": "TL-100",
            "holder": "u-tech",
            "status": "checkedOut",
            "dueBack": "2024-01-10T12:00:00Z",
        },
    )
    case.validate_response(response)


@pytest.mark.contract
def test_checkout_contract_missing_work_order_triggers_400():
    endpoint = schema["/checkout"]["post"]
    case = endpoint.make_case()
    case.body = {
        "toolId": "TL-100",
        "userId": "u-tech",
    }
    response = DummyResponse(400, json_body={"message": "workOrder is required"})
    case.validate_response(response)


@pytest.mark.contract
def test_tool_response_contains_required_fields():
    endpoint = schema["/tools/{toolId}"]["get"]
    response = DummyResponse(
        200,
        json_body={
            "toolId": "TL-100",
            "calibrationDue": "2024-01-10T12:00:00Z",
            "holder": None,
            "status": "available",
        },
    )
    endpoint.validate_response(response)


@pytest.mark.contract
def test_contract_breaking_change_detection():
    """Consumer style check that fails when critical fields disappear."""

    endpoint = schema["/return"]["post"]
    response = DummyResponse(
        200,
        json_body={
            "toolId": "TL-100",
            "status": "returned",
        },
    )
    endpoint.validate_response(response)

    breaking_response = DummyResponse(200, json_body={"toolId": "TL-100"})
    with pytest.raises(AssertionError):
        endpoint.validate_response(breaking_response)
