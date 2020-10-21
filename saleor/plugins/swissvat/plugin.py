from ..base_plugin import BasePlugin

from prices import Money, MoneyRange, TaxedMoney, TaxedMoneyRange

from ...checkout import calculations
from ...core.taxes import TaxType
from ...graphql.core.utils.error_codes import PluginErrorCode
from ...product.models import Product, ProductType
from ..base_plugin import BasePlugin, ConfigurationTypeField
from . import (
    DEFAULT_TAX_RATE_NAME,
    TaxRateType,
    apply_tax_to_price,
    get_taxed_shipping_price,
    get_taxes_for_country,
)


class SwissVatPlugin(BasePlugin):

    PLUGIN_NAME = "SwissVat"
    PLUGIN_ID = "drinks4us.swissvat"
    DEFAULT_ACTIVE = True
    PLUGIN_DESCRIPTION = (
        "Set Swiss Vat"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.active = True

    def _skip_plugin(self, previous_value: Union[TaxedMoney, TaxedMoneyRange]) -> bool:
        if not self.active:
            return True

        # The previous plugin already calculated taxes so we can skip our logic
        if isinstance(previous_value, TaxedMoneyRange):
            start = previous_value.start
            stop = previous_value.stop

            return start.net != start.gross and stop.net != stop.gross

        if isinstance(previous_value, TaxedMoney):
            return previous_value.net != previous_value.gross
        return False

    def calculate_checkout_total(
        self,
        checkout: "Checkout",
        lines: List["CheckoutLine"],
        discounts: List["DiscountInfo"],
        previous_value: TaxedMoney,
    ) -> TaxedMoney:
        if self._skip_plugin(previous_value):
            return previous_value

        return (
            calculations.checkout_subtotal(
                checkout=checkout, lines=lines, discounts=discounts
            )
            + calculations.checkout_shipping_price(
                checkout=checkout, lines=lines, discounts=discounts
            )
            - checkout.discount
        )

    def _get_taxes_for_country(self, country: Country):
        """Try to fetch cached taxes on the plugin level.

        If the plugin doesn't have cached taxes for a given country it will fetch it
        from cache or db.
        """
        if not country:
            country = Country(settings.DEFAULT_COUNTRY)
        country_code = country.code
        if country_code in self._cached_taxes:
            return self._cached_taxes[country_code]
        taxes = get_taxes_for_country(country)
        self._cached_taxes[country_code] = taxes
        return taxes

    def calculate_checkout_shipping(
        self,
        checkout: "Checkout",
        lines: List["CheckoutLine"],
        discounts: List["DiscountInfo"],
        previous_value: TaxedMoney,
    ) -> TaxedMoney:
        """Calculate shipping gross for checkout."""
        if self._skip_plugin(previous_value):
            return previous_value

        address = checkout.shipping_address or checkout.billing_address
        taxes = None
        if address:
            taxes = self._get_taxes_for_country(address.country)
        if not checkout.shipping_method:
            return previous_value

        return get_taxed_shipping_price(checkout.shipping_method.price, taxes)

    def calculate_order_shipping(
        self, order: "Order", previous_value: TaxedMoney
    ) -> TaxedMoney:
        if self._skip_plugin(previous_value):
            return previous_value

        address = order.shipping_address or order.billing_address
        taxes = None
        if address:
            taxes = self._get_taxes_for_country(address.country)
        if not order.shipping_method:
            return previous_value
        return get_taxed_shipping_price(order.shipping_method.price, taxes)