from datetime import time
from django.utils import timezone
from Punch.services import auto_close_session
from Punch.models import PunchSession


class GlobalAutoPunchOutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        now = timezone.localtime()
        today = timezone.localdate()

        # 1. Purane din ke active sessions ko 6:00 PM par close karo
        stale_old = PunchSession.objects.filter(
            status="active",
            date__lt=today,
        )
        for session in stale_old:
            six_pm = timezone.make_aware(
                timezone.datetime.combine(
                    session.date,
                    time(18, 0, 0)
                ),
                timezone.get_current_timezone()
            )
            auto_close_session(session, six_pm)

        # 2. Aaj ke sessions sirf 6:10 PM ke baad auto-close karein
        if now.time() >= time(18, 10):
            stale_today = PunchSession.objects.filter(
                status="active",
                date=today,
            )
            for session in stale_today:
                close_time = timezone.make_aware(
                    timezone.datetime.combine(today, time(18, 0, 0)),
                    timezone.get_current_timezone()
                )
                auto_close_session(session, close_time)

        response = self.get_response(request)
        return response


























































# from datetime import time
# from django.utils import timezone
# from Punch.services import auto_close_session
# from Punch.models import PunchSession


# class GlobalAutoPunchOutMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         now = timezone.localtime()
#         today = timezone.localdate()

#         # 6:10 PM ke baad ya next day koi bhi request aaye
#         # Purane din (kal, parso) ke sessions hamesha band karo
#         stale_old = PunchSession.objects.filter(
#             status="active",
#             date__lt=today,
#         )
#         for session in stale_old:
#             six_pm = timezone.make_aware(
#                 timezone.datetime.combine(
#                     session.date,
#                     timezone.datetime.min.time().replace(hour=18)
#                 )
#             )
#             auto_close_session(session, six_pm)

#         # Aaj ka session sirf 6:10 PM ke baad band karo
#         if now.time() >= time(18, 10):
#             stale_today = PunchSession.objects.filter(
#                 status="active",
#                 date=today,
#                 punch_in_at__hour__lt=18,
#             )
#             for session in stale_today:
#                 close_time = now.replace(hour=18, minute=0, second=0, microsecond=0)
#                 auto_close_session(session, close_time)

#         response = self.get_response(request)
#         return response