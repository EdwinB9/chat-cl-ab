"""
Módulo ui_components: Componentes de interfaz gráfica
Contiene todos los elementos de UI de Streamlit separados de la lógica de negocio
"""

import time
from typing import Dict, List, Any

# Importación opcional de streamlit
try:
    import streamlit as st
except ImportError:
    st = None

def setup_page_config():
    """Configurar la página de Streamlit"""
    st.set_page_config(
        page_title="Casa Limpia - Asistente de Comunicación IA",
        page_icon="✨",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

def render_custom_css():
    """Renderizar CSS personalizado para toda la aplicación"""
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 50%, #60A5FA 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(30, 58, 138, 0.3);
    }
    .main-title {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .main-subtitle {
        color: #E5E7EB;
        font-size: 1.2rem;
        margin-bottom: 0;
        font-weight: 300;
    }
    .control-panel {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #E5E7EB;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .result-container {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid #E5E7EB;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
    }
    .option-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e1e5e9;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .option-header {
        background: linear-gradient(90deg, #1f4e79, #2d5aa0);
        color: white;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    .feedback-section {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f4e79;
        margin-top: 1rem;
    }
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 500;
        margin-right: 0.5rem;
    }
    .status-success {
        background-color: #D1FAE5;
        color: #065F46;
    }
    .status-warning {
        background-color: #FEF3C7;
        color: #92400E;
    }
    .status-error {
        background-color: #FEE2E2;
        color: #991B1B;
    }
    </style>
    """, unsafe_allow_html=True)

def render_header():
    """Renderizar el header principal"""
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">✨ Casa Limpia Colombia</h1>
        <p class="main-subtitle">Asistente de Comunicación Inteligente</p>
    </div>
    """, unsafe_allow_html=True)

def render_ai_status(chatbot) -> Dict[str, Any]:
    """Renderizar el estado de los proveedores de IA"""
    ai_status = chatbot.ai_provider.get_status()
    
    with st.expander("⚡ Estado de Proveedores de IA", expanded=False):
        if ai_status["configured_count"] > 0:
            st.success(f"✅ {ai_status['configured_count']} proveedor(es) configurado(s)")
        else:
            st.warning("⚠️ No hay proveedores de IA configurados")
        
        cols = st.columns(3)
        for i, provider in enumerate(ai_status["providers"]):
            with cols[i % 3]:
                status_class = "status-success" if provider["status"] == "✅" else \
                              "status-warning" if provider["status"] == "⚠️" else "status-error"
                
                st.markdown(f"""
                <div class="status-badge {status_class}">
                    {provider["status"]} {provider["name"].title()}
                </div>
                """, unsafe_allow_html=True)
    
    return ai_status

def render_task_selector() -> str:
    """Renderizar selector de tipo de tarea"""
    task_type = st.radio(
        "¿Qué quieres hacer?",
        ["🚀 Generar Texto", "✏️ Corregir Texto"],
        horizontal=True,
        key="task_type",
        help="Elige si quieres generar contenido nuevo o corregir texto existente"
    )
    
    return "generate" if "Generar" in task_type else "correct"

def render_text_input(task_type: str) -> str:
    """Renderizar área de entrada de texto"""
    if task_type == "generate":
        placeholder = "Describe el tipo de comunicación que necesitas (ej: Día de la mujer, Felicitación por logros, Bienvenida nuevos colaboradores...)"
        label = "💭 ¿Qué tipo de texto necesitas?"
        help_text = "Describe la ocasión, evento o mensaje que quieres comunicar"
    else:
        placeholder = "Pega aquí el texto que quieres corregir y mejorar..."
        label = "📝 Texto a corregir:"
        help_text = "El sistema mejorará gramática, estilo y adaptará al tono Casa Limpia"
    
    user_input = st.text_area(
        label,
        placeholder=placeholder,
        height=120,
        max_chars=5000,
        key="user_input",
        help=help_text
    )
    
    if user_input:
        char_count = len(user_input)
        st.caption(f"Caracteres: {char_count}/5000")
        
        if task_type == "correct":
            st.info("🔧 **Función de Corrección**: Aplicará gramática, estilo Casa Limpia, vocabulario emocional y estructura profesional.")
    
    return user_input

def render_generation_controls(chatbot) -> tuple:
    """Renderizar controles de generación"""
    st.markdown('<div class="control-panel">', unsafe_allow_html=True)
    st.markdown("### ⚙️ Configuración de Generación")
    
    col_model, col_mode, col_num = st.columns([2, 2, 1])
    
    with col_model:
        # Obtener proveedores disponibles
        available_providers = chatbot.ai_provider.get_available_providers()
        provider_options = []
        provider_names = []
        
        for provider in available_providers:
            if provider["status"] == "✅":  # Solo mostrar los configurados
                provider_options.append(provider["display"])
                provider_names.append(provider["name"])
        
        if provider_options:
            selected_display = st.selectbox(
                "🤖 Modelo de IA:",
                provider_options,
                key="model_selector",
                help="Selecciona qué modelo de IA usar para generar el contenido"
            )
            
            # Encontrar el nombre interno del proveedor seleccionado
            selected_provider = provider_names[provider_options.index(selected_display)]
        else:
            selected_provider = "auto"
            st.warning("🔧 No hay modelos configurados. Configura al menos una API key.")
    
    with col_mode:
        generation_mode = st.radio(
            "📝 Modo de generación:",
            ["🎯 Una opción", "🎨 Múltiples opciones"],
            horizontal=True,
            key="generation_mode",
            help="Elige si quieres una sola versión o varias para comparar"
        )
    
    with col_num:
        if "Múltiples" in generation_mode:
            num_options = st.selectbox(
                "📊 Cantidad:",
                [2, 3, 4],
                index=1,
                key="num_options",
                help="Número de opciones diferentes a generar"
            )
        else:
            num_options = 1
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    return selected_provider, generation_mode, num_options

def render_generate_button() -> bool:
    """Renderizar botón de generar"""
    return st.button("🚀 Generar", type="primary", use_container_width=True)

def render_correct_button() -> bool:
    """Renderizar botón de corregir"""
    return st.button("✏️ Corregir Texto", type="primary", use_container_width=True)

def render_result_container(result: str, title: str = "📄 Resultado"):
    """Renderizar contenedor de resultado"""
    st.markdown('<div class="result-container">', unsafe_allow_html=True)
    st.markdown(f"### {title}")
    st.markdown(result)
    st.markdown('</div>', unsafe_allow_html=True)

def render_single_feedback(chatbot, original_input: str, result: str, task_type: str):
    """Renderizar feedback para una sola opción con estado persistente"""
    st.markdown("---")
    st.markdown("### ⭐ ¿Qué te parece el resultado?")
    
    # Crear keys únicos basados en el hash del resultado
    result_hash = str(hash(result))
    rating_key = f"rating_{result_hash}"
    feedback_key = f"feedback_{result_hash}"
    category_key = f"category_{result_hash}"
    
    # Inicializar valores en session_state si no existen
    if rating_key not in st.session_state:
        st.session_state[rating_key] = 3
    if feedback_key not in st.session_state:
        st.session_state[feedback_key] = ""
    if category_key not in st.session_state:
        st.session_state[category_key] = "General"
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        rating = st.select_slider(
            "Calificación:",
            options=[1, 2, 3, 4, 5],
            value=st.session_state[rating_key],
            format_func=lambda x: "⭐" * x,
            key=rating_key
        )
    
    with col2:
        feedback_text = st.text_area(
            "Comentarios (opcional):",
            value=st.session_state[feedback_key],
            placeholder="¿Qué mejorarías? ¿Qué te gustó?",
            height=80,
            key=feedback_key
        )
    
    # Categorías de feedback
    if task_type == "generate":
        categories = ["General", "Tono y estilo", "Contenido y mensaje", "Estructura", "Vocabulario", "Longitud"]
    else:
        categories = ["General", "Correcciones aplicadas", "Estilo Casa Limpia", "Claridad", "Precisión"]
    
    # Encontrar el índice de la categoría actual
    current_category_index = 0
    if st.session_state[category_key] in categories:
        current_category_index = categories.index(st.session_state[category_key])
    
    category = st.selectbox(
        "Categoría del feedback:",
        categories,
        index=current_category_index,
        key=category_key
    )
    
    if st.button("📝 Enviar Feedback", key=f"submit_{result_hash}"):
        chatbot.add_feedback(
            original=original_input,
            generated=result,
            task_type=task_type,
            rating=st.session_state[rating_key],
            comments=st.session_state[feedback_key],
            category=st.session_state[category_key]
        )
        
        # Limpiar el estado después de enviar
        st.session_state[rating_key] = 3
        st.session_state[feedback_key] = ""
        st.session_state[category_key] = "General"
        
        st.success("✅ ¡Gracias por tu feedback! El sistema seguirá aprendiendo.")
        st.balloons()
        st.rerun()

def render_multiple_feedback(chatbot, original_input: str, options: List[Dict], task_type: str):
    """Renderizar feedback para múltiples opciones con mejor UX"""
    
    st.markdown("### 📊 Compara las opciones y evalúa cada una")
    
    # Crear una clave única para este conjunto de opciones
    options_hash = str(hash(str([opt["text"] for opt in options])))
    
    # Inicializar estado si no existe
    if f"multi_feedback_init_{options_hash}" not in st.session_state:
        st.session_state[f"multi_feedback_init_{options_hash}"] = True
        for option in options:
            st.session_state[f"rating_{option['id']}_{options_hash}"] = 3
            st.session_state[f"feedback_{option['id']}_{options_hash}"] = ""
            st.session_state[f"category_{option['id']}_{options_hash}"] = "General"
    
    # Mostrar cada opción como una card separada (sin tabs)
    feedback_data = {}
    
    for i, option in enumerate(options):
        # Card container
        st.markdown(f'<div class="option-card">', unsafe_allow_html=True)
        
        # Header
        st.markdown(f'<div class="option-header">📝 {option["label"]} - Temperatura: {option.get("temperature", "N/A")}</div>', unsafe_allow_html=True)
        
        # Contenido de la opción
        st.markdown(option["text"])
        
        # Sección de feedback
        st.markdown(f'<div class="feedback-section">', unsafe_allow_html=True)
        st.markdown(f"**⭐ Evalúa {option['label']}:**")
        
        # Keys únicos para esta opción
        rating_key = f"rating_{option['id']}_{options_hash}"
        feedback_key = f"feedback_{option['id']}_{options_hash}"
        category_key = f"category_{option['id']}_{options_hash}"
        
        # Layout del feedback
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            rating = st.select_slider(
                "Calificación:",
                options=[1, 2, 3, 4, 5],
                value=st.session_state[rating_key],
                format_func=lambda x: "⭐" * x,
                key=rating_key,
                label_visibility="collapsed"
            )
            st.caption("⭐ Calificación")
        
        with col2:
            categories = ["General", "Tono y estilo", "Contenido y mensaje", "Estructura", "Vocabulario", "Longitud"]
            current_idx = 0
            if st.session_state[category_key] in categories:
                current_idx = categories.index(st.session_state[category_key])
            
            category = st.selectbox(
                "Categoría:",
                categories,
                index=current_idx,
                key=category_key,
                label_visibility="collapsed"
            )
            st.caption("📂 Categoría")
        
        with col3:
            feedback_text = st.text_area(
                "Comentarios:",
                value=st.session_state[feedback_key],
                placeholder=f"¿Qué opinas de {option['label']}?",
                height=80,
                key=feedback_key,
                label_visibility="collapsed"
            )
            st.caption("💬 Comentarios")
        
        # Almacenar datos del feedback
        feedback_data[option['id']] = {
            "rating": rating,
            "feedback": feedback_text,
            "category": category,
            "text": option["text"],
            "label": option["label"]
        }
        
        st.markdown('</div>', unsafe_allow_html=True)  # Cerrar feedback-section
        st.markdown('</div>', unsafe_allow_html=True)  # Cerrar option-card
        
        # Espacio entre cards
        st.markdown("")
    
    # Botón de envío mejorado
    st.markdown("---")
    
    # Mostrar resumen antes de enviar
    non_default_count = sum(1 for data in feedback_data.values() 
                           if data["rating"] != 3 or data["feedback"].strip())
    
    if non_default_count > 0:
        st.info(f"📊 Tienes feedback en {non_default_count} de {len(options)} opciones")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📝 Enviar Todo el Feedback", 
                    type="primary", 
                    use_container_width=True, 
                    key=f"submit_all_{options_hash}"):
            
            feedback_count = 0
            for option_id, data in feedback_data.items():
                if data["rating"] != 3 or data["feedback"].strip():
                    chatbot.add_feedback(
                        original=original_input,
                        generated=data["text"],
                        task_type=task_type,
                        rating=data["rating"],
                        comments=data["feedback"],
                        category=data["category"],
                        option_id=option_id
                    )
                    feedback_count += 1
            
            if feedback_count > 0:
                # Limpiar estado después de enviar
                for option in options:
                    st.session_state[f"rating_{option['id']}_{options_hash}"] = 3
                    st.session_state[f"feedback_{option['id']}_{options_hash}"] = ""
                    st.session_state[f"category_{option['id']}_{options_hash}"] = "General"
                
                st.session_state[f"multi_feedback_init_{options_hash}"] = False
                
                st.success(f"✅ ¡Perfecto! Se registraron {feedback_count} evaluaciones.")
                st.balloons()
                time.sleep(1)
                st.rerun()
            else:
                st.warning("💡 Ajusta las calificaciones o agrega comentarios para enviar feedback.")

