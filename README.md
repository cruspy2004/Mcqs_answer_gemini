# MCQ Answer Solver with Gemini AI

Automatically capture screenshots of Multiple Choice Questions and get AI-powered answers via Google's Gemini API.

## Features

- 🎯 **Hotkey Activation**: Press `ALT + S` to capture and analyze
- 🤖 **Gemini AI**: Powered by Google's Gemini 2.0 Flash model
- 🔔 **Desktop Notifications**: Answers appear as Windows notifications
- 📸 **Screenshot Capture**: Automatic full-screen capture
- ⚡ **Fast Response**: Quick analysis and answer delivery

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/cruspy2004/Mcqs_answer_gemini.git
cd Mcqs_answer_gemini
```

### 2. Install Dependencies

```bash
# Create virtual environment (optional but recommended)
python -m venv .venv
.venv\Scripts\activate

# Install required packages
pip install keyboard pyautogui requests pillow win10toast google-generativeai pytesseract
```

### 3. Get Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the API key

### 4. Set Environment Variable

**Windows Command Prompt:**
```cmd
set GEMINI_API_KEY=your_api_key_here
```

**Windows PowerShell:**
```powershell
$env:GEMINI_API_KEY="your_api_key_here"
```

**For permanent setup, add to system environment variables:**
1. Right-click "This PC" → Properties → Advanced System Settings
2. Click "Environment Variables"
3. Add new User variable: `GEMINI_API_KEY` with your key

### 5. Run the Script

**Option 1: Basic Script (script.py)**
```bash
python script.py
```

**Option 2: Advanced Overlay Script (script2.py)**
```bash
python script2.py
```

## Usage

1. **Start the script** - Run either script from command line
2. **Open an MCQ** - Display a multiple choice question on your screen
3. **Press ALT + S** - Capture screenshot and send to Gemini
4. **Get Answer** - Notification appears with the correct option (A, B, C, or D)

## Scripts

### script.py
- Simple implementation
- Desktop notifications
- Keyboard hotkey: `ALT + S`

### script2.py
- Advanced features with overlay UI
- OCR fallback support
- Keyboard hotkey: `A + S`
- Exit hotkey: `ALT + 4`

## Requirements

- Python 3.7+
- Windows OS (for notifications and keyboard hooks)
- Active internet connection
- Google Gemini API key

## Security Note

⚠️ **IMPORTANT**: Never commit your actual API key to version control. This repository uses environment variables to protect your credentials.

## Troubleshooting

**Keyboard not responding:**
- Run PowerShell or Command Prompt as Administrator
- The `keyboard` library requires elevated privileges on Windows

**"GEMINI_API_KEY not set" error:**
- Make sure you've set the environment variable before running the script
- Restart your terminal after setting environment variables

**Module not found errors:**
- Ensure all dependencies are installed in your active Python environment
- If using virtual environment, make sure it's activated

## License

MIT License - Feel free to use and modify

## Contributing

Pull requests are welcome! For major changes, please open an issue first.

---

**Made with ❤️ for students and learners**
