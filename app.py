import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 페이지 설정
st.set_page_config(
    page_title="학습자 개발 리포트 예시",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일링
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 30px;
    }
    .section-header {
        background-color: #1f77b4;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        margin: 20px 0 10px 0;
    }
    .metric-card {
        background: white;
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    .info-box {
        background-color: #f8f9fa;
        border-left: 4px solid #1f77b4;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .warning-box {
        background-color: #fff5f5;
        border-left: 4px solid #ff6b6b;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .success-box {
        background-color: #f0fff0;
        border-left: 4px solid #2ca02c;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .demo-section {
        background-color: #f0f8ff;
        border: 2px solid #1f77b4;
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

def create_demo_data():
    """데모용 가상 데이터 생성"""

    # 월별 학습 활동 데이터
    months = ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월']
    learning_activities = [3, 5, 2, 7, 4, 8, 6, 9, 5, 7, 4, 6]

    # 학습 유형별 데이터
    learning_types = ['온라인 교육', '오프라인 교육', '멘토링', '자기학습', '프로젝트']
    learning_values = [35, 25, 20, 15, 5]

    # 분기별 트렌드 데이터
    quarters = ['1분기', '2분기', '3분기', '4분기']
    trend_values = [15, 22, 18, 25]

    return {
        'months': months,
        'learning_activities': learning_activities,
        'learning_types': learning_types,
        'learning_values': learning_values,
        'quarters': quarters,
        'trend_values': trend_values
    }

def create_learning_activity_chart():
    """학습 활동 시각화 차트 생성"""

    demo_data = create_demo_data()

    # 서브플롯 생성 (2x2 레이아웃)
    fig = go.Figure()

    # 1. 월별 학습 활동 바 차트
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        x=demo_data['months'],
        y=demo_data['learning_activities'],
        name='학습 활동',
        marker_color='#1f77b4',
        text=demo_data['learning_activities'],
        textposition='auto'
    ))
    fig1.update_layout(
        title="📅 월별 학습 활동 현황",
        xaxis_title="월",
        yaxis_title="학습 활동 수",
        height=300
    )

    # 2. 학습 유형별 파이 차트
    fig2 = go.Figure()
    fig2.add_trace(go.Pie(
        labels=demo_data['learning_types'],
        values=demo_data['learning_values'],
        name='학습 유형',
        marker_colors=['#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    ))
    fig2.update_layout(
        title="📊 학습 유형별 분포",
        height=300
    )

    # 3. 분기별 트렌드 라인 차트
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=demo_data['quarters'],
        y=demo_data['trend_values'],
        mode='lines+markers',
        name='분기별 트렌드',
        line=dict(color='#2ca02c', width=3),
        marker=dict(size=10)
    ))
    fig3.update_layout(
        title="📈 분기별 학습 트렌드",
        xaxis_title="분기",
        yaxis_title="활동 점수",
        height=300
    )

    # 4. 학습 목표 달성률 게이지 차트
    fig4 = go.Figure()
    fig4.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=75,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "목표 달성률 (%)"},
        delta={'reference': 80},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 80], 'color': "yellow"},
                {'range': [80, 100], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    fig4.update_layout(
        title="🎯 학습 목표 달성률",
        height=300
    )

    return fig1, fig2, fig3, fig4

def show_advanced_report():
    """고급 학습자 리포트 표시"""
    st.markdown('<div class="section-header">👤 개인 정보</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="metric-card">
            <h4>이름</h4>
            <h3>김성공</h3>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-card">
            <h4>사번</h4>
            <h3>2251234</h3>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-card">
            <h4>부서</h4>
            <h3>경영기획관리실 DT팀</h3>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="metric-card">
            <h4>회사</h4>
            <h3>동아ST</h3>
        </div>
        """, unsafe_allow_html=True)

    # 학습 활동 분석
    st.markdown('<div class="section-header">📈 학습 활동 분석</div>', unsafe_allow_html=True)

    fig1, fig2, fig3, fig4 = create_learning_activity_chart()

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(fig1, use_container_width=True)
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        st.plotly_chart(fig2, use_container_width=True)
        st.plotly_chart(fig4, use_container_width=True)

    # 개발 성과 평가 결과
    st.markdown('<div class="section-header">🎯 개발 성과 평가 결과</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="metric-card">
            <h4>종합 개발 점수</h4>
            <h2 style="color: #1f77b4;">125점</h2>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-card">
            <h4>역량 수준</h4>
            <h2 style="color: #ff7f0e;">고급</h2>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-card">
            <h4>개발 위험도</h4>
            <h2 style="color: green;">저위험</h2>
        </div>
        """, unsafe_allow_html=True)

    # 권고사항
    st.markdown('<div class="section-header">💡 검사결과에 따른 권고사항</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="demo-section">
        <h4>🎉 우수한 학습자입니다!</h4>
        <p>당신은 고급 수준의 학습자로, 5년 내 역량 개발 성공 확률은 <strong>90% 이상</strong>입니다.</p>
        <p>고급 학습자는 다음의 고급 역량 개발 프로그램을 권장합니다:</p>
        <ul>
            <li>리더십 개발 프로그램 참여</li>
            <li>멘토링 프로그램 운영</li>
            <li>전문 자격증 취득</li>
            <li>외부 컨퍼런스 참여</li>
        </ul>
        <p><strong>다음 권장 학습 활동: 6개월 후, 2025년 12월</strong></p>
    </div>
    """, unsafe_allow_html=True)

def show_intermediate_report():
    """중급 학습자 리포트 표시"""
    st.markdown('<div class="section-header">👤 개인 정보</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="metric-card">
            <h4>이름</h4>
            <h3>이안정</h3>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-card">
            <h4>사번</h4>
            <h3>2255678</h3>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-card">
            <h4>부서</h4>
            <h3>품질경영실</h3>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="metric-card">
            <h4>회사</h4>
            <h3>동아제약</h3>
        </div>
        """, unsafe_allow_html=True)

    # 학습 활동 분석
    st.markdown('<div class="section-header">📈 학습 활동 분석</div>', unsafe_allow_html=True)

    # 학습 활동 차트
    months = ['1월', '2월', '3월', '4월', '5월', '6월']
    activities = [5, 7, 6, 9, 8, 10]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=months, y=activities, mode='lines+markers',
                            line=dict(color='#ff7f0e', width=3),
                            marker=dict(size=8)))
    fig.update_layout(title="월별 학습 활동 추이",
                     xaxis_title="월", yaxis_title="학습 활동 수",
                     height=300)
    st.plotly_chart(fig, use_container_width=True)

    # 개발 성과 평가 결과
    st.markdown('<div class="section-header">🎯 개발 성과 평가 결과</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="metric-card">
            <h4>종합 개발 점수</h4>
            <h2 style="color: #1f77b4;">85점</h2>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-card">
            <h4>역량 수준</h4>
            <h2 style="color: #ff7f0e;">중급</h2>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-card">
            <h4>개발 위험도</h4>
            <h2 style="color: orange;">중위험</h2>
        </div>
        """, unsafe_allow_html=True)

    # 권고사항
    st.markdown('<div class="section-header">💡 검사결과에 따른 권고사항</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="demo-section">
        <h4>📚 안정적인 학습자입니다!</h4>
        <p>당신은 중급 수준의 학습자로, 5년 내 역량 개발 성공 확률은 <strong>70% 이상</strong>입니다.</p>
        <p>중급 학습자는 다음의 중급 역량 개발 프로그램을 권장합니다:</p>
        <ul>
            <li>전문 기술 교육 프로그램</li>
            <li>프로젝트 리더 경험</li>
            <li>업무 관련 자격증 취득</li>
            <li>팀 내 지식 공유 활동</li>
        </ul>
        <p><strong>다음 권장 학습 활동: 3개월 후, 2025년 9월</strong></p>
    </div>
    """, unsafe_allow_html=True)

