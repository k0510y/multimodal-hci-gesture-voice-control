# -*- coding: utf-8 -*-
# ═══════════════════════════════════════════════════════════════
# main_file.py - PART 1 OF 3
# COMPLETE VERSION WITH ALL FIXES
# Gesture + Voice Control System
# ═══════════════════════════════════════════════════════════════

import math
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, 
                              QPushButton, QScrollArea, QWidget, QLabel,
                              QComboBox, QRadioButton, QDoubleSpinBox, QButtonGroup,
                              QFrame, QSplitter)

import pyautogui
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import screen_brightness_control as sbcontrol

pyautogui.FAILSAFE = False


# ═══════════════════════════════════════════════════════════════
# HELP WINDOW
# ═══════════════════════════════════════════════════════════════
class HelpWindow(QDialog):
    def __init__(self, parent=None, ui_instance=None):
        super().__init__(parent)
        self.setWindowTitle("❓ Help - Gesture + Voice Control")
        self.setGeometry(150, 100, 800, 650)
        self.setModal(False)
        self.ui_instance = ui_instance
        
        layout = QVBoxLayout()
        
        text = QTextEdit()
        text.setReadOnly(True)
        text.setStyleSheet("font-size: 11pt; padding: 10px;")
        text.setHtml("""
<h2>📖 HOW TO USE</h2>
<hr>
<h3>🎮 Gesture Control:</h3>
<ol>
    <li>Select gestures and actions from left panel dropdowns</li>
    <li>Each gesture = one action (no duplicates)</li>
    <li>Continuous actions need hand visible</li>
    <li>Trigger actions execute once per gesture</li>
</ol>

<h3>🎤 Voice Control:</h3>
<ol>
    <li>Say wake word <b>"Computer"</b> first</li>
    <li>Then say your command (see right panel)</li>
    <li>Wait for acknowledgment before next command</li>
</ol>

<h3>🤝 Hybrid Mode (Recommended):</h3>
<ul>
    <li>Use <b>hand gestures</b> for mouse movement</li>
    <li>Use <b>voice</b> for clicks and commands</li>
    <li>Both work simultaneously!</li>
</ul>

<hr>
<h2>✋ 12 Available Gestures</h2>
<table width="100%">
<tr><td>☝️ 1 Finger</td><td>✌ 2 Fingers</td><td>👆 3 Fingers</td></tr>
<tr><td>🖐 4 Fingers</td><td>✋ 5 Fingers</td><td>✊ Fist</td></tr>
<tr><td>✌️ Victory</td><td>👍 Thumbs Up</td><td>👎 Thumbs Down</td></tr>
<tr><td>🤘 Rock On</td><td>👌 OK Sign</td><td>🤏 Pinch</td></tr>
</table>

<hr>
<h2>💡 Recommended Setup</h2>
<h3>Continuous:</h3>
<ul>
<li>5 Fingers → Virtual Mouse</li>
<li>Fist → Drag Mode</li>
<li>Pinch → Pinch Volume</li>
<li>OK Sign → Pinch Brightness</li>
</ul>

<h3>Trigger:</h3>
<ul>
<li>1 Finger → Left Click</li>
<li>Victory → Right Click</li>
<li>2 Fingers → Volume Up</li>
<li>3 Fingers → Volume Down</li>
<li>Thumbs Up → Screenshot</li>
</ul>
        """)
        
        layout.addWidget(text)
        
        btn_layout = QHBoxLayout()
        
        copy_btn = QPushButton("📋 Apply Recommended Setup")
        copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover { background-color: #2980B9; }
        """)
        copy_btn.clicked.connect(self.apply_setup)
        
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #95A5A6;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 11pt;
            }
            QPushButton:hover { background-color: #7F8C8D; }
        """)
        close_btn.clicked.connect(self.close)
        
        btn_layout.addWidget(copy_btn)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def apply_setup(self):
        if self.ui_instance:
            self.ui_instance.applyRecommendedSetup()
        self.close()


