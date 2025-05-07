import yaml

def list_agents(agents_config):
    """
    Obtiene la lista de nombres de agentes de un diccionario o un archivo YAML.
    
    Args:
        agents_config: Diccionario con configuración de agentes o ruta al archivo YAML
    
    Returns:
        Lista de nombres de agentes
    """
    # Si es una cadena, asumimos que es una ruta y cargamos el archivo
    if isinstance(agents_config, str):
        try:
            with open(agents_config, 'r') as file:
                agents_config = yaml.safe_load(file)
        except Exception as e:
            print(f"Error al cargar archivo de agentes: {e}")
            return []
    
    # Devolver lista de claves
    return list(agents_config.keys())