def show_beginner_report():
    """초급 학습자 리포트 표시"""
    st.markdown('<div class="section-header">👤 개인 정보</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="metric-card">
            <h4>이름</h4>
            <h3>박개선</h3>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-card">
            <h4>사번</h4>
            <h3>2259999</h3>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-card">
            <h4>부서</h4>
            <h3>연구개발실</h3>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="metric-card">
            <h4>회사</h4>
            <h3>에스티팜</h3>
        </div>
        """, unsafe_allow_html=True)

    # 학습 활동 분석
    st.markdown('<div class="section-header">📈 학습 활동 분석</div>', unsafe_allow_html=True)

    # 학습 활동 차트
    months = ['1월', '2월', '3월', '4월', '5월', '6월']
    activities = [2, 3, 4, 5, 6, 7]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=months, y=activities, mode='lines+markers',
                            line=dict(color='#2ca02c', width=3),
                            marker=dict(size=8)))
    fig.update_layout(title="월별 학습 활동 추이",
                     xaxis_title="월", yaxis_title="학습 활동 수",
                     height=300)
    st.plotly_chart(fig, use_container_width=True)

    # 개발 성과 평가 결과
    st.markdown('<div class="section-header">🎯 개발 성과 평가 결과</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="metric-card">
            <h4>종합 개발 점수</h4>
            <h2 style="color: #1f77b4;">45점</h2>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-card">
            <h4>역량 수준</h4>
            <h2 style="color: #ff7f0e;">초급</h2>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-card">
            <h4>개발 위험도</h4>
            <h2 style="color: red;">고위험</h2>
        </div>
        """, unsafe_allow_html=True)

    # 권고사항
    st.markdown('<div class="section-header">💡 검사결과에 따른 권고사항</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="demo-section">
        <h4>⚠️ 학습 활동 개선이 필요합니다!</h4>
        <p>당신은 초급 수준의 학습자로, 5년 내 역량 개발 성공 확률은 <strong>40% 미만</strong>입니다.</p>
        <p>초급 학습자는 다음의 기초 역량 개발 프로그램을 권장합니다:</p>
        <ul>
            <li>기본 업무 스킬 교육</li>
            <li>온라인 학습 플랫폼 활용</li>
            <li>멘토링 프로그램 참여</li>
            <li>정기적인 학습 계획 수립</li>
        </ul>
        <p><strong>다음 권장 학습 활동: 1개월 후, 2025년 7월</strong></p>
    </div>
    """, unsafe_allow_html=True)

def show_missing_data_report():
    """교육 데이터 누락 리포트 표시"""
    st.markdown('<div class="section-header">⚠️ 교육 데이터 누락 안내</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="warning-box">
        <h4>⚠️ 교육 데이터 누락 안내</h4>
        <p><strong>현재 상황:</strong> 시스템에서 귀하의 교육 이수 데이터를 찾을 수 없습니다.</p>
        <p><strong>가능한 원인:</strong></p>
        <ul>
            <li>교육 이수 후 데이터 등록이 누락된 경우</li>
            <li>사번이 다르게 등록된 경우</li>
            <li>교육 프로그램이 시스템에 미등록된 경우</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="demo-section">
        <h5>📞 교육 담당자 연락처</h5>
        <p><strong>동아ST:</strong> 인재경영실 인재육성팀 (02-XXX-XXXX)</p>
        <p><strong>동아제약:</strong> 인재경영실 인재육성팀 (02-XXX-XXXX)</p>
        <p><strong>에스티팜:</strong> 인재경영실 인재경영팀 (02-XXX-XXXX)</p>
        <p><strong>기타 계열사:</strong> 각사 인재경영실</p>
        <p><strong>이메일:</strong> idp@donga.com</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
        <h5>📋 문의 시 준비사항</h5>
        <ul>
            <li>사번 및 소속 정보</li>
            <li>이수한 교육 프로그램명</li>
            <li>교육 이수 기간</li>
            <li>교육 시간 및 학점</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

def show_general_report():
    """일반 리포트 표시"""
    st.markdown('<div class="section-header">📊 일반 리포트</div>', unsafe_allow_html=True)

    # 설문 데이터 표시
    survey_data = st.session_state.get('survey_data', {})

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("<h4>📋 설문 응답 요약</h4>", unsafe_allow_html=True)

        # 기본 정보
        st.markdown(f"""
        <div class="info-box">
            <h5>👤 기본 정보</h5>
            <p>• 회사: {survey_data.get('company', 'N/A')}</p>
            <p>• 사번: {survey_data.get('employee_id', 'N/A')}</p>
            <p>• 학습 동기: {survey_data.get('learning_motivation', 'N/A')}</p>
        </div>
        """, unsafe_allow_html=True)

        # 학습 환경
        st.markdown(f"""
        <div class="info-box">
            <h5>⏰ 학습 환경</h5>
            <p>• 일일 학습 시간: {survey_data.get('daily_study_time', 'N/A')}</p>
            <p>• 선호 학습 방식: {survey_data.get('learning_preference', 'N/A')}</p>
            <p>• 주요 학습 자원: {', '.join(survey_data.get('learning_resources', []))}</p>
        </div>
        """, unsafe_allow_html=True)

        # 만족도
        st.markdown(f"""
        <div class="info-box">
            <h5>😊 학습 만족도</h5>
            <p>• 전반적 만족도: {st.session_state.get('learning_satisfaction', 'N/A')}/10점</p>
            <p>• 스킬 향상도: {st.session_state.get('skill_improvement', 'N/A')}/10점</p>
            <p>• 업무 적용도: {st.session_state.get('learning_application', 'N/A')}/10점</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("<h4>💡 개선 제안사항</h4>", unsafe_allow_html=True)

        # 만족도에 따른 권고사항
        satisfaction = survey_data.get('learning_satisfaction')
        if satisfaction and satisfaction >= 8:
            st.markdown("""
            <div class="success-box">
                <strong>🎉 우수한 학습 성과!</strong>
                <p>• 리더십 역할 확대 고려</p>
                <p>• 고급 과정 수강 권장</p>
            </div>
            """, unsafe_allow_html=True)
        elif satisfaction and satisfaction >= 6:
            st.markdown("""
            <div class="info-box">
                <strong>📈 개선 여지 있음</strong>
                <p>• 학습 방법 다양화</p>
                <p>• 멘토링 활용</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="warning-box">
                <strong>⚠️ 개선 필요</strong>
                <p>• 학습 환경 점검</p>
                <p>• 지원 체계 강화</p>
            </div>
            """, unsafe_allow_html=True)

def main():
    st.markdown("""
    <div class="main-header">
        <h1>📚 학습자 개발 리포트 시스템</h1>
        <h3>Learning Development Report System</h3>
        <p>설문조사 + 교육 데이터 결합 개인화 리포트</p>
    </div>
    """, unsafe_allow_html=True)

    # 탭 생성
    tab1, tab2, tab3 = st.tabs(["👤 학습자 선택", "📋 설문조사", "📊 개인화 리포트"])

    # 사이드바 - 예시 선택
    st.sidebar.header("🎯 데모 시나리오")

    demo_scenario = st.sidebar.selectbox(
        "데모 시나리오:",
        ["실제 데이터 사용", "고급 학습자 예시", "중급 학습자 예시", "초급 학습자 예시", "교육 데이터 누락 예시"]
    )

    # 탭 1: 학습자 선택
    with tab1:
        st.markdown('<div class="section-header">👤 학습자 선택</div>', unsafe_allow_html=True)

        if demo_scenario == "실제 데이터 사용":
            st.markdown("""
            <div class="demo-section">
                <h4>📋 실제 데이터 기반 학습자 선택</h4>
                <p>실제 IDP 데이터를 기반으로 학습자를 선택할 수 있습니다.</p>
            </div>
            """, unsafe_allow_html=True)

            # 실제 데이터 로드 시도
            try:
                idp_file = "「반출」IDP 신청현황 누적 수립율(중복존재)_0709_최신 수립현황_회사명바꾸기_부서나누기.csv"
                idp_data = pd.read_csv(idp_file, encoding='utf-8-sig')

                # 회사별 직원 목록 생성
                companies = idp_data['회사'].unique()
                selected_company = st.selectbox("회사 선택:", companies)

                company_employees = idp_data[idp_data['회사'] == selected_company]
                employee_list = company_employees[['사번', '이름', '부서']].drop_duplicates()
                employee_list['선택옵션'] = employee_list['이름'] + ' (' + employee_list['사번'] + ') - ' + employee_list['부서']

                selected_employee = st.selectbox("직원 선택:", employee_list['선택옵션'])

                if selected_employee:
                    selected_id = selected_employee.split('(')[1].split(')')[0]
                    st.session_state['selected_employee_id'] = selected_id
                    st.session_state['selected_employee_name'] = selected_employee.split('(')[0].strip()
                    st.session_state['selected_company'] = selected_company

                    st.success(f"✅ {selected_employee} 선택 완료!")
                    st.info("다음 단계: '📋 설문조사' 탭에서 설문을 진행해주세요.")

            except Exception as e:
                st.error(f"데이터 로드 오류: {e}")
                st.info("데모 시나리오를 선택하여 예시를 확인하세요.")

        else:
            # 데모 시나리오
            st.markdown(f"""
            <div class="demo-section">
                <h4>🎯 {demo_scenario}</h4>
                <p>이 시나리오에서는 가상의 학습자 데이터를 사용합니다.</p>
            </div>
            """, unsafe_allow_html=True)

            demo_employees = {
                "고급 학습자 예시": {"name": "김성공", "id": "2251234", "dept": "경영기획관리실 DT팀", "company": "동아ST"},
                "중급 학습자 예시": {"name": "이안정", "id": "2255678", "dept": "품질경영실", "company": "동아제약"},
                "초급 학습자 예시": {"name": "박개선", "id": "2259999", "dept": "연구개발실", "company": "에스티팜"},
                "교육 데이터 누락 예시": {"name": "최누락", "id": "2250000", "dept": "영업부", "company": "동아ST"}
            }

            if demo_scenario in demo_employees:
                employee = demo_employees[demo_scenario]
                st.markdown(f"""
                <div class="metric-card">
                    <h4>선택된 학습자</h4>
                    <h3>{employee['name']}</h3>
                    <p><strong>사번:</strong> {employee['id']}</p>
                    <p><strong>부서:</strong> {employee['dept']}</p>
                    <p><strong>회사:</strong> {employee['company']}</p>
                </div>
                """, unsafe_allow_html=True)

                st.session_state['selected_employee_id'] = employee['id']
                st.session_state['selected_employee_name'] = employee['name']
                st.session_state['selected_company'] = employee['company']
                st.session_state['demo_scenario'] = demo_scenario

                st.success("✅ 학습자 선택 완료!")
                st.info("다음 단계: '📋 설문조사' 탭에서 설문을 진행해주세요.")

    # 탭 2: 설문조사
    with tab2:
        st.markdown('<div class="section-header">📋 학습자 개발 설문조사</div>', unsafe_allow_html=True)

        if 'selected_employee_id' not in st.session_state:
            st.warning("⚠️ 먼저 '👤 학습자 선택' 탭에서 학습자를 선택해주세요.")
        else:
            # 선택된 학습자 정보 표시
            selected_company = st.session_state.get('selected_company', '동아ST')
            selected_name = st.session_state.get('selected_employee_name', '사용자')

            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 30px;
                        border-radius: 15px;
                        text-align: center;
                        margin: 20px 0;">
                <h2 style="margin: 0 0 10px 0;">{selected_company}의 {selected_name}님! 안녕하세요?</h2>
                <p style="font-size: 18px; margin: 0;">교육 리포트 발간을 위해 아래 5가지 설문에 응해주세요!</p>
                <p style="font-size: 16px; margin: 10px 0 0 0; opacity: 0.9;">2분 소요됩니다.</p>
            </div>
            """, unsafe_allow_html=True)
            # 단계별 진행 표시
            st.markdown("""
            <div style="display: flex; justify-content: space-between; margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 10px;">
                <div style="text-align: center; flex: 1;">
                    <div style="width: 30px; height: 30px; background: #1f77b4; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 5px;">1</div>
                    <small>기본정보</small>
                </div>
                <div style="text-align: center; flex: 1;">
                    <div style="width: 30px; height: 30px; background: #1f77b4; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 5px;">2</div>
                    <small>학습동기</small>
                </div>
                <div style="text-align: center; flex: 1;">
                    <div style="width: 30px; height: 30px; background: #1f77b4; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 5px;">3</div>
                    <small>학습환경</small>
                </div>
                <div style="text-align: center; flex: 1;">
                    <div style="width: 30px; height: 30px; background: #1f77b4; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 5px;">4</div>
                    <small>만족도</small>
                </div>
                <div style="text-align: center; flex: 1;">
                    <div style="width: 30px; height: 30px; background: #1f77b4; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 5px;">5</div>
                    <small>완료</small>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # 단계별 설문 진행
            if 'survey_step' not in st.session_state:
                st.session_state['survey_step'] = 1

            # 단계 1: 기본 정보
            if st.session_state['survey_step'] == 1:
                st.markdown("### 👤 1단계: 기본 정보 확인")
                st.markdown("**간단한 기본 정보를 확인해주세요.**")

                col1, col2 = st.columns([1, 1])

                with col1:
                    st.markdown("#### 🏢 소속 회사")
                    company = st.session_state.get('selected_company', '동아ST')
                    st.info(f"**{company}**")

                with col2:
                    st.markdown("#### 🆔 사번")
                    employee_id = st.session_state.get('selected_employee_id', '')
                    st.info(f"**{employee_id}**")

                st.session_state['company'] = company
                st.session_state['employee_id'] = employee_id

                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("다음 단계 →", type="primary", use_container_width=True):
                        st.session_state['survey_step'] = 2
                        st.rerun()

            # 단계 2: 학습 동기
            elif st.session_state['survey_step'] == 2:
                st.markdown("### 🎯 2단계: 학습 동기 및 목표")
                st.markdown("**현재 학습에 대한 동기와 향후 목표를 알려주세요.**")

                st.markdown("#### 📊 현재 학습 동기 수준")
                motivation_options = ["매우 낮음", "낮음", "보통", "높음", "매우 높음"]
                motivation_index = st.radio(
                    "현재 학습에 대한 동기 수준을 선택해주세요:",
                    options=motivation_options,
                    horizontal=True,
                    index=None
                )

                st.markdown("#### 🎯 향후 경력 목표")
                st.markdown("**복수 선택 가능합니다.**")

                career_goals_options = [
                    "현재 직무 전문성 향상",
                    "관리자 승진",
                    "전문가(스페셜리스트) 육성",
                    "타 부서 이동",
                    "창업/독립",
                    "아직 불분명"
                ]

                career_goals = []

                if st.checkbox("현재 직무 전문성 향상"):
                    career_goals.append("현재 직무 전문성 향상")
                if st.checkbox("관리자 승진"):
                    career_goals.append("관리자 승진")
                if st.checkbox("전문가(스페셜리스트) 육성"):
                    career_goals.append("전문가(스페셜리스트) 육성")
                if st.checkbox("타 부서 이동"):
                    career_goals.append("타 부서 이동")
                if st.checkbox("창업/독립"):
                    career_goals.append("창업/독립")
                if st.checkbox("아직 불분명"):
                    career_goals.append("아직 불분명")

                st.session_state['learning_motivation'] = motivation_index
                st.session_state['career_goals'] = career_goals

                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    if st.button("← 이전", use_container_width=True):
                        st.session_state['survey_step'] = 1
                        st.rerun()
                with col3:
                    if st.button("다음 단계 →", type="primary", use_container_width=True):
                        if motivation_index is None:
                            st.error("학습 동기 수준을 선택해주세요.")
                        elif not career_goals:
                            st.error("최소 하나의 경력 목표를 선택해주세요.")
                        else:
                            st.session_state['survey_step'] = 3
                            st.rerun()

            # 단계 3: 학습 환경
            elif st.session_state['survey_step'] == 3:
                st.markdown("### ⏰ 3단계: 학습 환경 및 자원")
                st.markdown("**현재 학습 환경과 활용 가능한 자원을 알려주세요.**")

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("#### ⏰ 학습 시간")
                    daily_study_time = st.selectbox(
                        "일일 학습 시간은 얼마나 되나요?",
                        ["30분 미만", "30분-1시간", "1-2시간", "2-3시간", "3시간 이상"],
                        index=None
                    )

                    st.markdown("#### 📚 선호 학습 방식")
                    learning_preference = st.selectbox(
                        "어떤 학습 방식을 선호하시나요?",
                        ["개인 학습", "그룹 학습", "멘토링", "실습 중심", "이론 중심", "혼합형"],
                        index=None
                    )

                with col2:
                    st.markdown("#### 📖 주요 학습 자원")
                    st.markdown("**복수 선택 가능합니다.**")

                    learning_resources = []

                    if st.checkbox("회사 내부 교육"):
                        learning_resources.append("회사 내부 교육")
                    if st.checkbox("온라인 강의"):
                        learning_resources.append("온라인 강의")
                    if st.checkbox("도서/서적"):
                        learning_resources.append("도서/서적")
                    if st.checkbox("동료 멘토링"):
                        learning_resources.append("동료 멘토링")
                    if st.checkbox("외부 세미나"):
                        learning_resources.append("외부 세미나")
                    if st.checkbox("자격증 과정"):
                        learning_resources.append("자격증 과정")
                    if st.checkbox("프로젝트 경험"):
                        learning_resources.append("프로젝트 경험")

                st.session_state['daily_study_time'] = daily_study_time
                st.session_state['learning_preference'] = learning_preference
                st.session_state['learning_resources'] = learning_resources

                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    if st.button("← 이전", use_container_width=True):
                        st.session_state['survey_step'] = 2
                        st.rerun()
                with col3:
                    if st.button("다음 단계 →", type="primary", use_container_width=True):
                        if daily_study_time is None:
                            st.error("일일 학습 시간을 선택해주세요.")
                        elif learning_preference is None:
                            st.error("선호 학습 방식을 선택해주세요.")
                        elif not learning_resources:
                            st.error("최소 하나의 학습 자원을 선택해주세요.")
                        else:
                            st.session_state['survey_step'] = 4
                            st.rerun()

            # 단계 4: 학습 만족도
            elif st.session_state['survey_step'] == 4:
                st.markdown("### 😊 4단계: 학습 만족도 및 효과성")
                st.markdown("**현재 학습에 대한 만족도와 효과성을 평가해주세요.**")

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("#### 😊 학습 만족도")
                    st.markdown("**1~10점 중 선택해주세요.**")
                    learning_satisfaction = st.selectbox(
                        "전반적인 학습 만족도",
                        options=["1점 (매우 불만족)", "2점", "3점", "4점", "5점", "6점", "7점", "8점", "9점", "10점 (매우 만족)"],
                        index=None
                    )

                    st.markdown("#### 📈 업무 스킬 향상도")
                    st.markdown("**1~10점 중 선택해주세요.**")
                    skill_improvement = st.selectbox(
                        "업무 스킬 향상도",
                        options=["1점 (전혀 향상되지 않음)", "2점", "3점", "4점", "5점", "6점", "7점", "8점", "9점", "10점 (크게 향상됨)"],
                        index=None
                    )

                with col2:
                    st.markdown("#### 💼 업무 적용도")
                    st.markdown("**1~10점 중 선택해주세요.**")
                    learning_application = st.selectbox(
                        "학습 내용 업무 적용도",
                        options=["1점 (전혀 적용되지 않음)", "2점", "3점", "4점", "5점", "6점", "7점", "8점", "9점", "10점 (잘 적용됨)"],
                        index=None
                    )

                    st.markdown("#### 📅 향후 학습 계획")
                    future_learning_plan = st.radio(
                        "향후 학습 계획은 구체적으로 세워져 있나요?",
                        options=["매우 구체적", "구체적", "보통", "모호함", "없음"],
                        index=None,
                        horizontal=True
                    )

                # 점수 추출 (드롭다운에서)
                if learning_satisfaction is not None:
                    learning_satisfaction_score = int(learning_satisfaction.split('점')[0])
                else:
                    learning_satisfaction_score = None

                if skill_improvement is not None:
                    skill_improvement_score = int(skill_improvement.split('점')[0])
                else:
                    skill_improvement_score = None

                if learning_application is not None:
                    learning_application_score = int(learning_application.split('점')[0])
                else:
                    learning_application_score = None

                st.session_state['learning_satisfaction'] = learning_satisfaction_score
                st.session_state['skill_improvement'] = skill_improvement_score
                st.session_state['learning_application'] = learning_application_score
                st.session_state['future_learning_plan'] = future_learning_plan

                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    if st.button("← 이전", use_container_width=True):
                        st.session_state['survey_step'] = 3
                        st.rerun()
                with col3:
                    if st.button("다음 단계 →", type="primary", use_container_width=True):
                        if learning_satisfaction is None:
                            st.error("전반적인 학습 만족도를 선택해주세요.")
                        elif skill_improvement is None:
                            st.error("업무 스킬 향상도를 선택해주세요.")
                        elif learning_application is None:
                            st.error("학습 내용 업무 적용도를 선택해주세요.")
                        elif future_learning_plan is None:
                            st.error("향후 학습 계획을 선택해주세요.")
                        else:
                            st.session_state['survey_step'] = 5
                            st.rerun()

            # 단계 5: 장애요인 및 완료
            elif st.session_state['survey_step'] == 5:
                st.markdown("### 🚧 5단계: 학습 장애요인 및 개선사항")
                st.markdown("**학습을 방해하는 요인과 개선 제안사항을 알려주세요.**")

                st.markdown("#### 🚧 학습 장애요인")
                st.markdown("**복수 선택 가능합니다.**")

                learning_barriers_options = [
                    "시간 부족", "동기 부족", "적절한 교육 프로그램 부족", "경비 부담",
                    "학습 환경 부족", "가족/개인 사정", "업무 부담", "기타"
                ]

                learning_barriers = []

                if st.checkbox("시간 부족"):
                    learning_barriers.append("시간 부족")
                if st.checkbox("동기 부족"):
                    learning_barriers.append("동기 부족")
                if st.checkbox("적절한 교육 프로그램 부족"):
                    learning_barriers.append("적절한 교육 프로그램 부족")
                if st.checkbox("경비 부담"):
                    learning_barriers.append("경비 부담")
                if st.checkbox("학습 환경 부족"):
                    learning_barriers.append("학습 환경 부족")
                if st.checkbox("가족/개인 사정"):
                    learning_barriers.append("가족/개인 사정")
                if st.checkbox("업무 부담"):
                    learning_barriers.append("업무 부담")
                if st.checkbox("기타"):
                    learning_barriers.append("기타")

                st.markdown("#### 💡 개선 제안사항")
                improvement_suggestions = st.text_area(
                    "더 나은 학습 환경을 위한 제안사항이 있으시면 자유롭게 작성해주세요.",
                    placeholder="예: 교육 시간 확보, 온라인 학습 플랫폼 구축, 멘토링 프로그램 운영 등...",
                    height=100
                )

                st.session_state['learning_barriers'] = learning_barriers
                st.session_state['improvement_suggestions'] = improvement_suggestions

                # 설문 완료 및 제출
                st.markdown("---")
                st.markdown("### ✅ 설문 완료")

                # 설문 요약 표시
                with st.expander("📋 설문 응답 요약", expanded=True):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write("**기본 정보**")
                        st.write(f"• 회사: {st.session_state.get('company', 'N/A')}")
                        st.write(f"• 사번: {st.session_state.get('employee_id', 'N/A')}")
                        st.write(f"• 학습 동기: {st.session_state.get('learning_motivation', 'N/A')}")
                        st.write(f"• 학습 시간: {st.session_state.get('daily_study_time', 'N/A')}")

                    with col2:
                        st.write("**학습 만족도**")
                        st.write(f"• 전반적 만족도: {st.session_state.get('learning_satisfaction', 'N/A')}/10점")
                        st.write(f"• 스킬 향상도: {st.session_state.get('skill_improvement', 'N/A')}/10점")
                        st.write(f"• 업무 적용도: {st.session_state.get('learning_application', 'N/A')}/10점")
                        st.write(f"• 학습 계획: {st.session_state.get('future_learning_plan', 'N/A')}")

                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    if st.button("← 이전", use_container_width=True):
                        st.session_state['survey_step'] = 4
                        st.rerun()
                with col3:
                    if st.button("📤 설문 제출 및 리포트 생성", type="primary", use_container_width=True):
                        if not learning_barriers:
                            st.error("최소 하나의 학습 장애요인을 선택해주세요.")
                        else:
                            # 설문 데이터 저장
                            survey_data = {
                                'company': st.session_state.get('company'),
                                'employee_id': st.session_state.get('employee_id'),
                                'learning_motivation': st.session_state.get('learning_motivation'),
                                'career_goals': st.session_state.get('career_goals'),
                                'daily_study_time': st.session_state.get('daily_study_time'),
                                'learning_preference': st.session_state.get('learning_preference'),
                                'learning_resources': st.session_state.get('learning_resources'),
                                'learning_satisfaction': st.session_state.get('learning_satisfaction'),
                                'skill_improvement': st.session_state.get('skill_improvement'),
                                'learning_application': st.session_state.get('learning_application'),
                                'future_learning_plan': st.session_state.get('future_learning_plan'),
                                'learning_barriers': st.session_state.get('learning_barriers'),
                                'improvement_suggestions': st.session_state.get('improvement_suggestions')
                            }

                            st.session_state['survey_data'] = survey_data
                            st.session_state['show_report'] = True

                            st.success("🎉 설문이 성공적으로 제출되었습니다!")
                            st.info("📊 '개인화 리포트' 탭에서 결과를 확인하세요.")
                            st.balloons()

    # 탭 3: 개인화 리포트
    with tab3:
        st.markdown('<div class="section-header">📊 개인화 리포트</div>', unsafe_allow_html=True)

        report_scenario = st.session_state.get('demo_scenario', '실제 데이터 사용')

        if 'selected_employee_id' not in st.session_state:
            st.warning("⚠️ 먼저 '👤 학습자 선택' 탭에서 학습자를 선택해주세요.")

        elif report_scenario == "실제 데이터 사용":
            if 'show_report' not in st.session_state or not st.session_state['show_report']:
                st.info("📋 '📋 설문조사' 탭에서 설문을 완료하고 '설문 제출 및 리포트 생성' 버튼을 눌러주세요.")
            else:
                show_general_report()
        elif report_scenario == "고급 학습자 예시":
            show_advanced_report()
        elif report_scenario == "중급 학습자 예시":
            show_intermediate_report()
        elif report_scenario == "초급 학습자 예시":
            show_beginner_report()
        elif report_scenario == "교육 데이터 누락 예시":
            show_missing_data_report()

    # 시스템 설명
    st.markdown('<div class="section-header">🔧 시스템 특징</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="info-box">
            <h5>📊 데이터 융합</h5>
            <p>객관적 교육 데이터 + 주관적 설문 데이터를 결합하여 정확한 분석 제공</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="info-box">
            <h5>🎯 개인화</h5>
            <p>개인별 특성에 맞는 맞춤형 분석 및 권고사항 제공</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="info-box">
            <h5>📞 연락처 안내</h5>
            <p>교육 데이터 누락 시 적절한 담당자 연락처 및 문의 방법 안내</p>
        </div>
        """, unsafe_allow_html=True)

    # 푸터
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 12px;">
        <p>※ 이 리포트는 설문조사와 교육 데이터를 결합한 AI 기반 분석 시스템을 통해 생성되었습니다.</p>
        <p>생성일: """ + datetime.now().strftime("%Y년 %m월 %d일") + """</p>
        <p>📞 교육 데이터 문의: idp@donga.com | 교육 담당자: 각사 인재경영실</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
