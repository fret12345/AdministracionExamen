from pydantic import BaseModel
from typing import Optional

class SiboifRecord(BaseModel):
    intendencia: str
    tipo_institucion: str
    institucion: str
    tipo_reporte: str
    fecha: str
    orden: int
    variable1: str
    variable2: Optional[str] = None
    variable3: Optional[str] = None
    valor1: float
    valor2: Optional[float] = None
    Anio: int
    Mes: int
