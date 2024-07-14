from django.core.validators import MinValueValidator
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Transaction, Wallet

TRANSACTION_BASE_API_URL = "/api/transactions"
WALLET_BASE_API_URL = "/api/wallets"


# Create your tests here.
class BaseTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_wallet = Wallet.objects.create(label="test wallet 1")
        cls.test_wallet_2 = Wallet.objects.create(label="test wallet 2")
        cls.transactions = []
        number_of_transactions = 11
        for transaction_amount in range(number_of_transactions):
            if transaction_amount % 2 == 0:
                cls.transactions.append(
                    Transaction.objects.create(
                        wallet=cls.test_wallet,
                        txid=f"test transaction {transaction_amount}",
                        amount=transaction_amount,
                    )
                )
            else:
                cls.transactions.append(
                    Transaction.objects.create(
                        wallet=cls.test_wallet_2,
                        txid=f"test transaction {transaction_amount}",
                        amount=transaction_amount,
                    )
                )
        cls.wallets = []
        number_of_wallets = 11
        for wallet_id in range(number_of_wallets):
            cls.transactions.append(
                Wallet.objects.create(label=f"test_wallet_{wallet_id}")
            )


class SwaggerSchemaTest(APITestCase):
    def test_swagger_schema(self):
        response = self.client.get("/swagger/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TransactionModelTest(APITestCase):
    """Transaction Model unit test."""

    def test_transaction_model_has_required_fields(self):
        wallet_field = Transaction._meta.get_field("wallet")
        txid_field = Transaction._meta.get_field("txid")
        id_field = Transaction._meta.get_field("id")
        amount_field = Transaction._meta.get_field("amount")
        self.assertEqual(wallet_field.get_internal_type(), "ForeignKey")
        self.assertEqual(wallet_field.blank, False)
        self.assertEqual(wallet_field.null, False)
        self.assertEqual(txid_field.get_internal_type(), "CharField")
        self.assertEqual(txid_field.unique, True)
        self.assertEqual(txid_field.blank, False)
        self.assertEqual(txid_field.null, False)
        self.assertEqual(id_field.get_internal_type(), "BigAutoField")
        self.assertEqual(id_field.unique, True)
        self.assertEqual(id_field.null, False)
        self.assertEqual(amount_field.get_internal_type(), "DecimalField")
        wallet = Transaction.objects.create(
            wallet=Wallet.objects.create(
                label="Test Wallet for transaction", balance=100
            ),
            txid="Test Transaction",
            amount=100,
        )
        self.assertEqual(str(wallet), "Test Transaction")


class WalletModelTest(APITestCase):
    """Wallet Model unit test."""

    def test_transaction_model_has_required_fields(self):
        label_field = Wallet._meta.get_field("label")
        balance_field = Wallet._meta.get_field("balance")
        id_field = Wallet._meta.get_field("id")

        # Check that validator is present.
        validators = balance_field.validators
        min_value_validator = None
        for validator in validators:
            if isinstance(validator, MinValueValidator):
                min_value_validator = validator
        self.assertEqual(label_field.get_internal_type(), "CharField")
        self.assertEqual(label_field.blank, False)
        self.assertEqual(label_field.null, False)
        self.assertEqual(id_field.get_internal_type(), "BigAutoField")
        self.assertEqual(id_field.unique, True)
        self.assertEqual(id_field.null, False)
        self.assertEqual(balance_field.get_internal_type(), "DecimalField")
        self.assertIsNotNone(min_value_validator)
        wallet = Wallet.objects.create(label="Test Wallet", balance=100)
        self.assertEqual(str(wallet), "Test Wallet: 100")


class TransactionViewTest(BaseTestCase):
    """Transaction API Unit tests."""

    # List Transactions unit tests
    def test_transaction_list(self):
        response = self.client.get(f"{TRANSACTION_BASE_API_URL}/")
        self.assertEqual(len(response.data.get("results")), 10)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("links").get("prev"), None)

    def test_transaction_list_last_page(self):
        response = self.client.get(f"{TRANSACTION_BASE_API_URL}/?page%5Bnumber%5D=2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get("links").get("prev"),
            "http://testserver/api/transactions/?page%5Bnumber%5D=1",
        )

    def test_transaction_list_wallet_filter(self):
        response = self.client.get(
            f"{TRANSACTION_BASE_API_URL}/?wallet={self.test_wallet.id}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get("results")), 6)

    def test_transaction_list_exact_amount(self):
        response = self.client.get(f"{TRANSACTION_BASE_API_URL}/?amount=1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_transaction_list_lt_amount(self):
        response = self.client.get(f"{TRANSACTION_BASE_API_URL}/?amount__lt=5&")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get("results")), 5)

    def test_transaction_list_gt_amount(self):
        response = self.client.get(f"{TRANSACTION_BASE_API_URL}/?amount__gt=5")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get("results")), 5)

    def test_transaction_list_gte_amount(self):
        response = self.client.get(f"{TRANSACTION_BASE_API_URL}/?amount__gte=5&")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get("results")), 6)

    def test_transaction_list_lte_amount(self):
        response = self.client.get(f"{TRANSACTION_BASE_API_URL}/?amount__lte=6")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get("results")), 7)

    def test_transaction_list_lte_and_gt_amount(self):
        response = self.client.get(
            f"{TRANSACTION_BASE_API_URL}/?amount__gt=4&amount__lte=6"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get("results")), 2)

    def test_transaction_list_lte_and_gt_amountand_wallet(self):
        response = self.client.get(
            f"{TRANSACTION_BASE_API_URL}/?amount__lt=8&amount__gt=2&amount__lte=6&wallet={self.test_wallet.id}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get("results")), 2)

    def test_transaction_list_txid(self):
        response = self.client.get(f"{TRANSACTION_BASE_API_URL}/?txid__icontains=1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get("results")), 2)

    def test_transaction_list_sort_amount_desc(self):
        response = self.client.get(f"{TRANSACTION_BASE_API_URL}/?sort=-amount")
        self.assertEqual(response.data.get("results")[0].get("amount"), 10)

    def test_transaction_list_sort_amount_asc(self):
        response = self.client.get(f"{TRANSACTION_BASE_API_URL}/?sort=amount")
        self.assertEqual(response.data.get("results")[0].get("amount"), 0)

    # Create transactions unit tests.
    def test_transaction_create(self):
        starting_balance = Wallet.objects.get(id=self.test_wallet.id).balance
        transaction_amount = 22
        data = {
            "data": {
                "type": "Transaction",
                "attributes": {
                    "wallet": self.test_wallet.id,
                    "txid": "string",
                    "amount": transaction_amount,
                },
            }
        }
        response = self.client.post(f"{TRANSACTION_BASE_API_URL}/", data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        post_balance = Wallet.objects.get(id=self.test_wallet.id)
        self.assertEqual(post_balance.balance, starting_balance + transaction_amount)

    def test_transaction_create_negative_amount(self):
        starting_balance = Wallet.objects.get(id=self.test_wallet.id).balance
        transaction_amount = -1
        data = {
            "data": {
                "type": "Transaction",
                "attributes": {
                    "wallet": self.test_wallet.id,
                    "txid": "string",
                    "amount": transaction_amount,
                },
            }
        }
        response = self.client.post(f"{TRANSACTION_BASE_API_URL}/", data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        post_balance = Wallet.objects.get(id=self.test_wallet.id)
        self.assertEqual(post_balance.balance, starting_balance + transaction_amount)

    def test_transaction_create_negative_balance(self):
        transaction_amount = -100000
        transaction_count_before = Transaction.objects.all().count()
        data = {
            "data": {
                "type": "Transaction",
                "attributes": {
                    "wallet": self.test_wallet.id,
                    "txid": "string",
                    "amount": transaction_amount,
                },
            }
        }
        response = self.client.post(f"{TRANSACTION_BASE_API_URL}/", data=data)
        transaction_count_after = Transaction.objects.all().count()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(transaction_count_before, transaction_count_after)

    def test_transaction_create_ixid_exists(self):
        transaction_amount = 5
        transaction_count_before = Transaction.objects.all().count()
        data = {
            "data": {
                "type": "Transaction",
                "attributes": {
                    "wallet": self.test_wallet.id,
                    "txid": f"test transaction {transaction_amount}",
                    "amount": transaction_amount,
                },
            }
        }
        response = self.client.post(f"{TRANSACTION_BASE_API_URL}/", data=data)
        transaction_count_after = Transaction.objects.all().count()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(transaction_count_before, transaction_count_after)

    def test_transaction_create_amount_is_higher(self):
        # test amount over 18 digits
        transaction_amount = 99999999999999999999999
        transaction_count_before = Transaction.objects.all().count()
        data = {
            "data": {
                "type": "Transaction",
                "attributes": {
                    "wallet": self.test_wallet.id,
                    "txid": f"test transaction {transaction_amount}",
                    "amount": transaction_amount,
                },
            }
        }
        response = self.client.post(f"{TRANSACTION_BASE_API_URL}/", data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        transaction_count_after = Transaction.objects.all().count()
        self.assertEqual(transaction_count_before, transaction_count_after)

    # Retrieve transaction unit tests.
    def test_transaction_retrieve(self):
        response = self.client.get(f"{TRANSACTION_BASE_API_URL}/1/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_transaction_retrieve_not_found(self):
        response = self.client.get(f"{TRANSACTION_BASE_API_URL}/10000/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Put Transaction unit tests.
    def test_transaction_put(self):
        old_transaction_txid = Transaction.objects.get(id=1).txid
        data = {
            "data": {
                "type": "Transaction",
                "id": 1,
                "attributes": {
                    "txid": "string",
                    "amount": "1231234535543",
                    "wallet": 2,
                },
            }
        }
        response = self.client.put(f"{TRANSACTION_BASE_API_URL}/1/", data=data)
        new_transaction_txid = Transaction.objects.get(id=1).txid
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(old_transaction_txid, new_transaction_txid)

    def test_transaction_put_not_found(self):
        data = {
            "data": {
                "type": "Transaction",
                "id": 1,
                "attributes": {
                    "txid": "string",
                    "amount": "1231234535543",
                    "wallet": 2,
                },
            }
        }
        response = self.client.put(f"{TRANSACTION_BASE_API_URL}/100000/", data=data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_transaction_put_wallet_balance_negative(self):
        old_transaction_txid = Transaction.objects.get(id=1).txid
        data = {
            "data": {
                "type": "Transaction",
                "id": 1,
                "attributes": {
                    "txid": "string22",
                    "amount": "-1231234535543",
                    "wallet": 1,
                },
            }
        }
        response = self.client.put(f"{TRANSACTION_BASE_API_URL}/1/", data=data)
        new_transaction_txid = Transaction.objects.get(id=1).txid
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(old_transaction_txid, new_transaction_txid)

    def test_transaction_patch_different_wallets(self):
        transaction = Transaction.objects.create(
            wallet=self.test_wallet,
            txid="test transaction patch",
            amount=50,
        )
        old_wallet_balance_from = Wallet.objects.get(id=self.test_wallet.id).balance
        new_wallet_balance_to = Wallet.objects.get(id=self.test_wallet_2.id).balance
        data = {
            "data": {
                "type": "Transaction",
                "id": transaction.id,
                "attributes": {
                    "txid": "string",
                    "amount": "100",
                    "wallet": self.test_wallet_2.id,
                },
            }
        }
        response = self.client.patch(
            f"{TRANSACTION_BASE_API_URL}/{transaction.id}/", data=data
        )
        new_wallet_balance_from = Wallet.objects.get(id=self.test_wallet.id).balance
        new_wallet_balance_to = Wallet.objects.get(id=self.test_wallet_2.id).balance
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(new_wallet_balance_from < old_wallet_balance_from)
        self.assertTrue(new_wallet_balance_to > new_wallet_balance_from)

    def test_transaction_patch_different_wallets_insufficient_balance(self):
        transaction = Transaction.objects.create(
            wallet=self.test_wallet,
            txid="test transaction patch balance",
            amount=10000,
        )
        _ = Transaction.objects.create(
            wallet=self.test_wallet,
            txid="test transaction patch 2",
            amount=-5000,
        )
        data = {
            "data": {
                "type": "Transaction",
                "id": transaction.id,
                "attributes": {
                    "txid": "string",
                    "amount": "100",
                    "wallet": self.test_wallet_2.id,
                },
            }
        }
        response = self.client.patch(
            f"{TRANSACTION_BASE_API_URL}/{transaction.id}/", data=data
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Put Transaction unit tests.
    def test_transaction_patch(self):
        old_transaction_txid = Transaction.objects.get(id=1).txid
        data = {
            "data": {
                "type": "Transaction",
                "id": 1,
                "attributes": {
                    "txid": "string",
                    "amount": "1231234535543",
                    "wallet": 2,
                },
            }
        }
        response = self.client.patch(f"{TRANSACTION_BASE_API_URL}/1/", data=data)
        new_transaction_txid = Transaction.objects.get(id=1).txid
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(old_transaction_txid, new_transaction_txid)

    def test_transaction_put_different_wallets(self):
        transaction = Transaction.objects.create(
            wallet=self.test_wallet,
            txid="test transaction diff wallets",
            amount=50,
        )
        old_wallet_balance_from = Wallet.objects.get(id=self.test_wallet.id).balance
        new_wallet_balance_to = Wallet.objects.get(id=self.test_wallet_2.id).balance
        data = {
            "data": {
                "type": "Transaction",
                "id": transaction.id,
                "attributes": {
                    "txid": "string",
                    "amount": "100",
                    "wallet": self.test_wallet_2.id,
                },
            }
        }
        response = self.client.put(
            f"{TRANSACTION_BASE_API_URL}/{transaction.id}/", data=data
        )
        new_wallet_balance_from = Wallet.objects.get(id=self.test_wallet.id).balance
        new_wallet_balance_to = Wallet.objects.get(id=self.test_wallet_2.id).balance
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(new_wallet_balance_from < old_wallet_balance_from)
        self.assertTrue(new_wallet_balance_to > new_wallet_balance_from)

    def test_transaction_put_different_wallets_insufficient_balance(self):
        transaction = Transaction.objects.create(
            wallet=self.test_wallet,
            txid="test transaction pozitive",
            amount=10000,
        )
        _ = Transaction.objects.create(
            wallet=self.test_wallet,
            txid="test transaction negative",
            amount=-5000,
        )
        data = {
            "data": {
                "type": "Transaction",
                "id": transaction.id,
                "attributes": {
                    "txid": "string",
                    "amount": "100",
                    "wallet": self.test_wallet_2.id,
                },
            }
        }
        response = self.client.put(
            f"{TRANSACTION_BASE_API_URL}/{transaction.id}/", data=data
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_transaction_patch_not_found(self):
        data = {
            "data": {
                "type": "Transaction",
                "id": 1,
                "attributes": {
                    "txid": "string",
                    "amount": "1231234535543",
                    "wallet": 2,
                },
            }
        }
        response = self.client.patch(f"{TRANSACTION_BASE_API_URL}/100000/", data=data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_transaction_patch_wallet_balance_negative(self):
        old_transaction_txid = Transaction.objects.get(id=1).txid
        data = {
            "data": {
                "type": "Transaction",
                "id": 1,
                "attributes": {
                    "txid": "string",
                    "amount": "-1231234535543",
                    "wallet": 1,
                },
            }
        }
        response = self.client.patch(f"{TRANSACTION_BASE_API_URL}/1/", data=data)
        new_transaction_txid = Transaction.objects.get(id=1).txid
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(old_transaction_txid, new_transaction_txid)

    # Delete transaction Unit tests.
    def test_transaction_delete(self):
        response = self.client.delete(f"{TRANSACTION_BASE_API_URL}/1/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_transaction_delete_negative_amount(self):
        self.test_wallet_2.balance = 1000
        self.test_wallet_2.save()
        transaction_negative = Transaction.objects.create(
            wallet=self.test_wallet_2, txid="negative transaction", amount=-100
        )
        response = self.client.delete(
            f"{TRANSACTION_BASE_API_URL}/{transaction_negative.id}/"
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_transaction_delete_negative_wallet_balance(self):
        wallet_old = Wallet.objects.get(id=self.test_wallet_2.id)
        wallet_old.balance = 0
        wallet_old.save()
        transaction_positive = Transaction.objects.create(
            wallet=wallet_old, txid="positive transaction", amount=100000
        )
        transaction_negative = Transaction.objects.create(
            wallet=wallet_old, txid="negative transaction", amount=-90000
        )
        response = self.client.delete(
            f"{TRANSACTION_BASE_API_URL}/{transaction_positive.id}/"
        )
        wallet_new = Wallet.objects.get(id=self.test_wallet_2.id)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            transaction_positive.amount + transaction_negative.amount,
            wallet_new.balance,
        )

    def test_transaction_delete_not_found(self):
        response = self.client.delete(f"{TRANSACTION_BASE_API_URL}/10000/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class WalletViewTest(BaseTestCase):
    """Wallet API Unit tests."""

    # List Wallets unit tests.
    def test_wallet_list(self):
        response = self.client.get(f"{WALLET_BASE_API_URL}/")
        self.assertEqual(len(response.data.get("results")), 10)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("links").get("prev"), None)

    def test_wallet_list_last_page(self):
        response = self.client.get(f"{WALLET_BASE_API_URL}/?page%5Bnumber%5D=2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get("links").get("prev"),
            "http://testserver/api/wallets/?page%5Bnumber%5D=1",
        )

    def test_wallet_list_label_iexact(self):
        response = self.client.get(
            f"{WALLET_BASE_API_URL}/?label__iexact=test_wallet_1"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get("results")), 1)

    def test_wallet_list_label_icontains(self):
        response = self.client.get(
            f"{WALLET_BASE_API_URL}/?label__icontains=test%20wallet"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get("results")), 2)

    def test_wallet_list_balance_exact(self):
        response = self.client.get(f"{WALLET_BASE_API_URL}/?balance=0")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get("results")), 10)

    def test_wallet_list_wallet_sort_label(self):
        response = self.client.get(f"{WALLET_BASE_API_URL}/?sort=label")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("results")[0].get("label"), "test wallet 1")

    def test_wallet_list_wallet_balance_sort_label_desc(self):
        response = self.client.get(f"{WALLET_BASE_API_URL}/?sort=-label")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("results")[0].get("label"), "test_wallet_9")

    # Retrieve wallet unit tests.
    def test_wallet_retrieve(self):
        response = self.client.get(f"{WALLET_BASE_API_URL}/1/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_wallet_retrieve_not_found(self):
        response = self.client.get(f"{WALLET_BASE_API_URL}/100000/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Wallet patch unit tests.
    def test_wallet_patch(self):
        old_label = Wallet.objects.get(id=3).label
        data = {"data": {"type": "Wallet", "id": 3, "attributes": {"label": "string"}}}
        response = self.client.patch("/api/wallets/3/", data=data)
        new_label = Wallet.objects.get(id=3).label
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(old_label, new_label)

    def test_wallet_patch_not_found(self):
        data = {
            "data": {"type": "Wallet", "id": 100, "attributes": {"label": "string"}}
        }
        response = self.client.patch("{WALLET_BASE_API_URL}/100/", data=data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Wallet put unit tests.
    def test_wallet_put(self):
        old_label = Wallet.objects.get(id=4).label
        data = {
            "data": {"type": "Wallet", "id": 4, "attributes": {"label": "str222ing"}}
        }
        response = self.client.put("/api/wallets/4/", data=data)
        new_label = Wallet.objects.get(id=3).label
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(old_label, new_label)

    def test_wallet_put_not_found(self):
        data = {
            "data": {"type": "Wallet", "id": 100, "attributes": {"label": "str222ing"}}
        }
        response = self.client.put("{WALLET_BASE_API_URL}/100/", data=data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Delete wallet Unit tests.
    def test_wallet_delete(self):
        response = self.client.delete(f"{WALLET_BASE_API_URL}/1/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_wallet_delete_not_found(self):
        response = self.client.delete(f"{WALLET_BASE_API_URL}/10000/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Post wallet Unit test
    def test_wallet_create(self):
        data = {"data": {"type": "Wallet", "attributes": {"label": "string"}}}
        response = self.client.post("/api/wallets/", data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
