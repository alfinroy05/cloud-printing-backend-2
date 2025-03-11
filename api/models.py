from django.db import models
from django.contrib.auth.models import User

# Store Model
class Store(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    contact = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.location})"

# Print Order Model
class PrintOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # ✅ Link order to user
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True, blank=True)  # ✅ Store Selection
    file = models.FileField(upload_to='uploads/')  # ✅ File upload field
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=255)
    page_size = models.CharField(max_length=10, choices=[('A4', 'A4'), ('A3', 'A3')])
    num_copies = models.IntegerField(default=1)
    print_type = models.CharField(max_length=20, choices=[('black_white', 'Black & White'), ('color', 'Color')])
    num_pages = models.IntegerField(default=1)  # ✅ Added field for total pages
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('printing', 'Printing'), ('completed', 'Completed')],
        default='pending'
    )  # ✅ Track order status
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def total_cost(self):
        """Calculate cost based on ₹2 per page and number of copies"""
        cost_per_page = 2  # ₹2 per page
        return self.num_pages * self.num_copies * cost_per_page

    def __str__(self):
        return f"{self.file_name} - {self.page_size} - {self.num_copies} copies - {self.status} - Store: {self.store.name if self.store else 'Not Selected'}"
