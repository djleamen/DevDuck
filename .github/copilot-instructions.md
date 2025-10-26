# DevDuck - Copilot Instructions

## Project Overview

DevDuck is a sentiment-aware debugging assistant that combines AI, hardware, and voice interaction to create an intelligent rubber duck debugging companion. The system consists of three main components:

1. **Python Backend** (FastAPI) - API server, VAPI webhook integration, sentiment analysis
2. **Electron Frontend** - Desktop application for user interaction
3. **Arduino Hardware** - Servo controller for physical duck movements

## Architecture

```
DevDuck/
├── devduck/              # Python backend (FastAPI)
│   ├── api/              # API endpoints and VAPI webhook
│   ├── ai/               # VAPI client integration
│   ├── analysis/         # Sentiment analysis
│   ├── hardware/         # USB communication with Arduino
│   └── utils/            # Utilities and security
├── frontend/             # Electron desktop app
│   ├── main.js           # Electron main process
│   └── renderer/         # UI components
├── arduino/              # Arduino servo controller
└── scripts/              # Utility scripts
```

## Technology Stack

- **Backend**: Python 3.x, FastAPI, uvicorn, pydantic
- **Frontend**: Electron, JavaScript, VAPI Web SDK
- **Hardware**: Arduino, pyserial
- **AI/ML**: VAPI API, SpeechRecognition
- **Testing**: pytest
- **Code Quality**: black (formatter), flake8 (linter)

## Development Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- Arduino IDE (for hardware development)
- ngrok (for VAPI webhook tunneling)

### Quick Start
1. Install Python dependencies: `pip install -r requirements.txt`
2. Start API server: `python scripts/start_api.py` (runs on port 8001)
3. Install frontend deps: `cd frontend && npm install`
4. Start frontend: `npm start`
5. Setup ngrok: `ngrok http 8001` (update VAPI variables in renderer.js)

## Code Style and Standards

### Python
- **Formatter**: Use `black` for code formatting (configured in requirements.txt)
- **Linter**: Use `flake8` for style checking
- **Docstrings**: Use triple-quoted strings for module and function documentation
- **Type Hints**: Use type hints where appropriate (already used in codebase)
- **Imports**: Standard library first, then third-party, then local imports
- **Logging**: Use the `logging` module (already configured), not print statements for debugging

### JavaScript/Frontend
- **Style**: Follow existing camelCase conventions
- **Async**: Use async/await for asynchronous operations
- **Error Handling**: Always include try-catch blocks for API calls
- **Comments**: Add comments for complex logic or VAPI integration points

### File Organization
- Keep related functionality together in modules
- Use `__init__.py` for package exports
- Place utility functions in appropriate util modules

## Key Components and Their Purposes

### Backend Files
- `devduck/api/vapi_webhook.py` - Main FastAPI application, all API endpoints
- `devduck/api/assistant_config.py` - VAPI assistant configuration
- `devduck/ai/__init__.py` - VAPI client implementation
- `devduck/analysis/__init__.py` - Sentiment analysis logic
- `devduck/hardware/usb_communication.py` - Arduino serial communication
- `devduck/main.py` - Main application coordinator
- `scripts/start_api.py` - API server startup script

### Frontend Files
- `frontend/main.js` - Electron main process, window management
- `frontend/renderer/renderer.js` - UI logic, VAPI integration
- `frontend/renderer/index.html` - Main UI structure
- `frontend/renderer/styles.css` - Application styling

### Hardware
- `arduino/devduck_controller/devduck_controller.ino` - Servo control code

## API Endpoints

When adding or modifying endpoints, follow the existing pattern in `vapi_webhook.py`:

