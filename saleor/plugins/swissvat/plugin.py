from django.conf import settings

from ..base_plugin import BasePlugin

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
    