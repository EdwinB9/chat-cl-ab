"""
Casa Limpia - Asistente de Comunicación IA
Interfaz minimalista enfocada en UX
"""

import os
import streamlit as st
import time
from core import MinimalChatBot


st.set_page_config(
     page_title="Casa Limpia Colombia - Asistente de Comunicación IA",
     page_icon="✨",
     layout="centered",
     initial_sidebar_state="collapsed"
)

def render_header():
    """Header simple usando elementos nativos de Streamlit"""
    st.title("✨ Casa Limpia Colombia")
    st.caption("Asistente de Comunicación Inteligente")
    st.markdown("---")

def render_simple_feedback(chatbot, original_text, generated_text, task_type):
    """Sistema de feedback robusto con categorización estandarizada"""
    st.markdown("---")
    
    # Crear un ID único más robusto
    content_id = f"feedback_{abs(hash(str(generated_text) + str(original_text) + str(task_type)))}"
    
    # Estado para controlar si el feedback fue enviado
    if get_feedback_state(content_id):
        # 🎉 Estado de feedback enviado - Diseño mejorado
        st.markdown("---")
        with st.container():
            # Header del feedback con icono y título
            col1, col2 = st.columns([1, 4])
            with col1:
                st.markdown("🎯")
            with col2:
                st.markdown("**💬 Feedback Enviado**")
            
            # Mensaje de confirmación con mejor diseño
            st.success("✅ **¡Excelente!** Tu feedback ha sido enviado y guardado correctamente.")
            
            # Botón para enviar feedback adicional con mejor diseño
            if st.button("🔄 Enviar feedback adicional", 
                        key=f"reset_{content_id}", 
                        help="Enviar feedback adicional sobre este resultado", 
                        type="secondary",
                        use_container_width=True):
                set_feedback_state(content_id, False)
        return
    
    # 📝 Formulario de feedback con UI/UX mejorada y categorización
    st.markdown("### 💬 **¿Qué opinas del resultado?**")
    st.caption("Tu opinión ayuda a mejorar la calidad del sistema de IA")
    
    with st.form(key=f"feedback_form_{content_id}"):
        # 🌟 Sección de calificación mejorada
        st.markdown("**⭐ Calificación:**")
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            # Slider de calificación con mejor diseño
            rating = st.select_slider(
                "Selecciona tu calificación:",
                options=[1, 2, 3, 4, 5],
                value=3,
                format_func=lambda x: f"{'⭐' * x} ({x}/5)",
                help="Evalúa la calidad del texto generado del 1 al 5"
            )
        
        with col2:
            # Indicador visual de la calificación seleccionada
            st.markdown(f"**Calificación actual:** {'⭐' * rating}")
            st.progress(rating / 5)
        
        with col3:
            # Descripción de la calificación
            rating_descriptions = {
                1: "❌ Muy malo",
                2: "⚠️ Malo", 
                3: "😐 Regular",
                4: "👍 Bueno",
                5: "🌟 Excelente"
            }
            st.caption(f"**{rating_descriptions[rating]}**")
        
        # 💭 Sección de comentarios simplificada
        st.markdown("**💭 ¿Qué opinas del resultado?**")
        comment = st.text_area(
            "Comparte tu opinión:",
            placeholder="¿Qué te gustó? ¿Qué mejorarías? ¿Qué opinas del estilo o contenido?",
            height=80,
            max_chars=300,
            help="Describe tu opinión sobre el resultado (máximo 300 caracteres)"
        )
        
        # Contador de caracteres
        if comment:
            char_count = len(comment)
            st.caption(f"📝 {char_count}/300 caracteres")
        
        # 📤 Botón de envío mejorado
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button(
                "📤 **Enviar Feedback Completo**", 
                help="Enviar tu evaluación completa y categorizada",
                type="primary",
                use_container_width=True
            )
        
        if submitted:
            try:
                # Guardar feedback simplificado
                chatbot.add_feedback(
                    original=original_text,
                    generated=generated_text,
                    task_type=task_type,
                    rating=rating,
                    comments=comment,
                    option_id="main_result"
                )
                
                # 🎉 Confirmación mejorada
                set_feedback_state(content_id, True)
                
                # Mensaje de éxito con resumen del feedback
                st.success("🎉 **¡Feedback enviado exitosamente!**")
                st.info(f"📊 **Calificación:** {rating}/5 ⭐")
                if comment:
                    st.info(f"💭 **Comentarios:** {comment[:100]}{'...' if len(comment) > 100 else ''}")
                
                # Globos de celebración
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ **Error al enviar feedback:** {str(e)}")
                st.info("💡 Intenta de nuevo o contacta al administrador")

