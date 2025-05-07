# app/utils/websockets/manager.py
import asyncio
from fastapi import WebSocket
from typing import List, Dict, Any, Optional

class WebSocketManager:
    """
    Gestor de conexiones WebSocket para comunicación en tiempo real.
    Implementado como singleton para asegurar una única instancia en toda la aplicación.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WebSocketManager, cls).__new__(cls)
            cls._instance.active_connections = []
            cls._instance.connection_info = {}
        return cls._instance

    async def connect(self, websocket: WebSocket, client_id: Optional[str] = None):
        """
        Establece una nueva conexión WebSocket.
        
        Args:
            websocket: La conexión WebSocket a establecer
            client_id: Identificador opcional del cliente
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        
        # Guardar información del cliente si se proporciona un ID
        if client_id:
            self.connection_info[websocket] = {
                "client_id": client_id,
                "connected_at": asyncio.get_event_loop().time()
            }
    
    def disconnect(self, websocket: WebSocket):
        """
        Desconecta una conexión WebSocket.
        
        Args:
            websocket: La conexión WebSocket a desconectar
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        if websocket in self.connection_info:
            del self.connection_info[websocket]
    
    async def send_to_client(self, client_id: str, message: Dict[str, Any]):
        """
        Envía un mensaje a un cliente específico por su ID.
        
        Args:
            client_id: ID del cliente al que enviar el mensaje
            message: Mensaje a enviar (diccionario que se convertirá a JSON)
        """
        disconnected = []
        for connection, info in self.connection_info.items():
            if info.get("client_id") == client_id:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.append(connection)
        
        # Limpiar conexiones desconectadas
        for conn in disconnected:
            self.disconnect(conn)
    
    def get_connection_count(self) -> int:
        """
        Obtiene el número de conexiones activas.
        
        Returns:
            Número de conexiones activas
        """
        return len(self.active_connections)


# Crear una instancia global para usar en toda la aplicación
ws_manager = WebSocketManager()