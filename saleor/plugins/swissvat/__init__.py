
DEFAULT_TAX_RATE_NAME = "standard"

def get_taxes_for_country(country):
    taxes = {
        DEFAULT_TAX_RATE_NAME: {
            "value": 7,
            "tax": None,
        }
    }
    
    return taxes

def get_taxed_shipping_price(shipping_price, taxes):
    """Calculate shipping price based on settings and taxes."""
    if not charge_taxes_on_shipping():
        taxes = None
    return apply_tax_to_price(taxes, DEFAULT_TAX_RATE_NAME, shipping_price)