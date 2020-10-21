from django.conf import settings

from ..base_plugin import BasePlugin

class SwissVatPlugin(BasePlugin):

    PLUGIN_NAME = "SwissVat"
    PLUGIN_ID = "drinks4us.swissvat"
    PLUGIN_DESCRIPTION = (
        "Set Swiss Vat"
    )
    