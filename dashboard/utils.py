import requests
import base64
import mimetypes

def send_whatsapp(phone_number, message="", file_path=None, filename=None):
    # Sirf digits rakho
    phone_clean = ''.join(filter(str.isdigit, str(phone_number)))
    
    # 10-digit number par 91 auto-add karo
    if len(phone_clean) == 10:
        phone_clean = "91" + phone_clean

    file_base64 = None
    mimetype = None

    # Agar local file path diya hai, toh use Base64 me convert karo
    if file_path:
        try:
            with open(file_path, "rb") as f:
                file_base64 = base64.b64encode(f.read()).decode('utf-8')
            
            # File ka extension / mimetype auto detect karo (e.g. application/pdf)
            mimetype, _ = mimetypes.guess_type(file_path)
            
            if not filename:
                import os
                filename = os.path.basename(file_path)
        except Exception as e:
            return {'status': 'error', 'message': f"File read karne me error: {str(e)}"}

    payload = {
        'phone_number': phone_clean,
        'message': message,
        'file_base64': file_base64,  # <-- Node.js ko ab sahi variable milega
        'filename': filename,
        'mimetype': mimetype
    }

    try:
        response = requests.post('http://127.0.0.1:3000/send', json=payload, timeout=60)
        return response.json()
    except Exception as e:
        return {'status': 'error', 'message': str(e)}



































































































# import requests

# def send_whatsapp(phone_number, message="", file_path=None, filename=None):
#     # Only keep digits
#     phone_clean = ''.join(filter(str.isdigit, str(phone_number)))
    
#     # Auto-add India country code (91) if missing (assuming 10 digit number)
#     if len(phone_clean) == 10:
#         phone_clean = "91" + phone_clean

#     payload = {
#         'phone_number': phone_clean,
#         'message': message,
#         'file_path': file_path,
#         'filename': filename
#     }

#     try:
#         response = requests.post('http://127.0.0.1:3000/send', json=payload, timeout=20)
#         return response.json()
#     except Exception as e:
#         return {'status': 'error', 'message': str(e)}