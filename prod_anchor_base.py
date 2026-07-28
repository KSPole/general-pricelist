import streamlit as st
import pandas as pd
import utils
import os

def render(filtered_products, options_df, rk, cat_no_space):
    is_main_ready, base_price, product_specs = False, 0, ""
    preview_images, priced_options, zero_options, selected_cam_parts = [], [], [], []

    st.markdown("<div style='font-size:15px; font-weight:bold; color:#2e6c80; margin-bottom:5px;'>1️⃣ 제품 종류 선택</div>", unsafe_allow_html=True)
    main_type = st.radio("제품 종류", ["뷸렛카메라박스", "각도기"], index=0, horizontal=True, key=f"bullet_main_{rk}", label_visibility="collapsed")

    combo_names = []
    
    # 엑셀 원본 데이터 (단가 검색용)
    df_pm = filtered_products

    # 💡 라디오 버튼을 4개의 이미지 아래에 '정확하게' 중앙 정렬시키는 마법의 강제 CSS
    st.markdown("""
    <style>
    /* 하부 판재 전용 라디오 버튼 스타일 무조건 강제 적용 */
    div[data-testid="stRadio"] > div[role="radiogroup"] {
        display: flex !important;
        flex-direction: row !important;
        justify-content: space-around !important;
        width: 100% !important;
        padding-top: 5px !important;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] > label {
        flex: 1 1 25% !important;
        display: flex !important;
        justify-content: center !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    if main_type == "뷸렛카메라박스":
        st.markdown("<div style='font-size:14px; margin-top:10px; margin-bottom:5px; color:#555;'>👇 뷸렛카메라박스 종류를 선택해 주세요</div>", unsafe_allow_html=True)
        bullet_opts = [
            "일반 뷸렛카메라박스", 
            "벽부형 뷸렛카메라박스", 
            "스텐밴드형 뷸렛카메라박스", 
            "밴드형 뷸렛카메라박스", 
            "주문형 스텐 카메라박스"
        ]
        sel_bullet = st.radio("뷸렛 종류", bullet_opts, index=0, horizontal=True, key=f"bullet_sub_{rk}", label_visibility="collapsed")
        
        # 💡 1. 일반 뷸렛카메라박스 (이미지와 라디오 버튼 완벽 일렬 매칭 UI)
        if sel_bullet == "일반 뷸렛카메라박스":
            st.markdown("<div style='font-size:14px; margin-top:10px; margin-bottom:5px; color:#555;'>👇 카메라박스 높이 선택</div>", unsafe_allow_html=True)
            box_height = st.radio("높이", ["60mm", "120mm"], index=0, horizontal=True, key=f"bh_{rk}", label_visibility="collapsed")
            
            # 첨부 이미지와 100% 똑같은 레이아웃 구축
            st.markdown("<div style='font-size:16px; margin-top:20px; margin-bottom:10px; color:#555; font-weight:bold;'>👇 하부 판재 선택</div>", unsafe_allow_html=True)
            
            # 1. 화면을 4등분하여 이미지만 먼저 나란히 배치
            cols = st.columns(4)
            plate_names = ["A", "B", "C", "D"]
            for i, p_name in enumerate(plate_names):
                with cols[i]:
                    img_png = f"images/하부판재-{p_name}.png"
                    img_jpg = f"images/하부판재-{p_name}.jpg"
                    
                    st.markdown("<div style='padding: 0px 5px;'>", unsafe_allow_html=True)
                    if os.path.exists(img_png):
                        st.image(img_png, use_container_width=True)
                    elif os.path.exists(img_jpg):
                        st.image(img_jpg, use_container_width=True)
                    else:
                        # 이미지가 없을 때 차지할 공간 (정사각형)
                        st.markdown(f"<div style='aspect-ratio: 1; border:1px solid #e0e0e0; display:flex; align-items:center; justify-content:center; border-radius:3px; color:#999; font-size:12px; text-align:center;'>{p_name}타입<br>이미지 없음</div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
            
            # 2. 이미지 바로 밑에 라디오 버튼 한 줄을 통째로 삽입! (위의 CSS가 이 라디오 버튼들을 4칸의 정중앙으로 쭉 찢어발겨(?) 정렬시킵니다)
            plate_opts = ["A타입", "B타입", "C타입", "D타입"]
            sel_plate = st.radio("하부 판재 라디오", plate_opts, index=0, horizontal=True, key=f"plate_{rk}", label_visibility="collapsed")
            
            # 단가 매칭
            match_df = df_pm[df_pm['제품명'].astype(str).str.replace(" ","").str.contains("일반뷸렛", na=False)]
            base_price = int(match_df.iloc[0]['단가']) if not match_df.empty else 20000
            
            product_specs = f"일반 뷸렛카메라박스 - 높이:{box_height} / 하부판재:{sel_plate}"
            is_main_ready = True
            
            # 우측 미리보기에는 헷갈리지 않게 '일반 뷸렛카메라박스' 본체 1가지만 고정
            combo_names = ["일반 뷸렛카메라박스"]
            
        # 💡 2. 벽부형 뷸렛카메라박스
        elif sel_bullet == "벽부형 뷸렛카메라박스":
            match_df = df_pm[df_pm['제품명'].astype(str).str.replace(" ","").str.contains("벽부형", na=False)]
            base_price = int(match_df.iloc[0]['단가']) if not match_df.empty else 20000 
            
            product_specs = "벽부형 뷸렛카메라박스"
            is_main_ready = True
            combo_names = ["벽부형 뷸렛카메라박스"]
            
        # 💡 3. 스텐밴드형 뷸렛카메라박스
        elif sel_bullet == "스텐밴드형 뷸렛카메라박스":
            match_df = df_pm[df_pm['제품명'].astype(str).str.replace(" ","").str.contains("스텐", na=False) & df_pm['제품명'].astype(str).str.replace(" ","").str.contains("밴드", na=False)]
            base_price = int(match_df.iloc[0]['단가']) if not match_df.empty else 40000
            
            product_specs = "스텐밴드형 뷸렛카메라박스"
            is_main_ready = True
            combo_names = ["스텐밴드형 뷸렛카메라박스"]
            
        # 💡 4. 밴드형 뷸렛카메라박스 (인치 선택)
        elif sel_bullet == "밴드형 뷸렛카메라박스":
            st.markdown("<div style='font-size:14px; margin-top:10px; margin-bottom:5px; color:#555;'>👉 설치할 파이프 직경 선택</div>", unsafe_allow_html=True)
            inch_opts = ["2.5인치", "3인치", "4인치", "5인치", "6인치"]
            sel_inch = st.radio("파이프 직경", inch_opts, index=0, horizontal=True, key=f"bullet_inch_{rk}", label_visibility="collapsed")
            
            match_df = df_pm[df_pm['제품명'].astype(str).str.replace(" ","").str.contains("밴드형", na=False) & ~df_pm['제품명'].astype(str).str.replace(" ","").str.contains("스텐", na=False)]
            base_price = int(match_df.iloc[0]['단가']) if not match_df.empty else 45000
            
            product_specs = f"밴드형 뷸렛카메라박스 ({sel_inch})"
            is_main_ready = True
            combo_names = ["밴드형 뷸렛카메라박스"]
            
        # 💡 5. 주문형 스텐 카메라박스 (주문제작)
        elif sel_bullet == "주문형 스텐 카메라박스":
            st.markdown("<div style='font-size:14px; margin-top:10px; margin-bottom:5px; color:#555;'>👉 주문제작 치수 입력 (mm)</div>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            c_w = c1.number_input("가로 (mm)", min_value=0, step=10, key=f"cw_{rk}")
            c_d = c2.number_input("세로 (mm)", min_value=0, step=10, key=f"cd_{rk}")
            c_h = c3.number_input("높이 (mm)", min_value=0, step=10, key=f"ch_{rk}")
            
            if c_w > 0 and c_d > 0 and c_h > 0:
                base_price = 0
                product_specs = f"주문형 스텐 뷸렛카메라박스 - 가로:{int(c_w)} x 세로:{int(c_d)} x 높이:{int(c_h)}"
                st.markdown("<div style='font-size:15px; font-weight:bold; color:#d9534f; margin-top:10px;'>💡 단가: 주문제작 단가 (별도 안내)</div>", unsafe_allow_html=True)
                is_main_ready = True
                combo_names = ["주문형 스텐 뷸렛카메라박스"]
            else:
                is_main_ready = False
                st.warning("⚠️ 가로, 세로, 높이를 모두 0보다 크게 입력해 주세요.")
                combo_names = ["주문형 스텐 뷸렛카메라박스"]

    # 💡 6. 각도기
    elif main_type == "각도기":
        st.markdown("<div style='font-size:14px; margin-top:10px; margin-bottom:5px; color:#555;'>👇 각도기 종류를 선택해 주세요</div>", unsafe_allow_html=True)
        ang_opts = ["알루미늄 각도기", "스텐 각도기(80*80)", "번호인식 각도기"]
        sel_ang = st.radio("각도기 선택", ang_opts, index=0, horizontal=True, key=f"ang_sub_{rk}", label_visibility="collapsed")
        
        price = 0
        if sel_ang == "알루미늄 각도기":
            df_opt = options_df[
                (options_df['적용 카테고리'].astype(str).str.contains('CCTV폴', na=False)) & 
                (options_df['옵션 구분(그룹명)'].astype(str).str.contains('카메라 부착 부품', na=False)) & 
                (options_df['추가 선택-1'].astype(str).str.contains('알루미늄 각도기', regex=False, na=False))
            ]
            price = int(df_opt.iloc[0]['단가']) if not df_opt.empty else 8000
            
        elif sel_ang == "스텐 각도기(80*80)":
            df_opt = options_df[
                (options_df['적용 카테고리'].astype(str).str.contains('CCTV폴', na=False)) & 
                (options_df['추가 선택-1'].astype(str).str.contains('스텐 각도기', na=False))
            ]
            price = int(df_opt.iloc[0]['단가']) if not df_opt.empty else 10000
            
        elif sel_ang == "번호인식 각도기":
            df_opt = options_df[
                (options_df['적용 카테고리'].astype(str).str.contains('CCTV폴', na=False)) & 
                (options_df['추가 선택-1'].astype(str).str.contains('번호인식 각도기', na=False))
            ]
            price = int(df_opt.iloc[0]['단가']) if not df_opt.empty else 25000
        
        base_price = price
        product_specs = f"각도기 - {sel_ang}"
        is_main_ready = True
        
        ang_kw = sel_ang.replace(" ", "").replace("(80*80)", "")
        combo_names = [f"각도기-{ang_kw}", "각도기"]

    # 공통 옵션 렌더링 및 출력
    if is_main_ready:
        st.markdown("<h2>2. 옵션 선택</h2>", unsafe_allow_html=True)
        opt_col, img_col = st.columns([5.5, 4.5])
        with opt_col:
            utils.render_generic_groups(cat_no_space, options_df, rk, priced_options, zero_options, preview_images)
        valid_paths = utils.display_images(combo_names, priced_options, zero_options, preview_images, img_col, cat_no_space)
        return is_main_ready, base_price, product_specs, valid_paths, priced_options, zero_options
        
    return False, 0, "", [], [], []