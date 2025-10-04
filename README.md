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

The API will be available at: `http://localhost:8001`

### 3. Start the Frontend

```bash
cd frontend
npm install

npm start
```

### 4. Start the API gateway

```bash
ngrok http 8001
```

Don't forget to update VAPI variables in `renderer.js`!

## API Endpoints

- `GET /` - Root; lists available endpoints
- `POST /listening/toggle` - Toggle listening state
- `GET /history` - Get conversation history
- `POST /history/clear` - Clear conversation history
- `GET /status` - Get current system status
- `GET /health` - Health check
- `POST /webhook/vapi` - VAPI webhook endpoint
- `POST /duck/talk/start` - Start duck talking animation
- `POST /duck/talk/stop` - Stop duck talking animation
- `POST /duck/gesture/{name}` - Trigger a gesture (`nod`, `shake`, `left`, `right`, `greet`, `goodluck`)
- `POST /get_code_snippet` - Read and return file contents
- `POST /store_context` - Store a snippet/context payload
- `POST /retrieve_context` - Retrieve a stored context by snippet id

## Project Structure

```
DevDuck/
├── arduino/                 # Arduino servo controller
│   └── devduck_controller/
│       └── devduck_controller.ino
├── devduck/                 # Python backend
│   ├── __init__.py
│   ├── main.py
│   ├── ai/
│   │   └── __init__.py      # VAPI integration hooks
│   ├── analysis/
│   │   └── __init__.py      # Sentiment analysis
│   ├── api/
│   │   ├── __init__.py
│   │   ├── assistant_config.py
│   │   └── vapi_webhook.py  # FastAPI app & endpoints
│   ├── hardware/
│   │   ├── __init__.py
│   │   └── usb_communication.py
│   └── utils/
│       ├── __init__.py
│       └── security.py
├── frontend/                # Electron desktop app
│   ├── main.js              # Electron main process
│   ├── package.json         # Frontend dependencies
│   ├── package-lock.json
│   └── renderer/            # Frontend UI files
│       ├── index.html
│       ├── renderer.js
│       └── styles.css
├── scripts/
│   └── start_api.py         # Starts FastAPI on port 8001
```

## Hardware Setup

The Arduino controller manages servo movements for the physical duck. See `arduino/devduck_controller/` for the servo control code.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Authors

- DJ Leamen
- Nahl Farhan
