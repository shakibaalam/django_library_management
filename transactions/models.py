from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from books.models import BookModel


class TransactionModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=[('deposit', 'Deposit'), ('borrow', 'Borrow'), ('return', 'Return')])
    transaction_date = models.DateTimeField(auto_now_add=True)
    balance_after_transaction = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} - {self.transaction_type} - {self.amount}'


class BorrowModel(models.Model):
    user = models.ForeignKey(User, related_name='borrowed_books', on_delete=models.CASCADE)
    book = models.ForeignKey(BookModel, related_name='borrowed_books', on_delete=models.CASCADE)
    borrow_date = models.DateTimeField(default=timezone.now)
    return_date = models.DateTimeField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"