- `GET /` - Root, lists available endpoints
- `POST /listening/toggle` - Toggle listening state
- `GET /history` - Get conversation history
- `POST /history/clear` - Clear conversation history
- `GET /status` - Get current system status
- `GET /health` - Health check
- `POST /webhook/vapi` - VAPI webhook endpoint
- `POST /duck/talk/start` - Start duck talking animation
- `POST /duck/talk/stop` - Stop duck talking animation
- `POST /duck/gesture/{name}` - Trigger gestures (nod, shake, left, right, greet, goodluck)
- `POST /get_code_snippet` - Read and return file contents
- `POST /store_context` - Store a snippet/context payload
- `POST /retrieve_context` - Retrieve stored context by snippet id

## Testing

- **Framework**: pytest (included in requirements.txt)
- **Location**: Tests are not currently implemented in the repository
- **When Adding Tests**: Place test files adjacent to the code they test or in a `tests/` directory
- **Naming**: Use `test_*.py` or `*_test.py` naming convention
- **Coverage**: Focus on API endpoints, sentiment analysis, and critical business logic

## Common Development Tasks

### Running the API Server
```bash
python scripts/start_api.py
# Server runs on http://localhost:8001
# Reload enabled for development
```

### Code Formatting and Linting
```bash
# Format Python code
black devduck/

# Check style
flake8 devduck/
```

### Testing Hardware Integration
- Requires Arduino connected via USB
- Check `devduck/hardware/usb_communication.py` for communication protocol
- Use `is_available()` to check hardware connection status

### VAPI Integration
- Requires valid VAPI API keys in `.env` file (see `.env.example`)
- VAPI webhook endpoint: `/webhook/vapi`
- Frontend uses `@vapi-ai/web` SDK
- Update VAPI variables in `frontend/renderer/renderer.js` after setting up ngrok

## Environment Variables

Create a `.env` file based on `.env.example`:
```
VAPI_API_KEY=your_api_key_here
VAPI_PUBLIC_KEY=your_public_key_here
VAPI_ASSISTANT_ID=your_assistant_id_here
VAPI_WEBHOOK_URL=https://your-ngrok-url.com/webhook/vapi
```

## Important Patterns and Conventions

### State Management
- Global state variables in `vapi_webhook.py`: `is_listening`, `conversation_history`, `context_store`
- Thread-safe operations for duck animation (`_talk_stop_event`, `_talk_thread`)

### Error Handling
- Use FastAPI's `HTTPException` for API errors
- Log errors using the `logger` module
- Return appropriate HTTP status codes (400 for client errors, 500 for server errors)

### Duck Animations
- Animations run in separate threads to avoid blocking
- Use `threading.Event` for clean shutdown
- Small delays (0.05-2.0s) to create smooth, non-jittery movements

### CORS Configuration
- Configured to allow all origins (`["*"]`) for development
- Update for production deployment

## Security Considerations

- **Secrets**: Never commit API keys or secrets to the repository
- **Webhook Validation**: VAPI webhooks should be validated (check `utils/security.py`)
- **Input Validation**: Use pydantic models for request validation
- **CORS**: Restrict origins in production environments

## Contribution Guidelines

When making changes:
1. Follow existing code style and patterns
2. Add logging for important operations
3. Update docstrings for new functions
4. Test API endpoints manually before committing
5. Ensure hardware operations are non-blocking
6. Update this file if adding new conventions or major features

## Debugging Tips

- **API Issues**: Check uvicorn logs for detailed error messages
- **Hardware Issues**: Use `is_available()` and check serial port permissions
- **VAPI Issues**: Verify webhook URL is accessible via ngrok and check `.env` configuration
- **Frontend Issues**: Use Electron DevTools (Ctrl+Shift+I / Cmd+Option+I)
- **Sentiment Analysis**: Check logs for sentiment results and movement triggers

## Resources

- FastAPI Documentation: https://fastapi.tiangolo.com/
- Electron Documentation: https://www.electronjs.org/docs/latest/
- VAPI Documentation: https://docs.vapi.ai/
- Arduino Reference: https://www.arduino.cc/reference/en/
