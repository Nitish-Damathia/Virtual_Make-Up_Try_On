from django.shortcuts import render
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from .models import Order, OrderItem

from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

PRODUCT_PRICES = {
    "Lipstick": 549,
    "Foundation": 799,
    "Eyeliner": 449,
}
def index(request):
    return render(request, 'shop/index.html')
def products(request):
    return render(request, 'shop/products.html')

def contact(request):
    return render(request, 'shop/contact.html')


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

# ✅ Signup
def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("signup")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("signup")

        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)  # auto login after signup
        return redirect("products")

    return render(request, "shop/signup.html")

# ✅ Login
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("products")
        else:
            messages.error(request, "Invalid username or password")
            return redirect("login")

    return render(request, "shop/login.html")

# ✅ Logout
def logout_view(request):
    logout(request)
    return redirect("login")



# views.py
@require_POST
def add_to_cart(request, product):
    shade = request.POST.get("shade", "")
    cart = request.session.get("cart", [])
    price = PRODUCT_PRICES.get(product, 0)

    # check if same product+shade exists, then increase quantity
    for item in cart:
        if item["product"] == product and item.get("shade", "") == shade:
            item["quantity"] = item.get("quantity", 1) + 1
            break
    else:
        cart.append({
            "product": product,
            "shade": shade,
            "price": price,
            "quantity": 1,
        })

    request.session["cart"] = cart
    request.session.modified = True
    return redirect("view_cart")

def remove_from_cart(request, index):
    cart = request.session.get('cart', [])
    try:
        cart.pop(index)
        request.session['cart'] = cart  # update session
    except IndexError:
        pass
    return redirect('view_cart')

def view_cart(request):
    cart = request.session.get("cart", [])

    for item in cart:
        # set defaults if not present
        item["price"] = item.get("price", PRODUCT_PRICES.get(item.get("product", ""), 0))
        item["quantity"] = item.get("quantity", 1)
        item["line_total"] = item["price"] * item["quantity"]

    total_price = sum(i["line_total"] for i in cart)

    return render(request, "shop/cart.html", {
        "cart": cart,
        "total_price": total_price,
    })



from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

@login_required(login_url="/login/")  # redirect to login if not logged in
@require_http_methods(["GET", "POST"])
def checkout(request):
    cart = request.session.get("cart", [])
    total_price = sum(item["price"] * item["quantity"] for item in cart)

    if request.method == "POST":
        # Customer Details
        name = request.POST.get("name")
        email = request.POST.get("email")
        mobile = request.POST.get("mobile")
        address = request.POST.get("address")
        landmark = request.POST.get("landmark")

        # ✅ Create Order
        order = Order.objects.create(
            user=request.user,   # link order to logged-in user
            name=name,
            email=email,
            mobile=mobile,
            address=address,
            landmark=landmark,
            total_price=total_price
        )

        # ✅ Save each item
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item["product"],
                shade=item.get("shade", ""),
                price=item["price"],
                quantity=item["quantity"],
                line_total=item["price"] * item["quantity"]
            )

        # ✅ Clear Cart
        request.session["cart"] = []
        request.session.modified = True

        return render(request, "shop/order_success.html", {
            "name": name,
            "total_price": total_price,
            "order_id": order.id
        })

    return render(request, "shop/checkout.html", {
        "cart": cart,
        "total_price": total_price
    })


from django.contrib.auth.decorators import login_required

@login_required
def my_orders(request):
    orders = Order.objects.filter(email=request.user.email).order_by("-created_at")
    return render(request, "shop/my_orders.html", {"orders": orders})


def lipstick_tryon(request):
    return render(request, 'shop/lipstick.html')

def eyeliner_tryon(request):
    return render(request, 'shop/eyeliner.html')

def foundation_tryon(request):
    return render(request, 'shop/foundation.html')
# views.py

from django.shortcuts import render
from django.http import JsonResponse
import cv2
import numpy as np
import mediapipe as mp
import base64

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True)

LIPS_OUTER = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409,
              291, 375, 321, 405, 314, 17, 84, 181, 91, 146]
LIPS_INNER = [78, 95, 88, 178, 87, 14, 317, 402, 318,
              324, 308, 415, 310, 311, 312, 13, 82, 81, 80, 191]

def hex_to_bgr(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (4, 2, 0))  # BGR

def apply_lipstick(frame, color_hex="#FF0055"):
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            outer = np.array([(int(p.x * w), int(p.y * h)) for i, p in enumerate(face_landmarks.landmark) if i in LIPS_OUTER], np.int32)
            inner = np.array([(int(p.x * w), int(p.y * h)) for i, p in enumerate(face_landmarks.landmark) if i in LIPS_INNER], np.int32)

            mask = np.zeros((h, w), dtype=np.uint8)
            cv2.fillPoly(mask, [outer], 255)
            cv2.fillPoly(mask, [inner], 0)

            mask = cv2.GaussianBlur(mask, (7, 7), 0)

            color = hex_to_bgr(color_hex)
            overlay = np.full_like(frame, color, dtype=np.uint8)
            alpha = mask.astype(float) / 255.0
            alpha = cv2.merge([alpha] * 3)

            frame = (frame.astype(float) * (1 - alpha) + overlay * alpha).astype(np.uint8)
            break
    return frame

def try_lipstick_view(request):
    return render(request, 'shop/try_lipstick.html')

def process_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        uploaded = request.FILES['image']
        file_bytes = np.asarray(bytearray(uploaded.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        output_img = apply_lipstick(img, "#D91A5B")

        _, buffer = cv2.imencode('.jpg', output_img)
        img_base64 = base64.b64encode(buffer).decode('utf-8')

        return JsonResponse({'image': f'data:image/jpeg;base64,{img_base64}'})
    return JsonResponse({'error': 'No image uploaded'}, status=400)






