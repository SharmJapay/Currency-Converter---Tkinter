"""Configuration and Security Management Module.

This module handles application paths for both raw scripts and frozen executables,
manages persistent configuration settings, and provides secure encryption and
decryption layers for storing sensitive API keys using Fernet symmetric encryption.
"""

import os
import sys
import json
from cryptography.fernet import Fernet


class ConfigManager:
    """Manages application lifecycle directories, state maps, and symmetric cryptography engines."""

    def __init__(self) -> None:
        """Starts the initialization of the class and binds application paths."""

        self.bind_paths()

    def get_application_paths(self) -> dict:
        """Dynamically resolves the root directory path where the binary or script lives.

        This function accounts for whether the application is running as a standard
        Python script or bundled as a standalone executable (e.g., via PyInstaller).

        Returns
            dict: A dictionary containing absolute file paths for configuration,
            encryption keys, application state, rate caches, and image assets.
        """

        if getattr(sys, "frozen", False):
            # Target the true directory housing your (.exe) binary
            bundle_dir = sys._MEIPASS

            # Direct state files to the user's home folder profile matrix
            user_home_data_dir = os.path.join(
                os.path.expanduser("~"), ".currency_converter"
            )
            os.makedirs(user_home_data_dir, exist_ok=True)

            return {
                "config": os.path.join(user_home_data_dir, "config.json"),
                "key": os.path.join(user_home_data_dir, ".key"),
                "state": os.path.join(user_home_data_dir, "state_cache.json"),
                "rates": os.path.join(user_home_data_dir, "rates_cache.json"),
                "image": os.path.join(bundle_dir, "images", "logo.png"),
            }

        else:
            # Standard developer environment fallback setup structure
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            utils_dir = os.path.join(base_dir, "utils")

            return {
                "config": os.path.join(utils_dir, "config.json"),
                "key": os.path.join(utils_dir, ".key"),
                "state": os.path.join(utils_dir, "state_cache.json"),
                "rates": os.path.join(utils_dir, "rates_cache.json"),
                "image": os.path.join(base_dir, "images", "logo.png"),
            }

    def bind_paths(self) -> None:
        """Maps unified system path bindings onto functional instance parameters."""

        # Path Bindings Definition Matrix
        self.path = self.get_application_paths()

        # Set the base configuration path
        self.config_path = self.path["config"]
        self.key_path = self.path["key"]

        # Set the cache configuration paths
        self.state_cache_file = self.path["state"]
        self.rates_cache_file = self.path["rates"]

        # Set the image path
        self.image_file = self.path["image"]

    def get_or_create_encryption_key(self) -> bytes:
        """Fetches the encryption key from environment variables or generates a new one.

        If a key is not found in the environment, a new cryptographically secure
        Fernet key is generated and temporarily assigned to the session environment.

        Returns
            bytes: The 32 url-safe base64-encoded bytes encryption key used for ciphers.
        """

        # Check if the persistent key file already exists on disk
        if os.path.exists(self.key_path):
            try:
                with open(self.key_path, "rb") as key_file:
                    key_bytes = key_file.read().strip()

                    if len(key_bytes) == 44:
                        return key_bytes

            except Exception as e:
                # Create error logging for unsuccessful reading of persistent key file
                print(f"Error reading persistent key file: {e}")

        # Generate a brand new encryption key token if missing
        new_key = Fernet.generate_key()

        try:
            os.makedirs(os.path.dirname(self.key_path), exist_ok=True)

            temp_key_path = f"{self.key_path}.tmp"

            with open(temp_key_path, "wb") as key_file:
                key_file.write(new_key)
            os.replace(temp_key_path, self.key_path)

            return new_key

        except Exception as e:
            # Create error logging for unsuccessful serialization of encryption key
            print(f"Critical: Could not serialize encryption key token onto disk: {e}")

        return new_key

    def load_api_key(self) -> str:
        """Safely extracts the custom API Key out from local persistent JSON scopes.

        It reads the encrypted API key string from the local configuration file,
        retrieves the active encryption key, and decrypts it back to plain text.

        Returns
            str: The decrypted plain text API key if successful.
        """

        # Checks the configuration for api key and returns if available
        if os.path.exists(self.config_path):

            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Ensure data structure is a valid dictionary before reading keys
                if not isinstance(data, dict):
                    return

                encrypted_key = data.get("API_KEY")

                if not encrypted_key:
                    return

                # Fetch the encryption key and initialize the cipher
                secret_key = self.get_or_create_encryption_key()
                cipher = Fernet(secret_key)

                # Encode and convert key to bytes first
                cleaned_key = encrypted_key.strip().encode("utf-8")

                # Decrypt the cleaned API key
                decrypted_key = cipher.decrypt(cleaned_key)

                # Decode back to string for JSON storage
                return decrypted_key.decode("utf-8")

            except Exception as e:
                # Create error logging for cryptographic error
                print(
                    f"Cryptographic error detected. Scrubbing out-of-sync configurations: {e}"
                )

                # Automatically clear un-parsable configurations
                try:
                    if os.path.exists(self.config_path):
                        os.remove(self.config_path)

                except Exception:
                    pass

    def save_api_key(self, api_key: str) -> bool:
        """Encapsulates and appends key state changes without altering user dropdown positions.

        Cleans whitespace, encrypts the provided API key string, merges it with
        any existing JSON configuration fields, and writes it back to disk safely.

        Args
            api_key (str): The raw, plain text API key provided by the user.

        Returns
            bool: True if the file directories were successfully verified and the
            encrypted configuration was saved to disk. False if an error occurs.
        """

        data = {}

        # Checks the configuration and loads data if available
        if os.path.exists(self.config_path):

            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    loaded_data = json.load(f)

                    if isinstance(loaded_data, dict):
                        data = loaded_data

            except Exception:
                pass

        try:
            # Setup the encryption cipher
            secret_key = self.get_or_create_encryption_key()
            cipher = Fernet(secret_key)

            # Encode and convert key to bytes first
            cleaned_key = api_key.strip().encode("utf-8")

            # Encrypt the cleaned API key
            encrypted_key = cipher.encrypt(cleaned_key)

            # Decode back to string for JSON storage, and update data structure
            data["API_KEY"] = encrypted_key.decode("utf-8")

            # Writes the updated data back to the file
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

            return True

        except Exception as e:
            # Create error logging for unsuccessful api encryption process
            print(f"Error saving encrypted API key: {e}")

            return False
