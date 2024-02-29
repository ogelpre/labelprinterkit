from ..constants import ErrorCodes


class Error:
    def __init__(self, byte1: int, byte2: int) -> None:
        value = byte1 | (byte2 << 8)
        self._errors = {
            err.name: bool(value & err_code)
            for err_code, err in {x.value: x for x in ErrorCodes}.items()
        }

    def any(self):
        return any(self._errors.values())

    def __getattr__(self, attr):
        return self._errors[attr]

    def __repr__(self):
        return "<Errors {}>".format(self._errors)
