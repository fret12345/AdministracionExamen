import requests
from typing import List
from src.ports.financial_repository import FinancialRepository
from src.domain.models import SiboifRecord
from src.domain.exceptions import ApiCaidaError

class ApiFinancialAdapter(FinancialRepository):
    """
    Adaptador de salida para consumir datos financieros a través de una API web.
    
    Principios de diseño:
    - SRP: Su única responsabilidad es la comunicación HTTP e infraestructura de red externa.
    - LSP: Puede reemplazar y ser utilizado en cualquier lugar que espere un FinancialRepository.
    """
    def __init__(self, url: str = "http://127.0.0.1:8000/api/siboif"):
        self.url = url

    def get_all(self) -> List[SiboifRecord]:
        """
        Consume la API externa y mapea la respuesta a entidades de dominio.
        Normaliza cualquier error de red o HTTP a la excepción del dominio ApiCaidaError.
        """
        try:
            response = requests.get(self.url, timeout=2.0)
            response.raise_for_status()
            data = response.json()
            
            records = []
            for item in data:
                # Inicializa el modelo validando y mapeando el diccionario de la API
                records.append(SiboifRecord(**item))
            return records
        except (requests.RequestException, ValueError, KeyError) as e:
            # Traducimos errores de infraestructura HTTP o formato JSON a un error de dominio de API caída
            raise ApiCaidaError(
                f"Error al consumir la API externa de Intendencia de Bancos: {e}"
            ) from e
