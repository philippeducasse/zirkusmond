from django.utils import timezone

from .models import PageView


class PageViewMiddleware:
    # run once at server startup
    # stores get_response, which returns either another middleware or the actual view
    def __init__(self, get_response):
        self.get_response = get_response

    # this method will run on every single request
    def __call__(self, request):
        response = self.get_response(request)

        if request.path.startswith(("/mondmin", "/static", "/media")):
            return response

        if not request.session.session_key:
            request.session.save()  # force a session_key to exist

        session_key = request.session.session_key

        # close out the previous pageview in this session -> gives us "time on page"
        last = (
            PageView.objects.filter(session_key=session_key, left_at__isnull=True)
            .order_by("-entered_at")
            .first()
        )

        if last:
            last.left_at = timezone.now()
            last.save(update_fields=["left_at"])

        # get device type
        user_agent = request.META.get("HTTP_USER_AGENT", "")

        # create new pageView. left_at is now null on this pv
        PageView.objects.create(
            session_key=session_key,
            path=request.path,
            referer=request.META.get("HTTP_REFERER", ""),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            ip_address=request.META.get("REMOTE_ADDR"),
            device_type=PageView.detect_device(user_agent),
        )

        return response
