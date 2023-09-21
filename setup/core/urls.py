from django.urls import path 
from .views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('signup/', RegisterView.as_view(), name='signup'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('products/', GetAllProduct, name='products'),
    path('products/<int:pk>/', GetProduct, name='product'),
    path('products/<str:category>/',GetByCategory, name='category'),
    path('add-to-cart/', AddToCart, name='add-to-cart'),
    path('carts/', GetCartItem,name='cart'),
    path('update-qte/',UpdateQte, name='update-qte'),
    path('delete/<int:pk>/', DeleteFromCart, name='delete'),
    path('address', AddressView.as_view(), name='address'),
    path('payments/',PaymentView.as_view(),name='payments'),
]
