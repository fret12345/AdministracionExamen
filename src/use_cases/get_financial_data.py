from typing import List, Tuple, Optional
from src.ports.financial_repository import FinancialRepository, GetFinancialDataUseCasePort
from src.domain.models import SiboifRecord
from src.domain.exceptions import DomainError

class ObtenerDatosSiboifUseCase(GetFinancialDataUseCasePort):
    def __init__(
        self, 
        primary_repository: Optional[FinancialRepository] = None, 
        fallback_repository: Optional[FinancialRepository] = None,
        **kwargs
    ):
        """
        Caso de uso para orquestar la obtención de datos de SIBOIF.
        
        Principios de diseño aplicados:
        - DIP: Depende de la abstracción FinancialRepository, no de clases concretas de infraestructura.
        - OCP: Se puede inyectar cualquier adaptador que implemente la interfaz FinancialRepository sin modificar este código.
        - SRP: Solo se encarga de coordinar el flujo y la lógica de fallback transparente de la consulta.
        
        Soporta compatibilidad de parámetros antiguos ('api_adapter', 'sqlite_adapter') para no romper pruebas externas.
        """
        self.primary_repository = primary_repository or kwargs.get('api_adapter')
        self.fallback_repository = fallback_repository or kwargs.get('sqlite_adapter')

        if not self.primary_repository:
            raise ValueError(
                "Debe especificarse al menos un repositorio principal para el caso de uso."
            )

    def ejecutar(self) -> Tuple[List[SiboifRecord], bool]:
        """
        Ejecuta el caso de uso para obtener los datos financieros de Siboif.
        
        Lógica de Fallback robusta:
        1. Intenta consumir primero el repositorio principal (ej. API).
        2. Si falla (lanzando cualquier excepción o DomainError), conmuta automáticamente
           y de forma transparente a usar el repositorio de respaldo (ej. SQLite local).
        3. Si no hay repositorio de respaldo configurado, propaga la excepción original.
        """
        try:
            records = self.primary_repository.get_all()
            return records, False
        except Exception as e:
            if not self.fallback_repository:
                raise e
            
            try:
                records = self.fallback_repository.get_all()
                return records, True
            except Exception as inner_e:
                # Si el de respaldo también falla, propagamos el error de la infraestructura interna
                raise inner_e
