"""
FastAPI app for DevDuck: VAPI webhook and basic endpoints
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json

logger = logging.getLogger(__name__)

app = FastAPI(title="DevDuck API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

is_listening = False
conversation_history: List[Dict[str, Any]] = []
context_store = {}


# Pydantic models for VAPI webhook requests
class VAPIWebhookRequest(BaseModel):
    message: Dict[str, Any]
    call: Optional[Dict[str, Any]] = None
    
class FunctionCallRequest(BaseModel):
    name: str
    parameters: Dict[str, Any]


def handle_analyze_code(params: Dict[str, Any]) -> Dict[str, Any]:
    file_path = params.get('file_path', '')
    code_content = params.get('code_content', '')
    
    if not file_path and not code_content:
        return {
            "result": "No code provided for analysis",
            "success": False
        }
    
    analysis = {
        "complexity": "medium",
        "issues": [],
        "suggestions": ["Consider adding comments", "Review variable naming"],
        "file_analyzed": file_path if file_path else "code_snippet"
    }
    
    if code_content:
        line_count = len(code_content.split('\n'))
        analysis["line_count"] = line_count
        if line_count > 50:
            analysis["complexity"] = "high"
            analysis["suggestions"].append("Consider breaking into smaller functions")
    
    return {
        "result": f"Code analysis complete for {analysis['file_analyzed']}",
        "analysis": analysis,
        "success": True
    }


def handle_suggest_break(params: Dict[str, Any]) -> Dict[str, Any]:
    stress_level = params.get('stress_level', 'medium')
    work_duration = params.get('work_duration', 60)
    
    suggestions = {
        "low": "You're doing great! Consider a 5-minute stretch break.",
        "medium": "Take a 10-15 minute break. Get some water and step away from the screen.",
        "high": "You need a proper break! Take 20-30 minutes, go for a walk, or do something relaxing."
    }
    
    suggestion = suggestions.get(stress_level, suggestions["medium"])
    
    if work_duration > 120:  # 2 hours
        suggestion += " You've been working for over 2 hours - definitely time for a break!"
    
    return {
        "result": suggestion,
        "stress_level": stress_level,
        "work_duration": work_duration,
        "success": True
    }


def handle_analyze_sentiment(params: Dict[str, Any]) -> Dict[str, Any]:
    from devduck.analysis import analyze_developer_mood
    
    text = params.get('text', '')
    context = params.get('context', '')
    
    if not text:
        return {
            "result": "No text provided for sentiment analysis",
            "success": False
        }
    
    sentiment_result = analyze_developer_mood(text)
    
    return {
        "result": f"Sentiment analysis complete: {sentiment_result['sentiment']} ({sentiment_result['confidence']:.2f} confidence)",
        "sentiment": sentiment_result,
        "context": context,
        "success": True
    }


def handle_get_project_status(_params: Dict[str, Any]) -> Dict[str, Any]:
    status = {
        "overall_health": "good",
        "active_issues": 0,
        "last_analysis": datetime.now(timezone.utc).isoformat(),
        "listening_status": is_listening,
        "conversation_count": len(conversation_history)
    }
    
    return {
        "result": "Project status retrieved successfully",
        "status": status,
        "success": True
    }


def handle_provide_encouragement(params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle encouragement requests"""
    mood = params.get('mood', 'neutral')
    context = params.get('context', '')
    
    encouragement_messages = {
        "frustrated": [
            "Take a deep breath! Every developer faces challenges - you've got this!",
            "Frustration is part of the learning process. Step back, take a break, and come back fresh.",
            "Remember: every bug you fix makes you a better developer!"
        ],
        "confused": [
            "Confusion is the beginning of understanding. Break the problem down into smaller pieces.",
            "It's okay to feel lost sometimes. Try explaining the problem out loud - it often helps!",
            "Don't be afraid to look things up or ask for help. Even senior developers do it!"
        ],
        "stressed": [
            "Stress is a sign you care about your work, but don't let it overwhelm you.",
            "Take a moment to prioritize. What's the one most important thing to focus on right now?",
            "Remember to breathe and take breaks. Your best work comes when you're relaxed."
        ],
        "neutral": [
            "Keep up the great work! You're making progress.",
            "Stay curious and keep learning. You're on the right track!",
            "Every line of code you write is a step forward in your journey."
        ]
    }
    
    messages = encouragement_messages.get(mood, encouragement_messages["neutral"])
    message = messages[0]  #  we could randomize this
    
    if context:
        message += f" Remember, you're working on {context} - that's valuable work!"
    
    return {
        "result": message,
        "mood": mood,
        "context": context,
        "success": True
    }


