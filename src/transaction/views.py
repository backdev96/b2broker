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
    WalletCreateSerializer,
    WalletListSerializer,
    WalletRetrieveSerializer
)


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    filter_backends = (filters.QueryParameterValidationFilter, filters.OrderingFilter,
                      django_filters.DjangoFilterBackend, SearchFilter)
    filterset_fields = {
       'amount': ('exact', 'lt', 'gt', 'gte', 'lte', 'in'),
       'wallet': ('exact',),
       'txid': ('icontains', 'iexact', ),
    }
    search_fields = ('wallet', 'txid', 'amount',)
    
    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return TransactionSerializer
        return TransactionCreateSerializer

    # def get_queryset(self):
    #     pass
    
    @swagger_auto_schema(
        operation_summary='Get list of Transactions',
        responses={200: TransactionSerializer()}
    )
    def list(self, request, *args, **kwargs):
        return super(TransactionViewSet, self).list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Get Transaction',
        responses={
            204: "No content",
            404: "Not Found"
        },
    )
    def retrieve(self, request, *args, **kwargs):
        return super(TransactionViewSet, self).retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Delete Transaction',
        responses={
            204: "No content",
            404: "Not Found"},
    )
    def destroy(self, request, *args, **kwargs):
        instance = get_object_or_404(Transaction, pk=self.kwargs.get('pk'))
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        operation_summary='Create Transaction',
        request_body=TransactionSerializer,
        responses={201: TransactionSerializer()},
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @swagger_auto_schema(
        operation_summary='Update Transaction',
        request_body=TransactionSerializer,
        responses={200: TransactionSerializer()},
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance: Transaction = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        response = TransactionSerializer(instance, context=self.get_serializer_context()).data
        return Response(response)

    @swagger_auto_schema(
        operation_summary='Patch Transaction',
    )
    def partial_update(self, request, *args, **kwargs):
        return super(TransactionViewSet, self).partial_update(request, *args, **kwargs)
    

class WalletViewSet(viewsets.ModelViewSet):
    queryset = Wallet.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return WalletListSerializer
        if self.action == 'retrieve':
            return WalletRetrieveSerializer
        return WalletCreateSerializer

    # def get_queryset(self):
    #     pass
    
    @swagger_auto_schema(
        operation_summary='Get list of Wallets',
        responses={200: WalletListSerializer()}
    )
    def list(self, request, *args, **kwargs):
        return super(WalletViewSet, self).list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Get Wallet',
    )
    def retrieve(self, request, *args, **kwargs):
        return super(WalletViewSet, self).retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Delete Wallet',
    )
    def destroy(self, request, *args, **kwargs):
        instance = get_object_or_404(Wallet, pk=self.kwargs.get('pk'))
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        operation_summary='Create Wallet',
        request_body=WalletCreateSerializer,
        responses={201: WalletRetrieveSerializer()},
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @swagger_auto_schema(
        operation_summary='Update Wallet',
        request_body=WalletCreateSerializer,
        responses={200: WalletRetrieveSerializer()},
    )
    def update(self, request, *args, **kwargs):
        return super(WalletViewSet, self).update(request, *args, **kwargs)
        # partial = kwargs.pop('partial', False)
        # instance: Wallet = self.get_object()
        # serializer = self.get_serializer(instance, data=request.data, partial=partial)
        # serializer.is_valid(raise_exception=True)
        # instance = serializer.save()
        # response = WalletRetrieveSerializer(instance, context=self.get_serializer_context()).data
        # headers = self.get_success_headers(serializer.data)
        # return Response(response.data, status=status.HTTP_200_OK, headers=headers)

    @swagger_auto_schema(
        operation_summary='Patch Wallet',
    )
    def partial_update(self, request, *args, **kwargs):
        return super(WalletViewSet, self).partial_update(request, *args, **kwargs)