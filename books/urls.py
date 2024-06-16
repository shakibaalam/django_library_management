from django.urls import path
from .views import BookListView,BookDetailView,BuyRequestView

urlpatterns = [
    path('', BookListView.as_view(), name='home'),
    path('books/category/<slug:category_slug>/', BookListView.as_view(), name='category_wise_post'),
    path('book_details/<int:pk>/', BookDetailView.as_view(), name='book_detail'),
    path("buy/<int:book_id>/", BuyRequestView.as_view(), name="buy_book"),
]