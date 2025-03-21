from rest_framework import serializers
from .models import PrintOrder, Store
from django.contrib.auth.models import User

# ✅ User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']

# ✅ Print Order Serializer
class PrintOrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # ✅ Directly use UserSerializer for cleaner data
    store_name = serializers.CharField(source='store.name', read_only=True)  # ✅ Display store name directly

    class Meta:
        model = PrintOrder
        fields = ['id', 'user', 'store_name', 'file_name', 'file_path', 'page_size', 
                  'num_copies', 'print_type', 'num_pages', 'status', 'uploaded_at']

# ✅ Store Serializer
class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'name', 'location', 'contact']
