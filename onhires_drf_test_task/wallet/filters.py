import typing

import django_filters

from .models import Wallet


class WalletFilter(django_filters.FilterSet):
    balance_min = django_filters.NumberFilter(field_name="balance", lookup_expr="gte")
    balance_max = django_filters.NumberFilter(field_name="balance", lookup_expr="lte")

    class Meta:
        model = Wallet
        fields: typing.ClassVar = ["label", "balance_min", "balance_max"]
