import os
import base64
import random
import numpy as np
from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas
import openai
from openai import OpenAI

# 1. Configuración de la página e Interfaz Infantil
st.set_page_config(page_title="¡Pequeños Artistas! 🎨✨", page_icon="🎨", layout="wide")

# Frase motivadora al inicio
st.markdown("""
    <div style="background-color: #FFE66D; padding: 15px; border-radius: 15px; text-align: center; margin-bottom: 20px;">
        <h3 style="color: #2B2D42; margin:0;">🌈 "Todo niño es un artista. El secreto es mantener la magia cuando crecemos." — Pablo Picasso 🚀</h3>
    </div>
""", unsafe_allow_html=True)

st.title("🌟 ¡El Lienzo Mágico de las Historias! 🎨")
st.write("Dibuja lo que te imagines, ingresa tu clave y ¡la IA evaluará tu arte y te contará una historia genial!")

# Function to encode image to base64
def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except FileNotFoundError:
        return None

# 2. Barra Lateral Infantil
with st.sidebar:
    st.header("🛠️ Tu Caja de Colores")
    
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
    
    stroke_width = st.slider('Grosor del pincel 🖌️', 2, 40, 12)
    stroke_color = st.color_picker("Color de la pintura 🎨", "#FF6B6B")
    bg_color = st.color_picker("Color de la hoja 📄", "#FFFFFF")
    
    st.divider()
    st.subheader("🔑 Configuración")
    ke = st.text_input('Ingresa tu API Key de OpenAI', type="password")

# Asignar API Key
os.environ['OPENAI_API_KEY'] = ke
api_key = os.environ.get('OPENAI_API_KEY')

# 3. Disposición Principal
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("🖼️ ¡Dibuja aquí tu obra de arte!")
    canvas_result = st_canvas(
        fill_color="rgba(255, 230, 109, 0.4)",
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color=bg_color,
        height=350,
        width=500,
        drawing_mode=drawing_mode,
        key="canvas_infantil_key",
    )
    
    analyze_button = st.button("🚀 ¡Analizar mi dibujo y contar historia!", type="primary", use_container_width=True)

with col2:
    st.subheader("⭐ La Magia del Cuento")
    
    if analyze_button:
        if not api_key:
            st.warning("🔑 Por favor ingresa tu OpenAI API Key en la barra lateral para continuar.")
        else:
            # Validación segura para evitar el RuntimeError del lienzo
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
                        # Guardar imagen temporalmente
                        input_numpy_array = np.array(canvas_result.image_data)
                        input_image = Image.fromarray(input_numpy_array.astype('uint8'), 'RGBA').convert('RGB')
                        input_image.save('img.png')
                        
                        base64_image = encode_image_to_base64("img.png")
                        
                        # Prompt infantil ajustado con sistema de calificación
                        prompt_text = (
                            "Eres un narrador amable, divertido y entusiasta para niños. "
                            "Observa este dibujo infantil y responde en español con la siguiente estructura: "
                            "1. Dales una calificación muy positiva en estrellas ⭐ (ejemplo: ⭐⭐⭐⭐⭐ / 5 estrellas). "
                            "2. Dales un título divertido a su medalla de artista (ej. ¡Medalla de Gran Creador de Dragones!). "
                            "3. Describe de forma corta y divertida qué ves en el dibujo. "
                            "4. Escribe un cuento mágico muy corto (máximo 2 párrafos) basado en lo que dibujaron."
                        )
                        
                        # Llamada a la API de OpenAI
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
                        st.success("¡Tu cuento está listo!")
                        st.markdown(resultado)

                    except Exception as e:
                        st.error(f"¡Ups! Ocurrió un error al analizar el dibujo: {e}")
            else:
                st.warning("🎨 ¡El lienzo está vacío! Dibuja algo antes de presionar el botón.")
