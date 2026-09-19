"""Main entry point for the Currency Exchange Converter application.

This script initializes and runs the graphical user interface (GUI) built with
Tkinter (ttk).

Typical usage:
    Run this script directly from the command line:
        $ python main.py
"""

import sys
from utils.classes.currency_converter import CurrencyExchangeConverter


def main():
    """Bootstraps application configurations and runs the main visual framework lifecycle loop."""

    try:
        # Instantiates the primary workspace controller window
        app = CurrencyExchangeConverter()

        # Executes background workers and establishes widget keyboard/mouse listeners
        app.run()

    except Exception as initialization_error:
        print(
            f"Critical Error: Failed to bootstrap application lifecycle: {initialization_error}",
            file=sys.stderr,
        )

        sys.exit(1)


if __name__ == "__main__":
    main()