def show_loading_spinner(message: str = "Generando..."):
    """Mostrar spinner de carga"""
    return st.spinner(message)

def show_provider_info(provider_name: str, available_providers: List[Dict]):
    """Mostrar información del proveedor seleccionado"""
    if provider_name != "auto":
        provider_display = next((p["display"] for p in available_providers if p["name"] == provider_name), provider_name)
        st.info(f"🤖 Usando: {provider_display}")

def render_error_message(message: str):
    """Renderizar mensaje de error"""
    st.error(f"❌ {message}")

def render_success_message(message: str):
    """Renderizar mensaje de éxito"""
    st.success(f"✅ {message}")

def render_warning_message(message: str):
    """Renderizar mensaje de advertencia"""
    st.warning(f"⚠️ {message}")

def render_info_message(message: str):
    """Renderizar mensaje informativo"""
    st.info(f"ℹ️ {message}")

def show_tips():
    """Mostrar consejos de uso"""
    with st.expander("💡 Consejos de uso", expanded=False):
        st.markdown("""
        **Para obtener mejores resultados:**
        
        🎯 **Generación de textos:**
        - Describe claramente la ocasión o evento
        - Menciona el público objetivo (colaboradores, directivos, etc.)
        - Especifica el tono deseado (formal, celebrativo, motivacional)
        
        ✏️ **Corrección de textos:**
        - Pega el texto completo que quieres mejorar
        - El sistema adaptará automáticamente al estilo Casa Limpia
        - Se corregirán gramática, vocabulario y estructura
        
        ⭐ **Feedback:**
        - Califica cada resultado del 1 al 5
        - Deja comentarios específicos sobre lo que te gustó o no
        - El sistema aprende de tus preferencias para mejorar
        """)
