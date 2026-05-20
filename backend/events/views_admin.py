from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django import forms

from .services import purge_old_payments

class PurgeForm(forms.Form):
    confirmed_only = forms.BooleanField(required=False, initial=False, label="Only confirmed payments")
    dry_run = forms.BooleanField(required=False, initial=True, label="Dry run (no changes)")

@staff_member_required
def purge_old_payments_view(request):
    """
    A small admin-like page to run the purge with a button.
    Only accessible to logged-in staff users.
    """
    if request.method == "POST":
        form = PurgeForm(request.POST)
        if form.is_valid():
            result = purge_old_payments(
                confirmed_only=form.cleaned_data["confirmed_only"],
                dry_run=form.cleaned_data["dry_run"],
            )
            if result["dry_run"]:
                messages.info(
                    request,
                    f"[Dry-run] Found {result['payments_found']} payments before {result['cutoff']:%Y-%m-%d}; "
                    f"visitors to add: {result['visitors_to_add']}."
                )
            else:
                messages.success(
                    request,
                    f"Deleted {result['deleted_count']} payments; "
                    f"+{result['visitors_to_add']} visitors accumulated. "
                    f"deleted_visitors now {result['final_deleted_visitors']}."
                )
            return redirect("/mondmin-purge-old-payments")
    else:
        form = PurgeForm()

    # Use a minimal template that inherits the admin base
    context = {
        "form": form,
        "title": "Purge old payments (~6 months)",
        "subtitle": "Deletes old ReservationPayments and updates deleted_visitors.",
    }
    return render(request, "admin_purge_old_payments.html", context)

