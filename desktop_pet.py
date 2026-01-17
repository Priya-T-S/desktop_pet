import sys
import os
import ctypes
import random
import psutil
import pyperclip
from pynput import keyboard

from PyQt5.QtWidgets import (
    QApplication, QLabel, QWidget,
    QListWidget, QListWidgetItem, QPushButton,
    QVBoxLayout, QHBoxLayout,
    QToolTip, QLineEdit, QCheckBox, QMessageBox,
    QMenu, QAction
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer, QPoint, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

# ================= CONFIGURATION (ADD YOUR PATH HERE) =================
# Get current directory to ensure paths work regardless of execution location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. Sound File Path
SOUND_YOWAI_MO = os.path.join(BASE_DIR, "gojo_satoru_s_yowai_mo.mp3")

# 2. Image File Paths
IMG_IDLE = os.path.join(BASE_DIR, "Gemini_Generated_Image_unlrigunlrigunlr-removebg-preview.png")
IMG_WAVE = os.path.join(BASE_DIR, "Gemini_Generated_Image_fhdklffhdklffhdk-removebg-preview.png")
IMG_LOW_BATTERY = os.path.join(BASE_DIR, "image-removebg-preview.png")
# =======================================================================

class SoundManager:
    def __init__(self):
        self.player = QMediaPlayer()

    def play(self, file_path):
        if os.path.exists(file_path):
            url = QUrl.fromLocalFile(file_path)
            self.player.setMedia(QMediaContent(url))
            self.player.play()

# ================= CLIPBOARD WINDOW =================
class ClipboardWindow(QWidget):
    def __init__(self, pet):
        super().__init__()
        self.pet = pet
        self.setWindowTitle("Clipboard History")
        self.setFixedSize(350, 450)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.list_widget = QListWidget()
        self.refresh_list()
        self.list_widget.itemClicked.connect(self.copy_item)

        delete_btn = QPushButton("Delete Selected")
        delete_btn.clicked.connect(self.delete_item)
        
        delete_all_btn = QPushButton("Delete All")
        delete_all_btn.clicked.connect(self.delete_all)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.hide)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(delete_btn)
        btn_layout.addWidget(delete_all_btn)
        btn_layout.addWidget(close_btn)

        layout = QVBoxLayout()
        layout.addWidget(self.list_widget)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def refresh_list(self):
        self.list_widget.clear()
        for item in reversed(self.pet.clip_history):
            self.list_widget.addItem(item)

    def copy_item(self, item):
        pyperclip.copy(item.text())
        QToolTip.showText(self.mapToGlobal(QPoint(100, 100)), "Copied to clipboard!", self)

    def delete_item(self):
        item = self.list_widget.currentItem()
        if not item: return
        text = item.text()
        if text in self.pet.clip_history:
            self.pet.clip_history.remove(text)
            self.pet.save_clipboard_history()
        self.refresh_list()

    def delete_all(self):
        reply = QMessageBox.question(self, 'Confirm', 'Clear all clipboard history?', 
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.pet.clip_history = []
            self.pet.save_clipboard_history()
            self.refresh_list()

    def closeEvent(self, event):
        event.ignore()
        self.hide()

# ================= TODO LIST WINDOW =================
class TodoWindow(QWidget):
    def __init__(self, pet, path):
        super().__init__()
        self.pet = pet
        self.path = path
        self.setWindowTitle("Todo List")
        self.setFixedSize(350, 450)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.layout = QVBoxLayout()
        
        input_layout = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Enter new task...")
        self.task_input.returnPressed.connect(self.add_task_from_input)
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.add_task_from_input)
        input_layout.addWidget(self.task_input)
        input_layout.addWidget(add_btn)
        self.layout.addLayout(input_layout)

        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()
        delete_btn = QPushButton("Delete Selected")
        delete_btn.clicked.connect(self.delete_task)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.hide)
        btn_layout.addWidget(delete_btn)
        btn_layout.addWidget(close_btn)
        self.layout.addLayout(btn_layout)
        
        self.setLayout(self.layout)
        self.load_tasks()

    def add_task_from_input(self):
        text = self.task_input.text().strip()
        if text:
            self.create_task_item(text, False)
            self.task_input.clear()
            self.save_tasks()

    def create_task_item(self, text, completed):
        item = QListWidgetItem(self.list_widget)
        container = QWidget()
        item_layout = QHBoxLayout()
        item_layout.setContentsMargins(5, 2, 5, 2)
        
        checkbox = QCheckBox()
        checkbox.setChecked(completed)
        label = QLabel(text)
        label.setWordWrap(True)
        
        if completed:
            font = label.font()
            font.setStrikeOut(True)
            label.setFont(font)
            label.setEnabled(False)

        def on_toggle(state):
            font = label.font()
            if state == Qt.Checked:
                font.setStrikeOut(True)
                label.setEnabled(False)
            else:
                font.setStrikeOut(False)
                label.setEnabled(True)
            label.setFont(font)
            self.save_tasks()

        checkbox.stateChanged.connect(on_toggle)
        item_layout.addWidget(checkbox)
        item_layout.addWidget(label)
        item_layout.addStretch()
        container.setLayout(item_layout)
        item.setSizeHint(container.sizeHint())
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, container)

    def delete_task(self):
        current_item = self.list_widget.currentItem()
        if current_item:
            self.list_widget.takeItem(self.list_widget.row(current_item))
            self.save_tasks()

    def save_tasks(self):
        tasks = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            widget = self.list_widget.itemWidget(item)
            if widget:
                checkbox = widget.findChild(QCheckBox)
                label = widget.findChild(QLabel)
                if checkbox and label:
                    tasks.append(f"{'DONE' if checkbox.isChecked() else 'TODO'}|{label.text()}")
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("\n".join(tasks))

    def load_tasks(self):
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if "|" in line:
                        status, text = line.split("|", 1)
                        self.create_task_item(text, status == "DONE")

    def get_pending_tasks(self):
        pending = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            widget = self.list_widget.itemWidget(item)
            if widget:
                checkbox = widget.findChild(QCheckBox)
                label = widget.findChild(QLabel)
                if checkbox and not checkbox.isChecked():
                    pending.append(label.text())
        return pending

    def closeEvent(self, event):
        event.ignore()
        self.hide()

