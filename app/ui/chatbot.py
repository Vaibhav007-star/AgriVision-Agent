"""
Farmer Advisory Chatbot UI View (app/ui/chatbot.py).
"""

import streamlit as st
from app.database.crud import save_chat_turn, get_chat_turns
from src.rag.knowledge_base import query_rag


def render_chatbot():
    """Renders the interactive bilingual advisory chatbot with live RAG retrieval & persistence."""
    st.markdown("## 💬 Farmer Advisory Chatbot / किसान सहायक")
    st.caption("Ask questions about treatments, dosage, organic alternatives, or crop management in English or Hindi.")
    
    session_id = "default_farmer_session"
    
    # Initialize chat from database if empty
    if "chat_messages" not in st.session_state:
        db_history = get_chat_turns(session_id)
        if db_history:
            st.session_state["chat_messages"] = [{"role": row["role"], "content": row["content"]} for row in db_history]
        else:
            st.session_state["chat_messages"] = [
                {"role": "assistant", "content": "नमस्ते! मैं आपका AgriVision कृषि सहायक हूँ। अपनी फसल, बीमारी या उपचार के बारे में कोई भी प्रश्न पूछें।\n\nHello! I am your AgriVision Assistant. Feel free to ask any question regarding crop diseases, treatments, or preventive care."}
            ]
            
    # Quick prompt suggestion chips
    st.markdown("**⚡ Quick Inquiries / त्वरित प्रश्न:**")
    qc1, qc2, qc3 = st.columns(3)
    quick_query = None
    if qc1.button("🍅 टमाटर के अगेती झुलसा का उपचार?"):
        quick_query = "टमाटर के अगेती झुलसा का उपचार कैसे करें?"
    if qc2.button("🥔 Potato Late Blight Fungicide"):
        quick_query = "What fungicide to use for Potato Late Blight?"
    if qc3.button("🌿 Organic Neem Oil Formulation"):
        quick_query = "How to mix and spray organic Neem oil for crop disease?"
        
    for msg in st.session_state["chat_messages"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
    prompt = st.chat_input("Type your question here (e.g. 'टमाटर के झुलसा रोग की रोकथाम कैसे करें?' or 'What fungicide dosage to use?')")
    active_prompt = prompt or quick_query
    
    if active_prompt:
        st.session_state["chat_messages"].append({"role": "user", "content": active_prompt})
        save_chat_turn(session_id, "user", active_prompt, language=st.session_state.get("language", "en"))
        with st.chat_message("user"):
            st.write(active_prompt)
            
        with st.chat_message("assistant"):
            with st.spinner("Searching Agricultural Vector Knowledge Base..."):
                rag_result = query_rag(active_prompt, top_k=2)
                docs = rag_result.get("documents", [])
                
                is_hindi = any('\u0900' <= char <= '\u097F' for char in active_prompt)
                
                if docs:
                    best_doc = docs[0]
                    context_snippet = best_doc["text"]
                    if is_hindi:
                        response_text = f"**🌾 AgriVision किसान परामर्श:**\n\n{context_snippet}\n\n*(स्रोत: `{best_doc['source']}`)*"
                    else:
                        response_text = f"**🌾 AgriVision Agronomic Advisory:**\n\n{context_snippet}\n\n*(Grounded Knowledge Source: `{best_doc['source']}`, Relevance: {best_doc.get('score', 0.85):.2f})*"
                else:
                    response_text = "Please ensure adequate plant spacing, avoid leaf wetness, and consult local extension officers for severe outbreaks."
                    
                st.write(response_text)
                st.session_state["chat_messages"].append({"role": "assistant", "content": response_text})
                save_chat_turn(session_id, "assistant", response_text, language=st.session_state.get("language", "en"))

