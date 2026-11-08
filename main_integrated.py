# main_integrated.py
# FINAL VERSION - NO GUI code, just logic, uses main_file.py GUI

import sys
import time

# ═══════════════════════════════════════════════════════════════
# Import cv2 and mediapipe FIRST
# ═══════════════════════════════════════════════════════════════
try:
    import cv2
    import mediapipe as mp
    print("✅ OpenCV + MediaPipe")
except ImportError as e:
    print(f"❌ Missing: {e}")
    sys.exit(1)

# ═══════════════════════════════════════════════════════════════
# Inject into main_file BEFORE importing
# ═══════════════════════════════════════════════════════════════
import main_file

main_file.cv2 = cv2
main_file.mp_drawing = mp.solutions.drawing_utils
main_file.mp_hands = mp.solutions.hands
main_file.cap = None
main_file.structuredLandmarks = []
main_file.prev_gesture = None
main_file.gesture_start_time = None

# ═══════════════════════════════════════════════════════════════
# Import from main_file (GUI + functions)
# ═══════════════════════════════════════════════════════════════
from main_file import Ui_MainWindow, executeAction, takeFeed, Controller
from PyQt5 import QtWidgets
from control_manager import ControlManager


class IntegratedMainWindow(QtWidgets.QMainWindow):
    """Main window - uses GUI from main_file.py"""

    def __init__(self):
        super().__init__()

        print("\n" + "=" * 60)
        print("🚀 GESTURE + VOICE CONTROL")
        print("=" * 60)

        # Use GUI from main_file.py directly
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        print("✅ GUI loaded from main_file.py")

        # Control manager
        self.control_manager = ControlManager(self.ui)
        print("✅ Control manager ready")

        # Connect buttons
        self._connect_buttons()

        # Connect mode selector
        self.ui.modeButtonGroup.buttonClicked.connect(self.on_mode_changed)

        # State
        self.is_running = False

        print("=" * 60)
        self._set_status("✅ Ready", "#2E86C1")

    def _connect_buttons(self):
        """Connect START/STOP"""
        try:
            self.ui.pushButton.clicked.disconnect()
        except:
            pass
        try:
            self.ui.pushButton_2.clicked.disconnect()
        except:
            pass

        self.ui.pushButton.clicked.connect(self.start_control)
        self.ui.pushButton_2.clicked.connect(self.stop_control)

    def on_mode_changed(self, button):
        """Mode changed"""
        if self.is_running:
            return
            
        mode = self.ui.get_selected_mode()
        names = {"gesture": "🎮 Gesture", "voice": "🎤 Voice", "both": "🤝 Hybrid"}
        self._set_status(f"Mode: {names[mode]}", "#3498DB")
        print(f"🔄 {mode}")

    def start_control(self):
        """START button"""
        if self.is_running:
            return
            
        mode = self.ui.get_selected_mode()
        print(f"\n🚀 STARTING {mode.upper()}")

        self.is_running = True

        try:
            if mode in ["gesture", "both"]:
                config = self._read_gesture_config()
                if config is None:
                    self.is_running = False
                    return

                mapping, label, delay = config

                if mode == "gesture":
                    self._set_status("🎮 Active", "#27AE60")
                    self.control_manager.start_gesture_only(mapping, label, delay)
                    self.is_running = False
                    self._set_status("⏸️ Stopped", "#E74C3C")
                else:
                    self.control_manager.start_both_parallel(mapping, label, delay)
                    self._set_status("🤝 Active", "#27AE60")

            elif mode == "voice":
                self.control_manager.start_voice_only()
                self._set_status("🎤 Active", "#27AE60")

        except Exception as e:
            print(f"❌ {e}")
            self.is_running = False
            self._set_status("❌ Error", "#E74C3C")

    def _read_gesture_config(self):
        """Read gesture config from GUI"""
        label = 'Right' if self.ui.radioButton_2.isChecked() else 'Left'
        delay = self.ui.doubleSpinBox.value()
        mapping = {}
        used = []

        # Continuous
        for i in range(1, 5):
            ges = getattr(self.ui, f"cont_{i}_gesture").currentText()
            act = getattr(self.ui, f"cont_{i}_action").currentText()
            stat = getattr(self.ui, f"cont_{i}_status")
            
            if ges != "None" and act != "None":
                key = ges.split(',')[0]
                if key in used:
                    self._set_status(f"❌ '{key}' duplicate", "#E74C3C")
                    stat.setText("❌")
                    return None
                used.append(key)
                mapping[key] = {"action": act, "type": "continuous"}
                stat.setText("✅")
            else:
                stat.setText("")

        # Trigger
        for i in range(1, 9):
            ges = getattr(self.ui, f"trig_{i}_gesture").currentText()
            act = getattr(self.ui, f"trig_{i}_action").currentText()
            stat = getattr(self.ui, f"trig_{i}_status")
            
            if ges != "None" and act != "None":
                key = ges.split(',')[0]
                if key in used:
                    self._set_status(f"❌ '{key}' duplicate", "#E74C3C")
                    stat.setText("❌")
                    return None
                used.append(key)
                mapping[key] = {"action": act, "type": "trigger"}
                stat.setText("✅")
            else:
                stat.setText("")

        if not mapping:
            self._set_status("⚠️ No gestures", "#F39C12")
            return None

        print(f"✅ {len(mapping)} gestures | {label} hand | {delay}s delay")
        return (mapping, label, delay)

    def stop_control(self):
        """STOP button"""
        if not self.is_running:
            return
            
        print("\n⏹️ STOP")
        self.control_manager.stop()
        self.is_running = False
        self._set_status("⏸️ Stopped", "#E74C3C")

    def closeEvent(self, event):
        """Window closing"""
        if self.is_running:
            self.control_manager.stop()
        event.accept()

    def _set_status(self, text, color):
        """Update status bar"""
        self.ui.statusBarLabel.setText(f"Status: {text}")
        self.ui.statusBarLabel.setStyleSheet(
            f"QLabel {{ background-color:{color}; color:white; padding:10px; "
            f"border-radius:5px; font-weight:bold; }}"
        )


# ═══════════════════════════════════════════════════════════════
# RUN
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🎯 GESTURE + VOICE CONTROL")
    print("=" * 60)

    app = QtWidgets.QApplication(sys.argv)
    
    try:
        window = IntegratedMainWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)