import streamlit as st
import pandas as pd
import utils

def render(filtered_products, options_df, rk, cat_no_space):
    is_main_ready, base_price, product_specs = False, 0, ""
    preview_images, priced_options, zero_options, selected_cam_parts = [], [], [], []

    st.markdown("<div style='font-size:15px; font-weight:bold; color:#2e6c80; margin-bottom:5px;'>1️⃣ 제품 종류 선택</div>", unsafe_allow_html=True)
    main_type = st.radio("제품 종류", ["뷸렛카메라박스", "각도기"], index=0, horizontal=True, key=f"bullet_main_{rk}", label_visibility="collapsed")

    combo_names = []
    
    # 엑셀 원본 데이터 (단가 검색용)
    df_pm = filtered_products

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
        
        # 💡 1. 일반 뷸렛카메라박스
        if sel_bullet == "일반 뷸렛카메라박스":
            st.markdown("<div style='font-size:14px; margin-top:10px; margin-bottom:5px; color:#555;'>👇 카메라박스 높이 선택</div>", unsafe_allow_html=True)
            box_height = st.radio("높이", ["60mm", "120mm"], index=0, horizontal=True, key=f"bh_{rk}", label_visibility="collapsed")
            
            st.markdown("<div style='font-size:14px; margin-top:15px; margin-bottom:5px; color:#555;'>👇 하부 판재 선택</div>", unsafe_allow_html=True)
            st.info("💡 선택하신 하부 판재의 도면은 우측 미리보기 화면에 표시됩니다.")
            plate_opts = ["A타입", "B타입", "C타입", "D타입"]
            sel_plate = st.radio("하부 판재", plate_opts, index=0, horizontal=True, key=f"plate_{rk}", label_visibility="collapsed")
            
            # 단가 매칭
            match_df = df_pm[df_pm['제품명'].astype(str).str.replace(" ","").str.contains("일반뷸렛", na=False)]
            base_price = int(match_df.iloc[0]['단가']) if not match_df.empty else 20000
            
            product_specs = f"일반 뷸렛카메라박스 - 높이:{box_height} / 하부판재:{sel_plate}"
            is_main_ready = True
            
            plate_kw = sel_plate.replace("타입", "")
            combo_names = [f"하부판재-{plate_kw}", "일반 뷸렛카메라박스"]
            
        # 💡 2. 벽부형 뷸렛카메라박스
        elif sel_bullet == "벽부형 뷸렛카메라박스":
            match_df = df_pm[df_pm['제품명'].astype(str).str.replace(" ","").str.contains("벽부형", na=False)]
            base_price = int(match_df.iloc[0]['단가']) if not match_df.empty else 20000 # 엑셀 미존재 시 임시단가
            
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
            
            # 제품마스터에서 '밴드형 뷸렛카메라박스' 단가 호출 (일단 기본 단가로 처리)
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
        
        # 각도기 단가는 옵션 엑셀에서 가져오는 기존 로직 유지
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