from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('api/users/', include('apps.users.urls')),
    # path('api/catalog/', include('apps.catalog.urls')),
    # path('api/cart/', include('apps.cart.urls')),
    # path('api/order/', include('apps.order.urls')),
    # path('api/payment/', include('apps.payment.urls')),
    # path('api/review/', include('apps.review.urls')),
]
