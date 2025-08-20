"""
Casa Limpia - Asistente de Comunicación IA
Interfaz minimalista enfocada en UX
"""

import os
import streamlit as st
from core import MinimalChatBot

# Configuración de página
st.set_page_config(
    page_title="Casa Limpia IA",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS minimalista y moderno
st.markdown("""
<style>
/* Reset y base */
.main { padding-top: 1rem; }
.block-container { padding-top: 1rem; max-width: 900px; }

/* Header minimalista */
.header {
    text-align: center;
    margin-bottom: 2rem;
    padding: 1.5rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 16px;
    color: white;
    box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
}

.header h1 {
    margin: 0;
    font-size: 2rem;
    font-weight: 600;
}

.header p {
    margin: 0.5rem 0 0 0;
    opacity: 0.9;
    font-size: 1rem;
}

/* Modo switcher */
.mode-switch {
    background: white;
    border-radius: 12px;
    padding: 0.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* Input areas */
.stTextArea textarea {
    border-radius: 12px;
    border: 2px solid #e1e5e9;
    font-size: 16px;
    transition: all 0.3s ease;
}

.stTextArea textarea:focus {
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* Botones principales */
.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    border-radius: 12px;
    color: white;
    font-weight: 600;
    height: 3rem;
    font-size: 1rem;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

/* Resultado */
.result-card {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    margin: 1.5rem 0;
    border: 1px solid #e1e5e9;
    box-shadow: 0 4px 16px rgba(0,0,0,0.1);
}

/* Feedback simple */
.feedback-card {
    background: #f8f9fa;
    border-radius: 12px;
    padding: 1.5rem;
    margin-top: 1rem;
    border-left: 4px solid #667eea;
}

/* Opciones múltiples */
.option-card {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
    border: 2px solid #e1e5e9;
    transition: all 0.3s ease;
}

.option-card:hover {
    border-color: #667eea;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.option-header {
    background: linear-gradient(90deg, #667eea, #764ba2);
    color: white;
    padding: 0.75rem 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
    font-weight: 600;
}

/* Ratings */
.stSelectSlider > div > div > div {
    background: #667eea !important;
}

/* Alertas */
.stAlert {
    border-radius: 12px;
    border: none;
}

/* Ocultar elementos innecesarios */
.viewerBadge_container__1QSob { display: none; }
#MainMenu { display: none; }
footer { display: none; }
header { display: none; }
</style>
""", unsafe_allow_html=True)

def render_header():
    """Header minimalista"""
    st.markdown("""
    <div class="header">
        <h1>✨ Casa Limpia IA</h1>
        <p>Comunicación inteligente y profesional</p>
    </div>
    """, unsafe_allow_html=True)

def render_simple_feedback(chatbot, original_text, generated_text, task_type):
    """Sistema de feedback simplificado que funciona"""
    st.markdown("---")
    
    # Crear un ID único basado en el contenido
    content_id = str(abs(hash(generated_text + original_text)))
    
    # Inicializar estado si no existe
    rating_key = f"rating_{content_id}"
    comment_key = f"comment_{content_id}"
    
    if rating_key not in st.session_state:
        st.session_state[rating_key] = 3
    if comment_key not in st.session_state:
        st.session_state[comment_key] = ""
    
    st.markdown("### 💬 ¿Qué te parece?")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        rating = st.select_slider(
            "Calificación",
            options=[1, 2, 3, 4, 5],
            value=st.session_state[rating_key],
            format_func=lambda x: "⭐" * x,
            key=rating_key
        )
    
    with col2:
        comment = st.text_input(
            "Comentario (opcional)",
            value=st.session_state[comment_key],
            placeholder="¿Qué mejorarías?",
            key=comment_key
        )
    
    if st.button("📤 Enviar feedback", key=f"submit_{content_id}", type="secondary"):
        # Guardar feedback
        chatbot.add_feedback(
            original=original_text,
            generated=generated_text,
            task_type=task_type,
            rating=rating,
            comments=comment
        )
        
        # Limpiar estado
        st.session_state[rating_key] = 3
        st.session_state[comment_key] = ""
        
        st.success("✅ ¡Gracias! Tu feedback ayuda a mejorar el sistema")
        st.balloons()
        st.rerun()

def main():
    # Inicializar chatbot
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = MinimalChatBot()
    
    chatbot = st.session_state.chatbot
    
    # Header
    render_header()
    
    # Modo de trabajo
    mode = st.radio(
        "Selecciona el modo",
        ["🚀 Generar texto", "✏️ Corregir texto"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    # Configuración de IA (expandible)
    with st.expander("⚙️ Configuración de IA", expanded=False):
        ai_providers = chatbot.ai_provider.get_providers_for_ui()
        available_providers = [name for name, status in ai_providers.items() if status["available"]]
        
        if available_providers:
            selected_provider = st.selectbox(
                "Modelo de IA:",
                available_providers,
                format_func=lambda x: f"🤖 {x.title()} - {ai_providers[x]['model']}"
            )
            
            # Mostrar estado
            status = ai_providers[selected_provider]
            st.info(f"✅ **{selected_provider.title()}** está disponible\n📊 Modelo: `{status['model']}`")
            
            # Actualizar provider seleccionado
            if 'selected_ai_provider' not in st.session_state:
                st.session_state.selected_ai_provider = selected_provider
            else:
                st.session_state.selected_ai_provider = selected_provider
        else:
            st.warning("⚠️ No hay modelos de IA disponibles. Configura una API key.")
    
    # Input principal
    if "Generar" in mode:
        user_input = st.text_area(
            "💭 ¿Qué tipo de comunicación necesitas?",
            placeholder="Ej: Día de la mujer, felicitación por logros, bienvenida nuevos colaboradores...",
            height=100,
            max_chars=1000
        )
        task_type = "generate"
        button_text = "🚀 Generar"
        button_help = "Crear comunicación profesional"
    else:
        user_input = st.text_area(
            "📝 Texto a corregir:",
            placeholder="Pega aquí el texto que quieres mejorar...",
            height=120,
            max_chars=2000
        )
        task_type = "correct"
        button_text = "✏️ Corregir"
        button_help = "Mejorar gramática y estilo"
    
    # Mostrar contador de caracteres
    if user_input:
        st.caption(f"{len(user_input)} caracteres")
    
    # Opciones y botón principal
    if user_input and len(user_input.strip()) > 10:
        
        # Opciones para generación
        if task_type == "generate":
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                generate_btn = st.button(button_text, help=button_help, use_container_width=True, type="primary")
            with col2:
                multiple = st.checkbox("Múltiples opciones", help="Generar 3 versiones diferentes")
            with col3:
                if hasattr(st.session_state, 'selected_ai_provider'):
                    provider = st.session_state.selected_ai_provider
                    st.caption(f"🤖 {provider.title()}")
        else:
            col1, col2 = st.columns([3, 1])
            with col1:
                generate_btn = st.button(button_text, help=button_help, use_container_width=True, type="primary")
            with col2:
                if hasattr(st.session_state, 'selected_ai_provider'):
                    provider = st.session_state.selected_ai_provider
                    st.caption(f"🤖 {provider.title()}")
            multiple = False
        
        # Procesar
        if generate_btn:
            # Usar el provider seleccionado si está disponible
            selected_provider = getattr(st.session_state, 'selected_ai_provider', None)
            
            with st.spinner("🤖 Trabajando..."):
                if task_type == "generate" and multiple:
                    # Múltiples opciones
                    options = chatbot.generate_multiple_options(user_input, 3, preferred_provider=selected_provider)
                    
                    if options and any(not opt["text"].startswith("❌") for opt in options):
                        st.markdown("### 📋 Opciones generadas")
                        
                        # Mostrar opciones mejoradas
                        for i, option in enumerate(options):
                            if not option["text"].startswith("❌"):
                                # Card más limpia
                                st.markdown(f"""
                                <div class="option-card">
                                    <div class="option-header">
                                        🎯 Opción {i+1} 
                                        <span style="float: right; font-size: 0.8em; opacity: 0.8;">
                                            🌡️ Temp: {option.get('temperature', 'N/A')}
                                        </span>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Mostrar el texto generado
                                st.markdown(f"**Resultado:**")
                                st.write(option["text"])
                                
                                # Feedback inline y simple
                                opt_id = f"opt_{i}_{abs(hash(option['text']))}"
                                
                                col1, col2, col3 = st.columns([1, 2, 1])
                                with col1:
                                    rating = st.select_slider(
                                        f"Rating",
                                        options=[1, 2, 3, 4, 5],
                                        value=3,
                                        format_func=lambda x: "⭐" * x,
                                        key=f"rating_{opt_id}",
                                        label_visibility="collapsed"
                                    )
                                with col2:
                                    comment = st.text_input(
                                        f"Comentario",
                                        placeholder="¿Qué opinas de esta opción?",
                                        key=f"comment_{opt_id}",
                                        label_visibility="collapsed"
                                    )
                                with col3:
                                    if st.button("💬 Feedback", key=f"submit_{opt_id}", help="Enviar feedback"):
                                        chatbot.add_feedback(
                                            original=user_input,
                                            generated=option["text"],
                                            task_type=task_type,
                                            rating=rating,
                                            comments=comment,
                                            option_id=f"option_{i+1}"
                                        )
                                        st.success("✅ ¡Feedback enviado!")
                                        st.rerun()
                                
                                st.divider()
                    else:
                        st.error("❌ No se pudieron generar las opciones. Verifica la configuración de IA.")
                
                else:
                    # Una sola opción
                    if task_type == "generate":
                        result = chatbot.generate_text(user_input)
                    else:
                        result = chatbot.correct_text(user_input)
                    
                    if not result.startswith("❌"):
                        # Mostrar resultado
                        st.markdown(f"""
                        <div class="result-card">
                            <h3>📄 {'Texto generado' if task_type == 'generate' else 'Texto corregido'}</h3>
                            {result}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Feedback simple
                        render_simple_feedback(chatbot, user_input, result, task_type)
                    else:
                        st.error(result)
    
    # Footer minimalista
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col2:
        st.caption("🏢 Casa Limpia Colombia - IA Comunicación")

if __name__ == "__main__":
    main()