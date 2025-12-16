import contextlib
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Union

from django.conf import settings
from django.contrib import admin
from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.utils import timezone


class DateRangeFilter(admin.SimpleListFilter):
    """
    A custom date range filter
    """

    template = "admin/django_admin_range/date_range_filter.html"

    def __init__(self, request, params, model, model_admin):
        self.field_name = self.parameter_name
        self.lookup_kwarg_gte = f"{self.field_name}__gte"
        self.lookup_kwarg_lte = f"{self.field_name}__lte"

        self.default_gte = None
        self.default_lte = None

        # Get values from params (may be QueryDict)
        self.date_gte = params.get(self.lookup_kwarg_gte, "")
        self.date_lte = params.get(self.lookup_kwarg_lte, "")

        # Handle list values (multiple inputs with the same name)
        def _first_nonempty(val):
            if isinstance(val, list):
                for v in val:
                    if v:
                        return v
                return ""
            return val or ""

        self.date_gte = _first_nonempty(self.date_gte)
        self.date_lte = _first_nonempty(self.date_lte)

        # Normalize whitespace
        if isinstance(self.date_gte, str):
            self.date_gte = self.date_gte.strip()
        if isinstance(self.date_lte, str):
            self.date_lte = self.date_lte.strip()

        # Remove empty params to avoid duplicate empty values causing admin errors
        try:
            mutable = getattr(params, "_mutable", True)
            params._mutable = True
            if not self.date_gte and self.lookup_kwarg_gte in params:
                del params[self.lookup_kwarg_gte]
            if not self.date_lte and self.lookup_kwarg_lte in params:
                del params[self.lookup_kwarg_lte]
            params._mutable = mutable
        except Exception:
            # If params is a plain dict, ignore
            if not self.date_gte:
                params.pop(self.lookup_kwarg_gte, None)
            if not self.date_lte:
                params.pop(self.lookup_kwarg_lte, None)

        super().__init__(request, params, model, model_admin)

    def has_output(self):
        return True

    def lookups(self, request, model_admin):
        return ()

    def queryset(self, request, queryset):  # sourcery skip: use-named-expression
        filters = {}

        if self.date_gte:
            with contextlib.suppress(ValueError, TypeError):
                date_gte = self._parse_date(self.date_gte)
                if date_gte:
                    filters[f"{self.field_name}__gte"] = date_gte

        if self.date_lte:
            with contextlib.suppress(ValueError, TypeError):
                date_lte = self._parse_date(self.date_lte)
                if date_lte:
                    filters[f"{self.field_name}__lte"] = date_lte

        return queryset.filter(**filters) if filters else queryset

    def _parse_date(self, date_string):
        """Parse date string to date object"""
        if not date_string:
            return None

        # Handle list (Django 5.x can pass list)
        if isinstance(date_string, list):
            date_string = date_string[0] if date_string else ""

        if not date_string:
            return None

        # Try different date formats
        date_formats = [
            "%Y-%m-%d",  # ISO format
            "%d.%m.%Y",  # European format
            "%d/%m/%Y",  # Alternative European
            "%m/%d/%Y",  # US format
        ]

        for fmt in date_formats:
            try:
                return datetime.strptime(date_string, fmt).date()
            except ValueError:
                continue

        return None

    def choices(self, changelist):
        yield {
            "title": self.title,
            "field_name": self.field_name,
            "date_gte": self.date_gte,
            "date_lte": self.date_lte,
            "query_string": changelist.get_query_string(
                remove=[self.lookup_kwarg_gte, self.lookup_kwarg_lte]
            ),
        }

    def expected_parameters(self):
        return [self.lookup_kwarg_gte, self.lookup_kwarg_lte]


