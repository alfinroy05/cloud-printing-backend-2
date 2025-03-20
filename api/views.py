from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import JsonResponse
import fitz  # PyMuPDF for reading PDFs
from io import BytesIO

from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .models import PrintOrder, Store
from .serializers import PrintOrderSerializer, StoreSerializer

import cloudinary.uploader  # ✅ Cloudinary for file storage

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
    return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)

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
                'access': str(refresh.access_token),
                'user': {'id': user.id, 'username': user.username, 'email': user.email}
            })
    except User.DoesNotExist:
        pass

    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

# ✅ Upload File API (Uses Cloudinary)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_file(request):
    print("✅ Received Upload Request")
    
    try:
        # ✅ Check for Authorization token
        token = request.headers.get('Authorization')
        if not token:
            print("❌ Missing authentication token!")
            return Response({'error': 'Authentication credentials were not provided.'}, status=status.HTTP_401_UNAUTHORIZED)

        # ✅ Check if a file is uploaded
        if 'file' not in request.FILES:
            print("❌ No file uploaded!")
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES['file']
        print(f"📂 File Received: {file.name}")

        page_size = request.data.get('page_size', 'A4')
        num_copies = int(request.data.get('num_copies', 1))
        print_type = request.data.get('print_type', 'black_white')
        store_id = request.data.get('store_id')

        user = request.user
        print(f"👤 User: {user}")

        # ✅ Validate Store Selection
        if not store_id:
            print("❌ No store selected!")
            return Response({'error': 'Please select a store'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            store = Store.objects.get(id=store_id)
        except Store.DoesNotExist:
            print("❌ Selected store does not exist!")
            return Response({'error': 'Selected store does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Process PDF Page Count
        page_count = 1
        if file.name.lower().endswith('.pdf'):
            try:
                pdf_file = BytesIO(file.read())  # ✅ Use BytesIO before uploading to Cloudinary
                with fitz.open(stream=pdf_file, filetype="pdf") as pdf:
                    page_count = pdf.page_count
                file.seek(0)  # ✅ Reset file pointer for Cloudinary upload
                print(f"📄 PDF has {page_count} pages")
            except Exception as e:
                print(f"❌ Failed to process PDF: {str(e)}")
                return Response({'error': f'Failed to process PDF: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Upload to Cloudinary
        try:
            cloudinary_response = cloudinary.uploader.upload(file)
            file_url = cloudinary_response.get('secure_url')
            file_name = cloudinary_response.get('original_filename')

            if not file_url:
                print("❌ Cloudinary upload failed! No file URL returned.")
                return Response({'error': 'Cloudinary upload failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            print(f"✅ File uploaded to Cloudinary: {file_url}")
        except Exception as e:
            print(f"❌ Cloudinary Error: {str(e)}")
            return Response({'error': f'Cloud upload failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # ✅ Save Print Order
        try:
            print_order = PrintOrder.objects.create(
                user=user,
                store=store,
                file_name=file_name,
                file_path=file_url,
                page_size=page_size,
                num_copies=num_copies,
                print_type=print_type,
                num_pages=page_count,
                status="pending"
            )
            print(f"✅ Print Order Created for Store: {store.name}", print_order)
        except Exception as e:
            print(f"❌ Could not save order: {str(e)}")
            return Response({'error': f'Could not save order: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            'message': 'File uploaded successfully',
            'order_id': print_order.id,
            'file_name': print_order.file_name,
            'page_size': print_order.page_size,
            'num_copies': print_order.num_copies,
            'print_type': print_order.print_type,
            'num_pages': print_order.num_pages,
            'store': print_order.store.name,
            'file_url': file_url  # ✅ Added URL for frontend access
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return Response({'error': f'Unexpected error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ✅ Fetch Print Orders (Authenticated Users)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_orders(request):
    user = request.user

    if user.is_staff:  # ✅ Admin gets all orders
        orders = PrintOrder.objects.all().order_by('-id')
    else:  # ✅ Regular user gets only their own orders
        orders = PrintOrder.objects.filter(user=user).order_by('-id')

    serializer = PrintOrderSerializer(orders, many=True)
    return Response(serializer.data)

# ✅ Fetch Available Stores
@api_view(['GET'])
def get_stores(request):
    stores = Store.objects.all()
    serializer = StoreSerializer(stores, many=True)
    return Response(serializer.data)

# ✅ Update Payment Status (Mark as "Completed")
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_payment_status(request):
    order_id = request.data.get('order_id')

    try:
        order = PrintOrder.objects.get(id=order_id, user=request.user)
        order.status = "completed"
        order.save()
        return Response({"message": "Payment successful, order marked as completed!"}, status=status.HTTP_200_OK)
    except PrintOrder.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
