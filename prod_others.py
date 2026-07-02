import streamlit as st
import pandas as pd
import utils

def render(filtered_products, options_df, rk, cat_no_space):
    is_main_ready, base_price, product_specs = False, 0, ""
    preview_images, priced_options, zero_options, selected_cam_parts = [], [], [], []

    # 1. 레이스웨이 브라켓
    if "레이스웨이브라켓" in cat_no_space:
        st.markdown("<div style='font-size:15px; font-weight:bold; color:#2e6c80; margin-bottom:5px;'>1️⃣ 상세 규격 및 레이스웨이 규격 입력</div>", unsafe_allow_html=True)
        p_list = filtered_products.apply(utils.build_spec_string, axis=1).tolist()
        sel_prod = st.selectbox("상세 규격 선택", options=p_list, index=None, placeholder="규격을 선택해주세요", key=f"p_{rk}")
        
        if sel_prod:
            st.markdown("<div style='background-color:#f9f9f9; padding:10px; border-radius:5px; margin-top:10px;'>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            w_rw = c1.text_input("👉 레이스웨이 가로 (mm)", placeholder="예: 100", key=f"rw_w_{rk}")
            h_rw = c2.text_input("👉 레이스웨이 세로 (mm)", placeholder="예: 50", key=f"rw_h_{rk}")
            st.markdown("</div>", unsafe_allow_html=True)
            
            idx = p_list.index(sel_prod)
            row = filtered_products.iloc[idx]
            base_price = int(row['단가'])
            product_specs = f"{sel_prod} / 레이스웨이규격: 가로{w_rw}mm x 세로{h_rw}mm"
            is_main_ready = True
            if pd.notna(row.get('이미지파일명')): preview_images.append(str(row['이미지파일명']).strip())

    # 2. 함체 (옵션 복구)
    elif "함체" in cat_no_space:
        st.markdown("<div style='font-size:15px; font-weight:bold; color:#2e6c80; margin-bottom:5px;'>1️⃣ 규격 선택</div>", unsafe_allow_html=True)
        p_list = filtered_products.apply(utils.build_spec_string, axis=1).tolist()
        sel_prod = st.selectbox("상세 규격 선택", options=p_list, index=None, placeholder="규격을 선택해주세요", key=f"p_{rk}")
        
        if sel_prod:
            idx = p_list.index(sel_prod)
            row = filtered_products.iloc[idx]
            base_price = int(row['단가'])
            product_specs = f"{sel_prod}"
            is_main_ready = True
            
            # 여기서 utils.render_generic_groups를 호출하면 엑셀의 옵션 데이터를 불러오므로
            # 고정 방식(벽부/밴드/자립 등)이 자동으로 복구됩니다.
            if pd.notna(row.get('이미지파일명')): preview_images.append(str(row['이미지파일명']).strip())

    # 3. 기타 (나머지)
    else:
        # 기존 기타 처리 로직 동일
        p_list = filtered_products.apply(utils.build_spec_string, axis=1).tolist()
        sel_prod = st.selectbox("상세 규격 선택", options=p_list, index=None, placeholder="규격을 선택해주세요", key=f"p_{rk}")
        if sel_prod:
            idx = p_list.index(sel_prod)
            row = filtered_products.iloc[idx]
            base_price = int(row['단가'])
            product_specs = f"{sel_prod}"
            is_main_ready = True

    # 공통 옵션 렌더링 및 출력
    if is_main_ready:
        st.markdown("<h2>2. 옵션 선택</h2>", unsafe_allow_html=True)
        opt_col, img_col = st.columns([5.5, 4.5])
        with opt_col:
            utils.render_generic_groups(cat_no_space, options_df, rk, priced_options, zero_options, preview_images)
        valid_paths = utils.display_images([cat_no_space], priced_options, zero_options, preview_images, img_col, cat_no_space)
        return is_main_ready, base_price, product_specs, valid_paths, priced_options, zero_options

    return False, 0, "", [], [], []