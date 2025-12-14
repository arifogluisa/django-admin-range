"""
Reusable Django admin range filters (date, datetime, numeric).
"""

from .filters import (
    DateRangeFilter,
    DateTimeRangeFilter,
    NumericRangeFilter,
    date_range_filter,
    datetime_range_filter,
    numeric_range_filter,
)

__all__ = [
    "DateRangeFilter",
    "DateTimeRangeFilter",
    "NumericRangeFilter",
    "date_range_filter",
    "datetime_range_filter",
    "numeric_range_filter",
]

# Django < 3.2 compatibility
default_app_config = "django_admin_range.apps.DjangoAdminRangeConfig"
