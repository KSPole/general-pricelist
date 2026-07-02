import streamlit as st
import pandas as pd
import utils

def render(filtered_products, options_df, rk, cat_no_space):
    is_main_ready, base_price, product_specs = False, 0, ""
    preview_images, priced_options, zero_options, selected_cam_parts = [], [], [], []

    st.markdown("<div style='font-size:15px; font-weight:bold; color:#2e6c80; margin-bottom:5px;'>1️⃣ 규격 및 상세 정보 입력</div>", unsafe_allow_html=True)
    p_list = filtered_products.apply(utils.build_spec_string, axis=1).tolist()
    sel_prod = st.selectbox("상세 규격 선택", options=p_list, index=None, placeholder="규격을 선택해주세요", key=f"p_{rk}")

    if sel_prod:
        st.markdown("<div style='background-color:#f9f9f9; padding:15px; border-radius:8px; margin-top:10px; border:1px solid #e0e0e0;'>", unsafe_allow_html=True)
        pipe_opt = st.radio("👉 체결할 파이프 지름 선택", ["2인치", "2.5인치", "3인치", "4인치"], index=0, horizontal=True, key=f"cctv_pipe_{rk}")
        st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
        print_text = st.text_input("👉 인쇄할 문구 직접 입력 (선택)", placeholder="예: 방범용 CCTV 작동중", key=f"cctv_txt_{rk}")
        st.markdown("</div>", unsafe_allow_html=True)
        
        idx = p_list.index(sel_prod)
        row = filtered_products.iloc[idx]
        base_price = int(row['단가'])
        
        product_specs = f"{sel_prod} / 체결파이프: {pipe_opt}"
        if print_text: product_specs += f" / 인쇄문구: {print_text}"
        is_main_ready = True
        
        img_val = row.get('이미지파일명')
        if pd.notna(img_val):
            preview_images.append(str(img_val).strip())
            combo_names = [str(img_val).strip(), "CCTV작동중판넬"]
        else:
            combo_names = ["CCTV작동중판넬"]

    if is_main_ready:
        st.markdown("<h2>2. 옵션 선택</h2>", unsafe_allow_html=True)
        opt_col, img_col = st.columns([5.5, 4.5])
        with opt_col:
            utils.render_generic_groups(cat_no_space, options_df, rk, priced_options, zero_options, preview_images)
        valid_paths = utils.display_images(combo_names, priced_options, zero_options, preview_images, img_col, cat_no_space)
        return is_main_ready, base_price, product_specs, valid_paths, priced_options, zero_options
    return False, 0, "", [], [], []