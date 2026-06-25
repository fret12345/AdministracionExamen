from pydantic import BaseModel
from typing import Optional

class SiboifRecord(BaseModel):
    """
    Entidad de dominio que representa un registro de SIBOIF.
    Representa fielmente el esquema del dominio sin dependencias de infraestructura.
    """
    intendencia: str
    tipo_institucion: str
    institucion: str
    tipo_reporte: str
    fecha: str
    orden: int
    variable1: str
    valor1: float
    Anio: int
    Mes: int
    variable2: Optional[str] = None
    variable3: Optional[str] = None
    valor2: Optional[float] = None
