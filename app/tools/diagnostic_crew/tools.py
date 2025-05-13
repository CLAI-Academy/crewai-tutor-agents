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
def analyze_image(image: str, prompt: Optional[str] = "Realiza un diagnóstico capilar detallado de esta imagen. Analiza: grosor del cabello, longitud, altura de tono base (1-10), porcentaje de canas, color natural, matiz, textura, presencia de mechas o tratamientos químicos, porosidad y condición general. Usa terminología técnica profesional de peluquería.") -> str:
    """
    Analiza una imagen de cabello utilizando el modelo GPT-4 Vision de OpenAI para realizar diagnóstico capilar.
    
    Args:
        image: URL de la imagen a analizar
        prompt: Instrucciones específicas para analizar la imagen (opcional)
    
    Returns:
        str: Análisis detallado de la imagen del cabello en formato estructurado
    """
    try:
        # Inicializar el cliente de OpenAI
        client = OpenAI()
        
        # Crear la solicitud a la API con un prompt específico para diagnóstico capilar
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Eres un experto en diagnóstico capilar y colorimetría profesional. Tu tarea es analizar imágenes de cabello y proporcionar un diagnóstico técnico detallado. Debes estructurar tu respuesta para que sea fácilmente convertible a formato JSON."
                },
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
            max_tokens=600  # Aumentado para permitir respuestas más detalladas
        )
        
        # Extraer y retornar la respuesta
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error al analizar la imagen: {str(e)}"
