# Plan: Replace ReservationPayment with Payment

Migrating off `django-payments` (`ReservationPayment` extends its `BasePayment`) to a
self-contained `Payment` model driven directly by a Stripe **PaymentIntent** (not Checkout
Sessions — the original plan below assumed Checkout; the implementation went with PaymentIntent +
`stripe_return` + `StripeWebhookView`).

---

## Status (2026-08-30)

### Done — new flow (pre-existing, implemented before this plan was revised)

- **`Payment` model** (`reservations/payments/models.py`): own `Status` enum
  (`pending`/`completed`/`failed`/`refunded`), `payment_method`, `stripe_payment_intent_id`,
  `stripe_session_id`, `custom_ticket_price`, `get_success_url()`/`get_failure_url()`,
  `create_for_reservation()`.
- **Views** (`reservations/payments/views.py`): `CreatePaymentIntentView`, `stripe_return`,
  `StripeWebhookView` (`payment_intent.succeeded/​payment_failed/​canceled`, `charge.refunded`).
- **Reservation creation** (`reservations/payments/services.py::create_reservation`): creates
  `Reservation` + `Guest`s only; `reserve` view returns `reservation_id`, frontend drives the
  PaymentIntent.
- **Confirmation email**: `reservations/payments/signals.py` — `post_save` on `Payment`, sends on
  `COMPLETED`. **Keep this file** (it is the live email path, not old-flow code).

### Done — this session

- **Step 6 — consumers repointed to `Payment`** (commit `f3186aa`): `events/models.py`
  `reservation_count()`, `events/services.py` (`send_confirmation_mail`, `purge_old_payments`,
  `purge_orphan_reservations`), `events/admin.py`, `shows/admin.py`. Status vocab
  `PaymentStatus.CONFIRMED` → `Payment.Status.COMPLETED`; reverse relation
  `reservation__reservationpayment__` → `reservation__payment__`; field `created` → `created_at`.
  `events/` and `shows/` no longer import `from payments`. Tests migrated (`make_payment()` helper).
- **Backfill migration** (commit `9cd05f1`): `reservations/migrations/0011_backfill_payment_from_legacy.py`
  mirrors every confirmed legacy `ReservationPayment` into a `COMPLETED` `Payment` (idempotent,
  `atomic = False`, `bulk_create` so no confirmation emails fire). Needed because step 6 is a
  **read cutover** — without it, bookings made through the old flow drop out of every capacity /
  revenue / door-list count the moment the deploy goes live (oversell risk; people book months
  ahead).
- **Step 8 (partial) — dead provider code deleted** (commit `e8941eb`):
  `reservations/payments/stripe_provider.py`, `PAYMENT_VARIANTS` from all four settings modules,
  the `payments.urls` include in `reservations/payments/urls.py`.
- **`PaymentAdmin`** already exists in `reservations/payments/admin.py` alongside the old admin.

---

## Decision change: `ReservationPayment` is kept as a long-lived archive

The original plan (step 8) dropped the `reservationpayment` table outright. **We are not doing
that.** Confirmed legacy rows still point at events months in the future; the two models must
coexist through that window. `ReservationPayment` + its table stay as a **read-only archive**:

- `ReservationPaymentAdmin` stays (browse-only history).
- `django-payments` dependency, `PAYMENT_MODEL`, and `from payments import …` in
  `reservations/payments/models.py` + `admin.py` **stay** while `ReservationPayment(BasePayment)`.
- `PAYMENT_HOST` / `PAYMENT_USES_SSL` **stay** — used by `Payment.get_success_url()` /
  `get_failure_url()` too.

---

## Remaining work

### 1. Deploy to prod (target 2026-08-31)

- Run the diagnostic against prod first:
  ```
  ReservationPayment.objects.filter(status='confirmed',
      reservation__event__begin__gte=now).exclude(
      reservation__payment__status='completed').values('reservation').distinct().count()
  ```
  This is how many bookings the backfill needs to rescue. If it's 0, the backfill is a no-op and
  step 6 is safe on its own.
