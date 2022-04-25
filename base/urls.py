from django.urls import path 
from . import views


urlpatterns = [
    # Products
    path ('products', views.getProducts, name='products'),
    path ('products/<str:pk>', views.getProduct, name='product'),
    
    # Orders
    path ('orders/add', views.addOrderItems, name='order-add'),
    path('my_orders', views.getMyOrders, name='my-orders'),
    path('order/<str:pk>', views.getOrderById, name='get-order-by-id'), 
]
