import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# 페이지 설정
st.set_page_config(
    page_title=" 동아 직군 IDP 대시보드",
    page_icon="👔",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("👔 동아 직군 IDP 대시보드")

# 대시보드 네비게이션
nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
with nav_col2:
    st.markdown("""
    <div style='text-align: center; padding: 10px; background-color: #f0f2f6; border-radius: 10px; margin-bottom: 20px;'>
        <h4>📊 대시보드 네비게이션</h4>
        <p style='margin: 5px 0;'>
            <a href="http://10.1.242.65:8503" target="_blank" style='color: #1f77b4; text-decoration: none; font-weight: bold;'>
                📢 8503: 동아IDP대시보드 (예측모델) ➜
            </a>
        </p>
        <p style='margin: 5px 0; color: #666; font-size: 14px;'>현재: 👔 8506 직군 IDP 대시보드</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

@st.cache_data(ttl=10)  # 10초 TTL로 캐시 갱신
def load_corrected_data():
    """정확한 CSV 파일 기반 데이터 로드"""

    try:
        # CSV 파일 로드
        idp_file = "「반출」IDP 신청현황 누적 수립율(중복존재)_0709_최신 수립현황_회사명바꾸기_부서나누기.csv"
        employee_file = "「반출」IDP 신청현황 누적 수립율(중복존재)_0709_인원최신화_6월_임원지우기_회사이름바꿔.csv"

        idp_data = pd.read_csv(idp_file, encoding='utf-8-sig')
        employee_data = pd.read_csv(employee_file, encoding='utf-8-sig')

        # IDP 수립자 고유 사번별 정리
        idp_unique = idp_data.groupby('사번').agg({
            '이름': 'first',
            '회사': 'first',
            '부서': 'first',
            '등록건수': 'sum'
        }).reset_index()

        idp_unique['IDP수립여부'] = idp_unique['등록건수'] > 0
        idp_with_idp = idp_unique[idp_unique['IDP수립여부'] == True]

        # 사번으로 직군 매칭
        merged = pd.merge(
            idp_with_idp,
            employee_data[['사번', '직군']],
            on='사번',
            how='left'
        )

        # 매칭 결과
        matched_count = merged['직군'].notna().sum()
        unmatched_count = merged['직군'].isna().sum()

        # 전체 직원 대비 직군별 IDP 수립률 계산
        full_merged = pd.merge(
            employee_data[['사번', '직군', '회사']],
            idp_with_idp[['사번', 'IDP수립여부']],
            on='사번',
            how='left'
        )
        full_merged['IDP수립여부'] = full_merged['IDP수립여부'].fillna(False)

        # 직군별 통계
        jobgroup_stats = full_merged.groupby('직군').agg({
            '사번': 'count',
            'IDP수립여부': 'sum'
        }).reset_index()
        jobgroup_stats.columns = ['직군', '전체인원', 'IDP수립인원']
        jobgroup_stats['수립률(%)'] = (jobgroup_stats['IDP수립인원'] / jobgroup_stats['전체인원'] * 100).round(1)
        jobgroup_stats = jobgroup_stats.sort_values('수립률(%)', ascending=False)

        # 회사별 통계
        company_stats = full_merged.groupby('회사').agg({
            '사번': 'count',
            'IDP수립여부': 'sum'
        }).reset_index()
        company_stats.columns = ['회사명', '전체_직원수', 'IDP_등록자수']
        company_stats['등록률(%)'] = (company_stats['IDP_등록자수'] / company_stats['전체_직원수'] * 100).round(1)
        company_stats = company_stats.sort_values('등록률(%)', ascending=False)

        # 회사별-직군별 교차 통계 생성
        company_jobgroup_stats = full_merged.groupby(['회사', '직군']).agg({
            '사번': 'count',
            'IDP수립여부': 'sum'
        }).reset_index()
        company_jobgroup_stats.columns = ['회사명', '직군', '전체_인원', 'IDP_수립자']
        company_jobgroup_stats['수립률(%)'] = (company_jobgroup_stats['IDP_수립자'] / company_jobgroup_stats['전체_인원'] * 100).round(1)

        return {
            'jobgroup_stats': jobgroup_stats,
            'company_stats': company_stats,
            'company_jobgroup_stats': company_jobgroup_stats,
            'matched_count': matched_count,
            'unmatched_count': unmatched_count,
            'total_employees': len(employee_data),
            'total_idp_employees': len(idp_with_idp),
            'idp_data': merged
        }

    except FileNotFoundError:
        return None  # Pass silently, handled in the main script body
    except Exception as e:
        st.error(f"데이터 처리 중 오류 발생: {e}")
        return None

# 데이터 로드
data = load_corrected_data()

if data is None:
    st.warning("""
    **⚠️ 데이터 파일을 찾을 수 없습니다.**

    대시보드가 정상적으로 작동하려면 원본 데이터 파일이 필요합니다.
    `streamlit_app_job_group.py`와 동일한 경로에 다음 두 개의 CSV 파일이 있는지 확인해주세요:
    - `「반출」IDP 신청현황 누적 수립율(중복존재)_0709_최신 수립현황_회사명바꾸기_부서나누기.csv`
    - `「반출」IDP 신청현황 누적 수립율(중복존재)_0709_인원최신화_6월_임원지우기_회사이름바꿔.csv`
    """)
    st.stop()

# 전체 현황 표시
st.header("📊 전체 IDP 수립 현황")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("그룹사 임직원 수", f"{data['total_employees']:,}명")

with col2:
    st.metric("IDP 수립건수", f"{data['total_idp_employees']:,}명")

with col3:
    overall_rate = (data['total_idp_employees'] / data['total_employees'] * 100)
    st.metric("전체 수립률", f"{overall_rate:.1f}%")

with col4:
    st.metric("매칭 성공", f"{data['matched_count']:,}명")

with col5:
    st.metric("매칭 불가 인원", f"{data['unmatched_count']}명",
              help="직원 마스터 데이터에 없는 사번으로 인한 매칭 실패")

st.markdown("---")

# 사이드바 네비게이션
st.sidebar.markdown("---")
st.sidebar.markdown("### 🚀 대시보드 바로가기")
st.sidebar.markdown("""
<div style='background-color: #f8f9fa; padding: 10px; border-radius: 8px; margin-bottom: 15px;'>
    <p style='margin: 0; font-size: 12px; color: #6c757d;'>현재: 👔 8506 직군 IDP</p>
    <a href="http://10.1.242.65:8503" target="_blank" style='color: #007bff; text-decoration: none; font-size: 14px;'>
        📢 8503: 동아IDP대시보드 ➜
    </a>
</div>
""", unsafe_allow_html=True)

# 사이드바 필터
st.sidebar.header("🔍 필터 옵션")

# 회사 필터
companies = ['전체'] + data['company_stats']['회사명'].tolist()
selected_company = st.sidebar.selectbox("회사 선택", companies)

# 직군 필터
job_groups = data['jobgroup_stats']['직군'].tolist()
selected_job_groups = st.sidebar.multiselect("직군 선택", job_groups, default=[])

# 수립률 필터
rate_filter = st.sidebar.selectbox("수립률 필터", ['전체', '70% 이상', '50% 이상', '50% 미만', '30% 미만'])

# 직군별 요약 표시
st.sidebar.markdown("---")
st.sidebar.subheader("📊 전체 직군 현황")

for _, row in data['jobgroup_stats'].iterrows():
    jobgroup = row['직군']
    total_count = row['전체인원']
    idp_count = row['IDP수립인원']
    rate = row['수립률(%)']

    is_selected = jobgroup in selected_job_groups
    icon = "🔹" if is_selected else "▫️"

    st.sidebar.markdown(f"{icon} **{jobgroup}**: {rate:.1f}% ({idp_count:,}/{total_count:,}명)")

# 메인 컨텐츠
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏢 회사별 IDP 수립률")

    # 필터링된 데이터
    if selected_company != "전체":
        filtered_company_data = data['company_stats'][data['company_stats']['회사명'] == selected_company]
    else:
        filtered_company_data = data['company_stats'].copy()

    if not filtered_company_data.empty:
        fig_company = px.bar(
            filtered_company_data.head(13),
            x='회사명',
            y='등록률(%)',
            title="회사별 IDP 수립률",
            color='등록률(%)',
            color_continuous_scale='RdYlBu_r'
        )
        fig_company.update_layout(xaxis_tickangle=-45, height=400)
        st.plotly_chart(fig_company, use_container_width=True)

with col2:
    st.subheader("👔 직군별 IDP 수립률")

    # 필터링된 데이터
    if selected_job_groups:
        filtered_jobgroup_data = data['jobgroup_stats'][data['jobgroup_stats']['직군'].isin(selected_job_groups)]
    else:
        filtered_jobgroup_data = data['jobgroup_stats'].copy()

    if not filtered_jobgroup_data.empty:
        fig_jobgroup = px.bar(
            filtered_jobgroup_data,
            x='직군',
            y='수립률(%)',
            title="직군별 IDP 수립률 (전체)",
            color='수립률(%)',
            color_continuous_scale='viridis'
        )
        fig_jobgroup.update_layout(xaxis_tickangle=-45, height=400)
        st.plotly_chart(fig_jobgroup, use_container_width=True)

st.markdown("---")

# 상세 데이터 현황 섹션
st.header("📋 상세 데이터 현황")

# 필터링된 데이터 준비
filtered_company_data = data['company_stats'].copy()
filtered_jobgroup_data = data['jobgroup_stats'].copy()
company_jobgroup_stats = data.get('company_jobgroup_stats', pd.DataFrame())

# 필터 적용 로직 개선
filtered_company_data = data['company_stats'].copy()
filtered_jobgroup_data = data['jobgroup_stats'].copy()
filtered_combined_data = data.get('company_jobgroup_stats', pd.DataFrame())

# 회사 필터
if selected_company != '전체':
    filtered_company_data = filtered_company_data[filtered_company_data['회사명'] == selected_company]
    if not filtered_combined_data.empty:
        filtered_combined_data = filtered_combined_data[filtered_combined_data['회사명'] == selected_company]

# 직군 필터
companies_with_selected_jobgroup = None
if selected_job_groups:
    filtered_jobgroup_data = filtered_jobgroup_data[filtered_jobgroup_data['직군'].isin(selected_job_groups)]
    if not filtered_combined_data.empty:
        companies_with_selected_jobgroup = filtered_combined_data[
            filtered_combined_data['직군'].isin(selected_job_groups)
        ]['회사명'].unique()
        filtered_company_data = filtered_company_data[filtered_company_data['회사명'].isin(companies_with_selected_jobgroup)]
        filtered_combined_data = filtered_combined_data[filtered_combined_data['직군'].isin(selected_job_groups)]

# 수립률 필터
rate_map = {
    '70% 이상': (lambda df, col: df[col] >= 70),
    '50% 이상': (lambda df, col: df[col] >= 50),
    '50% 미만': (lambda df, col: df[col] < 50),
    '30% 미만': (lambda df, col: df[col] < 30),
}
if rate_filter in rate_map:
    condition = rate_map[rate_filter]
    filtered_company_data = condition(filtered_company_data, '등록률(%)')
    filtered_jobgroup_data = condition(filtered_jobgroup_data, '수립률(%)')
    if not filtered_combined_data.empty:
        filtered_combined_data = condition(filtered_combined_data, '수립률(%)')

# 필터 상태 정보 표시
filter_info = []
if selected_company != '전체':
    filter_info.append(f"회사: {selected_company}")
if selected_job_groups:
    filter_info.append(f"직군: {', '.join(selected_job_groups)}")
if rate_filter != '전체':
    filter_info.append(f"수립률: {rate_filter}")

if filter_info:
    st.info(f"🔍 적용된 필터: {' | '.join(filter_info)}")
else:
    st.success("📊 전체 데이터를 표시하고 있습니다.")

# 상세 데이터 테이블
detail_col1, detail_col2 = st.columns(2)

with detail_col1:
    st.subheader("🏢 회사별 상세 현황")

    if not filtered_company_data.empty:
        display_company_data = filtered_company_data.copy()
        display_company_data = display_company_data.rename(columns={
            '회사명': '회사명',
            '전체_직원수': '전체 직원수',
            'IDP_등록자수': 'IDP 수립자',
            '등록률(%)': '수립률(%)'
        })

        st.dataframe(display_company_data, use_container_width=True, hide_index=True,
                    column_config={
                        "전체 직원수": st.column_config.NumberColumn("전체 직원수", format="%d명"),
                        "IDP 수립자": st.column_config.NumberColumn("IDP 수립자", format="%d명"),
                        "수립률(%)": st.column_config.NumberColumn("수립률(%)", format="%.1f%%")
                    })

        # 회사별 요약 통계
        if len(filtered_company_data) > 0:
            total_employees = filtered_company_data['전체_직원수'].sum()
            total_idp = filtered_company_data['IDP_등록자수'].sum()
            avg_rate = (total_idp / total_employees * 100) if total_employees > 0 else 0

            st.info(f"""
            **📊 필터링된 회사 요약**
            - 회사 수: {len(filtered_company_data)}개
            - 총 직원수: {total_employees:,}명
            - 총 IDP 수립자: {total_idp:,}명
            - 평균 수립률: {avg_rate:.1f}%
            """)
    else:
        st.warning("필터 조건에 맞는 회사가 없습니다.")

with detail_col2:
    st.subheader("👔 직군별 상세 현황")

    # 회사 필터가 적용된 경우 (직군이 전체이든 특정이든) 결합 데이터 표시
    if selected_company != '전체':
        if selected_job_groups:
            st.info(f"🔍 **필터 적용**: {selected_company} 회사의 {', '.join(selected_job_groups)} 직군")
        else:
            st.info(f"🔍 **필터 적용**: {selected_company} 회사의 모든 직군")

        if not filtered_combined_data.empty:
            display_combined_data = filtered_combined_data.copy()
            display_combined_data = display_combined_data.rename(columns={
                '회사명': '회사명',
                '직군': '직군',
                '전체_인원': '전체 인원',
                'IDP_수립자': 'IDP 수립자',
                '수립률(%)': '수립률(%)'
            })

            st.dataframe(display_combined_data, use_container_width=True, hide_index=True,
                        column_config={
                            "전체 인원": st.column_config.NumberColumn("전체 인원", format="%d명"),
                            "IDP 수립자": st.column_config.NumberColumn("IDP 수립자", format="%d명"),
                            "수립률(%)": st.column_config.NumberColumn("수립률(%)", format="%.1f%%")
                        })

            # 결합 데이터 요약 통계
            if len(filtered_combined_data) > 0:
                total_employees = filtered_combined_data['전체_인원'].sum()
                total_idp = filtered_combined_data['IDP_수립자'].sum()
                avg_rate = (total_idp / total_employees * 100) if total_employees > 0 else 0

                if selected_job_groups:
                    st.success(f"""
                    **🎯 {selected_company} - {', '.join(selected_job_groups)} 상세 현황**
                    - 매칭 건수: {len(filtered_combined_data)}건
                    - 총 직원수: {total_employees:,}명
                    - 총 IDP 수립자: {total_idp:,}명
                    - 수립률: {avg_rate:.1f}%
                    """)
                else:
                    st.success(f"""
                    **🎯 {selected_company} 회사 전체 직군 현황**
                    - 직군 수: {len(filtered_combined_data)}개
                    - 총 직원수: {total_employees:,}명
                    - 총 IDP 수립자: {total_idp:,}명
                    - 평균 수립률: {avg_rate:.1f}%
                    """)
        else:
            filter_condition = f"{selected_company} - {', '.join(selected_job_groups)}" if selected_job_groups else f"{selected_company} 회사"
            st.warning(f"선택한 조건 ({filter_condition})에 맞는 데이터가 없습니다.")

    # 회사 필터가 전체인 경우에만 기존 직군별 데이터 표시
    else:
        if not filtered_jobgroup_data.empty:
            display_jobgroup_data = filtered_jobgroup_data.copy()
            display_jobgroup_data = display_jobgroup_data.rename(columns={
                '직군': '직군',
                '전체인원': '전체 인원',
                'IDP수립인원': 'IDP 수립자',
                '수립률(%)': '수립률(%)'
            })

            st.dataframe(display_jobgroup_data, use_container_width=True, hide_index=True,
                        column_config={
                            "전체 인원": st.column_config.NumberColumn("전체 인원", format="%d명"),
                            "IDP 수립자": st.column_config.NumberColumn("IDP 수립자", format="%d명"),
                            "수립률(%)": st.column_config.NumberColumn("수립률(%)", format="%.1f%%")
                        })

            # 직군별 요약 통계
            if len(filtered_jobgroup_data) > 0:
                total_employees = filtered_jobgroup_data['전체인원'].sum()
                total_idp = filtered_jobgroup_data['IDP수립인원'].sum()
                avg_rate = (total_idp / total_employees * 100) if total_employees > 0 else 0

                st.info(f"""
                **📊 필터링된 직군 요약**
                - 직군 수: {len(filtered_jobgroup_data)}개
                - 총 직원수: {total_employees:,}명
                - 총 IDP 수립자: {total_idp:,}명
                - 평균 수립률: {avg_rate:.1f}%
                """)
        else:
            st.warning("필터 조건에 맞는 직군이 없습니다.")

# 심화 인사이트 섹션
st.markdown("---")
st.header("🎯 심화 분석 및 전략적 인사이트")
with st.expander("내용 보기/숨기기", expanded=False):
    # 데이터 분석을 위한 추가 계산
    total_rate = (data['total_idp_employees'] / data['total_employees'] * 100)
    high_performers = data['company_stats'][data['company_stats']['등록률(%)'] >= 70]
    mid_performers = data['company_stats'][(data['company_stats']['등록률(%)'] >= 50) & (data['company_stats']['등록률(%)'] < 70)]
    low_performers = data['company_stats'][data['company_stats']['등록률(%)'] < 50]

    high_jobgroups = data['jobgroup_stats'][data['jobgroup_stats']['수립률(%)'] >= 70]
    mid_jobgroups = data['jobgroup_stats'][(data['jobgroup_stats']['수립률(%)'] >= 50) & (data['jobgroup_stats']['수립률(%)'] < 70)]
    low_jobgroups = data['jobgroup_stats'][data['jobgroup_stats']['수립률(%)'] < 50]

    # 최고/최저 회사 및 직군
    top_company = data['company_stats'].iloc[0]
    bottom_company = data['company_stats'].iloc[-1]
    top_jobgroup = data['jobgroup_stats'].iloc[0]
    bottom_jobgroup = data['jobgroup_stats'].iloc[-1]

    # 탭으로 구성
    insight_tab1, insight_tab2, insight_tab3, insight_tab4 = st.tabs([
        "📊 종합 현황 분석", "🏢 회사별 심화 분석", "👔 직군별 심화 분석", "🎯 전략적 개선 방안"
    ])

    with insight_tab1:
        st.subheader("📈 전체 IDP 수립 현황 종합 분석")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("전체 수립률", f"{total_rate:.1f}%",
                    help="동아그룹 전체 IDP 수립률")

            # 성과 분포
            st.markdown("**📊 성과 분포**")
            st.markdown(f"""
            - 🟢 우수 (70% 이상): {len(high_performers)}개 회사
            - 🟡 보통 (50-70%): {len(mid_performers)}개 회사
            - 🔴 개선 필요 (<50%): {len(low_performers)}개 회사
            """)

        with col2:
            # 직군 성과 분포
            st.markdown("**👔 직군별 성과 분포**")
            st.markdown(f"""
            - 🟢 우수 (70% 이상): {len(high_jobgroups)}개 직군
            - 🟡 보통 (50-70%): {len(mid_jobgroups)}개 직군
            - 🔴 개선 필요 (<50%): {len(low_jobgroups)}개 직군
            """)

            # 데이터 품질 지표
            data_quality = (data['matched_count']/(data['matched_count']+data['unmatched_count'])*100)
            st.metric("데이터 매칭률", f"{data_quality:.1f}%",
                    help=f"매칭 불가 {data['unmatched_count']}명")

        with col3:
            # 핵심 지표
            st.markdown("**🎯 핵심 성과 지표**")

            # 상위 3개 회사 평균
            top3_companies = data['company_stats'].head(3)
            top3_avg = top3_companies['등록률(%)'].mean()

            # 하위 3개 회사 평균
            bottom3_companies = data['company_stats'].tail(3)
            bottom3_avg = bottom3_companies['등록률(%)'].mean()

            st.markdown(f"""
            - 상위 3개사 평균: **{top3_avg:.1f}%**
            - 하위 3개사 평균: **{bottom3_avg:.1f}%**
            - 성과 격차: **{top3_avg - bottom3_avg:.1f}%p**
            """)

    with insight_tab2:
        st.subheader("🏢 회사별 심화 분석")

        analysis_col1, analysis_col2 = st.columns(2)

        with analysis_col1:
            st.markdown("### 🏆 우수 성과 회사")

            if not high_performers.empty:
                for _, company in high_performers.iterrows():
                    total_employees = company['전체_직원수']
                    idp_employees = company['IDP_등록자수']
                    rate = company['등록률(%)']

                    # 규모별 분류
                    if total_employees >= 1000:
                        scale = "대규모"
                    elif total_employees >= 500:
                        scale = "중규모"
                    else:
                        scale = "소규모"

                    st.success(f"""
                    **{company['회사명']}** ({scale})
                    - 수립률: **{rate:.1f}%**
                    - 수립인원: {idp_employees:,}명 / {total_employees:,}명
                    - 우수 요인: {'전사적 참여 문화' if rate >= 80 else '적극적 독려 활동'}
                    """)
            else:
                st.info("70% 이상 수립률을 달성한 회사가 없습니다.")

        with analysis_col2:
            st.markdown("### ⚠️ 개선 필요 회사")

            if not low_performers.empty:
                for _, company in low_performers.iterrows():
                    total_employees = company['전체_직원수']
                    idp_employees = company['IDP_등록자수']
                    rate = company['등록률(%)']

                    improvement_potential = total_employees - idp_employees

                    st.error(f"""
                    **{company['회사명']}**
                    - 현재 수립률: **{rate:.1f}%**
                    - 개선 잠재력: {improvement_potential:,}명
                    - 우선 조치: {'긴급 개입 필요' if rate < 30 else '집중 관리 필요'}
                    """)

            # 개선 로드맵
            st.markdown("### 📈 단계별 개선 로드맵")
            st.markdown("""
            **1단계 (1개월)**: 30% 미만 회사 집중 지원
            - 경영진 면담 및 중요성 공유
            - 전담 담당자 지정

            **2단계 (3개월)**: 50% 목표 달성
            - 직군별 맞춤 교육 실시
            - 월별 진도 점검

            **3단계 (6개월)**: 70% 목표 달성
            - 우수 사례 벤치마킹
            - 인센티브 제도 도입
            """)

    with insight_tab3:
        st.subheader("👔 직군별 심화 분석")

        job_col1, job_col2 = st.columns(2)

        with job_col1:
            st.markdown("### 📈 직군별 성과 특성")

            for _, jobgroup in data['jobgroup_stats'].iterrows():
                job_name = jobgroup['직군']
                rate = jobgroup['수립률(%)']
                total = jobgroup['전체인원']
                idp_count = jobgroup['IDP수립인원']

                # 성과에 따른 아이콘 및 분석
                if rate >= 70:
                    icon = "🟢"
                    status = "우수"
                    analysis = "지속적 우수 성과 유지 필요"
                elif rate >= 50:
                    icon = "🟡"
                    status = "보통"
                    analysis = "추가 독려로 70% 달성 가능"
                else:
                    icon = "🔴"
                    status = "개선필요"
                    analysis = "집중적 개입 및 맞춤 지원 필요"

                st.markdown(f"""
                {icon} **{job_name}** ({status})
                - 수립률: **{rate:.1f}%** ({idp_count}/{total}명)
                - 분석: {analysis}
                """)

        with job_col2:
            st.markdown("### 🎯 직군별 맞춤 전략")

            # 우수 직군 전략
            if not high_jobgroups.empty:
                st.success("**🏆 우수 직군 관리 전략**")
                for _, job in high_jobgroups.head(2).iterrows():
                    st.markdown(f"""
                    **{job['직군']}** ({job['수립률(%)']:.1f}%)
                    - 우수 사례 전파 역할 부여
                    - 멘토링 프로그램 리더 활용
                    - 지속적 동기부여 방안 필요
                    """)

            # 개선 필요 직군 전략
            if not low_jobgroups.empty:
                st.warning("**⚠️ 개선 필요 직군 전략**")
                for _, job in low_jobgroups.iterrows():
                    st.markdown(f"""
                    **{job['직군']}** ({job['수립률(%)']:.1f}%)
                    - 직군 특성 분석 후 맞춤 프로그램
                    - 단계별 목표 설정 (월 10%씩 향상)
                    - 전담 지원팀 배정 필요
                    """)

    with insight_tab4:
        st.subheader("🎯 전략적 개선 방안")

        strategy_col1, strategy_col2 = st.columns(2)

        with strategy_col1:
            st.markdown("### 🚀 단기 실행 계획 (1-3개월)")

            # 우선순위 계산
            urgent_companies = low_performers.nlargest(3, '전체_직원수')
            urgent_jobgroups = low_jobgroups.nsmallest(3, '수립률(%)')

            st.markdown("**🎯 최우선 대상**")
            st.markdown("**회사별:**")
            for _, company in urgent_companies.iterrows():
                potential = company['전체_직원수'] - company['IDP_등록자수']
                st.markdown(f"- {company['회사명']}: {potential:,}명 확대 가능")

            st.markdown("**직군별:**")
            for _, job in urgent_jobgroups.iterrows():
                st.markdown(f"- {job['직군']}: {job['수립률(%)']:.1f}% → 50% 목표")

            st.markdown("""
            **📋 실행 액션**
            1. **위기 회사 집중 관리**
            - 주간 진도 점검 회의
            - CEO 직접 독려 메시지
            - 전담 지원팀 파견

            2. **직군별 맞춤 지원**
            - 직군 특성 맞춤 교육 콘텐츠
            - 동료 멘토링 프로그램
            - 성공 사례 공유 세션
            """)

        with strategy_col2:
            st.markdown("### 📈 중장기 발전 계획 (3-12개월)")

            # 목표 설정
            target_rate = 75
            current_total = data['total_idp_employees']
            target_total = int(data['total_employees'] * target_rate / 100)
            gap = target_total - current_total

            st.info(f"""
            **🎯 목표 설정**
            - 현재: {total_rate:.1f}% ({current_total:,}명)
            - 목표: {target_rate}% ({target_total:,}명)
            - 격차: {gap:,}명 추가 수립 필요
            """)

            st.markdown("""
            **🏗️ 시스템 구축**
            1. **데이터 기반 관리 체계**
            - 실시간 대시보드 구축
            - 주간/월간 자동 리포트
            - 예측 분석 도입

            2. **조직 문화 혁신**
            - IDP 수립 KPI 반영
            - 우수 조직 포상 제도
            - 지속적 개선 문화 정착

            3. **교육 시스템 고도화**
            - AI 기반 맞춤형 추천
            - 모바일 접근성 강화
            - 글로벌 베스트 프랙티스 도입
            """)

            # ROI 분석
            st.markdown("### 💰 투자 효과 예상")
            estimated_productivity = gap * 50000  # 1인당 연간 5만원 생산성 향상 가정
            st.success(f"""
            **예상 효과 (연간)**
            - 생산성 향상: {estimated_productivity:,}원
            - 직원 만족도 증가: 15-20%
            - 이직률 감소: 5-10%
            - 조직 역량 강화: 정성적 효과
            """)

# 추가 인사이트 - 데이터 기반 권고사항
st.markdown("---")
st.header("📊 데이터 기반 핵심 권고사항")

with st.expander("내용 보기/숨기기", expanded=False):
    recommendation_col1, recommendation_col2, recommendation_col3 = st.columns(3)

    with recommendation_col1:
        st.markdown("### 🔥 긴급 조치 필요")
        critical_rate = 30
        critical_companies = data['company_stats'][data['company_stats']['등록률(%)'] < critical_rate]
        critical_jobgroups = data['jobgroup_stats'][data['jobgroup_stats']['수립률(%)'] < critical_rate]

        if not critical_companies.empty:
            st.error(f"**위험 회사 ({len(critical_companies)}개)**")
            for _, company in critical_companies.iterrows():
                st.markdown(f"- {company['회사명']}: {company['등록률(%)']:.1f}%")

        if not critical_jobgroups.empty:
            st.error(f"**위험 직군 ({len(critical_jobgroups)}개)**")
            for _, job in critical_jobgroups.iterrows():
                st.markdown(f"- {job['직군']}: {job['수립률(%)']:.1f}%")

    with recommendation_col2:
        st.markdown("### 🎯 집중 투자 영역")

        # 큰 규모 + 낮은 성과 = 높은 임팩트
        high_impact = data['company_stats'][
            (data['company_stats']['전체_직원수'] >= 500) &
            (data['company_stats']['등록률(%)'] < 60)
        ]

        st.warning(f"**고임팩트 회사 ({len(high_impact)}개)**")
        for _, company in high_impact.iterrows():
            potential = company['전체_직원수'] - company['IDP_등록자수']
            st.markdown(f"- {company['회사명']}: {potential:,}명 확대 가능")

    with recommendation_col3:
        st.markdown("### 🏆 벤치마킹 대상")

        # 우수 성과 조직
        benchmarks = data['company_stats'][data['company_stats']['등록률(%)'] >= 70]

        if not benchmarks.empty:
            st.success(f"**모범 사례 ({len(benchmarks)}개)**")
            for _, company in benchmarks.iterrows():
                st.markdown(f"- {company['회사명']}: {company['등록률(%)']:.1f}%")

        # 우수 직군
        benchmark_jobs = data['jobgroup_stats'][data['jobgroup_stats']['수립률(%)'] >= 80]
        if not benchmark_jobs.empty:
            st.success(f"**우수 직군 ({len(benchmark_jobs)}개)**")
            for _, job in benchmark_jobs.iterrows():
                st.markdown(f"- {job['직군']}: {job['수립률(%)']:.1f}%")

st.markdown("---")
st.markdown("*📊 데이터 기준: 실제 CSV 파일 분석 결과*")
