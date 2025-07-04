from django.db import models
from django.contrib.auth.models import User


class ExpanseIncome(models.Model):
    TRANSACTION_TYPE = (
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    )
    
    TAX_TYPES = (
        ('flat', 'Flat'),
        ('percentage', 'Percentage'),
        ('zero', 'Zero'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True,null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE)
    tax_type = models.CharField(max_length=10, choices=TAX_TYPES)
    tax = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    @property
    def total(self):
        if self.tax_type == 'flat':
            return self.amount + self.tax
        elif self.tax_type == 'percentage':
            return self.amount * (1 + (self.tax / 100))
        return self.amount
    
    
    def __str__(self):
        return f"{self.title} - {self.amount}"