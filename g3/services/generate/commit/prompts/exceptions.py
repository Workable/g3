class PromptCreatorException(Exception):
    pass


class TokenLimitExceededException(PromptCreatorException):
    def __init__(self, msg: str = ""):
        super().__init__(msg)
