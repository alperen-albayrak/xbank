from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path("transactions/", include("transactions.urls")),
    # path('billing/', views.BillingView.as_view(), name='billing'),
    # path('tables/', views.TablesView.as_view(), name='tables'),
]
