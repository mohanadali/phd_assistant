# 🇮🇶 Iraq ATFM System - Air Traffic Flow Management for Iraqi Overflights

A real-time Air Traffic Flow Management (ATFM) system specifically designed for monitoring and managing overflights through Iraqi airspace. This system provides comprehensive traffic monitoring, capacity management, and flow control capabilities for Iraqi airspace operations.

## 🌟 Features

### Real-time Traffic Monitoring
- **Live aircraft tracking** using OpenSky Network API data
- **Interactive map** centered on Iraqi airspace with real-time aircraft positions
- **Aircraft classification** (Overflights, Domestic, Arrivals/Departures, Ground traffic)
- **Flight type filtering** with visual indicators

### Iraqi Airspace Management
- **Major Iraqi airports** monitoring (Baghdad, Basra, Erbil, Sulaymaniyah, Najaf, Mosul, Kirkuk)
- **Airspace sector monitoring** (Baghdad Control Center and subsectors)
- **Capacity utilization** tracking with alert levels
- **Overflight route management** (L866, M644, UL866, UM688)

### Flow Analysis & Predictions
- **Overflight flow analysis** by direction and altitude
- **Country-based traffic analysis** showing origin countries
- **Sector utilization monitoring** with capacity warnings
- **Route management recommendations**

### Decision Support Tools
- **Real-time alerts** for sector congestion
- **Flow control recommendations** based on current traffic
- **Capacity management** with visual indicators
- **Coordination tools** for Baghdad Control Center

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Internet connection for real-time data

### Installation
1. Clone or download the project
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the System
```bash
streamlit run app.py
```

The system will be available at `http://localhost:8501`

## 🗺️ System Overview

### Iraqi Airspace Coverage
- **Coordinates**: 29.0°N to 37.5°N, 38.5°E to 49.0°E
- **Major Cities**: Baghdad, Basra, Erbil, Sulaymaniyah
- **International Overflights**: Europe-Asia corridor traffic

### Monitored Airports
| ICAO | Airport Name | Capacity | Type |
|------|-------------|----------|------|
| ORBI | Baghdad International | 45 | Major |
| ORMM | Basra International | 25 | International |
| ORER | Erbil International | 30 | International |
| ORSU | Sulaymaniyah International | 20 | Regional |
| ORNI | Najaf International | 15 | Regional |
| ORMF | Mosul Airport | 15 | Domestic |
| ORKK | Kirkuk Airport | 12 | Domestic |

### Airspace Sectors
- **Baghdad Control Center (ORBB_CTR)**: Central Iraq operations
- **Baghdad North Sector (ORBB_N)**: Northern Iraq coverage
- **Baghdad South Sector (ORBB_S)**: Southern Iraq operations
- **Baghdad East Sector (ORBB_E)**: Eastern border management

## 📊 Dashboard Components

### 1. Real-time Metrics
- Total aircraft in Iraqi airspace
- Number of overflights
- Domestic traffic count
- High alert sectors
- Overflight percentage

### 2. Interactive Map
- Aircraft positions with flight type color coding
- Iraqi airports with status indicators
- Airspace sector boundaries
- Traffic density visualization

### 3. Analysis Tabs
- **Sector Utilization**: Capacity monitoring and alerts
- **Overflight Flow**: Direction and altitude analysis
- **Country Analysis**: Traffic by origin country
- **Route Management**: Major overflight routes status

### 4. Flow Control Interface
- Current operational measures
- Available control tools
- Coordination buttons for Baghdad Control

## 🎨 Visual Interface

### Color Coding
- **Red aircraft**: Overflights (high altitude, transit)
- **Blue aircraft**: Arrivals/Departures (near airports)
- **Green aircraft**: Domestic flights
- **Orange aircraft**: Transit traffic
- **Gray aircraft**: Ground operations

### Alert Levels
- 🟢 **LOW**: <70% capacity utilization
- 🟡 **MEDIUM**: 70-85% capacity utilization
- 🔴 **HIGH**: >85% capacity utilization (requires intervention)

## 🔧 Configuration

### Refresh Settings
- **Manual refresh**: Click "Refresh Data" button
- **Auto-refresh**: Enable 60-second automatic updates
- **Display filters**: Show overflights only, sector information

### Data Sources
- **OpenSky Network API**: Real-time ADS-B aircraft data
- **Coverage**: Global aircraft with ADS-B transponders
- **Update frequency**: Real-time (API dependent)

## 📈 Key Metrics

### Traffic Classification
- **Overflights**: Aircraft >20,000ft not near airports
- **Domestic**: Aircraft <20,000ft within Iraqi airspace
- **Arrivals/Departures**: Aircraft within 50km of airports
- **Ground**: Aircraft on airport surfaces

### Capacity Management
- **Sector limits**: Based on controller workload capacity
- **Alert thresholds**: 70% (warning), 85% (critical)
- **Flow control**: Automatic recommendations for interventions

## 🛠️ Technical Architecture

### Components
- **Frontend**: Streamlit web interface
- **Data Source**: OpenSky Network REST API
- **Mapping**: Folium interactive maps
- **Analytics**: Pandas/NumPy data processing
- **Visualization**: Plotly charts and graphs

### Real-time Processing
- Aircraft position filtering for Iraqi airspace
- Flight type classification algorithms
- Capacity utilization calculations
- Flow direction analysis

## 🌐 API Integration

### OpenSky Network
- **Endpoint**: `https://opensky-network.org/api/states/all`
- **Rate limits**: Public API limitations apply
- **Coverage**: Global ADS-B data
- **Data format**: JSON with aircraft state vectors

## 📋 Usage Guidelines

### For Air Traffic Controllers
1. Monitor sector utilization in real-time
2. Use alert levels for proactive management
3. Coordinate flow control measures through system recommendations
4. Track overflight patterns and trends

### For Traffic Managers
1. Analyze overflight flow patterns
2. Monitor capacity constraints
3. Plan tactical interventions
4. Coordinate with Baghdad Control Center

### For Supervisors
1. Overview of Iraqi airspace operations
2. Historical trend analysis
3. Performance monitoring
4. Strategic planning support

## 🔒 Limitations & Considerations

### Data Accuracy
- Dependent on aircraft ADS-B equipment
- Coverage may vary by aircraft type
- Real-time data subject to API availability

### Operational Use
- System provides decision support only
- Final authority remains with Baghdad Control
- Coordination required for all flow control measures

### Regional Factors
- Weather impacts not included in current version
- Military traffic may not be visible
- Cross-border coordination considerations

## 🚨 Emergency Procedures

### High Capacity Alerts
1. **Immediate**: Notify Baghdad Control Center
2. **Assessment**: Verify traffic situation
3. **Coordination**: Implement flow control measures
4. **Monitoring**: Track effectiveness of interventions

### System Issues
- Check internet connectivity
- Verify OpenSky API status
- Contact system administrator
- Use backup monitoring systems

## 📞 Support & Contacts

### Technical Support
- System maintenance and updates
- Data source integration
- Feature enhancements

### Operational Support
- Baghdad Control Center coordination
- Flow management procedures
- Emergency response protocols

## 📄 License

This system is developed for Iraqi aviation authorities and supporting organizations. Use in accordance with local aviation regulations and international agreements.

---

**🛩️ Iraq ATFM System** - Ensuring safe and efficient overflight operations through Iraqi airspace.