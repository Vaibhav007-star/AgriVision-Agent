"""
Services Subpackage for AgriVision Agent (app/services)
"""
from app.services.weather import get_field_weather
from app.services.translation import translate_text, generate_bilingual_prescription
from app.services.voice import is_voice_available, text_to_speech, speech_to_text

