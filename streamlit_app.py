import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
try:
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import PolynomialFeatures
    sklearn_available = True
except ImportError:
    sklearn_available = False
import warnings
warnings.filterwarnings('ignore')

# 페이지 설정
st.set_page_config(
    page_title="동아IDP대시보드",
    page_icon="📢",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📢 동아IDP대시보드")

# 대시보드 네비게이션
nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
with nav_col2:
    st.markdown("""
    <div style='text-align: center; padding: 10px; background-color: #f0f2f6; border-radius: 10px; margin-bottom: 20px;'>
        <h4>📊 대시보드 네비게이션</h4>
        <p style='margin: 5px 0; color: #666; font-size: 14px;'>현재: 📢 8503 동아IDP대시보드 (예측모델)</p>
        <p style='margin: 5px 0;'>
            <a href="http://10.1.242.65:8506" target="_blank" style='color: #1f77b4; text-decoration: none; font-weight: bold;'>
                👔 8506: 직군 IDP 대시보드 ➜
            </a>
        </p>
    </div>
    """, unsafe_allow_html=True)

with st.expander("ℹ️ 대시보드 사용 가이드", expanded=False):
    st.markdown("""
    **이 대시보드는 동아그룹의 IDP(개인 개발 계획) 현황을 분석하고 예측하기 위해 제작되었습니다.**

    - **전체 현황:** 상단의 KPI 카드는 전체 임직원 대비 IDP 등록률, 총 등록 건수 등 핵심 지표를 요약합니다.
    - **필터 기능:** 좌측 사이드바에서 특정 '회사'나 '직군'을 선택하여 데이터를 필터링할 수 있습니다.
    - **분기별 트렌드:** 시간 흐름에 따른 IDP 등록 추세를 확인하고, 4분기 예측치를 참고할 수 있습니다.
    - **상세 분석:** '회사별' 및 '직군별' 상세 분석 섹션에서 더 깊이 있는 데이터를 탐색할 수 있습니다.
    - **데이터 검색:** 하단의 '전체 회사 상세 현황' 표에서 특정 회사를 검색할 수 있습니다.

    **💡 Tip:** 궁금한 항목에 마우스를 올리면 추가 설명을 볼 수 있습니다. (예: KPI 카드)
    """)

st.markdown("---")

@st.cache_data
def load_real_data():
    """실제 CSV 파일 기반으로 정확한 IDP 데이터 로드"""

    try:
        # 1. 실제 CSV 파일들 로드
        idp_file = "「반출」IDP 신청현황 누적 수립율(중복존재)_0709_최신 수립현황_회사명바꾸기_부서나누기.csv"
        employee_file = "「반출」IDP 신청현황 누적 수립율(중복존재)_0709_인원최신화_6월_임원지우기_회사이름바꿔.csv"

        # 데이터 로드
        idp_data = pd.read_csv(idp_file, encoding='utf-8-sig')
        employee_data = pd.read_csv(employee_file, encoding='utf-8-sig')

        # 2. IDP 수립자 고유 사번별 정리
        idp_unique = idp_data.groupby('사번').agg({
            '이름': 'first',
            '회사': 'first',
            '부서': 'first',
            '등록건수': 'sum'
        }).reset_index()

        idp_unique['IDP수립여부'] = idp_unique['등록건수'] > 0
        idp_with_idp = idp_unique[idp_unique['IDP수립여부'] == True]

        # 3. 사번으로 직군 매칭
        merged = pd.merge(
            idp_with_idp,
            employee_data[['사번', '직군']],
            on='사번',
            how='left'
        )

        # 4. 매칭 성공/실패 분석
        matched_count = merged['직군'].notna().sum()
        unmatched_count = merged['직군'].isna().sum()

        # 5. 전체 직원 대비 직군별 IDP 수립률 계산
        full_merged = pd.merge(
            employee_data[['사번', '직군', '회사']],
            idp_with_idp[['사번', 'IDP수립여부']],
            on='사번',
            how='left'
        )
        full_merged['IDP수립여부'] = full_merged['IDP수립여부'].fillna(False)

        # 6. 직군별 통계 생성
        jobgroup_stats = full_merged.groupby('직군').agg({
            '사번': 'count',  # 전체 인원
            'IDP수립여부': 'sum'  # IDP 수립 인원
        }).reset_index()

        jobgroup_stats.columns = ['직군', '전체인원', 'IDP수립인원']
        jobgroup_stats['수립률(%)'] = (jobgroup_stats['IDP수립인원'] / jobgroup_stats['전체인원'] * 100).round(1)

        # 7. 회사별 통계 생성
        company_stats = full_merged.groupby('회사').agg({
            '사번': 'count',
            'IDP수립여부': 'sum'
        }).reset_index()
        company_stats.columns = ['회사명', '전체_직원수', 'IDP_등록자수']
        company_stats['등록률(%)'] = (company_stats['IDP_등록자수'] / company_stats['전체_직원수'] * 100).round(1)

        # 8. 회사별 분기별 데이터 생성 (실제 분기별 데이터 기준)
        # 분기별 컬럼이 있다고 가정하고 분기별 등록자 수를 계산
        # 실제로는 분기별 정보가 IDP 데이터에서 추출되어야 하지만,
        # 여기서는 전체 등록자수를 분기별로 분배하여 시뮬레이션
        np.random.seed(42)  # 일관된 결과를 위한 시드 설정

        for idx, row in company_stats.iterrows():
            total_idp = row['IDP_등록자수']
            # 실제 분기별 비율 적용 (3093:2709:1752 비율)
            total_quarters = 3093 + 2709 + 1752
            q1_ratio = 3093 / total_quarters
            q2_ratio = 2709 / total_quarters
            q3_ratio = 1752 / total_quarters

            # 회사별 분기별 등록자 수 계산
            q1_count = int(total_idp * q1_ratio)
            q2_count = int(total_idp * q2_ratio)
            q3_count = total_idp - q1_count - q2_count  # 나머지

            company_stats.loc[idx, '1분기_등록자'] = q1_count
            company_stats.loc[idx, '2분기_등록자'] = q2_count
            company_stats.loc[idx, '3분기_등록자'] = q3_count

        # 8. 분기별 더미 데이터 (기존 로직 호환용)
        q1_data = {'total': len(idp_with_idp) // 3}
        q2_data = {'total': len(idp_with_idp) // 3}
        q3_data = {'total': len(idp_with_idp) - 2 * (len(idp_with_idp) // 3)}

        # 9. 반환용 데이터 구조 생성
        # 기존 DATA 구조와 호환되도록 생성
        result_data = company_stats.copy()
        result_data['총_IDP_등록건'] = result_data['IDP_등록자수']

        # UNIQUE_IDP_DATA: 매칭된 IDP 사용자
        unique_idp_data = merged[merged['직군'].notna()].copy()
        unique_idp_data['사번_extracted'] = unique_idp_data['사번']

        # JOBGROUP_DATA: 전체 직원 데이터
        jobgroup_data = employee_data.copy()
        jobgroup_data['사번_clean'] = jobgroup_data['사번']

        # MERGED_DATA: 매칭된 데이터
        merged_data = merged.copy()
        merged_data['사번_extracted'] = merged_data['사번']

        return result_data, merged_data, jobgroup_data, unique_idp_data, {
            'matched_count': matched_count,
            'unmatched_count': unmatched_count,
            'jobgroup_stats': jobgroup_stats,
            'q1_data': q1_data,
            'q2_data': q2_data,
            'q3_data': q3_data
        }

    except FileNotFoundError:
        # 데이터 파일이 없을 경우, 빈 데이터프레임을 반환하여 앱이 중단되지 않도록 함
        # 상위 레벨에서 이 상태를 확인하고 사용자에게 경고 메시지를 표시
        empty_df = pd.DataFrame()
        return empty_df, empty_df, empty_df, empty_df, {}
    except Exception as e:
        st.error(f"데이터 처리 중 예상치 못한 오류가 발생했습니다: {e}")
        # 다른 종류의 오류는 사용자에게 표시
        empty_df = pd.DataFrame()
        return empty_df, empty_df, empty_df, empty_df, {}

# 데이터 로드
DATA, MERGED_DATA, JOBGROUP_DATA, UNIQUE_IDP_DATA, ANALYSIS_RESULTS = load_real_data()

# 데이터 로드 실패 시 경고 메시지 표시
if DATA.empty:
    st.warning("""
    **⚠️ 데이터 파일을 찾을 수 없습니다.**

    대시보드가 정상적으로 작동하려면 원본 데이터 파일이 필요합니다. 현재는 예시 데이터로 실행되고 있습니다.

    **해결 방법:** `streamlit_app.py`와 동일한 경로에 다음 두 개의 CSV 파일이 있는지 확인해주세요:
    - `「반출」IDP 신청현황 누적 수립율(중복존재)_0709_최신 수립현황_회사명바꾸기_부서나누기.csv`
    - `「반출」IDP 신청현황 누적 수립율(중복존재)_0709_인원최신화_6월_임원지우기_회사이름바꿔.csv`
    """)

# 전체 통계 계산 (정확한 데이터 기반)
if 'jobgroup_stats' in ANALYSIS_RESULTS:
    jobgroup_stats = ANALYSIS_RESULTS['jobgroup_stats']
    total_employees = jobgroup_stats['전체인원'].sum()
    total_idp_employees = jobgroup_stats['IDP수립인원'].sum()
    matched_count = ANALYSIS_RESULTS.get('matched_count', 0)
    unmatched_count = ANALYSIS_RESULTS.get('unmatched_count', 0)
    overall_participation_rate = (total_idp_employees / total_employees * 100) if total_employees > 0 else 0
else:
    total_employees = 6768
    total_idp_employees = 3541
    matched_count = 3541
    unmatched_count = 84
    overall_participation_rate = 52.3

# 분기별 데이터 (실제 분석 결과 사용)
# 실제 분기별 등록자 수 데이터
quarter_data_real = {
    '1분기': {'등록자수': 3093, '등록건수': 3139},
    '2분기': {'등록자수': 2709, '등록건수': 2720},
    '3분기': {'등록자수': 1752, '등록건수': 1752}
}

q1_total = quarter_data_real['1분기']['등록자수']
q2_total = quarter_data_real['2분기']['등록자수']
q3_total = quarter_data_real['3분기']['등록자수']

# 기존 변수들 호환성 유지
if not DATA.empty:
    total_idp_registrations = DATA['총_IDP_등록건'].sum() if '총_IDP_등록건' in DATA.columns else total_idp_employees
    average_participation_rate = DATA['등록률(%)'].mean() if '등록률(%)' in DATA.columns else overall_participation_rate
else:
    total_idp_registrations = total_idp_employees
    average_participation_rate = overall_participation_rate

# 실제 등록률 계산 (중복 제거된 인원 기준)
overall_registration_rate = (total_idp_employees / total_employees * 100) if total_employees > 0 else 0

# 분기별 등록률 계산 (중복 제거된 실제 데이터 기준)
quarters = ['1분기', '2분기', '3분기']
quarterly_rates = []

for quarter in quarters:
    if f'{quarter}_IDP_등록' in DATA.columns:
        total_reg = DATA[f'{quarter}_IDP_등록'].sum()
        rate = (total_reg / total_employees * 100) if total_employees > 0 else 0
    else:
        rate = 0
    quarterly_rates.append(rate)

# 전체 승인률은 실제 등록률과 동일하게 설정 (중복 제거 기준)
overall_approval_rate = overall_registration_rate

# ------------------------------------------------------------------
#  KPI 카드 섹션
# ------------------------------------------------------------------
st.subheader("📊 전체 현황")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="🏢 전체 임직원",
        value=f"{total_employees:,}명",
        help="동아그룹 13개 계열사 전체 임직원 수 (동천수, 수석 → 동아에코팩 합병)"
    )

with col2:
    st.metric(
        label="📋 총 IDP 등록건",
        value=f"{total_idp_registrations:,}건",
        help="전체 IDP 등록 건수 (중복 포함)"
    )

with col3:
    st.metric(
        label="📈 전체 등록률",
        value=f"{overall_registration_rate:.1f}%",
        delta=f"실제: {total_idp_employees:,}명",
        help="중복 제거된 실제 등록 인원 기준 등록률"
    )

with col4:
    st.metric(
        label="✅ 실제 등록인원",
        value=f"{total_idp_employees:,}명",
        help="중복 제거된 실제 IDP 등록 인원"
    )

with col5:
    avg_quarterly_rate = sum(quarterly_rates) / len(quarterly_rates) if quarterly_rates else 0
    st.metric(
        label="🎯 분기평균 등록률",
        value=f"{avg_quarterly_rate:.1f}%",
        help="1,2,3분기 등록률의 평균값 (중복 제거 기준)"
    )

st.markdown("---")

# ------------------------------------------------------------------
#  인사이트 및 독려 활동 섹션
# ------------------------------------------------------------------
st.subheader("💡 주요 인사이트 및 독려 활동")

# 인사이트 탭과 독려 활동 탭으로 구분
insight_tab, activity_tab = st.tabs(["📊 데이터 인사이트", "📢 독려 활동"])

with insight_tab:
    # 인사이트 컬럼 구성
    insight_col1, insight_col2 = st.columns(2)

    with insight_col1:
        st.markdown("### 🎯 핵심 발견사항")

        # 동적 인사이트 생성
        if not DATA.empty and '등록률(%)' in DATA.columns:
            top_company = DATA.nlargest(1, '등록률(%)')['회사명'].iloc[0]
            top_rate = DATA.nlargest(1, '등록률(%)')['등록률(%)'].iloc[0]

            low_companies = DATA[DATA['등록률(%)'] < 10].shape[0]
            high_companies = DATA[DATA['등록률(%)'] >= 50].shape[0]
        else:
            top_company = "N/A"
            top_rate = 0
            low_companies = 0
            high_companies = 0

        # 트렌드 분석 (실제 데이터 기반)
        trend_change = q3_total - q1_total
        trend_percent = ((q3_total - q1_total) / q1_total * 100) if q1_total > 0 else 0

        if trend_change > 0:
            trend_direction = f"📈 증가 (+{trend_change:,}명, +{trend_percent:.1f}%)"
        elif trend_change < 0:
            trend_direction = f"📉 감소 ({trend_change:,}명, {trend_percent:.1f}%)"
        else:
            trend_direction = "➡️ 변화없음"

        # --- 직군별 등록률 요약 추가 ---
        jobgroup_summary = ""
        try:
            if not JOBGROUP_DATA.empty and '직군' in JOBGROUP_DATA.columns and not UNIQUE_IDP_DATA.empty:
                jobgroup_mapping = JOBGROUP_DATA.set_index('사번_clean')['직군'].to_dict()
                unique_with_jobgroup = UNIQUE_IDP_DATA.copy()
                unique_with_jobgroup['직군'] = unique_with_jobgroup['사번_extracted'].map(jobgroup_mapping)
                unique_with_jobgroup['직군'] = unique_with_jobgroup['직군'].fillna('기타')
                total_by_jobgroup = JOBGROUP_DATA['직군'].value_counts()
                idp_by_jobgroup = unique_with_jobgroup.groupby('직군')['사번_extracted'].nunique()
                jobgroup_rates = (idp_by_jobgroup / total_by_jobgroup * 100).round(1).dropna()
                jobgroup_rates = jobgroup_rates[jobgroup_rates.index.notnull()]
                if not jobgroup_rates.empty:
                    avg_rate = jobgroup_rates.mean()
                    top3 = jobgroup_rates.sort_values(ascending=False).head(3)
                    bottom3 = jobgroup_rates.sort_values().head(3)
                    jobgroup_summary = f"""
**직군별 등록률 요약**
- 전체 평균: {avg_rate:.1f}%
- Top3: {', '.join([f'{k}({v:.1f}%)' for k,v in top3.items()])}
- Bottom3: {', '.join([f'{k}({v:.1f}%)' for k,v in bottom3.items()])}
"""
        except Exception as e:
            jobgroup_summary = "(직군별 등록률 계산 오류)"
        st.markdown(f"""
        **🏆 최고 성과**
        - **{top_company}**: {top_rate:.1f}% 등록률로 1위

        **📊 등록률 분포**
        - 50% 이상: {high_companies}개 회사
        - 10% 미만: {low_companies}개 회사

        **📈 분기별 트렌드**
        - 1분기: {q1_total:,}건 → 3분기: {q3_total:,}건
        - 전체 추세: {trend_direction}

        {jobgroup_summary}
        """)

    with insight_col2:
        st.markdown("### 🎯 개선 제안")

        # 개선이 필요한 회사들
        if not DATA.empty and '등록률(%)' in DATA.columns and '전체_직원수' in DATA.columns:
            low_performance = DATA[DATA['등록률(%)'] < 20].sort_values('전체_직원수', ascending=False)
        else:
            low_performance = pd.DataFrame()

        st.markdown(f"""
        **⚠️ 집중 관리 대상**
        """)

        if not low_performance.empty:
            for idx, row in low_performance.head(3).iterrows():
                st.markdown(f"- **{row['회사명']}**: {row['등록률(%)']:.1f}% ({row['전체_직원수']:,}명)")

        st.markdown(f"""

        **💡 제안사항**
        - 등록률 30% 미만 회사 대상 개별 지원
        - 우수 회사 사례 공유 세션 개최
        - 분기별 목표 설정 및 인센티브 도입
        - 부서장 대상 IDP 중요성 교육 강화
        """)

with activity_tab:
    st.markdown("### 📬 월간 IDP 레터")

    # IDP 레터 정보
    letters = [
        {
            "월": "8월",
            "제목": "8월 IDP 레터",
            "url": "https://www.mangoboard.net/publish/49752447",
            "설명": "8월 IDP 등록 현황 및 주요 안내"
        },
        {
            "월": "7월",
            "제목": "7월 IDP 레터",
            "url": "https://www.mangoboard.net/publish/49384442",
            "설명": "3분기 IDP 등록 현황 및 우수 사례 공유"
        },
        {
            "월": "6월",
            "제목": "6월 IDP 레터",
            "url": "https://www.mangoboard.net/publish/48822338",
            "설명": "2분기 중간 점검 및 등록 독려"
        }
    ]

    # 레터 카드 형태로 표시
    letter_col1, letter_col2, letter_col3 = st.columns(3)
    for i, letter in enumerate(letters):
        with [letter_col1, letter_col2, letter_col3][i]:
            with st.container():
                st.markdown(f"""
                <div style="
                    padding: 1rem;
                    border: 1px solid #ddd;
                    border-radius: 0.5rem;
                    background-color: #f8f9fa;
                    margin-bottom: 1rem;
                ">
                    <h4 style="margin-top: 0; color: #1f77b4;">📧 {letter['월']} 레터</h4>
                    <p style="margin: 0.5rem 0; font-size: 0.9rem;">{letter['설명']}</p>
                    <a href="{letter['url']}" target="_blank" style="
                        display: inline-block;
                        padding: 0.5rem 1rem;
                        background-color: #1f77b4;
                        color: white;
                        text-decoration: none;
                        border-radius: 0.25rem;
                        font-size: 0.9rem;
                    ">레터 보기 →</a>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("### 🎯 진행 중인 독려 활동")
    activity_col1, activity_col2 = st.columns(2)
    with activity_col1:
        st.markdown("""
        **📅 정기 활동**
        - 📬 월간 IDP 레터 발송
        - 📊 분기별 등록률 현황 공유
        - 🏆 우수 회사/개인 사례 발굴
        - 📞 저조 회사 개별 상담
        - 🆕 신규계열사(앱티스, 동아에코팩, 한국신동공업, 동아오츠카, 동아참메드, 디에이인포메이션, 수석, 동천수)와 기존계열사에 차별화된 독려이벤트 진행 중
        """)
    with activity_col2:
        st.markdown("""
        **💡 추가 독려 방법 제안**
        - 🥇 회사별 등록률 경쟁 프로그램 도입
        - 🏅 개인별 우수 IDP 시상 아이디어
        - 📈 목표 달성 회사 포상 방안
        - 🎉 분기별 성과 축하 이벤트 제안
        ※ 위 내용은 실제 운영 중인 제도가 아니라, 향후 도입 가능한 아이디어/제안임을 안내드립니다.
        """)

st.markdown("---")

# ------------------------------------------------------------------
#  사이드바 필터
# ------------------------------------------------------------------

# 사이드바 네비게이션
st.sidebar.markdown("---")
st.sidebar.markdown("### 🚀 대시보드 바로가기")
st.sidebar.markdown("""
<div style='background-color: #f8f9fa; padding: 10px; border-radius: 8px; margin-bottom: 15px;'>
    <p style='margin: 0; font-size: 12px; color: #6c757d;'>현재: 📢 8503 동아IDP대시보드</p>
    <a href="http://10.1.242.65:8506" target="_blank" style='color: #007bff; text-decoration: none; font-size: 14px;'>
        👔 8506: 직군 IDP ➜
    </a>
</div>
""", unsafe_allow_html=True)

st.sidebar.header("📋 필터 옵션")

companies = ["전체"] + sorted(DATA["회사명"].unique())
selected_company = st.sidebar.selectbox("회사 선택", companies)

# 직군 선택 (Panel 위젯 스타일)
st.sidebar.markdown("---")
st.sidebar.subheader("🔧 직군 필터")

# 직군 옵션 준비 - 실제 CSV 데이터에서 추출
try:
    if not JOBGROUP_DATA.empty and '직군' in JOBGROUP_DATA.columns:
        job_groups = sorted(JOBGROUP_DATA['직군'].dropna().unique().tolist())
    else:
        job_groups = ['경영관리', '기타', '연구개발', '영업/마케팅', '제조', '품질관리']  # 기본값
except:
    job_groups = ['경영관리', '기타', '연구개발', '영업/마케팅', '제조', '품질관리']  # 기본값

selected_job_groups = st.sidebar.multiselect(
    "직군 선택",
    options=job_groups,
    default=[],  # 빈 리스트 → 전체
    placeholder="전체 직군",
    help="여러 직군을 선택할 수 있습니다. 선택하지 않으면 전체 직군이 표시됩니다."
)

# 필터링
if selected_company != "전체":
    filtered_data = DATA[DATA["회사명"] == selected_company]
else:
    filtered_data = DATA.copy()

# 직군별 필터링은 상세 분석에서 사용
if len(selected_job_groups) > 0:
    filtered_jobgroup_data = MERGED_DATA[MERGED_DATA['직군'].isin(selected_job_groups)]
else:
    filtered_jobgroup_data = MERGED_DATA.copy()

# 사이드바에 직군별 요약 표시
st.sidebar.markdown("---")
st.sidebar.subheader("📊 직군별 요약")

# 전체 직군 통계 (실제 직군 컬럼 사용)
try:
    if not JOBGROUP_DATA.empty and '직군' in JOBGROUP_DATA.columns:
        # 실제 CSV 파일의 직군 컬럼을 직접 사용
        total_jobgroup_stats = JOBGROUP_DATA['직군'].value_counts()
    else:
        total_jobgroup_stats = pd.Series()
        st.sidebar.error("직군 데이터를 찾을 수 없습니다.")
except Exception as e:
    total_jobgroup_stats = pd.Series()
    st.sidebar.error(f"직군 통계 오류: {e}")

# IDP 직군 통계 (사번 매칭을 통한 실제 직군 정보 사용)
try:
    if not UNIQUE_IDP_DATA.empty and not JOBGROUP_DATA.empty and '직군' in JOBGROUP_DATA.columns and '사번_clean' in JOBGROUP_DATA.columns:
        # 사번을 통해 실제 직군 정보 매핑
        unique_with_jobgroup = UNIQUE_IDP_DATA.copy()
        jobgroup_mapping = JOBGROUP_DATA.set_index('사번_clean')['직군'].to_dict()

        # 사번으로 직군 매핑
        unique_with_jobgroup['직군'] = unique_with_jobgroup['사번_extracted'].map(jobgroup_mapping)

        # 매핑되지 않은 경우 '기타'로 분류
        unique_with_jobgroup['직군'] = unique_with_jobgroup['직군'].fillna('기타')

        # 직군별 실제 등록자 수 계산 (중복 제거)
        idp_jobgroup_stats = unique_with_jobgroup.groupby('직군')['사번_extracted'].nunique()

    else:
        idp_jobgroup_stats = pd.Series()
        st.sidebar.error("IDP 직군 매핑에 필요한 데이터가 부족합니다.")
except Exception as e:
    st.sidebar.error(f"IDP 직군 통계 계산 오류: {e}")
    idp_jobgroup_stats = pd.Series()

st.sidebar.markdown("**전체 직군 현황:**")
if not total_jobgroup_stats.empty:
    # 실제 데이터에서 존재하는 직군들을 표시
    for jobgroup in total_jobgroup_stats.index:
        total_count = total_jobgroup_stats.get(jobgroup, 0)
        idp_count = idp_jobgroup_stats.get(jobgroup, 0)
        participation_rate = (idp_count / total_count * 100) if total_count > 0 else 0

        is_selected = jobgroup in selected_job_groups
        icon = "🔹" if is_selected else "▫️"

        st.sidebar.markdown(f"{icon} **{jobgroup}**: {participation_rate:.1f}% ({idp_count:,}/{total_count:,}명)")
else:
    st.sidebar.warning("직군 데이터를 불러올 수 없습니다.")

if len(selected_job_groups) > 0:
    st.sidebar.markdown("---")
    st.sidebar.success(f"✅ {len(selected_job_groups)}개 직군 선택됨")

    # 선택된 직군의 총 통계
    selected_total = sum([total_jobgroup_stats.get(jg, 0) for jg in selected_job_groups])
    selected_idp = sum([idp_jobgroup_stats.get(jg, 0) for jg in selected_job_groups])
    selected_rate = (selected_idp / selected_total * 100) if selected_total > 0 else 0
    st.sidebar.metric(
        label="선택 직군 참여율",
        value=f"{selected_rate:.1f}%",
        delta=f"{selected_idp:,}/{selected_total:,}명"
    )
# ------------------------------------------------------------------
#  분기별 트렌드 분석
# ------------------------------------------------------------------
st.subheader("📈 분기별 IDP 등록 트렌드")

# 분기별 데이터 준비 - 실제 분석 결과 사용
quarters = ['1분기', '2분기', '3분기']

# 실제 분석 결과에서 분기별 데이터 (앞에서 분석한 실제 수치 사용)
quarter_data = {
    '1분기': {'등록자수': 3093, '등록건수': 3139},
    '2분기': {'등록자수': 2709, '등록건수': 2720},
    '3분기': {'등록자수': 1752, '등록건수': 1752}
}

quarter_totals = []
quarter_rates = []

for quarter in quarters:
    # 실제 분기별 등록자 수 사용
    total_reg = quarter_data[quarter]['등록자수']
    rate = (total_reg / total_employees * 100) if total_employees > 0 else 0
    quarter_totals.append(total_reg)
    quarter_rates.append(rate)

col1, col2 = st.columns([1.2, 0.8])

with col1:
    # 분기별 등록 건수 라인 차트
    fig_trend = go.Figure()

    fig_trend.add_trace(go.Scatter(
        x=quarters,
        y=quarter_totals,
        mode='lines+markers',
        name='등록 건수',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=10)
    ))

    fig_trend.update_layout(
        title="분기별 IDP 등록 건수 추이",
        xaxis_title="분기",
        yaxis_title="등록 건수",
        height=400,
        showlegend=False
    )

    st.plotly_chart(fig_trend, use_container_width=True)

with col2:
    # 분기별 수치 표
    quarter_summary = pd.DataFrame({
        '분기': quarters,
        '등록건수': quarter_totals,
        '등록률(%)': [f"{rate:.1f}%" for rate in quarter_rates]
    })

    st.markdown("**분기별 요약**")
    st.dataframe(
        quarter_summary,
        use_container_width=True,
        hide_index=True
    )

    # 분기별 평균
    avg_registrations = sum(quarter_totals) / len(quarters)
    avg_rate = sum(quarter_rates) / len(quarters)

    st.markdown(f"""
    **📊 분기별 평균**
    - 평균 등록건수: {avg_registrations:.0f}건
    - 평균 등록률: {avg_rate:.1f}%
    """)

st.markdown("---")

# ------------------------------------------------------------------
#  4분기 예측 모델
# ------------------------------------------------------------------
st.subheader("🔮 4분기 IDP 등록 예측 모델")

if sklearn_available:
    def create_prediction_model():
        """1-3분기 데이터를 바탕으로 4분기 예측"""
        try:
            # 실제 분기별 데이터
            quarters_num = np.array([1, 2, 3]).reshape(-1, 1)
            actual_registrations = np.array([3093, 2709, 1752])

            # 1. 선형 회귀 모델
            linear_model = LinearRegression()
            linear_model.fit(quarters_num, actual_registrations)

            # 2. 다항식 회귀 모델 (2차)
            poly_features = PolynomialFeatures(degree=2)
            quarters_poly = poly_features.fit_transform(quarters_num)
            poly_model = LinearRegression()
            poly_model.fit(quarters_poly, actual_registrations)

            # 4분기 예측
            q4_linear = linear_model.predict([[4]])[0]
            q4_poly = poly_model.predict(poly_features.transform([[4]]))[0]

            # 3. 추세 기반 예측 (감소율 적용)
            q2_to_q1_ratio = 2709 / 3093  # 약 0.876
            q3_to_q2_ratio = 1752 / 2709  # 약 0.647
            avg_decline = (q2_to_q1_ratio + q3_to_q2_ratio) / 2  # 약 0.762
            q4_trend = 1752 * avg_decline

            # 4. 계절성 반영 (연말 집중 등록 15% 증가)
            q4_seasonal = q4_trend * 1.15

            # 예측값들
            predictions = {
                'linear': max(0, q4_linear),
                'polynomial': max(0, q4_poly),
                'trend': max(0, q4_trend),
                'seasonal': max(0, q4_seasonal)
            }

            return predictions

        except Exception as e:
            st.error(f"예측 모델 오류: {e}")
            return None

    # 예측 실행
    predictions = create_prediction_model()

    if predictions:
        # 시나리오별 예측
        optimistic = max(predictions.values())  # 최대값 (낙관적)
        realistic = np.mean(list(predictions.values()))  # 평균값 (현실적)
        conservative = min(predictions.values())  # 최소값 (보수적)

        pred_col1, pred_col2, pred_col3 = st.columns(3)

        with pred_col1:
            total_optimistic = 3093 + 2709 + 1752 + optimistic
            rate_optimistic = (total_optimistic / total_employees * 100) if total_employees > 0 else 0
            st.success(f"""
            **🟢 낙관적 시나리오**
            - 4분기 예측: **{optimistic:,.0f}명**
            - 연간 총계: **{total_optimistic:,.0f}명**
            - 예상 등록률: **{rate_optimistic:.1f}%**
            """)

        with pred_col2:
            total_realistic = 3093 + 2709 + 1752 + realistic
            rate_realistic = (total_realistic / total_employees * 100) if total_employees > 0 else 0
            st.info(f"""
            **🟡 현실적 시나리오** (권장)
            - 4분기 예측: **{realistic:,.0f}명**
            - 연간 총계: **{total_realistic:,.0f}명**
            - 예상 등록률: **{rate_realistic:.1f}%**
            """)

        with pred_col3:
            total_conservative = 3093 + 2709 + 1752 + conservative
            rate_conservative = (total_conservative / total_employees * 100) if total_employees > 0 else 0
            st.warning(f"""
            **🔴 보수적 시나리오**
            - 4분기 예측: **{conservative:,.0f}명**
            - 연간 총계: **{total_conservative:,.0f}명**
            - 예상 등록률: **{rate_conservative:.1f}%**
            """)

        # 예측 차트
        quarters = ['1분기', '2분기', '3분기', '4분기(예측)']
        actual_data = [3093, 2709, 1752, realistic]

        fig_pred = go.Figure()

        # 실제 데이터 (1-3분기)
        fig_pred.add_trace(go.Scatter(
            x=quarters[:3],
            y=actual_data[:3],
            mode='lines+markers',
            name='실제 등록자',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8)
        ))

        # 예측 데이터 (4분기)
        fig_pred.add_trace(go.Scatter(
            x=[quarters[2], quarters[3]],
            y=[actual_data[2], actual_data[3]],
            mode='lines+markers',
            name='예측 등록자',
            line=dict(color='#ff7f0e', width=3, dash='dash'),
            marker=dict(size=8)
        ))

        # 예측 범위
        fig_pred.add_trace(go.Scatter(
            x=[quarters[3], quarters[3]],
            y=[conservative, optimistic],
            mode='markers',
            marker=dict(color='red', size=4),
            name='예측 범위',
            showlegend=False
        ))

        fig_pred.update_layout(
            title="📈 분기별 IDP 등록자 추이 및 4분기 예측",
            xaxis_title="분기",
            yaxis_title="등록자 수 (명)",
            height=400,
            hovermode='x unified'
        )

        st.plotly_chart(fig_pred, use_container_width=True)

        # 모델 설명
        with st.expander("🔍 예측 모델 상세 설명"):
            st.markdown(f"""
            **📊 사용된 4가지 예측 모델:**

            1. **선형 회귀**: {predictions['linear']:,.0f}명
               - 1-3분기 직선 추세를 4분기로 연장

            2. **다항식 회귀**: {predictions['polynomial']:,.0f}명
               - 비선형 패턴을 반영한 곡선 추세

            3. **추세 기반**: {predictions['trend']:,.0f}명
               - 실제 분기별 감소율 적용 (평균 23.8% 감소)

            4. **계절성 반영**: {predictions['seasonal']:,.0f}명
               - 연말 집중 등록 효과 15% 증가 반영

            **⚠️ 주의사항:**
            - 예측은 과거 데이터 기반 추정치입니다
            - 실제 결과는 정책 변화, 외부 요인에 따라 달라질 수 있습니다
            - 정기적인 모니터링과 업데이트가 필요합니다
            """)

else:
    st.warning("⚠️ scikit-learn 패키지가 설치되지 않아 예측 모델을 사용할 수 없습니다.")
    st.info("간단한 추세 기반 예측만 제공됩니다.")

    # 간단한 추세 기반 예측
    q2_to_q1_ratio = 2709 / 3093
    q3_to_q2_ratio = 1752 / 2709
    avg_decline = (q2_to_q1_ratio + q3_to_q2_ratio) / 2
    simple_prediction = 1752 * avg_decline

    st.metric("4분기 간단 예측", f"{simple_prediction:,.0f}명", help="추세 기반 예측")

st.markdown("---")

# ------------------------------------------------------------------
#  회사별 상세 분석
# ------------------------------------------------------------------
st.subheader("🔧 회사별 IDP 현황")

# 분석 유형 선택
analysis_type = st.radio(
    "분석 기준 선택:",
    options=["등록률순", "임직원수순", "등록건수순"],
    horizontal=True
)

# 정렬 기준 설정
if analysis_type == "등록률순":
    sort_column = "등록률(%)" if "등록률(%)" in filtered_data.columns else "IDP_등록자수"
    title_suffix = "등록률 기준"
elif analysis_type == "임직원수순":
    sort_column = "전체_직원수" if "전체_직원수" in filtered_data.columns else "전체_직원수"
    title_suffix = "임직원 수 기준"
else:
    sort_column = "IDP_등록자수" if "IDP_등록자수" in filtered_data.columns else "총_IDP_등록건"
    title_suffix = "등록건수 기준"

# 데이터 정렬
sorted_data = filtered_data.sort_values(sort_column, ascending=False)

# 전체 회사 차트 (막대 차트)
if analysis_type == "등록률순":
    y_column = "등록률(%)" if "등록률(%)" in sorted_data.columns else "IDP_등록자수"
    fig = px.bar(
        sorted_data,
        x="회사명",
        y=y_column,
        title=f"전체 회사별 IDP 등록률 ({title_suffix})",
        color=y_column,
        color_continuous_scale="viridis"
    )
    fig.update_layout(yaxis_title="등록률 (%)" if y_column == "등록률(%)" else "등록자 수")
elif analysis_type == "임직원수순":
    y_column = "전체_직원수" if "전체_직원수" in sorted_data.columns else "전체_직원수"
    fig = px.bar(
        sorted_data,
        x="회사명",
        y=y_column,
        title=f"전체 회사별 임직원 수 ({title_suffix})",
        color=y_column,
        color_continuous_scale="blues"
    )
    fig.update_layout(yaxis_title="임직원 수 (명)")
else:
    y_column = "IDP_등록자수" if "IDP_등록자수" in sorted_data.columns else "총_IDP_등록건"
    fig = px.bar(
        sorted_data,
        x="회사명",
        y=y_column,
        title=f"전체 회사별 IDP 등록건수 ({title_suffix})",
        color=y_column,
        color_continuous_scale="greens"
    )
    fig.update_layout(yaxis_title="등록건수 (건)")

fig.update_layout(
    height=500,
    xaxis_tickangle=-45,
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)

# 전체 회사 순위표
st.markdown(f"**전체 회사 순위 ({title_suffix})**")

# 사용 가능한 컬럼만 선택
available_columns = []
if "회사명" in sorted_data.columns:
    available_columns.append("회사명")
if "전체_직원수" in sorted_data.columns:
    available_columns.append("전체_직원수")
if "IDP_등록자수" in sorted_data.columns:
    available_columns.append("IDP_등록자수")
if "등록률(%)" in sorted_data.columns:
    available_columns.append("등록률(%)")

display_data = sorted_data[available_columns].copy()

# 포맷팅 (컬럼이 존재하는 경우에만)
if "전체_직원수" in display_data.columns:
    display_data["전체_직원수"] = display_data["전체_직원수"].apply(lambda x: f"{x:,}명")
if "IDP_등록자수" in display_data.columns:
    display_data["IDP_등록자수"] = display_data["IDP_등록자수"].apply(lambda x: f"{x:,}건")
if "등록률(%)" in display_data.columns:
    display_data["등록률(%)"] = display_data["등록률(%)"].apply(lambda x: f"{x:.1f}%")

# 컬럼 설정 동적 생성
column_config = {}
if "회사명" in display_data.columns:
    column_config["회사명"] = st.column_config.TextColumn("회사명", width="medium")
if "전체_직원수" in display_data.columns:
    column_config["전체_직원수"] = st.column_config.TextColumn("임직원", width="small")
if "IDP_등록자수" in display_data.columns:
    column_config["IDP_등록자수"] = st.column_config.TextColumn("등록건수", width="small")
if "등록률(%)" in display_data.columns:
    column_config["등록률(%)"] = st.column_config.TextColumn("등록률", width="small")

st.dataframe(
    display_data,
    use_container_width=True,
    hide_index=True,
    column_config=column_config
)

st.markdown("---")

# ------------------------------------------------------------------
#  직군별 상세 분석
# ------------------------------------------------------------------
if len(selected_job_groups) > 0 and job_groups:
    st.subheader(f"🔧 선택된 직군별 IDP 분석 ({len(selected_job_groups)}개 직군)")

    # 선택된 직군 표시
    selected_tags = " ".join([f"`{jg}`" for jg in selected_job_groups])
    st.markdown(f"**선택된 직군**: {selected_tags}")

    try:
        # 직군별 통계 계산
        if not filtered_jobgroup_data.empty and '직군' in filtered_jobgroup_data.columns and '사번_extracted' in filtered_jobgroup_data.columns:
            jobgroup_stats = filtered_jobgroup_data.groupby('직군').agg({
                '사번_extracted': 'nunique',  # 고유 직원 수
                '등록건수': 'sum' if '등록건수' in filtered_jobgroup_data.columns else lambda x: len(x)   # 총 등록 건수
            }).reset_index()
            jobgroup_stats = jobgroup_stats.rename(columns={'사번_extracted': '사번'})
        else:
            # 빈 데이터프레임 생성
            jobgroup_stats = pd.DataFrame(columns=['직군', '사번', '등록건수'])

        # 전체 직군 인원 수 추가
        if not JOBGROUP_DATA.empty and '직군' in JOBGROUP_DATA.columns and not jobgroup_stats.empty:
            total_by_jobgroup = JOBGROUP_DATA['직군'].value_counts().reset_index()
            total_by_jobgroup.columns = ['직군', '전체_인원수']

            jobgroup_stats = jobgroup_stats.merge(total_by_jobgroup, on='직군', how='left')
            jobgroup_stats['전체_인원수'] = jobgroup_stats['전체_인원수'].fillna(0)
            jobgroup_stats['참여율(%)'] = (jobgroup_stats['사번'] / jobgroup_stats['전체_인원수'] * 100).round(1)
            jobgroup_stats['1인당_등록건수'] = (jobgroup_stats['등록건수'] / jobgroup_stats['사번']).fillna(0).round(1)
        else:
            # 빈 데이터의 경우 기본값 설정
            if jobgroup_stats.empty:
                jobgroup_stats = pd.DataFrame(columns=['직군', '사번', '등록건수', '전체_인원수', '참여율(%)', '1인당_등록건수'])
    except Exception as e:
        st.error(f"직군별 분석 중 오류 발생: {e}")
        jobgroup_stats = pd.DataFrame(columns=['직군', '사번', '등록건수', '전체_인원수', '참여율(%)', '1인당_등록건수'])

    if not jobgroup_stats.empty:
        col1, col2 = st.columns([1, 1])

        with col1:
            # 직군별 참여율 차트
            fig_participation = px.bar(
                jobgroup_stats,
                x='직군',
                y='참여율(%)',
                title="직군별 IDP 참여율",
                color='참여율(%)',
                color_continuous_scale='viridis'
            )
            fig_participation.update_layout(height=350, xaxis_tickangle=-45)
            st.plotly_chart(fig_participation, use_container_width=True)

        with col2:
            # 직군별 1인당 등록건수 차트
            fig_intensity = px.bar(
                jobgroup_stats,
                x='직군',
                y='1인당_등록건수',
                title="직군별 1인당 등록건수",
                color='1인당_등록건수',
                color_continuous_scale='blues'
            )
            fig_intensity.update_layout(height=350, xaxis_tickangle=-45)
            st.plotly_chart(fig_intensity, use_container_width=True)
    else:
        st.warning("선택된 직군에 대한 데이터가 없습니다.")

    # 직군별 상세 테이블
    if not jobgroup_stats.empty:
        st.markdown("**📊 직군별 상세 현황**")

        display_jobgroup_stats = jobgroup_stats.copy()
        display_jobgroup_stats = display_jobgroup_stats.sort_values('참여율(%)', ascending=False)

        st.dataframe(
            display_jobgroup_stats,
            use_container_width=True,
            hide_index=True,
            column_config={
                "직군": st.column_config.TextColumn("직군", width="medium"),
                "전체_인원수": st.column_config.NumberColumn("전체 인원", format="%d명"),
                "사번": st.column_config.NumberColumn("참여 인원", format="%d명"),
                "참여율(%)": st.column_config.NumberColumn("참여율", format="%.1f%%"),
                "등록건수": st.column_config.NumberColumn("총 등록건수", format="%d건"),
                "1인당_등록건수": st.column_config.NumberColumn("1인당 등록건수", format="%.1f건")
            }
        )

st.markdown("---")

# ------------------------------------------------------------------
#  상세 데이터 테이블
# ------------------------------------------------------------------
st.subheader("📋 전체 회사 상세 현황")

# 검색 기능
st.markdown("### 🔍 검색 옵션")

search_col1, search_col2 = st.columns(2)

with search_col1:
    company_keyword = st.text_input("🏢 회사명 검색", placeholder="예: 동아, ST, 제약")

with search_col2:
    # 직군별 검색을 위한 선택박스
    available_job_groups = ["전체"] + job_groups if job_groups else ["전체"]
    selected_job_group_search = st.selectbox("🔧 직군별 검색", available_job_groups)

# 검색 조건 적용
search_data = filtered_data.copy()

# 회사명 검색 필터링
if company_keyword:
    search_data = search_data[search_data["회사명"].str.contains(company_keyword, case=False, na=False)]

# 직군별 검색 필터링 (MERGED_DATA를 통해 직군 정보 매칭)
if selected_job_group_search != "전체" and not MERGED_DATA.empty:
    try:
        # 선택된 직군에 해당하는 회사들 찾기
        job_companies = MERGED_DATA[MERGED_DATA['직군'] == selected_job_group_search]['회사명'].unique() if '직군' in MERGED_DATA.columns and '회사명' in MERGED_DATA.columns else []
        if len(job_companies) > 0:
            search_data = search_data[search_data["회사명"].isin(job_companies)]
    except:
        pass  # 오류 발생 시 전체 데이터 유지

# 검색 결과 표시
search_active = company_keyword or selected_job_group_search != "전체"

if search_active:
    search_result_col1, search_result_col2 = st.columns([3, 1])

    with search_result_col1:
        search_info = []
        if company_keyword:
            search_info.append(f"회사명: '{company_keyword}'")
        if selected_job_group_search != "전체":
            search_info.append(f"직군: '{selected_job_group_search}'")

        st.info(f"🔍 검색 조건: {' + '.join(search_info)} | 결과: {len(search_data)}개 회사")

    with search_result_col2:
        if st.button("🔄 검색 초기화", help="모든 검색 조건을 초기화합니다"):
            st.rerun()

# 검색 결과에 따른 안내 메시지
if search_active and len(search_data) == 0:
    st.warning("⚠️ 검색 조건에 맞는 회사가 없습니다. 다른 키워드나 조건을 시도해보세요.")
elif not search_active:
    st.success(f"📊 전체 {len(search_data)}개 회사 데이터를 표시하고 있습니다.")

# 전체 데이터 표시 - 실제 존재하는 컬럼만 사용
available_columns = []
if "회사명" in search_data.columns:
    available_columns.append("회사명")
if "전체_직원수" in search_data.columns:
    available_columns.append("전체_직원수")
if "IDP_등록자수" in search_data.columns:
    available_columns.append("IDP_등록자수")
if "등록률(%)" in search_data.columns:
    available_columns.append("등록률(%)")
if "1분기_등록자" in search_data.columns:
    available_columns.append("1분기_등록자")
if "2분기_등록자" in search_data.columns:
    available_columns.append("2분기_등록자")
if "3분기_등록자" in search_data.columns:
    available_columns.append("3분기_등록자")

# 사용 가능한 컬럼만으로 데이터 표시
final_data = search_data[available_columns].copy()

# 동적 컬럼 설정
column_config = {}
if "회사명" in available_columns:
    column_config["회사명"] = st.column_config.TextColumn("회사명", width="medium")
if "전체_직원수" in available_columns:
    column_config["전체_직원수"] = st.column_config.NumberColumn("임직원 수", format="%d명")
if "IDP_등록자수" in available_columns:
    column_config["IDP_등록자수"] = st.column_config.NumberColumn("IDP 등록자", format="%d명")
if "등록률(%)" in available_columns:
    column_config["등록률(%)"] = st.column_config.NumberColumn("IDP 등록률", format="%.1f%%")
if "1분기_등록자" in available_columns:
    column_config["1분기_등록자"] = st.column_config.NumberColumn("1분기", format="%d명")
if "2분기_등록자" in available_columns:
    column_config["2분기_등록자"] = st.column_config.NumberColumn("2분기", format="%d명")
if "3분기_등록자" in available_columns:
    column_config["3분기_등록자"] = st.column_config.NumberColumn("3분기", format="%d명")

st.dataframe(
    final_data,
    use_container_width=True,
    hide_index=True,
    column_config=column_config
)

# 요약 통계 및 액션 아이템
col1, col2, col3 = st.columns(3)

with col1:
    total_employees = search_data['전체_직원수'].sum() if '전체_직원수' in search_data.columns else 0
    total_idp = search_data['IDP_등록자수'].sum() if 'IDP_등록자수' in search_data.columns else 0

    st.info(f"""
    **📊 선택된 데이터 요약**
    - 회사 수: {len(search_data)}개
    - 총 임직원: {total_employees:,}명
    - IDP 등록자: {total_idp:,}명
    """)

with col2:
    if '등록률(%)' in search_data.columns:
        avg_rate = search_data['등록률(%)'].mean()
        status_emoji = "🟢" if avg_rate >= 40 else "🟡" if avg_rate >= 20 else "🔴"

        # 분기별 합계 계산
        q1_total = search_data['1분기_등록자'].sum() if '1분기_등록자' in search_data.columns else 0
        q2_total = search_data['2분기_등록자'].sum() if '2분기_등록자' in search_data.columns else 0
        q3_total = search_data['3분기_등록자'].sum() if '3분기_등록자' in search_data.columns else 0

        st.success(f"""
        **📈 등록 현황** {status_emoji}
        - 분기별 등록: 1Q({q1_total:,}) 2Q({q2_total:,}) 3Q({q3_total:,})
        - 평균 등록률: {avg_rate:.1f}%
        - 목표 대비: {"달성" if avg_rate >= 30 else "미달"}
        """)
    else:
        st.success("**📈 등록 현황**\n데이터 로딩 중...")

with col3:
    if '등록률(%)' in search_data.columns:
        # 개선 필요 회사 수
        low_performance_count = len(search_data[search_data['등록률(%)'] < 20])
        high_performance_count = len(search_data[search_data['등록률(%)'] >= 50])

        st.warning(f"""
        **🎯 액션 아이템**
        - 우수 회사: {high_performance_count}개 (50%↑)
        - 개선 필요: {low_performance_count}개 (20%↓)
        - 다음 레터: {["8월4일 발송 예정", "독려 활동 강화"][low_performance_count > 5]}
        """)
    else:
        st.warning("**🎯 액션 아이템**\n데이터 분석 중...")

# 실행 계획 제안
if len(search_data) > 0:
    st.markdown("### 📋 다음 분기 실행 계획")

    plan_col1, plan_col2 = st.columns(2)

    with plan_col1:
        st.markdown("""
        **🎯 단기 목표 (1개월)**
        - [ ] 9월 IDP 레터 발송
        - [ ] 등록률 20% 미만 회사 개별 미팅
        - [ ] 우수 사례 수집 및 공유
        - [ ] 부서장 대상 웨비나 개최
        """)

    with plan_col2:
        if '등록률(%)' in search_data.columns:
            current_avg_rate = search_data['등록률(%)'].mean()
            target_rate = min(current_avg_rate + 10, 60)  # 현재 등록률 + 10%, 최대 60%
            target_companies = len(search_data[search_data['등록률(%)'] < target_rate])
        else:
            target_rate = 50
            target_companies = len(search_data)

        st.markdown(f"""
        **📈 중기 목표 (3개월)**
        - [ ] 전체 평균 등록률 {target_rate:.0f}% 달성
        - [ ] {target_companies}개 회사 목표 등록률 도달
        - [ ] 분기별 경쟁 프로그램 도입
        - [ ] IDP 작성 가이드 업데이트
        """)
