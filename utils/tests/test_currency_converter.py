"""Automated Unit Tests for the Primary GUI Engine & Workspace Controller Class.

Focuses on validating keystroke character filtering, safe thread-to-UI update communications,
empty state field reset overrides, and local mathematical backup operations.
"""

import json
from unittest.mock import MagicMock, patch
import pytest
import requests

from utils.classes.config_manager import ConfigManager
from utils.classes.currency_converter import CurrencyExchangeConverter


@pytest.fixture
def headless_app_context():
    """Bootstraps a headless instantiation of the primary app framework to run tests safely without visual layouts."""
    with patch("requests.get") as mock_api_get:
        with patch.object(
            ConfigManager, "load_api_key", return_value="mock_valid_token"
        ):
            app = CurrencyExchangeConverter()
            app.withdraw()  # Suppresses visual rendering layouts
            yield app, mock_api_get
            try:
                app.destroy()
            except Exception:
                pass


def test_character_input_mask_validation(headless_app_context):
    """Validates real-time numeric entry validation rules checking algorithms."""
    app, _ = headless_app_context

    assert (
        app.validate_numeric_input("") is True
    )  # Allow clearing out the box while typing
    assert app.validate_numeric_input("150") is True  # Valid tracking integers
    assert (
        app.validate_numeric_input("150.35") is True
    )  # Valid tracking floating amounts
    assert (
        app.validate_numeric_input("150.35.1") is False
    )  # Reject tracking double decimal periods
    assert (
        app.validate_numeric_input("150a") is False
    )  # Reject standard alphabet injections


def test_blank_amount_field_reset_handling(headless_app_context):
    """Verifies that an empty amount input triggers an instantaneous readout reset instead of leaking prior text values."""
    app, _ = headless_app_context

    app.from_rate_combo.set("USD")
    app.to_rate_combo.set("EUR")
    app.amount_entry.delete(0, "end")
    app.amount_entry.insert(0, "")  # Simulate user backspacing or clearing input field

    app.trigger_immediate_conversion()
    assert app.result_label.cget("text") == "0.00 USD = 0.00 EUR"


def test_asynchronous_conversion_success_flow(headless_app_context):
    """Confirms successful API streams update display targets safely from running worker tasks across thread safe contexts."""
    app, mock_api_get = headless_app_context

    mock_payload = MagicMock()
    mock_payload.status_code = 200
    mock_payload.json.return_value = {"result": "success", "conversion_result": 92.45}
    mock_api_get.return_value = mock_payload

    app.from_rate_combo.set("USD")
    app.to_rate_combo.set("EUR")
    app.amount_entry.delete(0, "end")
    app.amount_entry.insert(0, "100.00")

    # Run background execution worker directly to process parsing mechanics synchronously
    app.async_convert("USD", "EUR", "100.00")
    app.update()  # Flush scheduled visual task steps flatly

    assert app.result_label.cget("text") == "100.00 USD = 92.45 EUR"
    assert app.loading is False


def test_defensive_offline_fallback_lifecycle(headless_app_context, tmp_path):
    """Validates network breaks drop safely into structured disk snapshot arrays using baseline cross multiplication math."""
    app, mock_api_get = headless_app_context

    mock_api_get.side_effect = requests.exceptions.RequestException(
        "Target connection dropped."
    )

    # Bind temporary rates paths storage definitions onto execution variables
    app.rates_cache_file = str(tmp_path / "rates_cache.json")
    fallback_rates = {"USD": 1.0, "EUR": 0.88, "GBP": 0.72}
    with open(app.rates_cache_file, "w", encoding="utf-8") as f:
        json.dump(fallback_rates, f)

    app.from_rate_combo.set("EUR")
    app.to_rate_combo.set("GBP")
    app.amount_entry.delete(0, "end")
    app.amount_entry.insert(0, "50.00")

    # Relative equation targets check logic:
    # (50.00 Amount / 0.88 EUR rate relative to USD) * 0.72 GBP rate relative to USD = 40.91 GBP
    app.async_convert("EUR", "GBP", "50.00")
    app.update()

    assert "40.91 GBP (Cached)" in app.result_label.cget("text")
    assert (
        app.loading is False
    )  # Validates that state cleanup hooks execute inside finally blocks across errors
