import re

def is_mobile_device(request):
    """
    Check karega ki request mobile/tablet se aa rahi hai ya nahi
    """
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    
    mobile_keywords = [
        'android', 'iphone', 'ipad', 'ipod', 'blackberry',
        'windows phone', 'opera mini', 'mobile', 'webos',
        'iemobile', 'silk'
    ]
    
    for keyword in mobile_keywords:
        if keyword in user_agent:
            return True
    
    return False


def is_mobile_access_allowed(user):
    """
    Check karega ki user ko mobile/tablet se access allow hai ya nahi.
    Admin aur specific employees (email se) ko allow hai.
    """
    # Admin ko hamesha allow karo
    if user.role == 'admin':
        return True
    
    # Exempt employees ki email list
    exempt_employees = [
        'affo@gmail.com',   # <-- Afshaan ki asli email yahaan likho
    ]
    
    # Email se check karo (case-insensitive)
    if user.email and user.email.lower() in [e.lower() for e in exempt_employees]:
        return True
    
    # Baaki sab employees ko block karo
    return False


































































































# accounts/utils.py
# import re

# def is_mobile_device(request):
#     """
#     Check karega ki request mobile se aa rahi hai ya nahi
#     """
#     user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    
#     mobile_keywords = [
#         'android', 'iphone', 'ipad', 'ipod', 'blackberry',
#         'windows phone', 'opera mini', 'mobile', 'webos',
#         'iemobile', 'silk'
#     ]
    
#     for keyword in mobile_keywords:
#         if keyword in user_agent:
#             return True
    
#     return False