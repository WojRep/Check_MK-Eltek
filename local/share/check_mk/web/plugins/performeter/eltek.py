#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

from cmk.gui.plugins.views.perfometers.utils import (
    perfometer_linear,
)

def perfometer_eltek(row, check_command, perf_data):

    PERF = {
        'system_current_load': {'type': 'linear', 'max': 15, 'color': 'red'},
    }

    for perf in perf_data:
        perf = list(perf)
        if PERF.get(perf[0]):
            name, value, xxx, warm, crit, _min, _max = perf
            perf_def = PERF[name]
            if perf_def['type'] == 'linear':
                perc_value = float(value * 100 / perf_def['max'])
                return u"%s" % str(value), perfometer_linear(perc_value, perf_def['color'])

perfometers['check_mk-eltek'] = perfometer_eltek

