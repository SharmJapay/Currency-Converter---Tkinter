"""Currency Exchange Converter Application.

This module contains the main class for a graphical currency conversion program.
It allows users to convert amounts between different global currencies using
real-time or static exchange rates.

Attributes:
    loading (bool): Track active background network tasks.
    debounce_id (int): Variable container tracker for debouncing text strokes
    api_url (str): The link for the currency exchange rate server.
    status_indicator_dot (str): The indicator light for API connection status
    status_indicator_text (str): The text that states the API Connection status
    from_rate_combo (list): The list of currencies codes
    to_rate_combo (list): The list of currencie codes
    spinner_label (str): The loading text while conversion takes place
    amount_entry (str): The numerical amount value
    result_label (str): The result text from the conversion

Methods:
    setup_window() -> None       : Configures the window settings of the application in the center of screen.
    setup_style() -> None        : Configures the style properties of window and widgets.
    setup_api() -> None          : Configures the API key and url of currency exchange rate server.
    load_rates_cache() -> list   : Loads cached rates data safely to extract currency code lists.
    load_saved_state() -> dict   : Loads persistent storage details configurations safely.
    save_current_state() -> None : Serializes target workspace properties on execution modifications.
    build_gui() -> None          : Creates the layout design of the user interface.
    run() -> None                : Starts the application interface.
    initialize_currency_data() -> None : Asynchronously fetches initial list of currencies and validates server status.
    get_currencies() -> list | None    : Fetches or updates the latest currency exchange rates.
    validate_numeric_input() -> bool   : Character-level input mask checking routine.
    check_key(event) -> None     : Filters exchange rate codes every time a key is released.
    swap_currencies() -> None    : Interchanges combobox selected indices layout values cleanly.
    animate_spinner() -> None   : Animates a looping sequence of text frame indicators while thread is processing.
    trigger_debounced_conversion(event=None) -> None : Implements a 300ms delay timer execution intercept cascade.
    trigger_immediate_conversion(event=None) -> None : Spawns network task inside a worker thread to protect typing flow fluidity.
    async_convert(src, dest, amount) -> None : Handles HTTP requesting workflows and live graphical state loops.
    manual_reconnect(event=None) -> None : Triggers a manual background reconnection sequence when clicking the status bar.
    silent_background_retry() -> None: Quietly attempts to re-verify the API status every 60 seconds if offline.
"""

import os
import sys
import json
import threading
import time

from tkinter import *
from tkinter import messagebox
import tkinter.ttk as ttk

import requests
from dotenv import load_dotenv


