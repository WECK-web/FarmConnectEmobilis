from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('create/', views.create_listing, name='create_listing'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:listing_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:listing_id>/', views.cart_remove, name='cart_remove'),
    path('checkout/', views.checkout, name='checkout'),
    path('dashboard/', views.farmer_dashboard, name='farmer_dashboard'),
    path('farmer/<str:username>/', views.farmer_profile, name='farmer_profile'),
    path('message/send/<str:recipient_username>/', views.send_message, name='send_message'),
    path('inbox/', views.inbox, name='inbox'),
    path('listing/id/<int:pk>/', views.edit_listing, name='edit_listing'),
    path('listing/delete/<int:pk>/', views.delete_listing, name='delete_listing'),
    path('orders/', views.consumer_orders, name='consumer_orders'),
    path('profile/', views.profile, name='profile'),
    path('order/update/<int:order_id>/', views.update_order_status, name='update_order_status'),
]
