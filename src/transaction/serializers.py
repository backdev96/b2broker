from rest_framework import serializers
from drf_yasg.utils import swagger_serializer_method
from .models import Transaction, Wallet


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Transaction

    wallet = serializers.PrimaryKeyRelatedField(queryset=Wallet.objects.all())


class TransactionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            "wallet",
            "txid",
            "amount"
        )
        model = Transaction


class WalletCreateSerializer(serializers.ModelSerializer):
    # Serializer for creating wallet.
    class Meta:
        fields = (
            "label",
        )
        model = Wallet


class WalletListSerializer(serializers.ModelSerializer):
        class Meta:
            fields = (
                "label",
                "balance",
            )
            model = Wallet


class WalletRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            "label",
            "balance",
            "transactions"
        )
        model = Wallet

    transactions = serializers.SerializerMethodField()

    @swagger_serializer_method(serializer_or_field=TransactionSerializer(many=True))
    def get_transactions(self, obj: Wallet):
        return TransactionSerializer(obj.transactions.all(), many=True).data
