# 💱 Currency Exchange Converter (SJ)

A modern, highly responsive, and feature-rich desktop Currency Converter built with Python's **Tkinter (ttk)** interface framework. This application features an elegant custom dark-themed UI, fluid asynchronous multi-threading architecture, intelligent auto-filtering currency dropdowns, dynamic input debouncing, and an autonomous offline-resilient cache layer with continuous automated re-polling connection diagnostics.

---

## ✨ Features

- 🎨 **Sleek Custom Dark Mode UI:** Styled from the ground up using customized `ttk` element maps, featuring uniform font allocations and polished active/hover accent feedback loops.
- 🔍 **Interactive Autocomplete Fields:** Custom-engineered `Combobox` options lists that dynamically filter as you type while seamlessly resolving standard Tkinter cursor-trapping and event-clicking lifecycle race conditions.
- ⚡ **Asynchronous Threading & Debouncing:** Keystroke actions utilize a `300ms` entry execution delay timer (debouncing) paired with asynchronous network task workers so typing flows never lock or stutter.
- 💾 **Smart Layout Serialization:** Automatically caches workspace settings (From/To choices and amount values) inside `utils/config.json` upon execution parameters changes to smoothly restore previous sessions at boot time.
- 🔌 **Resilient Offline Fallback Cache:** If connection lines drop, the system intercepts network drops and computes cross-multiplied currency pairs mathematically using a stored localized data block snapshot array (`utils/rates_cache.json`).
- 🎛️ **Hands-Free Network Recovery Diagnostics:** Incorporates an autonomous `60-second` quiet background re-polling loop to verify connection states, plus a click-activated manual override anchor right on the visual connection status indicator light.

---

## 📁 Repository Structure

```text
/Currency Exchange Conversion Project
│
├── utils/
│   ├── classes/
│   │   ├── currency_converter.py  # Primary GUI Engine & Workspace Controller Class
│   │   └── __init__.py            # Declares package definitions for module classes
│   ├── __init__.py                # Declares package definitions for core utilities
│   ├── config.json                # User interface settings configuration state file (Generated)
│   └── rates_cache.json           # Offline fallback database relative snapshot file (Generated)
│
├── images/
│   └── logo.png                   # Header interface logo graphic asset (Optional)
├── .env                           # Environmental variable configuration housing private API keys
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
git clone https://github.com/SharmJapay/Currency-Converter---Tkinter.git
 cd Currency\ Converter\ -\ Tkinter/
```

### 3. Install Package Dependencies
Run the standard pip manifest assembly command from your terminal layout to automatically pull down all necessary module distribution weights:
```bash
pip install -r requirements.txt
```

### 4. Provision API Keys and Credentials
This application integrates with **ExchangeRate-API** to populate real-time conversions.
1. Sign up for a free developer connection token at [ExchangeRate-API](https://exchangerate-api.com).
2. Create a file named `.env` inside your base project directory context level (next to `main.py`).
3. Populate it with your newly acquired secure secret hash line string exactly like this:
   ```env
   API_KEY=your_actual_hexadecimal_api_key_goes_here
   ```

---

## 🚀 Execution Guide

To invoke the graphic layouts window controller interface, execute the root program launch manager entry script driver:

```bash
python main.py
```

---

## ⚙️ Core Technical Architecture Spotlights

### Path Resolution Independence
To completely mitigate breaking crashes caused by users launching programs from terminal nested subdirectories, all file input mappings reference explicit base anchors evaluated dynamically from module compilation source nodes via absolute variable wrappers:
```python
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
```

### Network Fallback Mathematics
When HTTP request responses return communication socket failures, translation weights are locally extrapolated down from relative `USD` baselines extracted seamlessly via disk stream inputs:
```text
Target Rate = Destination Rate (relative to USD) / Source Rate (relative to USD)
```

