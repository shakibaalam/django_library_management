from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
from django.conf import settings
from .models import TransactionModel, BorrowModel
from books.models import BookModel
from .forms import DepositForm
from django.utils import timezone
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

def send_transaction_email(user, amount, subject, template):
        message = render_to_string(template, {
            'user' : user,
            'amount' : amount,
        })
        send_email = EmailMultiAlternatives(subject, '', to=[user.email])
        send_email.attach_alternative(message, "text/html")
        send_email.send()


class DepositMoneyView(View):
    @method_decorator(login_required)
    def get(self, request):
        form = DepositForm()
        return render(request, 'transactions/deposit.html', {'form': form})

    @method_decorator(login_required)
    def post(self, request):
        form = DepositForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            user_account = request.user.account
            user_account.balance += amount
            user_account.save()
            TransactionModel.objects.create(user=request.user, amount=amount, transaction_type='deposit')

            send_transaction_email(self.request.user, amount, "Deposit Message", "transactions/deposite_email.html")

            return redirect('transaction_report')
        return render(request, 'transactions/deposit.html', {'form': form})

class ReturnBookView(View):
    @method_decorator(login_required)
    def post(self, request, borrow_id):
        borrow = get_object_or_404(BorrowModel, id=borrow_id, user=request.user)
        user_account = request.user.account
        user_account.balance += borrow.amount
        user_account.save()
        borrow.return_date = timezone.now()
        borrow.save()
        TransactionModel.objects.create(user=request.user, amount=borrow.amount, transaction_type='return')
        
        return redirect('borrowed_history')

class TransactionReportView(LoginRequiredMixin, ListView):
    model = TransactionModel
    template_name = 'transactions/transaction_report.html'
    context_object_name = 'transactions'

    def get_queryset(self):
        return TransactionModel.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        account = self.request.user.account
        transactions = self.get_queryset().order_by('transaction_date')
        
        balance =0
        for transaction in transactions:
            # print('Balance',transaction)
            if transaction.transaction_type == 'deposit' or transaction.transaction_type == 'return':
                balance += transaction.amount
            elif transaction.transaction_type == 'borrow':
                balance -= transaction.amount
            transaction.balance_after_transaction = balance
        
        context.update({
            'account': account,
            'transactions': transactions,
            'current_balance': account.balance
        })
        return context


class BorrowListView(View):
    @method_decorator(login_required)
    def get(self, request):
        borrowed_books = request.user.borrowed_books.all()
        return render(request, 'transactions/borrowed_history.html', {'borrowed_books': borrowed_books})