def date_range_filter(field_name: str, title: Union[str, None] = None):
    """
    Factory function to create DateRangeFilter for a specific field

    Usage:
        list_filter = (
            date_range_filter('created_at', 'Creation Date'),
        )
    Note:
        The field must be a DateField. And second argument is optional.
        If you don't provide the title, it will try to use the field verbose_name or the field name as the title.
    """

    class DateRangeFilterWrapper(DateRangeFilter):
        parameter_name = field_name

        def __init__(self, request, params, model, model_admin):
            # Field type check
            field = None
            try:
                field = model._meta.get_field(field_name)
            except FieldDoesNotExist as e:
                raise FieldDoesNotExist(
                    f"date_range_filter: {model.__name__} model does not have field '{field_name}'"
                ) from e
            except Exception as e:
                raise RuntimeError(f"date_range_filter: unexpected error: {e}") from e

            if not isinstance(field, (models.DateField)):
                raise TypeError(
                    f"date_range_filter: field '{field_name}' is not a DateField/DateTimeField"
                )

            # Prefer explicit title, else model field verbose_name, else fallback
            if title:
                self.title = title.title()
            else:
                verbose_name = getattr(field, "verbose_name", None)
                if verbose_name:
                    self.title = verbose_name.title()
                else:
                    self.title = field_name.replace("_", " ").title()

            super().__init__(request, params, model, model_admin)

    return DateRangeFilterWrapper


class DateTimeRangeFilter(admin.SimpleListFilter):
    """
    A datetime range filter for DateTimeField values.
    """

    template = "admin/django_admin_range/datetime_range_filter.html"

    def __init__(self, request, params, model, model_admin):
        self.field_name = self.parameter_name
        self.lookup_kwarg_gte = f"{self.field_name}__gte"
        self.lookup_kwarg_lte = f"{self.field_name}__lte"

        self.datetime_gte = params.get(self.lookup_kwarg_gte, "")
        self.datetime_lte = params.get(self.lookup_kwarg_lte, "")

        def _first_nonempty(val):
            if isinstance(val, list):
                for v in val:
                    if v:
                        return v
                return ""
            return val or ""

        self.datetime_gte = _first_nonempty(self.datetime_gte)
        self.datetime_lte = _first_nonempty(self.datetime_lte)

        if isinstance(self.datetime_gte, str):
            self.datetime_gte = self.datetime_gte.strip()
        if isinstance(self.datetime_lte, str):
            self.datetime_lte = self.datetime_lte.strip()

        # Drop empty values to avoid duplicate blank params
        try:
            mutable = getattr(params, "_mutable", True)
            params._mutable = True
            if not self.datetime_gte and self.lookup_kwarg_gte in params:
                del params[self.lookup_kwarg_gte]
            if not self.datetime_lte and self.lookup_kwarg_lte in params:
                del params[self.lookup_kwarg_lte]
            params._mutable = mutable
        except Exception:
            if not self.datetime_gte:
                params.pop(self.lookup_kwarg_gte, None)
            if not self.datetime_lte:
                params.pop(self.lookup_kwarg_lte, None)

        # Parse once and reuse for display/queryset
        self.parsed_datetime_gte = (
            self._parse_datetime(self.datetime_gte, is_end=False)
            if self.datetime_gte
            else None
        )
        self.parsed_datetime_lte = (
            self._parse_datetime(self.datetime_lte, is_end=True)
            if self.datetime_lte
            else None
        )

        super().__init__(request, params, model, model_admin)

    def has_output(self):
        return True

    def lookups(self, request, model_admin):
        return ()

    def queryset(self, request, queryset):
        filters = {}

        if self.parsed_datetime_gte:
            filters[f"{self.field_name}__gte"] = self.parsed_datetime_gte

        if self.parsed_datetime_lte:
            filters[f"{self.field_name}__lte"] = self.parsed_datetime_lte

        return queryset.filter(**filters) if filters else queryset

    def _make_dt_aware(self, value: datetime):
        """
        Convert naive datetime to aware using current timezone when USE_TZ is on.
        """
        if value is None:
            return None

        if not settings.USE_TZ:
            return value

        try:
            tz = timezone.get_current_timezone()
            if timezone.is_naive(value):
                return timezone.make_aware(value, tz)
            return value.astimezone(tz)
        except Exception:
            # If conversion fails, return original to avoid breaking filtering.
            return value

    def _parse_datetime(self, value, is_end: bool = False):
        """
        Parse datetime strings to naive datetime.
        - Supports datetime-local input values and a few common formats.
        - If only a date is provided, start/end of day is applied for gte/lte.
        """
        if not value:
            return None

        if isinstance(value, list):
            value = value[0] if value else ""

        if not value:
            return None

        candidates = [
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
        ]

        for fmt in candidates:
            try:
                dt = datetime.strptime(value, fmt)
                return self._make_dt_aware(dt)
            except ValueError:
                continue

        # Date-only fallback
        for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%m/%d/%Y"):
            try:
                dt = datetime.strptime(value, fmt)
                dt = dt.replace(
                    hour=23 if is_end else 0,
                    minute=59 if is_end else 0,
                    second=59 if is_end else 0,
                    microsecond=999999 if is_end else 0,
                )
                return self._make_dt_aware(dt)
            except ValueError:
                continue

        return None

    def choices(self, changelist):
        def _fmt(dt):
            if not dt:
                return ""
            if settings.USE_TZ and timezone.is_aware(dt):
                dt = timezone.localtime(dt)
            return dt.strftime("%d-%m-%y %H:%M")

        datetime_gte_display = _fmt(self.parsed_datetime_gte)
        datetime_lte_display = _fmt(self.parsed_datetime_lte)
        yield {
            "title": self.title,
            "field_name": self.field_name,
            "datetime_gte": self.datetime_gte,
            "datetime_lte": self.datetime_lte,
            "datetime_gte_display": datetime_gte_display,
            "datetime_lte_display": datetime_lte_display,
            "query_string": changelist.get_query_string(
                remove=[self.lookup_kwarg_gte, self.lookup_kwarg_lte]
            ),
        }

    def expected_parameters(self):
        return [self.lookup_kwarg_gte, self.lookup_kwarg_lte]


