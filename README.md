# 🐾 Interactive Desktop Pet: Your Virtual Companion

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/framework-PyQt5-green.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![License](https://img.shields.io/badge/license-MIT-important.svg)](LICENSE)

An advanced, interactive desktop companion that lives on your screen. More than just a "pet," this application integrates productivity tools like a **Clipboard Manager** and a **Todo List**, while maintaining a charming presence through animations and smart interactions.

---

## 🌟 Key Features

### 🎭 Dynamic Animations & States
- **Idle State**: The pet hangs out on your desktop, keeping you company.
- **Waving Action**: Trigger a friendly wave animation with a keypress.
- **Low Battery Warning**: The pet changes its appearance to alert you when your laptop battery drops below 40% and isn't charging.

### 🛠️ Integrated Productivity Tools
- **Smart Clipboard History**: Automatically captures every text snippet you copy. Access your history anytime to re-copy previous items.
- **Persistent Todo List**: A built-in task manager that saves your progress. Mark tasks as done or delete them as you go.
- **Nudge System**: Every 15 minutes, the pet will give you a "cute nudge" by showing a random pending task from your todo list as a tooltip.

### 🔊 Interactive Audio & Safety
- **"Yowai Mo!" Exit Logic**: Inspired by Gojo Satoru, the pet plays a custom sound and warns you if you try to exit while you still have tasks to complete.
- **Confirmation Dialog**: A fail-safe Yes/No prompt ensures you don't accidentally close your companion.

---

## 🎮 Controls & Shortcuts

| Interaction | Input | Description |
| :--- | :--- | :--- |
| **Move** | `Left-Click + Drag` | Reposition the pet anywhere on your screen. |
| **Waving** | `Right Arrow Key` | Makes the pet wave (hold to keep waving). |
| **Todo List** | `Click Pet + T` | Opens the Todo List manager. |
| **Clipboard** | `Click Pet + C` | Opens the Clipboard History window. |
| **Menu** | `Right-Click` | Access Todo, Clipboard, and Exit options. |
| **Quick Exit** | `4 Rapid Clicks` | Triggers the exit sequence. |

---

## 🚀 Installation & Setup

### 1. Clone & Dependencies
First, ensure you have Python installed, then install the required libraries:

```bash
pip install PyQt5 pynput psutil pyperclip
```

### 2. Folder Structure
For the script to function correctly, ensure your `dp` folder looks like this:
```text
dp/
├── desktop_pet.py       # The main logic
├── run_pet.vbs          # Silent startup script
├── README.md            # This documentation
├── .gitignore           # Git exclusion rules
├── gojo_satoru_s_yowai_mo.mp3
└── [Your Image Assets].png
```

### 3. Silent Background Execution
To run the pet without a messy terminal window appearing, use the `run_pet.vbs` script:
```vbs
Set shell = CreateObject("WScript.Shell")
shell.Run """C:\Program Files\Python312\python.exe"" ""C:\Users\priya\OneDrive\Desktop\dp\desktop_pet.py""", 0
Set shell = Nothing
```

### 4. Windows Auto-Startup
To have your pet greet you every time you log in:
1. Press `Win + R`, type `shell:startup`, and hit Enter.
2. Right-click inside the folder and select **New > Shortcut**.
3. Browse to your `run_pet.vbs` file and finish.

---

## 🛠️ Technical Details

- **Process Management**: Uses `os._exit(0)` for a "hard kill" to ensure that background keyboard listeners and terminal instances are closed immediately upon exit.
- **Focus Policy**: Implements `Qt.StrongFocus` to ensure keyboard shortcuts are captured reliably during interaction.
- **Transparency**: Utilizes `Qt.WA_TranslucentBackground` for a seamless "floating" look on your desktop.

---

## 📝 License
This project is open-source and available under the [MIT License](LICENSE).

---
*Developed with a focus on blending productivity with personality.*
