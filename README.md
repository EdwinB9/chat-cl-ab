# ✨ Casa Limpia Colombia - Asistente de Comunicación IA

Chatbot especializado que genera y corrige textos siguiendo el estilo único y emotivo de Casa Limpia Colombia.

## 🚀 Inicio Rápido

```bash
# Instalar dependencias
pip install -r requirements.txt

# (Opcional) Configurar IA gratuita para mejores resultados
# Ver sección "Configuración de IA" abajo

# Ejecutar la aplicación
streamlit run app.py
```

## ⚡ Configuración de IA (Opcional pero Recomendado)

**Sin configuración:** El sistema funciona con respuestas simuladas inteligentes.  
**Con IA real:** Respuestas más variadas y naturales usando APIs gratuitas.

### 🚀 **Groq (Recomendado - Ultra rápido)**
1. Ve a [console.groq.com](https://console.groq.com)
2. Crea cuenta gratis (solo email)
3. Obtén tu API key
4. Configura: `GROQ_API_KEY=tu_key` como variable de entorno

### 🤗 **Hugging Face (100% Gratis)**
1. Ve a [huggingface.co](https://huggingface.co)
2. Crea cuenta gratis
3. Ve a Settings > Access Tokens > New Token
4. Configura: `HUGGINGFACE_API_KEY=tu_token`

### 🔧 **Otras Opciones Gratuitas:**
- **Together AI**: Modelos open source
- **Cohere**: Gratuito para desarrollo

### 💻 **Cómo configurar variables de entorno:**

**Windows:**
```cmd
set GROQ_API_KEY=tu_key_aqui
streamlit run app.py
```

**Mac/Linux:**
```bash
export GROQ_API_KEY=tu_key_aqui
streamlit run app.py
```

**O crear archivo `.env` en la carpeta del proyecto:**
```
GROQ_API_KEY=tu_key_aqui
HUGGINGFACE_API_KEY=tu_token_aqui
```

## 🎯 ¿Qué hace?

### **Generar Textos**
- 🎉 **Comunicaciones internas** (celebraciones, reconocimientos)
- 📧 **Emails comerciales** con tono cálido y familiar
- 🏆 **Mensajes de agradecimiento** profundos y emotivos
- 🌍 **Contenido sobre diversidad** e inclusión
- 💼 **Propuestas de servicio** personalizadas

### **Corregir Textos**
- ✏️ Aplica terminología preferida ("colaboradores" vs "empleados")
- 🎨 Ajusta al tono emotivo y humano de la empresa
- 📝 Mejora estructura narrativa
- ❤️ Fortalece mensaje familiar y valores

## 📋 Ejemplos de Uso

### Comunicación Interna:
```
Input: "Mensaje para celebrar el Día de la Mujer"
Output: Texto emotivo con estructura: reflexión → reconocimiento → mensaje → inspiración
```

### Email Comercial:
```
Input: "Email para familia interesada en limpieza regular"
Output: Email cálido con servicios, beneficios y información de contacto
```

### Reconocimiento:
```
Input: "Agradecimiento para supervisores por buenos resultados"
Output: Mensaje profundo sobre liderazgo, impacto y gratitud familiar
```

## 🎨 Estilo Casa Limpia Colombia

### **Características del Tono:**
- ❤️ **Profundamente humano** y emotivo
- 👨‍👩‍👧‍👦 **Familiar**: "Gran Familia Casalimpia"
- 🙏 **Gratitud auténtica** y reconocimiento
- ✨ **Celebrativo** y positivo
- 🤝 **Inclusivo** y diverso

### **Frases Típicas:**
- "Son el alma de nuestro servicio"
- "Ustedes son nuestro activo más valioso"
- "Gracias por ser inspiración y por ser familia"
- "La diversidad que nos construye"
- "Tu hogar en las mejores manos"

## ⚙️ Configuración (Backend)

El sistema usa archivos en `.config/` (se crean automáticamente):

- **`company_context.json`**: Información de la empresa, valores, servicios
- **`learning_data.json`**: Ejemplos reales y preferencias aprendidas
- **`correction_rules.json`**: Reglas de terminología y estilo
- **`settings.json`**: Configuración de la aplicación

## 💡 Tips para Mejores Resultados

### ✅ **Prompts Efectivos:**
- "Mensaje celebrativo para [ocasión] dirigido a [audiencia]"
- "Reconocimiento para [equipo] por [logro específico]"
- "Email comercial para [tipo de cliente]"

### ❌ **Evitar:**
- Prompts muy genéricos sin contexto
- Solicitudes sin conexión con valores empresariales
- Contenido puramente transaccional

## 📊 Ejemplos Reales Integrados

El sistema fue entrenado con textos reales de Casa Limpia Colombia:
- Mensaje Halloween (celebrativo y familiar)
- Día del Operario (reconocimiento profundo)
- Día de la Raza (diversidad e inclusión)
- Mensajes de responsabilidad social

## 🔄 Sistema de Aprendizaje

- **Rating con estrellas** (1-5) para cada texto generado
- **Comentarios específicos** sobre estilo y tono  
- **Mejora automática** basada en feedback
- **Adaptación continua** a preferencias del usuario
- **Feedback persistente** sin pérdida de datos al interactuar

---

**✨ Desarrollado específicamente para Casa Limpia Colombia**
*"Gran Familia Casalimpia - Tu hogar en las mejores manos"*
