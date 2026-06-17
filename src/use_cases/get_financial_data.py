from typing import List, Tuple
from src.ports.financial_repository import FinancialRepository
from src.domain.models import SiboifRecord
from src.domain.exceptions import ApiCaidaError

class ObtenerDatosSiboifUseCase:
    def __init__(self, api_adapter: FinancialRepository, sqlite_adapter: FinancialRepository):
        self.api_adapter = api_adapter
        self.sqlite_adapter = sqlite_adapter

    def ejecutar(self) -> Tuple[List[SiboifRecord], bool]:
        """
        Ejecuta el caso de uso para obtener los datos financieros de Siboif.
        
        Lógica de Fallback:
        1. Intenta consumir primero la API externa a través de api_adapter.
        2. Si falla y se lanza ApiCaidaError, captura la excepción e
           inmediatamente cambia de forma transparente a usar el sqlite_adapter
           para recuperar los datos de Siboif.db local.
        
        Retorna:
            Tuple[List[SiboifRecord], bool]:
                - La lista de registros financieros del dominio.
                - Un booleano: True si se activó el fallback (Modo Offline), False si fue exitoso por API.
        """
        try:
            records = self.api_adapter.get_all()
            return records, False
        except ApiCaidaError:
            records = self.sqlite_adapter.get_all()
            return records, True
        except Exception as e:
            # En caso de otro error inesperado de infraestructura de API, también reintentar local
            try:
                records = self.sqlite_adapter.get_all()
                return records, True
            except Exception as inner_e:
                raise inner_e
