from django.urls import path 
from . import views



urlpatterns = [
    path('user/login/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path ('users/register', views.registerUser, name='register'),
    path ('users/profile', views.getUserProfile, name='user-profile'),
    path ('users/profile/update', views.updateUserProfile, name='user-profile-update'),
    path ('users', views.getUsers, name='users'),
    
    # Товары
    path ('products', views.getProducts, name='products'),
    path ('products/<str:pk>', views.getProduct, name='product'),
    
    # Заказы
    path ('orders/add', views.addOrderItems, name='order-add'),
    path('my_orders', views.getMyOrders, name='my-orders'),
    path('order/<str:pk>', views.getOrderById, name='get-order-by-id'),
    path('order/<str:pk>/pay', views.updateOrderToPaid, name='pay'),
     
]
