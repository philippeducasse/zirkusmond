# Plan: Replace ReservationPayment with Payment

Migrating off `django-payments` (`ReservationPayment` extends its `BasePayment`) to a
self-contained `Payment` model driven by a Stripe **PaymentIntent** (`CreatePaymentIntentView` +
`stripe_return` + `StripeWebhookView`).

---

## ▶ Tomorrow's deploy (2026-08-31) — do exactly this, nothing more

**Deploy `main` as it stands. Add nothing, drop nothing, change nothing else.**

What happens on deploy:

- Migration `0011_backfill_payment_from_legacy` runs during `migrate`. It **only INSERTs `Payment`
  rows** — mirrors every confirmed legacy `ReservationPayment` into a `COMPLETED` `Payment`. No
  deletes, no schema changes, does not touch `ReservationPayment`.
- The step-6 code (commit `f3186aa`) now counts those `Payment` rows, so capacity / revenue /
  door-lists stay correct for bookings made through the old flow.
- The `reservations_reservationpayment` table is left **100% intact** — every row, column, real
  timestamp, `extra_data`, billing name, all statuses. `django-payments`, `PAYMENT_MODEL`,
  `ReservationPaymentAdmin` all stay.

### Pre-deploy check (the only task)

Restore a recent prod DB snapshot onto **staging**, run `migrate`, open the admin, spot-check that
a couple of events show the reservation counts / revenue you expect. If they look right, ship.

Optional sanity query against prod beforehand — how many bookings `0011` needs to rescue (if `0`,
the backfill is a harmless no-op):

```
ReservationPayment.objects.filter(status='confirmed', reservation__event__begin__gte=now)
    .exclude(reservation__payment__status='completed').values('reservation').distinct().count()
```

The `ReservationPayment` table stays intact **for this deploy only** — that keeps tomorrow low-risk
and reversible. Removing `django-payments` is the very next step (see below), not a someday.

---

## Status

### Done — new flow (pre-existing)

- **`Payment` model** (`reservations/payments/models.py`): own `Status` enum
  (`pending`/`completed`/`failed`/`refunded`), `payment_method`, `stripe_payment_intent_id`,
  `stripe_session_id`, `custom_ticket_price`, `get_success_url()`/`get_failure_url()`,
  `create_for_reservation()`.
- **Views** (`reservations/payments/views.py`): `CreatePaymentIntentView`, `stripe_return`,
  `StripeWebhookView` (`payment_intent.succeeded` / `payment_failed` / `canceled`,
  `charge.refunded`).
- **Reservation creation** (`reservations/payments/services.py::create_reservation`): creates
  `Reservation` + `Guest`s only; frontend drives the PaymentIntent.
- **Confirmation email**: `reservations/payments/signals.py` — `post_save` on `Payment`, sends on
  `COMPLETED`. **Keep this file** — it is the live email path, not old-flow code.

### Done — this session (all on `main`, not yet pushed)

| commit | what |
| --- | --- |
| `f3186aa` | **Step 6** — `events/models.py` `reservation_count()`, `events/services.py`, `events/admin.py`, `shows/admin.py` all query `Payment` instead of `ReservationPayment`. `PaymentStatus.CONFIRMED` → `Payment.Status.COMPLETED`; reverse lookup `reservation__reservationpayment__` → `reservation__payment__`; field `created` → `created_at`. `events/` + `shows/` no longer import `from payments`. Tests migrated (`make_payment()` helper). |
| `9cd05f1` | **Backfill migration** `0011` — mirrors confirmed legacy `ReservationPayment` → `COMPLETED Payment`. Idempotent, `atomic = False`, `bulk_create` (no confirmation emails fire). Needed because step 6 is a read cutover. |
| `e8941eb` | **Dead provider code deleted** — `stripe_provider.py`, `PAYMENT_VARIANTS` from all four settings modules, the `payments.urls` include. |
| `4f67868` | This plan doc. |

`PaymentAdmin` already exists in `reservations/payments/admin.py` alongside `ReservationPaymentAdmin`.

### Kept for tomorrow's deploy only (removed in the next step)

- `ReservationPayment` model + its table + `ReservationPaymentAdmin`.
- `django-payments` dependency, `"payments"` in `INSTALLED_APPS`, `PAYMENT_MODEL`, and
  `from payments import …` in `reservations/payments/models.py` + `admin.py`.

Kept for good: `PAYMENT_HOST` / `PAYMENT_USES_SSL` — the new `Payment` model's URL methods use
them too. `signals.py` — the live confirmation-email path.

