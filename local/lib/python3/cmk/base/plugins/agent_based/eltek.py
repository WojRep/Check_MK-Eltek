#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
from .agent_based_api.v1 import *
import sys
import traceback

NAME = "eltek_flatpack2"
SNMP_BASE = ".1.3.6.1.4.1.12148.10"

# Poprawiona konfiguracja wykrywania - szukamy konkretnej wartości "Eltek"
SNMP_DETECT = any_of(
    exists('.1.3.6.1.4.1.12148.10.2.6.0')
)

# Definicje OIDs
OIDs = {
    '0': {'id': 'model_name', 'oid': '2.6.0', 'name': "Model", 'do_metric': False},
    '1': {'id': 'firmware_version', 'oid': '2.7.0', 'name': 'Firmware', 'do_metric': False},
    '2': {'id': 'site_name', 'oid': '2.5.0', 'name': 'Site name', 'do_metric': False},
    '3': {'id': 'system_status', 'oid': '2.1.0', 'name': 'System status', 'do_metric': True, 'divider': 1},
    '4': {'id': 'system_voltage', 'oid': '10.5.5.0', 'name': 'Voltage', 'do_metric': True, 'divider': 100},
    '5': {'id': 'system_current_load', 'oid': '9.2.5.0', 'name': 'Current load', 'do_metric': True, 'divider': 10},
    '6': {'id': 'system_ac', 'oid': '3.4.1.6.1', 'name': 'AC voltage', 'do_metric': True, 'divider': 1},
}

# Statusy systemu
SYSTEM_STATUS_NAME = {
    "1": "normal",
    "2": "minor alarm",
    "3": "major alarm",
}

def parse_eltek_flatpack2(string_table):
    try:
        if not string_table or not string_table[0]:
            return {}

        parameters = string_table[0]
        param_list = {}

        for n in range(min(len(parameters), len(OIDs))):
            try:
                oid_info = OIDs.get(str(n), {})
                value = parameters[n]
                divider = oid_info.get('divider', 1)

                # Konwersja wartości
                if value.isdigit() and divider == 1:
                    value = int(value)
                elif value.isdigit():
                    value = float(int(value) / divider)
                else:
                    # Pozostaw jako string
                    value = str(value)
                    if value == '':
                        value = "N/A"

                param_list[oid_info['id']] = {
                    'value': value,
                    'name': oid_info['name'],
                    'do_metric': oid_info.get('do_metric', False),
                }
            except Exception as e:
                # Ignoruj problematyczne OIDy
                continue

        return param_list
    except Exception:
        # W przypadku błędu zwracamy pustą mapę
        return {}

def discover_eltek_flatpack2(section):
    if section:
        yield Service(item="Info")
        yield Service(item="Status")

def check_eltek_flatpack2(item, params, section):  # Dodano parametr 'params', nawet jeśli nie jest używany
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data")
        return

    try:
        if item == "Info":
            model_name = section.get('model_name', {}).get('value', 'Unknown')
            firmware_version = section.get('firmware_version', {}).get('value', 'Unknown')
            site_name = section.get('site_name', {}).get('value', 'Unknown')

            yield Result(state=State.OK, summary=f"Model: {model_name}, Firmware: {firmware_version}, Site name: {site_name}")

        elif item == "Status":
            system_status = section.get('system_status', {}).get('value', 0)
            system_voltage = section.get('system_voltage', {}).get('value', 0.0)
            system_current_load = section.get('system_current_load', {}).get('value', 0.0)
            system_ac = section.get('system_ac', {}).get('value', 0.0)

            # Formatowanie wartości
            try:
                system_voltage = float("{:.1f}".format(float(system_voltage)))
                system_current_load = float("{:.2f}".format(float(system_current_load)))
                system_ac = float("{:.2f}".format(float(system_ac)))
            except (ValueError, TypeError):
                pass

            # Podsumowanie
            summary = f"Status: {SYSTEM_STATUS_NAME.get(str(system_status), 'Unknown')}, "
            summary += f"AC: {system_ac}V, Voltage: {system_voltage}V, Current load: {system_current_load}A"

            # Stan
            if system_status == 1:
                state = State.OK
            elif system_status == 2:
                state = State.WARN
            elif system_status == 3:
                state = State.CRIT
            else:
                state = State.UNKNOWN

            yield Result(state=state, summary=summary)

            # Metryki
            yield Metric('system_status', float(system_status))
            yield Metric('system_voltage', system_voltage)
            yield Metric('system_current_load', system_current_load)
            yield Metric('system_ac', system_ac)
    except Exception as e:
        yield Result(state=State.UNKNOWN, summary=f"Check error: {e}")

