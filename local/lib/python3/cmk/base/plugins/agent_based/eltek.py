#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
from .agent_based_api.v1 import *

from .agent_based_api.v1.type_defs import *

from .utils import (
    temperature,
)

from typing import Dict, List

from cmk.utils import debug
from pprint import pprint

#####################################################
#####################################################
##                                                 ##
##               Eltek  Status                     ##
##                                                 ##
#####################################################
#####################################################

UNIT = {
    "c": u"°C",
    "f": u"°F",
    "k": u"K",
    'v': u"V",
    'a': u"A",
    'w': u"W",
    'wh': u"Wh",
    'hz': u"Hz",
    'pa': u"Pa",
    '%': u"%",
    'ug/m3': u"µg/㎥",
}

def _render_template(value: float):
    template = "%%%s" % ("d" if isinstance(value, int) else ".1f")
    return template % value


def _render_func(value: float, unit: str) -> str:
    return _render_template(value) + UNIT.get(unit) if UNIT.get(unit) else ''



SYSTEM_STATUS_NAME = {
	"1": "normal",
	"2": "minnor alarm",
        "3": "major alarm",
}

alarm_name = {
	"0": "normal",
	"1": "Alarm",
}

NAME="eltek"
SNMP_BASE = ".1.3.6.1.4.1.12148.10"
SNMP_DETECT = startswith('.1.3.6.1.4.1.112148.10.2.6.0', 'Eltek')

OIDs = {
'0': {'id': 'model_name', 'oid': '2.6.0', 'name': "Model", 'do_metric': False, 'unit': None, },
'1': {'id': 'firmware_version', 'oid': '2.7.0', 'name': 'Firmware', 'do_metric': False, 'unit': None, },
'2': {'id': 'site_name', 'oid': '2.5.0', 'name': 'Site name', 'do_metric':False, 'unit': None, },
'3': {'id': 'system_status', 'oid': '2.1.0', 'name': 'System status', 'do_metric': True, 'unit':'', 'divider': 1,  },
'4': {'id': 'system_voltage', 'oid': '10.5.5.0', 'name': 'Voltage', 'do_metric': True, 'unit': 'v', 'divider': 100, },
'5': {'id': 'system_current_load', 'oid': '9.2.5.0', 'name': 'Current load', 'do_metric': True, 'unit': 'a', 'divider': 10, },
'6': {'id': 'system_ac', 'oid': '3.4.1.6.1', 'name': 'AC voltage', 'do_metric': True, 'unit': 'v',  'divider': 1,  },
}


def _isFloat(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def _isInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def parse_eltek(string_table):
    param_list = {}
    parameters = string_table[0]
    for n in range(len(parameters)):
        name = OIDs[str(n)].get('name')
        do_metric = OIDs[str(n)].get('do_metric') if OIDs[str(n)].get('do_metric') else ''
        divider =  OIDs[str(n)].get('divider') if OIDs[str(n)].get('divider') else 1

        if _isInt(parameters[n]) and divider == 1:
            value = int(parameters[n])

        elif _isFloat(parameters[n]):
            value = float(int(parameters[n]) / divider)

        else:
            value = str(parameters[n])
            if (value is None) or (value == ''):
                value = chr(216)

        param_list.update(
		{str(OIDs[str(n)]['id']): {
		    'value': value,
		    'name': name,
		    'do_metric': do_metric,
		}})
    return param_list


def discover_eltek(section):
#    if len(section) == 0:
#        return
    yield Service(item="Eltek Info")
    yield Service(item="Eltek Status")


def check_eltek(item, params, section):
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data")
        return
    if item == "Eltek Info":
        model_name = section['model_name']['value']
        firmware_version = section['firmware_version']['value']
        site_name = section['site_name']['value']
        yield Result(state=State.OK, summary=f"Model: {model_name}, Firmware: {firmware_version}, Site name: {site_name}")

    if item == "Eltek Status":
        system_status = section['system_status']['value']
        system_voltage = section['system_voltage']['value']
        system_current_load = section['system_current_load']['value']
        system_ac = section['system_ac']['value']
        system_voltage = float("{:.1f}".format(system_voltage))
        system_current_load = float("{:.2f}".format(system_current_load))
        system_ac = float("{:.2f}".format(system_ac))
        summary = f"Status: {SYSTEM_STATUS_NAME.get(str(system_status))}, AC: {system_ac}"
        summary = summary + f"V, Voltage: {system_voltage}V, Current load: {system_current_load}A."
        if system_status == 1:
            state=State.OK
        elif system_status == 2:
            state=State.WARRNING
        elif system_status == 3:
            state=State.CRIT
        else:
            state=State.UNKNOWN
        yield Result(state=state, summary=summary)
        yield Metric('system_status', system_status)
        yield Metric('system_voltage', system_voltage)
        yield Metric('system_current_load', system_current_load)
        yield Metric('system_ac', system_ac)
        return
    yield Result(state=State.UNKNOWN, summary="No item or data")
    return


register.snmp_section(
    name=NAME,
    fetch = SNMPTree(
        base = SNMP_BASE,
        oids = [ oid['oid'] for _, oid in OIDs.items()],
    ),
    detect = SNMP_DETECT,
    parse_function = parse_eltek,
)


register.check_plugin(
    name = NAME,
    sections=[NAME],
    service_name = "%s",
    discovery_function = discover_eltek,
    check_default_parameters={},
    check_ruleset_name=NAME,
    check_function = check_eltek,
)
