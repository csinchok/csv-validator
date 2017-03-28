

class ValidationError(Exception):

    def __init__(self, message):

        self.message = message
        super().__init__(message)

        if isinstance(message, dict):
            self.error_dict = message
        else:
            self.error_dict = {}

    def __str__(self):
        if self.error_dict:
            return repr(dict(self.error_dict))
        else:
            return super().__str__()

    def __eq__(self, other):
        return isinstance(other, ValidationError) and self.message == other.message

    def __hash__(self):
        return super().__hash__()