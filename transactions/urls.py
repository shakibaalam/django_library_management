from django.urls import path
from .views import DepositMoneyView, TransactionReportView,BorrowListView,ReturnBookView

urlpatterns = [
    path("deposit/", DepositMoneyView.as_view(), name="deposit_money"),
    path("report/", TransactionReportView.as_view(), name="transaction_report"),
    path("borrowed_history/", BorrowListView.as_view(), name="borrowed_history"),
    path("return/<int:borrow_id>/", ReturnBookView.as_view(), name="return"),
]