# Rejestracja sekcji SNMP
register.snmp_section(
    name=NAME,
    fetch=SNMPTree(
        base=SNMP_BASE,
        oids=[oid['oid'] for _, oid in OIDs.items()],
    ),
    detect=SNMP_DETECT,
    parse_function=parse_eltek_flatpack2
)

# Rejestracja pluginu z parametrem check_default_parameters
register.check_plugin(
    name=NAME,
    service_name="Eltek %s",
    discovery_function=discover_eltek_flatpack2,
    check_function=check_eltek_flatpack2,
    check_default_parameters={},  # Dodane puste parametry domyślne
    sections=[NAME],
    check_ruleset_name=NAME
)


#####################################################
#####################################################
##                                                 ##
##               Eltek  Temperature                ##
##                                                 ##
#####################################################
#####################################################

# Definicje OIDs dla temperatur
TEMP_OIDs = {
    '0': {'id': 'rectifier_temp', 'oid': '5.18.5.0', 'name': "Rectifier Temperature", 'do_metric': True, 'divider': 1},
    '1': {'id': 'rectifier_temp_status', 'oid': '5.18.1.0', 'name': "Rectifier Temperature Status", 'do_metric': True, 'divider': 1},
    '2': {'id': 'battery_temp', 'oid': '10.7.5.0', 'name': "Battery Temperature", 'do_metric': True, 'divider': 1},
    '3': {'id': 'battery_temp_status', 'oid': '10.7.1.0', 'name': "Battery Temperature Status", 'do_metric': True, 'divider': 1},
}

# Statusy alarmu
# Statusy alarmu
ALARM_STATUS = {
    "0": "Error",  # error
    "1": "Normal state",  # normal
    "2": "Minor alarm",  # minorAlarm
    "3": "Major alarm",  # majorAlarm
    "4": "Disabled",  # disabled
    "5": "Disconnected",  # disconnected
    "6": "Not present",  # notPresent
    "7": "Minor and major alarm",  # minorAndMajor
    "8": "Critically low value alarm",  # majorLow
    "9": "Warning low value alarm",  # minorLow
    "10": "Critically high value alarm",  # majorHigh
    "11": "Warning high value alarm",  # minorHigh
    "12": "Event",  # event
    "13": "Value in volts",  # valueVolt
    "14": "Value in amps",  # valueAmp
    "15": "Temperature value",  # valueTemp
    "16": "Unit value",  # valueUnit
    "17": "Percentage value",  # valuePerCent
    "18": "Critical state",  # critical
    "19": "Warning"  # warning
}


def parse_eltek_flatpack2_temp(string_table):
    try:
        if not string_table or not string_table[0]:
            return {}

        parameters = string_table[0]
        param_list = {}

        for n in range(min(len(parameters), len(TEMP_OIDs))):
            try:
                oid_info = TEMP_OIDs.get(str(n), {})
                value = parameters[n]
                divider = oid_info.get('divider', 1)

                # Konwersja wartości
                if value.isdigit() and divider == 1:
                    value = int(value)
                elif value.isdigit():
                    value = float(int(value) / divider)
                else:
                    # Pozostaw jako string
                    value = str(value)
                    if value == '':
                        value = "N/A"

                param_list[oid_info['id']] = {
                    'value': value,
                    'name': oid_info['name'],
                    'do_metric': oid_info.get('do_metric', False),
                }
            except Exception as e:
                # Ignoruj problematyczne OIDy
                continue

        return param_list
    except Exception:
        # W przypadku błędu zwracamy pustą mapę
        return {}

