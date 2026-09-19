# 💱 Currency Exchange Converter (SJ)

A modern, highly responsive, and production-ready desktop Currency Converter built with Python's **Tkinter (ttk)** interface framework. This application features an elegant custom dark-themed UI, an asynchronous non-blocking visual feedback engine, intelligent auto-filtering currency dropdowns, dynamic input debouncing, a secure graphical credential management suite, and a cryptographically protected self-healing local database wrapper.

---

## ✨ Features

- 🎨 **Sleek Custom Dark Mode UI:** Styled from the ground up using customized `ttk` element maps, featuring uniform font allocations and polished active/hover accent feedback loops.
- 🎛️ **Secure In-App Key Management:** Eliminates the need for hardcoded keys or fragile external `.env` setups. Users can securely paste and view/mask personal connectivity tokens right from an integrated, styled modal Settings Dashboard.
- 🔒 **Self-Healing Cryptographic Layer:** Utilizes Fernet symmetric encryption with automated verification routines. If an invalid token, orphaned key, or corrupted configuration vector is identified at boot time, the engine triggers an automatic recovery and scrubs unstable data elements to protect the app from crashing.
- 🔍 **Interactive Autocomplete Fields:** Custom-engineered `Combobox` options lists that dynamically filter as you type while seamlessly resolving standard Tkinter cursor-trapping and event-clicking lifecycle race conditions via direct visual event mappings.
- ⚡ **Asynchronous Thread-Safe Architecture:** Protected against Tkinter race conditions. High-overhead network interactions are completely isolated inside asynchronous worker threads, while visual tasks like typing debouncing and animation spinner ticks scale smoothly over safe main-thread `.after()` schedules.
- 💾 **Smart Serialization:** Automatically saves and scales local workspace configurations—including source and destination dropdown choices, values, and transaction states.
- 🔌 **Resilient Offline Fallback Cache:** Enforces continuous fallback parsing safety boundaries. If connectivity fails, the engine safely hooks into localized snapshot logs (`rates_cache.json`) to compute relative cross-multiplied pairs mathematically using automated defensive value screening.
- 🩺 **Automated Re-Polling Diagnostics:** Incorporates a continuous `60-second` hands-free background network monitoring process alongside an instantaneous click-activated manual re-connection anchor on the visual indicator status panel.

---

## 📁 Repository Structure

```text
/Currency Exchange Conversion Project
│
├── utils/
│   ├── classes/
│   │   ├── config_manager.py      # Unified system path resolver & JSON Read/Write operations
│   │   ├── currency_converter.py  # Primary GUI Engine & Workspace Controller Class
│   │   ├── settings_dialog.py     # Modal Dark Mode API Credential Setup Panel Class
│   │   └── __init__.py            # Declares package definitions for module classes
│   ├── tests/
│   │   ├── test_config_manager.py # Unit tests for the config_manager utility module.
│   │   ├── test_currency_converter.py # Unit tests for the core converter interface.
│   │   ├── test_settings_dialog.py # Unit tests for the modal configuration dialog.
│   │   └── __init__.py            # Declares package definitions for test cases
│   ├── config.json                # Stores encrypted API data maps (Generated in Dev)
│   ├── state_cache.json           # Stores State configuration file (Generated in Dev)
│   ├── rates_cache.json           # Offline fallback database snapshot file (Generated in Dev)
│   ├── .key                       # Stores your individual encryption key safely (Generated in Dev)
│   └── __init__.py                # Declares package definitions for core utilities
│   
├── images/
│   └── logo.png                   # Header interface logo graphic asset (Optional)
├── main.py                        # Entry driver setup launching file
└── requirements.txt               # Repository distribution dependencies manifest file
```

---

## 🛠️ Installation & Setup

### 1. Prerequisites
Ensure you have Python installed on your system. You can verify this by checking your version in the terminal:
```bash
python --version
```

