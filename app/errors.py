class CommandError(Exception):
    def __init__(self, message: str, code: str = "CMD_ERROR"):
        super().__init__(message)
        self.code = code
