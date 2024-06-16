from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, View
from .models import CategoryModel,BookModel,ReviewModel
from transactions.models import BorrowModel,TransactionModel
from books.forms import ReviewForm
from django.utils.decorators import method_decorator
from django.contrib import messages
from transactions.views import send_transaction_email


class BookListView(ListView):
    model = BookModel
    template_name = 'index.html'
    context_object_name = 'books'

    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            return BookModel.objects.filter(category__slug=category_slug) 
        return BookModel.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = CategoryModel.objects.all()
        context['current_category'] = self.kwargs.get('category_slug', '')
        return context


@method_decorator(login_required, name='dispatch')
class BookDetailView(View):

    def get(self, request, *args, **kwargs):
        book = get_object_or_404(BookModel, pk=kwargs['pk'])
        review_form = ReviewForm()

        user_borrowed = BorrowModel.objects.filter(user=request.user, book=book, return_date__isnull=True).first()
        print('user_borrowed', user_borrowed)
        return render(request, 'books/book_details.html', {
            'book': book,
            'review_form': review_form,
            'user_borrowed': user_borrowed
        })

    def post(self, request, *args, **kwargs):
        book = get_object_or_404(BookModel, pk=kwargs['pk'])
        review_form = ReviewForm(request.POST)
        user_borrowed = BorrowModel.objects.filter(user=request.user, book=book, return_date__isnull=True).first()
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.book = book
            review.user = request.user  # Set the user field here
            review.save()
            return redirect(reverse('book_detail', kwargs={'pk': book.id}))
        return render(request, 'books/book_details.html', {
            'book': book,
            'review_form': review_form,
            'user_borrowed': user_borrowed
        })
    
@method_decorator(login_required, name='dispatch')
class BuyRequestView(View):
    def post(self, request, book_id):
        book = get_object_or_404(BookModel, id=book_id)
        user_account = request.user.account
        if user_account.balance >= book.price:
            user_account.balance -= book.price
            user_account.save()
            BorrowModel.objects.create(user=request.user, book=book, amount=book.price)
            TransactionModel.objects.create(user=request.user, amount=book.price, transaction_type='borrow')

            send_transaction_email(self.request.user, book.price, "Borrowing Message", "transactions/admin_email.html")

            messages.success(self.request,f'{book.title} is borrowed successfully')
            return redirect('borrowed_history')
        else:
            messages.error(self.request, f'Book price is greater than available balance')
            return redirect('book_detail', book.id)
    
