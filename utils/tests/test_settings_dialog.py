"""Automated Unit Tests for the Modal Configuration Dialog Module.

Focuses on validating modal parameter inheritance, credential tracking inputs,
and viewport coordinate bounds constraints.
"""

from unittest.mock import patch
import pytest

from utils.classes.config_manager import ConfigManager
from utils.classes.currency_converter import CurrencyExchangeConverter
from utils.classes.settings_dialog import SettingsDialog


@pytest.fixture
def parent_app_context():
    """Initializes the main Tk application driver environment to act as the modal layout parent frame anchor."""
    with patch.object(ConfigManager, "load_api_key", return_value="dummy_key"):
        app = CurrencyExchangeConverter()
        app.withdraw()  # Headless test mode configuration safety hook
        yield app
        try:
            app.destroy()
        except Exception:
            pass


def test_settings_dialog_initialization_and_inheritance(parent_app_context):
    """Verifies dialog windows safely capture style configurations and initialize variables correctly."""
    app = parent_app_context

    with patch.object(
        ConfigManager, "load_api_key", return_value="test_unmasked_token_abc"
    ):
        dialog = SettingsDialog(
            app, "clam", "#1e1e1e", "#2d2d2d", "#ffffff", "#007acc", "#005999"
        )
        dialog.withdraw()  # Suppress visual window generation tracking maps during tests execution loop

        # Verify values map properly across instance parameters
        assert dialog.dark_bg == "#1e1e1e"
        assert dialog.accent_color == "#007acc"
        assert dialog.api_key == "test_unmasked_token_abc"

        dialog.destroy()


def test_viewport_bounds_screening_intercept(parent_app_context):
    """Confirms offscreen position tracking variables filter out negative screen mappings safely to prevent coordinate layout anomalies."""
    app = parent_app_context

    # Place parent window location coordinates outside standard hardware view matrices (simulate multi-monitor overflow bugs)
    app.geometry("600x550+-250+-250")
    app.update()

    with patch.object(ConfigManager, "load_api_key", return_value=""):
        dialog = SettingsDialog(
            app, "clam", "#1e1e1e", "#2d2d2d", "#ffffff", "#007acc", "#005999"
        )
        dialog.withdraw()

        geometry_string = dialog.geometry()
        # Ensure coordinates are safely mapped to prevent off-screen UI rendering anomalies
        assert "+-" not in geometry_string

        dialog.destroy()
