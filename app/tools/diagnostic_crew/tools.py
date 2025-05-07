from crewai.tools import tool
import http.client
from datetime import datetime
import random
import json
import os

import base64
from openai import OpenAI
from typing import Optional

@tool
def analyze_image(image: str, prompt: Optional[str] = "What is in this image?") -> str:
    """
    Analiza una imagen utilizando el modelo GPT-4 Vision de OpenAI.
    
    Args:
        image_path: Ruta al archivo de imagen a analizar
        prompt: Pregunta o prompt específico para analizar la imagen (opcional)
    
    Returns:
        str: Descripción o análisis de la imagen
    """
    try:
        # Inicializar el cliente de OpenAI
        client = OpenAI()
        
        # # Codificar la imagen en base64
        # def encode_image(image_path):
        #     with open(image_path, "rb") as image_file:
        #         return base64.b64encode(image_file.read()).decode("utf-8")
        
        # # Obtener la imagen en formato base64
        # base64_image = encode_image(image_path)
        
        # Crear la solicitud a la API
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Asegurarse de usar el modelo correcto
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt,
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image
                            },
                        },
                    ],
                }
            ],
            max_tokens=300  # Ajustar según necesidades
        )
        
        # Extraer y retornar la respuesta
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error al analizar la imagen: {str(e)}"
