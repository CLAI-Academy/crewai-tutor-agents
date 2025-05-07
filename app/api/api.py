from fastapi import FastAPI, Body, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware 

import json
from app.utils.websockets.manager import ws_manager
import asyncio
import uuid

# Importando RouterFlow del archivo existente
from app.main import RouterFlow

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # ← vale sólo para local o staging
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Modelo para recibir el mensaje JSON
class MessageInput(BaseModel):
    message: str
    image: Optional[str] = None

# Creamos una única instancia del flow para toda la aplicación
flow = RouterFlow()

@app.get("/ping")
async def pong():
    return"pong"

@app.post("/conversation")
async def conversation(input_data: MessageInput = Body(...)):
    """
    Endpoint para procesar un mensaje y devolver una respuesta.
    
    Recibe:
    - message: Texto del mensaje del usuario
    - image: URL de la imagen en Supabase Storage (opcional)
    """
    # Actualizar el estado con el mensaje del usuario y la URL de la imagen (si existe)
    flow.state.user_input = input_data.message
    flow.state.image = input_data.image if input_data.image else ""
    
    # Procesar la conversación
    response = await flow.kickoff_async()
    print(flow.state)
    
    # Comprobar el tipo de respuesta
    if hasattr(response, 'raw'):
        return {"response": response.raw}
    else:
        # Si response es una cadena o de otro tipo sin atributo raw
        return {"response": response}

# Nuevo endpoint WebSocket
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Endpoint WebSocket para comunicación en tiempo real.
    """
    # Generar un ID único para el cliente
    client_id = str(uuid.uuid4())
    
    # Aceptar la conexión
    await ws_manager.connect(websocket, client_id)
    
    # Confirmar conexión establecida
    await websocket.send_json({
        "connected": True,
        "client_id": client_id
    })
    
    try:
        while True:
            # Esperar mensajes del cliente
            data = await websocket.receive_text()
            
            try:
                # Decodificar JSON
                message_data = json.loads(data)
                
                # Si es una consulta, procesarla
                if "message" in message_data:
                    user_message = message_data.get("message", "")
                    image_data = message_data.get("image", "")
                    
                    # Iniciar flow en background para no bloquear el WebSocket
                    asyncio.create_task(
                        process_flow_with_websocket(client_id, user_message, image_data)
                    )
                else:
                    await websocket.send_json({
                        "error": "Formato de mensaje no válido"
                    })
                    
            except json.JSONDecodeError:
                await websocket.send_json({
                    "error": "Formato JSON inválido"
                })
            except Exception as e:
                print(f"Error en websocket_endpoint para cliente {client_id}: {e}")
                await websocket.send_json({
                    "error": f"Error inesperado: {str(e)}"
                })
                
    except WebSocketDisconnect:
        # Cliente desconectado
        ws_manager.disconnect(websocket)
        print(f"Cliente {client_id} desconectado")

async def process_flow_with_websocket(client_id: str, user_message: str, image_data: str = ""):
    """
    Procesa un mensaje usando el flujo RouterFlow y envía actualizaciones por WebSocket.
    """
    try:
        # Crear una nueva instancia de RouterFlow para este cliente
        # (o usa la instancia global si prefieres))
        local_flow = RouterFlow()
        
        # Actualizar el estado
        local_flow.state.user_input = user_message
        local_flow.state.image = image_data
        local_flow.state.client_id = client_id  # Añadir client_id al estado
        
        # Iniciar con estado "pensando"
        await ws_manager.send_to_client(client_id, {
            "status": "pensando"
        })
        
        # Ejecutar el flujo
        result = await local_flow.kickoff_async()
        
        # Enviar estado completado y resultado
        await ws_manager.send_to_client(client_id, {
            "status": "completed",
            "resultado": result.raw if hasattr(result, 'raw') else result
        })
        
    except Exception as e:
        print(f"Error en process_flow_with_websocket para cliente {client_id}: {e}")
        # Notificar error al cliente
        await ws_manager.send_to_client(client_id, {
            "error": f"Error en el procesamiento: {str(e)}"
        })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)