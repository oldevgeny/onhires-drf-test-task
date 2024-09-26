from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db import transaction as db_transaction
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.test import APITestCase

from .models import Wallet
from .serializers import TransactionSerializer


class WalletTestCase(APITestCase):
    INITIAL_BALANCE = Decimal("100.00")

    def test_wallet_creation(self):
        """Test wallet creation."""
        test_balance_value = self.INITIAL_BALANCE
        wallet = Wallet.objects.create(label="Test Wallet", balance=test_balance_value)
        assert wallet.balance == test_balance_value, "Wallet balance should be 100."

    @staticmethod
    def test_wallet_creation_with_zero_balance() -> None:
        """Test wallet creation with zero balance."""
        wallet = Wallet.objects.create(label="Zero Balance Wallet", balance=0)
        assert wallet.balance == 0, "Wallet balance should be 0."

    @staticmethod
    def test_wallet_creation_with_negative_balance() -> None:
        """Test that creating a wallet with negative balance is prevented."""
        with pytest.raises(ValidationError) as exc_info:
            Wallet.objects.create(label="Negative Balance Wallet", balance=-50)
        assert "Balance cannot be negative" in str(
            exc_info.value
        ), "Error message should indicate that balance cannot be negative."

    def test_wallet_update_label(self):
        """Test updating the wallet's label."""
        wallet = Wallet.objects.create(label="Old Label", balance=self.INITIAL_BALANCE)
        wallet.label = "New Label"
        wallet.save()
        wallet.refresh_from_db()
        assert (
            wallet.label == "New Label"
        ), "Wallet label should be updated to 'New Label'."

    def test_wallet_update_balance(self):
        """Test updating the wallet's balance."""
        wallet = Wallet.objects.create(
            label="Test Wallet", balance=self.INITIAL_BALANCE
        )
        wallet.balance = Decimal("150.00")
        wallet.save()
        wallet.refresh_from_db()
        assert wallet.balance == Decimal(
            "150.00"
        ), "Wallet balance should be updated to 150.00."

    def test_wallet_deletion(self):
        """Test deleting a wallet."""
        wallet = Wallet.objects.create(
            label="Test Wallet", balance=self.INITIAL_BALANCE
        )
        wallet_id = wallet.id
        wallet.delete()
        assert not Wallet.objects.filter(
            id=wallet_id
        ).exists(), "Wallet should be deleted."

    def test_wallet_api_get(self):
        """Test retrieving a wallet via API."""
        wallet = Wallet.objects.create(label="API Wallet", balance=self.INITIAL_BALANCE)
        url = reverse(
            "wallet-detail", args=[wallet.id]
        )  # Adjust 'wallet-detail' if needed
        response = self.client.get(url)
        assert (
            response.status_code == status.HTTP_200_OK
        ), "Should be able to retrieve the wallet via API."
        assert response.data["label"] == "API Wallet", "Wallet label should match."
        assert (
            Decimal(response.data["balance"]) == self.INITIAL_BALANCE
        ), "Wallet balance should match."

    def test_wallet_api_list(self):
        """Test listing wallets via API."""
        maximum_wallets_count = 2
        Wallet.objects.create(label="Wallet 1", balance=Decimal("50.00"))
        Wallet.objects.create(label="Wallet 2", balance=Decimal("150.00"))

        url = reverse("wallet-list")  # Adjust 'wallet-list' if needed
        response = self.client.get(url)

        assert (
            response.status_code == status.HTTP_200_OK
        ), "Should be able to list wallets via API."
        assert (
            len(response.data["results"]) >= maximum_wallets_count
        ), "Should have at least two wallets in the list."

    def test_wallet_api_create(self):
        """Test creating a wallet via API."""
        url = reverse("wallet-list")
        data = {
            "label": "API Created Wallet",
            "balance": "200.00",
        }
        response = self.client.post(url, data, format="json")
        assert (
            response.status_code == status.HTTP_201_CREATED
        ), "Wallet should be created via API."
        wallet = Wallet.objects.get(id=response.data["id"])
        assert wallet.label == data["label"], "Wallet label should match."
        assert wallet.balance == Decimal(
            data["balance"]
        ), "Wallet balance should match."

    def test_wallet_api_update(self):
        """Test updating a wallet via API."""
        wallet = Wallet.objects.create(
            label="Initial Label", balance=self.INITIAL_BALANCE
        )
        url = reverse("wallet-detail", args=[wallet.id])
        data = {
            "label": "Updated Label",
            "balance": "250.00",
        }
        response = self.client.put(url, data, format="json")
        assert (
            response.status_code == status.HTTP_200_OK
        ), "Wallet should be updated via API."
        wallet.refresh_from_db()
        assert wallet.label == data["label"], "Wallet label should be updated."
        assert wallet.balance == Decimal(
            data["balance"]
        ), "Wallet balance should be updated."

    def test_wallet_api_delete(self):
        """Test deleting a wallet via API."""
        wallet = Wallet.objects.create(
            label="To Be Deleted", balance=self.INITIAL_BALANCE
        )
        url = reverse("wallet-detail", args=[wallet.id])
        response = self.client.delete(url)
        assert (
            response.status_code == status.HTTP_204_NO_CONTENT
        ), "Wallet should be deleted via API."
        assert not Wallet.objects.filter(
            id=wallet.id
        ).exists(), "Wallet should no longer exist."

    def test_wallet_api_filtering(self):
        """Test filtering wallets via API."""
        Wallet.objects.create(label="Filter Wallet 1", balance=Decimal("50.00"))
        Wallet.objects.create(label="Filter Wallet 2", balance=Decimal("150.00"))
        url = reverse("wallet-list")
        response = self.client.get(url, {"balance_min": "100"})
        assert (
            response.status_code == status.HTTP_200_OK
        ), "Should be able to filter wallets via API."
        for wallet_data in response.data["results"]:
            assert Decimal(wallet_data["balance"]) >= Decimal(
                100
            ), "Wallet balance should be at least 100."

    def test_wallet_api_ordering(self):
        """Test ordering wallets via API."""
        Wallet.objects.create(label="A Wallet", balance=Decimal("50.00"))
        Wallet.objects.create(label="B Wallet", balance=Decimal("150.00"))
        url = reverse("wallet-list")
        response = self.client.get(url, {"ordering": "label"})
        assert (
            response.status_code == status.HTTP_200_OK
        ), "Should be able to order wallets via API."
        labels = [wallet["label"] for wallet in response.data["results"]]
        assert labels == sorted(labels), "Wallets should be ordered by label."

    def test_wallet_api_pagination(self):
        """Test pagination of wallets via API."""
        default_page_size = 10
        total_count = 15

        for i in range(15):
            Wallet.objects.create(label=f"Wallet {i}", balance=Decimal("100.00"))

        url = reverse("wallet-list")
        response = self.client.get(url)

        assert (
            response.status_code == status.HTTP_200_OK
        ), "Should be able to paginate wallets via API."
        assert (
            len(response.data["results"]) == default_page_size
        ), "Default page size should be 10."
        assert response.data["count"] == total_count, "Total count should be 15."


