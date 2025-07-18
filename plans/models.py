from django.db import models

# Plans app models
# This module defines the Plan model which represents different subscription plans


class Plan(models.Model):
    BILLING_CHOICES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('lifetime', 'Lifetime'),
    ]

    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    # Optional for Free plan
    billing_cycle = models.CharField(
        max_length=10,
        choices=BILLING_CHOICES,
        blank=True,
        null=True
    )
    stripe_price_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Leave blank for Free plans"
    )

    is_active = models.BooleanField(default=True)

    # ✅ Feature flags
    allow_gallery = models.BooleanField(default=False)
    allow_music = models.BooleanField(default=False)
    allow_custom_banner = models.BooleanField(default=False)

    def __str__(self):
        cycle = self.billing_cycle if self.billing_cycle else "Free"
        return f"{self.name} ({cycle})"
