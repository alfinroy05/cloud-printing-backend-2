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

# ✅ Upload File API (Requires Authentication)
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

    # ✅ Validate Store Selection
    if not store_id:
        return Response({'error': 'Please select a store'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        store = Store.objects.get(id=store_id)
    except Store.DoesNotExist:
        return Response({'error': 'Selected store does not exist'}, status=status.HTTP_400_BAD_REQUEST)

    # ✅ Save File
    file_path = f"uploads/{file.name}"
    saved_path = default_storage.save(file_path, ContentFile(file.read()))

    # ✅ Extract Page Count if PDF
    page_count = 1
    if file.name.lower().endswith('.pdf'):
        try:
            full_path = default_storage.path(saved_path)
            with fitz.open(full_path) as pdf:
                page_count = pdf.page_count
        except Exception as e:
            return Response({'error': f'Failed to process PDF: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

    # ✅ Save Print Order
    try:
        print_order = PrintOrder.objects.create(
            user=user,
            store=store,
            file=file,
            file_name=file.name,
            file_path=saved_path,
            page_size=page_size,
            num_copies=num_copies,
            print_type=print_type,
            num_pages=page_count,
            status="pending"
        )
        print(f"✅ Print Order Created for Store: {store.name}", print_order)
    except Exception as e:
        return Response({'error': 'Could not save order'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({
        'message': 'File uploaded successfully',
        'order_id': print_order.id,
        'file_name': print_order.file_name,
        'page_size': print_order.page_size,
        'num_copies': print_order.num_copies,
        'print_type': print_order.print_type,
        'num_pages': print_order.num_pages,
        'store': print_order.store.name,
    }, status=status.HTTP_201_CREATED)

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