def reset_feedback_state():
    """Función para resetear el estado del feedback si es necesario"""
    # Limpiar todos los estados de feedback
    keys_to_remove = [key for key in st.session_state.keys() if key.startswith('feedback_sent_') or key.startswith('option_feedback_')]
    for key in keys_to_remove:
        del st.session_state[key]

def get_feedback_state(content_id):
    """Obtener el estado del feedback de manera robusta"""
    feedback_sent_key = f"feedback_sent_{content_id}"
    if feedback_sent_key not in st.session_state:
        st.session_state[feedback_sent_key] = False
    return st.session_state[feedback_sent_key]

def set_feedback_state(content_id, sent=True):
    """Establecer el estado del feedback de manera robusta"""
    feedback_sent_key = f"feedback_sent_{content_id}"
    st.session_state[feedback_sent_key] = sent

def display_saved_results(chatbot, user_input, task_type):
    """Mostrar resultados guardados en session_state si existen"""
    if not user_input:
        return
    
    # Buscar resultados guardados
    result_key = f"result_{task_type}_{abs(hash(user_input))}"
    if result_key in st.session_state:
        result = st.session_state[result_key]
        
        # Verificar si este resultado ya se mostró en esta sesión
        display_key = f"displayed_{result_key}"
        if display_key in st.session_state:
            # El resultado ya se mostró, no mostrar duplicado
            return False
        
        st.markdown("---")
        st.subheader(f"📄 {'Texto generado' if task_type == 'generate' else 'Texto corregido'}")
        
        # Contenedor destacado para el resultado
        with st.container():
            st.markdown(f"""
            <div style="padding: 1rem; border-radius: 8px; border-left: 4px solid #10b981;">
            {result}
            </div>
            """, unsafe_allow_html=True)
        
        # Feedback con clave única para evitar duplicados
        saved_feedback_key = f"saved_feedback_{result_key}"
        if saved_feedback_key not in st.session_state:
            render_simple_feedback(chatbot, user_input, result, task_type)
            st.session_state[saved_feedback_key] = True
        
        # Marcar como mostrado
        st.session_state[display_key] = True
        return True
    
    return False

