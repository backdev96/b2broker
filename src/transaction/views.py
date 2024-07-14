from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework_json_api import filters
from rest_framework_json_api import django_filters
from rest_framework.filters import SearchFilter

from .models import Transaction, Wallet
from .serializers import (
    TransactionSerializer,
    TransactionCreateSerializer,
    TransactionSwaggerCreateSerializer,
    WalletCreateSerializer,
    WalletListSerializer,
    WalletRetrieveSerializer,
    WalletSwaggerCreateSerializer,
    WalletSwaggerUpdateSerializer,
)


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    filter_backends = (
        filters.OrderingFilter,
        django_filters.DjangoFilterBackend,
        SearchFilter,
    )
    filterset_fields = {
        "amount": (
            "exact",
            "lt",
            "gt",
            "gte",
            "lte",
        ),
        "wallet": ("exact",),
        "txid": ("icontains",),
    }

    def get_serializer_class(self):
        if self.action == "list" or self.action == "retrieve":
            return TransactionSerializer
        return TransactionCreateSerializer

    @swagger_auto_schema(
        operation_summary="Get list of Transactions",
        responses={200: TransactionSerializer()},
    )
    def list(self, request, *args, **kwargs):
        return super(TransactionViewSet, self).list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Get Transaction",
        responses={204: "No content", 404: "Not Found"},
    )
    def retrieve(self, request, *args, **kwargs):
        return super(TransactionViewSet, self).retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete Transaction",
        responses={
            204: "No content",
            400: "Your wallet's balance is less than transaction's amount.",
            404: "Not Found",
        },
    )
    def destroy(self, request, *args, **kwargs):
        instance = get_object_or_404(Transaction, pk=self.kwargs.get("pk"))
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        operation_summary="Create Transaction",
        request_body=TransactionSwaggerCreateSerializer,
        responses={
            201: TransactionSerializer(),
            400: "Your wallet's balance is less than transaction's amount.",
        },
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @swagger_auto_schema(
        operation_summary="Update Transaction",
        request_body=TransactionSerializer,
        responses={
            200: TransactionSerializer(),
            400: "Your wallet's balance is less than transaction's amount.",
            404: "Not Found",
        },
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance: Transaction = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        response = TransactionSerializer(
            instance, context=self.get_serializer_context()
        ).data
        return Response(response)

    @swagger_auto_schema(
        operation_summary="Patch Transaction",
        request_body=TransactionSerializer,
        responses={
            200: TransactionSerializer(),
            400: "Your wallet's balance is less than transaction's amount.",
            404: "Not Found",
        },
    )
    def partial_update(self, request, *args, **kwargs):
        return super(TransactionViewSet, self).partial_update(request, *args, **kwargs)


class WalletViewSet(viewsets.ModelViewSet):
    queryset = Wallet.objects.all()
    filter_backends = (
        filters.OrderingFilter,
        django_filters.DjangoFilterBackend,
        SearchFilter,
    )
    filterset_fields = {
        "balance": (
            "exact",
            "lt",
            "gt",
            "gte",
            "lte",
        ),
        "label": (
            "icontains",
            "iexact",
        ),
    }

    def get_serializer_class(self):
        if self.action == "list":
            return WalletListSerializer
        if self.action == "retrieve":
            return WalletRetrieveSerializer
        return WalletCreateSerializer

    @swagger_auto_schema(
        operation_summary="Get list of Wallets", responses={200: WalletListSerializer()}
    )
    def list(self, request, *args, **kwargs):
        return super(WalletViewSet, self).list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Get list of Wallets",
        responses={200: WalletListSerializer(), 404: "Not Found"},
    )
    def retrieve(self, request, *args, **kwargs):
        return super(WalletViewSet, self).retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete Wallet",
        responses={204: "No content", 404: "Not Found"},
    )
    def destroy(self, request, *args, **kwargs):
        instance = get_object_or_404(Wallet, pk=self.kwargs.get("pk"))
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        operation_summary="Create Wallet",
        request_body=WalletSwaggerCreateSerializer,
        responses={201: WalletRetrieveSerializer()},
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @swagger_auto_schema(
        operation_summary="Update Wallet",
        request_body=WalletSwaggerUpdateSerializer,
        responses={200: WalletRetrieveSerializer(), 404: "Not Found"},
    )
    def update(self, request, *args, **kwargs):
        return super(WalletViewSet, self).update(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=WalletSwaggerUpdateSerializer,
        operation_summary="Patch Wallet",
        responses={200: WalletRetrieveSerializer(), 404: "Not Found"},
    )
    def partial_update(self, request, *args, **kwargs):
        return super(WalletViewSet, self).partial_update(request, *args, **kwargs)
