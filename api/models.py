from django.db import models
from django.contrib.auth.models import User
import cloudinary
from cloudinary.models import CloudinaryField

# Store Model
class Store(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    contact = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.location})"

# Print Order Model
class PrintOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True, blank=True)  
    file = CloudinaryField('file', folder='uploads/')  
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=255)
    page_size = models.CharField(max_length=10, choices=[('A4', 'A4'), ('A3', 'A3')])
    num_copies = models.IntegerField(default=1)
    print_type = models.CharField(max_length=20, choices=[('black_white', 'Black & White'), ('color', 'Color')])
    num_pages = models.IntegerField(default=1)  
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('printing', 'Printing'), ('completed', 'Completed')],
        default='pending'
    )  
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # ✅ AES Encryption Fields
    aes_key = models.BinaryField(null=True, blank=True)  # Encrypted AES key (Binary Data)
    iv = models.BinaryField(null=True, blank=True)       # Initialization Vector (IV)
    is_encrypted = models.BooleanField(default=False)    # Track if file is encrypted

    def total_cost(self):
        """Calculate cost based on print type."""
        cost_per_page = 2 if self.print_type == 'black_white' else 5
        return self.num_pages * self.num_copies * cost_per_page

    def __str__(self):
        store_name = self.store.name if self.store else 'Not Selected'
        return f"{self.file_name} - {self.page_size} - {self.num_copies} copies - {self.status} - Store: {store_name}"

    class Meta:
        verbose_name = "Print Order"
        verbose_name_plural = "Print Orders"
