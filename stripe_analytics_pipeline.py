from typing import Optional, Tuple

import dlt
from pendulum import DateTime
from stripe_analytics import (
    ENDPOINTS,
    INCREMENTAL_ENDPOINTS,
    stripe_source,
)


def load_data(
    endpoints: Tuple[str, ...] = ENDPOINTS + INCREMENTAL_ENDPOINTS,
    start_date: Optional[DateTime] = None,
    end_date: Optional[DateTime] = None,
) -> None:
    """
    This demo script uses the resources with non-incremental
    loading based on "replace" mode to load all data from provided endpoints.

    Args:
        endpoints: A tuple of endpoint names to retrieve data from. Defaults to most popular Stripe API endpoints.
        start_date: An optional start date to limit the data retrieved. Defaults to None.
        end_date: An optional end date to limit the data retrieved. Defaults to None.
    """
    pipeline = dlt.pipeline(
        pipeline_name="stripe_analytics",
        destination='duckdb',
        dataset_name="stripe_updated",
    )
    source = stripe_source(
        endpoints=endpoints, start_date=start_date, end_date=end_date
    )
    load_info = pipeline.run(source)
    print(load_info)


if __name__ == "__main__":
    # Scoped down from the default (all 9 endpoints) to just 2 for MVP + pagination check
    load_data(endpoints=("Customer", "Charge",))
