import sqlite3
from typing import List
from src.ports.financial_repository import FinancialRepository
from src.domain.models import SiboifRecord
from src.domain.exceptions import DatabaseConnectionError

class SqliteFinancialAdapter(FinancialRepository):
    """
    Adaptador de salida para la persistencia local en una base de datos SQLite.
    
    Principios de diseño:
    - SRP: Su única responsabilidad es comunicarse con la base de datos local y ejecutar consultas SQL.
    - LSP: Sustituye correctamente a FinancialRepository sin alterar el comportamiento esperado por el cliente.
    """
    def __init__(self, db_path: str = "Siboif.db"):
        self.db_path = db_path

    def get_all(self) -> List[SiboifRecord]:
        """
        Consulta la base de datos local SQLite y reconstruye la lista de entidades SiboifRecord.
        Garantiza el cierre seguro de la conexión y mapea errores SQL a excepciones de dominio.
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Consulta JOIN optimizada para reconstruir la estructura del dominio
            cursor.execute("""
                SELECT 
                    i.intendencia,
                    i.tipo_institucion,
                    i.nombre AS institucion,
                    tr.nombre AS tipo_reporte,
                    p.fecha,
                    part.orden,
                    c.nombre AS variable1,
                    part.valor AS valor1,
                    p.anio AS Anio,
                    p.mes AS Mes
                FROM partidas part
                JOIN instituciones i ON part.id_institucion = i.id_institucion
                JOIN tipos_reporte tr ON part.id_tipo_reporte = tr.id_tipo_reporte
                JOIN periodos p ON part.id_periodo = p.id_periodo
                JOIN cuentas c ON part.id_cuenta = c.id_cuenta
            """)
            rows = cursor.fetchall()
            
            records = []
            for r in rows:
                records.append(SiboifRecord(
                    intendencia=r[0],
                    tipo_institucion=r[1],
                    institucion=r[2],
                    tipo_reporte=r[3],
                    fecha=r[4],
                    orden=r[5],
                    variable1=r[6],
                    valor1=r[7],
                    Anio=r[8],
                    Mes=r[9]
                ))
            return records
        except sqlite3.Error as e:
            # Encapsula excepciones de infraestructura SQLite a nivel de dominio
            raise DatabaseConnectionError(
                f"Error de infraestructura de base de datos local al obtener registros: {e}"
            ) from e
        finally:
            if conn is not None:
                conn.close()