class CurrencyExchangeConverter(Tk):
    """A created currency exchange converter class"""

    # Define color palette (dark mode) constants
    DARK_BG = "#1e1e1e"  # Main background
    SURFACE_BG = "#2d2d2d"  # Secondary background
    TEXT_FG = "#ffffff"  # Primary text color
    ACCENT_COLOR = "#007acc"  # Highlight color
    DEEP_ACCENT_COLOR = "#005999"  # Deep Highlight color
    COLOR_SUCCESS = "#2ea44f"  # Green status light
    COLOR_DANGER = "#cb2431"  # Red status light
    COLOR_IDLE = "#888888"  # Gray status light

    # State cache configuration path
    # __file__ is at: utils/classes/currency_converter.py
    # Going up exactly two folder levels targets the workspace root containing main.py
    BASE_DIR = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )

    # Build explicit absolute paths referencing the utils subdirectory cleanly
    CONFIG_FILE = os.path.join(BASE_DIR, "utils", "config.json")
    RATES_CACHE_FILE = os.path.join(BASE_DIR, "utils", "rates_cache.json")

    def __init__(self) -> None:
        """Starts the initialization of the class."""

        # Call the Tk init function
        super().__init__()

        # Initialize tkinter window configurations
        self.setup_window()

        # Setup the customized stylesheet theme engine
        self.setup_style()

        # Load environment credentials and API endpoints
        self.setup_api()

        # Render the graphics layout design architecture
        self.build_gui()

        # Track active background thread network tasks
        self.loading = False

        # Variable container tracker for debouncing text strokes
        self.debounce_id = None

    def setup_window(self) -> None:
        """Configures the window settings of the application in the center of screen."""

        app_width = 600
        app_height = 550

        # Calculate Starting X and Y coordinates for Window mapping center focus
        coor_x = (self.winfo_screenwidth() / 2) - (app_width / 2)
        coor_y = (self.winfo_screenheight() / 2) - (app_height / 2)

        # Setup window properties
        self.title("Currency Exchange Converter")
        self.geometry(f"{app_width}x{app_height}+{int(coor_x)}+{int(coor_y)}")
        self.resizable(width=0, height=0)

        # Setup window background color
        self.configure(bg=self.DARK_BG)

    def setup_style(self) -> None:
        """Configures the style properties of window and widgets."""

        style = ttk.Style()

        # Use theme 'clam' or 'alt' — these built-in themes allow deep color customization
        style.theme_use("clam")

        # Configure default style properties for standard widget classes
        style.configure(
            ".",
            background=self.DARK_BG,
            foreground=self.TEXT_FG,
            fieldbackground=self.SURFACE_BG,
        )

        # Fine-tune individual widget elements
        style.configure("TFrame", background=self.SURFACE_BG)

        style.configure(
            "h1.TLabel",
            background=self.DARK_BG,
            foreground=self.TEXT_FG,
            font=("Arial", 20, "bold"),
        )

        style.configure(
            "h4.TLabel",
            background=self.SURFACE_BG,
            foreground=self.TEXT_FG,
            font=("Arial", 12, "bold"),
        )

        style.configure(
            "TButton",
            background=self.SURFACE_BG,
            foreground=self.TEXT_FG,
            bordercolor=self.DARK_BG,
            lightcolor=self.SURFACE_BG,
            darkcolor=self.SURFACE_BG,
            padding=6,
            font=("Arial", 12, "bold"),
        )

        # Add a hover state for buttons using style.map
        style.map(
            "TButton",
            background=[
                ("active", self.ACCENT_COLOR),
                ("pressed", self.DEEP_ACCENT_COLOR),
            ],
            foreground=[("active", self.TEXT_FG)],
        )

        style.configure(
            "TEntry",
            fieldbackground=self.DARK_BG,
            foreground=self.TEXT_FG,
            bordercolor=self.SURFACE_BG,
            insertcolor=self.TEXT_FG,
        )

        style.configure(
            "Custom.TCombobox",
            fieldbackground=self.DARK_BG,
            background=self.SURFACE_BG,
            foreground=self.TEXT_FG,
        )

        # Apply matched master font configurations directly into sub-widgets options databases
        self.option_add("*TCombobox*Listbox*Font", ("Arial", 11, "bold"))
        self.option_add("*TCombobox*Listbox*Background", self.SURFACE_BG)
        self.option_add("*TCombobox*Listbox*Foreground", self.TEXT_FG)
        self.option_add("*TCombobox*Listbox*selectBackground", self.ACCENT_COLOR)

    def setup_api(self) -> None:
        """Configures the API key and url of currency exchange rate server."""

        # Natively reads `.env` out from the root project folder directory where main.py sits
        load_dotenv()

        api_key = os.getenv("API_KEY")

        if api_key is None:
            messagebox.showerror(
                "API Key Error", "API_KEY environment variable is not set."
            )
            sys.exit(1)

        self.api_url = f"https://v6.exchangerate-api.com/v6/{api_key}/"

    def load_rates_cache(self) -> list:
        """Loads cached rates data safely to extract currency code lists.

        Returns
            (list): The cached currency code string identifiers
        """

        defaults = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "PHP"]

        if os.path.exists(self.RATES_CACHE_FILE):
            try:
                with open(self.RATES_CACHE_FILE, "r", encoding="utf-8") as f:
                    cached_data = json.load(f)

                    # Verify we got a valid dictionary before extracting keys
                    if isinstance(cached_data, dict):
                        return list(cached_data.keys())

            except Exception:
                pass

        return defaults

    def load_saved_state(self) -> dict:
        """Loads persistent storage details configurations safely.

        Returns
            (dict): The state configuration data loaded
        """

        defaults = {"from": "USD", "to": "EUR", "amount": "1.00"}

        if os.path.exists(self.CONFIG_FILE):

            try:
                with open(self.CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)

            except Exception:
                pass

        return defaults

    def save_current_state(self) -> None:
        """Serializes target workspace properties on execution modifications."""

        state = {
            "from": self.from_rate_combo.get(),
            "to": self.to_rate_combo.get(),
            "amount": self.amount_entry.get(),
        }

        try:
            with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=4)

        except Exception:
            pass

    def build_gui(self) -> None:
        """Creates the layout design of the user interface."""

        # Create App Logo using Label
        try:
            self.logo = PhotoImage(file="images/logo.png")
            Label(self, image=self.logo, bg=self.DARK_BG).pack(padx=20, pady=(30, 0))

        except Exception:
            pass

        # Create Label for App Name
        app_title = ttk.Label(
            self, text="Currency Exchange Converter (SJ)", style="h1.TLabel"
        )
        app_title.pack(padx=20, pady=20)

        # Create Status Indicator Frame
        status_indicator_frame = Frame(self, bg=self.DARK_BG)
        status_indicator_frame.pack(fill=X, padx=40, pady=(0, 10))

        # Create Labels for Status Indicator Dot and Status Indicator Text
        self.status_indicator_dot = Label(
            status_indicator_frame,
            text="●",
            fg=self.COLOR_IDLE,
            bg=self.DARK_BG,
            font=("Arial", 12),
            cursor="hand2",
        )
        self.status_indicator_dot.pack(side=LEFT, padx=(0, 5))

        self.status_indicator_text = Label(
            status_indicator_frame,
            text="Connecting to API...",
            fg=self.COLOR_IDLE,
            bg=self.DARK_BG,
            font=("Arial", 10, "italic"),
            cursor="hand2",
        )
        self.status_indicator_text.pack(side=LEFT)

        # Create Main Frame
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack()

        # Create Labels and Combobox for From and To Rates
        from_rate_label = ttk.Label(main_frame, text="From:", style="h4.TLabel")
        from_rate_label.grid(row=0, column=0, padx=5, pady=5, sticky=W)

        to_rate_label = ttk.Label(main_frame, text="To:", style="h4.TLabel")
        to_rate_label.grid(row=0, column=2, padx=5, pady=5, sticky=W)

        self.from_rate_combo = ttk.Combobox(
            main_frame, style="Custom.TCombobox", width=12, font=("Arial", 11, "bold")
        )
        self.from_rate_combo.grid(row=1, column=0, padx=5, pady=5)

        # Create Button for Swap Layout
        swap_rates = ttk.Button(
            main_frame, text="⇄", width=3, command=self.swap_currencies
        )
        swap_rates.grid(row=1, column=1, padx=2, pady=5)

        self.to_rate_combo = ttk.Combobox(
            main_frame, style="Custom.TCombobox", width=12, font=("Arial", 11, "bold")
        )
        self.to_rate_combo.grid(row=1, column=2, padx=5, pady=5)

        # Create Spinner Label
        self.spinner_label = Label(
            main_frame,
            text="",
            bg=self.SURFACE_BG,
            fg=self.ACCENT_COLOR,
            font=("Arial", 11, "bold"),
        )
        self.spinner_label.grid(row=2, column=2, padx=5, pady=5, sticky=E)

        # Create Label and Entry for Amount
        amount_label = ttk.Label(main_frame, text="Amount:", style="h4.TLabel")
        amount_label.grid(row=2, column=0, padx=5, pady=5, sticky=W)

        # Load caching attributes layer properties
        saved_state = self.load_saved_state()

        # Set up Real-Time Input Verification Hooks
        vcmd = (self.register(self.validate_numeric_input), "%P")

        # Attached the validate and validatecommand attributes
        self.amount_entry = ttk.Entry(
            main_frame, validate="key", validatecommand=vcmd, font=("Arial", 11, "bold")
        )
        self.amount_entry.insert(0, saved_state.get("amount", "1.00"))
        self.amount_entry.grid(
            row=3, column=0, columnspan=3, padx=5, pady=5, sticky=W + E
        )

        # Create Label for Result
        self.result_label = ttk.Label(
            self, text="0.00 USD = 0.00 USD", font=("Arial", 20, "bold")
        )
        self.result_label.pack(padx=20, pady=20)

    def run(self) -> None:
        """Starts the application interface."""

        # Asynchronously fetch currency codes without blocking startup
        threading.Thread(target=self.initialize_currency_data, daemon=True).start()

        # Bind Mouse Triggers
        self.status_indicator_dot.bind("<Button-1>", self.manual_reconnect)
        self.status_indicator_text.bind("<Button-1>", self.manual_reconnect)

        # Bind Autocomplete Keyboard Listeners
        self.from_rate_combo.bind("<KeyRelease>", self.check_key)
        self.from_rate_combo.bind(
            "<<ComboboxSelected>>", self.trigger_immediate_conversion
        )

        self.to_rate_combo.bind("<KeyRelease>", self.check_key)
        self.to_rate_combo.bind(
            "<<ComboboxSelected>>", self.trigger_immediate_conversion
        )

        # Reset selection drop-down data if completely empty on delete
        self.from_rate_combo.bind(
            "<BackSpace>",
            lambda e: (
                e.widget.config(values=getattr(e.widget, "all_options", []))
                if len(e.widget.get()) <= 1
                else None
            ),
        )
        self.to_rate_combo.bind(
            "<BackSpace>",
            lambda e: (
                e.widget.config(values=getattr(e.widget, "all_options", []))
                if len(e.widget.get()) <= 1
                else None
            ),
        )

        self.amount_entry.bind("<KeyRelease>", self.trigger_debounced_conversion)

        # Initialize the automatic re-polling reconnection manager loop
        self.after(60000, self.silent_background_retry)

    def initialize_currency_data(self) -> None:
        """Asynchronously fetches initial list of currencies and validates server status."""

        # Initialized Data Sources (Currency codes and Exchange rate)
        currencies = self.get_currencies()
        fallback = self.load_rates_cache()

        # Set fetched currencies as values for Comboboxes
        options = currencies if currencies else fallback

        self.from_rate_combo.all_options = options
        self.to_rate_combo.all_options = options

        self.from_rate_combo["values"] = options
        self.to_rate_combo["values"] = options

        # Map positions matching cached state targets safely
        saved_state = self.load_saved_state()

        try:
            self.from_rate_combo.set(saved_state.get("from", "USD"))
            self.to_rate_combo.set(saved_state.get("to", "EUR"))

        except Exception:
            self.from_rate_combo.current(0)
            self.to_rate_combo.current(0)

        # Switch status color and status text dynamically
        status_color = self.COLOR_SUCCESS if currencies else self.COLOR_DANGER
        status_indicator_text_string = (
            "API Server Connected" if currencies else "API Server Offline"
        )

        self.status_indicator_dot.config(fg=status_color)
        self.status_indicator_text.config(
            text=status_indicator_text_string, fg=status_color
        )

        self.trigger_immediate_conversion()

    def get_currencies(self) -> list | None:
        """Fetches or updates the latest currency exchange rates.

        Returns
            (list | None): The fetched currency code string identifiers from api server
        """

        # Request currency codes and exchange rates from the server
        try:
            response = requests.get(f"{self.api_url}/latest/USD", timeout=5).json()

            if response.get("result") == "success":

                # Save data snapshot to maintain an offline baseline configuration
                with open(self.RATES_CACHE_FILE, "w", encoding="utf-8") as f:
                    json.dump(response.get("conversion_rates", {}), f, indent=4)

                return list(response["conversion_rates"])

        except Exception:
            pass

        return None

    def validate_numeric_input(self, proposed_text: str) -> bool:
        """Character-level input mask checking routine.

        Returns
            (bool): True if layout modifications pass rule evaluations
        """

        # Allow clearing out the box entirely while typing
        if proposed_text == "":
            return True

        # Only allow strings that parse completely into valid currency floats
        try:
            # Prevent typing more than one decimal point
            if proposed_text.count(".") > 1:
                return False

            float(proposed_text)
            return True

        except ValueError:
            return False

    def check_key(self, event) -> None:
        """Filters exchange rate codes every time a key is released."""

        if event.keysym in (
            "BackSpace",
            "Delete",
            "Left",
            "Right",
            "Up",
            "Down",
            "Shift_L",
            "Shift_R",
            "Control_L",
            "Control_R",
            "Caps_Lock",
        ):
            return

        combobox = event.widget
        typed_text = combobox.get()
        all_options = getattr(
            combobox, "all_options", ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "PHP"]
        )

        # Prevent key filtering if click event locks a completely valid choice
        if typed_text in all_options:
            return

        # Filter items
        data = (
            all_options
            if not typed_text
            else [item for item in all_options if typed_text.lower() in item.lower()]
        )

        # Dynamically update the dropdown options
        combobox["values"] = data

        # Automatically drops open the menu visuals without stealing text field typing focus
        if data:
            current_cursor_position = combobox.index(INSERT)
            combobox.event_generate("<Down>")
            combobox.focus_set()
            combobox.icursor(current_cursor_position)

    def swap_currencies(self) -> None:
        """Interchanges combobox selected indices layout values cleanly."""

        src = self.from_rate_combo.get()
        dest = self.to_rate_combo.get()

        self.from_rate_combo.set(dest)
        self.to_rate_combo.set(src)

        self.trigger_immediate_conversion()

    def animate_spinner(self) -> None:
        """Animates a looping sequence of text frame indicators while thread is processing."""

        spinner_chars = ["|", "/", "-", "\\"]
        idx = 0

        while self.loading:
            self.spinner_label.config(text=f"Fetching {spinner_chars[idx]}")
            idx = (idx + 1) % len(spinner_chars)
            time.sleep(0.1)

        self.spinner_label.config(text="")

    def trigger_debounced_conversion(self, event=None) -> None:
        """Implements a 300ms delay timer execution intercept cascade."""
        if self.debounce_id:
            self.after_cancel(self.debounce_id)

        # Schedule the actual task 300 milliseconds into the future
        self.debounce_id = self.after(300, self.trigger_immediate_conversion)

    def trigger_immediate_conversion(self, event=None) -> None:
        """Spawns network task inside a worker thread to protect typing flow fluidity."""

        src = self.from_rate_combo.get()
        dest = self.to_rate_combo.get()
        amount = self.amount_entry.get()

        # Prevent error alerts if entry box is temporarily empty while typing
        if not amount:
            return

        # Validation check to ensure amount is a number
        try:
            valid_amount = float(amount)

        except ValueError:
            self.result_label.config(text="Invalid Amount")
            return

        # Commit current settings into cache file allocations
        self.save_current_state()

        # Intercept and process local calculations instantly for matching entities
        if src == dest:
            self.result_label.config(
                text=f"{valid_amount:.2f} {src} = {valid_amount:.2f} {dest}"
            )
            return

        # Shift currency conversion to background thread
        threading.Thread(
            target=self.async_convert, args=(src, dest, amount), daemon=True
        ).start()

    def async_convert(self, src, dest, amount) -> None:
        """Handles HTTP requesting workflows and live graphical state loops."""

        self.loading = True

        # Shift spinner animation to background thread
        threading.Thread(target=self.animate_spinner, daemon=True).start()

        # Request conversion of exchange rate from the server
        try:
            response = requests.get(
                f"{self.api_url}/pair/{src}/{dest}/{amount}", timeout=5
            ).json()

            # Verify parameters haven't changed while request was in flight
            if (
                src == self.from_rate_combo.get()
                and dest == self.to_rate_combo.get()
                and amount == self.amount_entry.get()
            ):

                if response.get("result") == "success":
                    result = response["conversion_result"]
                    self.result_label.config(
                        text=f"{float(amount):.2f} {src} = {float(result):.2f} {dest}"
                    )

                    self.status_indicator_dot.config(fg=self.COLOR_SUCCESS)
                    self.status_indicator_text.config(
                        text="API Server Connected", fg=self.COLOR_SUCCESS
                    )

                else:
                    self.result_label.config(text="Conversion Failed")

        except Exception:

            # OFFLINE STATE FALLBACK LOGIC RENDER ROUTINE

            if (
                src == self.from_rate_combo.get()
                and dest == self.to_rate_combo.get()
                and amount == self.amount_entry.get()
            ):

                if os.path.exists(self.RATES_CACHE_FILE):

                    try:
                        with open(self.RATES_CACHE_FILE, "r", encoding="utf-8") as f:
                            cached_rates = json.load(f)

                        if src in cached_rates and dest in cached_rates:

                            # Calculate math using USD standard baselines cross multiplication
                            rate_to_usd = cached_rates[src]
                            dest_to_usd = cached_rates[dest]

                            calculated_result = (
                                float(amount) / rate_to_usd
                            ) * dest_to_usd

                            self.result_label.config(
                                text=f"{float(amount):.2f} {src} = {calculated_result:.2f} {dest} (Cached)"
                            )
                            self.status_indicator_dot.config(fg=self.COLOR_IDLE)
                            self.status_indicator_text.config(
                                text="Offline Mode - Using Cached Rates",
                                fg=self.COLOR_IDLE,
                            )

                            return

                    except Exception:
                        pass

                # If no cache data exists, fallback to standard error alerts
                self.result_label.config(text="Connection Error")
                self.status_indicator_dot.config(fg=self.COLOR_DANGER)
                self.status_indicator_text.config(
                    text="API Server Offline", fg=self.COLOR_DANGER
                )

        finally:
            # Safely turn off loading flag if no other background network requests are active
            self.loading = False

    def manual_reconnect(self, event=None) -> None:
        """Triggers a manual background reconnection sequence when clicking the status bar."""

        # Prevent spam clicking if a request is currently active
        if self.loading:
            return

        # Shift visual elements back to loading state instantly
        self.status_indicator_dot.config(fg=self.COLOR_IDLE)
        self.status_indicator_text.config(
            text="Reconnecting to API...", fg=self.COLOR_IDLE
        )
        self.result_label.config(text="Reconnecting...")

        # Run initialization data loop inside a background thread to prevent UI freezing
        threading.Thread(target=self.initialize_currency_data, daemon=True).start()

    def silent_background_retry(self) -> None:
        """Quietly attempts to re-verify the API status every 60 seconds if offline."""

        if not self.loading:
            current_status = self.status_indicator_text.cget("text")

            if "Offline" in current_status or "Using Cached" in current_status:
                threading.Thread(
                    target=self.initialize_currency_data, daemon=True
                ).start()

        # Add 60-second clock loop that never breaks
        self.after(60000, self.silent_background_retry)
