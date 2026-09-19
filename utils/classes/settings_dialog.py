"""Application Modal Configuration Dialog Module.

This module houses the custom settings frame implementation handling visual theme variables,
live API input configuration tracking parameters, and custom modal display controls.
"""

from tkinter import *
from tkinter import messagebox
import tkinter.ttk as ttk

from utils.classes.config_manager import ConfigManager


class SettingsDialog(Toplevel):
    """A standard top-level modal configurations control interface window.

    Provides elements mapping out direct credentials updates without bypassing active user interactions.

    Attributes
        parent (Misc): Reference container targeting parent instance layout properties.
        dark_theme (str): Active style sheet setup target identifier indicator.
        dark_bg (str): Hex color maps variable matching workspace frame background configurations.
        surface_bg (str): Hex color setups variable targeting central frame backgrounds properties.
        text_fg (str): Hex color variables managing explicit texts visibility attributes layers.
        accent_color (str): Hex indicator identifying dynamic layouts hover highlight elements.
        deep_accent_color (str): Hex color configurations allocating system buttons interactions active behaviors.
    """

    def __init__(
        self,
        parent,
        dark_theme,
        dark_bg,
        surface_bg,
        text_fg,
        accent_color,
        deep_accent_color,
    ) -> None:
        """Initializes the setup menu UI layout frame properties."""

        # Call the Tk Toplevel init function
        super().__init__(parent)

        # Pull down shared background variables
        self.parent = parent
        self.dark_theme = dark_theme
        self.dark_bg = dark_bg
        self.surface_bg = surface_bg
        self.text_fg = text_fg
        self.accent_color = accent_color
        self.deep_accent_color = deep_accent_color

        # Setup the configuration manager
        self.setup_config_manager()

        # Initialize tkinter sub window configurations
        self.setup_subwindow()

        # Setup the customized stylesheet theme engine
        self.setup_style()

        # Render the graphics layout design architecture
        self.build_gui()

    def setup_config_manager(self) -> None:
        """Initializes and anchors target config instances mapping state files layout scopes."""

        self.config_manager = ConfigManager()

        fetched_key = self.config_manager.load_api_key()

        self.api_key = fetched_key if fetched_key else ""

        self.save_api_key = self.config_manager.save_api_key

    def setup_subwindow(self) -> None:
        """Configures the subwindow settings of the application."""

        app_width = 400
        app_height = 170

        self.update_idletasks()

        # Calculate Starting X and Y coordinates for subwindow mapping center focus
        coor_x = (
            self.parent.winfo_x() + (self.parent.winfo_width() / 2) - (app_width / 2)
        )
        coor_y = (
            self.parent.winfo_y() + (self.parent.winfo_height() / 2) - (app_height / 2)
        )

        # Enforce viewport bounds screening to prevent multi-monitor layout coordinate shifts
        if coor_x < 0:
            coor_x = 0
        if coor_y < 0:
            coor_y = 0

        # Setup subwindow properties
        self.title("Configuration Settings")
        self.geometry(f"{app_width}x{app_height}+{int(coor_x)}+{int(coor_y)}")
        self.resizable(width=0, height=0)

        # Setup subwindow background color
        self.configure(bg=self.dark_bg)

        # Modal locks (centers focus and intercepts background actions)
        self.transient(self.parent)
        self.grab_set()

    def setup_style(self) -> None:
        """Configures individual styling, color mappings, active states, and custom listbox options."""

        style = ttk.Style()

        # Configure default style properties for standard widget classes
        style.configure(
            ".",
            background=self.dark_bg,
            foreground=self.text_fg,
            fieldbackground=self.surface_bg,
        )

        # Fine-tune individual widget elements
        style.configure("TFrame", background=self.surface_bg)

        style.configure(
            "title.TLabel",
            background=self.dark_bg,
            foreground=self.text_fg,
            font=("Arial", 16, "bold"),
        )

        style.configure(
            "TEntry",
            fieldbackground=self.dark_bg,
            foreground=self.text_fg,
            bordercolor=self.surface_bg,
            insertcolor=self.text_fg,
        )

        style.configure(
            "TButton",
            background=self.surface_bg,
            foreground=self.text_fg,
            bordercolor=self.dark_bg,
            lightcolor=self.surface_bg,
            darkcolor=self.surface_bg,
            padding=6,
            font=("Arial", 12, "bold"),
        )

        # Add a hover state for buttons using style.map
        style.map(
            "TButton",
            background=[
                ("active", self.accent_color),
                ("pressed", self.deep_accent_color),
            ],
            foreground=[("active", self.text_fg)],
        )

    def build_gui(self) -> None:
        """Creates the layout design of the user interface and registers layout containers."""

        # Create Title Label
        subwin_title = ttk.Label(
            self, text="ExchangeRate-API Personal Key:", style="title.TLabel"
        )
        subwin_title.pack(padx=20, pady=20)

        # Create Input Wrapper Frame
        input_wrapper_frame = ttk.Frame(self)
        input_wrapper_frame.pack(fill="x", padx=25)

        # Create Key Entry Field (Masked secure mode by default)
        self.key_entry = ttk.Entry(
            input_wrapper_frame,
            font=("Arial", 11, "bold"),
            show="*",
        )
        self.key_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.key_entry.insert(0, self.api_key)

        # Create Visibility Toggle Button Control
        self.show_button = Button(
            input_wrapper_frame,
            text="👁",
            relief="flat",
            width=3,
            cursor="hand2",
            command=self.toggle_visibility,
            bg=self.surface_bg,
            fg=self.text_fg,
            activebackground=self.accent_color,
            activeforeground=self.text_fg,
            bd=0,
        )
        self.show_button.pack(side="right")

        # Create Button Wrapper Frame
        button_wrapper_frame = ttk.Frame(self)
        button_wrapper_frame.pack(fill="x", padx=25, pady=25)

        save_button = ttk.Button(
            button_wrapper_frame,
            text="Save Key",
            cursor="hand2",
            command=self.save_settings,
        )
        save_button.pack(side="right", padx=(8, 0))

        cancel_button = ttk.Button(
            button_wrapper_frame,
            text="Cancel",
            cursor="hand2",
            command=self.destroy,
        )
        cancel_button.pack(side="right")

    def toggle_visibility(self) -> None:
        """Swaps text character display masking configurations dynamically."""

        if self.key_entry.cget("show") == "*":
            self.key_entry.config(show="")
            self.show_button.config(bg=self.accent_color)

        else:
            self.key_entry.config(show="*")
            self.show_button.config(bg=self.surface_bg)

    def save_settings(self) -> None:
        """Saves the API key to config.json."""

        new_key = self.key_entry.get().strip()

        if not new_key:
            messagebox.showwarning("Empty Field", "Please insert a valid key or exit.")
            return

        if self.save_api_key(new_key):
            messagebox.showinfo(
                "Success", "API configuration profile captured successfully."
            )

            self.destroy()

        else:
            messagebox.showerror(
                "Write Error", "Could not write settings file to local directory path."
            )
