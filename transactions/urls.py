from django.urls import path

from . import views


urlpatterns = [
    path("", views.IndexView.as_view(), name='transactions'),
    path('wallets/', views.WalletsView.as_view(), name='wallets'),
    path("add-wallet", views.AddWalletView.as_view(), name='add-wallet'),
    path("<int:wallet_id>/edit-wallet", views.EditWalletView.as_view(), name='edit-wallet'),
    path("<int:wallet_id>/delete-wallet", views.DeleteWalletView.as_view(), name='delete-wallet'),
    path("recorded-wallet", views.RecordedWalletView.as_view(), name='recorded-wallet'),
    path("add-record", views.AddRecordView.as_view(), name='add-record'),
    path("<int:wallet_id>/delete-record", views.DeleteRecordView.as_view(), name='delete-record'),
    path("make-transaction", views.MakeTransactionsView.as_view(), name='make-transaction'),
    path("<int:transaction_id>/cancel-transaction", views.CancelTransactionView.as_view(), name='cancel-transaction'),
]
