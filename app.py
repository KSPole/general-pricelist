import streamlit as st
import base64
import pandas as pd
from datetime import datetime
import os

# --- 1. 기본 설정 및 파비콘 ---
favicon_base64 = "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAABVElEQVRYR+2WwU3DMBhGn3gE2AANsAEdAbhA0m6AEdoNkA1aNtAxwAZ0A1hB0gKxA2yARyB8UpUoTpzYiUNV/ZOT+Hn9+f+xZck5x1mW/bDWftm2vd/v97v9fr/Vdd11XR9qrf16vT7e7/efHMcxhmH4tNa+TNM0hRDONsYYzrmXbds+GGMeg8Fgu1qt3gRBhEajwX6/P2y3288wDHkYhgchxN5aezFN09xae5dluVqtVovP5/PZ9Xq9GIZhwBhziTHmdrPZPO73+ykhZLTWPkopt2maXmRZfjPGPG2322tVVS9KKf7p+35f1/UnY8zjZrN5U0rxn36/Hw3D8FfX9WEYho9Syn0YhvX9fv+z1Wrl+Xz+LKVc+/3+bxiGnxJCLsMw3Aoh3gVBMBsMBqMQIuec35RS/NM0Te/WOt638fG/wD/yAv+kHwG+wBf4Al/gC3yBL/AFvsAX+AJf4Aua7z/g2/0N/wD/+Qe8AL5Gz3T0SgAAAABJRU5ErkJggg=="

st.set_page_config(
    page_title="한국시스템폴 단가표",
    page_icon=f"data:image/png;base64,{favicon_base64}",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 1번 & 3번 요구사항: 상단 공백 제거 및 스크롤 없는 화면 압축 스타일(CSS) 주입
st.markdown(
    f"""
    <link rel="shortcut icon" href="data:image/png;base64,{favicon_base64}">
    <link rel="apple-touch-icon" href="data:image/png;base64,{favicon_base64}">
    <style>
        /* 최상단 마진 및 패딩 극소화 */
        .block-container {{
            padding-top: 0.5rem !important;
            padding-bottom: 0.5rem !important;
            max-width: 450px !important;
        }}
        /* 타이틀 디자인 및 여백 제거 */
        h1 {{
            text-align: center;
            font-size: 2.4rem !important;
            line-height: 1.2 !important;
            margin-top: 0px !important;
            margin-bottom: 5px !important;
            padding-bottom: 5px !important;
            font-weight: 800 !important;
            color: #1e293b;
        }}
        /* 안내 문구 간격 축소 */
        .caption-text {{
            text-align: center;
            font-size: 0.9rem;
            color: #64748b;
            margin-bottom: 10px;
        }}
        /* 입력창 라벨 및 높이 압축 */
        label {{
            margin-bottom: 2px !important;
            font-size: 0.85rem !important;
        }}
        .stTextInput > div > div > input {{
            padding: 4px 10px !important;
            height: 38px !important;
        }}
        .stSelectbox > div > div > div {{
            padding: 4px 10px !important;
            height: 38px !important;
        }}
        /* 버튼 조밀하게 배치 */
        .stButton>button {{
            width: 100%;
            background-color: #004b9b;
            color: white;
            font-weight: bold;
            height: 42px !important;
            margin-top: 10px !important;
            border-radius: 6px;
        }}
        /* 탭 간격 조절 */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            margin-bottom: 10px;
        }}
        .stTabs [data-baseweb="tab"] {{
            height: 35px;
            font-size: 0.85rem;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

LOG_FILE = "access_log.csv"

def save_log(company_name, position, user_name):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_data = pd.DataFrame([[now, company_name, position, user_name]], 
                            columns=["접속시간", "업체명", "직급", "성명"])
    if os.path.exists(LOG_FILE):
        log_df = pd.read_csv(LOG_FILE)
        log_df = pd.concat([log_df, new_data], ignore_index=True)
    else:
        log_df = new_data
    log_df.to_csv(LOG_FILE, index=False, encoding='utf-8-sig')

# --- 3. 메인 화면 구성 ---

# 2번 요구사항: "한국시스템폴" 줄바꿈 "단가표"로 위쪽 공간에 표시
st.markdown("<h1>한국시스템폴<br>단가표</h1>", unsafe_allow_html=True)

# 1번 요구사항: 일반접속과 관리자 전용 메뉴 분리 (로그 확인은 관리자 탭 내부에만 존재)
tab1, tab2 = st.tabs(["일반 업체 접속", "본사직원/관리자 전용"])

with tab1:
    st.markdown("<p class='caption-text'>단가표 확인을 위해 정보를 입력해 주세요.</p>", unsafe_allow_html=True)
    
    # 3번 요구사항: 스크롤 없이 한 화면에 다 들어오도록 촘촘하게 배치
    company_name = st.text_input("업체명", placeholder="예: 한국시스템폴")
    
    col1, col2 = st.columns(2)
    with col1:
        user_name = st.text_input("성명", placeholder="예: 홍길동")
    with col2:
        position = st.selectbox("직급", ["대표", "이사", "부장", "차장", "과장", "대리", "사원", "기타"])
    
    if st.button("단가표 접속하기"):
        if company_name and user_name:
            save_log(company_name, position, user_name)
            st.success(f"{company_name} {user_name}님 환영합니다. 단가표로 이동합니다.")
        else:
            st.error("업체명과 성명을 모두 입력해 주세요.")

with tab2:
    st.write("본사 관리자 인증 메뉴입니다.")
    admin_password = st.text_input("관리자 비밀번호", type="password", key="admin_pwd")
    
    if st.button("관리자 로그인"):
        if admin_password == "ksp1234":
            st.success("관리자 인증 성공")
            st.subheader("📊 실시간 접속 로그 확인")
            
            if os.path.exists(LOG_FILE):
                log_data = pd.read_csv(LOG_FILE)
                st.dataframe(log_data.sort_values(by="접속시간", ascending=False), use_container_width=True)
            else:
                st.info("아직 누적된 접속 기록이 없습니다.")
        else:
            st.error("비밀번호가 일치하지 않습니다.")
