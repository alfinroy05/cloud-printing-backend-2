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
    total_pages = serializers.SerializerMethodField()  # ✅ Add a custom field for total pages

    class Meta:
        model = PrintOrder
        fields = ['id', 'user', 'store_name', 'file_name', 'file_path', 'page_size', 
                  'num_copies', 'print_type', 'num_pages', 'status', 'uploaded_at', 'total_pages']

    def get_total_pages(self, obj):
        # Calculate total pages as num_pages * num_copies
        return obj.num_pages * obj.num_copies

# ✅ Store Serializer (with Latitude and Longitude)
class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'name', 'location', 'contact', 'latitude', 'longitude']
