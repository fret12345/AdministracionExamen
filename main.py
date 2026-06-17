from src.adapters.output.api_financial_adapter import ApiFinancialAdapter
from src.adapters.output.sqlite_financial_adapter import SqliteFinancialAdapter
from src.use_cases.get_financial_data import ObtenerDatosSiboifUseCase
from src.adapters.input.app_ui import render_ui

def main():
    # 1. Instanciar adaptadores de salida
    api_adapter = ApiFinancialAdapter(url="http://127.0.0.1:8000/api/siboif")
    sqlite_adapter = SqliteFinancialAdapter(db_path="Siboif.db")
    
    # 2. Inyectar dependencias en el caso de uso (Fallback automático integrado)
    use_case = ObtenerDatosSiboifUseCase(api_adapter=api_adapter, sqlite_adapter=sqlite_adapter)
    
    # 3. Arrancar la visualización pasando el caso de uso
    render_ui(use_case)

if __name__ == "__main__":
    main()
