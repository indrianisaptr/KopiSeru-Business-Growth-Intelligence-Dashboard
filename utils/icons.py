"""
utils/icons.py
Inline Lucide SVG icons for KopiSeru Dashboard HTML components.
"""


def _svg(inner: str) -> str:
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" '
        'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round" '
        'style="vertical-align:middle;display:inline-block">'
        + inner + "</svg>"
    )


# KPI Metrics

SVG_REVENUE = _svg(
    '<line x1="12" x2="12" y1="2" y2="22"/>'
    '<path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>'
)

SVG_PROFIT = _svg(
    '<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/>'
    '<polyline points="16 7 22 7 22 13"/>'
)

SVG_MARGIN = _svg(
    '<line x1="18" x2="18" y1="20" y2="10"/>'
    '<line x1="12" x2="12" y1="20" y2="4"/>'
    '<line x1="6" x2="6" y1="20" y2="14"/>'
)

SVG_TRANSACTION = _svg(
    '<path d="M4 2v20l2-1 2 1 2-1 2 1 2-1 2 1 2-1 2 1V2l-2 1-2-1-2 1-2-1-2 1-2-1-2 1Z"/>'
    '<path d="M16 8H8"/><path d="M16 12H8"/><path d="M12 16H8"/>'
)

SVG_SATISFACTION = _svg(
    '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02'
    ' 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>'
)

SVG_BRANCH = _svg(
    '<path d="m2 7 4.41-4.41A2 2 0 0 1 7.83 2h8.34a2 2 0 0 1 1.42.59L22 7"/>'
    '<path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"/>'
    '<path d="M15 22v-4a2 2 0 0 0-2-2h-2a2 2 0 0 0-2 2v4"/>'
    '<path d="M2 7h20"/>'
)

SVG_CITY = _svg(
    '<line x1="3" x2="21" y1="22" y2="22"/>'
    '<rect width="9" height="11" x="2" y="11"/>'
    '<rect width="5" height="7" x="13" y="15"/>'
    '<path d="M18 22V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v1"/>'
    '<path d="M9 22v-4h6v4"/>'
    '<path d="M7 14h.01"/><path d="M7 18h.01"/>'
)

SVG_TICKET = _svg(
    '<path d="M2 9a3 3 0 0 1 0 6v2a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-2'
    'a3 3 0 0 1 0-6V7a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2Z"/>'
)

SVG_SMILE = _svg(
    '<circle cx="12" cy="12" r="10"/>'
    '<path d="M8 14s1.5 2 4 2 4-2 4-2"/>'
    '<line x1="9" x2="9.01" y1="9" y2="9"/>'
    '<line x1="15" x2="15.01" y1="9" y2="9"/>'
)

SVG_TARGET = _svg(
    '<circle cx="12" cy="12" r="10"/>'
    '<circle cx="12" cy="12" r="6"/>'
    '<circle cx="12" cy="12" r="2"/>'
)

SVG_THUMBUP = _svg(
    '<path d="M7 10v12"/>'
    '<path d="M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8A2 2 0 0 1 17.5 22H4'
    'a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h2.76a2 2 0 0 0 1.79-1.11L12 2h0'
    'a3.13 3.13 0 0 1 3 3.88Z"/>'
)

SVG_WARNING = _svg(
    '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16'
    'a2 2 0 0 0 1.73-3Z"/>'
    '<path d="M12 9v4"/><path d="M12 17h.01"/>'
)

SVG_CASH = _svg(
    '<rect width="20" height="12" x="2" y="6" rx="2"/>'
    '<circle cx="12" cy="12" r="2"/>'
    '<path d="M6 12h.01M18 12h.01"/>'
)

SVG_CART = _svg(
    '<circle cx="8" cy="21" r="1"/>'
    '<circle cx="19" cy="21" r="1"/>'
    '<path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78'
    'a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"/>'
)

# Sidebar / UI

SVG_BRAND = _svg(
    '<path d="M17 8h1a4 4 0 1 1 0 8h-1"/>'
    '<path d="M3 8h14v9a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4Z"/>'
    '<line x1="6" x2="6" y1="2" y2="4"/>'
    '<line x1="10" x2="10" y1="2" y2="4"/>'
    '<line x1="14" x2="14" y1="2" y2="4"/>'
)

SVG_FILTER = _svg(
    '<polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>'
)

SVG_CALENDAR = _svg(
    '<rect width="18" height="18" x="3" y="4" rx="2" ry="2"/>'
    '<line x1="16" x2="16" y1="2" y2="6"/>'
    '<line x1="8" x2="8" y1="2" y2="6"/>'
    '<line x1="3" x2="21" y1="10" y2="10"/>'
)

SVG_PIN = _svg(
    '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/>'
    '<circle cx="12" cy="10" r="3"/>'
)

SVG_INSIGHT = _svg(
    '<path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5'
    'A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5"/>'
    '<path d="M9 18h6"/><path d="M10 22h4"/>'
)

SVG_HIGH = _svg(
    '<circle cx="12" cy="12" r="10"/>'
    '<path d="m9 12 2 2 4-4"/>'
)

SVG_LOW = _svg(
    '<circle cx="12" cy="12" r="10"/>'
    '<path d="m15 9-6 6"/><path d="m9 9 6 6"/>'
)

SVG_SEARCH = _svg(
    '<circle cx="11" cy="11" r="8"/>'
    '<path d="m21 21-4.3-4.3"/>'
)


def svg(name: str) -> str:
    """Return SVG string by name (case-insensitive). Empty string if not found."""
    return globals().get(f"SVG_{name.upper()}", "")
