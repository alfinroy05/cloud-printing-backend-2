from django.urls import path
from .views import home, register, login, upload_file, get_orders, get_stores, store_register, store_login

urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('store/register/', store_register, name='store_register'),
    path('store/login/', store_login, name='store_login'),
    path('orders/', get_orders, name='get_orders'),
    path('upload/', upload_file, name='upload_file'),
    path('stores/', get_stores, name='get_stores'),
]
