from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class RiskLevel(str, Enum):
    BAJO = "Bajo"  # Inversiones más seguras, menor rentabilidad
    MEDIO = "Medio"  # Equilibrio entre riesgo y rentabilidad
    ALTO = "Alto"  # Mayor riesgo, mayor rentabilidad potencial
    MUY_ALTO = "Muy Alto"  # Máximo riesgo, máxima rentabilidad potencial

class AssetClass(str, Enum):
    ACCIONES = "Acciones"  # Inversión en empresas
    CRIPTOMONEDAS = "Criptomonedas"  # Monedas digitales como Bitcoin
    FONDOS = "Fondos"  # Inversión colectiva gestionada por expertos
    BONOS = "Bonos"  # Préstamos a empresas o gobiernos
    INMOBILIARIO = "Inmobiliario"  # Inversión en propiedades

class AssetAllocation(BaseModel):
    tipo_inversion: AssetClass = Field(..., description="Tipo de inversión (acciones, criptomonedas, etc.)")
    nombre: str = Field(..., description="Nombre de la inversión (ej: Bitcoin, Apple, etc.)")
    porcentaje: float = Field(..., description="Porcentaje de tu dinero que se invertirá aquí")
    rentabilidad_esperada: float = Field(..., description="Rentabilidad que podrías obtener en un año")
    ingreso_mensual: float = Field(..., description="Dinero que podrías ganar cada mes")
    descripcion: str = Field(..., description="Explicación simple de esta inversión")
    ventajas: List[str] = Field(..., description="Beneficios de esta inversión")
    desventajas: List[str] = Field(..., description="Riesgos o desventajas a considerar")

class InvestmentScenario(BaseModel):
    nombre_escenario: str = Field(..., description="Nombre fácil de entender para esta estrategia")
    nivel_riesgo: RiskLevel = Field(..., description="Nivel de riesgo de esta estrategia")
    inversion_total: float = Field(..., description="Cantidad total de dinero a invertir")
    inversiones: List[AssetAllocation] = Field(..., description="Lista de inversiones propuestas")
    explicacion: str = Field(..., description="Explicación clara de por qué esta estrategia podría funcionar")
    pasos_a_seguir: List[str] = Field(..., description="Pasos simples para implementar esta estrategia")
    tiempo_recomendado: str = Field(..., description="Cuánto tiempo se recomienda mantener esta inversión")
    objetivo: str = Field(..., description="Qué se espera lograr con esta estrategia")

class ScenarioComparison(BaseModel):
    nombre_escenario: str = Field(..., description="Nombre de la estrategia")
    nivel_riesgo: RiskLevel = Field(..., description="Nivel de riesgo")
    ganancia_total: float = Field(..., description="Cuánto podrías ganar en total")
    ingreso_mensual: float = Field(..., description="Cuánto podrías ganar cada mes")
    recomendado: bool = Field(..., description="Si esta estrategia es recomendada para ti")
    razon_recomendacion: str = Field(..., description="Por qué se recomienda o no esta estrategia")

class OptimizedInvestmentReport(BaseModel):
    escenarios: List[InvestmentScenario] = Field(..., description="Diferentes estrategias de inversión propuestas")
    comparaciones: List[ScenarioComparison] = Field(..., description="Comparación entre las diferentes estrategias")
    analisis_mercado: Dict[str, Any] = Field(..., description="Situación actual del mercado explicada de forma sencilla")
    recomendaciones: Dict[str, Any] = Field(..., description="Consejos y recomendaciones finales")
    preguntas_frecuentes: List[Dict[str, str]] = Field(..., description="Preguntas comunes y sus respuestas")
    consejos_practicos: List[str] = Field(..., description="Consejos útiles para empezar a invertir")