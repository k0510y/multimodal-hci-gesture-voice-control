# voice_engine.py
# FINAL VERSION - 10 second timeout, handles partial commands, all fixes

import speech_recognition as sr
import pyttsx3
from threading import Thread, Event
import time
import re

class VoiceEngine:
    """Ultra-accurate voice control with 10-second user timeout"""
    
    def __init__(self, action_callback=None):
        print("🎤 Initializing Voice Engine...")
        
        # Speech Recognition
        self.recognizer = sr.Recognizer()
        
        # BALANCED SETTINGS (not too aggressive)
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8  # ← More patient
        self.recognizer.phrase_threshold = 0.3  # ← Wait longer to start
        self.recognizer.non_speaking_duration = 0.5  # ← Wait longer to finish
        
        self.microphone = sr.Microphone()
        
        # TTS
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 180)  # Slightly slower
            self.tts_engine.setProperty('volume', 0.8)
            self.tts_enabled = True
        except:
            self.tts_enabled = False
        
        # Configuration
        self.wake_word = "computer"
        self.listening = False
        self.action_callback = action_callback
        
        # Thread control
        self.stop_event = Event()
        self.listen_thread = None
        
        # Quick calibration
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print("✅ Ready")
        except Exception as e:
            print(f"⚠️ {e}")
        
        print("✅ Voice Engine ready")
    
    def start(self):
        if self.listening:
            return
        
        self.listening = True
        self.stop_event.clear()
        
        self.listen_thread = Thread(target=self._listen_loop, daemon=True)
        self.listen_thread.start()
        
        self.speak("Ready")
        print(f"🎤 Listening for '{self.wake_word}'...")
    
    def stop(self):
        if not self.listening:
            return
        
        self.listening = False
        self.stop_event.set()
        
        if self.listen_thread and self.listen_thread.is_alive():
            self.listen_thread.join(timeout=1)
        
        print("✅ Voice stopped")
    
    def _listen_loop(self):
        """Main listening loop with 10-second user patience"""
        error_count = 0
        
        while self.listening and not self.stop_event.is_set():
            try:
                with self.microphone as source:
                    # Gentle ambient adjustment
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                    
                    # ⏱️ LONGER TIMEOUT - Give user time to think
                    audio = self.recognizer.listen(
                        source,
                        timeout=3,            # Wait 3 seconds for speech to start
                        phrase_time_limit=10  # ← 10 SECONDS to finish speaking!
                    )
                    
                    # Convert to text
                    text = self.recognizer.recognize_google(audio, language='en-US').lower()
                    
                    # Clean text
                    text = self._clean_text(text)
                    
                    error_count = 0
                    
                    # Check for wake word
                    if self.wake_word in text:
                        print(f"✅ Wake: '{text}'")
                        
                        # Extract command
                        command = self._extract_command(text)
                        
                        if command:
                            # Command in same phrase
                            print(f"🎤 Command: '{command}'")
                            self._execute_command(command)
                        else:
                            # Wait for command
                            self.speak("Yes")
                            
                            try:
                                # ⏱️ LONG TIMEOUT - 10 seconds to say command
                                cmd_audio = self.recognizer.listen(
                                    source,
                                    timeout=3,
                                    phrase_time_limit=10  # ← 10 seconds!
                                )
                                command = self.recognizer.recognize_google(cmd_audio, language='en-US').lower()
                                command = self._clean_text(command)
                                
                                print(f"🎤 Command: '{command}'")
                                self._execute_command(command)
                                
                            except sr.WaitTimeoutError:
                                print("⏱️ Timeout - no command")
                                self.speak("Timeout")
                            except sr.UnknownValueError:
                                print("❓ Could not understand")
                                self.speak("Not clear")
                
            except sr.WaitTimeoutError:
                continue  # Normal
                
            except sr.UnknownValueError:
                error_count += 1
                if error_count >= 10:
                    error_count = 0
                continue
                
            except sr.RequestError as e:
                print(f"❌ API error: {e}")
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Error: {e}")
                time.sleep(0.5)
            
            # Tiny delay
            time.sleep(0.05)
    
    def _clean_text(self, text):
        """Clean text - remove punctuation, fix mishears"""
        # Remove punctuation
        text = re.sub(r'[^\w\s]', '', text)
        
        # Normalize spaces
        text = ' '.join(text.split())
        
        # Lowercase
        text = text.lower()
        
        # Corrections
        corrections = {
            # Wake word
            'computa': 'computer',
            'computers': 'computer',
            'compute': 'computer',
            'computerr': 'computer',
            'computor': 'computer',
            
            # Click
            'clique': 'click',
            'clic': 'click',
            'clickk': 'click',
            
            # Scroll
            'scrollup': 'scroll up',
            'scrolldown': 'scroll down',
            
            # Volume
            'volumeup': 'volume up',
            'volumedown': 'volume down',
            
            # Brightness
            'brightnessup': 'brightness up',
            'brightnessdown': 'brightness down',
            
            # Clicks
            'rightclick': 'right click',
            'doubleclick': 'double click',
        }
        
        for wrong, right in corrections.items():
            text = text.replace(wrong, right)
        
        return text
    
    def _extract_command(self, text):
        """Extract command after wake word"""
        wake_pos = text.find(self.wake_word)
        
        if wake_pos == -1:
            return None
        
        # Get everything after wake word
        after_wake = text[wake_pos + len(self.wake_word):].strip()
        
        # Remove stray single letters
        while after_wake and len(after_wake) > 0 and after_wake[0] in 'rstuvwxyz' and (len(after_wake) == 1 or after_wake[1] == ' '):
            after_wake = after_wake[1:].strip()
        
        return after_wake if after_wake else None
    
    def _execute_command(self, command):
        """Execute command"""
        action = self._parse_command(command)
        if action and self.action_callback:
            self.action_callback(action)
    
    def _parse_command(self, cmd):
        """
        IMPROVED COMMAND PARSING
        Handles partial commands like "volume" or "brightness"
        """
        
        # ══════════════════════════════════════════════════════
        # MOUSE MOVEMENT
        # ══════════════════════════════════════════════════════
        
        # Center
        if any(word in cmd for word in ['center', 'centre', 'middle']):
            self.speak("Center")
            return {"source": "voice", "action": "mouse_move", "params": {"position": "center"}}
        
        # Directional
        if 'mouse' in cmd or 'cursor' in cmd or 'move' in cmd:
            if 'up' in cmd:
                self.speak("Up")
                return {"source": "voice", "action": "mouse_move_relative", "params": {"x": 0, "y": -100}}
            elif 'down' in cmd and 'scroll' not in cmd:
                self.speak("Down")
                return {"source": "voice", "action": "mouse_move_relative", "params": {"x": 0, "y": 100}}
            elif 'left' in cmd:
                self.speak("Left")
                return {"source": "voice", "action": "mouse_move_relative", "params": {"x": -100, "y": 0}}
            elif 'right' in cmd and 'click' not in cmd:
                self.speak("Right")
                return {"source": "voice", "action": "mouse_move_relative", "params": {"x": 100, "y": 0}}
        
        # ══════════════════════════════════════════════════════
        # CLICKS
        # ══════════════════════════════════════════════════════
        
        if 'double' in cmd and 'click' in cmd:
            self.speak("Double click")
            return {"source": "voice", "action": "Double Click"}
        
        if 'right' in cmd and 'click' in cmd:
            self.speak("Right click")
            return {"source": "voice", "action": "Right Click"}
        
        if 'click' in cmd:
            self.speak("Click")
            return {"source": "voice", "action": "Left Click"}
        
        # ══════════════════════════════════════════════════════
        # SCROLL
        # ══════════════════════════════════════════════════════
        
        if 'scroll' in cmd:
            if 'up' in cmd or 'off' in cmd:
                self.speak("Scroll up")
                return {"source": "voice", "action": "Scroll Up"}
            elif 'down' in cmd:
                self.speak("Scroll down")
                return {"source": "voice", "action": "Scroll Down"}
        
        # ══════════════════════════════════════════════════════
        # VOLUME - IMPROVED: Handles just "volume"
        # ══════════════════════════════════════════════════════
        
        if 'volume' in cmd or 'sound' in cmd:
            if 'up' in cmd or 'increase' in cmd or 'louder' in cmd or 'higher' in cmd or 'raise' in cmd:
                self.speak("Volume up")
                return {"source": "voice", "action": "Volume Up"}
            elif 'down' in cmd or 'decrease' in cmd or 'quieter' in cmd or 'lower' in cmd:
                self.speak("Volume down")
                return {"source": "voice", "action": "Volume Down"}
            else:
                # Just "volume" without direction
                self.speak("Say up or down")
                print("   💡 Hint: Say 'volume up' or 'volume down'")
                return None
        
        if 'mute' in cmd or 'unmute' in cmd or 'silence' in cmd:
            self.speak("Mute toggle")
            return {"source": "voice", "action": "Mute Toggle"}
        
        # ══════════════════════════════════════════════════════
        # BRIGHTNESS - IMPROVED: Handles just "brightness"
        # ══════════════════════════════════════════════════════
        
        if 'brightness' in cmd or 'bright' in cmd:
            if 'up' in cmd or 'increase' in cmd or 'brighter' in cmd or 'higher' in cmd or 'raise' in cmd:
                self.speak("Brighter")
                return {"source": "voice", "action": "Brightness Up"}
            elif 'down' in cmd or 'decrease' in cmd or 'dimmer' in cmd or 'darker' in cmd or 'lower' in cmd:
                self.speak("Dimmer")
                return {"source": "voice", "action": "Brightness Down"}
            else:
                # Just "brightness" without direction
                self.speak("Say up or down")
                print("   💡 Hint: Say 'brightness up' or 'brightness down'")
                return None
        
        # ══════════════════════════════════════════════════════
        # WINDOW MANAGEMENT
        # ══════════════════════════════════════════════════════
        
        if 'minimize' in cmd or 'minimise' in cmd:
            self.speak("Minimize")
            return {"source": "voice", "action": "Minimize Window"}
        
        if 'maximize' in cmd or 'maximise' in cmd:
            self.speak("Maximize")
            return {"source": "voice", "action": "Maximize Window"}
        
        if any(word in cmd for word in ['close window', 'close app', 'close this', 'exit']):
            self.speak("Closing")
            return {"source": "voice", "action": "Close Window"}
        
        # ══════════════════════════════════════════════════════
        # OTHER
        # ══════════════════════════════════════════════════════
        
        if 'screenshot' in cmd or 'screen shot' in cmd or 'capture' in cmd or 'snap' in cmd:
            self.speak("Screenshot")
            return {"source": "voice", "action": "Screenshot"}
        
        # ══════════════════════════════════════════════════════
        # MODE SWITCHING
        # ══════════════════════════════════════════════════════
        
        if 'gesture' in cmd and ('mode' in cmd or 'switch' in cmd or 'only' in cmd):
            self.speak("Gesture mode")
            return {"source": "voice", "action": "switch_mode", "params": {"mode": "gesture"}}
        
        if 'voice' in cmd and ('mode' in cmd or 'switch' in cmd or 'only' in cmd):
            self.speak("Voice mode")
            return {"source": "voice", "action": "switch_mode", "params": {"mode": "voice"}}
        
        if any(word in cmd for word in ['both', 'hybrid', 'enable both']):
            self.speak("Hybrid mode")
            return {"source": "voice", "action": "switch_mode", "params": {"mode": "both"}}
        
        # ══════════════════════════════════════════════════════
        # UNKNOWN
        # ══════════════════════════════════════════════════════
        
        print(f"❌ Unknown command: '{cmd}'")
        self.speak("Unknown command")
        return None
    
    def speak(self, text):
        """Text-to-speech"""
        if not self.tts_enabled:
            return
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except:
            pass


# TEST
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎤 VOICE ENGINE TEST - 10 SECOND TIMEOUT")
    print("="*60)
    
    def callback(action):
        print(f"✅ ACTION: {action}")
    
    engine = VoiceEngine(action_callback=callback)
    
    print("\nSay: 'computer, volume up'")
    print("You have 10 seconds to speak!")
    print("Press Ctrl+C to stop\n")
    
    try:
        engine.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping...")
        engine.stop()