import typing

from django.contrib import admin
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as trans

from .models import Transaction, Wallet


class BalanceRangeFilter(admin.SimpleListFilter):
    title = trans("Balance Range")
    parameter_name = "balance_range"

    def lookups(self, _: typing.Any, model: typing.Any) -> list[tuple[str, str]]:  # noqa: ANN401, ARG002, PLR6301
        """Return the balance range lookups."""
        return [
            ("<50", trans("Less than 50")),
            ("50-100", trans("50 to 100")),
            ("100-500", trans("100 to 500")),
            ("500+", trans("More than 500")),
        ]

    def queryset(self, _: typing.Any, queryset: QuerySet) -> QuerySet:  # noqa: ANN401
        """Return the queryset based on the balance range."""
        value = self.value()
        if value == "<50":
            return queryset.filter(balance__lt=50)
        if value == "50-100":
            return queryset.filter(balance__gte=50, balance__lte=100)
        if value == "100-500":
            return queryset.filter(balance__gt=100, balance__lte=500)
        if value == "500+":
            return queryset.filter(balance__gt=500)
        return queryset


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("id", "label", "balance")
    search_fields = ("id", "label")
    list_filter = ("label", BalanceRangeFilter)
    ordering = ("id", "label", "balance")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "txid", "wallet", "amount")
    search_fields = ("id", "txid", "wallet__label", "wallet__id")
    list_filter = ("wallet", "amount")
    ordering = ("id", "txid", "wallet", "amount")

    def wallet(self, obj: Transaction) -> str:  # noqa: PLR6301
        """Return the wallet label."""
        return obj.wallet.label

    wallet.admin_order_field = "wallet__label"
    wallet.short_description = "Wallet Label"
