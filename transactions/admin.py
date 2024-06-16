from django.contrib import admin
from . import models

admin.site.register(models.TransactionModel)
admin.site.register(models.BorrowModel)