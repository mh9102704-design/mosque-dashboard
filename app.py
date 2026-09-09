import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
import pandas as pd
import datetime

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & SYSTEM-AWARE CSS (PURE BLACK DARK MODE)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Geospatial Hazard & Travel Monitor",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Clean UI: Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 96%; }
    
    /* CSS Variables for Dynamic System Theming */
    :root {
        --bg-page: #f8fafc;
        --text-main: #0f172a;
        --card-bg: #ffffff;
        --card-border: #cbd5e1;
        --hero-bg: #1e293b;
        --hero-text: #ffffff;
        --alert-bg: #fff1f2;
        --alert-border: #fecdd3;
        --alert-title: #9f1239;
        --alert-text: #881337;
        --alert-border-left: #e11d48;
        --tag-bg: #f1f5f9;
        --tag-text: #0f172a;
        --input-bg: #ffffff;
        --input-border: #94a3b8;
        --accent: #2563eb;
    }

    /* PURE BLACK DARK MODE WITH HIGH-CONTRAST TEXT */
    @media (prefers-color-scheme: dark) {
        :root {
            --bg-page: #000000;         
            --text-main: #f1f5f9;       
            --card-bg: #0a0a0a;         
            --card-border: #262626;     
            --hero-bg: #050505;         
            --hero-text: #ffffff;
            --alert-bg: #1a0505;        
            --alert-border: #450a0a;
            --alert-title: #fca5a5;
            --alert-text: #fecaca;
            --alert-border-left: #dc2626;
            --tag-bg: #171717;
            --tag-text: #e2e8f0;
            --input-bg: #121212;        
            --input-border: #333333;
            --accent: #3b82f6;
        }
    }
    
    .stApp {
        background-color: var(--bg-page) !important;
        color: var(--text-main) !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* High Contrast Enforcement */
    label, p, span, h1, h2, h3, h4, h5, h6, 
    div[data-testid="stWidgetLabel"] p,
    .stTabs [data-baseweb="tab"] {
        color: var(--text-main) !important;
        font-weight: 600 !important;
    }
    
    /* Form Inputs */
    input, textarea, div[data-baseweb="select"] > div, div[data-baseweb="base-input"] {
        background-color: var(--input-bg) !important;
        color: var(--text-main) !important;
        border-color: var(--input-border) !important;
    }
    
    /* Hero Header Banner */
    .hero-banner {
        background-color: var(--hero-bg);
        padding: 32px 32px;
        border-radius: 12px;
        margin-bottom: 24px;
        border: 1px solid var(--card-border);
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }
    .hero-title {
        font-family: 'Georgia', serif;
        font-size: 2.4rem;
        color: var(--hero-text) !important;
        margin-bottom: 6px;
    }
    .hero-subtitle {
        font-size: 1.05rem;
        color: var(--hero-text) !important;
        opacity: 0.9;
        line-height: 1.6;
    }
    
    /* Pulse Animation for Critical Alerts */
    @keyframes pulse-dot {
        0% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(1.1); }
        100% { opacity: 1; transform: scale(1); }
    }
    .pulse-icon { display: inline-block; animation: pulse-dot 2s infinite ease-in-out; }
    
    /* Hazard Alert Card */
    .hazard-alert-card {
        background-color: var(--alert-bg);
        border: 1px solid var(--alert-border);
        border-left: 6px solid var(--alert-border-left);
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 28px;
    }
    .hazard-alert-title {
        color: var(--alert-title) !important;
        font-size: 1.1rem;
        font-weight: 700 !important;
        margin-bottom: 6px;
    }
    .hazard-alert-body {
        color: var(--alert-text) !important;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    /* Interactive Cards */
    .gov-card {
        background-color: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 10px;
        padding: 24px;
        margin-bottom: 16px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .gov-card:hover {
        transform: translateY(-2px);
        border-color: var(--accent);
    }
    
    /* Risk Indicator Tags */
    .risk-tag {
        background-color: var(--tag-bg);
        border: 1px solid var(--card-border);
        color: var(--tag-text) !important;
        border-radius: 16px;
        padding: 6px 14px;
        font-size: 0.75rem;
        font-weight: 700 !important;
        display: inline-block;
        margin-right: 8px;
        margin-bottom: 8px;
        letter-spacing: 0.5px;
    }
    
    .dot-indicator { height: 12px; width: 12px; border-radius: 50%; display: inline-block; margin-right: 8px; }
    .dot-level-1 { background-color: #3b82f6; }
    .dot-level-2 { background-color: #eab308; }
    .dot-level-3 { background-color: #f97316; }
    .dot-level-4 { background-color: #ef4444; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. STATE PERSISTENCE & ALERTS DATABASE
# -----------------------------------------------------------------------------
if "corridor_result" not in st.session_state:
    st.session_state.corridor_result = None

if "community_reports" not in st.session_state:
    st.session_state.community_reports = [
        {"location": "M-2 Motorway (Salt Range)", "type": "SLIPPERY ROAD", "time": "Just now", "details": "Light rain causing low friction along descent. Heavy transports advised to gear down."},
        {"location": "Babusar Pass Summit", "type": "ROAD CLOSURE (C)", "time": "2 hours ago", "details": "NHA confirms pass closed for all traffic due to heavy snow accumulation and ice."}
    ]

HAZARD_ALERTS = [
    {"keywords": ["khyber", "kp", "peshawar", "swat", "hazara", "chitral", "dir", "mansehra"], 
     "level": "Level 3: Reconsider Travel",
     "code": "dot-level-3",
     "tags": ["FLASH FLOOD (F)", "LANDSLIDE (L)", "HEAVY RAIN (R)"],
     "msg": "NDMA Watch: Heavy precipitation & localized flash flood risk active across upper KP districts over the next 48 hours."},
    {"keywords": ["babusar", "naran", "kaghan", "chilas", "gilgit", "skardu", "khunjerab"], 
     "level": "Level 4: Do Not Travel",
     "code": "dot-level-4",
     "tags": ["SNOW BLOCKAGE (S)", "BLACK ICE (B)", "FREEZING (F)"],
     "msg": "NHA Alert: High-altitude mountain pass impassable due to heavy snow and ice formation."}
]

# -----------------------------------------------------------------------------
# 3. REMOTE SENSING & GEOSPATIAL API ENGINES
# -----------------------------------------------------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def geocode_location(query):
    url = "https://nominatim.openstreetmap.org/search"
    headers = {"User-Agent": "GeospatialPortfolioApp/1.0", "Accept-Language": "en"}
    try:
        res = requests.get(url, headers=headers, params={"q": query, "format": "json", "limit": 1}, timeout=6)
        if res.status_code == 200 and len(res.json()) > 0:
            data = res.json()[0]
            return float(data["lat"]), float(data["lon"]), data.get("display_name", query)
    except Exception:
        pass
    return None, None, None

@st.cache_data(ttl=3600, show_spinner=False)
def get_osrm_route(o_lat, o_lon, d_lat, d_lon):
    url = f"http://router.project-osrm.org/route/v1/driving/{o_lon},{o_lat};{d_lon},{d_lat}?overview=full&geometries=geojson"
    try:
        res = requests.get(url, timeout=6)
        if res.status_code == 200:
            data = res.json()
            if "routes" in data and data["routes"]:
                route = data["routes"][0]
                polyline = [[lat, lon] for lon, lat in route["geometry"]["coordinates"]]
                dist_km = route["distance"] / 1000.0
                dur_hrs = route["duration"] / 3600.0
                return polyline, dist_km, dur_hrs
    except Exception:
        pass
    return [[o_lat, o_lon], [d_lat, d_lon]], 0.0, 0.0

@st.cache_data(ttl=1800, show_spinner=False)
def get_live_weather(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat, "longitude": lon, 
        "current_weather": True, 
        "hourly": "temperature_2m,precipitation,snow_depth,windspeed_10m", 
        "timezone": "auto"
    }
    try:
        res = requests.get(url, params=params, timeout=6)
        if res.status_code == 200: 
            return res.json()
    except Exception: pass
    return None

@st.cache_data(ttl=86400, show_spinner=False)
def get_nasa_power_data(lat, lon):
    end_date = datetime.date.today().strftime("%Y%m%d")
    start_date = (datetime.date.today() - datetime.timedelta(days=3)).strftime("%Y%m%d")
    url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    params = {
        "parameters": "T2M,PRECTOTCORR,RH2M", 
        "community": "RE", "longitude": lon, "latitude": lat, 
        "start": start_date, "end": end_date, "format": "JSON"
    }
    try:
        res = requests.get(url, params=params, timeout=8)
        if res.status_code == 200:
            return res.json()
    except Exception: pass
    return None

def assess_hazard(temp, precip_24h, snow_24h, wind_speed, location_name="", raw_input=""):
    combined_text = f"{location_name} {raw_input}".lower()
    matched_alert = next((alert for alert in HAZARD_ALERTS if any(kw in combined_text for kw in alert["keywords"])), None)

    if snow_24h > 0.05 or (temp < 0 and precip_24h > 2):
        level_str, dot_cls = "Level 4: Do Not Travel", "dot-level-4"
        tags = ["NATURAL DISASTER (N)", "BLACK ICE (B)", "ROAD CLOSURE (C)"]
        msg = "Severe Winter Storm / Black Ice. Passes blocked or dangerous. Chains mandatory."
    elif precip_24h > 15:
        level_str, dot_cls = "Level 3: Reconsider Travel", "dot-level-3"
        tags = ["HEAVY RAINFALL (R)", "LANDSLIDE (L)", "FLASH FLOOD (F)"]
        msg = "Heavy Rainfall. Flash flood and slope landslide risk active."
    elif wind_speed > 45:
        level_str, dot_cls = "Level 2: Exercise Increased Caution", "dot-level-2"
        tags = ["HIGH WIND GUSTS (W)", "DEBRIS RISK (D)"]
        msg = "High Wind Gusts. Potential for fallen trees or vehicle instability."
    elif temp < 3:
        level_str, dot_cls = "Level 2: Exercise Increased Caution", "dot-level-2"
        tags = ["FREEZING TEMP (F)", "ROAD FROST (R)"]
        msg = "Near-Freezing Temperatures. Road frost expected during early morning hours."
    else:
        level_str, dot_cls = "Level 1: Exercise Normal Precautions", "dot-level-1"
        tags = ["CLEAR ATMOSPHERE (C)"]
        msg = "Normal Atmospheric Conditions. Safe for standard travel."

    if matched_alert:
        level_str, dot_cls = matched_alert["level"], matched_alert["code"]
        tags, msg = matched_alert["tags"], matched_alert["msg"]

    return level_str, dot_cls, tags, msg

def compute_safe_departure(hourly_data):
    try:
        times = pd.to_datetime(hourly_data["time"][:24])
        temps = hourly_data["temperature_2m"][:24]
        precips = hourly_data["precipitation"][:24]
        safe_hours = [times[i] for i in range(24) if temps[i] > 2 and precips[i] < 2.0]
                
        if len(safe_hours) >= 4:
            return f"Optimal Departure Window: {safe_hours[0].strftime('%I:%M %p')} - {safe_hours[-1].strftime('%I:%M %p')}"
        elif len(safe_hours) > 0:
            return f"Narrow Safe Window: Around {safe_hours[0].strftime('%I:%M %p')}. Exercise caution."
        else:
            return "Adverse Conditions: No optimal departure windows over the next 24 hours."
    except Exception:
        return "Exercise standard safety precautions."

# -----------------------------------------------------------------------------
# 4. PORTFOLIO SIDEBAR
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/satellite-in-orbit.png", width=60)
    st.title("Geospatial Platform")
    
    st.divider()
    st.subheader("🛠️ Architecture & Tech Stack")
    st.caption("• **Language:** Python 3.10+\n• **Framework:** Streamlit\n• **Earth Obs:** NASA POWER API\n• **Telemetry:** Open-Meteo High-Res\n• **Routing:** OSRM Network Engine\n• **Mapping:** Folium & Leaflet")
    
    st.divider()
    st.subheader("🚨 Threat Matrix")
    st.write("• **Level 1:** Normal Precautions")
    st.write("• **Level 2:** Increased Caution")
    st.write("• **Level 3:** Reconsider Travel")
    st.write("• **Level 4:** Do Not Travel")
    
    st.divider()
    st.caption("👨‍💻 **Developed by:** Muhammad Hammad")
    st.caption("🎓 *NASA ARSET Certified: Applied Remote Sensing & Earth Observation*")

# -----------------------------------------------------------------------------
# 5. HERO BANNER & HAZARD ALERTS
# -----------------------------------------------------------------------------
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">Geospatial Hazard & Travel Monitor</div>
    <div class="hero-subtitle">
        An environmental risk assessment platform evaluating real-time atmospheric telemetry, 
        satellite climate baselines, and highway network geometry to predict road safety across Pakistan.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hazard-alert-card">
    <div class="hazard-alert-title">
        <span class="pulse-icon">🔴</span> ACTIVE DISASTER & ROAD HAZARD BULLETINS
    </div>
    <div class="hazard-alert-body">
        • <strong>NDMA Watch:</strong> High flash flood and landslide risk active across upper KP and Azad Kashmir.<br/>
        • <strong>NHA Alert:</strong> Babusar Pass (N-15) closed to all traffic due to heavy snow accumulation and ice formation.
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 6. INTERACTIVE APP TABS
# -----------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["🛣️ Highway Corridor Evaluator", "🛰️ Remote Sensing & Telemetry", "📢 Field Intelligence Feed"])

# --- TAB 1: HIGHWAY CORRIDOR EVALUATOR ---
with tab1:
    st.write("<br/>", unsafe_allow_html=True)
    col_orig, col_dest, col_btn = st.columns([2, 2, 1])
    with col_orig:
        origin_input = st.text_input("Origin City / Landmark:", "Lalamusa", key="orig_input")
    with col_dest:
        dest_input = st.text_input("Destination City / Pass:", "Murree", key="dest_input")
    with col_btn:
        st.write("<br/>", unsafe_allow_html=True)
        if st.button("Assess Corridor", use_container_width=True, type="primary"):
            with st.spinner("Processing geospatial routes..."):
                o_lat, o_lon, o_name = geocode_location(origin_input)
                d_lat, d_lon, d_name = geocode_location(dest_input)
                
                if o_lat and d_lat:
                    route_polyline, dist_km, duration_hrs = get_osrm_route(o_lat, o_lon, d_lat, d_lon)
                    w_origin = get_live_weather(o_lat, o_lon)
                    w_dest = get_live_weather(d_lat, d_lon)
                    
                    st.session_state.corridor_result = {
                        "o_lat": o_lat, "o_lon": o_lon, "o_name": o_name,
                        "d_lat": d_lat, "d_lon": d_lon, "d_name": d_name,
                        "route_polyline": route_polyline,
                        "dist_km": dist_km, "duration_hrs": duration_hrs,
                        "w_origin": w_origin, "w_dest": w_dest,
                        "origin_input": origin_input, "dest_input": dest_input
                    }
                else:
                    st.error("Location resolution failed. Check city spelling.")

    res = st.session_state.corridor_result
    if res:
        st.success(f"**Route Acquired:** {res['o_name'].split(',')[0]} ➔ {res['d_name'].split(',')[0]} | **Distance:** {res['dist_km']:.1f} km | **Est. Duration:** {res['duration_hrs']:.1f} hours")
        
        if res['w_dest'] and "hourly" in res['w_dest']:
            dep_text = compute_safe_departure(res['w_dest']["hourly"])
            st.info(f"⏱️ **Trajectory Engine:** {dep_text}")
            
        col_o, col_d = st.columns(2)
        
        with col_o:
            st.markdown('<div class="gov-card">', unsafe_allow_html=True)
            st.write(f"### Origin: {res['origin_input']}")
            o_temp, o_precip, o_snow, o_wind = 20.0, 0.0, 0.0, 10.0
            if res['w_origin']:
                o_curr = res['w_origin'].get("current_weather", {})
                o_hourly = res['w_origin'].get("hourly", {})
                o_temp, o_wind = o_curr.get("temperature", 20.0), o_curr.get("windspeed", 10.0)
                o_precip = max(o_hourly.get("precipitation", [0])[:24])
                o_snow = max(o_hourly.get("snow_depth", [0])[:24])
            
            o_lvl, o_dot, o_tags, o_msg = assess_hazard(o_temp, o_precip, o_snow, o_wind, res['o_name'], res['origin_input'])
            
            st.markdown(f'<div><span class="dot-indicator {o_dot}"></span><strong style="font-size: 1.1rem;">{o_lvl}</strong></div><br/>', unsafe_allow_html=True)
            tag_html = "".join([f'<span class="risk-tag">{t}</span>' for t in o_tags])
            st.markdown(f'<div>{tag_html}</div><br/>', unsafe_allow_html=True)
            st.write(f"**Current Temp:** {o_temp}°C  |  **Max 24h Rain:** {o_precip}mm  |  **Wind:** {o_wind}km/h")
            st.caption(o_msg)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_d:
            st.markdown('<div class="gov-card">', unsafe_allow_html=True)
            st.write(f"### Destination: {res['dest_input']}")
            d_temp, d_precip, d_snow, d_wind = 20.0, 0.0, 0.0, 10.0
            if res['w_dest']:
                d_curr = res['w_dest'].get("current_weather", {})
                d_hourly = res['w_dest'].get("hourly", {})
                d_temp, d_wind = d_curr.get("temperature", 20.0), d_curr.get("windspeed", 10.0)
                d_precip = max(d_hourly.get("precipitation", [0])[:24])
                d_snow = max(d_hourly.get("snow_depth", [0])[:24])
            
            d_lvl, d_dot, d_tags, d_msg = assess_hazard(d_temp, d_precip, d_snow, d_wind, res['d_name'], res['dest_input'])
            
            st.markdown(f'<div><span class="dot-indicator {d_dot}"></span><strong style="font-size: 1.1rem;">{d_lvl}</strong></div><br/>', unsafe_allow_html=True)
            tag_html = "".join([f'<span class="risk-tag">{t}</span>' for t in d_tags])
            st.markdown(f'<div>{tag_html}</div><br/>', unsafe_allow_html=True)
            st.write(f"**Current Temp:** {d_temp}°C  |  **Max 24h Rain:** {d_precip}mm  |  **Wind:** {d_wind}km/h")
            st.caption(d_msg)
            st.markdown('</div>', unsafe_allow_html=True)

        # Map rendered with clean, unwatermarked OpenStreetMap tiles
        m_route = folium.Map(location=[(res['o_lat'] + res['d_lat'])/2, (res['o_lon'] + res['d_lon'])/2], zoom_start=9, tiles="OpenStreetMap")
        folium.Marker([res['o_lat'], res['o_lon']], popup=f"Origin: {res['origin_input']}", icon=folium.Icon(color='green', icon='play')).add_to(m_route)
        folium.Marker([res['d_lat'], res['d_lon']], popup=f"Destination: {res['dest_input']}", icon=folium.Icon(color='red', icon='stop')).add_to(m_route)
        folium.PolyLine(res['route_polyline'], color="#3b82f6", weight=5, opacity=0.85).add_to(m_route)
        
        st_folium(m_route, height=450, use_container_width=True, key="gov_route_map")

# --- TAB 2: REMOTE SENSING & TELEMETRY ---
with tab2:
    st.write("<br/>", unsafe_allow_html=True)
    st.markdown("Assess atmospheric anomalies by cross-referencing Open-Meteo High-Res forecasts against **NASA POWER Multi-Decadal Baselines**.")
    
    search_query = st.text_input("Target Geographic Coordinate or District:", key="single_search")
    
    if search_query.strip():
        with st.spinner("Extracting Earth Observation Data..."):
            lat_f, lon_f, name_f = geocode_location(search_query)
            if lat_f is not None:
                col_m, col_i = st.columns([1.5, 1])
                
                with col_i:
                    st.markdown('<div class="gov-card">', unsafe_allow_html=True)
                    st.write(f"### {name_f.split(',')[0]}")
                    
                    weather_data = get_live_weather(lat_f, lon_f)
                    nasa_data = get_nasa_power_data(lat_f, lon_f)
                    
                    if weather_data:
                        current = weather_data.get("current_weather", {})
                        temp, wind = current.get("temperature", 0.0), current.get("windspeed", 0.0)
                        
                        s_lvl, s_dot, s_tags, s_msg = assess_hazard(temp, 0, 0, wind, name_f, search_query)
                        st.markdown(f'<div><span class="dot-indicator {s_dot}"></span><strong style="font-size: 1.1rem;">{s_lvl}</strong></div><br/>', unsafe_allow_html=True)
                        st.write(f"📡 **Live Telemetry:** Temp {temp}°C | Wind {wind} km/h")
                        
                        if nasa_data and 'properties' in nasa_data:
                            params = nasa_data['properties'].get('parameter', {})
                            if params:
                                dates = list(params['T2M'].keys())
                                if dates:
                                    latest_date = dates[-1]
                                    nasa_temp = params['T2M'][latest_date]
                                    nasa_precip = params['PRECTOTCORR'][latest_date]
                                    st.write(f"🛰️ **NASA POWER Baseline (2m):** Temp {nasa_temp}°C | Precip {nasa_precip}mm")
                        
                        st.caption(s_msg)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col_m:
                    m_single = folium.Map(location=[lat_f, lon_f], zoom_start=11, tiles="OpenStreetMap")
                    folium.Marker([lat_f, lon_f], popup=name_f, icon=folium.Icon(color='blue')).add_to(m_single)
                    st_folium(m_single, height=400, use_container_width=True, key=f"single_gov_map_{lat_f}")
            else:
                st.error("District not found in index.")

# --- TAB 3: FIELD INTELLIGENCE FEED ---
with tab3:
    st.write("<br/>", unsafe_allow_html=True)
    col_f1, col_f2 = st.columns([3, 2])
    
    with col_f1:
        st.write("### Published Ground Reports")
        for report in st.session_state.community_reports:
            st.markdown(f"""
            <div class="gov-card">
                <strong style="font-size: 1.05rem;">📍 {report['location']}</strong>
                <span style="float: right; font-size: 0.85rem; opacity: 0.7;">{report['time']}</span><br/>
                <div style="margin-top: 8px;"><span class="risk-tag">{report['type']}</span></div>
                <div style="margin-top: 8px;">{report['details']}</div>
            </div>
            """, unsafe_allow_html=True)
            
    with col_f2:
        st.markdown('<div class="gov-card">', unsafe_allow_html=True)
        st.write("### File Field Intelligence")
        with st.form("report_form", clear_on_submit=True):
            rep_loc = st.text_input("Corridor / District:", placeholder="e.g., N-5 Expressway near Lalamusa")
            rep_type = st.selectbox("Risk Indicator:", ["CRIME (C)", "HEALTH (H)", "NATURAL DISASTER (N)", "UNREST (U)", "OTHER (O)"])
            rep_details = st.text_area("Field Description:")
            
            if st.form_submit_button("Submit Advisory", type="primary") and rep_loc:
                st.session_state.community_reports.insert(0, {
                    "location": rep_loc, 
                    "type": rep_type, 
                    "time": datetime.date.today().strftime("%m/%d/%Y"), 
                    "details": rep_details
                })
                st.success("Advisory record updated.")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)