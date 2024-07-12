from rest_framework.exceptions import ValidationError


class InsufficientFundsError(ValidationError):
    pass

