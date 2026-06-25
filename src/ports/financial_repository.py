from abc import ABC, abstractmethod
from typing import List, Tuple
from src.domain.models import SiboifRecord

class FinancialRepository(ABC):
    """
    Puerto de salida (Outbound Port) para acceder a los datos financieros de SIBOIF.
    Cualquier adaptador de salida de persistencia o servicios web (SQLite, API, CSV) 
    debe implementar esta interfaz de forma completa (LSP).
    """
    @abstractmethod
    def get_all(self) -> List[SiboifRecord]:
        """
        Obtiene todos los registros de Siboif.
        """
        pass

class GetFinancialDataUseCasePort(ABC):
    """
    Puerto de entrada (Inbound Port) que expone el caso de uso de obtención de datos.
    Permite desacoplar adaptadores de entrada (como Streamlit UI) de la implementación concreta
    del caso de uso, cumpliendo con el Principio de Inversión de Dependencias (DIP).
    """
    @abstractmethod
    def ejecutar(self) -> Tuple[List[SiboifRecord], bool]:
        """
        Ejecuta el caso de uso de obtención de datos.
        Retorna la lista de registros y un indicador booleano de si se activó el fallback local.
        """
        pass
