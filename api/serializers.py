from rest_framework import serializers
from .models import PrintOrder, Store  # ✅ Import required models
from django.contrib.auth.models import User


# ✅ User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']  # ✅ Include only necessary fields


# ✅ Print Order Serializer
class PrintOrderSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()  # ✅ More flexible user data
    store = serializers.StringRelatedField()  # ✅ Shows store name instead of ID

    class Meta:
        model = PrintOrder
        fields = '__all__'  # ✅ Includes all fields in PrintOrder model

    def get_user(self, obj):
        """ ✅ Return user data (or None if missing) """
        if obj.user:
            return {
                "username": obj.user.username,
                "email": obj.user.email
            }
        return None  # ✅ Avoids errors if user is null


# ✅ Store Serializer
class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'name', 'location', 'contact']  # ✅ Explicitly define fields
