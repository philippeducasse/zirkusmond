# Stripe Payment System Documentation

## Overview

The reservation system integrates Stripe for payment processing. This document covers the complete payment flow from initialization through confirmation or failure.

## Architecture

### Components

1. **StripeProviderV3** (`stripe_provider.py`)
   - Custom provider extending django-payments
   - Handles checkout session creation and webhook processing

2. **ReservationPayment Model** (`reservations/models.py`)
   - Stores payment information and status
   - Tracks reservation association

3. **Signal Handler** (`signals.py`)
   - Listens for payment status changes
   - Sends confirmation/rejection emails

4. **Webhook Endpoint** (`views.py`)
   - Receives Stripe webhook events
   - Routes to provider for processing

## Payment Initialization Flow

### 1. Create Payment
```python
reservation = Reservation.objects.create(...)
payment = ReservationPayment.objects.create(
    reservation=reservation,
    variant='stripe',
    description='Show ticket',
    total=reservation.price,
    currency='EUR',
    billing_email=reservation.email
)
```

Initial status: `WAITING`

### 2. Display Checkout Form
```python
# In payment view
form = payment.get_form()  # Calls StripeProviderV3.get_form()
```

**What happens in get_form():**
- Creates a Stripe checkout session with:
  - Line items (tickets/products)
  - Success/cancel URLs
  - Customer email
  - Client reference ID (payment token for webhook lookup)
- Raises `RedirectNeeded` to send user to Stripe checkout

### 3. User Completes/Abandons Checkout
- **Success**: User completes payment on Stripe
- **Abandon**: User closes browser or session expires (24 hours)
- **Cancel**: User clicks cancel button

Stripe sends webhook events for all outcomes.

## Webhook Processing

### Webhook Flow

```
Stripe Event → Django View (/payments/stripe-webhook/)
  ↓
static_callback() routes to StripeProviderV3.process_data()
  ↓
Event type determines payment status change
  ↓
Payment status changes → Signal triggered
  ↓
Signal handler sends email (if applicable)
```

### Event Types and Handling

#### Success Events

**`checkout.session.completed`**
- Triggered when checkout session completes
- Checks `payment_status` field in session object
- If `"paid"`: Payment status → `CONFIRMED`
- Triggers: ✅ Confirmation email sent

#### Failure Events

**`charge.failed`**
- Triggered when card charge fails
- Examples: Insufficient funds, card blocked, etc.
- Payment status → `REJECTED`
- Triggers: ✅ Rejection email sent

**`payment_intent.payment_failed`**
- Triggered when payment intent fails
- Examples: 3D Secure/SCA denied, issuer declined, etc.
- Payment status → `REJECTED`
- Triggers: ✅ Rejection email sent

**`checkout.session.async_payment_failed`**
- Triggered when async payment explicitly fails
- Examples: Bank transfer rejected, etc.
- Payment status → `REJECTED`
- Triggers: ✅ Rejection email sent

#### Abandoned Session

