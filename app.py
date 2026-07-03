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
    layout="centered", # 모바일에 더 잘 맞도록 centered 유지
    initial_sidebar_state="collapsed" # 사이드바 기본 숨김
)

# 모바일 등에서도 파비콘이 강제로 보이도록 HTML 태그 주입 및 여백 축소 CSS
st.markdown(
    f"""
    <link rel="shortcut icon" href="data:image/png;base64,{favicon_base64}">
    <link rel="apple-touch-icon" href="data:image/png;base64,{favicon_base64}">
    <style>
        /* 화면 상단 여백 대폭 축소 */
        .block-container {{
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
        }}
        /* 타이틀 글씨 크기 및 여백 조정 */
        h1 {{
            text-align: center;
            font-size: 2.2rem !important;
            margin-bottom: 0px !important;
            padding-bottom: 15px !important;
        }}
        /* 입력창 사이 간격 축소 */
        .stTextInput > div > div > input {{
            padding: 8px 12px !important;
        }}
        .stSelectbox > div > div > div {{
            padding: 8px 12px !important;
        }}
        /* 버튼 디자인 */
        .stButton>button {{
            width: 100%;
            background-color: #004b9b;
            color: white;
            font-weight: bold;
            height: 3rem;
            margin-top: 10px;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# --- 2. 데이터 저장 및 관리 (로그) ---
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

# --- 3. 메인 화면 ---

# 변경된 타이틀 (줄바꿈 적용)
st.markdown("<h1>한국시스템폴<br>단가표</h1>", unsafe_allow_html=True)

# 탭 구성: 일반 사용자용 / 관리자용
tab1, tab2 = st.tabs(["일반 접속", "본사직원/관리자 전용 접속"])

with tab1:
    st.write("단가표 확인을 위해 아래 정보를 입력해 주세요.")
    
    # 입력 폼을 좀 더 촘촘하게 배치
    col1, col2 = st.columns(2)
    with col1:
        company_name = st.text_input("업체명", placeholder="예: 한국시스템폴")
        user_name = st.text_input("성명", placeholder="예: 홍길동")
    with col2:
        position = st.selectbox("직급", ["대표", "이사", "부장", "차장", "과장", "대리", "사원", "기타"])
    
    if st.button("단가표 접속하기"):
        if company_name and user_name:
            save_log(company_name, position, user_name)
            # 단가표 페이지로 이동하는 로직 (기존 코드에 맞게 수정 필요)
            # st.switch_page("pages/1_단가표.py") 처럼 사용하거나, 세션 상태를 변경하여 화면을 전환합니다.
            st.success(f"{company_name} {user_name} {position}님 환영합니다. (단가표 페이지 연결 대기 중...)")
        else:
            st.error("업체명과 성명을 모두 입력해 주세요.")

with tab2:
    st.write("관리자 전용 메뉴입니다.")
    admin_password = st.text_input("관리자 비밀번호", type="password")
    
    if st.button("관리자 로그인"):
        # 실제 사용하실 비밀번호로 변경하세요 (예: "ksp1234")
        if admin_password == "ksp1234":
            st.success("관리자 로그인 성공")
            st.subheader("접속 로그 확인")
            if os.path.exists(LOG_FILE):
                log_data = pd.read_csv(LOG_FILE)
                st.dataframe(log_data.sort_values(by="접속시간", ascending=False), use_container_width=True)
            else:
                st.info("아직 접속 기록이 없습니다.")
        else:
            st.error("비밀번호가 틀렸습니다.")