

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('products/', views.products, name='products'),
    path('contact/', views.contact, name='contact'),
    path("cart/", views.view_cart, name="view_cart"),
    # urls.py
    path("add-to-cart/<str:product>/", views.add_to_cart, name="add_to_cart"),
path('remove-from-cart/<int:index>/', views.remove_from_cart, name='remove_from_cart'),

path("checkout/", views.checkout, name="checkout"),

path("my-orders/", views.my_orders, name="my_orders"),


    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    # ... other urls






    path('lipstick/', views.lipstick_tryon, name='lipstick_tryon'),

path('eyeliner/', views.eyeliner_tryon, name='eyeliner_tryon'),

path('foundation/', views.foundation_tryon, name='foundation_tryon'),
path('process-image/', views.process_image, name='process_image'),

]

