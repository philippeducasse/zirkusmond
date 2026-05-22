from datetime import timedelta

from django.contrib import admin
from django.db import models
from django.utils import timezone
from image_cropping import ImageRatioField
from tinymce import models as tinymce_models

from .managers import PastShowManager, UnscheduledShowManager, UpcomingShowManager

# class SiteStats(models.Model):
#     deleted_visitors = models.PositiveIntegerField(default=0)

#     def __str__(self):
#         return f"Site Stats (deleted_visitors={self.deleted_visitors})"


class Show(models.Model):
    title = models.CharField(max_length=255)
    description = tinymce_models.HTMLField()
    cast = tinymce_models.HTMLField()
    video_link = models.CharField(max_length=255, blank=True)
    card_image = models.ImageField()
    website_link = models.CharField(max_length=255, blank=True)
    banner_link = models.ImageField(blank=True)
    seo_image_crop = ImageRatioField("banner_link", "400x225", editable=False)

    private = models.BooleanField(default=False)
    third_party_reservation = models.BooleanField(
        default=False,
        help_text="Check this field if the company has their own reservation system. Tickets / reservations will not be sold on zirkusmond.de",
    )
    third_party_reservation_link = models.CharField(
        max_length=255, blank=True, help_text="External link to reserve tickets"
    )
    last_modified = models.DateTimeField(auto_now=True)

    reservation_price = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Only set this field if you are not selling full tickets. Guests will have to pay rest at the door",
    )
    base_ticket_price = models.PositiveIntegerField(
        blank=True, null=True, help_text="The default ticket price on the sliding scale"
    )
    min_ticket_price = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Minimum price for sliding scale. Defaults to base_ticket_price - 10 EUR if not set",
    )
    max_ticket_price = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Maximum price for sliding scale. Defaults to base_ticket_price + 10 EUR if not set",
    )

    def future_events(self):
        return [e for e in self.events.all() if e.begin > timezone.now()]

    def last_event(self):
        return self.events.order_by("begin").last()

    def first_event(self):
        return self.events.order_by("begin").first()

    def __str__(self):
        return self.title

    def dates_text(self):
        # TODO
        return "/".join(map(str, self.events.all()))

    def lastmod(self):
        return self.last_modified.strftime("%Y-%m-%d")

    @admin.display(boolean=True)
    def reservation_open(self) -> bool:
        return any(e.reservation_open() for e in self.events.all())

    @admin.display(boolean=True)
    def show_in_preview(self):
        events = self.events.all()
        return not self.private and (
            not len(events) or events[-1].begin + timedelta(hours=4) > timezone.now()
        )

    def clean(self):
        from django.core.exceptions import ValidationError

        errors = {}
        if self.reservation_price is not None and self.base_ticket_price is not None:
            errors["__all__"] = "You cannot set both reservation and ticket price, chose one."
        if self.base_ticket_price is not None:
            if self.min_ticket_price is not None and self.min_ticket_price > self.base_ticket_price:
                errors["min_ticket_price"] = "Minimum price cannot be greater than ticket price."
            if self.max_ticket_price is not None and self.max_ticket_price < self.base_ticket_price:
                errors["max_ticket_price"] = "Maximum price cannot be less than ticket price."
        if errors:
            raise ValidationError(errors)

    def get_effective_min_price(self, base_price):
        if self.min_ticket_price is not None:
            return self.min_ticket_price
        if base_price is not None:
            return max(5, base_price - 10)
        return 5

    def get_effective_max_price(self, base_price):
        if self.max_ticket_price is not None:
            return self.max_ticket_price
        if base_price is not None:
            return base_price + 10
        return 15


class UpcomingShow(Show):
    objects = UpcomingShowManager()

    class Meta:
        proxy = True


class PastShow(Show):
    objects = PastShowManager()

    class Meta:
        proxy = True


class UnscheduledShow(Show):
    objects = UnscheduledShowManager()

    class Meta:
        proxy = True