class TransactionTestCase(APITestCase):
    INITIAL_WALLET_LABEL = "Test Wallet"
    INITIAL_BALANCE = Decimal("100.00")
    NEGATIVE_TRANSACTION = Decimal("-50.00")
    POSITIVE_TRANSACTION = Decimal("50.00")

    def setUp(self):
        """Create a wallet with a balance of INITIAL_BALANCE for testing."""
        self.wallet = Wallet.objects.create(
            label=self.INITIAL_WALLET_LABEL,
            balance=self.INITIAL_BALANCE,
        )

    def test_valid_negative_transaction(self):
        """Test a valid negative transaction (withdrawal)."""
        data = {
            "txid": "tx1",
            "amount": self.NEGATIVE_TRANSACTION,
            "wallet": self.wallet.id,
        }
        serializer = TransactionSerializer(data=data)
        assert serializer.is_valid(), f"Serializer should be valid: {serializer.errors}"
        transaction = serializer.save()
        self.wallet.refresh_from_db()
        expected_balance = self.INITIAL_BALANCE + self.NEGATIVE_TRANSACTION
        assert (
            self.wallet.balance == expected_balance
        ), f"Wallet balance should be {expected_balance} after the transaction."
        assert (
            transaction.amount == self.NEGATIVE_TRANSACTION
        ), f"Transaction amount should be {self.NEGATIVE_TRANSACTION}."

    def test_valid_positive_transaction(self):
        """Test a valid positive transaction (deposit)."""
        data = {
            "txid": "tx2",
            "amount": self.POSITIVE_TRANSACTION,
            "wallet": self.wallet.id,
        }
        serializer = TransactionSerializer(data=data)
        assert serializer.is_valid(), f"Serializer should be valid: {serializer.errors}"
        transaction = serializer.save()
        self.wallet.refresh_from_db()
        expected_balance = self.INITIAL_BALANCE + self.POSITIVE_TRANSACTION
        assert (
            self.wallet.balance == expected_balance
        ), f"Wallet balance should be {expected_balance} after the transaction."
        assert (
            transaction.amount == self.POSITIVE_TRANSACTION
        ), f"Transaction amount should be {self.POSITIVE_TRANSACTION}."

    def test_zero_amount_transaction(self):
        """Test that a transaction with zero amount is invalid."""
        data = {
            "txid": "tx3",
            "amount": Decimal("0.00"),
            "wallet": self.wallet.id,
        }
        serializer = TransactionSerializer(data=data)
        assert (
            not serializer.is_valid()
        ), "Serializer should be invalid for zero amount."
        assert (
            "amount" in serializer.errors or "non_field_errors" in serializer.errors
        ), "Error should be related to zero amount."

    def test_transaction_negative_balance(self):
        """Test that a transaction leading to negative wallet balance is invalid."""
        data = {
            "txid": "tx4",
            "amount": Decimal("-150.00"),
            "wallet": self.wallet.id,
        }
        serializer = TransactionSerializer(data=data)
        assert (
            not serializer.is_valid()
        ), "Serializer should be invalid due to negative balance."
        assert (
            "non_field_errors" in serializer.errors
        ), "Error should be related to negative balance."

    def test_update_transaction_amount(self):
        """Test updating transaction amount and adjusting wallet balance."""
        # Create initial transaction
        data = {
            "txid": "tx5",
            "amount": Decimal("50.00"),
            "wallet": self.wallet.id,
        }
        serializer = TransactionSerializer(data=data)
        assert serializer.is_valid(), f"Serializer should be valid: {serializer.errors}"
        transaction = serializer.save()
        self.wallet.refresh_from_db()
        expected_balance = self.INITIAL_BALANCE + Decimal("50.00")
        assert (
            self.wallet.balance == expected_balance
        ), f"Wallet balance should be {expected_balance} after creating the transaction."

        # Update transaction amount to 70.00
        updated_data = {
            "amount": Decimal("70.00"),
            "wallet": self.wallet.id,
        }
        serializer = TransactionSerializer(
            instance=transaction, data=updated_data, partial=True
        )
        assert serializer.is_valid(), f"Serializer should be valid: {serializer.errors}"
        updated_transaction = serializer.save()
        self.wallet.refresh_from_db()
        expected_balance += Decimal("20.00")  # Difference between new and old amount
        assert (
            self.wallet.balance == expected_balance
        ), f"Wallet balance should be {expected_balance} after updating the transaction."
        assert updated_transaction.amount == Decimal(
            "70.00"
        ), "Transaction amount should be updated to 70.00."

    def test_update_transaction_wallet(self):
        """Test changing the wallet of a transaction and adjusting balances."""
        # Create a second wallet
        second_wallet = Wallet.objects.create(
            label="Second Wallet", balance=Decimal("200.00")
        )

        # Create initial transaction in the first wallet
        data = {
            "txid": "tx6",
            "amount": Decimal("50.00"),
            "wallet": self.wallet.id,
        }
        serializer = TransactionSerializer(data=data)
        assert serializer.is_valid(), f"Serializer should be valid: {serializer.errors}"
        transaction = serializer.save()

        self.wallet.refresh_from_db()
        second_wallet.refresh_from_db()
        expected_balance_wallet1 = self.INITIAL_BALANCE + Decimal("50.00")
        expected_balance_wallet2 = Decimal("200.00")
        assert (
            self.wallet.balance == expected_balance_wallet1
        ), f"Wallet 1 balance should be {expected_balance_wallet1} after creating the transaction."
        assert (
            second_wallet.balance == expected_balance_wallet2
        ), f"Wallet 2 balance should be {expected_balance_wallet2}."

        # Update transaction to move it to the second wallet
        updated_data = {
            "wallet": second_wallet.id,
            "amount": Decimal("50.00"),
        }
        # Set partial=True to allow partial updates
        serializer = TransactionSerializer(
            instance=transaction, data=updated_data, partial=True
        )
        assert serializer.is_valid(), f"Serializer should be valid: {serializer.errors}"
        serializer.save()

        self.wallet.refresh_from_db()
        second_wallet.refresh_from_db()
        expected_balance_wallet1 -= Decimal("50.00")  # Remove transaction from wallet 1
        expected_balance_wallet2 += Decimal("50.00")  # Add transaction to wallet 2
        assert (
            self.wallet.balance == expected_balance_wallet1
        ), f"Wallet 1 balance should be {expected_balance_wallet1} after moving the transaction."
        assert (
            second_wallet.balance == expected_balance_wallet2
        ), f"Wallet 2 balance should be {expected_balance_wallet2} after receiving the transaction."

    def test_delete_transaction(self):
        """Test deleting a transaction and adjusting wallet balance."""
        data = {
            "txid": "tx7",
            "amount": Decimal("50.00"),
            "wallet": self.wallet.id,
        }
        serializer = TransactionSerializer(data=data)
        assert serializer.is_valid(), f"Serializer should be valid: {serializer.errors}"
        transaction = serializer.save()
        self.wallet.refresh_from_db()
        expected_balance = self.INITIAL_BALANCE + Decimal("50.00")
        assert (
            self.wallet.balance == expected_balance
        ), f"Wallet balance should be {expected_balance} after creating the transaction."

        # Simulate deletion of the transaction with balance adjustment
        try:
            with db_transaction.atomic():
                wallet = Wallet.objects.select_for_update().get(pk=self.wallet.pk)
                new_balance = wallet.balance - transaction.amount
                if new_balance < Decimal(0):
                    raise DRFValidationError(
                        "Cannot delete transaction: wallet balance cannot be negative."
                    )
                wallet.balance = new_balance
                wallet.save()
                transaction.delete()
        except DRFValidationError as e:
            pytest.fail(f"Deletion failed: {e}")

        self.wallet.refresh_from_db()
        expected_balance -= Decimal("50.00")
        assert (
            self.wallet.balance == expected_balance
        ), f"Wallet balance should be {expected_balance} after deleting the transaction."

    def test_delete_transaction_negative_balance(self):
        """Test that deleting a transaction leading to negative wallet balance is prevented."""
        # Create a transaction increasing the wallet balance
        data = {
            "txid": "tx8",
            "amount": Decimal("80.00"),
            "wallet": self.wallet.id,
        }
        serializer = TransactionSerializer(data=data)
        assert serializer.is_valid(), f"Serializer should be valid: {serializer.errors}"
        transaction = serializer.save()
        self.wallet.refresh_from_db()
        expected_balance = self.INITIAL_BALANCE + Decimal("80.00")
        assert (
            self.wallet.balance == expected_balance
        ), f"Wallet balance should be {expected_balance} after creating the transaction."

        # Modify wallet balance so deletion would cause negative balance
        self.wallet.balance = Decimal("30.00")  # Less than the transaction amount
        self.wallet.save()

        # Define a helper function to attempt to delete the transaction
        def attempt_delete_transaction():  # noqa: ANN202
            with db_transaction.atomic():
                wallet = Wallet.objects.select_for_update().get(pk=self.wallet.pk)
                new_balance = wallet.balance - transaction.amount
                if new_balance < Decimal(0):
                    raise DRFValidationError(
                        "Cannot delete transaction: wallet balance cannot be negative."
                    )
                wallet.balance = new_balance
                wallet.save()
                transaction.delete()

        # Use pytest.raises with a single statement (the helper function call)
        with pytest.raises(DRFValidationError) as exc_info:
            attempt_delete_transaction()

        # Assertions on the exception
        self.wallet.refresh_from_db()
        assert self.wallet.balance == Decimal(
            "30.00"
        ), "Wallet balance should remain unchanged after failed deletion."
        assert "wallet balance cannot be negative" in str(
            exc_info.value
        ), "Error message should indicate prevention of negative balance."
