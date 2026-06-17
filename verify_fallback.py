import sys
from src.domain.models import SiboifRecord
from src.domain.exceptions import ApiCaidaError
from src.ports.financial_repository import FinancialRepository
from src.adapters.output.api_financial_adapter import ApiFinancialAdapter
from src.adapters.output.sqlite_financial_adapter import SqliteFinancialAdapter
from src.use_cases.get_financial_data import ObtenerDatosSiboifUseCase

class MockSuccessfulApiAdapter(FinancialRepository):
    def get_all(self):
        # Retorna una lista con un único registro mockeado
        return [
            SiboifRecord(
                intendencia="Seguros",
                tipo_institucion="Compañía de Seguros",
                institucion="MOCK_SEGUROS",
                tipo_reporte="Balance General",
                fecha="2018-12-31",
                orden=10,
                variable1="Activos",
                valor1=500000.0,
                Anio=2018,
                Mes=12
            )
        ]

def test_sqlite_adapter():
    print("--- [1] Test de SqliteFinancialAdapter ---")
    adapter = SqliteFinancialAdapter(db_path="Siboif.db")
    try:
        records = adapter.get_all()
        print(f"Éxito: Se recuperaron {len(records)} registros desde SQLite.")
        assert len(records) > 0, "No se recuperó ningún registro."
        assert isinstance(records[0], SiboifRecord), "Los registros no son del tipo SiboifRecord."
        print(f"Muestra del primer registro: {records[0]}")
        print("Test 1: PASADO\n")
        return True
    except Exception as e:
        print(f"Error en Test 1: {e}")
        return False

def test_api_adapter_failure():
    print("--- [2] Test de ApiFinancialAdapter (Falla esperada) ---")
    # Apuntamos a un puerto donde no hay ningún servicio para forzar el fallo
    adapter = ApiFinancialAdapter(url="http://127.0.0.1:9999/api/siboif")
    try:
        adapter.get_all()
        print("Error: El adaptador no lanzó excepción en una URL caída.")
        return False
    except ApiCaidaError as e:
        print(f"Éxito: Se capturó la excepción esperada 'ApiCaidaError': {e}")
        print("Test 2: PASADO\n")
        return True
    except Exception as e:
        print(f"Error: Se lanzó una excepción inesperada: {e}")
        return False

def test_use_case_fallback():
    print("--- [3] Test de Fallback en el Caso de Uso (API caída -> SQLite local) ---")
    api_adapter = ApiFinancialAdapter(url="http://127.0.0.1:9999/api/siboif")
    sqlite_adapter = SqliteFinancialAdapter(db_path="Siboif.db")
    use_case = ObtenerDatosSiboifUseCase(api_adapter=api_adapter, sqlite_adapter=sqlite_adapter)
    
    try:
        records, es_fallback = use_case.ejecutar()
        print(f"Éxito: El caso de uso se ejecutó correctamente.")
        print(f"¿Se activó el Fallback?: {es_fallback}")
        print(f"Total registros obtenidos: {len(records)}")
        assert es_fallback is True, "El fallback debería haberse activado (es_fallback = True)."
        assert len(records) > 0, "Debería haber registros recuperados del fallback de SQLite."
        print("Test 3: PASADO\n")
        return True
    except Exception as e:
        print(f"Error en Test 3: {e}")
        return False

def test_use_case_success_no_fallback():
    print("--- [4] Test de Éxito en el Caso de Uso (API exitosa -> Sin fallback) ---")
    api_adapter = MockSuccessfulApiAdapter()
    sqlite_adapter = SqliteFinancialAdapter(db_path="Siboif.db")
    use_case = ObtenerDatosSiboifUseCase(api_adapter=api_adapter, sqlite_adapter=sqlite_adapter)
    
    try:
        records, es_fallback = use_case.ejecutar()
        print(f"Éxito: El caso de uso se ejecutó correctamente.")
        print(f"¿Se activó el Fallback?: {es_fallback}")
        print(f"Total registros obtenidos: {len(records)}")
        assert es_fallback is False, "El fallback NO debería haberse activado."
        assert len(records) == 1, "Debería haber exactamente 1 registro mockeado de la API."
        assert records[0].institucion == "MOCK_SEGUROS", "La institución no coincide."
        print("Test 4: PASADO\n")
        return True
    except Exception as e:
        print(f"Error en Test 4: {e}")
        return False

if __name__ == "__main__":
    print("=== INICIANDO PRUEBAS DE ARQUITECTURA HEXAGONAL ===\n")
    t1 = test_sqlite_adapter()
    t2 = test_api_adapter_failure()
    t3 = test_use_case_fallback()
    t4 = test_use_case_success_no_fallback()
    
    if all([t1, t2, t3, t4]):
        print("=== TODAS LAS PRUEBAS SE COMPLETARON CON ÉXITO ===")
        sys.exit(0)
    else:
        print("=== ALGUNAS PRUEBAS FALLARON ===")
        sys.exit(1)
