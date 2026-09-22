from pathlib import Path

import plotly.express as px
import plotly.graph_objs as go
import streamlit as st
import pandas as pd

TARGET_DIR = 'data'
TARGET_CSV = 'data.csv'

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / TARGET_DIR / TARGET_CSV

st.set_page_config(
    page_title='북항/신항 환적효율 대시보드',
    layout='wide',
)

st.title('북항/신항 환적 효율성 KPI 대시보드')
st.caption('데이터: 부산항만공사_외내항컨테이너통합집계정보, 2024년')



