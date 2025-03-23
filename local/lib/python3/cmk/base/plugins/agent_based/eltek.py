#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
from .agent_based_api.v1 import *
import sys
import traceback

NAME = "eltek"
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

def parse_eltek(string_table):
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

def discover_eltek(section):
    if section:
        yield Service(item="Eltek Info")
        yield Service(item="Eltek Status")

def check_eltek(item, section):
    # Usunięto parametr 'params' z funkcji
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data")
        return

    try:
        if item == "Eltek Info":
            model_name = section.get('model_name', {}).get('value', 'Unknown')
            firmware_version = section.get('firmware_version', {}).get('value', 'Unknown')
            site_name = section.get('site_name', {}).get('value', 'Unknown')

            yield Result(state=State.OK, summary=f"Model: {model_name}, Firmware: {firmware_version}, Site name: {site_name}")

        elif item == "Eltek Status":
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
    parse_function=parse_eltek,
)

# Rejestracja pluginu bez parametru check_default_parameters
register.check_plugin(
    name=NAME,
    service_name="%s",
    discovery_function=discover_eltek,
    check_function=check_eltek,
    sections=[NAME],
)


#####################################################
#####################################################
##                                                 ##
##               Eltek  Temperature                ##
##                                                 ##
#####################################################
#####################################################


ALARM = {
    '0': 'Błąd',  # error
    '1': 'Stan normalny',  # normal
    '2': 'Alarm niskiego poziomu',  # minorAlarm
    '3': 'Alarm wysokiego poziomu',  # majorAlarm
    '4': 'Wyłączony',  # disabled
    '5': 'Odłączony',  # disconnected
    '6': 'Nieobecny',  # notPresent
    '7': 'Alarm niskiego i wysokiego poziomu',  # minorAndMajor
    '8': 'Alarm krytycznie niskiej wartości',  # majorLow
    '9': 'Alarm ostrzegawczo niskiej wartości',  # minorLow
    '10': 'Alarm krytycznie wysokiej wartości',  # majorHigh
    '11': 'Alarm ostrzegawczo wysokiej wartości',  # minorHigh
    '12': 'Zdarzenie',  # event
    '13': 'Wartość w woltach',  # valueVolt
    '14': 'Wartość w amperach',  # valueAmp
    '15': 'Wartość temperatury',  # valueTemp
    '16': 'Wartość jednostkowa',  # valueUnit
    '17': 'Wartość procentowa',  # valuePerCent
    '18': 'Stan krytyczny',  # critical
    '19': 'Ostrzeżenie'  # warning
}

# Typ źródła pomiaru
SOURCE_TYPE = {
    'rectifier': 'Prostownik',
    'battery': 'Bateria'
}

def discover_eltek_temp(section):
    # Lepsze sprawdzanie pustych sekcji
    if not section or not section[0]:
        return

    try:
        # Sprawdź dostępne źródła temperatur
        rectifier_temp = section[0][0] if len(section[0]) > 0 else ""
        battery_temp = section[0][2] if len(section[0]) > 2 else ""

        # Jeśli dostępna temperatura prostownika
        if rectifier_temp and rectifier_temp != "":
            yield Service(item=f"{SOURCE_TYPE['rectifier']} Temp")

        # Jeśli dostępna temperatura baterii
        if battery_temp and battery_temp != "":
            yield Service(item=f"{SOURCE_TYPE['battery']} Temp")
    except Exception:
        # W przypadku wyjątku nie wykrywamy nic
        return


def check_eltek_temp(item, params, section):
    # Poprawiona obsługa pustych danych
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data")
        return

    if not section[0]:
        yield Result(state=State.UNKNOWN, summary="No correct data")
        return

    try:
        # Identyfikacja typu źródła na podstawie item
        source_type = None
        if SOURCE_TYPE['rectifier'] in item and len(section[0]) > 1:
            source_type = 'rectifier'
            temp_value = section[0][0]
            status_value = section[0][1]
        elif SOURCE_TYPE['battery'] in item and len(section[0]) > 3:
            source_type = 'battery'
            temp_value = section[0][2]
            status_value = section[0][3]
        else:
            yield Result(state=State.UNKNOWN, summary=f"Unknown source type in {item}")
            return

        # Konwersja temperatury na wartość liczbową
        try:
            temp_numeric = float(temp_value) / 1  # Zakładamy, że wartość jest w jednostkach 1°C
        except (ValueError, TypeError):
            temp_numeric = None

        # Konwersja statusu na wartość liczbową
        try:
            status_numeric = int(status_value)
        except (ValueError, TypeError):
            status_numeric = None

        state = State.OK
        summary_parts = []

        # Obsługa wartości temperatury
        if temp_numeric is not None:
            summary_parts.append(f"Temperatura: {temp_numeric:.1f}°C")

            # Progi alarmowe (można dostosować)
            if source_type == 'rectifier':
                if temp_numeric > 50.0:
                    state = State.CRIT
                elif temp_numeric > 40.0 and state != State.CRIT:
                    state = State.WARN
            elif source_type == 'battery':
                if temp_numeric > 40.0:
                    state = State.CRIT
                elif temp_numeric > 30.0 and state != State.CRIT:
                    state = State.WARN

        # Obsługa statusu
        if status_numeric is not None:
            status_text = ALARM.get(str(status_numeric), f"Status nieznany ({status_numeric})")
            summary_parts.append(f"Status: {status_text}")

            # Mapowanie statusów na stany monitorowania
            if status_numeric in [0, 3, 7, 8, 10, 18]:  # Stany krytyczne
                state = State.CRIT
            elif status_numeric in [2, 9, 11, 19] and state != State.CRIT:  # Stany ostrzegawcze
                state = State.WARN
            elif status_numeric in [4, 5, 6] and state not in [State.CRIT, State.WARN]:  # Brak danych
                state = State.UNKNOWN

        # Metryki dla wykresów
        metrics = []
        if temp_numeric is not None:
            metrics.append(Metric("temperature", temp_numeric))
        if status_numeric is not None:
            metrics.append(Metric("status", status_numeric))

        summary = f"{SOURCE_TYPE.get(source_type, 'Nieznany')}: " + ", ".join(summary_parts)

        if not summary_parts:
            yield Result(state=State.UNKNOWN, summary=f"Brak danych dla {SOURCE_TYPE.get(source_type, 'źródła')}")
        else:
            # Poprawione wyrażenie - nie rozpakowujemy pustej listy
            yield Result(state=state, summary=summary)
            # Dodajemy metryki osobno
            for metric in metrics:
                yield metric
    except Exception as e:
        yield Result(state=State.UNKNOWN, summary=f"Check error: {str(e)}")


register.snmp_section(
    name=NAME + "_temp",
    fetch = SNMPTree(
        base = SNMP_BASE,
        oids = [
            "5.18.5.0", # Restifier Temperatura
            "5.18.1.0", # Rectifier Temperature Status:
            "10.7.5.0", # Battery Temperatura
            "10.7.1.0"  # Battery Temperature Status:
        ],
    ),
    detect = SNMP_DETECT,
)

register.check_plugin(
    name = NAME + "_temp",
    sections=[NAME+"_temp"],
    service_name = "%s",
    discovery_function = discover_eltek_temp,
    check_default_parameters={},
    check_ruleset_name='temperature',  # Poprawiona nazwa ruleset - teraz używamy standardowej nazwy
    check_function = check_eltek_temp,
)
