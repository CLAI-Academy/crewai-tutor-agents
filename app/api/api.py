from fastapi import FastAPI, Body
from pydantic import BaseModel
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware 

# Importando RouterFlow del archivo existente
from app.main import RouterFlow

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "https://preview--charla-amiga-rapida.lovable.app", "https://lovable.dev/projects/b51d96c6-03e4-4145-af36-6fbe11fd5c39"],  # URL sin barra al final
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Métodos permitidos
    allow_headers=["Content-Type", "Authorization"],  # Cabeceras permitidas
)

# Modelo para recibir el mensaje JSON
class MessageInput(BaseModel):
    message: str
    image: str = ""
# Creamos una única instancia del flow para toda la aplicación
flow = RouterFlow()

@app.get("/ping")
async def pong():
    return"pong"

from fastapi import FastAPI, Body

# Importar la utilidad que creamos
from app.utils.image_utils import TempImage

# Tu código existente aquí...
# Creamos una única instancia del flow para toda la aplicación
flow = RouterFlow()

class MessageInput(BaseModel):
    message: str
    image: Optional[str] = None

@app.post("/conversation")
async def conversation(input_data: MessageInput = Body(...)):
    """
    Endpoint para procesar un mensaje y devolver una respuesta.
    """
    # Usar el administrador de contexto para manejar la imagen temporal
    with TempImage(input_data.image) as image_path:
        # Actualizar el estado con el mensaje del usuario y la ruta de la imagen (si existe)
        flow.state.user_input = input_data.message
        flow.state.image_path = image_path if image_path else ""
        
        # Procesar la conversación
        response = await flow.kickoff_async()
        print(flow.state)
        
         # Comprobar el tipo de respuesta
        if hasattr(response, 'raw'):
            return {"response": response.raw}
        else:
            # Si response es una cadena o de otro tipo sin atributo raw
            return {"response": response}
    # La imagen se elimina automáticamente al salir del bloque "with"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)