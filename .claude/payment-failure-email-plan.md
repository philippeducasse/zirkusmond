# Plan: Gate the payment-failure email on "user was shown success first"

## Context

`on_payment_status_changed` (`reservations/payments/signals.py`) sends a "Payment
Failed" email any time `Payment.status` becomes `FAILED`. `Payment.status` is only
ever written by `StripeWebhookView.post` (`reservations/payments/views.py`), in
response to Stripe's `payment_intent.payment_failed` / `payment_intent.canceled`
events — and that webhook fires for **every** failed intent, whether the decline was
synchronous (card declined instantly — the user is shown `/payment/failure` right
away, either by `StripePaymentForm.tsx` resolving in-page or by the `stripe_return`
redirect view) or asynchronous (the intent enters `processing`, the frontend treats
that as success and shows `/payment/success`, and the actual decline — e.g. a
bank/ACH/SEPA failure — arrives later via webhook).

The failure email is meant to fire only in the second case: the user already
believes the payment succeeded and needs to be told it actually failed. Today
nothing distinguishes the two cases, so the email also goes out when the user is
looking at the failure page and already knows.

**Chosen approach:** use Stripe's `payment_intent.processing` webhook event as the
signal that the intent went through the "initial checks passed" path. A synchronous
decline never enters `processing` — Stripe fails it directly — so a `Payment` that
reaches `FAILED` without ever having seen a `processing` event was shown failure
directly, and the email should be skipped. A `Payment` that saw `processing` first
(the delayed-decline case) gets the email as before. This is backend-only: no
frontend changes, no new endpoints.

**Caveat:** this depends on the Stripe webhook endpoint being subscribed to the
`payment_intent.processing` event type in the Stripe Dashboard/CLI config (not
visible from this repo). If it isn't enabled, the failure email simply never fires
for genuine delayed-decline cases — a safe, silent false-negative rather than
today's false-positive — worth a quick check in the Stripe webhook settings after
deploying.

---

## Step 1 — Add `processing_at` to `Payment`

In `reservations/payments/models.py`, add next to `created_at`:

```python
processing_at = models.DateTimeField(null=True, blank=True)
```

Records when Stripe told us the intent entered `processing` (i.e. initial checks
passed and the frontend would have shown the success page). Generate the migration
with `python manage.py makemigrations reservations`.

---

## Step 2 — Handle `payment_intent.processing` in the webhook, and pin down `update_fields`

In `StripeWebhookView.post` (`reservations/payments/views.py`):

- Add a branch for `event["type"] == "payment_intent.processing"`, mirroring the
  existing `payment_intent.succeeded` branch (lines 166–186): look up the `Payment`
  by `stripe_payment_intent_id`, set `processing_at = timezone.now()`, save, log,
  404 if not found.
- Change the three existing status-writing saves (`payment.status = ...;
  payment.save()` at lines 175–176, 194–195, 214–215) to
  `payment.save(update_fields=["status"])`, and the new `processing_at` save to
  `payment.save(update_fields=["processing_at"])`.
- Also give `stripe_return`'s incidental `payment.save()` (line 92, updating
  `payment_method`) an explicit `update_fields=["payment_method"]`.

This is needed so the signal (Step 3) can tell *which* save actually changed
`status` vs. an incidental save. Without it, a `Payment` that's already `FAILED`
could have its failure email re-sent by an unrelated later save — a pre-existing
latent bug this change would otherwise make easier to trigger, since we're adding
another non-status save path (`processing_at`).

---

## Step 3 — Gate the email in `on_payment_status_changed`

In `reservations/payments/signals.py`:

- Accept `update_fields` and skip entirely when it's provided and doesn't include
  `"status"`:
  ```python
  if update_fields is not None and "status" not in update_fields:
      return
  ```
- In the `FAILED` branch, only send the email when `instance.processing_at` is set;
  otherwise log-and-skip:
  ```python
  elif instance.status == Payment.Status.FAILED:
      if not instance.processing_at:
          logger.info(
              "payment failure email skipped for payment=%s: no processing event seen "
              "(user was likely shown the failure page directly)",
              payment_id,
          )
          return
      try:
          send_mail(...)
      ...
  ```
- Leave the `COMPLETED` branch otherwise unchanged.

---

## Step 4 — Tests

`StripeWebhookViewTest` in `reservations/payments/tests.py` already has a
`_construct_event` helper (line 297) and patches `stripe.Webhook.construct_event`.
Add, following the existing style:

- `test_payment_intent_processing_sets_processing_at` — send a
  `payment_intent.processing` event, assert `Payment.objects.get(...).processing_at`
  is set.
- `test_failure_email_sent_when_processing_seen_first` — send a `processing` event
  then a `payment_failed` event, assert `mail.outbox` has one message.
- `test_failure_email_not_sent_without_processing` — send `payment_intent.payment_failed`
  directly (no prior `processing` event), assert `mail.outbox` is empty.
- `test_confirmation_email_still_sent_on_completed` — regression check that the
  `COMPLETED` path is untouched.

No existing test currently asserts on `mail.outbox` for this signal, so these are
new coverage, not modifications of existing tests.

---

## Verification

- `python manage.py test reservations.payments`
- Stripe CLI: `stripe trigger payment_intent.processing` then
  `stripe trigger payment_intent.payment_failed` against the local webhook endpoint
  → confirm an email is queued (console/log backend). Triggering
  `payment_intent.payment_failed` alone → confirm no email.
- After deploy, confirm in the Stripe Dashboard webhook endpoint settings that
  `payment_intent.processing` is one of the subscribed event types.
