# Development Guide

## Plugin Structure
```python
eltek.py
├── SNMP Configuration
│   ├── OID Definitions
│   └── Detection Logic
├── Data Parsing
│   ├── Value Conversion
│   └── Error Handling
├── Check Functions
│   ├── System Status
│   └── Temperature
└── Metric Registration
    ├── Performance Metrics
    └── State Metrics
```

## Adding New OIDs
1. Extend OID dictionary:
```python
OIDs['7'] = {
    'id': 'battery_voltage',
    'oid': '10.7.3.0',
    'name': 'Battery Voltage',
    'do_metric': True,
    'divider': 100
}
```

2. Update parse function:
```python
def parse_eltek_flatpack2(string_table):
    # Add new value handling
    if oid_info['id'] == 'battery_voltage':
        value = validate_voltage(value)
```

3. Register new metric:
```python
yield Metric('battery_voltage', voltage_value)
```

## Creating New Checks
### 1. Service Discovery
```python
def discover_battery_health(section):
    if section.get('battery_voltage'):
        yield Service(item="Battery Health")
```

### 2. Check Logic
```python
def check_battery_health(item, params, section):
    voltage = section['battery_voltage']['value']
    if voltage < 48.0:
        yield Result(state=State.CRIT, summary=f"Low voltage: {voltage}V")
    yield Metric('voltage', voltage)
```

### 3. Registration
```python
register.check_plugin(
    name='eltek_battery_health',
    service_name="Battery %s",
    discovery_function=discover_battery_health,
    check_function=check_battery_health
)
```

## Metric Collection
```python
# Add to check function
yield Metric(
    name='battery_voltage',
    value=voltage_value,
    levels=(params.get('warn', 48.0), params.get('crit', 46.0)),
    boundaries=(40.0, 60.0)
)
```

## Error Handling
Common patterns:
```python
try:
    # SNMP operations
except SNMPError as e:
    logger.error("SNMP fetch failed: %s", e)
except ValueError as e:
    logger.warning("Invalid value conversion: %s", e)
```

## Debugging
```bash
# Check_MK diagnostic commands
cmk --debug check eltek_flatpack2
cmk -vv snmpwalk HOST .1.3.6.1.4.1.12148
```

## Contributing
1. Follow PEP8 guidelines
2. Validate with Check_MK's `pylint` rules
3. Test SNMP simulations:
```python
pytest -v tests/unit/test_eltek_snmp.py
```

## Troubleshooting Checklist
```mermaid
graph TD
    A[SNMP Timeout] --> B[Verify Community String]
    A --> C[Check Firewall Rules]
    D[Missing Metrics] --> E[Validate OID Mappings]
    D --> F[Check MIB Import]
    G[Incorrect Values] --> H[Verify Divider Logic]
    G --> I[Check SNMP Version]
