import typing
from decimal import Decimal

from django.db import DatabaseError, transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.request import Request
from rest_framework.response import Response

from . import filters, models, serializers
from .models import Wallet


class WalletViewSet(viewsets.ModelViewSet):
    queryset = models.Wallet.objects.all()
    serializer_class = serializers.WalletSerializer
    filter_backends: typing.ClassVar = [OrderingFilter, DjangoFilterBackend]
    ordering_fields: typing.ClassVar = ["label", "balance"]
    filterset_class = filters.WalletFilter
    filterset_fields: typing.ClassVar = ["label", "balance"]
    ordering: typing.ClassVar = ["id"]


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = models.Transaction.objects.all()
    serializer_class = serializers.TransactionSerializer
    filter_backends: typing.ClassVar = [OrderingFilter, DjangoFilterBackend]
    ordering_fields: typing.ClassVar = ["amount", "txid"]
    filterset_fields: typing.ClassVar = ["wallet", "txid", "amount"]

    def destroy(self, _: Request, *args: typing.Any, **kwargs: typing.Any) -> Response:  # noqa: ARG002, ANN401
        """Override the destroy method to update the wallet balance."""
        instance = self.get_object()
        try:
            with transaction.atomic():
                wallet = Wallet.objects.select_for_update().get(pk=instance.wallet.pk)

                new_balance = wallet.balance - instance.amount
                if new_balance < Decimal(0):
                    return Response(
                        {
                            "detail": "It is impossible to delete the transaction: the wallet balance cannot be negative."
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                wallet.balance = new_balance
                wallet.save()

                instance.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)

        except DatabaseError:
            return Response(
                {
                    "detail": "It is impossible to delete the transaction: the wallet is currently locked. Please try again later."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
