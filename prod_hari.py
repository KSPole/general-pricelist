import streamlit as st
import pandas as pd
import utils
import re

def render(filtered_products, options_df, rk, cat_no_space):
    is_main_ready, base_price, product_specs = False, 0, ""
    preview_images, priced_options, zero_options, selected_cam_parts = [], [], [], []
    
    # 1. 상세 규격 선택 (하리형 브라켓 일반 규격)
    st.markdown("<div style='font-size:15px; font-weight:bold; color:#2e6c80; margin-bottom:5px;'>1️⃣ 상세 규격 선택</div>", unsafe_allow_html=True)
    p_list = filtered_products.apply(utils.build_spec_string, axis=1).tolist()
    sel_prod = st.selectbox("상세 규격 선택", options=p_list, index=None, placeholder="규격을 선택해주세요", key=f"p_{rk}", label_visibility="collapsed")
    
    if sel_prod:
        idx = p_list.index(sel_prod)
        row = filtered_products.iloc[idx]
        base_price, product_specs, is_main_ready = int(row['단가']), f"{sel_prod}", True
        if pd.notna(row.get('이미지파일명')): preview_images.append(str(row['이미지파일명']).strip())

    if is_main_ready:
        st.markdown("<h2>2. 옵션 선택</h2>", unsafe_allow_html=True)
        opt_col, img_col = st.columns([5.5, 4.5])
        with opt_col:
            # 👉 수정 1: "T형" 텍스트 간소화
            st.markdown("<div class='option-group-title'>📁 기본형 / T형 선택</div>", unsafe_allow_html=True)
            brk_opts = ["기본형(박스형)", "T형"]
            brk_shape = st.radio("기본형 / T형 선택", brk_opts, index=0, horizontal=True, key=f"brk_shape_{rk}", label_visibility="collapsed")
            
            if "T형" in brk_shape:
                t_row = options_df[(options_df['적용 카테고리'].astype(str).str.replace(" ", "") == cat_no_space) & (options_df['추가 선택-1'].astype(str).str.contains("T형", na=False))]
                t_price = int(t_row.iloc[0]['단가']) if not t_row.empty else 25000
                priced_options.append({"cart_name": "T형", "display_name": "형태: T형", "unit_price": t_price, "qty_per_main": 1, "total_per_main": t_price, "group": "브라켓형태"})
            
            # 👉 수정 2: 카메라 형태 "선택 안 함" 삭제 & 뷸렛카메라 기본 선택
            st.markdown("<div class='option-group-title'>📁 카메라 형태</div>", unsafe_allow_html=True)
            cam_opts = ["뷸렛카메라", "돔카메라", "하우징카메라"]
            cam_type = st.radio("카메라 형태", cam_opts, index=0, horizontal=True, key=f"cam_other_{rk}", label_visibility="collapsed")
            
            box_height = ""
            if cam_type in ["뷸렛카메라", "돔카메라"]:
                # 👉 수정 3: 박스 사이즈 "선택 안 함" 삭제 & 60mm 기본 선택
                st.markdown("<div class='option-group-title'>📁 카메라박스 사이즈</div>", unsafe_allow_html=True)
                box_opts = ["높이 60mm", "높이 120mm"]
                box_height = st.radio("카메라박스 사이즈", box_opts, index=0, horizontal=True, key=f"box_hei_{rk}", label_visibility="collapsed")
                
                h_row = options_df[(options_df['적용 카테고리'].astype(str).str.replace(" ", "") == cat_no_space) & (options_df['추가 선택-1'].astype(str).str.contains(box_height.replace("높이 ", ""), na=False))]
                h_price = int(h_row.iloc[0]['단가']) if not h_row.empty else 5000
                priced_options.append({"cart_name": box_height, "display_name": f"박스 높이: {box_height}", "unit_price": h_price, "qty_per_main": 1, "total_per_main": h_price, "group": "박스사이즈"})
            
            elif cam_type == "하우징카메라":
                zero_options.append({"cart_name": "각도기(기본)", "display_name": "각도기(기본 포함)"})
            
            # 기타 옵션 렌더링
            utils.render_generic_groups(cat_no_space, options_df, rk, priced_options, zero_options, preview_images)

        # 지능형 이미지 파일명 생성 유지
        combo_names = []
        base_brk = "하리형브라켓"
        
        t_prefix = "T형-" if "T형" in brk_shape else ""
        
        box_kw = ""
        if box_height:
            if "60mm" in box_height:
                box_kw = "60"
            elif "120mm" in box_height:
                box_kw = "120"
                
        if cam_type == "뷸렛카메라":
            if box_kw: combo_names.append(f"{base_brk}-{t_prefix}뷸렛-{box_kw}")
            combo_names.append(f"{base_brk}-{t_prefix}뷸렛")
            
        elif cam_type == "돔카메라":
            if box_kw: combo_names.append(f"{base_brk}-{t_prefix}돔-{box_kw}")
            combo_names.append(f"{base_brk}-{t_prefix}돔")
            
        elif cam_type == "하우징카메라":
            combo_names.append(f"{base_brk}-{t_prefix}하우징")
            
        if "T형" in brk_shape:
            combo_names.append(f"{base_brk}-T형")
        
        combo_names.append(base_brk)
        combo_names.append(cat_no_space)
        
        combo_names = list(dict.fromkeys(combo_names))

        valid_paths = utils.display_images(combo_names, priced_options, zero_options, preview_images, img_col, cat_no_space)
        return is_main_ready, base_price, product_specs, valid_paths, priced_options, zero_options

    return False, 0, "", [], [], []