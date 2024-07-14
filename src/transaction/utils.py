# Utils to avoid repeating code.
def make_transaction(wallet, amount):
    if amount > 0:
        wallet.deposit(amount)
    else:
        wallet.withdraw(amount)


def reverse_transaction(wallet, amount):
    if amount < 0:
        wallet.deposit(amount)
    else:
        wallet.withdraw(amount)
