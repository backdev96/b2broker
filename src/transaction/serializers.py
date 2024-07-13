from rest_framework import serializers
from drf_yasg.utils import swagger_serializer_method
from .models import Transaction, Wallet


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Transaction

    wallet = serializers.PrimaryKeyRelatedField(queryset=Wallet.objects.all())

    def to_representation(self, instance: Transaction):
        representation = super().to_representation(instance)
        representation["amount"] = int(instance.amount)
        return representation


class TransactionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("wallet", "txid", "amount")
        model = Transaction


class WalletCreateSerializer(serializers.ModelSerializer):
    # Serializer for creating wallet.
    class Meta:
        fields = ("label",)
        model = Wallet


class WalletListSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            "label",
            "balance",
        )
        model = Wallet

    def to_representation(self, instance: Wallet):
        representation = super().to_representation(instance)
        representation["balance"] = int(instance.balance)
        return representation


class WalletRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("label", "balance", "transactions")
        model = Wallet

    transactions = serializers.SerializerMethodField()

    def to_representation(self, instance: Wallet):
        representation = super().to_representation(instance)
        representation["balance"] = int(instance.balance)
        return representation

    @swagger_serializer_method(serializer_or_field=TransactionSerializer(many=True))
    def get_transactions(self, obj: Wallet):
        return TransactionSerializer(obj.transactions.all(), many=True).data


""" Serializers for swagger schema. """


class DataTransactionSerializer(serializers.Serializer):
    type = serializers.CharField(default="Transaction")
    attributes = TransactionCreateSerializer()


class TransactionSwaggerCreateSerializer(serializers.Serializer):
    data = DataTransactionSerializer()


class DataTransactionUpdateSerializer(serializers.Serializer):
    type = serializers.CharField(default="Wallet")
    id = serializers.IntegerField()
    attributes = WalletCreateSerializer()


class TransactionSwaggerUpdateSerializer(serializers.Serializer):
    data = DataTransactionUpdateSerializer()


class DataWalletSerializer(serializers.Serializer):
    type = serializers.CharField(default="Wallet")
    attributes = WalletCreateSerializer()


class DataWalletUpdateSerializer(serializers.Serializer):
    type = serializers.CharField(default="Wallet")
    id = serializers.IntegerField()
    attributes = WalletCreateSerializer()


class WalletSwaggerCreateSerializer(serializers.Serializer):
    data = DataWalletSerializer()


class WalletSwaggerUpdateSerializer(serializers.Serializer):
    data = DataWalletUpdateSerializer()
