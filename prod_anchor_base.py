import streamlit as st
import pandas as pd
import utils

def render(filtered_products, options_df, rk, cat_no_space):
    is_main_ready, base_price, product_specs = False, 0, ""
    preview_images, priced_options, zero_options, selected_cam_parts = [], [], [], []

    st.markdown("<div style='font-size:15px; font-weight:bold; color:#2e6c80; margin-bottom:5px;'>1️⃣ 규격 선택</div>", unsafe_allow_html=True)
    p_list = filtered_products.apply(utils.build_spec_string, axis=1).tolist()
    p_list.append("주문형 앙카베이스 (직접 입력)") 
    sel_prod = st.selectbox("상세 규격 선택", options=p_list, index=None, placeholder="규격을 선택해주세요", key=f"p_{rk}")

    if sel_prod == "주문형 앙카베이스 (직접 입력)":
        st.markdown("<div style='background-color:#f9f9f9; padding:10px; border-radius:5px;'>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:14px; font-weight:bold; color:#d9534f; margin-bottom:8px;'>👇 주문형 앙카 간격 입력</div>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        w_hole = c1.text_input("👉 가로 간격 (mm)", placeholder="예: 200", key=f"ab_w_{rk}")
        h_hole = c2.text_input("👉 세로 간격 (mm)", placeholder="예: 200", key=f"ab_h_{rk}")
        st.markdown("</div>", unsafe_allow_html=True)
        
        if w_hole and h_hole:
            base_price = 0
            for _, r in filtered_products.iterrows():
                if "주문형" in str(r.get('제품명', '')):
                    base_price = int(r.get('단가', 0))
                    break
            product_specs = f"주문형 앙카베이스 / 앙카간격: 가로 {w_hole}mm x 세로 {h_hole}mm"
            is_main_ready = True
            combo_names = ["앙카베이스-주문형", "앙카베이스"]
            
    elif sel_prod:
        idx = p_list.index(sel_prod)
        row = filtered_products.iloc[idx]
        base_price = int(row['단가'])
        product_specs = f"{sel_prod}"
        is_main_ready = True
        img_val = row.get('이미지파일명')
        if pd.notna(img_val):
            preview_images.append(str(img_val).strip())
            combo_names = [str(img_val).strip(), "앙카베이스"]
        else:
            combo_names = ["앙카베이스"]

    if is_main_ready:
        st.markdown("<h2>2. 옵션 선택</h2>", unsafe_allow_html=True)
        opt_col, img_col = st.columns([5.5, 4.5])
        with opt_col:
            utils.render_generic_groups(cat_no_space, options_df, rk, priced_options, zero_options, preview_images)
        valid_paths = utils.display_images(combo_names, priced_options, zero_options, preview_images, img_col, cat_no_space)
        return is_main_ready, base_price, product_specs, valid_paths, priced_options, zero_options
    return False, 0, "", [], [], []