def datetime_range_filter(field_name: str, title: Union[str, None] = None):
    """
    Factory for DateTimeRangeFilter bound to a specific DateTimeField.
    Usage:
        list_filter = (
            datetime_range_filter('created_at', 'Creation Date'),
        )
    Note:
        The field must be a DateTimeField. And second argument is optional.
        If you don't provide the title, it will try to use the field verbose_name or the field name as the title.
    """

    class DateTimeRangeFilterWrapper(DateTimeRangeFilter):
        parameter_name = field_name

        def __init__(self, request, params, model, model_admin):
            field = None
            try:
                field = model._meta.get_field(field_name)
            except FieldDoesNotExist as e:
                raise FieldDoesNotExist(
                    f"datetime_range_filter: {model.__name__} model does not have field '{field_name}'"
                ) from e
            except Exception as e:
                raise RuntimeError(
                    f"datetime_range_filter: unexpected error: {e}"
                ) from e

            if not isinstance(field, models.DateTimeField):
                raise TypeError(
                    f"datetime_range_filter: field '{field_name}' is not a DateTimeField"
                )

            if title:
                self.title = title.title()
            else:
                verbose_name = getattr(field, "verbose_name", None)
                if verbose_name:
                    self.title = verbose_name.title()
                else:
                    self.title = field_name.replace("_", " ").title()

            super().__init__(request, params, model, model_admin)

    return DateTimeRangeFilterWrapper


