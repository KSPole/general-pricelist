import streamlit as st
import pandas as pd
import utils

def render(filtered_products, options_df, rk, cat_no_space):
    is_main_ready, base_price, product_specs = False, 0, ""
    preview_images, priced_options, zero_options, selected_cam_parts = [], [], [], []

    st.markdown("<div style='font-size:15px; font-weight:bold; color:#2e6c80; margin-bottom:5px;'>1️⃣ 규격 선택</div>", unsafe_allow_html=True)
    p_list = filtered_products.apply(utils.build_spec_string, axis=1).tolist()
    sel_prod = st.selectbox("상세 규격 선택", options=p_list, index=None, placeholder="규격을 선택해주세요", key=f"p_{rk}")

    if sel_prod:
        idx = p_list.index(sel_prod)
        row = filtered_products.iloc[idx]
        base_price = int(row['단가'])
        product_specs = f"{sel_prod}"
        is_main_ready = True
        
        img_val = row.get('이미지파일명')
        if pd.notna(img_val):
            preview_images.append(str(img_val).strip())

    if is_main_ready:
        st.markdown("<h2>2. 옵션 선택</h2>", unsafe_allow_html=True)
        opt_col, img_col = st.columns([5.5, 4.5])
        
        with opt_col:
            # 👉 1. 함체 형태 선택
            st.markdown("<div class='option-group-title'>📁 함체 형태</div>", unsafe_allow_html=True)
            box_opts = ["기본형(사방 막힘)", "환풍구(팬)형"]
            box_type = st.radio("함체 형태", box_opts, index=0, horizontal=True, key=f"box_type_{rk}", label_visibility="collapsed")
            
            b_type_val = "기본형" if "기본형" in box_type else "환풍구(팬)형"
            if "환풍구" in box_type:
                type_row = options_df[(options_df['적용 카테고리'].astype(str).str.contains('함체', na=False)) & (options_df['추가 선택-1'].astype(str).str.contains(b_type_val[:3], na=False))]
                type_price = int(type_row.iloc[0]['단가']) if not type_row.empty else 80000
                priced_options.append({"cart_name": b_type_val, "display_name": f"형태: {b_type_val}", "unit_price": type_price, "qty_per_main": 1, "total_per_main": type_price, "group": "함체형태"})
            
            # 👉 2. 고정 방식 선택
            st.markdown("<div class='option-group-title'>📁 고정 방식</div>", unsafe_allow_html=True)
            fix_opts = ["선택 안 함", "벽부형", "밴드형", "스텐(서스)밴드형", "자립식"]
            box_fix = st.radio("고정 방식", fix_opts, index=0, horizontal=True, key=f"box_fix_{rk}", label_visibility="collapsed")
            
            if box_fix != "선택 안 함":
                fix_price = 0
                if box_fix == "자립식":
                    st.markdown("<div class='option-group-title'>📁 자립식 하부 파이프 규격</div>", unsafe_allow_html=True)
                    c_p1, c_p2 = st.columns(2)
                    pipe_inch = c_p1.selectbox("파이프 직경", ["4인치", "5인치"], index=0, key=f"pipe_inch_{rk}")
                    pipe_height = c_p2.selectbox("파이프 높이", ["0.5M", "1M", "1.5M"], index=0, key=f"pipe_height_{rk}")
                    cart_name_fix = f"자립식 파이프 ({pipe_inch} {pipe_height})"
                    display_name_fix = f"고정방식: 자립식({pipe_inch} {pipe_height})"
                    
                    for _, r in options_df[options_df['적용 카테고리'].astype(str).str.contains('함체', na=False)].iterrows():
                        row_text = (str(r.get('옵션 구분(그룹명)', '')) + str(r.get('추가 선택-1', ''))).replace(" ", "")
                        h_val = pipe_height.replace("M", "")
                        if "자립" in row_text and pipe_inch[:1] in row_text and (h_val in row_text or ("1" if h_val=="1.0" else h_val) in row_text):
                            fix_price = int(r['단가'])
                            break
                else:
                    cart_name_fix = box_fix
                    display_name_fix = f"고정 방식: {box_fix}"
                    for _, r in options_df[options_df['적용 카테고리'].astype(str).str.replace(" ","").str.contains('함체', na=False)].iterrows():
                        opt_name = str(r['추가 선택-1']).replace(" ", "")
                        if box_fix == "밴드형" and "스텐" not in opt_name and "서스" not in opt_name and "밴드" in opt_name: 
                            fix_price = int(r['단가']); break
                        elif box_fix == "스텐(서스)밴드형" and ("스텐" in opt_name or "서스" in opt_name): 
                            fix_price = int(r['단가']); break
                        elif box_fix == "벽부형" and "벽부" in opt_name: 
                            fix_price = int(r['단가']); break
                
                priced_options.append({"cart_name": cart_name_fix, "display_name": display_name_fix, "unit_price": fix_price, "qty_per_main": 1, "total_per_main": fix_price, "group": "고정방식"})
            
            # 👉 3. 추가 홀 가공
            st.markdown("<div class='option-group-title'>📁 추가 홀 가공</div>", unsafe_allow_html=True)
            st.info("💡 추가 홀 가공에 따른 금액이 변동될 수 있습니다. (별도 안내)")
            hole_val = st.text_input("👉 가공이 필요한 위치/수량, 인입 방식 등을 적어주세요 (선택사항)", key=f"hole_{rk}")
            if hole_val: 
                zero_options.append({"cart_name": f"홀 가공 요청: {hole_val}", "display_name": f"홀 가공: {hole_val} (금액 변동 가능)"})
            
            # 공통 부가 옵션이 있을 경우 렌더링
            utils.render_generic_groups(cat_no_space, options_df, rk, priced_options, zero_options, preview_images)

        # 👉 4. 지시하신 이미지 파일명 논리 적용 ("함체-기본형-벽부형" 등)
        combo_names = []
        if box_fix != "선택 안 함":
            combo_names.append(f"함체-{b_type_val}-{box_fix}")
        combo_names.append(f"함체-{b_type_val}")
        combo_names.append("함체")
        
        valid_paths = utils.display_images(combo_names, priced_options, zero_options, preview_images, img_col, cat_no_space)
        return is_main_ready, base_price, product_specs, valid_paths, priced_options, zero_options

    return False, 0, "", [], [], []