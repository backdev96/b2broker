from django.db import models, transaction

from .exceptions import InsufficientFundsError


class Wallet(models.Model):
    label = models.CharField(max_length=255, verbose_name="label")
    balance = models.PositiveBigIntegerField(verbose_name="balance", default=0)  # default=0 for the wallet creation.

    class Meta:
        verbose_name = "Wallet"
        verbose_name_plural = "Wallets"
    
    def __str__(self):
        return f"{self.label}: {self.balance}"
    
    @transaction.atomic()
    def deposit(self, amount):
        obj = self.__class__.objects.get(id=self.id).select_for_update()
        obj.balance += amount
        obj.save()
    
    @transaction.atomic()
    def withdraw(self, amount):
        if amount > obj.balance:
            raise InsufficientFundsError("Your wallet's balance is less than transaction's amount.")
        obj = self.get_queryset().select_for_update().get()
        obj.balance += amount
        obj.save()


class Transaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, verbose_name="wallet", related_name="transactions")
    txid = models.CharField(max_length=255, unique=True, verbose_name="txid")
    amount = models.BigIntegerField(verbose_name="transaction's amount") # BigIntegerField covers 19 digits.

    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
    
    def __str__(self):
        return self.txid

    # def full_clean(self, *args, **kwargs) -> None:
    #     # Checks if wallet's balance is higher than transaction amount if negative.
    #     # Returns 400 http status code.
    #     if self.wallet.balance + self.amount < 0:
    #         raise InsufficientFundsError("Your wallet's balance is less than transaction's amount.")
    #     return super().full_clean()

    def save(self, *args, **kwargs):
        if self.amount > 0:
            self.wallet.deposit(self.amount)
        else:
            self.wallet.withdraw(self.amount)
        super(Transaction, self).save(*args, **kwargs)
