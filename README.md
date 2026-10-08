# 🤖 AIVA — Personal AI Assistant

> A multimodal AI-powered desktop assistant built with Python, Google Gemini, YOLO, OpenCV, and CustomTkinter.

AIVA (AI Virtual Assistant) is a Python-based desktop application that combines **Generative AI, Computer Vision, Voice Interaction, and System Monitoring** into a single interactive assistant.

AIVA can understand natural-language conversations, analyze images, detect objects, interact through voice, monitor system resources, and maintain conversation memory through a modern desktop interface.

---

## ✨ Features

* 💬 **AI Chat** — Natural-language conversations powered by Google Gemini
* 🖼️ **Image Analysis** — Ask questions about uploaded images using Gemini Vision
* 🎯 **Object Detection** — Detect objects using YOLO
* 📷 **Webcam Detection** — Real-time object detection through webcam
* 🎙️ **Voice Input** — Speech-to-text interaction using SpeechRecognition
* 🔊 **Voice Output** — Text-to-speech responses using pyttsx3
* 🧠 **Conversation Memory** — Stores relevant conversation information
* 💻 **System Monitoring** — Monitor CPU, RAM, and disk usage
* 📤 **Chat Export** — Export conversations for future reference
* 🎨 **Modern UI** — Responsive desktop interface built with CustomTkinter
* 🖥️ **Windows Application** — Can be packaged as a standalone desktop application

---

## 🧠 System Architecture

```text
                     ┌──────────────────┐
                     │      User        │
                     └────────┬─────────┘
                              │
                    Text / Voice / Image
                              │
                              ▼
                    ┌──────────────────┐
                    │  AIVA Interface  │
                    │   CustomTkinter  │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
        ┌──────────┐   ┌──────────┐   ┌──────────┐
        │  Gemini  │   │   YOLO   │   │  Voice   │
        │   AI     │   │Detection │   │   I/O    │
        └────┬─────┘   └────┬─────┘   └────┬─────┘
             │              │              │
             └──────────────┼──────────────┘
                            ▼
                    ┌────────────────┐
                    │ AIVA Response  │
                    └────────────────┘
```

---

## 🛠️ Tech Stack

| Technology            | Purpose                             |
| --------------------- | ----------------------------------- |
| **Python**            | Core application development        |
| **Google Gemini API** | Generative AI & image understanding |
| **YOLO**              | Object detection                    |
| **OpenCV**            | Image & webcam processing           |
| **CustomTkinter**     | Desktop GUI                         |
| **SpeechRecognition** | Speech-to-text                      |
| **pyttsx3**           | Text-to-speech                      |
| **psutil**            | System monitoring                   |
| **PyInstaller**       | Windows executable packaging        |

---

## 📂 Project Structure

```text
AIVA-personal-assistant/
│
├── ai.py
├── aiva_app.py
├── aiva.ico
├── .gitignore
├── requirements.txt
└── README.md
```

> YOLO model weights, personal memory files, chat logs, build files, and API keys are intentionally excluded from the repository.

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/akashsekar-cpu/AIVA-personal-assistant.git
```

### 2. Open the project

```bash
cd AIVA-personal-assistant
```

### 3. Create a virtual environment

Windows:

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 API Configuration

AIVA uses the Google Gemini API.

Create an environment variable for your API key instead of placing the key directly inside the source code.

Windows PowerShell:

```powershell
$env:GOOGLE_API_KEY="YOUR_API_KEY"
```

Or use a `.env` file if the project is configured with `python-dotenv`:

```text
GOOGLE_API_KEY=YOUR_API_KEY
```

⚠️ **Never commit your API key to GitHub.**

---

## 🤖 YOLO Model

AIVA uses YOLO for object detection.

The model weights are intentionally excluded from GitHub because model files can be large.

Download the required YOLO model and place it inside the project directory according to the model path configured in the application.

---

## ▶️ Running AIVA

After installing the dependencies and configuring your API key:

```bash
python aiva_app.py
```

The AIVA desktop interface should launch.

---

## 📸 Core Capabilities

### 💬 AI Conversation

AIVA uses Google's Gemini model to understand user questions and generate intelligent responses.

### 🖼️ Image Understanding

Users can provide images and ask questions about their contents. Gemini Vision processes the visual information and generates an explanation.

### 🎯 Object Detection

YOLO identifies objects in images and webcam frames.

Example:

```text
Image
  ↓
YOLO
  ↓
Object Detection
  ↓
Bounding Boxes + Labels
```

### 🎙️ Voice Interaction

AIVA supports voice-based interaction using speech recognition and text-to-speech technologies.

```text
User Voice
    ↓
Speech Recognition
    ↓
AIVA
    ↓
Gemini
    ↓
Response
    ↓
Text-to-Speech
```

### 💻 System Monitoring

AIVA can monitor:

* CPU usage
* RAM usage
* Disk usage

using the `psutil` library.

---

## 🔐 Security

The following files are intentionally excluded from version control:

```text
.env
*.pt
aiva_memory.json
aiva_chatlog.txt
build/
dist/
*.exe
```

This prevents sensitive credentials, personal conversation data, and large model files from being uploaded.

---

## 🚀 Future Improvements

* [ ] Add RAG-based document question answering
* [ ] Add PDF and document processing
* [ ] Add long-term conversational memory
* [ ] Add tool/function calling
* [ ] Add web search capabilities
* [ ] Add local LLM support
* [ ] Improve voice interaction
* [ ] Add multilingual voice support
* [ ] Add authentication
* [ ] Improve AI response evaluation
* [ ] Deploy backend services through APIs

---

## 🎯 Learning Outcomes

Through this project, the following practical concepts were implemented:

* Generative AI
* Large Language Model APIs
* Multimodal AI
* Computer Vision
* Object Detection
* Speech Recognition
* Text-to-Speech
* API Integration
* Desktop Application Development
* System Monitoring
* Python Application Architecture

---

## 👨‍💻 Author

**Akash Sekar**

AI & Data Science Student

GitHub: [@akashsekar-cpu](https://github.com/akashsekar-cpu)

---

## ⭐ Project

If you find this project useful or interesting, consider giving the repository a ⭐.
