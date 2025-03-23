# Eltek Flatpack2 Check_MK Monitoring Plugin

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

Official Check_MK plugin for monitoring Eltek Flatpack2 power systems via SNMP.

## Features

- 📊 System health monitoring (voltage, current, load)
- 🔥 Temperature monitoring (rectifier & battery)
- 🚨 Alarm status tracking with state mapping
- 📈 Performance metrics for Grafana/Prometheus
- ⚙️ Preconfigured thresholds with customization

## Requirements

- Check_MK ≥ 2.2
- SNMP v2c access to Eltek devices
- MIB files:
  - ELTEK-COMMON-MIB
  - SP2-MIB.txt

## Installation

```bash
# Clone repository
git clone https://github.com/Check_MK-Eltek.git

# Copy plugin files
cp -r Check_MK-Eltek/local /omd/sites/[SITE_NAME]/local/

# Copy MIB files to Check_MK's MIB directory
cp Check_MK-Eltek/MIB/* /omd/sites/[SITE_NAME]/share/check_mk/mibs/
```

Restart Check_MK services after installation:
```bash
omd restart [SITE_NAME]
```

## Configuration

### 1. SNMP Community
Configure in Check_MK host settings:
```yaml
snmp_communities:
  - community: "public"
    version: "2"
```

### 2. Temperature Thresholds
Create rule in `etc/check_mk/conf.d/temperature.mk`:
```python
checkgroup_parameters.setdefault("temperature", [])

checkgroup_parameters["temperature"] = [
    {
        "levels": (40.0, 50.0),  # (warning, critical)
    },
] + checkgroup_parameters["temperature"]
```

## Documentation

- [Technical Architecture](docs/architecture.md)
- [Development Guide](docs/development.md)
- [Troubleshooting](docs/troubleshooting.md)

## License

This project is licensed under the GNU General Public License v3.0 - see [LICENSE](LICENSE) file for details.
