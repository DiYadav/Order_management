from django.urls import path
from .views import OrderDetailAPIView, OrderListCreateAPIView, OrderStatusUpdateAPIView, OrderCancelAPIView


urlpatterns = [
    path("",OrderListCreateAPIView.as_view(),name="order-list-create"),
    path("<int:pk>/",OrderDetailAPIView.as_view(),name="order-detail"),
    path("<int:pk>/status/",OrderStatusUpdateAPIView.as_view(),name="order-status-update"),
    path("<int:pk>/cancel/",OrderCancelAPIView.as_view(),name="order-cancel"),
]
