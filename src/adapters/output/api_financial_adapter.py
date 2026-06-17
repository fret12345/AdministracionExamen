import requests
from typing import List
from src.ports.financial_repository import FinancialRepository
from src.domain.models import SiboifRecord
from src.domain.exceptions import ApiCaidaError

class ApiFinancialAdapter(FinancialRepository):
    def __init__(self, url: str = "http://127.0.0.1:8000/api/siboif"):
        self.url = url

    def get_all(self) -> List[SiboifRecord]:
        try:
            # Petición HTTP a la API externa
            response = requests.get(self.url, timeout=2.0)
            response.raise_for_status()
            data = response.json()
            
            # Mapear datos recibidos a entidades de dominio
            records = []
            for item in data:
                records.append(SiboifRecord(**item))
            return records
        except Exception as e:
            # Lanza obligatoriamente ApiCaidaError al fallar la conexión
            raise ApiCaidaError(f"Error al consumir la API externa de Intendencia de Bancos: {e}") from e