- Restore a recent prod snapshot onto **staging**, run `migrate`, eyeball a few events'
  `reserved_tickets` / revenue in the admin vs. expectations.
- Deploy `main`. Migration `0011` runs in the same `migrate` step, before new code serves traffic.

### 2. Coexistence window (~months)

Both models live. `Payment` = all live bookings + backfilled history. `ReservationPayment` =
frozen archive, read by nothing except its admin.

- Known caveat: backfilled `Payment.created_at` = migration time, so `purge_old_payments`
  (6-month cutoff) won't touch those rows until ~2027-03. Harmless; revisit if it matters.

### 3. Final teardown — when no confirmed `ReservationPayment` points at a future event

- Cut `ReservationPayment` loose from `django-payments`: either de-parent to a plain
  `models.Model` / `managed = False` model, or drop it from Django's model state via
  `migrations.SeparateDatabaseAndState(state_operations=[DeleteModel], database_operations=[])`.
  **The table is kept** either way (optionally `pg_dump -t reservations_reservationpayment` first).
- Remove `django-payments` from `pyproject.toml`, `"payments"` from `INSTALLED_APPS`,
  `PAYMENT_MODEL` from `base.py`, and the remaining `from payments import …` lines.
- Strip the now-dead old-flow methods on `ReservationPayment`: `get_process_url` (references the
  removed `process_payment` URL name), `get_purchased_items`, `get_metadata`, `get_failure_url`,
  `get_success_url`, `validate_custom_price`, `from_reservation`. Keep the fields and the
  admin-display helpers (`ticket_price`, `ticket_count`, `event`).
- Decide `ReservationPaymentAdmin`'s fate (keep as read-only archive admin, or drop with the
  data).
- `docs/stripe-payment-system.md` describes the old flow — delete or mark superseded.

---

## Original step-by-step plan (historical, for reference)

<details>
<summary>Steps 2–8 as first written — kept for context; superseded by the status above</summary>

### Step 2 — Extend the `Payment` model
Add `payment_method`; rename `stripe_payment_intent_id` → `stripe_session_id`; add
`get_success_url()` / `get_failure_url()`; write the migration.
_(Done, but the flow stayed on PaymentIntent — both `stripe_payment_intent_id` and
`stripe_session_id` exist.)_

### Step 3 — Build the new Stripe Checkout view
Replace the stub `create_payment_intent` with a `create_checkout_session` view.
_(Superseded — kept the PaymentIntent view; Checkout was not adopted.)_

### Step 4 — Webhook handler for `Payment`
New webhook view replacing `StripeProviderV3.process_data`; wire into
`reservations/payments/urls.py`, replacing the `payments.urls` include. _(Done as
`StripeWebhookView`; `payments.urls` include removed in `e8941eb`.)_

### Step 5 — Swap the reservation creation flow
`reservations/payments/services.py` creates a `Payment` instead of `ReservationPayment`; `reserve`
redirects appropriately. _(Done as `create_reservation` + frontend-driven PaymentIntent.)_

### Step 6 — Update all `ReservationPayment` consumers
`events/services.py`, `events/admin.py`, `shows/admin.py`, `events/models.py` → query `Payment`.
Status `PaymentStatus.CONFIRMED` → `"completed"`, `REJECTED` → `"failed"`. _(Done — `f3186aa`.)_

### Step 7 — Replace the `ReservationPayment` admin with a `Payment` admin
Rewrite `ReservationPaymentAdmin` as `PaymentAdmin`. _(Done additively — `PaymentAdmin` exists;
`ReservationPaymentAdmin` is **kept** as the archive admin, not removed.)_

### Step 8 — Remove `ReservationPayment` and django-payments
Drop the `reservationpayment` table; remove `PAYMENT_*` settings, `django-payments`,
`stripe_provider.py`, `signals.py`, the `payments.urls` include, all `from payments import`.
_(Revised: table is **kept** as an archive; `stripe_provider.py` + `PAYMENT_VARIANTS` +
`payments.urls` include removed in `e8941eb`; `signals.py` is **kept** as the live email path;
the rest waits for the teardown in "Remaining work" §3.)_

</details>
