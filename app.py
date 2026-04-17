import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Flight Analytics Dashboard", layout="wide")

st.title("✈️ Flight Analytics Dashboard")
st.markdown("Analyze flight patterns, base distribution, and route frequency.")

# -----------------------------
# 📁 업로드 (맨 위로 이동)
# -----------------------------
st.sidebar.header("📂 Upload Data")

flight_file = st.sidebar.file_uploader(
    "Upload Flight Data CSV",
    type=["csv"]
)

airport_file = st.sidebar.file_uploader(
    "Upload Airport Coordinates CSV",
    type=["csv"]
)

# -----------------------------
# 데이터 둘 다 있어야 시작
# -----------------------------
if flight_file:

    df = pd.read_csv(flight_file)
    df = df[['SEQ_NBR', 'BASE', 'SEQ_PATTERN', 'FLIGHT_PATTERN']].dropna()

    df['NUM_STOPS'] = df['SEQ_PATTERN'].apply(lambda x: len(str(x).split('-')))

    # -----------------------------
    # 🔍 필터
    # -----------------------------
    st.sidebar.header("🔍 Filters")

    base_filter = st.sidebar.multiselect("Select BASE", df['BASE'].unique())
    pattern_filter = st.sidebar.multiselect("Select FLIGHT_PATTERN", df['FLIGHT_PATTERN'].unique())

    filtered_df = df.copy()

    if base_filter:
        filtered_df = filtered_df[filtered_df['BASE'].isin(base_filter)]

    if pattern_filter:
        filtered_df = filtered_df[filtered_df['FLIGHT_PATTERN'].isin(pattern_filter)]

    # =====================================================
    # 🗺️ 1️⃣ ROUTE MAP (맨 위로 이동)
    # =====================================================
    st.subheader("🗺️ Route Map (Connected)")

    if airport_file:

        df_airports = pd.read_csv(airport_file)

        # 컬럼 고정
        code_col = "Orig"
        lat_col = "Airport1Latitude"
        lon_col = "Airport1Longitude"
        
        # 안전장치 (컬럼 없으면 에러 메시지)
        required_cols = [code_col, lat_col, lon_col]
        
        missing_cols = [col for col in required_cols if col not in df_airports.columns]
        
        if missing_cols:
            st.error(f"Missing columns in airport CSV: {missing_cols}")
            st.stop()
        
        # 중복 제거 (필수)
        df_airports_clean = df_airports.drop_duplicates(subset=[code_col])
        
        # 매핑 생성
        airport_map = df_airports_clean.set_index(code_col)[[lat_col, lon_col]].to_dict("index")

        airport_map = df_airports.set_index(code_col)[[lat_col, lon_col]].to_dict("index")

        selected_route = st.selectbox(
            "Select Route",
            filtered_df['SEQ_PATTERN'].unique()
        )

        codes = selected_route.split('-')

        lats, lons, valid_codes = [], [], []

        for code in codes:
            if code in airport_map:
                lats.append(airport_map[code][lat_col])
                lons.append(airport_map[code][lon_col])
                valid_codes.append(code)

        if len(lats) > 1:

            map_df = pd.DataFrame({"lat": lats, "lon": lons})

            fig = px.line_mapbox(
                map_df,
                lat="lat",
                lon="lon",
                zoom=3,
                height=500
            )

            fig.add_scattermapbox(
                lat=lats,
                lon=lons,
                mode='markers+text',
                text=valid_codes,
                textposition="top right"
            )

            fig.update_layout(
                mapbox_style="open-street-map",
                margin={"r":0,"t":0,"l":0,"b":0}
            )

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.warning("좌표 매칭 실패")

    else:
        st.info("👈 Airport CSV도 업로드하면 지도 표시됨")

    # =====================================================
    # 📊 KPI
    # =====================================================
    st.subheader("📊 Key Metrics")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Flights", len(filtered_df))
    col2.metric("Unique Bases", filtered_df['BASE'].nunique())
    col3.metric("Unique Routes", filtered_df['SEQ_PATTERN'].nunique())
    col4.metric("Avg Stops", round(filtered_df['NUM_STOPS'].mean(), 2))

    # =====================================================
    # 📋 데이터
    # =====================================================
    st.subheader("📋 Data Preview")
    st.dataframe(filtered_df, use_container_width=True)

    # =====================================================
    # 📈 분석
    # =====================================================
    st.subheader("📍 Base Distribution")
    fig1 = px.bar(filtered_df['BASE'].value_counts().reset_index(),
                  x='BASE', y='count')
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("🛫 Top Routes")
    fig2 = px.bar(filtered_df['SEQ_PATTERN'].value_counts().head(10).reset_index(),
                  x='SEQ_PATTERN', y='count')
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("🧭 Stops Distribution")
    fig3 = px.histogram(filtered_df, x='NUM_STOPS')
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("📊 Pattern Breakdown")
    fig4 = px.pie(filtered_df['FLIGHT_PATTERN'].value_counts().reset_index(),
                  names='FLIGHT_PATTERN', values='count')
    st.plotly_chart(fig4, use_container_width=True)

else:
    st.info("👈 Upload Flight Data CSV to begin.")
