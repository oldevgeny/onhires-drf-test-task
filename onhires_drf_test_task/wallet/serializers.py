from decimal import Decimal
from typing import ClassVar

from django.db import transaction
from rest_framework import serializers

from .models import Transaction, Wallet


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields: ClassVar[list[str]] = ["id", "label", "balance"]


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields: ClassVar[list[str]] = ["id", "txid", "wallet", "amount"]

    def validate(self, data: dict) -> dict:  # noqa: PLR6301
        """Validate that the transaction will not cause a negative wallet balance."""
        wallet, amount = data.get("wallet"), data.get("amount")
        new_balance = wallet.balance + amount if all((wallet, amount)) else None

        if new_balance is None:
            raise serializers.ValidationError(
                "Transaction denied: Wallet or amount not provided."
            )

        if new_balance < Decimal(0):
            raise serializers.ValidationError(
                "Transaction denied: Wallet balance cannot be negative."
            )

        return data

    def create(self, validated_data: dict) -> Transaction:  # noqa: PLR6301
        """Create a transaction and update the wallet balance atomically."""
        try:
            with transaction.atomic():
                wallet = Wallet.objects.select_for_update(nowait=True).get(
                    pk=validated_data["wallet"].pk
                )

                new_balance = wallet.balance + validated_data["amount"]

                if new_balance < Decimal(0):
                    raise serializers.ValidationError(
                        "Transaction denied: Wallet balance cannot be negative."
                    )

                wallet.balance = new_balance
                wallet.save()

                return Transaction.objects.create(**validated_data)
        except ZeroDivisionError as exc:
            raise serializers.ValidationError(
                "The wallet is currently locked. Please try again later."
            ) from exc

    def update(self, instance: Transaction, validated_data: dict) -> Transaction:  # noqa: PLR6301
        """
        Update a transaction and update the wallet balance atomically.

        - If the wallet is changed, the amount will be subtracted from
          the old wallet and added to the new wallet.

        """
        try:
            with transaction.atomic():
                old_wallet = Wallet.objects.select_for_update().get(
                    pk=instance.wallet.pk
                )
                new_wallet = validated_data.get("wallet", instance.wallet)
                new_wallet = Wallet.objects.select_for_update().get(pk=new_wallet.pk)

                old_amount = instance.amount
                new_amount = validated_data.get("amount", instance.amount)

                if old_wallet.pk != new_wallet.pk:
                    old_wallet.balance -= old_amount
                    if old_wallet.balance < Decimal(0):
                        raise serializers.ValidationError(
                            "Transaction denied: Wallet balance cannot be negative."
                        )
                    old_wallet.save()

                    new_balance = new_wallet.balance + new_amount
                    if new_balance < Decimal(0):
                        raise serializers.ValidationError(
                            "Transaction denied: Wallet balance cannot be negative."
                        )
                    new_wallet.balance = new_balance
                    new_wallet.save()
                else:
                    amount_difference = new_amount - old_amount
                    new_balance = old_wallet.balance + amount_difference
                    if new_balance < Decimal(0):
                        raise serializers.ValidationError(
                            "Transaction denied: Wallet balance cannot be negative."
                        )
                    old_wallet.balance = new_balance
                    old_wallet.save()

                for attr, value in validated_data.items():
                    setattr(instance, attr, value)
                instance.save()

                return instance

        except ZeroDivisionError as exc:
            raise serializers.ValidationError(
                "The wallet is currently locked. Please try again later."
            ) from exc
