import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Flight Route Dashboard", layout="wide")

st.title("✈️ Flight Route Visualization Dashboard")

# -----------------------------
# 📁 파일 업로드
# -----------------------------
st.sidebar.header("📂 Upload Data")

main_file = st.sidebar.file_uploader(
    "Upload Flight Data CSV",
    type=["csv"]
)

airport_file = st.sidebar.file_uploader(
    "Upload Airport Mapping CSV",
    type=["csv"]
)

if main_file and airport_file:

    df = pd.read_csv(main_file)
    df_airports = pd.read_csv(airport_file)

    # -----------------------------
    # 🧠 데이터 전처리
    # -----------------------------
    selected_columns = ['SEQ_NBR', 'BASE', 'SEQ_PATTERN', 'FLIGHT_PATTERN']
    df = df[selected_columns].copy()

    # 공항 코드 → 이름 매핑
    airport_name_map = df_airports.set_index('Orig')['Name'].to_dict()

    df['BASE_NAME'] = df['BASE'].map(airport_name_map)

    def map_seq_pattern_to_names(pattern):
        if isinstance(pattern, str):
            codes = pattern.split('-')
            names = [airport_name_map.get(code, code) for code in codes]
            return '-'.join(names)
        return pattern

    df['SEQ_PATTERN_NAMES'] = df['SEQ_PATTERN'].apply(map_seq_pattern_to_names)

    # 좌표 매핑
    airport_coords_map = df_airports.set_index('Name')[
        ['Airport1Latitude', 'Airport1Longitude']
    ].apply(tuple, axis=1).to_dict()

    def get_path_coordinates(seq_pattern_names):
        if isinstance(seq_pattern_names, str):
            names = seq_pattern_names.split('-')
            return [airport_coords_map[name] for name in names if name in airport_coords_map]
        return []

    df['PATH_COORDINATES'] = df['SEQ_PATTERN_NAMES'].apply(get_path_coordinates)

    # -----------------------------
    # 🔍 필터
    # -----------------------------
    st.sidebar.header("🔍 Filters")

    base_filter = st.sidebar.multiselect(
        "Select BASE",
        options=df['BASE'].unique()
    )

    pattern_filter = st.sidebar.multiselect(
        "Select SEQ_PATTERN",
        options=df['SEQ_PATTERN'].unique()
    )

    filtered_df = df.copy()

    if base_filter:
        filtered_df = filtered_df[filtered_df['BASE'].isin(base_filter)]

    if pattern_filter:
        filtered_df = filtered_df[filtered_df['SEQ_PATTERN'].isin(pattern_filter)]

    # -----------------------------
    # 📊 KPI
    # -----------------------------
    col1, col2, col3 = st.columns(3)

    col1.metric("Total Flights", len(filtered_df))
    col2.metric("Unique Bases", filtered_df['BASE'].nunique())
    col3.metric("Unique Patterns", filtered_df['SEQ_PATTERN'].nunique())

    # -----------------------------
    # 📋 데이터 테이블
    # -----------------------------
    st.subheader("📋 Flight Data")
    st.dataframe(filtered_df, use_container_width=True)

    # -----------------------------
    # 📈 시각화
    # -----------------------------
    st.subheader("📊 Distribution")

    col1, col2 = st.columns(2)

    with col1:
        fig1 = px.histogram(filtered_df, x="BASE", title="BASE Distribution")
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = px.histogram(filtered_df, x="SEQ_PATTERN", title="Pattern Distribution")
        st.plotly_chart(fig2, use_container_width=True)

    # -----------------------------
    # ✈️ Flight 선택
    # -----------------------------
    st.subheader("✈️ Flight Route Viewer")

    flight_options = filtered_df[filtered_df['PATH_COORDINATES'].map(len) > 0]

    if not flight_options.empty:

        selected_flight = st.selectbox(
            "Select Flight",
            options=flight_options['SEQ_NBR'],
            format_func=lambda x: f"Flight {x}"
        )

        flight_row = flight_options[flight_options['SEQ_NBR'] == selected_flight].iloc[0]
        path = flight_row['PATH_COORDINATES']

        # 좌표 분리
        lats = [p[0] for p in path]
        lons = [p[1] for p in path]

        map_df = pd.DataFrame({
            "lat": lats,
            "lon": lons
        })

        st.map(map_df)

    else:
        st.warning("No flight paths available with coordinates.")

else:
    st.info("👈 Upload both datasets to start.")
