#!/usr/bin/env python3
"""
Test script for validating structured JSON outputs from the hair diagnostic agents.
"""
import json
import os
import sys
from pprint import pprint

# Add the project root to the path to import app modules
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)
print(f"Current directory: {current_dir}")
print(f"Project root added to path: {project_root}")

try:
    from app.crews.diagno_crew.diagno_crew import DiagnosticCrew
    print("Successfully imported DiagnosticCrew")
except ImportError as e:
    print(f"Error importing DiagnosticCrew: {e}")
    # Try alternative import path
    try:
        from crews.diagno_crew.diagno_crew import DiagnosticCrew
        print("Successfully imported DiagnosticCrew using relative import")
    except ImportError as e2:
        print(f"Error with alternative import: {e2}")
        sys.exit(1)

def test_json_parsing():
    """Test the JSON parsing functionality in DiagnosticCrew"""
    
    # Sample raw output that might come from the LLM
    sample_hair_diagno_output = """
    Aquí está mi análisis del cabello:
    
    ```json
    {
      "cliente": {
        "fecha_diagnostico": "2025-05-12"
      },
      "cabello": {
        "grosor": "fino",
        "longitud": "melena_media",
        "altura_tono": {
          "valor": 6,
          "descripcion": "Rubio oscuro"
        },
        "canas": {
          "porcentaje": 25,
          "descripcion": "Canas distribuidas principalmente en la zona frontal"
        },
        "matiz": "dorado",
        "textura": "ondulado",
        "alteraciones": {
          "mechas": true,
          "tecnica_usada": "balayage",
          "porosidad": {
            "minima": 2,
            "maxima": 4,
            "descripcion": "Porosidad media en medios, alta en puntas"
          },
          "tratamientos": {
            "planchado": true,
            "lisado_quimico": false,
            "moldeado": false,
            "decolorado": true,
            "otro": "Tratamiento de queratina hace 3 meses"
          }
        },
        "analisis_color": {
          "raices": "Tono base 6 con reflejos dorados",
          "medios": "Tono 7 con mechas más claras",
          "puntas": "Tono 8-9 con signos de decoloración"
        },
        "condicion_general": "Cabello con signos de estrés térmico, puntas abiertas y medios porosos"
      },
      "imagen_url": "https://example.com/image.jpg",
      "observaciones": "Se recomienda tratamiento hidratante y reconstrucción de keratina"
    }
    ```
    """
    
    sample_color_suggestion_output = """
    Basado en el diagnóstico previo, aquí está mi recomendación:
    
    ```json
    {
      "coloracion": {
        "fecha": "2025-05-12",
        "formulacion": {
          "nombre_mezcla": "Cobertura nutritiva balanceada",
          "tipo_mezcla": "Permanente con tratamiento",
          "marca": "Wella Professionals",
          "grama": "60",
          "componentes": [
            {
              "color": "6/0",
              "gramos": "30"
            },
            {
              "color": "6/3",
              "gramos": "15"
            },
            {
              "color": "6/7",
              "gramos": "15"
            }
          ],
          "oxidante": {
            "volumen": "20",
            "gramos_ml": "60"
          },
          "tiempo_exposicion": "35"
        },
        "aplicacion": {
          "raices": {
            "color": "6/0 + 6/3 + 6/7",
            "porcentaje_porosidad": 2
          },
          "medios": {
            "color": "7/0 + 7/3",
            "porcentaje_porosidad": 3
          },
          "puntas": {
            "color": "8/0 + 8/3 (10 min)",
            "porcentaje_porosidad": 4
          }
        },
        "color_obtenido": "Rubio oscuro dorado neutro con reflejos cálidos",
        "reequilibrio_ph": {
          "champu_acido": true,
          "acondicionador": true,
          "plex": true,
          "otro": "Mascarilla de proteínas"
        },
        "recomendaciones": [
          "Usar champú y acondicionador para cabellos teñidos",
          "Aplicar protector térmico antes de usar herramientas de calor",
          "Tratamiento hidratante semanal"
        ],
        "mantenimiento": {
          "frecuencia": "cada 4-6 semanas",
          "productos_recomendados": [
            "Wella ColorMotion+ Shampoo",
            "Wella Fusion Intense Repair Mask",
            "Olaplex Nº6 Bond Smoother"
          ]
        }
      },
      "observaciones": "Considerar reducir uso de herramientas térmicas para mejorar la salud capilar"
    }
    ```
    """
    
    crew = DiagnosticCrew(client_id="test_client")
    
    # Test parsing hair diagno output
    print("Testing hair diagnosis output parsing:")
    diagno_parsed = crew.parse_json_output(sample_hair_diagno_output)
    pprint(diagno_parsed)
    print("\nValidating JSON structure...")
    assert "cliente" in diagno_parsed, "Missing 'cliente' field in parsed output"
    assert "cabello" in diagno_parsed, "Missing 'cabello' field in parsed output"
    
    # Test parsing color suggestion output
    print("\n\nTesting color suggestion output parsing:")
    color_parsed = crew.parse_json_output(sample_color_suggestion_output)
    pprint(color_parsed)
    print("\nValidating JSON structure...")
    assert "coloracion" in color_parsed, "Missing 'coloracion' field in parsed output"
    assert "formulacion" in color_parsed["coloracion"], "Missing 'formulacion' field in parsed output"
    
    print("\n✅ All tests passed! The JSON parsing is working correctly.")

if __name__ == "__main__":
    test_json_parsing()
