class DomainError(Exception):
    """Excepción base para todos los errores del dominio financiero."""
    pass

class ApiCaidaError(DomainError):
    """Excepción lanzada cuando la API externa no responde o está caída."""
    pass

class RegistroNoEncontradoError(DomainError):
    """Excepción lanzada cuando no se encuentra un registro en el repositorio."""
    pass

class DatabaseConnectionError(DomainError):
    """Excepción lanzada cuando hay un error al conectar o consultar la base de datos local."""
    pass
