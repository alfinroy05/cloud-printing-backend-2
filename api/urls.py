from django.urls import path
from .views import home, register, login, upload_file 
from .views import get_orders,get_stores 

urlpatterns = [
    path('', home, name='home'),  # ✅ Home route
    path('register/', register, name='register'),
    path('login/', login, name='login'),
     path('orders/', get_orders, name='get_orders'),
      path('upload/', upload_file, name='upload_file'),
     path('stores/', get_stores, name='get_stores'),
]
