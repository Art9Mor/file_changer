class ApplicationError(Exception):
    """
    Базовая ошибка сценария.
    """


class ResourceNotFound(ApplicationError):
    """
    Сущность не найдена.
    """

    def __init__(self, resource: str = 'resource') -> None:
        self.resource = resource
        super().__init__(resource)


class EmptyFileError(ApplicationError):
    """
    Загружен пустой файл.
    """


class FileTooLargeError(ApplicationError):
    """
    Превышен допустимый размер файла.
    """

    def __init__(self, max_bytes: int) -> None:
        self.max_bytes = max_bytes
        super().__init__()
