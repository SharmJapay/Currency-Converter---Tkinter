"""Currency Exchange Converter Application.

This module contains the main class for a graphical currency conversion program
built on Tkinter. It allows users to convert amounts between different global
currencies using real-time API integrations or localized cache fallbacks.

Constants:
    DARK_THEME (str): Built-in Tkinter style theme used for basic customization.
    DARK_BG (str): Hex color code for the main window background.
    SURFACE_BG (str): Hex color code for frame containers.
    TEXT_FG (str): Hex color code for text labels.
    ACCENT_COLOR (str): Hex color code for standard interaction highlights.
    DEEP_ACCENT_COLOR (str): Hex color code for active button states.
    COLOR_SUCCESS (str): Hex color code representing a healthy API status.
    COLOR_DANGER (str): Hex color code representing a network connection error.
    COLOR_IDLE (str): Hex color code representing disconnected or fallback cache operations.
"""

import os
import json
import threading

from tkinter import *
import tkinter.ttk as ttk

import requests

from utils.classes.config_manager import ConfigManager
from utils.classes.settings_dialog import SettingsDialog


class CurrencyExchangeConverter(Tk):
    """A Tkinter-based graphical interface for currency exchange calculations.

    Handles real-time data fetching, thread separation for background web
    requests, interface state caching, and localized rate arithmetic cross-multiplication
    when operating offline.

    Attributes:
        loading (bool): Tracks active background network or processing tasks.
        debounce_id (str or None): Tkinter 'after' registration token tracking keystroke delay timers.
        config_manager (class):
        state_cache_file(str):
        rates_cache_file(str):
        image_cache_file(str):
        api_url (str or None): Complete REST endpoint URL utilizing the loaded API credential.
        logo (PhotoImage): Image asset container housing the application banner graphic.
        status_indicator_dot (Label): Graphical dot widget reflecting API and network connectivity health.
        status_indicator_text (Label): Contextual status string describing connection states.
        from_rate_combo (Combobox): Selection dropdown housing source currency identifiers.
        to_rate_combo (Combobox): Selection dropdown housing destination currency identifiers.
        spinner_label (Label): Interactive tracking spinner shown during pending worker threads.
        amount_entry (Entry): Numeric input text field mapping target exchange rates.
        result_label (Label): Calculated conversion readout displayed at the foot of the layout.


    Methods:
        setup_window() -> None          : Configures the window settings of the application in the center of screen.
        setup_style() -> None           : Configures individual styling, color mappings, active states, and custom listbox options.
        setup_config_manager() -> None  : Initializes and anchors target config instances mapping state files layout scopes.
        setup_api() -> None             : Configures the API key and url dynamically from local user files.
        load_saved_rates() -> list      : Loads cached rates data safely to extract currency code lists.
        load_saved_state() -> dict      : Loads persistent storage details configurations safely.
        save_current_state() -> None    : Serializes target workspace properties on execution modifications into a local JSON cache.
        open_settings_panel() -> None   : Launches the modally configured user credential authorization view panel.
        build_gui() -> None             : Creates the layout design of the user interface and registers layout containers.
        run() -> None                   : Starts the application interface, spawns worker data routines.
        bind_widgets() -> None          : Registers mouse/keyboard hooks.
        initialize_currency_data() -> None : Asynchronously fetches initial list of currencies and validates server status.
        get_currencies() -> list | None    : Fetches or updates the latest currency exchange rates from the API.
        validate_numeric_input() -> bool   : Character-level input mask validation checking routine.
        check_key(event) -> None        : Filters exchange rate codes every time an autocomplete alphanumeric key is released.
        swap_currencies() -> None       : Interchanges combobox selected indices layout values cleanly and hits an immediate refresh.
        animate_spinner() -> None       : Animates a looping sequence of text frame indicators while thread is processing.
        trigger_debounced_conversion(event=None) -> None : Implements a 300ms delay timer execution intercept cascade to minimize rapid-fire API hits.
        trigger_immediate_conversion(event=None) -> None : Spawns network task inside a worker thread to protect typing flow fluidity, validating fields first.
        async_convert(src, dest, amount) -> None : Handles HTTP requesting workflows and live graphical state loops, falling back to local files if offline.
        manual_reconnect(event=None) -> None     : Triggers a manual background reconnection sequence when clicking the status bar.
        silent_background_retry() -> None        : Quietly attempts to re-verify the API status every 60 seconds if currently marked offline.
    """

    # Define theme constant
    DARK_THEME = "clam"

    # Define color palette (dark mode) constants
    DARK_BG = "#1e1e1e"
    SURFACE_BG = "#2d2d2d"
    TEXT_FG = "#ffffff"
    ACCENT_COLOR = "#007acc"
    DEEP_ACCENT_COLOR = "#005999"
    COLOR_SUCCESS = "#2ea44f"
    COLOR_DANGER = "#cb2431"
    COLOR_IDLE = "#888888"

    def __init__(self) -> None:
        """Starts the initialization of the class, bootstrapping themes, states, and layouts."""

        # Call the Tk init function
        super().__init__()

        # Initialize tkinter window configurations
        self.setup_window()

        # Setup the customized stylesheet theme engine
        self.setup_style()

        # Setup the configuration manager
        self.setup_config_manager()

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
        app_height = 630

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
        """Configures individual styling, color mappings, active states, and custom listbox options."""

        style = ttk.Style()
        style.theme_use(self.DARK_THEME)

        # Configure default style properties for standard widget classes
        style.configure(
            ".",
            background=self.DARK_BG,
            foreground=self.TEXT_FG,
            fieldbackground=self.SURFACE_BG,
        )

        # Fine-tune individual widget elements
        style.configure("TFrame", background=self.DARK_BG)

        style.configure(
            "h1.TLabel",
            background=self.DARK_BG,
            foreground=self.TEXT_FG,
            font=("Arial", 20, "bold"),
        )

        style.configure(
            "h4.TLabel",
            background=self.DARK_BG,
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
            font=("Arial", 11, "bold"),
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

    def setup_config_manager(self) -> None:
        """Initializes and anchors target config instances mapping state files layout scopes."""

        self.config_manager = ConfigManager()

        # Bind explicit tracking properties
        self.state_cache_file = self.config_manager.state_cache_file
        self.rates_cache_file = self.config_manager.rates_cache_file
        self.image_file = self.config_manager.image_file

    def setup_api(self) -> None:
        """Configures the API key and url dynamically from local user files."""

        api_key = self.config_manager.load_api_key()

        self.api_url = (
            f"https://v6.exchangerate-api.com/v6/{api_key}/" if api_key else None
        )

    def load_saved_rates(self) -> list:
        """Loads cached rates data safely to extract currency code lists.

        Returns
            list: The cached currency code string identifiers, or hardcoded defaults if missing.
        """

        defaults = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "PHP"]

        if os.path.exists(self.rates_cache_file):
            try:
                with open(self.rates_cache_file, "r", encoding="utf-8") as f:
                    cached_data = json.load(f)

                    if isinstance(cached_data, dict):
                        return list(cached_data.keys())

            except Exception:
                pass

        return defaults

    def load_saved_state(self) -> dict:
        """Loads persistent storage details configurations safely.

        Returns
            dict: The workspace state dictionary mapping source, target, and transaction text.
        """

        defaults = {"from": "USD", "to": "EUR", "amount": "1.00"}

        if os.path.exists(self.state_cache_file):

            try:
                with open(self.state_cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)

            except Exception:
                pass

        return defaults

    def save_current_state(self) -> None:
        """Serializes target workspace properties on execution modifications into a local JSON cache."""

        state = {
            "from": self.from_rate_combo.get(),
            "to": self.to_rate_combo.get(),
            "amount": self.amount_entry.get(),
        }

        try:
            with open(self.state_cache_file, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=4)

        except Exception:
            pass

    def open_settings_panel(self) -> None:
        """Launches the modally configured user credential authorization view panel."""

        # Create settings dialog window
        dialog = SettingsDialog(
            self,
            self.DARK_THEME,
            self.DARK_BG,
            self.SURFACE_BG,
            self.TEXT_FG,
            self.ACCENT_COLOR,
            self.DEEP_ACCENT_COLOR,
        )

        # Wait for the user to close the settings menu, then refresh everything
        self.wait_window(dialog)

        # Re-read the saved configuration profiles instantly
        self.setup_api()

        # Safely spin up a fresh authentication sequence to confirm connection health
        threading.Thread(target=self.initialize_currency_data, daemon=True).start()

    def build_gui(self) -> None:
        """Creates the layout design of the user interface and registers layout containers."""

        # Create Top Header Actions Frame
        header_actions_frame = Frame(self, bg=self.DARK_BG)
        header_actions_frame.pack(fill=X, padx=20, pady=(15, 0))

        # Create Settings Button
        settings_gear_button = ttk.Button(
            header_actions_frame,
            text="⚙ Settings",
            cursor="hand2",
            command=self.open_settings_panel,
        )
        settings_gear_button.pack(side=RIGHT)

        # Create App Logo using Label
        try:
            self.logo = PhotoImage(file=self.image_file)
            Label(self, image=self.logo, bg=self.DARK_BG).pack(padx=20, pady=(30, 0))

        except Exception:
            pass

        # Create App Title Label
        app_title = ttk.Label(
            self, text="Currency Exchange Converter (SJ)", style="h1.TLabel"
        )
        app_title.pack(padx=20, pady=20)

        # Create Status Indicator Frame
        status_indicator_frame = Frame(self, bg=self.DARK_BG)
        status_indicator_frame.pack(fill=X, padx=40, pady=(0, 10))

        # Create Status Indicator Dot and Status Indicator Text Labels
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

        # Create From Rate and To Rate Labels
        from_rate_label = ttk.Label(main_frame, text="From:", style="h4.TLabel")
        from_rate_label.grid(row=0, column=0, padx=5, pady=5, sticky=W)

        to_rate_label = ttk.Label(main_frame, text="To:", style="h4.TLabel")
        to_rate_label.grid(row=0, column=2, padx=5, pady=5, sticky=W)

        # Create From Rate Combobox
        self.from_rate_combo = ttk.Combobox(
            main_frame, style="Custom.TCombobox", width=12, font=("Arial", 11, "bold")
        )
        self.from_rate_combo.grid(row=1, column=0, padx=5, pady=5)

        # Create Swap Layout Button
        swap_rates = ttk.Button(
            main_frame,
            text="⇄",
            width=3,
            cursor="hand2",
            command=self.swap_currencies,
        )
        swap_rates.grid(row=1, column=1, padx=2, pady=5)

        # Create To Rate Combobox
        self.to_rate_combo = ttk.Combobox(
            main_frame, style="Custom.TCombobox", width=12, font=("Arial", 11, "bold")
        )
        self.to_rate_combo.grid(row=1, column=2, padx=5, pady=5)

        # Create Spinner Label
        self.spinner_label = Label(
            main_frame,
            text="",
            bg=self.DARK_BG,
            fg=self.ACCENT_COLOR,
            font=("Arial", 11, "bold"),
        )
        self.spinner_label.grid(row=2, column=2, padx=5, pady=5, sticky=E)

        # Create Amount Label
        amount_label = ttk.Label(main_frame, text="Amount:", style="h4.TLabel")
        amount_label.grid(row=2, column=0, padx=5, pady=5, sticky=W)

        # Load caching attributes layer properties
        saved_state = self.load_saved_state()

        # Set up Real-Time Input Verification Hooks
        vcmd = (self.register(self.validate_numeric_input), "%P")

        # Create Amount Entry and attach the validate and validatecommand attributes
        self.amount_entry = ttk.Entry(
            main_frame, validate="key", validatecommand=vcmd, font=("Arial", 11, "bold")
        )
        self.amount_entry.insert(0, saved_state.get("amount", "1.00"))
        self.amount_entry.grid(
            row=3, column=0, columnspan=3, padx=5, pady=5, sticky=W + E
        )

        # Create Result Label
        self.result_label = ttk.Label(
            self, text="0.00 USD = 0.00 USD", font=("Arial", 20, "bold")
        )
        self.result_label.pack(padx=20, pady=20)

    def run(self) -> None:
        """Starts the application interface, spawns worker data routines."""

        # Asynchronously fetch currency codes without blocking startup
        threading.Thread(target=self.initialize_currency_data, daemon=True).start()

        self.bind_widgets()

        # Initialize the automatic re-polling reconnection manager loop
        self.after(60000, self.silent_background_retry)
        self.mainloop()

    def bind_widgets(self) -> None:
        """Registers mouse/keyboard hooks."""

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

    def initialize_currency_data(self) -> None:
        """Asynchronously fetches initial list of currencies and validates server status."""

        # Initialize fallback cache data source
        fallback = self.load_saved_rates()

        # Set fallback if the user has not established credentials yet
        if not self.api_url:
            self.after(
                0, lambda: self.status_indicator_dot.config(fg=self.COLOR_DANGER)
            )
            self.after(
                0,
                lambda: self.status_indicator_text.config(
                    text="Missing API Key. Click 'Settings' to configure.",
                    fg=self.COLOR_DANGER,
                ),
            )
            self.after(0, lambda: self.result_label.config(text="API Key Required"))

            self.from_rate_combo.all_options = fallback
            self.to_rate_combo.all_options = fallback

            self.after(0, lambda: self.from_rate_combo.config(values=fallback))
            self.after(0, lambda: self.to_rate_combo.config(values=fallback))

            return

        # Fetch currency codes and exchange rate data source
        currencies = self.get_currencies()

        # Set values for Comboboxes
        options = currencies if currencies else fallback

        # Cache option lists locally on the reference arrays
        self.from_rate_combo.all_options = options
        self.to_rate_combo.all_options = options

        # Safely offload widget mutations back onto the primary UI loop thread
        self.after(0, lambda: self.from_rate_combo.config(values=options))
        self.after(0, lambda: self.to_rate_combo.config(values=options))

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

        self.after(0, lambda: self.status_indicator_dot.config(fg=status_color))
        self.after(
            0,
            lambda: self.status_indicator_text.config(
                text=status_indicator_text_string, fg=status_color
            ),
        )

        self.after(0, self.trigger_immediate_conversion)

    def get_currencies(self) -> list | None:
        """Fetches or updates the latest currency exchange rates from the API.

        Returns
            list or None: A list of code strings from the API, or None if connection fails.
        """

        # Do not proceed with request if the user has not established credentials yet
        if not self.api_url:
            return

        # Request currency codes and exchange rates from the server
        try:
            response_raw = requests.get(f"{self.api_url}/latest/USD", timeout=5)

            # Ensure server successfully answers before attempting to run JSON decoding layers
            if response_raw.status_code == 200:
                response = response_raw.json()

                if response.get("result") == "success":

                    # Save data snapshot to maintain an offline baseline configuration
                    with open(self.rates_cache_file, "w", encoding="utf-8") as f:
                        json.dump(response.get("conversion_rates", {}), f, indent=4)

                    return list(response["conversion_rates"])

        except Exception:
            pass

    def validate_numeric_input(self, proposed_text: str) -> bool:
        """Character-level input mask validation checking routine.

        Args
            proposed_text (str): Proposed content value variant currently inside the entry field.

        Returns
            bool: True if layout modifications pass rule evaluations, False to reject input.
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
        """Filters exchange rate codes every time an autocomplete alphanumeric key is released.

        Args
            event (Event): The Tkinter window keystroke layout tracker instance.
        """

        # Prevent key filtering for selected special keys
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
            current_cursor_position = combobox.index("insert")
            combobox.event_generate("<Down>")
            combobox.focus_set()
            combobox.icursor(current_cursor_position)

    def swap_currencies(self) -> None:
        """Interchanges combobox selected indices layout values cleanly and hits an immediate refresh."""

        src = self.from_rate_combo.get()
        dest = self.to_rate_combo.get()

        # Assign src and dest to 'to rate' and 'from rate' respectively to switch values
        self.from_rate_combo.set(dest)
        self.to_rate_combo.set(src)

        self.trigger_immediate_conversion()

    def animate_spinner(self) -> None:
        """Animates a looping sequence of text frame indicators while thread is processing."""

        spinner_chars = ["|", "/", "-", "\\"]
        idx = 0

        def step_animation() -> None:
            """Run a safe visual loop that schedules itself on the main loop"""

            # Read loading flag safely. Widget mutation is decoupled here.
            if self.loading:
                nonlocal idx

                char = spinner_chars[idx]
                self.spinner_label.config(text=f"Fetching {char}")

                idx = (idx + 1) % len(spinner_chars)

                # Schedule next frame 100ms in the future on the MAIN thread
                self.after(100, step_animation)

            else:
                self.spinner_label.config(text="")

        # Trigger the first frame animation step on the main thread
        self.after(0, step_animation)

    def trigger_debounced_conversion(self, event=None) -> None:
        """Implements a 300ms delay timer execution intercept cascade to minimize rapid-fire API hits.

        Args
            event (Event, optional): The Tkinter window layout keystroke tracker instance. Defaults to None.
        """

        if self.debounce_id:
            self.after_cancel(self.debounce_id)

        # Schedule the actual task 300 milliseconds into the future
        self.debounce_id = self.after(300, self.trigger_immediate_conversion)

    def trigger_immediate_conversion(self, event=None) -> None:
        """Spawns network task inside a worker thread to protect typing flow fluidity, validating fields first.

        Args
            event (Event, optional): The Tkinter combobox selection indicator link object. Defaults to None.
        """

        # Intercept layout input updates if an active background network thread is already running
        if self.loading:
            return

        # Suspends the currency conversion if the user has not established credentials yet
        if not self.api_url:
            self.result_label.config(text="API Key Required")
            return

        src = self.from_rate_combo.get().strip().upper()
        dest = self.to_rate_combo.get().strip().upper()
        amount = self.amount_entry.get()

        # Prevent processing if dropdown arrays are completely empty
        if not src or not dest:
            self.result_label.config(text="Select Currencies")
            return

        # Prevent error alerts if entry box is temporarily empty while typing
        if not amount or amount.strip() == "":
            self.result_label.config(text=f"0.00 {src} = 0.00 {dest}")
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
        """Handles HTTP requesting workflows and live graphical state loops, falling back to local files if offline.

        Args
            src (str): Origin currency string code.
            dest (str): Target conversion currency string code.
            amount (str): Raw target floating string amount."""

        # Suspends the currency conversion if the user has not established credentials yet
        if not self.api_url:
            return

        self.loading = True

        self.animate_spinner()

        # Request conversion of exchange rate from the server
        try:
            response_raw = requests.get(
                f"{self.api_url}/pair/{src}/{dest}/{amount}", timeout=5
            )

            # Raise exception if network drops or drops a captive portal HTML page
            if response_raw.status_code != 200:
                raise requests.exceptions.RequestException("Non-200 Server Response")

            response = response_raw.json()

            # Verify parameters haven't changed while request was in flight
            if (
                src == self.from_rate_combo.get()
                and dest == self.to_rate_combo.get()
                and amount == self.amount_entry.get()
            ):

                if response.get("result") == "success":
                    result = response["conversion_result"]
                    text_out = f"{float(amount):.2f} {src} = {float(result):.2f} {dest}"

                    self.after(0, lambda: self.result_label.config(text=text_out))
                    self.after(
                        0,
                        lambda: self.status_indicator_dot.config(fg=self.COLOR_SUCCESS),
                    )
                    self.after(
                        0,
                        lambda: self.status_indicator_text.config(
                            text="API Server Connected", fg=self.COLOR_SUCCESS
                        ),
                    )

                elif response.get("error-type") == "invalid-key":
                    self.after(
                        0, lambda: self.result_label.config(text="Invalid API Key")
                    )
                    self.after(
                        0,
                        lambda: self.status_indicator_dot.config(fg=self.COLOR_DANGER),
                    )
                    self.after(
                        0,
                        lambda: self.status_indicator_text.config(
                            text="Unauthorized API Token Connection",
                            fg=self.COLOR_DANGER,
                        ),
                    )
                else:
                    self.after(
                        0, lambda: self.result_label.config(text="Conversion Failed")
                    )

        except Exception:

            # OFFLINE STATE FALLBACK LOGIC RENDER ROUTINE

            if (
                src == self.from_rate_combo.get()
                and dest == self.to_rate_combo.get()
                and amount == self.amount_entry.get()
            ):

                if os.path.exists(self.rates_cache_file):

                    try:
                        with open(self.rates_cache_file, "r", encoding="utf-8") as f:
                            cached_rates = json.load(f)

                        if (
                            isinstance(cached_rates, dict)
                            and src in cached_rates
                            and dest in cached_rates
                        ):

                            # Calculate math using USD standard baselines cross multiplication
                            rate_to_usd = cached_rates[src]
                            dest_to_usd = cached_rates[dest]

                            # Prevent arithmetic ZeroDivisionError drops
                            if rate_to_usd == 0:
                                raise ValueError("Base rate cannot be zero.")

                            calculated_result = (
                                float(amount) / rate_to_usd
                            ) * dest_to_usd
                            text_out = f"{float(amount):.2f} {src} = {calculated_result:.2f} {dest} (Cached)"

                            self.after(
                                0, lambda: self.result_label.config(text=text_out)
                            )
                            self.after(
                                0,
                                lambda: self.status_indicator_dot.config(
                                    fg=self.COLOR_IDLE
                                ),
                            )
                            self.after(
                                0,
                                lambda: self.status_indicator_text.config(
                                    text="Offline Mode - Using Cached Rates",
                                    fg=self.COLOR_IDLE,
                                ),
                            )

                            return

                    except Exception as fallback_error:
                        # Create error logging for unsuccessful fallback parsing
                        print(f"Fallback parsing exception: {fallback_error}")

                # If no cache data exists, fallback to standard error alerts
                self.after(0, lambda: self.result_label.config(text="Connection Error"))
                self.after(
                    0, lambda: self.status_indicator_dot.config(fg=self.COLOR_DANGER)
                )
                self.after(
                    0,
                    lambda: self.status_indicator_text.config(
                        text="API Server Offline", fg=self.COLOR_DANGER
                    ),
                )

        finally:
            # Safely clear loading state if no other background network requests are active
            self.after(0, lambda: setattr(self, "loading", False))

    def manual_reconnect(self, event=None) -> None:
        """Triggers a manual background reconnection sequence when clicking the status bar.

        Args
            event (Event, optional): Mouse interaction tracker object. Defaults to None.
        """

        # Prevent spam clicking if a request is currently active
        if self.loading:
            return

        # Shift visual elements back to loading state instantly
        self.status_indicator_dot.config(fg=self.COLOR_IDLE)
        self.status_indicator_text.config(
            text="Reconnecting to API...", fg=self.COLOR_IDLE
        )
        self.result_label.config(text="Reconnecting...")

        # Run initialization data loop inside a background thread
        threading.Thread(target=self.initialize_currency_data, daemon=True).start()

    def silent_background_retry(self) -> None:
        """Quietly attempts to re-verify the API status every 60 seconds if currently marked offline."""

        if not self.loading:
            current_status = self.status_indicator_text.cget("text")

            if "Offline" in current_status or "Using Cached" in current_status:

                # Spin up another authentication sequence if status is offline
                threading.Thread(
                    target=self.initialize_currency_data, daemon=True
                ).start()

        # Add 60-second clock loop that never breaks
        self.after(60000, self.silent_background_retry)
