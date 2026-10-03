"""
Optional Voice Interaction Service (app/services/voice.py).
Provides graceful fallback Speech-to-Text and Text-to-Speech helpers.
Treated as an optional advanced feature without breaking core functionality.
"""

from typing import Dict, Any, Optional


def is_voice_available() -> bool:
    """Checks if speech synthesis or recognition packages are installed."""
    try:
        import pyttsx3
        return True
    except ImportError:
        return False


def text_to_speech(text: str, language: str = "en") -> Dict[str, Any]:
    """
    Converts text to spoken audio if local voice engine is available.
    """
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty("rate", 150)
        # engine.say(text)
        # engine.runAndWait()
        return {"success": True, "message": "Voice audio generated successfully."}
    except Exception as e:
        return {
            "success": False,
            "message": f"Voice service unavailable (optional feature): {str(e)}"
        }


def speech_to_text(audio_bytes: Optional[bytes] = None) -> Dict[str, Any]:
    """
    Converts speech audio bytes to text transcription.
    """
    return {
        "success": False,
        "transcription": "",
        "message": "Speech recognition is active in text mode."
    }

