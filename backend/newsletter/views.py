from django.shortcuts import redirect, render
from rest_framework.decorators import api_view
from rest_framework.response import Response

from newsletter.forms import NewsletterRegistrationForm
from newsletter.models import NewsletterRegistration
from newsletter.services import register_newsletter_email


@api_view(["POST"])
def register(request):
    email = request.data.get("email")
    if not email:
        return Response({"error": "Email is required"}, status=400)
    NewsletterRegistration.objects.get_or_create(email=email)
    return Response({"success": True}, status=201)


def newsletter_registration(request):
    if request.method == "POST":
        form = NewsletterRegistrationForm(request.POST)
        if form.is_valid():
            register_newsletter_email(form.cleaned_data["email"])
            return render(request, "newsletter_registered.html")

    return redirect("/")