### 2. Clone the Project Workspace Folder Tree
```bash
git clone https://github.com
cd Currency\ Converter\ -\ Tkinter/
```

### 3. Install Package Dependencies
Run the standard pip manifest assembly command from your terminal layout to automatically pull down all necessary module distribution weights:
```bash
pip install -r requirements.txt
```

---

## 🚀 Execution Guide

To invoke the graphic layouts window controller interface, execute the root program launch manager entry script driver:

```bash
python main.py
```

### Automated Unit Tests
To run the complete sandboxed testing infrastructure across all split sub-modules, run `pytest` pointing to the test directory path:
```bash
python -m pytest utils/tests/ -v
```

---

## 🛡️ Pre-Deployment Sanity Checks

Before freezing the code or publishing an application release, sequentially execute these three check operations within your workspace root terminal. This workflow minimizes compile runtime defects, catches syntax warnings, and confirms thread integrity:

### 1. Run Split Test Suites
Execute all granular test files concurrently. Ensure there are 0 failures, unhandled warnings, or missing dependencies:
```bash
python -m pytest utils/tests/ -v
```

### 2. Validate Global Compilation Cleanliness
Compile the codebase globally to discover lingering byte-code defects, incomplete import patterns, or broken indentation types:
```bash
python -m compileall .
```

### 3. Build & Test Frozen Binary Integrity
Generate a standalone distribution build package. Launch the generated binary file from the `dist/` workspace folder to assert file footprint mapping rules (`~/.currency_converter/`) translate seamlessly across host workstations:
```bash
pyinstaller --noconfirm --onefile --windowed --add-data "images/logo.png;images" main.py
```


---

### Configuring your personal connection token:
This application integrates with **ExchangeRate-API** to populate real-time conversions.

On your very first execution, the application will alert you that an API Key is required:
1. **Sign up** for a free developer connection token at [ExchangeRate-API](https://exchangerate-api.com).
2. Click the **⚙ Settings** button located in the top-right corner of the application interface.
3. Securely paste your secret key string inside the entry field (click the **👁 icon** to show or obscure your characters).
4. Click **Save Key**. The core application engine will instantly spin up a background worker thread, check connection integrity lines, and seamlessly generate your local database profiles.

---

## ⚙️ Core Technical Architecture Spotlights

### Distributed Path Isolation (Production Ready)
To completely prevent filesystem lockups or `PermissionError` faults when compiling your application code into an executable `.exe` (via PyInstaller), runtime state management paths dynamically fork:
* **Developer Context:** Keeps all active files neatly bounded within the local workspace directory structure tree inside local project roots.
* **Frozen Executable Context:** Automatically aggregates files into the user's home profile directory layout environment under `~/.currency_converter/`. This guarantees seamless execution across consumer environments without administrative escalation requirements.

```python
if getattr(sys, 'frozen', False):
    user_home_data_dir = os.path.join(os.path.expanduser("~"), ".currency_converter")
    # State targets map flatly to an unrestricted environment directory wrapper...
```

### Defensive Offline Lifecycle Mathematics
When data streams drop, conversions are cleanly managed relative to standard baseline matrix points extracted directly from disk blocks using mathematical cross-multiplication with division-by-zero intercept validation guardrails:


$$ \text{Target Converter Amount} = \left( \frac{\text{Input Amount}}{\text{Source Rate relative to USD}} \right) \times \text{Destination Rate relative to USD} $$



---

## 📦 Packaging to a Standalone Executable (.exe)

Because all configuration paths are abstracted through the central path resolver matrix within `config_manager`, the codebase is completely optimized for multi-platform distribution pooling. Run this command from your root directory tree to build a lean, performance-optimized, single-binary distribution package:

```bash
pyinstaller --noconfirm --onefile --windowed --add-data "images/logo.png;images" main.py
```

Your compiled application asset `(main.exe)` will manifest immediately within your newly generated `dist/` directory folder!
