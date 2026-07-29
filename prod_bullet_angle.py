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
    
    if filtered_products is not None and not filtered_products.empty:
        df_pm = filtered_products.copy()
    else:
        df_pm = options_df.copy()
        
    df_pm['제품명_검색용'] = df_pm['제품명'].astype(str).str.replace(' ', '') if '제품명' in df_pm.columns else pd.Series()
    
    def find_col(keyword):
        for c in df_pm.columns:
            if keyword in c: return c
        return None
        
    h_col = find_col('높이/길이')
    inch_col = find_col('직경')

    # 도면 이미지 중앙 정렬 CSS
    st.markdown("""
    <style>
    [data-testid="stImage"] {
        display: flex;
        justify-content: center;
        align-items: center;
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
        
        # 💡 1. 일반 뷸렛카메라박스
        if sel_bullet == "일반 뷸렛카메라박스":
            st.markdown("<div style='font-size:14px; margin-top:10px; margin-bottom:5px; color:#555;'>👇 카메라박스 높이 선택</div>", unsafe_allow_html=True)
            box_height = st.radio("높이", ["60mm", "120mm"], index=1, horizontal=True, key=f"bh_{rk}", label_visibility="collapsed")
            
            st.markdown("<div style='font-size:14px; margin-top:20px; margin-bottom:10px; color:#555; font-weight:bold;'>👇 하부 판재 선택</div>", unsafe_allow_html=True)
            
            plate_opts = ["A타입", "B타입", "C타입", "D타입"]
            sel_plate = st.radio("하부 판재 라디오", plate_opts, index=0, horizontal=True, key=f"plate_{rk}", label_visibility="collapsed")
            
            st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
            
            img_area, empty_area = st.columns([2.5, 7.5])
            with img_area:
                cols = st.columns(4, gap="small")
                plate_names = ["A", "B", "C", "D"]
                for i, p_name in enumerate(plate_names):
                    with cols[i]:
                        img_png = f"images/하부판재-{p_name}.png"
                        img_jpg = f"images/하부판재-{p_name}.jpg"
                        
                        if os.path.exists(img_png):
                            st.image(img_png, width="stretch")
                        elif os.path.exists(img_jpg):
                            st.image(img_jpg, width="stretch")
                        else:
                            st.markdown(f"<div style='aspect-ratio: 1; width: 100%; border:1px solid #e0e0e0; display:flex; align-items:center; justify-content:center; border-radius:3px; color:#999; font-size:10px; text-align:center;'>{p_name}<br>없음</div>", unsafe_allow_html=True)
            
            h_val = float(box_height.replace("mm", ""))
            match_df = pd.DataFrame()
            if '제품명_검색용' in df_pm.columns and h_col:
                match_df = df_pm[(df_pm['제품명_검색용'] == '일반뷸렛카메라박스') & 
                                 (pd.to_numeric(df_pm[h_col], errors='coerce') == h_val)]
            
            if not match_df.empty:
                base_price = int(match_df.iloc[0]['단가'])
            else:
                base_price = 15000 if h_val == 60 else 20000
            
            product_specs = f"일반 뷸렛카메라박스 - 높이:{box_height} / 하부판재:{sel_plate}"
            is_main_ready = True
            combo_names = [f"일반 뷸렛카메라박스-{int(h_val)}"]
            
        # 💡 2. 벽부형 뷸렛카메라박스
        elif sel_bullet == "벽부형 뷸렛카메라박스":
            match_df = pd.DataFrame()
            if '제품명_검색용' in df_pm.columns:
                match_df = df_pm[df_pm['제품명_검색용'].str.contains('벽부형', na=False)]
                
            if not match_df.empty:
                base_price = int(match_df.iloc[0]['단가'])
            else:
                base_price = 35000
            
            product_specs = "벽부형 뷸렛카메라박스"
            is_main_ready = True
            combo_names = ["벽부형 뷸렛카메라박스"]
            
        # 💡 3. 스텐밴드형 뷸렛카메라박스
        elif sel_bullet == "스텐밴드형 뷸렛카메라박스":
            match_df = pd.DataFrame()
            if '제품명_검색용' in df_pm.columns:
                match_df = df_pm[df_pm['제품명_검색용'].str.contains('스텐', na=False) & df_pm['제품명_검색용'].str.contains('밴드', na=False)]
                
            if not match_df.empty:
                base_price = int(match_df.iloc[0]['단가'])
            else:
                base_price = 40000
            
            product_specs = "스텐밴드형 뷸렛카메라박스"
            is_main_ready = True
            combo_names = ["스텐밴드형 뷸렛카메라박스"]
            
        # 💡 4. 밴드형 뷸렛카메라박스 (인치 선택)
        elif sel_bullet == "밴드형 뷸렛카메라박스":
            st.markdown("<div style='font-size:14px; margin-top:10px; margin-bottom:5px; color:#555;'>👉 설치할 파이프 직경 선택</div>", unsafe_allow_html=True)
            inch_opts = ["2.5인치", "3인치", "4인치", "5인치", "6인치"]
            sel_inch = st.radio("파이프 직경", inch_opts, index=0, horizontal=True, key=f"bullet_inch_{rk}", label_visibility="collapsed")
            
            inch_val = float(sel_inch.replace("인치", "").strip())
            match_df = pd.DataFrame()
            if '제품명_검색용' in df_pm.columns and inch_col:
                # 괄호 문법 오류 수정 완료된 영역
                match_df = df_pm[(df_pm['제품명_검색용'] == '밴드형뷸렛카메라박스') & 
                                 (pd.to_numeric(df_pm[inch_col], errors='coerce') == inch_val)]
            
            if not match_df.empty:
                base_price = int(match_df.iloc[0]['단가'])
            else:
                price_map = {2.5: 45000, 3.0: 45000, 4.0: 45000, 5.0: 50000, 6.0: 55000}
                base_price = price_map.get(inch_val, 45000)
            
            product_specs = f"밴드형 뷸렛카메라박스 ({sel_inch})"
            is_main_ready = True
            combo_names = ["밴드형 뷸렛카메라박스"]
            
        # 💡 5. 주문형 스텐 카메라박스 (주문제작)
        elif sel_bullet == "주문형 스텐 카메라박스":
            st.markdown("<div style='font-size:14px; margin-top:10px; margin-bottom:5px; color:#555;'>👉 주문제작 치수 입력 (mm)</div>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            c_w = c1.number_input("가로 (mm)", min_value=0, value=None, step=10, key=f"cw_{rk}", placeholder="예: 150")
            c_d = c2.number_input("세로 (mm)", min_value=0, value=None, step=10, key=f"cd_{rk}", placeholder="예: 150")
            c_h = c3.number_input("높이 (mm)", min_value=0, value=None, step=10, key=f"ch_{rk}", placeholder="예: 150")
            
            if c_w is not None and c_d is not None and c_h is not None and c_w > 0 and c_d > 0 and c_h > 0:
                base_price = 0
                product_specs = f"주문형 스텐 뷸렛카메라박스 - 가로:{int(c_w)} x 세로:{int(c_d)} x 높이:{int(c_h)}"
                st.markdown("<div style='font-size:15px; font-weight:bold; color:#d9534f; margin-top:10px;'>💡 단가: 주문제작 단가 (별도 안내)</div>", unsafe_allow_html=True)
                is_main_ready = True
                combo_names = ["주문형 스텐 뷸렛카메라박스"]
            else:
                is_main_ready = False
                st.warning("⚠️ 가로, 세로, 높이에 제작하실 치수(mm)를 모두 입력해 주세요.")
                combo_names = ["주문형 스텐 뷸렛카메라박스"]

    # 💡 6. 각도기
    elif main_type == "각도기":
        st.markdown("<div style='font-size:14px; margin-top:10px; margin-bottom:5px; color:#555;'>👇 각도기 종류를 선택해 주세요</div>", unsafe_allow_html=True)
        ang_opts = ["알루미늄 각도기", "스텐 각도기(80*80)", "번호인식 각도기"]
        sel_ang = st.radio("각도기 선택", ang_opts, index=0, horizontal=True, key=f"ang_sub_{rk}", label_visibility="collapsed")
        
        target_name = sel_ang.replace(" ", "").replace("(80*80)", "")
        match_df = pd.DataFrame()
        if '제품명_검색용' in df_pm.columns:
            match_df = df_pm[df_pm['제품명_검색용'].str.contains(target_name, na=False)]
            
        if not match_df.empty:
            base_price = int(match_df.iloc[0]['단가'])
        else:
            ang_map = {"알루미늄각도기": 8000, "스텐각도기": 10000, "번호인식각도기": 25000}
            base_price = ang_map.get(target_name, 10000)
        
        product_specs = f"각도기 - {sel_ang}"
        is_main_ready = True
        
        ang_kw = sel_ang.replace("(80*80)", "").strip()
        combo_names = [ang_kw]

    # 공통 옵션 렌더링 및 출력
    if is_main_ready:
        st.markdown("<h2>2. 옵션 선택</h2>", unsafe_allow_html=True)
        opt_col, img_col = st.columns([5.5, 4.5])
        with opt_col:
            utils.render_generic_groups(cat_no_space, options_df, rk, priced_options, zero_options, preview_images)
        valid_paths = utils.display_images(combo_names, priced_options, zero_options, preview_images, img_col, cat_no_space)
        return is_main_ready, base_price, product_specs, valid_paths, priced_options, zero_options
        
    return False, 0, "", [], [], []