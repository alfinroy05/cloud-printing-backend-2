from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import fitz  # PyMuPDF for reading PDFs

from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .models import PrintOrder, Store
from .serializers import PrintOrderSerializer, StoreSerializer

# ✅ Home Route
def home(request):
    return JsonResponse({"message": "Welcome to Web2Print API!"})

# ✅ User Registration API
@api_view(['POST'])
def register(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, email=email, password=password)
    user.save()

    return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)  # ✅ FIXED INDENTATION



# ✅ User Login API (JWT-based)
@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    try:
        user = User.objects.get(email=email)
        user = authenticate(username=user.username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),  # ✅ Ensure `access` key exists
                'user': {'id': user.id, 'username': user.username, 'email': user.email}
            })
    except User.DoesNotExist:
        pass

    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
import cloudinary.uploader



@api_view(['GET'])
@permission_classes([IsAuthenticated])  # ✅ Ensure authentication is required
def get_orders(request):
    # ✅ Check if the user is an admin (staff)
    if request.user.is_staff:
        orders = PrintOrder.objects.all().order_by('-id')  # ✅ Admin can view all orders
    else:
        orders = PrintOrder.objects.filter(user=request.user).order_by('-id')  # ✅ Regular users only view their orders
    
    serializer = PrintOrderSerializer(orders, many=True)
    return Response(serializer.data)



# ✅ Fetch Available Stores
@api_view(['GET'])
def get_stores(request):
    stores = Store.objects.all()
    serializer = StoreSerializer(stores, many=True)
    return Response(serializer.data)

# ✅ Update Payment Status (Requires Authentication)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_payment_status(request):
    order_id = request.data.get('order_id')

    try:
        order = PrintOrder.objects.get(id=order_id, user=request.user)
        order.status = "paid"
        order.save()
        return Response({"message": "Payment successful, order updated!"}, status=status.HTTP_200_OK)
    except PrintOrder.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)


from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import fitz  # PyMuPDF for reading PDFs

from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .models import PrintOrder, Store
from .serializers import PrintOrderSerializer, StoreSerializer

from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Store
from rest_framework_simplejwt.tokens import RefreshToken

# ✅ Store Registration API
@api_view(['POST'])
def store_register(request):
    username = request.data.get('username')
    password = request.data.get('password')
    store_name = request.data.get('storeName')
    location = request.data.get('location')
    contact = request.data.get('contact')

    # ✅ Check if username already exists
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

    # ✅ Create User
    user = User.objects.create_user(username=username, password=password)

    # ✅ Create Store
    store = Store.objects.create(name=store_name, location=location, contact=contact, admin=user)

    return Response({'message': 'Store registered successfully!'}, status=status.HTTP_201_CREATED)


# ✅ Store Login API
@api_view(['POST'])
def store_login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {'id': user.id, 'username': user.username}
        })
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from base64 import b64encode
import cloudinary.uploader

def encrypt_file(file_data, key):
    iv = os.urandom(16)  # Generate random IV
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted_data = cipher.encrypt(pad(file_data, AES.block_size))
    return iv + encrypted_data

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_file(request):
    print("✅ Received Upload Request")

    if 'file' not in request.FILES:
        return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

    file = request.FILES['file']
    page_size = request.data.get('page_size', 'A4')
    num_copies = int(request.data.get('num_copies', 1))
    print_type = request.data.get('print_type', 'black_white')
    store_id = request.data.get('store_id')

    user = request.user
    print(f"👤 User: {user}")

    try:
        store = Store.objects.get(id=store_id)
    except Store.DoesNotExist:
        return Response({'error': 'Selected store does not exist'}, status=status.HTTP_400_BAD_REQUEST)

    # ✅ Read and Encrypt File Data
    file_data = file.read()
    aes_key = get_random_bytes(32)  # Generate a new AES key
    iv = get_random_bytes(16)       # Generate IV
    encrypted_data = encrypt_file(file_data, aes_key)

    # ✅ Upload Encrypted File to Cloudinary
    try:
        encrypted_file_path = f"encrypted_{file.name}"
        with open(encrypted_file_path, "wb") as f:
            f.write(encrypted_data)

        response = cloudinary.uploader.upload(
            encrypted_file_path,
            resource_type="raw",
            folder="uploads/"
        )
        print("✅ File uploaded to Cloudinary:", response['secure_url'])
        cloudinary_url = response['secure_url']

        # Remove local encrypted file after upload
        os.remove(encrypted_file_path)

    except Exception as e:
        print(f"❌ Error uploading to Cloudinary: {str(e)}")
        return Response({'error': f'Failed to upload to Cloudinary: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # ✅ Save Print Order with Encryption Details
    print_order = PrintOrder.objects.create(
        user=user,
        store=store,
        file_name=file.name,
        file_path=cloudinary_url,
        page_size=page_size,
        num_copies=num_copies,
        print_type=print_type,
        num_pages=1,
        status="pending"
    )

    return Response({
        'message': 'File uploaded and encrypted successfully',
        'order_id': print_order.id,
        'file_name': print_order.file_name,
        'store': print_order.store.name,
        'aes_key': b64encode(aes_key).decode(),
        'iv': b64encode(iv).decode()
    }, status=status.HTTP_201_CREATED)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_decryption_key(request):
    order_id = request.data.get('order_id')
    try:
        order = PrintOrder.objects.get(id=order_id)
        # Provide the AES key securely
        return Response({'aes_key': 'your-32-byte-secret-key-here'})
    except PrintOrder.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)



from Crypto.Util.Padding import unpad

def decrypt_file(encrypted_data, key):
    iv = encrypted_data[:16]  # Extract IV from the start
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_data = unpad(cipher.decrypt(encrypted_data[16:]), AES.block_size)
    return decrypted_data
