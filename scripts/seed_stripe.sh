#!/usr/bin/env bash
set -euo pipefail

# Seeds fake Stripe test-mode customers + charges via the real Stripe API
# (no Stripe CLI/dashboard steps needed - just a secret key).
: "${STRIPE_SECRET_KEY:?Set STRIPE_SECRET_KEY to your sk_test_... key first}"

# Range 1-115: creates (fake1-fake115). Deliberately pushed past 100 records
# so dlt's pagination (has_more/starting_after) actually gets exercised across
#multiple pages, instead of everything fitting in one API response.
for i in $(seq 1 115); do
  # The card (source=tok_visa) must be attached at customer-creation time,
  # not passed on the /charges call below - passing `customer` + `source`
  # together on a charge tells Stripe "attach this card to that customer,"
  # which fails with resource_missing for a brand-new customer with no card.
  customer_id=$(curl -s https://api.stripe.com/v1/customers \
    -u "${STRIPE_SECRET_KEY}:" \
    -d email="fake${i}@example.com" \
    -d name="Fake Customer ${i}" \
    -d source=tok_visa \
    | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

  # No `source` here - Stripe uses the customer's default card (attached above).
  curl -s https://api.stripe.com/v1/charges \
    -u "${STRIPE_SECRET_KEY}:" \
    -d amount=$(( (RANDOM % 5000) + 500 )) \
    -d currency=usd \
    -d customer="${customer_id}" \
    -d description="Fake charge ${i}" > /dev/null

  echo "Created ${customer_id} + 1 charge"
done
