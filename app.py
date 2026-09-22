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

### KPI 카드
# st.subheader('핵심지표')
# st.caption('필터와는 무관합니다.')

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        '환적 TEU Factor (신항)',
        value=f'{kpi_teu_sinhang:.2f}',
        border=True
    )

with col2:
    st.metric(
        '신/북항 TEU격차',
        value=f'{kpi_teu_gap:.2f}%',
        border=True
    )

with col3:
    st.metric(
        '환적 공컨비율 격차',
        value=f'{kpi_empty_gap:.2f}%p',
        border=True
    )

with col4:
    st.metric(
        '물동량-TEU Factor 상관계수',
        f'신항 {kpi_corr_sinhang:.2f} / 북항 {kpi_corr_bukhang:.2f}',
        border=True
    )
###

### 사이드바
with st.sidebar:
    st.header('검색조건')
    month_range = st.slider(
        '월 범위',
        min_value=1,
        max_value=12,
        value=(1,12)
    )
###

### 데이터프레임
filtered = df[(df['월'] >= month_range[0]) & (df['월'] <= month_range[1])]

st.subheader('원본 데이터')
st.dataframe(filtered)
###

### 그래프
col_teu, col_empty = st.columns(2)

with col_teu:
    st.subheader('청코드, 환적여부별 TEU Factor')

    teu = filtered.groupby(['청코드', '환적여부']).agg(물동량=('전체물동량', 'sum'), 개수=('전체개수', sum)).reset_index()
    teu['TEU_FACTOR'] = teu['물동량'] / teu['개수']
    teu['환적여부'] = teu['환적여부'].map({True: '환적', False: '수출입(일반)'})

    teu = teu[teu['청코드'] != '감천']

    teu_fig = px.bar(
        teu,
        x='청코드',
        y='TEU_FACTOR',
        color='환적여부',
        barmode='group'
    )
    st.plotly_chart(teu_fig)

with col_empty:
    st.subheader('청코드, 환적여부별 공컨비율')

    grp2 = filtered.groupby(['청코드', '환적여부', '적공구분'])['전체물동량'].sum().unstack(fill_value=0).reset_index()
    grp2['공컨비율(%)'] = ((grp2['공컨'] / (grp2['공컨'] + grp2['적컨'])) * 100).round(2)
    grp2['환적여부'] = grp2['환적여부'].map({True: '환적', False: '수출입(일반)'})
    grp2 = grp2[grp2['청코드'] != '감천']

    empty_fig = px.bar(
        grp2,
        x='청코드',
        y='공컨비율(%)',
        color='환적여부',
        barmode='group',
        title='공컨 비율'
    )

    st.plotly_chart(empty_fig)



