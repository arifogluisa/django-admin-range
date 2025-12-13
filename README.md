[![Published on Django Packages](https://img.shields.io/badge/Published%20on-Django%20Packages-0c3c26)](https://djangopackages.org/packages/p/django-admin-range/)

# django-admin-range

Reuseable date, datetime, and numeric range filters for Django admin. Install the package and drop the filters straight into `list_filter` — the templates, CSS, and JS are bundled so you do not have to wire up static files manually.


## Installation

```bash
# with uv
uv add django-admin-range

# or pip
pip install django-admin-range
```

Add the app to `INSTALLED_APPS` so Django can discover the bundled templates and static assets:

```python
INSTALLED_APPS = [
    # ...
    "django_admin_range",
]
```

## Usage

```python
from django.contrib import admin
from django_admin_range.filters import date_range_filter, datetime_range_filter, numeric_range_filter


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_filter = [
        date_range_filter("created_at", "Created"),
        datetime_range_filter("paid_at", "Paid at"),
        numeric_range_filter("total", "Total amount"),
    ]
```

That is it. The admin changelist will render the range controls and load the package's CSS/JS automatically.

