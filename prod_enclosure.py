import streamlit as st
import pandas as pd
import utils

def render(filtered_products, options_df, rk, cat_no_space):
    is_main_ready, base_price, product_specs = False, 0, ""
    preview_images, priced_options, zero_options = [], [], []
    combo_names = []

    st.markdown("<div style='font-size:15px; font-weight:bold; color:#2e6c80; margin-bottom:5px;'>1️⃣ 규격 선택 (일반 함체)</div>", unsafe_allow_html=True)
    p_list = filtered_products.apply(utils.build_spec_string, axis=1).tolist()
    sel_prod = st.selectbox("상세 규격 선택", options=p_list, index=None, placeholder="규격을 선택해주세요", key=f"p_{rk}")
    
    if sel_prod:
        idx = p_list.index(sel_prod)
        row = filtered_products.iloc[idx]
        base_price = int(row['단가'])
        product_specs = f"{sel_prod}"
        is_main_ready = True
        if pd.notna(row.get('이미지파일명')): preview_images.append(str(row['이미지파일명']).strip())

    if is_main_ready:
        # 💡 [추가] 1. 함체 형태 선택 메뉴 (규격 바로 아래 배치)
        st.markdown("<div style='margin-top:15px; font-weight:bold; color:#555;'>👉 함체 형태</div>", unsafe_allow_html=True)
        shape_opts = ["기본형", "팬/환풍구형"]
        sel_shape = st.radio("함체 형태", shape_opts, horizontal=True, key=f"shape_{rk}", label_visibility="collapsed")
        
        # 함체 형태 단가 계산 (options.csv 연동)
        shape_mask = options_df['옵션 구분(그룹명)'].astype(str).str.replace(" ", "").str.contains('함체형태|형태', na=False)
        shape_df = options_df[shape_mask & (options_df['적용 카테고리'].astype(str).str.replace(" ", "").str.contains("함체", na=False))]
        
        if not shape_df.empty:
            clean_sel_shape = sel_shape.replace(" ", "")
            shape_p = 0
            for _, r_row in shape_df.iterrows():
                opt_name = str(r_row.get('추가 선택-1', '')).replace(" ", "")
                if opt_name in clean_sel_shape or clean_sel_shape in opt_name:
                    shape_p = int(r_row['단가'])
                    break
            if shape_p > 0:
                priced_options.append({"cart_name": f"함체형태: {sel_shape}", "display_name": f"형태: {sel_shape}", "unit_price": shape_p, "qty_per_main": 1, "total_per_main": shape_p, "group": "함체형태"})

        # 💡 [순서 변경] 2. 고정 방식 선택 메뉴 (옵션 메뉴 위로 끌어올림)
        st.markdown("<div style='margin-top:15px; font-weight:bold; color:#555;'>👉 고정 방식</div>", unsafe_allow_html=True)
        fix_opts = ["선택 안 함", "벽부형", "밴드형", "스텐(서스)밴드형", "자립식"]
        sel_fix = st.radio("고정 방식", fix_opts, index=0, horizontal=True, key=f"fix_{rk}", label_visibility="collapsed")
        
        fix_mask = options_df['옵션 구분(그룹명)'].astype(str).str.replace(" ", "").str.contains('고정방식', na=False)
        
        if sel_fix != "선택 안 함":
            p = 0
            final_fix_name = sel_fix
            fix_df = options_df[fix_mask & (options_df['적용 카테고리'].astype(str).str.replace(" ", "").str.contains("함체", na=False))]
            
            if sel_fix == "밴드형":
                st.markdown("<div style='font-size:14px; font-weight:bold; color:#555; margin-top:10px; margin-bottom:5px;'>👉 밴드형 파이프 지름 선택</div>", unsafe_allow_html=True)
                inch_opts = ["2.5인치", "3인치", "4인치", "5인치", "6인치"]
                sel_inch = st.radio("밴드형 파이프 지름", inch_opts, index=0, horizontal=True, key=f"inch_{rk}", label_visibility="collapsed")
                
                clean_inch_band = sel_inch.replace(" ", "")
                match = fix_df[
                    (fix_df['추가 선택-1'].astype(str).str.replace(" ", "", regex=False) == "밴드형") & 
                    (fix_df['추가 선택-2'].astype(str).str.replace(" ", "", regex=False) == clean_inch_band)
                ]
                if not match.empty:
                    p = int(match.iloc[0]['단가'])
                
                final_fix_name = f"밴드형 ({sel_inch})"
                
                st.markdown("<div style='font-size:14px; font-weight:bold; color:#555; margin-top:10px; margin-bottom:5px;'>📏 정확한 파이프 지름을 모를 경우 둘레(mm) 입력</div>", unsafe_allow_html=True)
                circ_str = st.text_input("둘레 입력", value="", key=f"circ_{rk}", label_visibility="collapsed", placeholder="숫자만 입력하세요")
                if circ_str and circ_str.strip().replace('.', '', 1).isdigit():
                    circ = float(circ_str.strip())
                    if circ > 0:
                        calc_dia_mm = circ / 3.14
                        inches_num = [2.5, 3, 4, 5, 6]
                        matched_inch = next((inc for inc in inches_num if calc_dia_mm < inc * 25.4 + 10), inches_num[-1])
                        disp_inch = int(matched_inch) if matched_inch.is_integer() else matched_inch
                        st.markdown(f"<div style='background-color:#e8f4f8; border-left:4px solid #2e6c80; padding:10px; margin-top:5px; font-size:14px; font-weight:bold; color:#2e6c80; border-radius:4px;'>💡 둘레 {circ}mm ≒ 지름 {calc_dia_mm:.1f}mm ▶ <span style='color:#d9534f;'>{disp_inch}인치 규격과 일치합니다.</span></div>", unsafe_allow_html=True)
            
            elif sel_fix == "자립식":
                st.markdown("<div style='font-size:14px; font-weight:bold; color:#555; margin-top:10px; margin-bottom:5px;'>👉 자립식 하부 파이프 규격</div>", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                sel_jarip_inch = c1.selectbox("파이프 직경", ["4인치", "5인치"], key=f"j_inch_{rk}")
                sel_jarip_hei = c2.selectbox("길이/규격", ["0.5", "1", "1.5"], key=f"j_hei_{rk}")
                
                clean_inch = sel_jarip_inch.replace(" ", "")
                target_hei_num = float(sel_jarip_hei)
                
                matched_price = 0
                for _, r_row in fix_df.iterrows():
                    c1_val = str(r_row.get('추가 선택-1', '')).replace(" ", "")
                    c2_val = str(r_row.get('추가 선택-2', '')).replace(" ", "")
                    c3_val = str(r_row.get('길이/규격', ''))
                    
                    try: excel_hei_num = float(c3_val.replace("M", "").replace(" ", ""))
                    except: excel_hei_num = -1.0
                        
                    if c1_val == "자립식" and c2_val == clean_inch and excel_hei_num == target_hei_num:
                        matched_price = int(r_row['단가'])
                        break
                        
                p = matched_price
                final_fix_name = f"자립식 ({sel_jarip_inch} / {sel_jarip_hei})"
                
            else:
                clean_sel_fix = sel_fix.replace(" ", "")
                match = fix_df[fix_df['추가 선택-1'].astype(str).str.replace(" ", "", regex=False) == clean_sel_fix]
                if not match.empty: p = int(match.iloc[0]['단가'])
                    
            priced_options.append({"cart_name": f"고정방식: {final_fix_name}", "display_name": f"고정 방식: {final_fix_name}", "unit_price": p, "qty_per_main": 1, "total_per_main": p, "group": "고정방식"})

        # 💡 [핵심] 이미지 파일명 조합 (요청하신 규칙 100% 적용)
        shape_img_str = "환풍구(팬)형" if "팬" in sel_shape or "환풍구" in sel_shape else "기본형"
        fix_img_str = sel_fix
        
        if sel_fix != "선택 안 함":
            combo_names.append(f"함체-{shape_img_str}-{fix_img_str}")
        else:
            combo_names.append(f"함체-{shape_img_str}")
        combo_names.append("함체") # (못 찾을 경우 대비한 기본 보험 폴백)

        # 💡 3. 추가 옵션 선택 (고정방식과 함체형태 선택이 끝난 아래쪽에 렌더링)
        st.markdown("<h2 style='margin-top:25px;'>2. 추가 옵션 선택</h2>", unsafe_allow_html=True)
        opt_col, img_col = st.columns([5.5, 4.5])
        with opt_col:
            # 밖으로 빼낸 함체형태와 고정방식은 제외하고 나머지 옵션(키, 도장 등)만 렌더링
            exc_mask = options_df['옵션 구분(그룹명)'].astype(str).str.replace(" ", "").str.contains('고정방식|함체형태|형태', na=False)
            rem_options_df = options_df[~exc_mask]
            utils.render_generic_groups(cat_no_space, rem_options_df, rk, priced_options, zero_options, preview_images)

        valid_paths = utils.display_images(combo_names, priced_options, zero_options, preview_images, img_col, cat_no_space)
        return is_main_ready, base_price, product_specs, valid_paths, priced_options, zero_options

    return False, 0, "", [], [], []