import os
import time

from foris.config import ConfigPageMixin, add_config_page
from foris.config_handlers import BaseConfigHandler
from foris.core import gettext_dummy as gettext, ugettext as _
from foris.plugins import ForisPlugin
from foris.ubus import call as ubus_call


class SamplePluginConfigHandler(BaseConfigHandler):
    pass


class SamplePluginPage(ConfigPageMixin, SamplePluginConfigHandler):
    menu_order = 70
    template = "ups_pfc8591/ups_pfc8591.tpl"
    userfriendly_title = gettext("I2C collect")

    def _prepare_render_args(self, args):
        args['PLUGIN_NAME'] = SamplePluginPlugin.PLUGIN_NAME
        args['PLUGIN_STYLES'] = SamplePluginPlugin.PLUGIN_STYLES
        args['PLUGIN_STATIC_SCRIPTS'] = SamplePluginPlugin.PLUGIN_STATIC_SCRIPTS
        args['PLUGIN_DYNAMIC_SCRIPTS'] = SamplePluginPlugin.PLUGIN_DYNAMIC_SCRIPTS
        args['data'] = {}
        for fld in ["voltage", "light", "temperature", "trimmer"]:
            args['data'][fld] = ubus_call("ups-pfc8591", "read_data", {"range": 172800, "field": fld})[0]['data']
            for _, dt in enumerate(args['data'][fld]):
                dt[0] = time.strftime('%H:%M:%S', time.gmtime(int(dt[0])))
                if fld == "voltage":
                    dt[1] = float(dt[1]) * 0.0593
                elif fld == "light":
                    dt[1] = float(255 - dt[1]) # TODO calibrate
                elif fld == "temperature":
                    dt[1] = float(255 - dt[1]) # TODO calibrate
                elif fld == "trimmer":
                    dt[1] = float(dt[1]) / 2.55

    def render(self, **kwargs):
        self._prepare_render_args(kwargs)
        return super(SamplePluginPage, self).render(**kwargs)


class SamplePluginPlugin(ForisPlugin):
    PLUGIN_NAME = "ups_pfc8591"
    DIRNAME = os.path.dirname(os.path.abspath(__file__))

    PLUGIN_STYLES = [
    ]
    PLUGIN_STATIC_SCRIPTS = [
        "js/Chart.bundle.min.js"
    ]
    PLUGIN_DYNAMIC_SCRIPTS = [
        "ups_pfc8591.js"
    ]

    def __init__(self, app):
        super(SamplePluginPlugin, self).__init__(app)
        add_config_page("ups_pfc8591", SamplePluginPage, top_level=True)
