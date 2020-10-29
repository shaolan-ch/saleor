from django.conf import settings

from ..base_plugin import BasePlugin

from ...core.taxes import TaxType
from django_countries.fields import Country

class SwissVatPlugin(BasePlugin):

    PLUGIN_NAME = "SwissVat"
    PLUGIN_ID = "drinks4us.swissvat"
    PLUGIN_DESCRIPTION = (
        "Set Swiss Vat"
    )

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
    
    #
    # Helper methoden
    #
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
    
    #
    # Main methoden
    #
    def get_tax_rate_type_choices(
        self, previous_value: List["TaxType"]
    ) -> List["TaxType"]:
        if not self.active:
            return previous_value

        choices = [
            TaxType(code="standard", description="Normale Taxe")
        ]
        # sort choices alphabetically by translations
        return sorted(choices, key=lambda x: x.code)

    def get_tax_rate_percentage_value(
        self, obj: Union["Product", "ProductType"], country: Country, previous_value
    ) -> Decimal:
        """Return tax rate percentage value for given tax rate type in the country."""
        if not self.active:
            return previous_value

        return Decimal(7)

    