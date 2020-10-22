from django.urls import path, include
from rest_framework import routers

from engine.views import OrdersViewSet, ProductsViewSet

router = routers.DefaultRouter(trailing_slash=True)
router.register('orders', OrdersViewSet)
router.register('products', ProductsViewSet)
urlpatterns = router.urls