---

## Next step — remove `django-payments`

**The objective is a codebase with no `django-payments`.** Do this once tomorrow's deploy is
verified in prod (days, not months). The only open question is how much of the old
`ReservationPayment` record to preserve — decide that, then execute.

### Data decision: how much of the old record to keep

`0011` already mirrors the counting subset (`reservation`, `total`, `custom_ticket_price`,
`status='completed'`) into `Payment`. Not carried by `0011`: `billing_*` (payer identity — but
the `reservation` FK still reaches the booker), `variant` (card/paypal/bank), real payment date,
`transaction_id` / `token` / `extra_data` (Stripe payload / chargeback evidence), and every
non-`confirmed` row. Germany's ~10-year accounting retention is the reason these matter.

Two ways to keep them, **both ending with `django-payments` gone**:

- **B — keep the `reservationpayment` table as a standalone archive.** A state-only migration
  (`SeparateDatabaseAndState(state_operations=[…], database_operations=[])`) reparents
  `ReservationPayment` from `BasePayment` to a plain model; the table is untouched.
  `ReservationPaymentAdmin` stays as a read-only browser. Full fidelity, `Payment` stays clean,
  two payment tables.

- **C — fold the full record into `Payment`, then drop the table.** Add nullable `legacy_*`
  columns to `Payment` (`legacy_billing_first_name`/`_last_name`/`_email`, `legacy_variant`,
  `legacy_transaction_id`, `legacy_token`, `legacy_extra_data`); rewrite `0011` to copy **all**
  rows (status map: `confirmed→completed`, `refunded→refunded`, `rejected`/`error→failed`,
  `waiting`/`input`/`preauth→pending`) and set `created_at` from the original `created` via a
  `bulk_update` pass. `pg_dump -t reservations_reservationpayment` for the retention file, then
  drop the table. One table; `Payment` carries 7 archive columns; fiddlier migration.

Default to **B** unless a single payment table is genuinely worth the permanent columns on
`Payment`.

### Then, regardless of B or C

- Remove `django-payments` from `pyproject.toml` (+ `uv lock`), `"payments"` from
  `INSTALLED_APPS`, `PAYMENT_MODEL` from `base.py`, all remaining `from payments import …`.
- **Squash `reservations/migrations/0001..0011` into one migration** — `0002` / `0004` / `0005`
  import from `payments` to rebuild state, so the package can't be uninstalled until those are
  collapsed. (Squash also folds in the B/C schema change.)
- Strip the now-dead old-flow methods on `ReservationPayment` (B) or delete the model (C):
  `get_process_url` (references the removed `process_payment` URL), `get_purchased_items`,
  `get_metadata`, `get_failure_url`, `get_success_url`, `validate_custom_price`,
  `from_reservation`. Under B keep the fields + admin-display helpers (`ticket_price`,
  `ticket_count`, `event`).
- `docs/stripe-payment-system.md` — delete or mark superseded.
- Verify: `grep -rn "payments" backend/ --include='*.py'` returns only the local
  `reservations/payments/` package; `uv run manage.py check` clean; full suite green.

---

## Original step-by-step plan (historical)

<details>
<summary>Steps 2–8 as first written — superseded by the status above</summary>

### Step 2 — Extend the `Payment` model
Add `payment_method`; rename `stripe_payment_intent_id` → `stripe_session_id`; add
`get_success_url()` / `get_failure_url()`; write the migration.
_(Done, but the flow stayed on PaymentIntent — both id fields exist.)_

### Step 3 — Build the new Stripe Checkout view
_(Superseded — kept the PaymentIntent view; Checkout not adopted.)_

### Step 4 — Webhook handler for `Payment`
_(Done as `StripeWebhookView`; `payments.urls` include removed in `e8941eb`.)_

### Step 5 — Swap the reservation creation flow
_(Done as `create_reservation` + frontend-driven PaymentIntent.)_

### Step 6 — Update all `ReservationPayment` consumers
_(Done — `f3186aa`.)_

### Step 7 — Replace the `ReservationPayment` admin with a `Payment` admin
_(Done additively — `PaymentAdmin` exists; `ReservationPaymentAdmin` kept as archive admin.)_

### Step 8 — Remove `ReservationPayment` and django-payments
_(Partial: `stripe_provider.py` + `PAYMENT_VARIANTS` + `payments.urls` include removed in
`e8941eb`. `signals.py` kept — it is the live email path. Model + table + `django-payments`
removal is the "archive decision" above, no deadline.)_

</details>
