from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import logout
from .utils import is_mobile_device, is_mobile_access_allowed


class MobileRestrictionMiddleware:
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        self.allowed_urls = [
            '/login/',
            '/logout/',
            '/static/',
            '/media/',
            '/favicon.ico',
        ]
    
    def __call__(self, request):
        current_path = request.path
        
        for allowed in self.allowed_urls:
            if current_path.startswith(allowed):
                return self.get_response(request)
        
        if not request.user.is_authenticated:
            return self.get_response(request)
        
        if is_mobile_device(request):
            
            if is_mobile_access_allowed(request.user):
                return self.get_response(request)
            
            messages.error(
                request,
                "🚫 Employees can only access this CRM from Laptop/Desktop. "
                "Mobile/Tablet access is restricted."
            )
            logout(request)
            return redirect('login')
        
        return self.get_response(request)






















































# accounts/middleware.py
# from django.shortcuts import redirect
# from django.contrib import messages
# from django.contrib.auth import logout
# from .utils import is_mobile_device


# class MobileRestrictionMiddleware:
    
#     def __init__(self, get_response):
#         self.get_response = get_response
        
#         # Yeh URLs mobile pe bhi allow hain
#         self.allowed_urls = [
#             '/login/',
#             '/logout/',
#             '/static/',
#             '/media/',
#             '/favicon.ico',
#         ]
    
#     def __call__(self, request):
#         current_path = request.path
        
#         # Allowed URLs ko skip karo
#         for allowed in self.allowed_urls:
#             if current_path.startswith(allowed):
#                 return self.get_response(request)
        
#         # Agar user login nahi hai, aage jaane do
#         if not request.user.is_authenticated:
#             return self.get_response(request)
        
#         # Mobile check karo
#         if is_mobile_device(request):
            
#             # ✅ ADMIN ko allow karo
#             if request.user.role == 'admin':
#                 return self.get_response(request)
            
#             # ❌ EMPLOYEE ko block karo
#             if request.user.role == 'employee':
#                 messages.error(
#                     request,
#                     "🚫 Employees can only access this CRM from Laptop/Desktop. "
#                     "Mobile access is restricted."
#                 )
#                 logout(request)
#                 return redirect('login')
        
#         response = self.get_response(request)
#         return response