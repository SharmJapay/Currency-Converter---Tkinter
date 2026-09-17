"""Main entry point for the Currency Exchange Converter application.

This script initializes and runs the graphical user interface (GUI) built with
Tkinter (ttk).

Typical usage:
    Run this script directly from the command line:
        $ python main.py
"""

from utils.classes.currency_converter import CurrencyExchangeConverter


def main():
    """Start the program and executes the application logic flow"""

    # Create an instance of converter class
    app = CurrencyExchangeConverter()
    app.run()
    app.mainloop()


if __name__ == "__main__":
    main()
