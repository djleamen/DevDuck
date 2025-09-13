# DevDuck 🦆

A simplified USB-connected AI rubber duck that listens to developers and provides helpful responses through voice interaction.

## Features

- **Voice Listening Toggle** - Start/stop listening with a simple button
- **Conversation History** - Track all interactions in a dropdown
-  **Basic Sentiment Analysis** - Understand developer mood from text
- **Web API** - RESTful endpoints for frontend communication
- **Electron Frontend** - Clean, minimal desktop interface

## Quick Start

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the API Server

```bash
python scripts/start_api.py
```

The API will be available at: `http://localhost:8000`

### 3. Start the Frontend

```bash
cd frontend
npm install

npm start
```

## API Endpoints

- `POST /listening/toggle` - Toggle listening state
- `GET /history` - Get conversation history
- `POST /history/clear` - Clear conversation history
- `GET /status` - Get current system status
- `GET /health` - Health check

## Project Structure

```
DevDuck/
├── devduck/                 # Python backend
│   ├── ai/                  # VAPI integration
│   ├── analysis/            # Sentiment analysis
│   ├── api/                 # FastAPI endpoints
│   ├── hardware/            # USB/Arduino communication
│   └── utils/               # Utilities
├── frontend/                # Electron desktop app
│   ├── renderer/            # Frontend UI files
│   ├── main.js              # Electron main process
│   └── package.json         # Frontend dependencies
├── arduino/                 # Arduino servo controller
├── scripts/                 # Startup scripts
└── requirements.txt         # Python dependencies
```

## Hardware Setup

The Arduino controller manages servo movements for the physical duck. See `arduino/devduck_controller/` for the servo control code.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Authors

- DJ Leamen
- Nahl Farhan
