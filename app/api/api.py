from fastapi import FastAPI, Body
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware 

# Importando RouterFlow del archivo existente
from app.main import RouterFlow

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080/"],  # URL de tu frontend
    allow_credentials=True,
    allow_methods=[""],  # Permitir todos los métodos HTTP
    allow_headers=[""],  # Permitir todas las cabeceras
)


# Modelo para recibir el mensaje JSON
class MessageInput(BaseModel):
    message: str

# Creamos una única instancia del flow para toda la aplicación
flow = RouterFlow()

@app.get("/ping")
async def pong():
    return"pong"

@app.post("/conversation")
async def conversation(input_data: MessageInput = Body(...)):
    """
    Endpoint para procesar un mensaje y devolver una respuesta.
    Acepta un JSON en el body con el campo 'message'.
    """
    # Actualizar el estado con el mensaje del usuario
    flow.state.user_input = input_data.message
    
    # Procesar la conversación
    response = await flow.kickoff_async()
    print(flow.state)
    # Devolver directamente la respuesta
    return {"response": response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)