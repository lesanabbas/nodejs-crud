from django.db import models


# Create your models here.
class Pizza(models.Model):
    CATEGORY_CHOICES = [
        ("Veg", "Vegetarian"),
        ("Non-Veg", "Non-Vegetarian"),
        ("Specialty", "Specialty"),
    ]

    SIZE_CHOICES = [
        ("Small", "Small"),
        ("Medium", "Medium"),
        ("Large", "Large"),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    stock = models.IntegerField(default=0)  # Number of pizzas in stock
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="Veg")
    available_sizes = models.CharField(
        max_length=50, choices=SIZE_CHOICES, default="Medium"
    )  # Available sizes (Small, Medium, Large)
    toppings = models.TextField(
        blank=True, null=True
    )  # A text field to list available toppings
    created_at = models.DateTimeField(auto_now_add=True)  # Time when pizza was created
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    # You can add methods here if needed, for example:
    def is_available(self):
        return self.stock > 0 and self.status == "Active"
