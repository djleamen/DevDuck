"""
VAPI Assistant Configuration for DevDuck

This module contains the assistant configuration that can be used 
to create or update the VAPI assistant.
"""

DEVDUCK_ASSISTANT_CONFIG = {
    "name": "DevDuck",
    "model": {
        "provider": "openai",
        "model": "gpt-3.5-turbo",
        "systemMessage": """You are DevDuck, a helpful AI rubber duck debugging assistant. 

Your role is to:
- Help developers with code review and debugging
- Provide emotional support during development challenges  
- Offer encouragement and practical advice
- Analyze code for potential issues
- Suggest breaks when developers seem stressed

Keep your responses:
- Concise and clear (under 100 words when possible)
- Encouraging and supportive
- Practical and actionable
- Focused on the developer's immediate needs

You have access to several functions:
- analyze_code: Review code for issues and suggestions
- analyze_sentiment: Understand the developer's emotional state
- suggest_break: Recommend break times based on work duration
- get_project_status: Check the current project health
- provide_encouragement: Give motivational support

Always prioritize the developer's well-being alongside their technical needs.""",
        "temperature": 0.7,
        "maxTokens": 150
    },
    "voice": {
        "provider": "playht",
        "voiceId": "jennifer"
    },
    "firstMessage": "Hi! I'm DevDuck, your AI debugging buddy. I'm here to help you with code, provide encouragement, and make sure you're taking care of yourself while coding. What are you working on today?",
    "serverUrl": "https://4e3e6f218d9f.ngrok-free.app/webhook/vapi",
    "functions": [
        {
            "name": "analyze_code",
            "description": "Analyze code for potential issues, complexity, and improvement suggestions",
            "parameters": {
                "type": "object",
                "properties": {
                    "code_content": {
                        "type": "string",
                        "description": "The code content to analyze"
                    },
                    "file_path": {
                        "type": "string", 
                        "description": "Optional file path for context"
                    }
                },
                "required": ["code_content"]
            }
        },
        {
            "name": "analyze_sentiment",
            "description": "Analyze the developer's emotional state from their words",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to analyze for sentiment"
                    },
                    "context": {
                        "type": "string",
                        "description": "Additional context about the situation"
                    }
                },
                "required": ["text"]
            }
        },
        {
            "name": "suggest_break",
            "description": "Suggest break times based on work duration and stress level",
            "parameters": {
                "type": "object", 
                "properties": {
                    "work_duration": {
                        "type": "number",
                        "description": "How long the developer has been working (in minutes)"
                    },
                    "stress_level": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Current stress level"
                    }
                },
                "required": ["work_duration", "stress_level"]
            }
        },
        {
            "name": "get_project_status", 
            "description": "Get the current project health and status",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "provide_encouragement",
            "description": "Provide motivational support based on current mood",
            "parameters": {
                "type": "object",
                "properties": {
                    "mood": {
                        "type": "string",
                        "enum": ["frustrated", "confused", "stressed", "neutral"],
                        "description": "Current emotional state"
                    },
                    "context": {
                        "type": "string",
                        "description": "What the developer is working on"
                    }
                },
                "required": ["mood"]
            }
        }
    ]
}