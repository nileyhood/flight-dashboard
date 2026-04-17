import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Flight Analytics Dashboard", layout="wide")

st.title("✈️ Flight Analytics Dashboard")
st.markdown("Analyze flight patterns, base distribution, and route frequency.")

# -----------------------------
# 📁 데이터 업로드
# -----------------------------
uploaded_file = st.sidebar.file_uploader(
    "Upload Flight Data CSV",
    type=["csv"]
)

if uploaded_file:

    df = pd.read_csv(uploaded_file)

    # -----------------------------
    # 🧠 기본 전처리
    # -----------------------------
    df = df[['SEQ_NBR', 'BASE', 'SEQ_PATTERN', 'FLIGHT_PATTERN']].dropna()

    # route 길이 (경유지 수)
    df['NUM_STOPS'] = df['SEQ_PATTERN'].apply(lambda x: len(str(x).split('-')))

    # -----------------------------
    # 🔍 필터
    # -----------------------------
    st.sidebar.header("🔍 Filters")

    base_filter = st.sidebar.multiselect(
        "Select BASE",
        df['BASE'].unique()
    )

    pattern_filter = st.sidebar.multiselect(
        "Select FLIGHT_PATTERN",
        df['FLIGHT_PATTERN'].unique()
    )

    filtered_df = df.copy()

    if base_filter:
        filtered_df = filtered_df[filtered_df['BASE'].isin(base_filter)]

    if pattern_filter:
        filtered_df = filtered_df[filtered_df['FLIGHT_PATTERN'].isin(pattern_filter)]

    # -----------------------------
    # 📊 KPI
    # -----------------------------
    st.subheader("📊 Key Metrics")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Flights", len(filtered_df))
    col2.metric("Unique Bases", filtered_df['BASE'].nunique())
    col3.metric("Unique Routes", filtered_df['SEQ_PATTERN'].nunique())
    col4.metric("Avg Stops", round(filtered_df['NUM_STOPS'].mean(), 2))

    # -----------------------------
    # 📋 데이터 테이블
    # -----------------------------
    st.subheader("📋 Data Preview")
    st.dataframe(filtered_df, use_container_width=True)

    # -----------------------------
    # 📈 분석 1: Base Distribution
    # -----------------------------
    st.subheader("📍 Base Distribution")

    base_counts = filtered_df['BASE'].value_counts().reset_index()
    base_counts.columns = ['BASE', 'Count']

    fig1 = px.bar(base_counts, x='BASE', y='Count', title="Flights per Base")
    st.plotly_chart(fig1, use_container_width=True)

    # -----------------------------
    # 📈 분석 2: Top Routes
    # -----------------------------
    st.subheader("🛫 Top Flight Routes")

    route_counts = filtered_df['SEQ_PATTERN'].value_counts().reset_index().head(10)
    route_counts.columns = ['Route', 'Count']

    fig2 = px.bar(route_counts, x='Route', y='Count', title="Top 10 Routes")
    st.plotly_chart(fig2, use_container_width=True)

    # -----------------------------
    # 📈 분석 3: Stops Distribution
    # -----------------------------
    st.subheader("🧭 Route Complexity (Stops)")

    fig3 = px.histogram(filtered_df, x='NUM_STOPS', nbins=10,
                        title="Distribution of Number of Stops")
    st.plotly_chart(fig3, use_container_width=True)

    # -----------------------------
    # 📈 분석 4: Pattern Breakdown
    # -----------------------------
    st.subheader("📊 Flight Pattern Breakdown")

    pattern_counts = filtered_df['FLIGHT_PATTERN'].value_counts().reset_index()
    pattern_counts.columns = ['Pattern', 'Count']

    fig4 = px.pie(pattern_counts, names='Pattern', values='Count')
    st.plotly_chart(fig4, use_container_width=True)
    # -----------------------------
    # 🗺️ Route Map (LINE VERSION)
    # -----------------------------
    st.subheader("🗺️ Route Map (Connected)")
    
    airport_file = st.sidebar.file_uploader(
        "Upload Airport Coordinates CSV",
        type=["csv"]
    )
    
    if airport_file:
    
        df_airports = pd.read_csv(airport_file)
    
        # 공항 코드 → 좌표 매핑
        airport_map = df_airports.set_index("Orig")[
            ["Airport1Latitude", "Airport1Longitude"]
        ].to_dict("index")
    
        selected_route = st.selectbox(
            "Select Route to Visualize",
            filtered_df['SEQ_PATTERN'].unique()
        )
    
        # route → 좌표 변환
        codes = selected_route.split('-')
    
        lats = []
        lons = []
    
        for code in codes:
            if code in airport_map:
                lats.append(airport_map[code]["Airport1Latitude"])
                lons.append(airport_map[code]["Airport1Longitude"])
    
        if len(lats) > 1:
    
            map_df = pd.DataFrame({
                "lat": lats,
                "lon": lons
            })
    
            fig = px.line_mapbox(
                map_df,
                lat="lat",
                lon="lon",
                zoom=3,
                height=500
            )
    
            # 점도 같이 표시
            fig.add_scattermapbox(
                lat=lats,
                lon=lons,
                mode='markers+text',
                text=codes,
                textposition="top right"
            )
    
            fig.update_layout(
                mapbox_style="open-street-map",
                margin={"r":0,"t":0,"l":0,"b":0}
            )
    
            st.plotly_chart(fig, use_container_width=True)
    
        else:
            st.warning("Not enough coordinates to draw route.")

else:
    st.info("👈 Upload your Flight Data CSV to begin analysis.")
