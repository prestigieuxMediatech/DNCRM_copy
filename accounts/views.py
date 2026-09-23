from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from .utils import is_mobile_device, is_mobile_access_allowed


ROLE_DASHBOARD_URLS = {
    "admin": "dashboard:admin_dashboard",
    "employee": "dashboard:employee_dashboard",
}


def get_dashboard_url_name(user):
    return ROLE_DASHBOARD_URLS.get(user.role)


@never_cache
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        if not email or not password:
            messages.error(request, "Please enter both your email address and password.")
            return render(request, "auth/login.html", {"email": email})

        user = authenticate(request, username=email, password=password)
        if user is None:
            messages.error(request, "Invalid email address or password.")
            return render(request, "auth/login.html", {"email": email})

        # 🔒 Mobile check (Login se pehle)
        if is_mobile_device(request):
            
            if is_mobile_access_allowed(user):
                pass  # Allow
            
            else:
                messages.error(
                    request,
                    "❌ Mobile/Tablet login is not allowed for you. "
                    "Please use a Laptop or Desktop."
                )
                return render(request, "auth/login.html", {"email": email})

        dashboard_url = get_dashboard_url_name(user)
        if dashboard_url is None:
            messages.error(request, "Your account does not have access to a dashboard.")
            return render(request, "auth/login.html", {"email": email})

        if request.user.is_authenticated and request.user.pk != user.pk:
            logout(request)

        login(request, user)
        if not request.POST.get("remember"):
            request.session.set_expiry(0)

        messages.success(request, "You have been logged in successfully.")
        return redirect(dashboard_url)

    return render(request, "auth/login.html")


@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("login")


































































































# from django.contrib import messages
# from django.contrib.auth import authenticate, login, logout
# from django.shortcuts import redirect, render
# from django.views.decorators.cache import never_cache
# from django.views.decorators.http import require_POST
# from .utils import is_mobile_device 


# ROLE_DASHBOARD_URLS = {
#     "admin": "dashboard:admin_dashboard",
#     "employee": "dashboard:employee_dashboard",
# }


# def get_dashboard_url_name(user):
#     """Return the dashboard URL name allowed for the user's application role."""
#     return ROLE_DASHBOARD_URLS.get(user.role)


# @never_cache
# def login_view(request):
#     if request.method == "POST":
#         email = request.POST.get("email", "").strip()
#         password = request.POST.get("password", "")

#         if not email or not password:
#             messages.error(request, "Please enter both your email address and password.")
#             return render(request, "auth/login.html", {"email": email})

#         user = authenticate(request, username=email, password=password)
#         if user is None:
#             messages.error(request, "Invalid email address or password.")
#             return render(request, "auth/login.html", {"email": email})



#                 # ============================================
#         # 🔒 YEH MOBILE CHECK ADD KARO (Login se pehle)
#         # ============================================
#         if is_mobile_device(request):
            
#             # Admin ko allow karo
#             if user.role == 'admin':
#                 pass  # Aage jaane do, login hoga
            
#             # Employee ko block karo
#             elif user.role == 'employee':
#                 messages.error(
#                     request,
#                     "❌ Mobile login is not allowed for employees. "
#                     "Please use a Laptop or Desktop."
#                 )
#                 return render(request, "auth/login.html", {"email": email})
#         # ============================================




        

#         dashboard_url = get_dashboard_url_name(user)
#         if dashboard_url is None:
#             messages.error(request, "Your account does not have access to a dashboard.")
#             return render(request, "auth/login.html", {"email": email})

#         if request.user.is_authenticated and request.user.pk != user.pk:
#             logout(request)

#         login(request, user)
#         if not request.POST.get("remember"):
#             request.session.set_expiry(0)

#         messages.success(request, "You have been logged in successfully.")
#         return redirect(dashboard_url)

#     return render(request, "auth/login.html")


# @require_POST
# def logout_view(request):
#     logout(request)
#     messages.success(request, "You have been logged out successfully.")
#     return redirect("login")
