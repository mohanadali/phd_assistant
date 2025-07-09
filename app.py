import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import st_folium
import requests
import time
from datetime import datetime, timedelta
import pytz
from geopy.distance import geodesic
import json
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Set page configuration
st.set_page_config(
    page_title="Iraq ATFM System - Overflight Management",
    page_icon="🇮🇶",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
.main {
    padding-top: 1rem;
}
.stMetric {
    background-color: #f0f2f6;
    border: 1px solid #e1e5e9;
    padding: 0.5rem;
    border-radius: 0.25rem;
    margin: 0.25rem 0;
}
.alert-high {
    background-color: #dc3545;
    color: white;
    padding: 0.5rem;
    border-radius: 0.25rem;
    margin: 0.25rem 0;
}
.alert-medium {
    background-color: #fd7e14;
    color: white;
    padding: 0.5rem;
    border-radius: 0.25rem;
    margin: 0.25rem 0;
}
.alert-low {
    background-color: #198754;
    color: white;
    padding: 0.5rem;
    border-radius: 0.25rem;
    margin: 0.25rem 0;
}
.sector-info {
    background-color: #e9ecef;
    border-left: 4px solid #007bff;
    padding: 1rem;
    margin: 0.5rem 0;
    border-radius: 0.25rem;
}
</style>
""", unsafe_allow_html=True)

class OpenSkyAPI:
    """Interface to OpenSky Network API for real-time flight data"""
    
    def __init__(self):
        self.base_url = "https://opensky-network.org/api"
        
    def get_states(self, bbox: Optional[Tuple[float, float, float, float]] = None) -> Optional[pd.DataFrame]:
        """Get current aircraft states"""
        try:
            url = f"{self.base_url}/states/all"
            if bbox:
                # bbox: (lat_min, lon_min, lat_max, lon_max)
                url += f"?lamin={bbox[0]}&lomin={bbox[1]}&lamax={bbox[2]}&lomax={bbox[3]}"
            
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            if not data or 'states' not in data or not data['states']:
                return None
                
            # Define column names based on OpenSky API documentation
            columns = [
                'icao24', 'callsign', 'origin_country', 'time_position',
                'last_contact', 'longitude', 'latitude', 'baro_altitude',
                'on_ground', 'velocity', 'true_track', 'vertical_rate',
                'sensors', 'geo_altitude', 'squawk', 'spi', 'position_source'
            ]
            
            df = pd.DataFrame(data['states'], columns=columns)
            df['timestamp'] = data['time']
            
            # Clean and convert data types
            df['callsign'] = df['callsign'].str.strip() if 'callsign' in df.columns else ''
            df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
            df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
            df['baro_altitude'] = pd.to_numeric(df['baro_altitude'], errors='coerce')
            df['velocity'] = pd.to_numeric(df['velocity'], errors='coerce')
            df['true_track'] = pd.to_numeric(df['true_track'], errors='coerce')
            df['vertical_rate'] = pd.to_numeric(df['vertical_rate'], errors='coerce')
            
            # Filter out invalid positions
            df = df.dropna(subset=['latitude', 'longitude'])
            df = df[(df['latitude'] != 0) & (df['longitude'] != 0)]
            
            return df
            
        except Exception as e:
            st.error(f"Error fetching OpenSky data: {str(e)}")
            return None

class IraqATFMSystem:
    """Iraq-specific Air Traffic Flow Management System for Overflights"""
    
    def __init__(self):
        self.opensky = OpenSkyAPI()
        
        # Iraq airspace boundary (approximate)
        self.iraq_boundary = {
            'lat_min': 29.0,
            'lat_max': 37.5,
            'lon_min': 38.5,
            'lon_max': 49.0
        }
        
        # Iraqi airports
        self.iraqi_airports = {
            'ORBI': {'name': 'Baghdad International Airport', 'lat': 33.2625, 'lon': 44.2346, 'capacity': 45, 'type': 'Major'},
            'ORMM': {'name': 'Basra International Airport', 'lat': 30.5491, 'lon': 47.6647, 'capacity': 25, 'type': 'International'},
            'ORER': {'name': 'Erbil International Airport', 'lat': 36.2374, 'lon': 43.9632, 'capacity': 30, 'type': 'International'},
            'ORSU': {'name': 'Sulaymaniyah International Airport', 'lat': 35.5617, 'lon': 45.3147, 'capacity': 20, 'type': 'Regional'},
            'ORNI': {'name': 'Najaf International Airport', 'lat': 31.9886, 'lon': 44.4049, 'capacity': 15, 'type': 'Regional'},
            'ORMF': {'name': 'Mosul Airport', 'lat': 36.3058, 'lon': 43.1447, 'capacity': 15, 'type': 'Domestic'},
            'ORKK': {'name': 'Kirkuk Airport', 'lat': 35.4697, 'lon': 44.3489, 'capacity': 12, 'type': 'Domestic'}
        }
        
        # Iraqi airspace sectors
        self.airspace_sectors = {
            'ORBB_CTR': {
                'name': 'Baghdad Control Center',
                'lat': 33.0, 'lon': 44.0,
                'area': 'Central Iraq',
                'capacity': 35,
                'alt_min': 6000, 'alt_max': 42000
            },
            'ORBB_N': {
                'name': 'Baghdad North Sector',
                'lat': 35.5, 'lon': 44.0,
                'area': 'Northern Iraq',
                'capacity': 25,
                'alt_min': 6000, 'alt_max': 42000
            },
            'ORBB_S': {
                'name': 'Baghdad South Sector',
                'lat': 31.0, 'lon': 45.0,
                'area': 'Southern Iraq',
                'capacity': 20,
                'alt_min': 6000, 'alt_max': 42000
            },
            'ORBB_E': {
                'name': 'Baghdad East Sector',
                'lat': 33.0, 'lon': 47.0,
                'area': 'Eastern Iraq',
                'capacity': 15,
                'alt_min': 6000, 'alt_max': 42000
            }
        }
        
        # Major overflight routes through Iraq
        self.overflight_routes = {
            'L866': {'name': 'L866 (Europe-Asia)', 'points': [(35.0, 42.0), (34.0, 45.0), (33.0, 48.0)]},
            'M644': {'name': 'M644 (Gulf Route)', 'points': [(30.0, 47.0), (32.0, 45.0), (34.0, 44.0)]},
            'UL866': {'name': 'UL866 (Upper Level)', 'points': [(36.0, 43.0), (34.5, 45.5), (33.0, 47.5)]},
            'UM688': {'name': 'UM688 (Middle East Corridor)', 'points': [(31.5, 46.0), (33.5, 44.5), (35.5, 43.0)]}
        }
        
    def get_iraq_traffic(self) -> Optional[pd.DataFrame]:
        """Get traffic data for Iraq airspace"""
        bbox = (
            self.iraq_boundary['lat_min'],
            self.iraq_boundary['lon_min'],
            self.iraq_boundary['lat_max'],
            self.iraq_boundary['lon_max']
        )
        return self.opensky.get_states(bbox)
    
    def classify_aircraft_type(self, df: pd.DataFrame) -> pd.DataFrame:
        """Classify aircraft as overflight, departure, arrival, or domestic"""
        if df is None or df.empty:
            return df
            
        df = df.copy()
        df['flight_type'] = 'Unknown'
        
        for idx, row in df.iterrows():
            lat, lon = row['latitude'], row['longitude']
            altitude = row.get('baro_altitude', 0)
            on_ground = row.get('on_ground', False)
            
            # Check if near any Iraqi airport
            near_airport = False
            for airport_data in self.iraqi_airports.values():
                distance = geodesic((lat, lon), (airport_data['lat'], airport_data['lon'])).kilometers
                if distance <= 50:  # Within 50km of airport
                    near_airport = True
                    break
            
            # Classification logic
            if on_ground:
                df.at[idx, 'flight_type'] = 'Ground'
            elif altitude and altitude > 20000 and not near_airport:
                df.at[idx, 'flight_type'] = 'Overflight'
            elif near_airport and altitude and altitude < 10000:
                df.at[idx, 'flight_type'] = 'Arrival/Departure'
            elif altitude and altitude < 20000:
                df.at[idx, 'flight_type'] = 'Domestic'
            else:
                df.at[idx, 'flight_type'] = 'Transit'
                
        return df
    
    def calculate_sector_traffic(self, df: pd.DataFrame) -> Dict:
        """Calculate traffic load in each airspace sector"""
        if df is None or df.empty:
            return {}
            
        sector_data = {}
        
        for sector_id, sector in self.airspace_sectors.items():
            # Count aircraft in sector (simplified rectangular area)
            sector_aircraft = df[
                (df['latitude'].between(sector['lat'] - 1.5, sector['lat'] + 1.5)) &
                (df['longitude'].between(sector['lon'] - 1.5, sector['lon'] + 1.5)) &
                (df['baro_altitude'] >= sector['alt_min']) &
                (df['baro_altitude'] <= sector['alt_max']) &
                (df['on_ground'] == False)
            ]
            
            traffic_count = len(sector_aircraft)
            capacity_util = (traffic_count / sector['capacity']) * 100
            
            # Determine alert level
            if capacity_util >= 85:
                alert_level = 'HIGH'
            elif capacity_util >= 70:
                alert_level = 'MEDIUM'
            else:
                alert_level = 'LOW'
                
            sector_data[sector_id] = {
                'name': sector['name'],
                'area': sector['area'],
                'traffic_count': traffic_count,
                'capacity': sector['capacity'],
                'capacity_utilization': capacity_util,
                'alert_level': alert_level,
                'coordinates': (sector['lat'], sector['lon']),
                'aircraft_list': sector_aircraft['callsign'].tolist() if not sector_aircraft.empty else []
            }
            
        return sector_data
    
    def analyze_overflight_flow(self, df: pd.DataFrame) -> Dict:
        """Analyze overflight patterns and flow rates"""
        if df is None or df.empty:
            return {}
            
        overflights = df[df['flight_type'] == 'Overflight']
        
        analysis = {
            'total_overflights': len(overflights),
            'by_country': overflights['origin_country'].value_counts().to_dict() if not overflights.empty else {},
            'altitude_distribution': {},
            'flow_rate_analysis': {},
            'route_utilization': {}
        }
        
        if not overflights.empty:
            # Altitude distribution
            alt_ranges = {
                'FL200-FL300': len(overflights[(overflights['baro_altitude'] >= 6096) & (overflights['baro_altitude'] < 9144)]),
                'FL300-FL400': len(overflights[(overflights['baro_altitude'] >= 9144) & (overflights['baro_altitude'] < 12192)]),
                'FL400+': len(overflights[overflights['baro_altitude'] >= 12192])
            }
            analysis['altitude_distribution'] = alt_ranges
            
            # Flow direction analysis
            if 'true_track' in overflights.columns:
                directions = {
                    'Eastbound': len(overflights[(overflights['true_track'] >= 45) & (overflights['true_track'] < 135)]),
                    'Westbound': len(overflights[(overflights['true_track'] >= 225) & (overflights['true_track'] < 315)]),
                    'Northbound': len(overflights[(overflights['true_track'] >= 315) | (overflights['true_track'] < 45)]),
                    'Southbound': len(overflights[(overflights['true_track'] >= 135) & (overflights['true_track'] < 225)])
                }
                analysis['flow_rate_analysis'] = directions
        
        return analysis

def create_iraq_traffic_map(df: pd.DataFrame, sector_data: Dict, airports: Dict) -> folium.Map:
    """Create interactive map showing Iraq airspace traffic"""
    # Center map on Iraq
    m = folium.Map(location=[33.0, 44.0], zoom_start=6)
    
    # Add Iraq boundary
    iraq_coords = [
        [29.0, 38.5], [29.0, 49.0], [37.5, 49.0], [37.5, 38.5], [29.0, 38.5]
    ]
    folium.Polygon(
        locations=iraq_coords,
        color='blue',
        weight=3,
        fill=True,
        fillOpacity=0.1,
        popup="Iraq Airspace"
    ).add_to(m)
    
    # Add aircraft positions
    if df is not None and not df.empty:
        color_map = {
            'Overflight': 'red',
            'Arrival/Departure': 'blue',
            'Domestic': 'green',
            'Transit': 'orange',
            'Ground': 'gray',
            'Unknown': 'purple'
        }
        
        for _, aircraft in df.iterrows():
            flight_type = aircraft.get('flight_type', 'Unknown')
            color = color_map.get(flight_type, 'purple')
            
            popup_text = f"""
            <b>Callsign:</b> {aircraft.get('callsign', 'N/A')}<br>
            <b>Country:</b> {aircraft.get('origin_country', 'N/A')}<br>
            <b>Type:</b> {flight_type}<br>
            <b>Altitude:</b> {aircraft.get('baro_altitude', 'N/A')} m<br>
            <b>Velocity:</b> {aircraft.get('velocity', 'N/A')} m/s<br>
            <b>Track:</b> {aircraft.get('true_track', 'N/A')}°
            """
            
            size = 8 if flight_type == 'Overflight' else 5
            
            folium.CircleMarker(
                location=[aircraft['latitude'], aircraft['longitude']],
                radius=size,
                popup=popup_text,
                color=color,
                fillColor=color,
                fillOpacity=0.7,
                weight=2
            ).add_to(m)
    
    # Add Iraqi airports
    for icao, airport in airports.items():
        popup_text = f"""
        <b>{airport['name']} ({icao})</b><br>
        <b>Type:</b> {airport['type']}<br>
        <b>Capacity:</b> {airport['capacity']} movements/hour
        """
        
        folium.Marker(
            location=[airport['lat'], airport['lon']],
            popup=popup_text,
            icon=folium.Icon(color='darkblue', icon='plane')
        ).add_to(m)
    
    # Add sector centers with status
    for sector_id, data in sector_data.items():
        color_map = {'LOW': 'green', 'MEDIUM': 'orange', 'HIGH': 'red'}
        color = color_map[data['alert_level']]
        
        popup_text = f"""
        <b>{data['name']}</b><br>
        <b>Area:</b> {data['area']}<br>
        <b>Traffic:</b> {data['traffic_count']}/{data['capacity']}<br>
        <b>Utilization:</b> {data['capacity_utilization']:.1f}%<br>
        <b>Alert:</b> {data['alert_level']}
        """
        
        folium.CircleMarker(
            location=data['coordinates'],
            radius=15,
            popup=popup_text,
            color=color,
            fillColor=color,
            fillOpacity=0.5,
            weight=3
        ).add_to(m)
    
    return m

def main():
    # Title and header
    st.title("🇮🇶 Iraq ATFM System - Overflight Management")
    st.markdown("**Real-time Air Traffic Flow Management for Iraqi Airspace**")
    
    # Initialize Iraq ATFM system
    iraq_atfm = IraqATFMSystem()
    
    # Sidebar controls
    st.sidebar.header("Iraq ATFM Controls")
    st.sidebar.markdown("🛫 **Monitoring Iraqi Airspace**")
    
    # Auto-refresh toggle
    auto_refresh = st.sidebar.checkbox("Auto-refresh (60s)", value=False)
    refresh_button = st.sidebar.button("🔄 Refresh Data")
    
    # Display settings
    show_overflights_only = st.sidebar.checkbox("Show Overflights Only", value=False)
    show_sectors = st.sidebar.checkbox("Show Sector Information", value=True)
    
    # Data fetching
    if auto_refresh or refresh_button or 'iraq_flight_data' not in st.session_state:
        with st.spinner("Fetching real-time flight data for Iraqi airspace..."):
            flight_data = iraq_atfm.get_iraq_traffic()
            if flight_data is not None:
                flight_data = iraq_atfm.classify_aircraft_type(flight_data)
            st.session_state.iraq_flight_data = flight_data
            st.session_state.last_update = datetime.now()
    else:
        flight_data = st.session_state.get('iraq_flight_data')
    
    # Display last update time
    if 'last_update' in st.session_state:
        st.sidebar.info(f"Last updated: {st.session_state.last_update.strftime('%H:%M:%S UTC')}")
    
    # Main dashboard
    if flight_data is not None and not flight_data.empty:
        # Filter data if requested
        display_data = flight_data
        if show_overflights_only:
            display_data = flight_data[flight_data['flight_type'] == 'Overflight']
        
        # Calculate metrics
        sector_data = iraq_atfm.calculate_sector_traffic(flight_data)
        overflight_analysis = iraq_atfm.analyze_overflight_flow(flight_data)
        
        # Key metrics row
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            total_aircraft = len(flight_data)
            st.metric("Total Aircraft", total_aircraft)
        
        with col2:
            overflights = len(flight_data[flight_data['flight_type'] == 'Overflight'])
            st.metric("Overflights", overflights)
        
        with col3:
            domestic = len(flight_data[flight_data['flight_type'].isin(['Domestic', 'Arrival/Departure'])])
            st.metric("Domestic Traffic", domestic)
        
        with col4:
            high_alert_sectors = sum(1 for d in sector_data.values() if d['alert_level'] == 'HIGH')
            st.metric("High Alert Sectors", high_alert_sectors)
        
        with col5:
            overflight_rate = (overflights / total_aircraft * 100) if total_aircraft > 0 else 0
            st.metric("Overflight Rate", f"{overflight_rate:.1f}%")
        
        # Two-column layout for main content
        col_left, col_right = st.columns([2.5, 1.5])
        
        with col_left:
            st.subheader("🗺️ Iraqi Airspace Traffic Map")
            
            # Create and display map
            traffic_map = create_iraq_traffic_map(display_data, sector_data, iraq_atfm.iraqi_airports)
            st_folium(traffic_map, width=800, height=600)
        
        with col_right:
            st.subheader("📊 Airspace Sectors")
            
            if show_sectors:
                # Sector status cards
                for sector_id, data in sector_data.items():
                    alert_class = f"alert-{data['alert_level'].lower()}"
                    
                    st.markdown(f"""
                    <div class="{alert_class}">
                        <strong>{data['name']}</strong><br>
                        Area: {data['area']}<br>
                        Traffic: {data['traffic_count']}/{data['capacity']}<br>
                        Utilization: {data['capacity_utilization']:.1f}%<br>
                        Status: {data['alert_level']}
                    </div>
                    """, unsafe_allow_html=True)
            
            # Flight type distribution
            st.subheader("✈️ Flight Type Distribution")
            flight_types = flight_data['flight_type'].value_counts()
            
            fig = px.pie(
                values=flight_types.values,
                names=flight_types.index,
                title="Aircraft by Type"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Detailed analysis section
        st.subheader("📈 Overflight Analysis")
        
        # Create tabs for different analyses
        tab1, tab2, tab3, tab4 = st.tabs(["Sector Utilization", "Overflight Flow", "Country Analysis", "Route Management"])
        
        with tab1:
            # Sector utilization chart
            sector_names = [sector_data[sid]['name'] for sid in sector_data.keys()]
            utilizations = [sector_data[sid]['capacity_utilization'] for sid in sector_data.keys()]
            
            fig = px.bar(
                x=sector_names,
                y=utilizations,
                title="Airspace Sector Utilization",
                color=utilizations,
                color_continuous_scale=['green', 'yellow', 'red'],
                labels={'x': 'Sector', 'y': 'Capacity Utilization (%)'}
            )
            fig.add_hline(y=85, line_dash="dash", line_color="red", annotation_text="Critical Level (85%)")
            fig.add_hline(y=70, line_dash="dash", line_color="orange", annotation_text="Warning Level (70%)")
            st.plotly_chart(fig, use_container_width=True)
            
            # Detailed sector information
            st.subheader("Sector Details")
            for sector_id, data in sector_data.items():
                with st.expander(f"{data['name']} - {data['area']}"):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.write(f"**Current Traffic:** {data['traffic_count']}")
                        st.write(f"**Capacity:** {data['capacity']}")
                        st.write(f"**Utilization:** {data['capacity_utilization']:.1f}%")
                    with col_b:
                        st.write(f"**Alert Level:** {data['alert_level']}")
                        if data['aircraft_list']:
                            st.write(f"**Aircraft:** {', '.join(data['aircraft_list'][:5])}")
                            if len(data['aircraft_list']) > 5:
                                st.write(f"...and {len(data['aircraft_list'])-5} more")
        
        with tab2:
            # Overflight flow analysis
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.subheader("Altitude Distribution")
                if overflight_analysis['altitude_distribution']:
                    alt_dist = overflight_analysis['altitude_distribution']
                    fig = px.bar(
                        x=list(alt_dist.keys()),
                        y=list(alt_dist.values()),
                        title="Overflights by Altitude"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col_b:
                st.subheader("Flow Direction")
                if overflight_analysis['flow_rate_analysis']:
                    flow_data = overflight_analysis['flow_rate_analysis']
                    fig = px.pie(
                        values=list(flow_data.values()),
                        names=list(flow_data.keys()),
                        title="Traffic Flow by Direction"
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            # Country analysis
            st.subheader("Overflight Traffic by Country")
            
            if overflight_analysis['by_country']:
                country_data = overflight_analysis['by_country']
                
                # Top 10 countries
                top_countries = dict(list(country_data.items())[:10])
                
                fig = px.bar(
                    x=list(top_countries.values()),
                    y=list(top_countries.keys()),
                    orientation='h',
                    title="Top 10 Countries by Overflight Volume",
                    labels={'x': 'Number of Aircraft', 'y': 'Country'}
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Detailed country table
                country_df = pd.DataFrame(list(country_data.items()), columns=['Country', 'Aircraft Count'])
                st.dataframe(country_df, use_container_width=True)
        
        with tab4:
            # Route management
            st.subheader("Major Overflight Routes")
            
            for route_id, route in iraq_atfm.overflight_routes.items():
                st.markdown(f"""
                <div class="sector-info">
                    <strong>{route_id}</strong> - {route['name']}<br>
                    Status: <span style="color: green;">Active</span><br>
                    Current Traffic: Monitoring...
                </div>
                """, unsafe_allow_html=True)
            
            # Route recommendations
            st.subheader("Route Management Recommendations")
            
            recommendations = []
            
            # Check sector congestion
            for sector_id, data in sector_data.items():
                if data['alert_level'] == 'HIGH':
                    recommendations.append(f"🚨 **{data['name']}**: Consider rerouting traffic. Sector at {data['capacity_utilization']:.1f}% capacity.")
                elif data['alert_level'] == 'MEDIUM':
                    recommendations.append(f"⚠️ **{data['name']}**: Monitor closely. May need tactical interventions.")
            
            # Overflight-specific recommendations
            if overflight_analysis['total_overflights'] > 30:
                recommendations.append("📈 **High Overflight Volume**: Consider implementing flow control measures.")
            
            if recommendations:
                for rec in recommendations:
                    st.markdown(rec)
            else:
                st.success("✅ All sectors operating within normal parameters. No immediate interventions required.")
        
        # Flow control measures
        st.subheader("🎯 Flow Control Measures")
        
        measures_col1, measures_col2 = st.columns(2)
        
        with measures_col1:
            st.markdown("### Current Measures")
            st.info("📋 **Status**: Normal Operations")
            st.write("• All sectors within operational limits")
            st.write("• Standard separation minima in effect")
            st.write("• No flow restrictions active")
        
        with measures_col2:
            st.markdown("### Available Tools")
            if st.button("🚦 Implement Flow Control"):
                st.warning("Flow control measures would be coordinated with Baghdad Control Center")
            if st.button("📍 Reroute Traffic"):
                st.info("Alternative routes would be activated through coordination")
            if st.button("⏰ Adjust Timing"):
                st.info("Departure slots would be modified for affected flights")
    
    else:
        st.warning("⚠️ No flight data available for Iraqi airspace. Please check your connection and try again.")
        st.info("💡 The system monitors Iraqi airspace using real-time ADS-B data. Data availability may vary based on coverage and aircraft equipment.")
    
    # Auto-refresh functionality
    if auto_refresh:
        time.sleep(60)
        st.rerun()
    
    # Footer information
    st.markdown("---")
    st.markdown("**🛩️ Iraq ATFM System** | Monitoring Iraqi airspace for safe and efficient overflight operations")

if __name__ == "__main__":
    main()
