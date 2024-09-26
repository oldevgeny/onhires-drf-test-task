from rest_framework.routers import DefaultRouter

from .views import TransactionViewSet, WalletViewSet

router = DefaultRouter()
router.register(r"wallets", WalletViewSet)
router.register(r"transactions", TransactionViewSet)

urlpatterns = router.urls
