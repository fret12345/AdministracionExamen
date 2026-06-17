from abc import ABC, abstractmethod
from typing import List
from src.domain.models import SiboifRecord

class FinancialRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[SiboifRecord]:
        """
        Obtiene todos los registros financieros.
        """
        pass