class NumericRangeFilter(admin.SimpleListFilter):
    """
    A numeric range filter for numeric fields (int, float, decimal).
    """

    template = "admin/django_admin_range/numeric_range_filter.html"

    def __init__(self, request, params, model, model_admin):
        self.field_name = self.parameter_name
        self.lookup_kwarg_gte = f"{self.field_name}__gte"
        self.lookup_kwarg_lte = f"{self.field_name}__lte"

        self.num_gte = params.get(self.lookup_kwarg_gte, "")
        self.num_lte = params.get(self.lookup_kwarg_lte, "")

        def _first_nonempty(val):
            if isinstance(val, list):
                for v in val:
                    if v:
                        return v
                return ""
            return val or ""

        self.num_gte = _first_nonempty(self.num_gte)
        self.num_lte = _first_nonempty(self.num_lte)

        if isinstance(self.num_gte, str):
            self.num_gte = self.num_gte.strip()
        if isinstance(self.num_lte, str):
            self.num_lte = self.num_lte.strip()

        # Drop empty values to avoid duplicate blank params
        try:
            mutable = getattr(params, "_mutable", True)
            params._mutable = True
            if not self.num_gte and self.lookup_kwarg_gte in params:
                del params[self.lookup_kwarg_gte]
            if not self.num_lte and self.lookup_kwarg_lte in params:
                del params[self.lookup_kwarg_lte]
            params._mutable = mutable
        except Exception:
            if not self.num_gte:
                params.pop(self.lookup_kwarg_gte, None)
            if not self.num_lte:
                params.pop(self.lookup_kwarg_lte, None)

        # Parse once and reuse
        self.parsed_num_gte = self._parse_number(self.num_gte) if self.num_gte else None
        self.parsed_num_lte = self._parse_number(self.num_lte) if self.num_lte else None

        super().__init__(request, params, model, model_admin)

    def has_output(self):
        return True

    def lookups(self, request, model_admin):
        return ()

    def queryset(self, request, queryset):
        filters = {}
        if self.parsed_num_gte is not None:
            filters[f"{self.field_name}__gte"] = self.parsed_num_gte
        if self.parsed_num_lte is not None:
            filters[f"{self.field_name}__lte"] = self.parsed_num_lte
        return queryset.filter(**filters) if filters else queryset

    def _parse_number(self, value):
        """
        Parse input into Decimal for consistent comparison.
        """
        if value is None:
            return None
        if isinstance(value, list):
            value = value[0] if value else ""
        if value == "":
            return None
        try:
            return Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError):
            return None

    def choices(self, changelist):
        def _fmt(v):
            if v is None:
                return ""
            # Normalize trailing zeros for display
            return format(v.normalize(), "f") if isinstance(v, Decimal) else str(v)

        yield {
            "title": self.title,
            "field_name": self.field_name,
            "num_gte": self.num_gte,
            "num_lte": self.num_lte,
            "num_gte_display": _fmt(self.parsed_num_gte),
            "num_lte_display": _fmt(self.parsed_num_lte),
            "query_string": changelist.get_query_string(
                remove=[self.lookup_kwarg_gte, self.lookup_kwarg_lte]
            ),
        }

    def expected_parameters(self):
        return [self.lookup_kwarg_gte, self.lookup_kwarg_lte]


def numeric_range_filter(field_name: str, title: Union[str, None] = None):
    """
    Factory for NumericRangeFilter bound to a numeric field.
    Usage:
        list_filter = (
            numeric_range_filter('price', 'Price'),
        )
    Note:
        The field must be a numeric field (IntegerField, FloatField, DecimalField). And second argument is optional.
        If you don't provide the title, it will try to use the field verbose_name or the field name as the title.
    """

    class NumericRangeFilterWrapper(NumericRangeFilter):
        parameter_name = field_name

        def __init__(self, request, params, model, model_admin):
            field = None
            try:
                field = model._meta.get_field(field_name)
            except FieldDoesNotExist as e:
                raise FieldDoesNotExist(
                    f"numeric_range_filter: {model.__name__} model does not have field '{field_name}'"
                ) from e
            except Exception as e:
                raise RuntimeError(
                    f"numeric_range_filter: unexpected error: {e}"
                ) from e

            numeric_fields = (
                models.IntegerField,
                models.FloatField,
                models.DecimalField,
            )

            if not isinstance(field, numeric_fields):
                raise TypeError(
                    f"numeric_range_filter: field '{field_name}' is not a numeric field"
                )

            if title:
                self.title = title.title()
            else:
                verbose_name = getattr(field, "verbose_name", None)
                if verbose_name:
                    self.title = verbose_name.title()
                else:
                    self.title = field_name.replace("_", " ").title()

            super().__init__(request, params, model, model_admin)

    return NumericRangeFilterWrapper
