from django import template

register = template.Library()

MAPA_KOLOROW = {
    "czarny": "#212529",
    "szary": "#adb5bd",
    "biały": "#ffffff",
    "czerwony": "#dc3545",
    "pomarańczowy": "#fd7e14",
    "żółty": "#ffc107",
    "zielony": "#28a745",
    "niebieski": "#0d6efd",
    "fioletowy": "#6f42c1",
    "brązowy": "#7b4b2a",
    "różowy": "#f06595",
}


@register.filter
def kolor_hex(nazwa):
    return MAPA_KOLOROW.get(nazwa, "#cccccc")