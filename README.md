[![](https://img.shields.io/pypi/v/django-admin-range.svg?color=blue&logo=pypi&logoColor=white)](https://pypi.org/project/django-admin-range/)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/django-admin-range?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/django-admin-range)
[![](https://img.shields.io/github/stars/arifogluisa/django-admin-range?logo=github)](https://github.com/arifogluisa/django-admin-range/stargazers)
[![](https://img.shields.io/pypi/l/django-admin-range.svg?color=blue)](https://github.com/arifogluisa/django-admin-range/blob/master/LICENSE)
[![](https://img.shields.io/codacy/grade/75aace1dda574b58bd2a519d958fa24d?logo=codacy)](https://app.codacy.com/gh/arifogluisa/django-admin-range)

# django-admin-range

Reusable date, datetime, and numeric range filters for Django admin with modern UI design. Compatible with Django's default admin, Jazzmin, and Grappelli admin interfaces. Install the package and drop the filters straight into `list_filter` — the templates, CSS, and JS are bundled so you do not have to wire up static files manually.

_Inspired by [django-admin-rangefilter](https://github.com/silentsokolov/django-admin-rangefilter/)_

## Examples

### Default Django Admin

![Django Default Admin](https://raw.githubusercontent.com/arifogluisa/django-admin-range/refs/heads/master/docs/images/django-default.gif)

### Jazzmin Theme

![Jazzmin Theme](https://raw.githubusercontent.com/arifogluisa/django-admin-range/refs/heads/master/docs/images/jazzmin.gif)

### Grappelli Theme

![Grappelli Theme](https://raw.githubusercontent.com/arifogluisa/django-admin-range/refs/heads/master/docs/images/grapelli.gif)

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

## License
Released under [MIT License](LICENSE).

## Supporting

- ⭐ Star this project on [GitHub](https://github.com/arifogluisa/django-admin-range)
- ⚡ Follow me on [GitHub](https://github.com/arifogluisa)
