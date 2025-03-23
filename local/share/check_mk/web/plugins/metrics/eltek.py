#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

from cmk.gui.i18n import _

from cmk.gui.plugins.metrics import (
    check_metrics,
    metric_info,
    graph_info,
)

metric_info['system_status'] = {
	'title': _('System status'),
	'unit': '',
	'color': '31/b',
}

metric_info['system_voltage'] = {
	'title': _('Voltege Output'),
	'unit': 'v',
	'color': '51/a',
}

metric_info['system_current_load'] = {
	'title': _('System current load'),
	'unit': 'a',
	'color': '14/a',
}

metric_info['system_ac'] = {
	'title': _('System input AC'),
	'unit': 'v',
	'color': '24/a',
}

metric_info['batt_current'] = {
        'title': _('Battery current'),
        'unit': 'a',
        'color': '26/a',
}

metric_info['batt_temp'] = {
        'title': _('Battery temperature'),
        'unit': 'c',
        'color': '22/a',
}

metric_info['batt_soc'] = {
        'title': _('Battery SoC'),
        'unit': '%',
        'color': '16/a',
}

metric_info['batt_charge_mode'] = {
        'title': _('Charge mode: 1-float, 2-equal'),
        'unit': '',
        'color': '41/a',
}

metric_info['batt_current_alarm'] = {
        'title': _('Current of battery status: 1-normal, 2-too HIGH'),
        'unit': '%',
        'color': '47/a',
}

metric_info['batt_temp_alarm'] = {
        'title': _('Battery temperature status: 1-normal, 2-too HIGH'),
        'unit': '',
        'color': '15/a',
}


