# control_manager.py
# ─────────────────────────────────────────────────────────────
# FULLY FIXED VERSION - All issues resolved
# ─────────────────────────────────────────────────────────────

import threading
from queue import Queue, Empty
import pyautogui
import time

from voice_engine import VoiceEngine

# ── Import from main_file ──
import main_file
from main_file import executeAction, takeFeed, Controller


class ControlManager:
    """
    Manages three modes:
      gesture  → your existing gesture system
      voice    → new voice control
      both     → gesture + voice at the same time
    """

    def __init__(self, ui_instance):
        self.ui = ui_instance
        self.mode = "gesture"

        self.action_queue = Queue()
        self.voice_engine = VoiceEngine(action_callback=self.handle_voice_action)

        self.gesture_mapping = {}
        self.gesture_label  = "Right"
        self.gesture_delay  = 0.3

        self.running = False
        self.gesture_thread          = None
        self.action_processor_thread = None

        # Track whether camera was started
        self._camera_started = False
        self._camera_stop_lock = threading.Lock()

        print("✅ Control Manager initialized")

    # ─────────────────────────────────────────────
    # MODE
    # ─────────────────────────────────────────────
    def set_mode(self, mode):
        if mode == self.mode:
            return
        print(f"🔄 {self.mode} → {mode}")
        self.stop()
        self.mode = mode

    # ─────────────────────────────────────────────
    # START — GESTURE ONLY
    # ─────────────────────────────────────────────
    def start_gesture_only(self, gesture_mapping, label, delay):
        print("\n🎮 STARTING GESTURE ONLY MODE")
        self.gesture_mapping = gesture_mapping
        self.gesture_label   = label
        self.gesture_delay   = delay
        self.running         = True
        
        with self._camera_stop_lock:
            self._camera_started = True

        # Run takeFeed in main thread (it has its own loop)
        try:
            takeFeed(gesture_mapping, label, delay, self.ui)
        except Exception as e:
            print(f"❌ Gesture error: {e}")
        finally:
            with self._camera_stop_lock:
                self._camera_started = False

    # ─────────────────────────────────────────────
    # START — VOICE ONLY
    # ─────────────────────────────────────────────
    def start_voice_only(self):
        print("\n🎤 STARTING VOICE ONLY MODE")
        self.running         = True
        
        with self._camera_stop_lock:
            self._camera_started = False  # No camera in voice-only

        self.voice_engine.start()

        self.action_processor_thread = threading.Thread(
            target=self._process_actions, daemon=True
        )
        self.action_processor_thread.start()
        
        print("✅ Voice-only mode active!")

    # ─────────────────────────────────────────────
    # START — BOTH (HYBRID)
    # ─────────────────────────────────────────────
    def start_both_parallel(self, gesture_mapping, label, delay):
        print("\n🤝 STARTING HYBRID MODE")
        self.gesture_mapping = gesture_mapping
        self.gesture_label   = label
        self.gesture_delay   = delay
        self.running         = True
        
        with self._camera_stop_lock:
            self._camera_started = True  # Camera will open

        # Gesture thread
        self.gesture_thread = threading.Thread(
            target=self._gesture_thread_func,
            args=(gesture_mapping, label, delay),
            daemon=True
        )
        self.gesture_thread.start()
        print("🎮 Gesture thread started")

        # Voice engine
        self.voice_engine.start()
        print("🎤 Voice engine started")

        # Action processor
        self.action_processor_thread = threading.Thread(
            target=self._process_actions, daemon=True
        )
        self.action_processor_thread.start()
        print("✅ Hybrid mode active!")

    # ─────────────────────────────────────────────
    # INTERNAL THREADS
    # ─────────────────────────────────────────────
    def _gesture_thread_func(self, gesture_mapping, label, delay):
        try:
            takeFeed(gesture_mapping, label, delay, self.ui)
        except Exception as e:
            print(f"❌ Gesture thread error: {e}")

    def handle_voice_action(self, action):
        print(f"🎤 Voice action: {action}")
        self.action_queue.put(action)

    def _process_actions(self):
        print("⚙️ Action processor running…")
        while self.running:
            try:
                action = self.action_queue.get(timeout=0.1)

                # mode switch request
                if action.get("action") == "switch_mode":
                    new_mode = action['params']['mode']
                    print(f"🔄 Mode switch requested: {new_mode}")
                    # Let the UI handle mode switching
                    continue

                # voice mouse — absolute
                if action.get("action") == "mouse_move":
                    self._voice_mouse_abs(action["params"])

                # voice mouse — relative
                elif action.get("action") == "mouse_move_relative":
                    self._voice_mouse_rel(action["params"])

                # everything else → your existing executeAction()
                else:
                    name = action.get("action")
                    if name:
                        executeAction(name, None, self.gesture_label)

            except Empty:
                continue
            except Exception as e:
                print(f"❌ Action error: {e}")

        print("⚙️ Action processor stopped")

    # ─────────────────────────────────────────────
    # VOICE MOUSE HELPERS
    # ─────────────────────────────────────────────
    def _voice_mouse_abs(self, params):
        if params.get("position") == "center":
            sw, sh = pyautogui.size()
            x, y = sw // 2, sh // 2
            pyautogui.moveTo(x, y, duration=0.5)
            print(f"   🖱️ Center ({x}, {y})")

    def _voice_mouse_rel(self, params):
        cx, cy = pyautogui.position()
        sw, sh = pyautogui.size()
        nx = max(0, min(cx + params.get("x", 0), sw - 1))
        ny = max(0, min(cy + params.get("y", 0), sh - 1))
        pyautogui.moveTo(nx, ny, duration=0.3)
        print(f"   🖱️ Moved to ({nx}, {ny})")

    # ─────────────────────────────────────────────
    # STOP  ← FIXED VERSION
    # ─────────────────────────────────────────────
    def stop(self):
        print("\n⏹️ Stopping…")
        self.running = False

        # Stop voice if it was running
        if self.voice_engine.listening:
            try:
                self.voice_engine.stop()
            except Exception as e:
                print(f"⚠️ Voice stop error: {e}")

        # Only stop camera if it was started
        with self._camera_stop_lock:
            if self._camera_started:
                try:
                    # Safe camera cleanup
                    if hasattr(main_file, 'cap') and main_file.cap is not None:
                        if main_file.cap.isOpened():
                            main_file.cap.release()
                        main_file.cap = None
                    
                    # Close OpenCV windows
                    try:
                        import cv2
                        cv2.destroyAllWindows()
                        # Give time for windows to close
                        time.sleep(0.1)
                    except Exception as e:
                        print(f"⚠️ CV2 cleanup: {e}")
                        
                except Exception as e:
                    print(f"⚠️ Camera cleanup: {e}")
                
                self._camera_started = False

        # Wait for threads
        if self.gesture_thread and self.gesture_thread.is_alive():
            self.gesture_thread.join(timeout=2)
        if self.action_processor_thread and self.action_processor_thread.is_alive():
            self.action_processor_thread.join(timeout=2)

        # Drain queue
        while not self.action_queue.empty():
            try:
                self.action_queue.get_nowait()
            except Empty:
                break

        print("✅ All stopped")