import sqlite3
from typing import List
from src.ports.financial_repository import FinancialRepository
from src.domain.models import SiboifRecord

class SqliteFinancialAdapter(FinancialRepository):
    def __init__(self, db_path: str = "Siboif.db"):
        self.db_path = db_path

    def get_all(self) -> List[SiboifRecord]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            # Consulta JOIN optimizada para reconstruir la estructura denormalizada
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
                    Mes=r[9],
                    variable2=None,
                    variable3=None,
                    valor2=None
                ))
            return records
        finally:
            conn.close()
