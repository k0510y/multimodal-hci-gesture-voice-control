# Real-Time Multimodal Human-Computer Interaction via Gesture and Voice Control

A touchless computer interaction system that combines hand gesture recognition and voice commands to control desktop operations in real time.

## Overview

This project explores an alternative way of interacting with computers by integrating computer vision and speech recognition into a unified system.

Using a standard RGB webcam and built-in microphone, the application allows users to perform desktop operations through hand gestures and voice commands without requiring specialized hardware such as depth cameras, wearable sensors, or a dedicated GPU.

The system supports simultaneous gesture and voice interaction, allowing users to switch naturally between input methods without manually changing modes.

## Key Features

### 1. Hand Gesture Recognition
- Real-time hand tracking using MediaPipe Hands.
- Extraction of 21 hand landmarks.
- Geometric, rule-based classification of 12 hand postures.
- Virtual mouse movement and cursor control.
- Click, drag, scroll and other desktop interactions.

### 2. Voice Command Recognition
- Wake-word activation using "Computer".
- Speech recognition and keyword-based command parsing.
- Support for 22+ voice commands.
- Desktop operations including mouse control, scrolling, volume, brightness and window management.

### 3. Cursor Stabilization
- Three-zone damping mechanism to reduce unwanted cursor movement.
- Low-pass filtering and smoothing to minimize hand tremors.
- Landmark-based cursor tracking.

### 4. Analog Volume and Brightness Control
- Pinch-based interaction for continuous parameter adjustment.
- Vertical and horizontal hand movement for volume and brightness control.

### 5. Concurrent Execution
- Separate threads for gesture recognition, voice recognition and action processing.
- Queue-based communication for voice commands.
- Independent execution of both input modalities.

### 6. Graphical User Interface
- PyQt5-based desktop interface.
- Gesture-to-action configuration.
- Voice command reference.
- Hybrid, gesture-only and voice-only operating modes.
- Status indicators and recommended configurations.

### 7. Graceful Failure Handling
- Independent operation of gesture and voice channels.
- Voice functionality remains available during camera failure.
- Gesture functionality continues during network failure.

## Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Computer Vision | OpenCV, MediaPipe |
| Gesture Recognition | MediaPipe Hands, Geometric Classification |
| Speech Recognition | SpeechRecognition, Google Speech Recognition API |
| Desktop Automation | PyAutoGUI |
| Audio Control | PyCaw |
| Brightness Control | screen-brightness-control |
| GUI | PyQt5 |
| Concurrency | Python Threading, Queue |

## System Architecture

The application is organized into four functional layers:

1. **Hardware Input:** Captures webcam frames and microphone audio.
2. **Signal Processing:** Processes visual frames and recorded speech.
3. **Intelligence Layer:** Performs hand landmark detection, gesture classification and voice command recognition.
4. **Action Execution:** Translates recognized inputs into desktop operations.

Gesture and voice processing operate concurrently, coordinated through a control manager and inter-thread communication.

## Performance Evaluation

The system was evaluated under different lighting and background noise conditions.

| Metric | Result |
|---|---:|
| Gesture Recognition Accuracy | 95.2% |
| Voice Recognition Accuracy (Quiet) | 94.8% |
| Voice Recognition Accuracy (Moderate Noise) | 88.6% |
| Cursor Movement Latency | 68–75 ms |
| Click Latency | 72–85 ms |
| Scroll Latency | 80–95 ms |
| Voice Command Latency | 190–260 ms |
| System Usability Scale | 76.4 |

The evaluation included 15 participants and multiple lighting conditions.

## Installation

### Prerequisites
- Windows operating system
- Python 3.x
- Webcam
- Microphone
- Internet connectivity for cloud-based speech recognition

### Clone the Repository

```bash
git clone YOUR_REPOSITORY_URL
cd YOUR_REPOSITORY_NAME
```

### Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Application

```bash
python main.py
```



## License

A license can be added once the repository's intended usage and permissions have been decided.
