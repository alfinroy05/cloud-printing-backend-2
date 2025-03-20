from rest_framework import serializers
from .models import PrintOrder, Store  
from django.contrib.auth.models import User


# ✅ User Serializer (Includes User ID)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']  # ✅ Added 'id' for easier reference


# ✅ Store Serializer
class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'name', 'location', 'contact']


# ✅ Print Order Serializer
class PrintOrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # ✅ Nested User Data
    store = StoreSerializer(read_only=True)  # ✅ Nested Store Data

    class Meta:
        model = PrintOrder
        fields = [
            'id', 'user', 'store', 'file_name', 'file_path', 
            'page_size', 'num_copies', 'print_type', 'num_pages', 
            'status', 'uploaded_at'
        ]  # ✅ Explicitly listed fields