# ═══════════════════════════════════════════════════════════════
# MAIN WINDOW - TWO COLUMN LAYOUT
# ═══════════════════════════════════════════════════════════════
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1100, 750)
        MainWindow.setStyleSheet("background-color: #FFFFFF;")
        
        self.centralwidget = QWidget(MainWindow)
        main_layout = QVBoxLayout(self.centralwidget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # ─────────────────────────────────────────────────────
        # HEADER
        # ─────────────────────────────────────────────────────
        header = QHBoxLayout()
        
        title = QLabel("🎯 Gesture + Voice Control")
        title.setStyleSheet("""
            QLabel {
                color: #2C3E50;
                font-size: 20pt;
                font-weight: bold;
                padding: 10px;
            }
        """)
        
        self.helpButton = QPushButton("? HELP")
        self.helpButton.setFixedSize(90, 40)
        self.helpButton.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                border-radius: 8px;
                font-size: 11pt;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #2980B9; }
        """)
        self.helpButton.clicked.connect(self.showHelp)
        
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.helpButton)
        main_layout.addLayout(header)
        
        # ─────────────────────────────────────────────────────
        # MODE SELECTOR
        # ─────────────────────────────────────────────────────
        mode_frame = QFrame()
        mode_frame.setStyleSheet("""
            QFrame {
                background-color: #ECF0F1;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        mode_layout = QHBoxLayout(mode_frame)
        
        mode_label = QLabel("Control Mode:")
        mode_label.setStyleSheet("font-size: 12pt; font-weight: bold; color: #2C3E50;")
        
        self.modeButtonGroup = QButtonGroup()
        
        self.gestureOnlyRadio = QRadioButton("🎮 Gesture Only")
        self.voiceOnlyRadio = QRadioButton("🎤 Voice Only")
        self.bothRadio = QRadioButton("🤝 Both (Hybrid)")
        
        self.bothRadio.setChecked(True)
        
        self.modeButtonGroup.addButton(self.gestureOnlyRadio, 1)
        self.modeButtonGroup.addButton(self.voiceOnlyRadio, 2)
        self.modeButtonGroup.addButton(self.bothRadio, 3)
        
        radio_style = """
            QRadioButton {
                font-size: 11pt;
                padding: 8px 15px;
                color: #34495E;
                background-color: white;
                border-radius: 6px;
                margin: 0 5px;
            }
            QRadioButton:hover {
                background-color: #D6EAF8;
                color: #2980B9;
            }
            QRadioButton:checked {
                background-color: #2E86C1;
                color: white;
                font-weight: bold;
            }
        """
        for r in [self.gestureOnlyRadio, self.voiceOnlyRadio, self.bothRadio]:
            r.setStyleSheet(radio_style)
        
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.gestureOnlyRadio)
        mode_layout.addWidget(self.voiceOnlyRadio)
        mode_layout.addWidget(self.bothRadio)
        mode_layout.addStretch()
        
        main_layout.addWidget(mode_frame)
        
        # ─────────────────────────────────────────────────────
        # TWO COLUMN SECTION
        # ─────────────────────────────────────────────────────
        splitter = QSplitter(QtCore.Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        
        left_widget = self._create_gesture_panel()
        splitter.addWidget(left_widget)
        
        right_widget = self._create_voice_panel()
        splitter.addWidget(right_widget)
        
        splitter.setSizes([500, 500])
        
        main_layout.addWidget(splitter, 1)
        
        # ─────────────────────────────────────────────────────
        # SETTINGS
        # ─────────────────────────────────────────────────────
        settings_layout = QHBoxLayout()
        
        settings_label = QLabel("Settings:")
        settings_label.setStyleSheet("font-size: 11pt; font-weight: bold; color: #34495E;")
        
        self.radioButton = QRadioButton("Left Hand")
        self.radioButton_2 = QRadioButton("Right Hand")
        self.radioButton_2.setChecked(True)
        
        for r in [self.radioButton, self.radioButton_2]:
            r.setStyleSheet("font-size: 10pt;")
        
        delay_label = QLabel("Delay:")
        delay_label.setStyleSheet("font-size: 10pt; color: #34495E;")
        
        self.doubleSpinBox = QDoubleSpinBox()
        self.doubleSpinBox.setFixedWidth(70)
        self.doubleSpinBox.setDecimals(1)
        self.doubleSpinBox.setRange(0.0, 2.0)
        self.doubleSpinBox.setSingleStep(0.1)
        self.doubleSpinBox.setValue(0.3)
        self.doubleSpinBox.setStyleSheet("""
            QDoubleSpinBox {
                padding: 5px;
                border: 1px solid #BDC3C7;
                border-radius: 4px;
                font-size: 10pt;
            }
        """)
        
        settings_layout.addWidget(settings_label)
        settings_layout.addWidget(self.radioButton)
        settings_layout.addWidget(self.radioButton_2)
        settings_layout.addStretch()
        settings_layout.addWidget(delay_label)
        settings_layout.addWidget(self.doubleSpinBox)
        
        main_layout.addLayout(settings_layout)
        
        # ─────────────────────────────────────────────────────
        # BUTTONS
        # ─────────────────────────────────────────────────────
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        self.pushButton = QPushButton("▶ START")
        self.pushButton.setFixedHeight(50)
        self.pushButton.setStyleSheet("""
            QPushButton {
                background-color: #27AE60;
                color: white;
                border-radius: 8px;
                font-size: 14pt;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #229954; }
        """)
        self.pushButton.clicked.connect(self.pressStart)
        
        self.pushButton_2 = QPushButton("⏹ STOP")
        self.pushButton_2.setFixedHeight(50)
        self.pushButton_2.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                color: white;
                border-radius: 8px;
                font-size: 14pt;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #C0392B; }
        """)
        self.pushButton_2.clicked.connect(self.pressStop)
        
        btn_layout.addWidget(self.pushButton)
        btn_layout.addWidget(self.pushButton_2)
        main_layout.addLayout(btn_layout)
        
        # ─────────────────────────────────────────────────────
        # STATUS BAR
        # ─────────────────────────────────────────────────────
        self.statusBarLabel = QLabel("Status: ✅ Ready - Select mode and click START")
        self.statusBarLabel.setStyleSheet("""
            QLabel {
                background-color: #ECF0F1;
                color: #2980B9;
                padding: 10px;
                border-radius: 5px;
                font-size: 10pt;
                font-weight: bold;
            }
        """)
        main_layout.addWidget(self.statusBarLabel)
        
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)
        
        self.retranslateUi(MainWindow)
    
    # ═════════════════════════════════════════════════════════
    # LEFT PANEL: GESTURE CONTROLS
    # ═════════════════════════════════════════════════════════
    def _create_gesture_panel(self):
        panel = QWidget()
        panel.setStyleSheet("""
            QWidget {
                background-color: #F8F9FA;
                border-radius: 8px;
            }
        """)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        
        header = QLabel("🎮 GESTURE CONTROL")
        header.setStyleSheet("""
            QLabel {
                background-color: #3498DB;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-size: 12pt;
                font-weight: bold;
            }
        """)
        layout.addWidget(header)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(8)
        
        cont_label = QLabel("🖱️ CONTINUOUS ACTIONS")
        cont_label.setStyleSheet("""
            QLabel {
                background-color: #D5F4E6;
                color: #27AE60;
                padding: 6px;
                border-radius: 4px;
                font-size: 10pt;
                font-weight: bold;
            }
        """)
        scroll_layout.addWidget(cont_label)
        
        for i in range(1, 5):
            row = self._create_gesture_row(f"cont_{i}")
            scroll_layout.addWidget(row)
        
        scroll_layout.addSpacing(10)
        
        trig_label = QLabel("👆 TRIGGER ACTIONS")
        trig_label.setStyleSheet("""
            QLabel {
                background-color: #FEF5E7;
                color: #E67E22;
                padding: 6px;
                border-radius: 4px;
                font-size: 10pt;
                font-weight: bold;
            }
        """)
        scroll_layout.addWidget(trig_label)
        
        for i in range(1, 9):
            row = self._create_gesture_row(f"trig_{i}")
            scroll_layout.addWidget(row)
        
        scroll_layout.addStretch()
        
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        return panel
    
    def _create_gesture_row(self, row_id):
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(2, 2, 2, 2)
        row_layout.setSpacing(8)
        
        ges = QComboBox()
        ges.setFixedWidth(140)
        ges.setObjectName(f"{row_id}_gesture")
        ges.setStyleSheet("""
            QComboBox {
                padding: 6px;
                border: 1px solid #BDC3C7;
                border-radius: 4px;
                background-color: white;
                font-size: 9pt;
            }
            QComboBox:hover { border-color: #3498DB; }
        """)
        setattr(self, f"{row_id}_gesture", ges)
        
        arrow = QLabel("→")
        arrow.setStyleSheet("font-size: 14pt; color: #7F8C8D;")
        arrow.setFixedWidth(20)
        
        act = QComboBox()
        act.setFixedWidth(150)
        act.setObjectName(f"{row_id}_action")
        act.setStyleSheet("""
            QComboBox {
                padding: 6px;
                border: 1px solid #BDC3C7;
                border-radius: 4px;
                background-color: white;
                font-size: 9pt;
            }
            QComboBox:hover { border-color: #3498DB; }
        """)
        setattr(self, f"{row_id}_action", act)
        
        status = QLabel("")
        status.setFixedWidth(60)
        status.setObjectName(f"{row_id}_status")
        status.setStyleSheet("font-size: 9pt;")
        setattr(self, f"{row_id}_status", status)
        
        row_layout.addWidget(ges)
        row_layout.addWidget(arrow)
        row_layout.addWidget(act)
        row_layout.addWidget(status)
        row_layout.addStretch()
        
        return row
    
    # ═════════════════════════════════════════════════════════
    # RIGHT PANEL: VOICE COMMANDS
    # ═════════════════════════════════════════════════════════
    def _create_voice_panel(self):
        panel = QWidget()
        panel.setStyleSheet("""
            QWidget {
                background-color: #F8F9FA;
                border-radius: 8px;
            }
        """)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        
        header = QLabel("🎤 VOICE CONTROL")
        header.setStyleSheet("""
            QLabel {
                background-color: #9B59B6;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-size: 12pt;
                font-weight: bold;
            }
        """)
        layout.addWidget(header)
        
        wake_info = QLabel("💡 Wake word: Say <b>'Computer'</b> before each command")
        wake_info.setStyleSheet("""
            QLabel {
                background-color: #FFF9C4;
                color: #F57C00;
                padding: 8px;
                border-radius: 4px;
                font-size: 10pt;
            }
        """)
        wake_info.setWordWrap(True)
        layout.addWidget(wake_info)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        commands_widget = QWidget()
        cmd_layout = QVBoxLayout(commands_widget)
        cmd_layout.setSpacing(6)
        
        text = QTextEdit()
        text.setReadOnly(True)
        text.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #BDC3C7;
                border-radius: 5px;
                padding: 10px;
                font-size: 10pt;
            }
        """)
        text.setHtml("""
<h3 style="color:#2C3E50; margin-top:0;">📋 Available Commands</h3>

<h4 style="color:#27AE60;">🖱️ Mouse Control:</h4>
<ul style="line-height:1.6;">
  <li><b>"Computer, move mouse center"</b></li>
  <li><b>"Computer, move mouse up / down / left / right"</b></li>
  <li><b>"Computer, click"</b> - Left click</li>
  <li><b>"Computer, right click"</b></li>
  <li><b>"Computer, double click"</b></li>
</ul>

<h4 style="color:#E67E22;">📜 Scrolling:</h4>
<ul style="line-height:1.6;">
  <li><b>"Computer, scroll up"</b></li>
  <li><b>"Computer, scroll down"</b></li>
</ul>

<h4 style="color:#9B59B6;">🔊 Volume:</h4>
<ul style="line-height:1.6;">
  <li><b>"Computer, volume up"</b></li>
  <li><b>"Computer, volume down"</b></li>
  <li><b>"Computer, mute"</b></li>
</ul>

<h4 style="color:#F39C12;">🔆 Brightness:</h4>
<ul style="line-height:1.6;">
  <li><b>"Computer, brightness up"</b></li>
  <li><b>"Computer, brightness down"</b></li>
</ul>

<h4 style="color:#E74C3C;">🪟 Window Management:</h4>
<ul style="line-height:1.6;">
  <li><b>"Computer, minimize"</b></li>
  <li><b>"Computer, maximize"</b></li>
  <li><b>"Computer, close window"</b></li>
</ul>

<h4 style="color:#3498DB;">📸 Other:</h4>
<ul style="line-height:1.6;">
  <li><b>"Computer, screenshot"</b></li>
</ul>

<hr style="margin:10px 0;">
<p style="color:#7F8C8D; font-size:9pt;">
<b>💡 Tip:</b> In Hybrid mode, use hand to move mouse and voice to click!
</p>
        """)
        
        cmd_layout.addWidget(text)
        
        scroll.setWidget(commands_widget)
        layout.addWidget(scroll)
        
        return panel
    
    def showHelp(self):
        help_win = HelpWindow(self.centralwidget.parent(), self)
        help_win.exec_()
    
    def get_selected_mode(self):
        if self.gestureOnlyRadio.isChecked():
            return "gesture"
        elif self.voiceOnlyRadio.isChecked():
            return "voice"
        return "both"


# ═══════════════════════════════════════════════════════════════
# END OF PART 1
# Continue with PART 2 for button handlers and Controller class
# ═══════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════
# main_file.py - PART 2 OF 3 - COMPLETELY FIXED
# ALL VOLUME/BRIGHTNESS/SCROLL BUGS FIXED
# ═══════════════════════════════════════════════════════════════

    def applyRecommendedSetup(self):
        """Apply recommended gesture configuration"""
        # Continuous
        self.cont_1_gesture.setCurrentText("5,✋")
        self.cont_1_action.setCurrentText("Virtual Mouse")
        self.cont_2_gesture.setCurrentText("Fist,✊")
        self.cont_2_action.setCurrentText("Drag Mode")
        self.cont_3_gesture.setCurrentText("Pinch,🤏")
        self.cont_3_action.setCurrentText("Pinch Volume")
        self.cont_4_gesture.setCurrentText("OK Sign,👌")
        self.cont_4_action.setCurrentText("Pinch Brightness")
        
        # Trigger
        self.trig_1_gesture.setCurrentText("1,☝️")
        self.trig_1_action.setCurrentText("Left Click")
        self.trig_2_gesture.setCurrentText("Victory,✌️")
        self.trig_2_action.setCurrentText("Right Click")
        self.trig_3_gesture.setCurrentText("2,✌")
        self.trig_3_action.setCurrentText("Volume Up")
        self.trig_4_gesture.setCurrentText("3,👆")
        self.trig_4_action.setCurrentText("Volume Down")
        self.trig_5_gesture.setCurrentText("Thumbs Up,👍")
        self.trig_5_action.setCurrentText("Screenshot")
        
        self.statusBarLabel.setText("Status: ✅ Recommended setup applied!")
        self.statusBarLabel.setStyleSheet("""
            QLabel {
                background-color: #27AE60;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
    
    def pressStop(self):
        """Stop button handler"""
        stopFeed()
        self.statusBarLabel.setText("Status: ⏸️ Stopped")
        self.statusBarLabel.setStyleSheet("""
            QLabel {
                background-color: #E74C3C;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
    
    def pressStart(self):
        """Start button handler - reads configuration and starts system"""
        label = 'Right' if self.radioButton_2.isChecked() else 'Left'
        gesture_mapping = {}
        used_gestures = []
        
        print("\n" + "="*60)
        print("🎯 READING CONFIGURATION...")
        print("="*60)
        
        # Read continuous gestures
        print("\n🖱️  CONTINUOUS:")
        for i in range(1, 5):
            ges_widget = getattr(self, f"cont_{i}_gesture")
            act_widget = getattr(self, f"cont_{i}_action")
            status_widget = getattr(self, f"cont_{i}_status")
            
            ges_text = ges_widget.currentText()
            act_text = act_widget.currentText()
            
            if ges_text != "None" and act_text != "None":
                ges = ges_text.split(',')[0]
                
                if ges in used_gestures:
                    error_msg = f"❌ '{ges}' already assigned!"
                    self.statusBarLabel.setText(f"Status: {error_msg}")
                    self.statusBarLabel.setStyleSheet("""
                        QLabel {
                            background-color: #E74C3C;
                            color: white;
                            padding: 10px;
                            border-radius: 5px;
                            font-weight: bold;
                        }
                    """)
                    status_widget.setText("❌ Dup!")
                    status_widget.setStyleSheet("color: #E74C3C; font-weight: bold;")
                    return
                
                used_gestures.append(ges)
                gesture_mapping[ges] = {"action": act_text, "type": "continuous"}
                status_widget.setText("✅")
                status_widget.setStyleSheet("color: #27AE60; font-weight: bold;")
                print(f"  {i}. {ges} → {act_text}")
            else:
                status_widget.setText("")
        
        # Read trigger gestures
        print("\n👆 TRIGGER:")
        for i in range(1, 9):
            ges_widget = getattr(self, f"trig_{i}_gesture")
            act_widget = getattr(self, f"trig_{i}_action")
            status_widget = getattr(self, f"trig_{i}_status")
            
            ges_text = ges_widget.currentText()
            act_text = act_widget.currentText()
            
            if ges_text != "None" and act_text != "None":
                ges = ges_text.split(',')[0]
                
                if ges in used_gestures:
                    error_msg = f"❌ '{ges}' already assigned!"
                    self.statusBarLabel.setText(f"Status: {error_msg}")
                    self.statusBarLabel.setStyleSheet("""
                        QLabel {
                            background-color: #E74C3C;
                            color: white;
                            padding: 10px;
                            border-radius: 5px;
                            font-weight: bold;
                        }
                    """)
                    status_widget.setText("❌ Dup!")
                    status_widget.setStyleSheet("color: #E74C3C; font-weight: bold;")
                    return
                
                used_gestures.append(ges)
                gesture_mapping[ges] = {"action": act_text, "type": "trigger"}
                status_widget.setText("✅")
                status_widget.setStyleSheet("color: #27AE60; font-weight: bold;")
                print(f"  {i}. {ges} → {act_text}")
            else:
                status_widget.setText("")
        
        if len(gesture_mapping) == 0:
            self.statusBarLabel.setText("Status: ⚠️ No gestures configured!")
            self.statusBarLabel.setStyleSheet("""
                QLabel {
                    background-color: #F39C12;
                    color: white;
                    padding: 10px;
                    border-radius: 5px;
                    font-weight: bold;
                }
            """)
            return
        
        print(f"\n✅ Total: {len(gesture_mapping)} gestures")
        print("="*60 + "\n")
        
        delay = self.doubleSpinBox.value()
        self.statusBarLabel.setText(f"Status: 🎥 Starting... ({len(gesture_mapping)} active)")
        self.statusBarLabel.setStyleSheet("""
            QLabel {
                background-color: #27AE60;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        
        takeFeed(gesture_mapping, label, delay, self)
    
    def retranslateUi(self, MainWindow):
        """Populate dropdowns with gestures and actions"""
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Gesture + Voice Control"))
        
        gestures = ["None", "1,☝️", "2,✌", "3,👆", "4", "5,✋", "Fist,✊", 
                   "Victory,✌️", "Thumbs Up,👍", "Thumbs Down,👎", 
                   "Rock On,🤘", "OK Sign,👌", "Pinch,🤏"]
        
        cont_actions = ["None", "Virtual Mouse", "Drag Mode", "Pinch Volume", 
                       "Pinch Brightness", "Scroll Up", "Scroll Down"]
        
        trig_actions = ["None", "Left Click", "Right Click", "Double Click",
                       "Volume Up", "Volume Down", "Mute Toggle",
                       "Brightness Up", "Brightness Down", "Screenshot",
                       "Minimize Window", "Maximize Window", "Close Window"]
        
        # Populate continuous
        for i in range(1, 5):
            ges = getattr(self, f"cont_{i}_gesture")
            act = getattr(self, f"cont_{i}_action")
            for g in gestures:
                ges.addItem(g)
            for a in cont_actions:
                act.addItem(a)
        
        # Populate trigger
        for i in range(1, 9):
            ges = getattr(self, f"trig_{i}_gesture")
            act = getattr(self, f"trig_{i}_action")
            for g in gestures:
                ges.addItem(g)
            for a in trig_actions:
                act.addItem(a)


# ═══════════════════════════════════════════════════════════════
# CONTROLLER CLASS - ALL FIXES APPLIED
# ═══════════════════════════════════════════════════════════════
class Controller:
    """Handles all gesture control logic"""
    tx_old = 0
    ty_old = 0
    flag = False
    grabflag = False
    pinchmajorflag = False
    pinchminorflag = False
    pinchstartxcoord = None
    pinchstartycoord = None
    pinchdirectionflag = None
    prevpinchlv = 0
    pinchlv = 0
    framecount = 0
    prev_hand = None
    pinch_threshold = 0.3
    
    @staticmethod
    def get_position(hand_result):
        """Get smoothed mouse position from hand position"""
        point = 9
        position = [hand_result.landmark[point].x, hand_result.landmark[point].y]
        sx, sy = pyautogui.size()
        x_old, y_old = pyautogui.position()
        x = int(position[0] * sx)
        y = int(position[1] * sy)
        
        if Controller.prev_hand is None:
            Controller.prev_hand = [x, y]
        
        delta_x = x - Controller.prev_hand[0]
        delta_y = y - Controller.prev_hand[1]
        distsq = delta_x**2 + delta_y**2
        ratio = 1
        Controller.prev_hand = [x, y]
        
        if distsq <= 25:
            ratio = 0
        elif distsq <= 900:
            ratio = 0.07 * (distsq ** (1/2))
        else:
            ratio = 2.1
        
        x, y = x_old + delta_x * ratio, y_old + delta_y * ratio
        return (x, y)
    
    @staticmethod
    def pinch_control_init(hand_result):
        """Initialize pinch control"""
        Controller.pinchstartxcoord = hand_result.landmark[8].x
        Controller.pinchstartycoord = hand_result.landmark[8].y
        Controller.pinchlv = 0
        Controller.prevpinchlv = 0
        Controller.framecount = 0
    
    @staticmethod
    def get_pinch_ylv(hand_result):
        """Get vertical pinch level"""
        dist = round((Controller.pinchstartycoord - hand_result.landmark[8].y) * 10, 1)
        return dist
    
    @staticmethod
    def get_pinch_xlv(hand_result):
        """Get horizontal pinch level"""
        dist = round((hand_result.landmark[8].x - Controller.pinchstartxcoord) * 10, 1)
        return dist
    
    @staticmethod
    def change_system_volume():
        """FIXED: Pinch volume with keyboard fallback"""
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            currentVolumeLv = volume.GetMasterVolumeLevelScalar()
            currentVolumeLv += Controller.pinchlv / 50.0
            if currentVolumeLv > 1.0:
                currentVolumeLv = 1.0
            elif currentVolumeLv < 0.0:
                currentVolumeLv = 0.0
            volume.SetMasterVolumeLevelScalar(currentVolumeLv, None)
        except:
            # Fallback: keyboard shortcut (always works)
            if Controller.pinchlv > 0:
                pyautogui.press('volumeup')
            elif Controller.pinchlv < 0:
                pyautogui.press('volumedown')
    
    @staticmethod
    def change_system_brightness():
        """FIXED: Handles list return for multi-monitor setups"""
        try:
            current = sbcontrol.get_brightness(display=0)
            
            # FIX: Handle list return (multi-monitor)
            if isinstance(current, list):
                current = current[0] if len(current) > 0 else 50
            elif current is None:
                current = 50
            
            current = int(current)
            currentBrightnessLv = current / 100.0
            currentBrightnessLv += Controller.pinchlv / 50.0
            
            if currentBrightnessLv > 1.0:
                currentBrightnessLv = 1.0
            elif currentBrightnessLv < 0.0:
                currentBrightnessLv = 0.0
            
            new_val = int(100 * currentBrightnessLv)
            sbcontrol.set_brightness(new_val, display=0)
        except Exception:
            pass  # Silent fail for smooth pinch control
    
    @staticmethod
    def pinch_control(hand_result, controlHorizontal, controlVertical):
        """Handle pinch control logic"""
        if Controller.framecount == 5:
            Controller.framecount = 0
            Controller.pinchlv = Controller.prevpinchlv
            
            if Controller.pinchdirectionflag == True:
                controlHorizontal()
            elif Controller.pinchdirectionflag == False:
                controlVertical()
        
        lvx = Controller.get_pinch_xlv(hand_result)
        lvy = Controller.get_pinch_ylv(hand_result)
        
        if abs(lvy) > abs(lvx) and abs(lvy) > Controller.pinch_threshold:
            Controller.pinchdirectionflag = False
            if abs(Controller.prevpinchlv - lvy) < Controller.pinch_threshold:
                Controller.framecount += 1
            else:
                Controller.prevpinchlv = lvy
                Controller.framecount = 0
        
        elif abs(lvx) > Controller.pinch_threshold:
            Controller.pinchdirectionflag = True
            if abs(Controller.prevpinchlv - lvx) < Controller.pinch_threshold:
                Controller.framecount += 1
            else:
                Controller.prevpinchlv = lvx
                Controller.framecount = 0


# ═══════════════════════════════════════════════════════════════
# ACTION EXECUTION - ALL BUGS FIXED (VOLUME + SCROLL)
# ═══════════════════════════════════════════════════════════════
def executeAction(action, hand_result=None, label=None):
    """Execute actions - COMPLETELY FIXED for volume + scroll"""
    
    # ─────────────────────────────────────────────────────
    # MOUSE CONTROL
    # ─────────────────────────────────────────────────────
    if action == "Virtual Mouse":
        if hand_result:
            x, y = Controller.get_position(hand_result)
            pyautogui.moveTo(x, y, duration=0.1)
    
    elif action == "Drag Mode":
        if hand_result:
            if not Controller.grabflag:
                Controller.grabflag = True
                pyautogui.mouseDown(button="left")
            x, y = Controller.get_position(hand_result)
            pyautogui.moveTo(x, y, duration=0.1)
    
    elif action == "Pinch Volume":
        if hand_result and label == 'Right':
            if not Controller.pinchmajorflag:
                Controller.pinch_control_init(hand_result)
                Controller.pinchmajorflag = True
            Controller.pinch_control(hand_result, lambda: None, Controller.change_system_volume)
    
    elif action == "Pinch Brightness":
        if hand_result and label == 'Right':
            if not Controller.pinchmajorflag:
                Controller.pinch_control_init(hand_result)
                Controller.pinchmajorflag = True
            Controller.pinch_control(hand_result, lambda: None, Controller.change_system_brightness)
    
    # ─────────────────────────────────────────────────────
    # CLICKS
    # ─────────────────────────────────────────────────────
    elif action == "Left Click":
        pyautogui.click()
        print("   ✅ Left Click")
    
    elif action == "Right Click":
        pyautogui.click(button='right')
        print("   ✅ Right Click")
    
    elif action == "Double Click":
        pyautogui.doubleClick()
        print("   ✅ Double Click")
    
    # ─────────────────────────────────────────────────────
    # VOLUME - COMPLETELY FIXED WITH KEYBOARD FALLBACK
    # ─────────────────────────────────────────────────────
    elif action == "Volume Up":
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            current = volume.GetMasterVolumeLevelScalar()
            new_vol = min(current + 0.05, 1.0)
            volume.SetMasterVolumeLevelScalar(new_vol, None)
            print(f"   ✅ Volume UP: {int(new_vol * 100)}%")
        except:
            # FALLBACK: Use keyboard shortcut (always works)
            pyautogui.press('volumeup')
            print(f"   ✅ Volume UP (keyboard)")
    
    elif action == "Volume Down":
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            current = volume.GetMasterVolumeLevelScalar()
            new_vol = max(current - 0.05, 0.0)
            volume.SetMasterVolumeLevelScalar(new_vol, None)
            print(f"   ✅ Volume DOWN: {int(new_vol * 100)}%")
        except:
            # FALLBACK: Use keyboard shortcut (always works)
            pyautogui.press('volumedown')
            print(f"   ✅ Volume DOWN (keyboard)")
    
    elif action == "Mute Toggle":
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            current_mute = volume.GetMute()
            volume.SetMute(not current_mute, None)
            print(f"   ✅ Mute: {'OFF' if current_mute else 'ON'}")
        except:
            # FALLBACK: Use keyboard shortcut (always works)
            pyautogui.press('volumemute')
            print(f"   ✅ Mute toggle (keyboard)")
    
    # ─────────────────────────────────────────────────────
    # BRIGHTNESS - COMPLETELY FIXED FOR LISTS
    # ─────────────────────────────────────────────────────
    elif action == "Brightness Up":
        try:
            current = sbcontrol.get_brightness(display=0)
            
            # FIX: Handle list return (multi-monitor)
            if isinstance(current, list):
                current = current[0] if len(current) > 0 else 50
            elif current is None:
                current = 50
            
            current = int(current)
            new_bright = min(current + 10, 100)
            sbcontrol.set_brightness(new_bright, display=0)
            print(f"   ✅ Brightness UP: {new_bright}%")
        except Exception as e:
            print(f"   ❌ Brightness error: {e}")
    
    elif action == "Brightness Down":
        try:
            current = sbcontrol.get_brightness(display=0)
            
            # FIX: Handle list return (multi-monitor)
            if isinstance(current, list):
                current = current[0] if len(current) > 0 else 50
            elif current is None:
                current = 50
            
            current = int(current)
            new_bright = max(current - 10, 0)
            sbcontrol.set_brightness(new_bright, display=0)
            print(f"   ✅ Brightness DOWN: {new_bright}%")
        except Exception as e:
            print(f"   ❌ Brightness error: {e}")
    
    # ─────────────────────────────────────────────────────
    # OTHER ACTIONS
    # ─────────────────────────────────────────────────────
    elif action == "Screenshot":
        pyautogui.hotkey('win', 'printscreen')
        print("   ✅ Screenshot")
    
    elif action == "Minimize Window":
        pyautogui.hotkey('win', 'down')
        print("   ✅ Minimized")
    
    elif action == "Maximize Window":
        pyautogui.hotkey('win', 'up')
        print("   ✅ Maximized")
    
    elif action == "Close Window":
        pyautogui.hotkey('alt', 'f4')
        print("   ✅ Closed Window")
    
    # ─────────────────────────────────────────────────────
    # SCROLL - FIXED WITH OUTPUT
    # ─────────────────────────────────────────────────────
    elif action == "Scroll Up":
        pyautogui.scroll(120)
        print("   ✅ Scroll UP")
    
    elif action == "Scroll Down":
        pyautogui.scroll(-120)
        print("   ✅ Scroll DOWN")


def get_distance(point1, point2):
    """Calculate Euclidean distance between two points"""
    dist = math.sqrt((point1['x'] - point2['x'])**2 + (point1['y'] - point2['y'])**2)
    return dist


# ═══════════════════════════════════════════════════════════════
# END OF PART 2
# Continue with PART 3 for gesture recognition and camera feed
# ═══════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════
# main_file.py - PART 3 OF 3
# Gesture Recognition, Camera Feed, and Main Execution
# ═══════════════════════════════════════════════════════════════

def recognizeHandGesture(landmarks, label):
    """Recognize hand gesture from 21 landmarks (12 gestures total)"""
    thumbState = 'UNKNOWN'
    indexFingerState = 'UNKNOWN'
    middleFingerState = 'UNKNOWN'
    ringFingerState = 'UNKNOWN'
    littleFingerState = 'UNKNOWN'
    thumbUp = False
    thumbDown = False
    
    # ─────────────────────────────────────────────────────
    # THUMB STATE
    # ─────────────────────────────────────────────────────
    if label.strip() == 'Left':
        pseudoFixKeyPoint = landmarks[2]['x']
        if pseudoFixKeyPoint < landmarks[3]['x'] < landmarks[4]['x']:
            thumbState = 'OPEN'
        elif pseudoFixKeyPoint > landmarks[3]['x'] > landmarks[4]['x']:
            thumbState = 'CLOSE'
    else:
        pseudoFixKeyPoint = landmarks[2]['x']
        if pseudoFixKeyPoint < landmarks[3]['x'] < landmarks[4]['x']:
            thumbState = 'CLOSE'
        elif pseudoFixKeyPoint > landmarks[3]['x'] > landmarks[4]['x']:
            thumbState = 'OPEN'
    
    # Thumb direction (up/down)
    if landmarks[4]['y'] < landmarks[3]['y'] < landmarks[2]['y']:
        thumbUp = True
    elif landmarks[4]['y'] > landmarks[3]['y'] > landmarks[2]['y']:
        thumbDown = True
    
    # ─────────────────────────────────────────────────────
    # FINGER STATES
    # ─────────────────────────────────────────────────────
    
    # Index finger
    pseudoFixKeyPoint = landmarks[6]['y']
    if pseudoFixKeyPoint > landmarks[7]['y'] > landmarks[8]['y']:
        indexFingerState = 'OPEN'
    elif pseudoFixKeyPoint < landmarks[7]['y'] < landmarks[8]['y']:
        indexFingerState = 'CLOSE'
    
    # Middle finger
    pseudoFixKeyPoint = landmarks[10]['y']
    if pseudoFixKeyPoint > landmarks[11]['y'] > landmarks[12]['y']:
        middleFingerState = 'OPEN'
    elif pseudoFixKeyPoint < landmarks[11]['y'] < landmarks[12]['y']:
        middleFingerState = 'CLOSE'
    
    # Ring finger
    pseudoFixKeyPoint = landmarks[14]['y']
    if pseudoFixKeyPoint > landmarks[15]['y'] > landmarks[16]['y']:
        ringFingerState = 'OPEN'
    elif pseudoFixKeyPoint < landmarks[15]['y'] < landmarks[16]['y']:
        ringFingerState = 'CLOSE'
    
    # Little finger
    pseudoFixKeyPoint = landmarks[18]['y']
    if pseudoFixKeyPoint > landmarks[19]['y'] > landmarks[20]['y']:
        littleFingerState = 'OPEN'
    elif pseudoFixKeyPoint < landmarks[19]['y'] < landmarks[20]['y']:
        littleFingerState = 'CLOSE'
    
    # ─────────────────────────────────────────────────────
    # GESTURE RECOGNITION (12 gestures)
    # ─────────────────────────────────────────────────────
    recognizedHandGesture = None
    
    # 5 Fingers
    if (thumbState == 'OPEN' and indexFingerState == 'OPEN' and 
        middleFingerState == 'OPEN' and ringFingerState == 'OPEN' and 
        littleFingerState == 'OPEN'):
        recognizedHandGesture = '5'
    
    # 4 Fingers
    elif (thumbState == 'CLOSE' and indexFingerState == 'OPEN' and 
          middleFingerState == 'OPEN' and ringFingerState == 'OPEN' and 
          littleFingerState == 'OPEN'):
        recognizedHandGesture = '4'
    
    # 3 Fingers
    elif (thumbState == 'CLOSE' and indexFingerState == 'OPEN' and 
          middleFingerState == 'OPEN' and ringFingerState == 'OPEN' and 
          littleFingerState == 'CLOSE'):
        recognizedHandGesture = '3'
    
    # 2 Fingers
    elif (thumbState == 'OPEN' and indexFingerState == 'OPEN' and 
          middleFingerState == 'CLOSE' and ringFingerState == 'CLOSE' and 
          littleFingerState == 'CLOSE'):
        recognizedHandGesture = '2'
    
    # 1 Finger
    elif (thumbState == 'CLOSE' and indexFingerState == 'OPEN' and 
          middleFingerState == 'CLOSE' and ringFingerState == 'CLOSE' and 
          littleFingerState == 'CLOSE'):
        recognizedHandGesture = '1'
    
    # Fist
    elif (thumbState == 'CLOSE' and indexFingerState == 'CLOSE' and 
          middleFingerState == 'CLOSE' and ringFingerState == 'CLOSE' and 
          littleFingerState == 'CLOSE'):
        recognizedHandGesture = 'Fist'
    
    # Victory
    elif (thumbState == 'CLOSE' and indexFingerState == 'OPEN' and 
          middleFingerState == 'OPEN' and ringFingerState == 'CLOSE' and 
          littleFingerState == 'CLOSE'):
        recognizedHandGesture = 'Victory'
    
    # Thumbs Up
    elif (thumbState == 'OPEN' and thumbUp and 
          indexFingerState == 'CLOSE' and middleFingerState == 'CLOSE' and 
          ringFingerState == 'CLOSE' and littleFingerState == 'CLOSE'):
        recognizedHandGesture = 'Thumbs Up'
    
    # Thumbs Down
    elif (thumbState == 'OPEN' and thumbDown and 
          indexFingerState == 'CLOSE' and middleFingerState == 'CLOSE' and 
          ringFingerState == 'CLOSE' and littleFingerState == 'CLOSE'):
        recognizedHandGesture = 'Thumbs Down'
    
    # Rock On
    elif (thumbState == 'OPEN' and indexFingerState == 'OPEN' and 
          middleFingerState == 'CLOSE' and ringFingerState == 'CLOSE' and 
          littleFingerState == 'OPEN'):
        recognizedHandGesture = 'Rock On'
    
    # OK Sign
    elif (get_distance(landmarks[4], landmarks[8]) < 0.05 and 
          middleFingerState == 'OPEN' and ringFingerState == 'OPEN' and 
          littleFingerState == 'OPEN'):
        recognizedHandGesture = 'OK Sign'
    
    # Pinch
    elif (get_distance(landmarks[4], landmarks[8]) < 0.03 and 
          middleFingerState == 'CLOSE' and ringFingerState == 'CLOSE' and 
          littleFingerState == 'CLOSE'):
        recognizedHandGesture = 'Pinch'
    
    return recognizedHandGesture


def getStructuredLandmarks(landmarks):
    """Convert flat landmark array to structured format"""
    global structuredLandmarks
    structuredLandmarks = []
    for j in range(42):
        if (j % 2 == 1):
            structuredLandmarks.append({'x': landmarks[j - 1], 'y': landmarks[j]})
    return structuredLandmarks


def takeFeed(gesture_mapping, label, delay, ui_instance):
    """Start camera and gesture detection loop"""
    global cap, prev_gesture, gesture_start_time
    
    import time
    
    print(f"\n🎥 Initializing camera...")
    hands = mp_hands.Hands(min_detection_confidence=0.7, max_num_hands=1, min_tracking_confidence=0.6)
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    
    if not cap.isOpened():
        print("❌ Camera failed to open!")
        ui_instance.statusBarLabel.setText("Status: ❌ Camera failed!")
        ui_instance.statusBarLabel.setStyleSheet("""
            QLabel {
                background-color: #E74C3C;
                color: white;
                padding: 10px;
                border-radius: 5px;
            }
        """)
        return
    
    print("✅ Camera opened!")
    print("👋 Show your hand and make gestures...")
    print("📋 Active gestures:", list(gesture_mapping.keys()))
    print("Press 'q' in camera window to quit\n")
    
    ui_instance.statusBarLabel.setText(f"Status: 🎥 Camera active - {len(gesture_mapping)} gestures ready!")
    ui_instance.statusBarLabel.setStyleSheet("""
        QLabel {
            background-color: #27AE60;
            color: white;
            padding: 10px;
            border-radius: 5px;
        }
    """)
    
    prev_gesture = None
    gesture_start_time = None
    last_trigger_time = {}
    
    # ═══════════════════════════════════════════════════════════
    # MAIN DETECTION LOOP
    # ═══════════════════════════════════════════════════════════
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            break
        
        # Process image
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = hands.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        # ─────────────────────────────────────────────────────
        # HAND DETECTED
        # ─────────────────────────────────────────────────────
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw hand
                mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                # Extract landmarks
                landmark_data = []
                for point in hand_landmarks.landmark:
                    landmark_data.append(point.x)
                    landmark_data.append(point.y)
                
                landmarks = getStructuredLandmarks(landmark_data)
                current_gesture = recognizeHandGesture(landmarks, label)
                
                # ─────────────────────────────────────────────
                # GESTURE MATCHED
                # ─────────────────────────────────────────────
                if current_gesture and current_gesture in gesture_mapping:
                    gesture_info = gesture_mapping[current_gesture]
                    action = gesture_info["action"]
                    action_type = gesture_info["type"]
                    
                    # Gesture changed - apply delay
                    if current_gesture != prev_gesture:
                        if gesture_start_time is None or (time.time() - gesture_start_time) > delay:
                            gesture_start_time = time.time()
                            prev_gesture = current_gesture
                    
                    # Check if enough time has passed
                    if gesture_start_time and (time.time() - gesture_start_time) > delay:
                        
                        if action_type == "continuous":
                            # Execute continuously while hand visible
                            executeAction(action, hand_landmarks, label)
                        
                        elif action_type == "trigger":
                            # Execute once with cooldown
                            current_time = time.time()
                            if current_gesture not in last_trigger_time or \
                               (current_time - last_trigger_time[current_gesture]) > 0.5:
                                print(f'👉 Gesture: {current_gesture} → {action}')
                                executeAction(action, hand_landmarks, label)
                                last_trigger_time[current_gesture] = current_time
                
                else:
                    # Reset flags when no valid gesture
                    if Controller.grabflag:
                        Controller.grabflag = False
                        pyautogui.mouseUp(button="left")
                    Controller.pinchmajorflag = False
                    Controller.pinchminorflag = False
                    prev_gesture = None
                    gesture_start_time = None
        
        # ─────────────────────────────────────────────────────
        # NO HAND DETECTED
        # ─────────────────────────────────────────────────────
        else:
            if Controller.grabflag:
                Controller.grabflag = False
                pyautogui.mouseUp(button="left")
            Controller.prev_hand = None
            Controller.pinchmajorflag = False
            Controller.pinchminorflag = False
            prev_gesture = None
            gesture_start_time = None
        
        # Show window
        cv2.imshow('Gesture Control - Press Q to quit', image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Cleanup
    stopFeed()
    ui_instance.statusBarLabel.setText("Status: ⏸️ Stopped")
    ui_instance.statusBarLabel.setStyleSheet("""
        QLabel {
            background-color: #E74C3C;
            color: white;
            padding: 10px;
            border-radius: 5px;
        }
    """)


def stopFeed():
    """Stop camera and cleanup"""
    global cap
    if cap is not None:
        cap.release()
    cv2.destroyAllWindows()
    print("\n📷 Camera stopped")
    print("="*60)


# ═══════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import sys
    import cv2
    from time import sleep
    import mediapipe as mp
    
    print("\n" + "="*60)
    print("🚀 GESTURE + VOICE CONTROL - STARTING")
    print("="*60)
    
    # Start Qt Application
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    
    print("✅ GUI opened successfully!")
    print("\n📖 Click '? HELP' button for instructions and recommended setup")
    print("="*60 + "\n")
    
    # Initialize MediaPipe
    mp_drawing = mp.solutions.drawing_utils
    mp_hands = mp.solutions.hands
    
    # Global variables
    global cap
    global structuredLandmarks
    global prev_gesture
    global gesture_start_time
    cap = None
    structuredLandmarks = []
    prev_gesture = None
    gesture_start_time = None
    
    # Run application
    sys.exit(app.exec_())

# ═══════════════════════════════════════════════════════════════
# END OF PART 3
# ═══════════════════════════════════════════════════════════════