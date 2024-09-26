from decimal import Decimal

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_wallet_balance(value: Decimal) -> None:
    """Validate the wallet balance."""
    if value < 0:
        raise ValidationError(
            _("Balance cannot be negative. Current balance: %(balance)s"),
            params={"balance": value},
        )
