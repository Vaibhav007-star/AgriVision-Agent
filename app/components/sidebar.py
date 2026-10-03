"""
Sidebar component for AgriVision Agent Streamlit UI.
Handles navigation, system status monitoring, and language selection.
"""

import streamlit as st
import os
from src.config import config


def render_sidebar():
    """Renders the navigation sidebar with configuration indicators."""
    with st.sidebar:
        st.markdown("## 🌿 AgriVision System")
        st.markdown("*Autonomous Agricultural Diagnosis*")
        st.divider()
        
        # Navigation
        menu_options = [
            "🏠 Home",
            "🔍 Disease Detection",
            "🤖 AI Agent Diagnosis",
            "💬 Farmer Advisory Chat",
            "🌦️ Weather & Field Context",
            "📊 Crop Health Dashboard",
            "📜 Scan History",
            "⚙️ System Settings"
        ]
        
        selected_page = st.radio("Navigation", menu_options, index=0, label_visibility="collapsed")
        st.divider()
        
        # Language Selector
        st.markdown("### 🌐 Language / भाषा")
        language = st.selectbox(
            "Select Interface Language",
            options=["English", "हिंदी (Hindi)"],
            index=0 if config.app.DEFAULT_LANGUAGE == "en" else 1,
            label_visibility="collapsed"
        )
        st.session_state["language"] = "hi" if "Hindi" in language else "en"
        
        st.divider()
        
        # System Health Indicators
        st.markdown("### ⚡ System Status")
        
        # DL Model status
        model_exists = config.model.MODEL_PATH.exists()
        st.markdown(
            f"🧠 **Vision Model:** {'🟢 Ready' if model_exists else '🟡 Mock/Setup Mode'}"
        )
        
        # LLM status
        has_groq = bool(config.llm.GROQ_API_KEY)
        has_gemini = bool(config.llm.GEMINI_API_KEY)
        llm_status = "🟢 Configured" if (has_groq or has_gemini) else "🟡 Local / Rule Engine"
        st.markdown(f"🤖 **Agent LLM:** {llm_status} (`{config.llm.PROVIDER}`)")
        
        # Database status
        st.markdown("🗄️ **Local SQLite DB:** 🟢 Connected")
        
        st.divider()
        st.caption("AgriVision Agent v1.0 • Academic DL Project")
        
        return selected_page

