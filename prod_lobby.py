import streamlit as st
import pandas as pd
import utils

def render(filtered_products, options_df, rk, cat_no_space):
    is_main_ready, base_price, product_specs = False, 0, ""
    preview_images, priced_options, zero_options, selected_cam_parts = [], [], [], []

    st.markdown("<div style='font-size:15px; font-weight:bold; color:#2e6c80; margin-bottom:5px;'>1️⃣ 사이즈 및 정보 입력</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    w_val = c1.text_input("👉 가로 (mm)", placeholder="숫자만 입력", key=f"lobby_w_{rk}")
    h_val = c2.text_input("👉 세로 (mm)", placeholder="숫자만 입력", key=f"lobby_h_{rk}")
    model_val = st.text_input("👉 로비폰 제조사 / 모델명", placeholder="예: 코맥스 DRC-40K", key=f"lobby_m_{rk}")
    bend_opt = st.radio("사방 절곡 여부", ["사방 절곡 없음", "사방 절곡 있음"], index=0, horizontal=True, key=f"lobby_b_{rk}")

    if w_val and h_val:
        base_price = int(filtered_products.iloc[0]['단가']) if not filtered_products.empty else 0
        product_specs = f"가로 {w_val}mm x 세로 {h_val}mm"
        if model_val: product_specs += f" / 모델명: {model_val}"
        product_specs += f" / {bend_opt}"
        is_main_ready = True
        
        if bend_opt == "사방 절곡 없음":
            preview_images.append("로비폰보강판-사방절곡없음")
            combo_names = ["로비폰보강판-사방절곡없음", "로비폰보강판"]
        else:
            preview_images.append("로비폰보강판-사방절곡있음")
            combo_names = ["로비폰보강판-사방절곡있음", "로비폰보강판"]

    if is_main_ready:
        st.markdown("<h2>2. 옵션 선택</h2>", unsafe_allow_html=True)
        opt_col, img_col = st.columns([5.5, 4.5])
        with opt_col:
            utils.render_generic_groups(cat_no_space, options_df, rk, priced_options, zero_options, preview_images)
        valid_paths = utils.display_images(combo_names, priced_options, zero_options, preview_images, img_col, cat_no_space)
        return is_main_ready, base_price, product_specs, valid_paths, priced_options, zero_options
    return False, 0, "", [], [], []