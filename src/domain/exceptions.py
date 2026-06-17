class ApiCaidaError(Exception):
    """Excepción lanzada cuando la API externa no responde o está caída."""
    pass

class RegistroNoEncontradoError(Exception):
    """Excepción lanzada cuando no se encuentra un registro en el repositorio."""
    pass
