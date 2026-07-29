import streamlit as st
import pandas as pd
import utils

def render(filtered_products, options_df, rk, cat_no_space):
    is_main_ready, base_price, product_specs = False, 0, ""
    preview_images, priced_options, zero_options, selected_cam_parts = [], [], [], []

    st.markdown("<div style='font-size:15px; font-weight:bold; color:#2e6c80; margin-bottom:5px;'>1️⃣ 규격 선택</div>", unsafe_allow_html=True)
    
    # 💡 수정 포인트: 화면 드롭다운에 표시할 때는 엑셀의 "주문형앙카베이스"를 빼고(중복 방지) 기성품만 남깁니다.
    display_df = filtered_products[~filtered_products['제품명'].astype(str).str.replace(" ", "").str.contains("주문형앙카베이스", na=False)]
    
    p_list = display_df.apply(utils.build_spec_string, axis=1).tolist()
    
    # 그리고 우리가 만든 직접 입력 창 전용 메뉴를 맨 끝에 딱 하나만 추가합니다.
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
            # 단가 추출은 걸러내지 않은 원본 데이터(filtered_products)에서 안전하게 가져옵니다.
            match_df = filtered_products[filtered_products['제품명'].astype(str).str.replace(" ", "").str.contains("주문형앙카베이스", na=False)]
            
            if not match_df.empty:
                base_price = int(match_df.iloc[0]['단가'])
            else:
                base_price = 0
                
            product_specs = f"주문형 앙카베이스 / 앙카간격: 가로 {w_hole}mm x 세로 {h_hole}mm"
            is_main_ready = True
            combo_names = ["주문형 앙카베이스"]
            
    elif sel_prod:
        # 💡 일반 규격을 선택했을 때는 display_df를 기준으로 순서를 찾아 단가 어긋남 버그를 원천 차단합니다.
        idx = p_list.index(sel_prod)
        row = display_df.iloc[idx]
        base_price = int(row['단가'])
        product_specs = f"{sel_prod}"
        is_main_ready = True
        
        # 기성품 앙카베이스는 파일명을 "앙카베이스"로 고정 지정
        combo_names = ["앙카베이스"]

    if is_main_ready:
        st.markdown("<h2>2. 옵션 선택</h2>", unsafe_allow_html=True)
        opt_col, img_col = st.columns([5.5, 4.5])
        with opt_col:
            utils.render_generic_groups(cat_no_space, options_df, rk, priced_options, zero_options, preview_images)
        valid_paths = utils.display_images(combo_names, priced_options, zero_options, preview_images, img_col, cat_no_space)
        return is_main_ready, base_price, product_specs, valid_paths, priced_options, zero_options
        
    return False, 0, "", [], [], []