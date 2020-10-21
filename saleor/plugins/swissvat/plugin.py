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

    