def discover_eltek_flatpack2_temp(section):
    if not section:
        return

    try:
        # Sprawdzamy dostępność temperatur prostownika i baterii
        rectifier_temp = section.get('rectifier_temp', {}).get('value', None)
        battery_temp = section.get('battery_temp', {}).get('value', None)

        # Jeśli dostępna temperatura prostownika
        if rectifier_temp and rectifier_temp != "N/A":
            yield Service(item="Rectifier Temp")

        # Jeśli dostępna temperatura baterii
        if battery_temp and battery_temp != "N/A":
            yield Service(item="Battery Temp")
    except Exception:
        return

def check_eltek_flatpack2_temp(item, params, section):
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data")
        return

    try:
        if item == "Rectifier Temp":  # Zmienione z "Prostownik Temp"
            temp_value = section.get('rectifier_temp', {}).get('value', None)
            status_value = section.get('rectifier_temp_status', {}).get('value', None)
            source_type = "Rectifier"  # Zmienione z "Prostownik"

            # Progi temperatur dla prostownika
            warn_temp = params.get("levels", (40.0, 50.0))[0]
            crit_temp = params.get("levels", (40.0, 50.0))[1]

        elif item == "Battery Temp":
            temp_value = section.get('battery_temp', {}).get('value', None)
            status_value = section.get('battery_temp_status', {}).get('value', None)
            source_type = "Battery"

            # Progi temperatur dla baterii
            warn_temp = params.get("levels", (30.0, 40.0))[0]
            crit_temp = params.get("levels", (30.0, 40.0))[1]
        else:
            yield Result(state=State.UNKNOWN, summary=f"Unknown source type in {item}")
            return

        state = State.OK
        summary_parts = []

        # Obsługa wartości temperatury
        if temp_value is not None:
            try:
                temp_value = float(temp_value)
                summary_parts.append(f"Temperature: {temp_value:.1f}°C")

                # Sprawdzenie progów temperatur
                if temp_value > crit_temp:
                    state = State.CRIT
                elif temp_value > warn_temp:
                    state = State.WARN
            except (ValueError, TypeError):
                summary_parts.append(f"Temperature: {temp_value}")

        # Obsługa statusu
        if status_value is not None:
            try:
                status_numeric = int(status_value)
                status_text = ALARM_STATUS.get(str(status_numeric), f"Unknown Status ({status_numeric})")
                summary_parts.append(f"Status: {status_text}")

                # Mapowanie statusów na stany monitorowania
                if status_numeric in [0, 3, 7, 8, 10, 18]:  # Stany krytyczne
                    if state != State.CRIT:  # Nie nadpisujemy już wykrytego stanu krytycznego
                        state = State.CRIT
                elif status_numeric in [2, 9, 11, 19] and state != State.CRIT:  # Stany ostrzegawcze
                    state = State.WARN
                elif status_numeric in [4, 5, 6] and state == State.OK:
                    state = State.UNKNOWN
            except (ValueError, TypeError):
                summary_parts.append(f"Status: {status_value}")

        summary = f"{source_type}: " + ", ".join(summary_parts)

        if not summary_parts:
            yield Result(state=State.UNKNOWN, summary=f"No data for {source_type}")  # Zmienione z "Brak danych dla"
        else:
            yield Result(state=state, summary=summary)

            # Metryki
            if temp_value is not None and isinstance(temp_value, (int, float)):
                yield Metric("temperature", temp_value, levels=(warn_temp, crit_temp))
            if status_value is not None and isinstance(status_value, (int, float)):
                yield Metric("status", float(status_value))
    except Exception as e:
        yield Result(state=State.UNKNOWN, summary=f"Check error: {e}")

# Rejestracja sekcji SNMP dla temperatur
register.snmp_section(
    name=NAME + "_temp",
    fetch=SNMPTree(
        base=SNMP_BASE,
        oids=[oid['oid'] for _, oid in TEMP_OIDs.items()],
    ),
    detect=SNMP_DETECT,
    parse_function=parse_eltek_flatpack2_temp
)

# Rejestracja pluginu temperatur z poprawnym ruleset name
register.check_plugin(
    name=NAME + "_temp",
    service_name="Eltek %s",
    discovery_function=discover_eltek_flatpack2_temp,
    check_function=check_eltek_flatpack2_temp,
    check_default_parameters={
        "levels": (40.0, 50.0),  # Domyślne progi dla temperatury
    },
    check_ruleset_name='temperature',
    sections=[NAME + "_temp"]
)