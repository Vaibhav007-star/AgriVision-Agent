"""
Header component for AgriVision Agent Streamlit UI.
"""

import streamlit as st


def render_header(title: str = "🌾 AgriVision Agent", subtitle: str = "Agentic AI-Based Crop Disease Detection, Diagnosis & Advisory System"):
    """Renders the top hero/header banner."""
    st.markdown(
        f"""
        <div class="hero-card">
            <h1 class="hero-title">{title}</h1>
            <p class="hero-subtitle">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

