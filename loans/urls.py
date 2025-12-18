from django.urls import path
from .views import (
    LoanListView, LoanDetailView, LoanCreateView,
    LoanReturnView, LoanUpdateView, LoanDeleteView,
    user_loans, loan_stats, calculate_overdue_fines
)

app_name = 'loans'

urlpatterns = [
    # User endpoints
    path('', LoanListView.as_view(), name='loan_list'),
    path('<int:pk>/', LoanDetailView.as_view(), name='loan_detail'),
    path('borrow/', LoanCreateView.as_view(), name='loan_create'),
    path('<int:pk>/return/', LoanReturnView.as_view(), name='loan_return'),
    path('my-loans/', user_loans, name='user_loans'),
    
    # Admin endpoints
    path('<int:pk>/update/', LoanUpdateView.as_view(), name='loan_update'),
    path('<int:pk>/delete/', LoanDeleteView.as_view(), name='loan_delete'),
    path('stats/', loan_stats, name='loan_stats'),
    path('calculate-fines/', calculate_overdue_fines, name='calculate_fines'),
]


