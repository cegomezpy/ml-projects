"""Tests for the Open-Meteo archive client, with the HTTP call replaced by a stub."""

import json
from pathlib import Path
from typing import Any

import httpx
import pytest

from wh_forecast.data import open_meteo


class StubResponse:
    def __init__(self, payload: dict[str, Any], status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                "error",
                request=httpx.Request("GET", "http://x"),
                response=httpx.Response(self.status_code),
            )

    def json(self) -> dict[str, Any]:
        return self._payload


@pytest.fixture
def stub_http(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    calls: dict[str, Any] = {"payload": {}, "status": 200}

    def fake_get(url: str, params: dict[str, Any], timeout: float) -> StubResponse:
        calls["url"], calls["params"] = url, params
        return StubResponse(calls["payload"], calls["status"])

    monkeypatch.setattr(open_meteo.httpx, "get", fake_get)
    return calls


def test_hourly_fetch_saves_raw_response_under_location_name(
    stub_http: dict[str, Any], tmp_path: Path
) -> None:
    stub_http["payload"] = {"hourly": {"time": ["2024-01-01T00:00", "2024-01-01T01:00"]}}

    data = open_meteo.fetch_hourly(
        "havana", 23.0, -82.0, "2024-01-01", "2024-01-02", save_dir=tmp_path
    )

    saved = json.loads((tmp_path / "havana_hourly.json").read_text(encoding="utf-8"))
    assert saved == data == stub_http["payload"]


def test_hourly_fetch_requests_all_weather_variables(
    stub_http: dict[str, Any], tmp_path: Path
) -> None:
    stub_http["payload"] = {"hourly": {"time": []}}

    open_meteo.fetch_hourly("havana", 23.0, -82.0, "2024-01-01", "2024-01-02", save_dir=tmp_path)

    requested = stub_http["params"]["hourly"].split(",")
    assert {"shortwave_radiation", "direct_radiation", "diffuse_radiation", "cloud_cover"} <= set(
        requested
    )
    assert stub_http["params"]["latitude"] == 23.0


def test_hourly_fetch_error_is_raised_and_no_file_written(
    stub_http: dict[str, Any], tmp_path: Path
) -> None:
    stub_http["status"] = 500

    with pytest.raises(httpx.HTTPStatusError):
        open_meteo.fetch_hourly(
            "havana", 23.0, -82.0, "2024-01-01", "2024-01-02", save_dir=tmp_path
        )

    assert list(tmp_path.iterdir()) == []


def test_hourly_fetch_reports_number_of_saved_records(
    stub_http: dict[str, Any], tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    stub_http["payload"] = {"hourly": {"time": ["t1", "t2", "t3"]}}

    open_meteo.fetch_hourly("havana", 23.0, -82.0, "2024-01-01", "2024-01-02", save_dir=tmp_path)

    assert "3 hourly records" in capsys.readouterr().out


def test_hourly_fetch_network_failure_is_raised_and_no_file_written(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def failing_get(url: str, params: dict[str, Any], timeout: float) -> StubResponse:
        raise httpx.ConnectError("no network")

    monkeypatch.setattr(open_meteo.httpx, "get", failing_get)

    with pytest.raises(httpx.RequestError):
        open_meteo.fetch_hourly(
            "havana", 23.0, -82.0, "2024-01-01", "2024-01-02", save_dir=tmp_path
        )

    assert list(tmp_path.iterdir()) == []


def test_daily_fetch_error_is_raised_and_no_file_written(
    stub_http: dict[str, Any], tmp_path: Path
) -> None:
    stub_http["status"] = 503

    with pytest.raises(httpx.HTTPStatusError):
        open_meteo.fetch_historical(
            "havana", 23.0, -82.0, "2024-01-01", "2024-01-01", save_dir=tmp_path
        )

    assert list(tmp_path.iterdir()) == []


def test_daily_fetch_saves_raw_response(stub_http: dict[str, Any], tmp_path: Path) -> None:
    stub_http["payload"] = {"daily": {"time": ["2024-01-01"]}}

    data = open_meteo.fetch_historical(
        "havana", 23.0, -82.0, "2024-01-01", "2024-01-01", save_dir=tmp_path
    )

    assert json.loads((tmp_path / "havana_raw.json").read_text(encoding="utf-8")) == data
