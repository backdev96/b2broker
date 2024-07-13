from decimal import Decimal
from django.db import models, transaction
from django.core.validators import MinValueValidator

from .exceptions import InsufficientFundsError


class Wallet(models.Model):
    label = models.CharField(max_length=255, verbose_name="label")
    balance = models.DecimalField(
        max_digits=18,
        decimal_places=0,
        verbose_name="balance",
        default=0,
        validators=[MinValueValidator(Decimal("0"))],
    )  # default=0 for the wallet creation.

    class Meta:
        verbose_name = "Wallet"
        verbose_name_plural = "Wallets"

    def __str__(self):
        return f"{self.label}: {self.balance}"

    def _get_object(self):
        return self.__class__.objects.filter(id=self.id).select_for_update().get()

    @transaction.atomic()
    def deposit(self, amount):
        obj = self._get_object()
        obj.balance += amount
        obj.save()

    @transaction.atomic()
    def withdraw(self, amount):
        # Checks if wallet's balance is higher than transaction amount if negative.
        # Returns 400 http status code.
        obj = self._get_object()
        if amount > obj.balance:
            raise InsufficientFundsError(
                "Your wallet's balance is less than transaction's amount."
            )
        obj = self._get_object()
        obj.balance += amount
        obj.save()


class Transaction(models.Model):
    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        verbose_name="wallet",
        related_name="transactions",
    )
    txid = models.CharField(max_length=255, unique=True, verbose_name="txid")
    amount = models.DecimalField(
        max_digits=18, decimal_places=0, verbose_name="transaction's amount"
    )

    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

    def __str__(self):
        return self.txid

    def save(self, *args, **kwargs):
        if self.amount > 0:
            self.wallet.deposit(self.amount)
        else:
            self.wallet.withdraw(self.amount)
        super(Transaction, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.amount < 0:
            self.wallet.deposit(self.amount)
        else:
            self.wallet.withdraw(self.amount)
        super(Transaction, self).save(*args, **kwargs)