# ================= DESKTOP PET =================
class DesktopPet(QLabel):
    def __init__(self):
        super().__init__()
        self.sounds = SoundManager()

        # Load Images
        self.idle = self.load_pixmap(IMG_IDLE, Qt.green)
        self.wave = self.load_pixmap(IMG_WAVE, Qt.yellow)
        self.low_battery = self.load_pixmap(IMG_LOW_BATTERY, Qt.red)

        scale = 0.35
        self.idle = self.scale_img(self.idle, scale)
        self.wave = self.scale_img(self.wave, scale)
        self.low_battery = self.scale_img(self.low_battery, scale)

        self.setPixmap(self.idle)
        self.resize(self.idle.size())
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFocusPolicy(Qt.StrongFocus)

        screen = QApplication.primaryScreen().availableGeometry()
        self.move(screen.width() - self.width() - 20, screen.height() - self.height() - 20)

        self.clip_history_file = os.path.join(BASE_DIR, "clipboard_history.txt")
        self.clip_history = self.load_clipboard_history()
        self.clip_window = ClipboardWindow(self)
        self.todo_window = TodoWindow(self, os.path.join(BASE_DIR, "todo_list.txt"))

        self.mouse_pressed = False
        
        # Click counter for stopping the program
        self.click_count = 0
        self.click_reset_timer = QTimer(self)
        self.click_reset_timer.setSingleShot(True)
        self.click_reset_timer.timeout.connect(self.reset_click_count)

        # Timers
        self.clip_timer = QTimer(self)
        self.clip_timer.timeout.connect(self.check_clipboard)
        self.clip_timer.start(2000)

        self.battery_timer = QTimer(self)
        self.battery_timer.timeout.connect(self.check_battery)
        self.battery_timer.start(600)

        self.reminder_timer = QTimer(self)
        self.reminder_timer.timeout.connect(self.show_reminder)
        self.reminder_timer.start(15 * 60 * 1000) 

        self.show()

    def load_pixmap(self, path, fallback_color):
        if os.path.exists(path):
            return QPixmap(path)
        pix = QPixmap(100, 100)
        pix.fill(fallback_color)
        return pix

    def scale_img(self, img, scale):
        return img.scaled(int(img.width() * scale), int(img.height() * scale), 
                         Qt.KeepAspectRatio, Qt.SmoothTransformation)

    def load_clipboard_history(self):
        if os.path.exists(self.clip_history_file):
            with open(self.clip_history_file, "r", encoding="utf-8") as f:
                return [line.strip() for line in f.readlines() if line.strip()]
        return []

    def save_clipboard_history(self):
        with open(self.clip_history_file, "w", encoding="utf-8") as f:
            f.write("\n".join(self.clip_history))

    def reset_click_count(self):
        self.click_count = 0

    def force_exit(self):
        pending = self.todo_window.get_pending_tasks()
        if pending:
            self.sounds.play(SOUND_YOWAI_MO)
            # Use Yes/No buttons for confirmation
            reply = QMessageBox.question(self, "Yowai Mo!", 
                                       f"You still have {len(pending)} tasks left! Yowai mo~\nDo you really want to exit?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                os._exit(0)
            else:
                # Reset click count if user chooses No or closes the dialog
                self.reset_click_count()
        else:
            # If no tasks, just exit directly
            os._exit(0)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mouse_pressed = True
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            self.setFocus()
            
            # Increment click count
            self.click_count += 1
            self.click_reset_timer.start(2000)
            
            if self.click_count >= 4:
                self.force_exit()
                
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mouse_pressed = False
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_pos)
            event.accept()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_C:
            self.clip_window.refresh_list()
            self.clip_window.show()
        elif event.key() == Qt.Key_T:
            self.todo_window.show()
        super().keyPressEvent(event)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        todo_action = QAction("📋 Todo List", self)
        todo_action.triggered.connect(self.todo_window.show)
        clip_action = QAction("📎 Clipboard History", self)
        clip_action.triggered.connect(lambda: (self.clip_window.refresh_list(), self.clip_window.show()))
        exit_action = QAction("❌ Exit", self)
        exit_action.triggered.connect(self.force_exit)
        menu.addAction(todo_action)
        menu.addAction(clip_action)
        menu.addSeparator()
        menu.addAction(exit_action)
        menu.exec_(event.globalPos())

    def show_reminder(self):
        pending = self.todo_window.get_pending_tasks()
        if pending:
            task = random.choice(pending)
            QToolTip.showText(self.mapToGlobal(QPoint(0, 0)), f"Cute nudge: {task} ✨", self)

    def check_clipboard(self):
        try:
            text = pyperclip.paste()
            if text and (not self.clip_history or text != self.clip_history[-1]):
                if text in self.clip_history: self.clip_history.remove(text)
                self.clip_history.append(text)
                self.save_clipboard_history()
        except: pass

    def check_battery(self):
        battery = psutil.sensors_battery()
        if battery and battery.percent <= 40 and not battery.power_plugged:
            self.setPixmap(self.low_battery)
        else:
            self.setPixmap(self.idle)

# ================= APP START =================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    pet = DesktopPet()

    def on_press(key):
        try:
            if key == keyboard.Key.right: pet.setPixmap(pet.wave)
        except: pass

    def on_release(key):
        try:
            if key == keyboard.Key.right: pet.setPixmap(pet.idle)
        except: pass

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    sys.exit(app.exec_())
