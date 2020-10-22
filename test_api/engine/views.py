from rest_framework import viewsets
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.permissions import SAFE_METHODS
from django_filters import rest_framework as filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from engine.serializers import OrderSerializer, ProductsSerializer
from engine.models import Order, Products
from engine.choices import OrderChoices
from authentication import auth


# Create your views here.
class OrderFilter(filters.FilterSet):
    start_date = filters.DateFilter(field_name='created_at', lookup_expr='gte')
    end_date = filters.DateFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Order
        fields = ('id', 'start_date', 'end_date')


class OrdersViewSet(auth.OrderGetQuerySetMixin, viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all().order_by('-id')
    filterset_class = OrderFilter
    permission_classes = (auth.OrderPermissions,)

    @action(detail=True, methods=['PATCH'], serializer_class=OrderSerializer)
    def complete(self, request, pk):
        order = self.get_object()
        if order.status == OrderChoices.ACTIVE:
            order.complete()
            serializer = OrderSerializer(order)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(data={'message': 'Order must be active.'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['PATCH'], serializer_class=OrderSerializer)
    def pay(self, request, pk):
        order = self.get_object()
        if order.status == OrderChoices.COMPLETED:
            order.pay()
            serializer = OrderSerializer(order)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(data={'message': 'Order must be completed first.'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['GET'], serializer_class=OrderSerializer)
    def check(self, request, pk):
        order = self.get_object()
        if order.status == OrderChoices.PAID:
            serializer = OrderSerializer(order)
            return render(request, "check.html", context=serializer.data)
        return Response(data={'message': 'Check not paid yet.'}, status=status.HTTP_400_BAD_REQUEST)


class ProductsViewSet(viewsets.ModelViewSet):
    serializer_class = ProductsSerializer
    queryset = Products.objects.all().order_by('-id')
    permission_classes = (IsAuthenticated,)