@app.post("/listening/toggle")
async def toggle_listening():
    global is_listening
    is_listening = not is_listening
    status = 'listening' if is_listening else 'stopped'
    
    conversation_history.append({
        'time': datetime.now(timezone.utc).isoformat(),
        'event': status,
        'type': 'system'
    })
    
    logger.info("Listening toggled to: %s", status)
    return {'isListening': is_listening, 'status': status}


@app.get("/history")
async def get_history():
    return {
        'history': conversation_history,
        'count': len(conversation_history)
    }


@app.post("/history/clear")
async def clear_history():
    conversation_history.clear()
    logger.info("Conversation history cleared")
    return {'message': 'History cleared', 'count': 0}


@app.get("/status")
async def get_status():
    return {
        'isListening': is_listening,
        'historyCount': len(conversation_history),
        'timestamp': datetime.now(timezone.utc).isoformat()
    }


@app.get("/health")
async def health_check():
    return {'status': 'healthy', 'service': 'DevDuck API'}


@app.get("/")
async def root():
    return {
        'message': 'DevDuck API is running',
        'endpoints': [
            '/listening/toggle',
            '/history',
            '/history/clear',
            '/status',
            '/health',
            '/webhook/vapi'
        ]
    }


@app.post("/webhook/vapi")
async def vapi_webhook(request: Request):
    try:
        body = await request.json()
        logger.info("Received VAPI webhook: %s", json.dumps(body, indent=2))
        
        message = body.get('message', {})
        message_type = message.get('type', '')
        
        if message_type == 'function-call':
            function_call = message.get('functionCall', {})
            function_name = function_call.get('name', '')
            parameters = function_call.get('parameters', {})
            
            handlers = {
                'analyze_code': handle_analyze_code,
                'suggest_break': handle_suggest_break,
                'analyze_sentiment': handle_analyze_sentiment,
                'get_project_status': handle_get_project_status,
                'provide_encouragement': handle_provide_encouragement
            }
            
            if function_name in handlers:
                result = handlers[function_name](parameters)
                
                conversation_history.append({
                    'time': datetime.now(timezone.utc).isoformat(),
                    'type': 'function_call',
                    'function': function_name,
                    'parameters': parameters,
                    'result': result
                })
                
                return {
                    "result": result.get("result", "Function executed successfully"),
                    "success": result.get("success", True),
                    "data": result
                }
            else:
                logger.warning("Unknown function: %s", function_name)
                return {
                    "result": f"Unknown function: {function_name}",
                    "success": False
                }
        
        elif message_type in ['conversation-started', 'conversation-ended', 'speech-started', 'speech-ended']:
            conversation_history.append({
                'time': datetime.now(timezone.utc).isoformat(),
                'type': 'conversation_event',
                'event': message_type,
                'message': message
            })
            
            return {"success": True, "message": f"Event {message_type} logged"}
        
        return {"success": True, "message": "Webhook received"}
        
    except Exception as e:
        logger.error("Error processing VAPI webhook: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Webhook processing error: {str(e)}") from e


@app.post("/get_code_snippet")
def get_code_snippet(request: FunctionCallRequest):
    file_path = request.parameters.get("file_path")
    if not file_path:
        raise HTTPException(status_code=400, detail="File path is required")

    try:
        with open(file_path, "r") as file:
            code_snippet = file.read()
        return {"success": True, "code_snippet": code_snippet}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/store_context")
def store_context(request: FunctionCallRequest):
    snippet_id = request.parameters.get("snippet_id")
    context = request.parameters.get("context")

    if not snippet_id or not context:
        raise HTTPException(status_code=400, detail="Snippet ID and context are required")

    context_store[snippet_id] = context
    return {"success": True, "message": "Context stored successfully"}


@app.post("/retrieve_context")
def retrieve_context(request: FunctionCallRequest):
    snippet_id = request.parameters.get("snippet_id")

    if not snippet_id:
        raise HTTPException(status_code=400, detail="Snippet ID is required")

    context = context_store.get(snippet_id)
    if not context:
        raise HTTPException(status_code=404, detail="Context not found")

    return {"success": True, "context": context}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
