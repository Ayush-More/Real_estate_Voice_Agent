# Real Estate Voice Agent

AI-powered real estate sales agent built with [Pipecat](https://docs.pipecat.ai/). Phase 1 runs locally using your laptop microphone and speakers.

## Architecture

```
Browser (mic/speaker)
    ↕ WebRTC
Python Server (Pipecat Runner)
    → Deepgram STT → Gemini LLM → Cartesia TTS
```

## Project Structure

```
Voice Agent/
├── server/                  # Python backend
│   ├── bot.py               # Main entry — pipeline + server
│   ├── config/
│   │   └── prompts.py       # Real estate system prompts
│   ├── pyproject.toml       # Python dependencies
│   ├── .env                 # API keys (git-ignored)
│   └── .env.example         # Template for API keys
├── client/                  # Test frontend
│   ├── index.html           # Start/Stop UI
│   ├── js/app.js            # Pipecat WebRTC client
│   └── css/style.css        # UI styles
└── README.md
```

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- A modern browser (Chrome/Edge recommended) with microphone access

## Setup

1. **Install dependencies**

   ```powershell
   cd server
   uv sync
   ```

2. **Configure API keys** (already set in `server/.env` if you provided them)

   ```powershell
   copy .env.example .env
   # Edit .env with your Deepgram, Google, and Cartesia keys
   ```

## Start the Project

```powershell
cd server
uv run bot.py
```

Then open **http://localhost:7860** in your browser.

1. Click **Start Conversation**
2. Allow microphone access when prompted
3. Speak with the agent (it plays responses through your speakers)
4. Click **Stop Conversation** when done

## Quick Summary — How It Works

| Step | What Happens |
|------|-------------|
| 1 | You click **Start** → browser connects to the server via WebRTC |
| 2 | Your microphone audio streams to the Python server |
| 3 | **Deepgram** transcribes your speech to text |
| 4 | **Gemini** generates a salesperson response based on the real estate prompt |
| 5 | **Cartesia** converts the response to natural speech |
| 6 | Audio plays through your laptop speakers |
| 7 | You click **Stop** → WebRTC disconnects and the session ends |

The agent persona ("Alex") promotes **Sunrise Heights Residency** in Whitefield, Bangalore. This is a test property for Phase 1.

## Phase 2 (Coming Next)

- Connect to a telephony provider for outbound calls
- Load contact list from Excel sheet
- Call leads sequentially as a sales agent

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Port 7860 in use | Run `uv run bot.py --port 8080` and open that port |
| No microphone | Check browser permissions (click lock icon in address bar) |
| API errors | Verify keys in `server/.env` |
| Windows install fails on `daily-python` | This project uses WebRTC only (no Daily dependency) |

## Learn More

- [Pipecat Documentation](https://docs.pipecat.ai/)
- [Pipecat Your First Agent](https://docs.pipecat.ai/pipecat/learn/your-first-agent)