def main():
    # Inicializar chatbot
    chatbot = MinimalChatBot()
    
    # Header
    render_header()
    
    # Modo de trabajo mejorado
    st.markdown("### 🎯 Selecciona el modo de trabajo")
    mode = st.radio(
        "Modo de trabajo",
        ["🚀 Generar texto", "✏️ Corregir texto"],
        horizontal=True,
        help="Elige si quieres generar un nuevo texto o corregir uno existente"
    )
    
    # Configuración de IA (expandible) - Mejorada
    with st.expander("⚙️ Configuración de IA", expanded=False):
        ai_providers = chatbot.ai_provider.get_providers_for_ui()
        available_providers = [name for name, status in ai_providers.items() if status["available"]]
        
        if available_providers:
            # Inicializar el provider seleccionado si no existe
            if 'selected_ai_provider' not in st.session_state:
                st.session_state.selected_ai_provider = available_providers[0]
            
            # Selector mejorado
            col1, col2 = st.columns([3, 1])
            with col1:
                selected_provider = st.selectbox(
                    "Modelo de IA:",
                    available_providers,
                    index=available_providers.index(st.session_state.selected_ai_provider),
                    key="ai_provider_selector",
                    format_func=lambda x: f"🤖 {x.title()} - {ai_providers[x]['model']}"
                )
            
            with col2:
                st.markdown("")  # Espaciado
                st.markdown("")  # Espaciado
                if st.button("🔄 Cambiar", key="change_provider_btn", help="Cambiar modelo de IA"):
                    st.session_state.selected_ai_provider = selected_provider
                    st.rerun()
            
            # Actualizar el provider seleccionado en session_state
            st.session_state.selected_ai_provider = selected_provider
            
            # Mostrar estado del provider seleccionado de forma más clara
            status = ai_providers[selected_provider]
            st.info(f"**Modelo activo:** {selected_provider.title()} - {status['model']}")
            
        else:
            st.warning("⚠️ No hay modelos de IA disponibles")
            st.info("💡 Configura una API key en tu archivo .env")
    
    # Input principal mejorado
    st.markdown("---")
    if "Generar" in mode:
        user_input = st.text_area(
            "💭 ¿Qué tipo de comunicación necesitas?",
            placeholder="Ej: Día de la mujer, felicitación por logros, bienvenida nuevos colaboradores...",
            height=120,
            max_chars=1000,
            help="Describe el tipo de comunicación que necesitas generar"
        )
        task_type = "generate"
        button_text = "🚀 Generar"
        button_help = "Crear comunicación profesional"
    else:
        user_input = st.text_area(
            "📝 Texto a corregir:",
            placeholder="Pega aquí el texto que quieres mejorar...",
            height=150,
            max_chars=2000,
            help="Pega el texto que quieres que sea corregido y mejorado"
        )
        task_type = "correct"
        button_text = "✏️ Corregir"
        button_help = "Mejorar gramática y estilo"
    
    # Mostrar contador de caracteres con mejor formato
    if user_input:
        char_count = len(user_input)
        word_count = len(user_input.split())
        st.caption(f"📊 {char_count} caracteres • {word_count} palabras")
    
    # Slider de longitud del texto (solo para generación)
    if "Generar" in mode and user_input:
        st.markdown("---")
        st.markdown("### 📏 Configuración de Longitud")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Slider con valores de palabras - usar solo session_state
            text_length_words = st.slider(
                "**Longitud del texto generado:**",
                min_value=20,
                max_value=160,
                value=60,  # Valor inicial fijo
                step=10,
                key="text_length_slider",
                help="Controla la longitud del texto generado (20-160 palabras)"
            )
        
        with col2:
            # Mostrar métricas de longitud de forma más clara
            chars_approx = text_length_words * 5  # Aproximación: 5 caracteres por palabra
            
            st.metric(
                label="📝 Palabras objetivo",
                value=text_length_words,
                delta=f"≈ {chars_approx} caracteres"
            )
    
    # Opciones y botón principal
    if user_input and len(user_input.strip()) > 10:
        
        # Opciones para generación - Mejoradas
        if task_type == "generate":
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                generate_btn = st.button(button_text, help=button_help, use_container_width=True, type="primary")
            with col2:
                multiple = st.checkbox("🔄 Múltiples opciones", help="Generar 3 versiones diferentes para comparar")
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
            # LIMPIAR RESULTADOS ANTERIORES antes de generar nuevos
            result_key = f"result_{task_type}_{abs(hash(user_input))}"
            
            # Limpiar resultado principal
            if result_key in st.session_state:
                del st.session_state[result_key]
            
            # Limpiar opciones múltiples (solo el contenido, no el feedback)
            for i in range(10):  # Limpiar hasta 10 opciones
                option_key = f"option_{i}_{abs(hash(user_input))}_"
                # Buscar y eliminar solo las opciones de contenido, NO el feedback
                keys_to_remove = [key for key in st.session_state.keys() 
                                 if key.startswith(option_key) and not key.startswith("option_feedback_")]
                for key in keys_to_remove:
                    del st.session_state[key]
            
            # Limpiar marcadores de display
            display_key = f"displayed_{result_key}"
            if display_key in st.session_state:
                del st.session_state[display_key]
            
            # NO limpiar feedback states - mantener el estado del feedback
            # feedback_keys = [key for key in st.session_state.keys() if key.startswith("feedback_sent_") or key.startswith("option_feedback_")]
            # for key in feedback_keys:
            #     del st.session_state[key]
            
            
            # Obtener el provider seleccionado del session_state
            selected_provider = st.session_state.get('selected_ai_provider', None)
            
            # Mostrar qué modelo se está usando
            if selected_provider:
                st.info(f"🤖 Generando con: **{selected_provider.title()}**")
            
            with st.spinner("🤖 Trabajando..."):
                if task_type == "generate" and multiple:
                    # Múltiples opciones
                    text_length_words = st.session_state.get('text_length_slider', 60)
                    text_length_chars = text_length_words * 5  # Convertir palabras a caracteres
                    options = chatbot.generate_multiple_options(user_input, 3, preferred_provider=selected_provider, max_chars=text_length_chars)
                    
                    if options and any(not opt["text"].startswith("❌") for opt in options):
                        st.markdown("### 📋 Opciones generadas")
                        
                        # Guardar todas las opciones en session_state para persistencia total
                        options_key = f"multiple_options_{task_type}_{abs(hash(user_input))}"
                        st.session_state[options_key] = options
                        
                        # Mostrar opciones con mejor UX
                        for i, option in enumerate(options):
                            if not option["text"].startswith("❌"):
                                # Guardar la opción individual en session_state para mantenerla visible
                                option_key = f"option_{i}_{abs(hash(user_input))}_{abs(hash(option['text']))}"
                                st.session_state[option_key] = option["text"]
                                
                                # Contenedor para cada opción con mejor organización
                                with st.container():
                                    st.markdown("---")
                                    st.subheader(f"🎯 Opción {i+1}")
                                    st.caption(f"🌡️ Temperatura: {option.get('temperature', 'N/A')}")
                                    
                                    # Mostrar el texto generado en un contenedor destacado que se mantiene visible
                                    st.markdown("**Resultado:**")
                                    with st.container():
                                        # Usar st.markdown para mejor formato y persistencia
                                        st.markdown(f"""
                                        <div style="padding: 1rem; border-radius: 8px; border-left: 4px solid #3b82f6;">
                                        {option["text"]}
                                        </div>
                                        """, unsafe_allow_html=True)
                                    
                                    # 🎨 FEEDBACK MEJORADO con UI/UX moderna
                                    opt_id = f"opt_{i}_{abs(hash(user_input))}"
                                    
                                    # Estado para controlar si el feedback fue enviado para esta opción
                                    option_feedback_key = f"option_feedback_{opt_id}"
                                    if option_feedback_key not in st.session_state:
                                        st.session_state[option_feedback_key] = False
                                    
                                    if st.session_state[option_feedback_key]:
                                        # 🎉 Estado de feedback enviado - Diseño mejorado
                                        st.markdown("---")
                                        with st.container():
                                            # Header del feedback con icono y título
                                            col1, col2 = st.columns([1, 4])
                                            with col1:
                                                st.markdown("🎯")
                                            with col2:
                                                st.markdown("**💬 Feedback Enviado**")
                                            
                                            # Mensaje de confirmación con mejor diseño
                                            st.success("✅ **¡Excelente!** Tu feedback ha sido enviado y guardado correctamente.")
                                            
                                            # Botón para enviar feedback adicional con mejor diseño
                                            if st.button("🔄 Enviar feedback adicional", 
                                                        key=f"reset_option_{opt_id}", 
                                                        help="Enviar feedback adicional sobre esta opción", 
                                                        type="secondary",
                                                        use_container_width=True):
                                                st.session_state[option_feedback_key] = False
                                    
                                    else:
                                        # 📝 Formulario de feedback con UI/UX mejorada
                                        st.markdown("---")
                                        st.markdown("### 💬 **¿Qué opinas de esta opción?**")
                                        st.caption("Tu opinión ayuda a mejorar la calidad del sistema de IA")
                                        
                                        with st.form(key=f"option_feedback_form_{opt_id}"):
                                            # 🌟 Sección de calificación mejorada
                                            st.markdown("**⭐ Calificación:**")
                                            col1, col2, col3 = st.columns([1, 2, 1])
                                            
                                            with col1:
                                                # Slider de calificación con mejor diseño
                                                rating = st.select_slider(
                                                    "Selecciona tu calificación:",
                                                    options=[1, 2, 3, 4, 5],
                                                    value=3,
                                                    format_func=lambda x: f"{'⭐' * x} ({x}/5)",
                                                    help="Evalúa la calidad de esta opción del 1 al 5"
                                                )
                                            
                                            with col2:
                                                # Indicador visual de la calificación seleccionada
                                                st.markdown(f"**Calificación actual:** {'⭐' * rating}")
                                                st.progress(rating / 5)
                                            
                                            with col3:
                                                # Descripción de la calificación
                                                rating_descriptions = {
                                                    1: "❌ Muy malo",
                                                    2: "⚠️ Malo", 
                                                    3: "😐 Regular",
                                                    4: "👍 Bueno",
                                                    5: "🌟 Excelente"
                                                }
                                                st.caption(f"**{rating_descriptions[rating]}**")
                                            
                                            # 💭 Sección de comentarios mejorada
                                            st.markdown("**💭 Comentarios:**")
                                            comment = st.text_area(
                                                "Comparte tu opinión:",
                                                placeholder="¿Qué te gustó? ¿Qué mejorarías? ¿Qué opinas del estilo o contenido?",
                                                height=80,
                                                max_chars=500,
                                                help="Describe tu opinión sobre esta opción (máximo 500 caracteres)"
                                            )
                                            
                                            # Contador de caracteres
                                            if comment:
                                                char_count = len(comment)
                                                st.caption(f"📝 {char_count}/500 caracteres")
                                            
                                            # 📤 Botón de envío mejorado
                                            st.markdown("---")
                                            col1, col2, col3 = st.columns([1, 2, 1])
                                            with col2:
                                                submitted = st.form_submit_button(
                                                    "📤 **Enviar Feedback**", 
                                                    help="Enviar tu evaluación y comentarios",
                                                    type="primary",
                                                    use_container_width=True
                                                )
                                            
                                            if submitted:
                                                try:
                                                    # Guardar feedback
                                                    chatbot.add_feedback(
                                                        original=user_input,
                                                        generated=option["text"],
                                                        task_type=task_type,
                                                        rating=rating,
                                                        comments=comment,
                                                        option_id=f"option_{i+1}"
                                                    )
                                                    
                                                    # 🎉 Confirmación mejorada
                                                    st.session_state[option_feedback_key] = True
                                                    
                                                    # Mensaje de éxito con mejor diseño
                                                    st.success("🎉 **¡Feedback enviado exitosamente!**")
                                                    st.info(f"📊 **Calificación:** {rating}/5 ⭐")
                                                    if comment:
                                                        st.info(f"💭 **Comentario:** {comment}")
                                                    
                                                    # Globos de celebración
                                                    st.balloons()
                                                    
                                                except Exception as e:
                                                    st.error(f"❌ **Error al enviar feedback:** {str(e)}")
                                                    st.info("💡 Intenta de nuevo o contacta al administrador")
                                    
                                    st.markdown("---")
                                    
                                    # Marcar que esta opción ya se mostró para evitar duplicados
                                    option_display_key = f"option_displayed_{option_key}"
                                    st.session_state[option_display_key] = True
                    else:
                        st.error("❌ No se pudieron generar las opciones. Verifica la configuración de IA.")
                        
                
                else:
                    # Una sola opción
                    if task_type == "generate":
                        # Obtener la longitud del slider (en palabras) y convertir a caracteres
                        text_length_words = st.session_state.get('text_length_slider', 60)
                        text_length_chars = text_length_words * 5  # Convertir palabras a caracteres
                        result = chatbot.generate_text(user_input, preferred_provider=selected_provider, max_chars=text_length_chars)
                    else:
                        result = chatbot.correct_text(user_input, preferred_provider=selected_provider)
                    
                    if not result.startswith("❌"):
                        # Guardar el resultado en session_state para mantenerlo visible
                        result_key = f"result_{task_type}_{abs(hash(user_input))}"
                        st.session_state[result_key] = result
                        
                        # Mostrar resultado con mejor presentación
                        st.markdown("---")
                        st.subheader(f"📄 {'Texto generado' if task_type == 'generate' else 'Texto corregido'}")
                        
                        # Contenedor destacado para el resultado que se mantiene visible
                        with st.container():
                            # Usar st.markdown para mejor formato y persistencia
                            st.markdown(f"""
                            <div style="padding: 1rem; border-radius: 8px; border-left: 4px solid #10b981;">
                            {result}
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Feedback mejorado
                        render_simple_feedback(chatbot, user_input, result, task_type)
                        
                        # Marcar que este resultado ya se mostró para evitar duplicados
                        display_key = f"displayed_{result_key}"
                        st.session_state[display_key] = True
                    else:
                        st.error(result)
    
    # MOSTRAR RESULTADOS EXISTENTES después del procesamiento (si no se generó nuevo contenido)
    if user_input and len(user_input.strip()) > 10 and not generate_btn:
        # Buscar resultados existentes en session_state
        result_key = f"result_{task_type}_{abs(hash(user_input))}"
        if result_key in st.session_state:
            result = st.session_state[result_key]
            
            # Mostrar resultado existente
            st.markdown("---")
            st.subheader(f"📄 {'Texto generado' if task_type == 'generate' else 'Texto corregido'}")
            
            # Contenedor destacado para el resultado
            with st.container():
                st.markdown(f"""
                <div style="padding: 1rem; border-radius: 8px; border-left: 4px solid #10b981;">
                {result}
                </div>
                """, unsafe_allow_html=True)
            
            # Feedback
            render_simple_feedback(chatbot, user_input, result, task_type)
        
        # Buscar opciones múltiples existentes
        options_key = f"multiple_options_{task_type}_{abs(hash(user_input))}"
        if options_key in st.session_state:
            options = st.session_state[options_key]
            
            if options and any(not opt["text"].startswith("❌") for opt in options):
                st.markdown("---")
                st.markdown("### 📋 Opciones generadas (anteriores)")
                
                # Mostrar opciones existentes con feedback
                for i, option in enumerate(options):
                    if not option["text"].startswith("❌"):
                        # Contenedor para cada opción
                        with st.container():
                            st.markdown("---")
                            st.subheader(f"🎯 Opción {i+1}")
                            st.caption(f"🌡️ Temperatura: {option.get('temperature', 'N/A')}")
                            
                            # Mostrar el texto generado
                            st.markdown("**Resultado:**")
                            with st.container():
                                st.markdown(f"""
                                <div style="padding: 1rem; border-radius: 8px; border-left: 4px solid #3b82f6;">
                                {option["text"]}
                                </div>
                                """, unsafe_allow_html=True)
                            
                            # 🎨 Feedback mejorado para opción existente
                            opt_id = f"opt_{i}_{abs(hash(user_input))}"
                            option_feedback_key = f"option_feedback_{opt_id}"
                            
                            if option_feedback_key in st.session_state and st.session_state[option_feedback_key]:
                                # 🎉 Estado de feedback enviado - Diseño mejorado
                                st.markdown("---")
                                with st.container():
                                    # Header del feedback con icono y título
                                    col1, col2 = st.columns([1, 4])
                                    with col1:
                                        st.markdown("🎯")
                                    with col2:
                                        st.markdown("**💬 Feedback Enviado**")
                                    
                                    # Mensaje de confirmación con mejor diseño
                                    st.success("✅ **¡Excelente!** Tu feedback ha sido enviado y guardado correctamente.")
                                    
                                    # Botón para enviar feedback adicional con mejor diseño
                                    if st.button("🔄 Enviar feedback adicional", 
                                                key=f"reset_existing_option_{opt_id}", 
                                                help="Enviar feedback adicional sobre esta opción", 
                                                type="secondary",
                                                use_container_width=True):
                                        st.session_state[option_feedback_key] = False
                            else:
                                # 📝 Formulario de feedback con UI/UX mejorada para opciones existentes
                                st.markdown("---")
                                st.markdown("### 💬 **¿Qué opinas de esta opción?**")
                                st.caption("Tu opinión ayuda a mejorar la calidad del sistema de IA")
                                
                                with st.form(key=f"existing_option_feedback_form_{opt_id}"):
                                    # 🌟 Sección de calificación mejorada
                                    st.markdown("**⭐ Calificación:**")
                                    col1, col2, col3 = st.columns([1, 2, 1])
                                    
                                    with col1:
                                        # Slider de calificación con mejor diseño
                                        rating = st.select_slider(
                                            "Selecciona tu calificación:",
                                            options=[1, 2, 3, 4, 5],
                                            value=3,
                                            format_func=lambda x: f"{'⭐' * x} ({x}/5)",
                                            help="Evalúa la calidad de esta opción del 1 al 5"
                                        )
                                    
                                    with col2:
                                        # Indicador visual de la calificación seleccionada
                                        st.markdown(f"**Calificación actual:** {'⭐' * rating}")
                                        st.progress(rating / 5)
                                    
                                    with col3:
                                        # Descripción de la calificación
                                        rating_descriptions = {
                                            1: "❌ Muy malo",
                                            2: "⚠️ Malo", 
                                            3: "😐 Regular",
                                            4: "👍 Bueno",
                                            5: "🌟 Excelente"
                                        }
                                        st.caption(f"**{rating_descriptions[rating]}**")
                                    
                                    # 💭 Sección de comentarios mejorada
                                    st.markdown("**💭 Comentarios:**")
                                    comment = st.text_area(
                                        "Comparte tu opinión:",
                                        placeholder="¿Qué te gustó? ¿Qué mejorarías? ¿Qué opinas del estilo o contenido?",
                                        height=80,
                                        max_chars=500,
                                        help="Describe tu opinión sobre esta opción (máximo 500 caracteres)"
                                    )
                                    
                                    # Contador de caracteres
                                    if comment:
                                        char_count = len(comment)
                                        st.caption(f"📝 {char_count}/500 caracteres")
                                    
                                    # 📤 Botón de envío mejorado
                                    st.markdown("---")
                                    col1, col2, col3 = st.columns([1, 2, 1])
                                    with col2:
                                        submitted = st.form_submit_button(
                                            "📤 **Enviar Feedback**", 
                                            help="Enviar tu evaluación y comentarios",
                                            type="primary",
                                            use_container_width=True
                                        )
                                    
                                    if submitted:
                                        try:
                                            # Guardar feedback
                                            chatbot.add_feedback(
                                                original=user_input,
                                                generated=option["text"],
                                                task_type=task_type,
                                                rating=rating,
                                                comments=comment,
                                                option_id=f"option_{i+1}"
                                            )
                                            
                                            # 🎉 Confirmación mejorada
                                            st.session_state[option_feedback_key] = True
                                            
                                            # Mensaje de éxito con mejor diseño
                                            st.success("🎉 **¡Feedback enviado exitosamente!**")
                                            st.info(f"📊 **Calificación:** {rating}/5 ⭐")
                                            if comment:
                                                st.info(f"💭 **Comentario:** {comment}")
                                            
                                            # Globos de celebración
                                            st.balloons()
                                            
                                        except Exception as e:
                                            st.error(f"❌ **Error al enviar feedback:** {str(e)}")
                                            st.info("💡 Intenta de nuevo o contacta al administrador")
    
    # Footer mejorado
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.caption("🏢 Casa Limpia Colombia - Asistente de Comunicación IA")
        st.caption("✨ Potenciado con Inteligencia Artificial")

if __name__ == "__main__":
    main()