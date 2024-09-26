import typing

from django.db import models

from . import validators


class Wallet(models.Model):
    """Model to store wallets."""

    label = models.CharField(max_length=255)
    balance = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[validators.validate_wallet_balance],
    )

    def save(self, *args: typing.Any, **kwargs: typing.Any) -> None:  # noqa: ANN401
        """Override save to include validation."""
        validators.validate_wallet_balance(self.balance)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """Return the label and balance of the wallet."""
        return f"{self.label} - {self.balance:.2f}"


class Transaction(models.Model):
    """Model to store transactions."""

    txid = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    wallet = models.ForeignKey(
        Wallet,
        related_name="transactions",
        on_delete=models.PROTECT,
    )

    def __str__(self) -> str:
        """Return the transaction id and amount."""
        return f"{self.txid} - {self.amount:.2f}"

    class Meta:
        indexes: typing.ClassVar = [
            models.Index(fields=["wallet"]),
        ]
