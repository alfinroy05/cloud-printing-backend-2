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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")  # ✅ Reverse lookup: user.orders.all()
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True, blank=True, related_name="orders")  # ✅ store.orders.all()
    file = models.FileField(upload_to='uploads/')  # ✅ File upload field
    file_name = models.CharField(max_length=255, default="Untitled")  # ✅ Default to avoid null issues
    file_path = models.TextField(default="")  # ✅ Allows longer file paths
    page_size = models.CharField(max_length=10, choices=[('A4', 'A4'), ('A3', 'A3')])
    num_copies = models.PositiveIntegerField(default=1)  # ✅ Prevents negative values
    print_type = models.CharField(max_length=20, choices=[('black_white', 'Black & White'), ('color', 'Color')])
    num_pages = models.PositiveIntegerField(default=1)  # ✅ Prevents negative values
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('printing', 'Printing'), ('completed', 'Completed')],
        default='pending'
    )  # ✅ Order status tracking
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def total_cost(self):
        """Calculate cost dynamically based on page size and print type."""
        price_per_page = {
            'A4': {'black_white': 2, 'color': 5},
            'A3': {'black_white': 4, 'color': 10}
        }
        return self.num_pages * self.num_copies * price_per_page[self.page_size][self.print_type]

    def __str__(self):
        store_info = self.store.name if self.store else "Not Assigned"
        return f"📄 {self.file_name} - {self.page_size} - {self.num_copies} copies - {self.status} - Store: {store_info}"
