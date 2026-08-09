""" This source uses Stripe API and dlt to load data such as Customer, Subscription, Event etc. to the database. """

from typing import Any, Dict, Generator, Iterable, Optional, Tuple

import dlt
import stripe
from dlt.sources import DltResource
from pendulum import DateTime

from .helpers import pagination
from .settings import ENDPOINTS, INCREMENTAL_ENDPOINTS


@dlt.source
def stripe_source(
    endpoints: Tuple[str, ...] = ENDPOINTS,
    stripe_secret_key: str = dlt.secrets.value,
    start_date: Optional[DateTime] = None,
    end_date: Optional[DateTime] = None,
) -> Iterable[DltResource]:
    """
    Retrieves data from the Stripe API for the specified endpoints.

    For all endpoints, Stripe API responses do not provide the key "updated",
    so in most cases, we are forced to load the data in 'replace' mode.
    This source is suitable for all types of endpoints, including 'Events', 'Invoice', etc.
    but these endpoints can also be loaded in incremental mode (see source incremental_stripe_source).

    Args:
        endpoints (Tuple[str, ...]): A tuple of endpoint names to retrieve data from. Defaults to most popular Stripe API endpoints.
        stripe_secret_key (str): The API access token for authentication. Defaults to the value in the `dlt.secrets` object.
        start_date (Optional[DateTime]): An optional start date to limit the data retrieved. Format: datetime(YYYY, MM, DD). Defaults to None.
        end_date (Optional[DateTime]): An optional end date to limit the data retrieved. Format: datetime(YYYY, MM, DD). Defaults to None.

    Returns:
        Iterable[DltResource]: Resources with data that was created during the period greater than or equal to 'start_date' and less than 'end_date'.
    """
    stripe.api_key = stripe_secret_key
    # Bumped from the scaffolded default "2022-11-15" (deprecated, warned on
    # every run) to the current version+track string from Stripe's changelog.
    # Note the ".dahlia" release-track suffix is part of the version string,
    # not a stray artifact - a first attempt at this fix dropped it and broke
    # every request with "Invalid Stripe API version".
    stripe.api_version = "2026-07-29.dahlia"

    def stripe_resource(
        endpoint: str,
    ) -> Generator[Dict[Any, Any], Any, None]:
        yield from pagination(endpoint, start_date, end_date)

    for endpoint in endpoints:
        yield dlt.resource(
            stripe_resource,
            name=endpoint,
            write_disposition="replace",
        )(endpoint)
