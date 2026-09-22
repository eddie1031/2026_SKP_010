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

df = pd.read_csv(DATA_PATH, encoding='euc-kr')
df['환적여부'] = df['수출입구분명'].isin(['수출환적', '수입환적'])

def monthly_teu_factor(target_df):
    zone_df = target_df.groupby('월').agg(물동량=('전체물동량', 'sum'), 개수=('전체개수', 'sum')).reset_index()
    zone_df['TEU_FACTOR'] = zone_df['물동량'] / zone_df['개수']
    return zone_df

### TEU FACTOR
teu_all = df.groupby(['청코드', '환적여부']).agg(물동량=('전체물동량', 'sum'), 개수=('전체개수', sum))
teu_all['TEU_FACTOR'] = teu_all['물동량'] / teu_all['개수']
kpi_teu_sinhang = teu_all.loc[('신항', True), 'TEU_FACTOR']
kpi_teu_bukhang = teu_all.loc[('북항', True), 'TEU_FACTOR']
kpi_teu_gap = (kpi_teu_sinhang / kpi_teu_bukhang - 1) * 100
###

### 공컨비율
empty_all = df.groupby(['청코드', '환적여부', '적공구분'])['전체물동량'].sum().unstack(fill_value=0)
empty_all['공컨비율'] = empty_all['공컨'] / (empty_all['공컨'] + empty_all['적컨']) * 100
kpi_empty_sinhang = empty_all.loc[('신항', True), '공컨비율']
kpi_empty_bukhang = empty_all.loc[('북항', True), '공컨비율']
kpi_empty_gap = (kpi_empty_sinhang - kpi_empty_bukhang)
###

### 상관계수
monthly_sin_full = monthly_teu_factor(df[df['청코드'] == '신항'])
monthly_buk_full = monthly_teu_factor(df[df['청코드'] == '북항'])
kpi_corr_sinhang = monthly_sin_full['물동량'].corr(monthly_sin_full['TEU_FACTOR'])
kpi_corr_bukhang = monthly_buk_full['물동량'].corr(monthly_buk_full['TEU_FACTOR'])
###