import os
import base64
import numpy as np
from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas
from openai import OpenAI

# 1. Configuración de la página con tema infantil
st.set_page_config(page_title="¡Pequeños Artistas! 🎨✨", page_icon="🎨", layout="centered")

# Estilos CSS personalizados (Fondo azul oscuro con contraste para texto blanco)
st.markdown("""
    <style>
    /* Fondo principal azul oscuro */
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
    }
    
    /* Cambiar el color de los textos predeterminados a blanco */
    h1, h2, h3, h4, h5, h6, p, label, div {
        color: #F8FAFC !important;
    }
    
    /* Contenedores tipo tarjeta en fondo azul violeta oscuro */
    div[data-testid="stVerticalBlock"] > div {
        border-radius: 20px;
    }
    
    /* Botón principal infantil */
    .stButton>button {
        background-color: #FF6B6B;
        color: white !important;
        font-size: 18px;
        font-weight: bold;
        border-radius: 12px;
        border: none;
        padding: 10px 24px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #FF5252;
        color: white !important;
        transform: scale(1.02);
    }
    </style>
""", unsafe_allow_html=True)

# 2. Frase motivadora e Encabezado
st.markdown("""
    <div style="background: linear-gradient(135deg, #FFE66D, #FFD166); padding: 18px; border-radius: 20px; text-align: center; margin-bottom: 25px; box-shadow: 0px 4px 10px rgba(0,0,0,0.3);">
        <h3 style="color: #2B2D42 !important; margin:0; font-family: 'Comic Sans MS', sans-serif;">🌈 "Todo niño es un artista. El secreto es mantener la magia cuando crecemos." — Pablo Picasso 🚀</h3>
    </div>
""", unsafe_allow_html=True)

st.title("🌟 ¡El Lienzo Mágico de las Historias! 🎨")
st.write("Dibuja lo que te imagines, ingresa tu clave mágica y ¡descubre la calificación de tu obra junto a un cuento genial!")

# Función para codificar la imagen en Base64
def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except FileNotFoundError:
        return None

# 3. Barra Lateral para la Herramienta de Dibujo
with st.sidebar:
    st.header("🛠️ Tu Caja de Herramientas")
    
    drawing_mode = st.selectbox(
        "Herramienta:",
        ("freedraw", "line", "rect", "circle"),
        format_func=lambda x: {
            "freedraw": "✏️ Lápiz Mágico",
            "line": "📏 Línea Recta",
            "rect": "⬛ Cuadrado",
            "circle": "🔴 Círculo"
        }.get(x, x)
    )
    
    stroke_width = st.slider('Grosor del pincel 🖌️', 2, 40, 10)
    stroke_color = st.color_picker("Color de la pintura 🎨", "#FF6B6B")
    bg_color = st.color_picker("Color de la hoja 📄", "#FFFFFF")

# 4. Sección Principal (Layout Centrado en Pasos)

# PASO 1: Campo para la Clave API
st.markdown("### 🔑 Paso 1: Ingresa tu Clave Mágica (OpenAI API Key)")
ke = st.text_input('Ingresa tu API Key para activar la magia:', type="password", placeholder="sk-...", key="input_api_key")

os.environ['OPENAI_API_KEY'] = ke
api_key = os.environ.get('OPENAI_API_KEY')

if not api_key:
    st.info("💡 Necesitas ingresar tu API key aquí arriba para que la máquina pueda calificar tu dibujo.")

st.divider()

# PASO 2: El Lienzo
st.markdown("### 🖼️ Paso 2: ¡Dibuja tu Obra de Arte!")

canvas_result = st_canvas(
    fill_color="rgba(255, 230, 109, 0.4)",
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=380,
    width=600,
    drawing_mode=drawing_mode,
    key="canvas_infantil_key",
)

analyze_button = st.button("🚀 ¡Analizar mi dibujo y crear historia!", use_container_width=True)

# 5. Sección de Resultados
if analyze_button:
    if not api_key:
        st.error("⚠️ ¡Falta la clave! Por favor escribe tu OpenAI API Key en el paso 1.")
    else:
        # Validación de trazos en el lienzo
        has_drawings = False
        img_data = None
        
        if canvas_result is not None:
            if canvas_result.json_data is not None:
                objects = canvas_result.json_data.get("objects", [])
                if len(objects) > 0:
                    has_drawings = True
            try:
                img_data = canvas_result.image_data
            except Exception:
                img_data = None

        if has_drawings or (img_data is not None and np.any(img_data)):
            with st.spinner("🧙‍♂️ El mago de los cuentos está observando tu dibujo..."):
                try:
                    # Guardar la imagen del canvas
                    input_numpy_array = np.array(canvas_result.image_data)
                    input_image = Image.fromarray(input_numpy_array.astype('uint8'), 'RGBA').convert('RGB')
                    input_image.save('img.png')
                    
                    base64_image = encode_image_to_base64("img.png")
                    
                    # Prompt formateado asegurando compatibilidad UTF-8
                    prompt_text = (
                        "Eres un narrador amable, divertido y entusiasta para ninos. "
                        "Observa este dibujo infantil y responde en espanol con la siguiente estructura: "
                        "1. Dales una calificacion muy positiva en estrellas (ejemplo: 5 / 5 estrellas). "
                        "2. Dales un titulo divertido a su medalla de artista (ej. Medalla de Gran Creador de Dragones). "
                        "3. Describe de forma corta y divertida que ves en el dibujo. "
                        "4. Escribe un cuento magico corto (maximo 2 parrafos) adaptado para ninos basado en lo que dibujaron."
                    )
                    
                    client = OpenAI(api_key=api_key)
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": prompt_text},
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/png;base64,{base64_image}",
                                        },
                                    },
                                ],
                            }
                        ],
                        max_tokens=600,
                    )
                    
                    resultado = response.choices[0].message.content
                    
                    st.balloons()
                    st.success("¡Tu cuento y calificación están listos!")
                    
                    # Contenedor visual para mostrar el resultado
                    st.markdown(f"""
                        <div style="background-color: #1E293B; padding: 25px; border-radius: 15px; border: 2px solid #38BDF8; color: #F8FAFC;">
                            {resultado}
                        </div>
                    """, unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"¡Ups! Ocurrió un error al procesar la imagen: {e}")
        else:
            st.warning("🎨 ¡El lienzo está vacío! Dibuja algo antes de presionar el botón.")