**`checkout.session.expired`**
- Triggered when checkout session expires (24 hours default)
- Indicates user abandoned payment, NOT a payment failure
- Payment status → `ERROR`
- Triggers: ❌ **NO email sent** (intentional - don't email about abandoned sessions)

## Payment Status States

| Status | Meaning | Email Sent | Next States |
|--------|---------|-----------|------------|
| `WAITING` | Awaiting payment | ❌ | CONFIRMED, REJECTED, ERROR |
| `CONFIRMED` | Payment succeeded | ✅ Confirmation | (final) |
| `REJECTED` | Payment failed | ✅ Rejection | (final) |
| `ERROR` | Session expired/abandoned | ❌ | (final) |
| `PREAUTH` | Preauthorized (unused) | ❌ | |
| `REFUNDED` | Refunded | ❌ | |

## Email Notifications

### Confirmation Email
- **Triggered**: Payment status → `CONFIRMED`
- **Recipient**: `reservation.email`
- **Handler**: `on_payment_status_changed` signal
- **Action**: Calls `services.send_confirmation_mail(reservation)`

### Rejection Email
- **Triggered**: Payment status → `REJECTED`
- **Recipient**: `reservation.email`
- **Subject**: "Payment Failed - Please Try Again"
- **Body**: Includes:
  - Show title
  - Admission date
  - Order ID (payment PK)
  - Request to retry or contact support

Example rejection email:
```
Subject: Payment Failed - Please Try Again

Your payment for "Circus Show" on 2026-06-15 failed.

Please try again or contact us for assistance.

Order ID: a1a7027a-f89c-4706-9ac1-f9815e8c7c8f
```

## Error Handling

### Webhook Error Handling

The webhook endpoint in `views.py` catches exceptions and:
1. Logs the error with full traceback
2. Extracts payment token from webhook payload (if available)
3. Sends "Payment Processing" notification email to customer
4. Returns HTTP 500 to Stripe (Stripe will retry)

```python
except Exception as e:
    logger.error("stripe webhook error: %s", e, exc_info=True)
    # Extract payment and send notification email
    send_mail(
        subject="Payment Processing - Please Wait",
        message="We're processing your payment. If you don't receive..."
    )
    return HttpResponse(status=500)
```

### Expected Exceptions

- Missing session in webhook: `PaymentError(code=400, message="session not present")`
- Missing object in webhook: `PaymentError(code=400, message="object not present in event")`

## Testing

### Test Class: `StripePaymentRejectionEmailTest`

**Setup**: Creates test payment and provides webhook event posting

#### Test Cases

**1. `test_confirmed_payment_sends_confirmation_email`**
- Posts `checkout.session.completed` event with `payment_status="paid"`
- Asserts: Payment status → `CONFIRMED`
- Asserts: Confirmation email sent

**2. `test_rejected_payment_sends_failure_email`**
- Posts `checkout.session.async_payment_failed` event
- Asserts: Payment status → `REJECTED`
- Asserts: Rejection email sent with "Failed" in subject

**3. `test_expired_session_does_not_send_email`**
- Posts `checkout.session.expired` event
- Asserts: NO email sent
- Asserts: Payment status → `ERROR`

**4. `test_charge_failed_sends_rejection_email`**
- Posts `charge.failed` event
- Asserts: Payment status → `REJECTED`
- Asserts: Rejection email sent

**5. `test_payment_intent_payment_failed_sends_rejection_email`**
- Posts `payment_intent.payment_failed` event
- Asserts: Payment status → `REJECTED`
- Asserts: Rejection email sent

**6. `test_rejection_email_includes_order_id`**
- Verifies rejection email body includes payment ID

**7. `test_rejection_email_includes_event_info`**
- Verifies rejection email body includes show title

### Running Tests

```bash
python manage.py test reservations.payments.tests.StripePaymentRejectionEmailTest
```

All tests should pass: 7 tests, 0 failures

## Stripe Dashboard Configuration

### 1. API Keys
- Navigate: Developers → API Keys
- Copy "Secret key" and "Publishable key"
- Set in environment: `STRIPE_TOKEN`, `STRIPE_PUBLIC_KEY`

### 2. Webhook Endpoint
- Navigate: Developers → Webhooks
- Click "Add endpoint"
- URL: `https://your-domain.com/payments/stripe-webhook/`
- Events to enable:
  - `checkout.session.completed`
  - `checkout.session.async_payment_succeeded`
  - `checkout.session.expired`
  - `checkout.session.async_payment_failed`
  - `charge.failed`
  - `payment_intent.payment_failed`

### 3. Signing Secret
- Copy webhook signing secret
- Set in environment: `STRIPE_HOOK_TOKEN`
- Used to verify webhook authenticity

### 4. Testing Webhooks
- Use Stripe CLI for local testing:
  ```bash
  stripe listen --forward-to localhost:8000/payments/stripe-webhook/
  stripe trigger checkout.session.completed
  ```

## Implementation Files

### `stripe_provider.py`
- Custom StripeProviderV3 class
- `get_form()`: Creates checkout session
- `process_data()`: Handles webhook events

### `signals.py`
- `on_payment_status_changed()`: Signal handler
- Sends emails based on status change
- Only sends rejection email for `REJECTED` status (not `ERROR`)

### `views.py`
- `stripe_webhook()`: Webhook endpoint
- Routes to `static_callback()` for processing
- Error handling and fallback notifications

### `tests.py`
- `StripePaymentRejectionEmailTest`: Comprehensive webhook tests

## Payment Flow Diagram

```
┌─────────────────────────┐
│ Create ReservationPayment│
│ Status: WAITING         │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Get Payment Form        │
│ (StripeProviderV3)      │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Redirect to Stripe      │
│ Checkout Session        │
└────────────┬────────────┘
             │
     ┌───────┴───────┐
     │               │
     ▼               ▼
┌──────────┐  ┌──────────────┐
│ Success  │  │ Failure/     │
│          │  │ Abandon      │
└────┬─────┘  └────┬─────────┘
     │             │
     ▼             ▼
┌──────────────────────────┐
│ Stripe Webhook Event     │
│ (checkout.session.*)     │
└────┬─────────────────────┘
     │
     ▼
┌──────────────────────────┐
│ StripeProviderV3         │
│ .process_data()          │
└────┬─────────────────────┘
     │
   ┌─┴─────────────┬──────────────┐
   │               │              │
   ▼               ▼              ▼
CONFIRMED      REJECTED        ERROR
(paid)      (charge failed) (session expired)
   │               │              │
   ▼               ▼              ▼
✅ Confirm    ✅ Rejection    ❌ No Email
   Email         Email
```

## Key Design Decisions

### 1. ERROR Status for Abandoned Sessions
- **Why**: Abandoned sessions are not payment failures - they're just incomplete transactions
- **Result**: `ERROR` status doesn't trigger rejection email
- **Alternative rejected**: Using `REJECTED` status would send confusing failure emails

### 2. Signal-Based Email Dispatch
- **Why**: Decouples webhook handling from email logic
- **Result**: Email is sent when status changes, not during webhook processing
- **Benefit**: Can send emails for other status changes in future (e.g., refunds)

### 3. Explicit Event Types for Failures
- **Why**: Need to distinguish between "payment failed" and "session abandoned"
- **Result**: Handle `charge.failed`, `payment_intent.payment_failed`, and `checkout.session.async_payment_failed` separately from `checkout.session.expired`
- **Benefit**: Send rejection email only for real failures

## Troubleshooting

### Webhooks Not Received
1. Check webhook endpoint URL in Stripe Dashboard
2. Verify domain is publicly accessible (webhooks won't work on localhost without tunnel)
3. Use `stripe listen` command locally for testing
4. Check Django logs for webhook errors

### Email Not Sent
1. Check SMTP settings in Django settings
2. Check signal logs for email sending attempts
3. Verify reservation has valid email address
4. Check spam/junk folder

### Payment Status Not Changing
1. Verify webhook is being received (check logs)
2. Check `process_data()` logic for event type
3. Verify `change_status()` is being called
4. Check for exceptions in webhook processing

### Wrong Email Sent
1. Verify event type in webhook (check Stripe Dashboard event logs)
2. Check `payment_status` field in session object (for success events)
3. Verify signal handler conditions