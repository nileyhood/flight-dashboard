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
    # 🔎 Route Explorer
    # -----------------------------
    st.subheader("🔎 Route Explorer")

    selected_route = st.selectbox(
        "Select a Route",
        filtered_df['SEQ_PATTERN'].unique()
    )

    route_data = filtered_df[filtered_df['SEQ_PATTERN'] == selected_route]

    st.write(f"Total Flights for this route: {len(route_data)}")
    st.dataframe(route_data)

else:
    st.info("👈 Upload your Flight Data CSV to begin analysis.")
