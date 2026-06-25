from src.adapters.output.api_financial_adapter import ApiFinancialAdapter
from src.adapters.output.sqlite_financial_adapter import SqliteFinancialAdapter
from src.use_cases.get_financial_data import ObtenerDatosSiboifUseCase
from src.adapters.input.app_ui import render_ui

def main():
    # 1. Instanciar adaptadores de salida concretos
    api_adapter = ApiFinancialAdapter(url="http://127.0.0.1:8000/api/siboif")
    sqlite_adapter = SqliteFinancialAdapter(db_path="Siboif.db")
    
    # 2. Inyectar dependencias en el caso de uso.
    # Cumple con DIP al depender de la interfaz FinancialRepository, y con OCP 
    # ya que podemos alternar o quitar adaptadores sin tocar la lógica de ejecución.
    use_case = ObtenerDatosSiboifUseCase(
        primary_repository=api_adapter, 
        fallback_repository=sqlite_adapter
    )
    
    # 3. Arrancar la visualización (UI) pasando el puerto del caso de uso
    render_ui(use_case)

if __name__ == "__main__":
    main()
