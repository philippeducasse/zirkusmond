from datetime import timedelta
from decimal import Decimal

from django.contrib import admin
from django.db import models
from django.utils import timezone
from image_cropping import ImageRatioField
from tinymce import models as tinymce_models


class SiteStats(models.Model):
    deleted_visitors = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Site Stats (deleted_visitors={self.deleted_visitors})"


class Show(models.Model):
    title = models.CharField(max_length=255)
    description = tinymce_models.HTMLField()
    cast = tinymce_models.HTMLField()
    video_link = models.CharField(max_length=255, blank=True)
    card_image = models.ImageField()
    website_link = models.CharField(max_length=255, blank=True)
    banner_link = models.ImageField(blank=True)
    head_img = ImageRatioField('banner_link', '400x225')

    private = models.BooleanField(default=False)
    third_party_reservation = models.BooleanField(default=False)
    third_party_reservation_link = models.CharField(max_length=255, blank=True)
    last_modified = models.DateTimeField(auto_now=True)

    reservation_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    ticket_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    min_ticket_price = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        help_text="Minimum price for sliding scale. Defaults to ticket_price - 10 EUR if not set.")
    max_ticket_price = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        help_text="Maximum price for sliding scale. Defaults to ticket_price + 10 EUR if not set.")

    def events(self):
        return list(self.event_set.all())

    def last_event(self):
        events = self.events()
        return events[0] if events else None

    def first_event(self):
        events = self.events()
        return events[-1] if events else None

    def __str__(self):
        return self.title

    def dates_text(self):
        # TODO
        return '/'.join(map(str, self.events()))

    def lastmod(self):
        return self.last_modified.strftime('%Y-%m-%d')

    @admin.display
    def reserved_tickets(self):
        annotated_capacity = getattr(self, 'annotated_total_capacity', None)
        annotated_reservations = getattr(self, 'annotated_confirmed_reservations', None)
        annotated_guests = getattr(self, 'annotated_confirmed_guests', None)
        if None not in (annotated_capacity, annotated_reservations, annotated_guests):
            reserved = annotated_reservations + annotated_guests
            return f'{reserved}/{annotated_capacity}'

        events = self.event_set.all()
        available = sum(e.reservation_capacity for e in events)
        reserved = sum(e.reservation_count() for e in events)
        return f'{reserved}/{available}'

    @admin.display(boolean=True)
    def reservation_open(self) -> bool:
        return any(e.reservation_open() for e in self.events())

    @admin.display(boolean=True)
    def show_in_preview(self):
        events = self.events()
        return (
            not self.private
            and (
                not len(events)
                or events[-1].begin + timedelta(hours=4) > timezone.now()
            )
        )

    def clean(self):
        from django.core.exceptions import ValidationError
        errors = {}
        if self.ticket_price is not None:
            if self.ticket_price < 0:
                errors['ticket_price'] = 'Price cannot be negative.'
            if self.min_ticket_price is not None and self.min_ticket_price > self.ticket_price:
                errors['min_ticket_price'] = 'Minimum price cannot be greater than ticket price.'
            if self.max_ticket_price is not None and self.max_ticket_price < self.ticket_price:
                errors['max_ticket_price'] = 'Maximum price cannot be less than ticket price.'
        if self.min_ticket_price is not None and self.min_ticket_price < 0:
            errors['min_ticket_price'] = 'Price cannot be negative.'
        if self.max_ticket_price is not None and self.max_ticket_price < 0:
            errors['max_ticket_price'] = 'Price cannot be negative.'
        if self.reservation_price is not None and self.reservation_price < 0:
            errors['reservation_price'] = 'Price cannot be negative.'
        if errors:
            raise ValidationError(errors)

    def get_effective_min_price(self, base_price):
        if self.min_ticket_price is not None:
            return self.min_ticket_price
        if base_price is not None:
            return max(Decimal('5.0'), base_price - Decimal('10.0'))
        return Decimal('5.0')

    def get_effective_max_price(self, base_price):
        if self.max_ticket_price is not None:
            return self.max_ticket_price
        if base_price is not None:
            return base_price + Decimal('10.0')
        return Decimal('15.0')


class UpcomingShow(Show):
    class Meta:
        proxy = True
        verbose_name = "Upcoming show"
        verbose_name_plural = "Upcoming shows"