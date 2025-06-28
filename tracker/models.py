from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

class ProductSearch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)
    target_price = models.FloatField(validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    last_checked = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} (Target: {self.target_price} BDT)"

class ProductResult(models.Model):
    search = models.ForeignKey(ProductSearch, on_delete=models.CASCADE)
    site = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    price = models.FloatField()
    url = models.URLField(max_length=500)
    in_stock = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['price']
    
    def __str__(self):
        return f"{self.site}: {self.title[:50]}... ({self.price} BDT)"
