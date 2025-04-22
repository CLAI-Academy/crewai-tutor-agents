import os
import base64
import uuid
from typing import Optional

def process_temp_image(base64_image: Optional[str], upload_dir: str = "temp_uploads") -> Optional[str]:
    """
    Procesa una imagen en base64, la guarda temporalmente y devuelve su ruta.
    
    Args:
        base64_image: String en formato base64 o None si no hay imagen
        upload_dir: Directorio donde se guardarán las imágenes temporales
        
    Returns:
        La ruta del archivo temporal o None si no hay imagen
    """
    # Verificar si hay una imagen válida
    if not base64_image or not isinstance(base64_image, str) or not base64_image.startswith('data:image'):
        return None
        
    # Asegurar que el directorio existe
    os.makedirs(upload_dir, exist_ok=True)
    
    # Procesar la imagen
    try:
        # Separar el header del contenido base64
        header, encoded = base64_image.split(",", 1)
        # Determinar formato de archivo
        img_format = header.split("/")[1].split(";")[0]
        
        # Crear nombre de archivo único
        filename = f"{uuid.uuid4()}.{img_format}"
        image_path = os.path.join(upload_dir, filename)
        
        # Guardar archivo
        with open(image_path, "wb") as img_file:
            img_file.write(base64.b64decode(encoded))
        
        return image_path
        
    except Exception as e:
        print(f"Error procesando la imagen: {e}")
        return None


class TempImage:
    """
    Clase para manejar imágenes temporales con el patrón de contexto (with statement)
    para asegurar que se eliminen después de usarse.
    """
    def __init__(self, base64_image: Optional[str], upload_dir: str = "temp_uploads"):
        self.base64_image = base64_image
        self.upload_dir = upload_dir
        self.image_path = None
        
    def __enter__(self) -> Optional[str]:
        self.image_path = process_temp_image(self.base64_image, self.upload_dir)
        return self.image_path
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Eliminar la imagen temporal si existe
        if self.image_path and os.path.exists(self.image_path):
            try:
                os.remove(self.image_path)
                print(f"Imagen temporal eliminada: {self.image_path}")
            except Exception as e:
                print(f"Error al eliminar la imagen temporal: {e}")