import streamlit as st
import pandas as pd
import utils

def render(filtered_products, options_df, rk, cat_no_space):
    is_main_ready, base_price, product_specs = False, 0, ""
    preview_images, priced_options, zero_options, selected_cam_parts = [], [], [], []

    st.markdown("<div style='font-size:15px; font-weight:bold; color:#2e6c80; margin-bottom:5px;'>1️⃣ 제품 종류 선택</div>", unsafe_allow_html=True)
    main_type = st.radio("제품 종류", ["뷸렛카메라박스", "각도기"], index=0, horizontal=True, key=f"bullet_main_{rk}", label_visibility="collapsed")

    if main_type == "뷸렛카메라박스":
        st.markdown("<div style='font-size:14px; margin-top:5px; margin-bottom:2px; color:#555;'>👇 상세 규격을 선택해 주세요</div>", unsafe_allow_html=True)
        sub_df = filtered_products[~filtered_products['제품명'].astype(str).str.contains('각도기', na=False)]
        p_list = sub_df.apply(utils.build_spec_string, axis=1).tolist()
        sel_prod = st.selectbox("상세 규격 선택", options=p_list, index=None, placeholder="규격을 선택해주세요", key=f"p_{rk}", label_visibility="collapsed")
        
        if sel_prod:
            idx = p_list.index(sel_prod)
            row = sub_df.iloc[idx]
            base_price = int(row['단가'])
            product_specs = f"뷸렛카메라박스 - {sel_prod}"
            is_main_ready = True
            img_val = row.get('이미지파일명')
            if pd.notna(img_val):
                preview_images.append(str(img_val).strip())
                combo_names = [str(img_val).strip(), "뷸렛카메라박스"]
            else:
                combo_names = ["뷸렛카메라박스"]
    
    elif main_type == "각도기":
        st.markdown("<div style='font-size:14px; margin-top:5px; margin-bottom:2px; color:#555;'>👇 각도기 종류를 선택해 주세요</div>", unsafe_allow_html=True)
        sub_df = filtered_products[filtered_products['제품명'].astype(str).str.contains('각도기', na=False)]
        p_list = sub_df.apply(utils.build_spec_string, axis=1).tolist()
        sel_prod = st.selectbox("각도기 선택", options=p_list, index=None, placeholder="각도기를 선택해주세요", key=f"ang_sub_{rk}", label_visibility="collapsed")
        
        if sel_prod:
            ang_opt = ""
            if "알루미늄" in sel_prod: ang_opt = "알루미늄 각도기"
            elif "스텐" in sel_prod: ang_opt = "스텐 각도기"
            elif "번호인식" in sel_prod: ang_opt = "번호인식 각도기"
            else: ang_opt = sel_prod
            
            price = 0
            if ang_opt == "알루미늄 각도기":
                df_opt = options_df[
                    (options_df['적용 카테고리'].astype(str).str.contains('CCTV폴', na=False)) & 
                    (options_df['옵션 구분(그룹명)'].astype(str).str.contains('카메라 부착 부품', na=False)) & 
                    (options_df['추가 선택-1'].astype(str).str.contains('알루미늄 각도기(추가)', regex=False, na=False))
                ]
                price = int(df_opt.iloc[0]['단가']) if not df_opt.empty else 8000
            elif ang_opt == "스텐 각도기":
                df_opt = options_df[
                    (options_df['적용 카테고리'].astype(str).str.contains('CCTV폴', na=False)) & 
                    (options_df['추가 선택-1'].astype(str).str.contains('스텐 각도기', na=False))
                ]
                price = int(df_opt.iloc[0]['단가']) if not df_opt.empty else 10000
            elif ang_opt == "번호인식 각도기":
                df_opt = options_df[
                    (options_df['적용 카테고리'].astype(str).str.contains('CCTV폴', na=False)) & 
                    (options_df['추가 선택-1'].astype(str).str.contains('번호인식 각도기', na=False))
                ]
                price = int(df_opt.iloc[0]['단가']) if not df_opt.empty else 25000
            else:
                idx = p_list.index(sel_prod)
                price = int(sub_df.iloc[idx]['단가'])
            
            base_price = price
            product_specs = f"각도기 - {sel_prod}"
            is_main_ready = True
            ang_kw = ang_opt.replace(" ", "")
            combo_names = [f"각도기-{ang_kw}", ang_opt, "각도기"]

    if is_main_ready:
        st.markdown("<h2>2. 옵션 선택</h2>", unsafe_allow_html=True)
        opt_col, img_col = st.columns([5.5, 4.5])
        with opt_col:
            utils.render_generic_groups(cat_no_space, options_df, rk, priced_options, zero_options, preview_images)
        valid_paths = utils.display_images(combo_names, priced_options, zero_options, preview_images, img_col, cat_no_space)
        return is_main_ready, base_price, product_specs, valid_paths, priced_options, zero_options
    return False, 0, "", [], [], []