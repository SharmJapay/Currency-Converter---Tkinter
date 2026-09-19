"""Automated Unit Tests for the Configuration and Security Management Module.

Focuses on validating file path configurations, symmetric key lifecycle routines,
and automatic self-healing security triggers for corrupt data elements.
"""

import os
import json
from unittest.mock import patch
import pytest

from utils.classes.config_manager import ConfigManager


@pytest.fixture
def sandbox_config_manager(tmp_path):
    """Provides an isolated ConfigManager sandbox mapping configurations inside a temporary directory."""
    with patch.object(ConfigManager, "get_application_paths") as mock_paths:
        mock_paths.return_value = {
            "config": str(tmp_path / "config.json"),
            "key": str(tmp_path / ".key"),
            "state": str(tmp_path / "state_cache.json"),
            "rates": str(tmp_path / "rates_cache.json"),
            "image": str(tmp_path / "logo.png"),
        }
        cm = ConfigManager()
        yield cm


def test_key_lifecycle_persistence(sandbox_config_manager):
    """Verifies that encryption keys are uniquely created and reliably re-read from disk blocks."""
    cm = sandbox_config_manager
    assert not os.path.exists(cm.key_path)

    # First access: Key must generate dynamically
    first_key = cm.get_or_create_encryption_key()
    assert (
        len(first_key) == 44
    )  # Standard base64-encoded Fernet string format byte footprint length check
    assert os.path.exists(cm.key_path)

    # Second access: Key should match the recorded disk footprint exactly
    second_key = cm.get_or_create_encryption_key()
    assert first_key == second_key


def test_credential_encryption_and_decryption_cycle(sandbox_config_manager):
    """Validates that plaintext API secrets undergo pristine cipher conversions and return unharmed."""
    cm = sandbox_config_manager
    raw_secret_key = "exchangerate_api_live_token_string_example_xyz"

    # Encapsulate and write data blocks safely to configuration profiles
    save_status = cm.save_api_key(raw_secret_key)
    assert save_status is True
    assert os.path.exists(cm.config_path)

    # Ensure plain text data was encrypted and not recorded verbatim
    with open(cm.config_path, "r", encoding="utf-8") as f:
        disk_payload = json.load(f)
    assert disk_payload["API_KEY"] != raw_secret_key

    # Decrypt block and confirm plain text matches original string
    extracted_token = cm.load_api_key()
    assert extracted_token == raw_secret_key


def test_self_healing_intercept_on_malformed_tokens(sandbox_config_manager):
    """Confirms that out-of-sync encryption tokens trigger self-healing to prevent application state hanging."""
    cm = sandbox_config_manager

    # Write corrupted garbage structural strings straight into standard storage targets
    os.makedirs(os.path.dirname(cm.config_path), exist_ok=True)
    with open(cm.config_path, "w", encoding="utf-8") as f:
        json.dump({"API_KEY": "completely_unreadable_corrupt_cryptographic_token"}, f)

    # Parsing execution loop must intercept cipher failure gracefully and scrub configuration state
    decrypted_key = cm.load_api_key()
    assert decrypted_key is None
    assert not os.path.exists(
        cm.config_path
    )  # File must be auto-purged to defuse loop locks
