import streamlit as st
import pandas as pd
import utils
import re

def render(filtered_products, options_df, rk, cat_no_space):
    is_main_ready, base_price, product_specs = False, 0, ""
    preview_images, priced_options, zero_options, selected_cam_parts = [], [], [], []
    combo_names = []

    # 1. 레이스웨이 브라켓
    if "레이스웨이브라켓" in cat_no_space or "레이스웨이" in cat_no_space:
        st.markdown("<div style='font-size:15px; font-weight:bold; color:#2e6c80; margin-bottom:5px;'>1️⃣ 레이스웨이 브라켓 형태 선택</div>", unsafe_allow_html=True)
        p_list = filtered_products.apply(utils.build_spec_string, axis=1).tolist()
        
        # '높이'를 '카메라박스 높이'로 변경
        p_list = [p.replace("높이", "카메라박스 높이") for p in p_list]
        sel_prod = st.selectbox("상세 규격 선택", options=p_list, index=None, placeholder="규격을 선택해주세요", key=f"p_{rk}")
        
        if sel_prod:
            st.markdown("<div style='background-color:#f9f9f9; padding:10px; border-radius:5px; margin-top:10px;'>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            w_rw = c1.text_input("👉 레이스웨이 가로 (mm)", placeholder="예: 100", key=f"rw_w_{rk}")
            h_rw = c2.text_input("👉 레이스웨이 카메라박스 높이 (mm)", placeholder="예: 50", key=f"rw_h_{rk}")
            st.markdown("</div>", unsafe_allow_html=True)
            
            idx = p_list.index(sel_prod)
            row = filtered_products.iloc[idx]
            base_price = int(row['단가'])
            product_specs = f"{sel_prod} / 레이스웨이규격: 가로{w_rw}mm x 카메라박스 높이{h_rw}mm"
            is_main_ready = True
            
            # 레이스웨이 4가지 이미지 파일명 완벽 분기 처리
            r_type = "하부형" if "하부" in sel_prod else ("측면형" if "측면" in sel_prod else "")
            r_hei = "120mm" if "120" in sel_prod else ("60mm" if "60" in sel_prod else "")
            
            if r_type and r_hei:
                combo_names = [f"레이스웨이브라켓-{r_type}-{r_hei}", "레이스웨이브라켓"]
            elif pd.notna(row.get('이미지파일명')):
                preview_images.append(str(row['이미지파일명']).strip())
                combo_names = [str(row['이미지파일명']).strip(), "레이스웨이브라켓"]
            else:
                combo_names = ["레이스웨이브라켓"]

    # 2. 함체
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
            if pd.notna(row.get('이미지파일명')): preview_images.append(str(row['이미지파일명']).strip())
            combo_names = ["함체"]

    # 3. 기타 (나머지)
    else:
        p_list = filtered_products.apply(utils.build_spec_string, axis=1).tolist()
        sel_prod = st.selectbox("상세 규격 선택", options=p_list, index=None, placeholder="규격을 선택해주세요", key=f"p_{rk}")
        if sel_prod:
            idx = p_list.index(sel_prod)
            row = filtered_products.iloc[idx]
            base_price = int(row['단가'])
            product_specs = f"{sel_prod}"
            is_main_ready = True
            if pd.notna(row.get('이미지파일명')): preview_images.append(str(row['이미지파일명']).strip())
            combo_names = [cat_no_space]

    # 공통 옵션 렌더링 및 출력
    if is_main_ready:
        st.markdown("<h2>2. 옵션 선택</h2>", unsafe_allow_html=True)
        opt_col, img_col = st.columns([5.5, 4.5])
        with opt_col:
            
            if "함체" in cat_no_space:
                # 1. 엑셀 데이터 중 '고정방식'을 제외한 나머지(함체 형태 등)만 먼저 렌더링
                fix_mask = options_df['옵션 구분(그룹명)'].astype(str).str.replace(" ", "").str.contains('고정방식', na=False)
                rem_options_df = options_df[~fix_mask]
                utils.render_generic_groups(cat_no_space, rem_options_df, rk, priced_options, zero_options, preview_images)

                # 2. 고정 방식 커스텀 출력
                st.markdown("<div class='option-group-title'>📁 고정 방식</div>", unsafe_allow_html=True)
                fix_opts = ["선택 안 함", "벽부형", "밴드형", "스텐(서스)밴드형", "자립식"]
                sel_fix = st.radio("고정 방식", fix_opts, index=0, horizontal=True, key=f"fix_{rk}", label_visibility="collapsed")
                
                if sel_fix != "선택 안 함":
                    p = 0
                    final_fix_name = sel_fix
                    
                    # 함체 카테고리의 고정방식 데이터만 추출
                    fix_df = options_df[fix_mask & (options_df['적용 카테고리'].astype(str).str.replace(" ", "").str.contains("함체", na=False))]
                    
                    # 💡 1. 밴드형 로직 (contains가 아닌 '==' 으로 완벽 일치 검색)
                    if sel_fix == "밴드형":
                        st.markdown("<div style='font-size:14px; font-weight:bold; color:#555; margin-top:10px; margin-bottom:5px;'>👉 밴드형 파이프 지름 선택</div>", unsafe_allow_html=True)
                        inch_opts = ["2.5인치", "3인치", "4인치", "5인치", "6인치"]
                        sel_inch = st.radio("밴드형 파이프 지름", inch_opts, index=0, horizontal=True, key=f"inch_{rk}", label_visibility="collapsed")
                        
                        clean_inch_band = sel_inch.replace(" ", "")
                        
                        # "5인치"가 "2.5인치"를 검색하지 못하도록 완전히 똑같은지(==) 검사합니다.
                        match = fix_df[
                            (fix_df['추가 선택-1'].astype(str).str.replace(" ", "", regex=False) == "밴드형") & 
                            (fix_df['추가 선택-2'].astype(str).str.replace(" ", "", regex=False) == clean_inch_band)
                        ]
                        
                        if not match.empty:
                            p = int(match.iloc[0]['단가'])
                        else:
                            p = 0
                        
                        final_fix_name = f"밴드형 ({sel_inch})"
                        
                        st.markdown("<div style='font-size:14px; font-weight:bold; color:#555; margin-top:10px; margin-bottom:5px;'>📏 정확한 파이프 지름을 모를 경우 둘레(mm) 입력</div>", unsafe_allow_html=True)
                        circ_str = st.text_input("둘레 입력", value="", key=f"circ_{rk}", label_visibility="collapsed", placeholder="숫자만 입력하세요")
                        
                        if circ_str and circ_str.strip().replace('.', '', 1).isdigit():
                            circ = float(circ_str.strip())
                            if circ > 0:
                                calc_dia_mm = circ / 3.14
                                inches_num = [2.5, 3, 4, 5, 6]
                                matched_inch = None
                                for inc in inches_num:
                                    base_mm = inc * 25.4
                                    if calc_dia_mm < base_mm + 10:
                                        matched_inch = inc
                                        break
                                if matched_inch is None: matched_inch = inches_num[-1]
                                disp_inch = int(matched_inch) if matched_inch.is_integer() else matched_inch
                                
                                st.markdown(f"<div style='background-color:#e8f4f8; border-left:4px solid #2e6c80; padding:10px; margin-top:5px; font-size:14px; font-weight:bold; color:#2e6c80; border-radius:4px;'>💡 둘레 {circ}mm ≒ 지름 {calc_dia_mm:.1f}mm ▶ <span style='color:#d9534f;'>{disp_inch}인치 규격과 일치합니다.</span></div>", unsafe_allow_html=True)
                    
                    # 💡 2. 자립식 로직 (숫자로 변환하여 1.0과 1.5를 명확히 구분)
                    elif sel_fix == "자립식":
                        st.markdown("<div style='font-size:14px; font-weight:bold; color:#555; margin-top:10px; margin-bottom:5px;'>👉 자립식 하부 파이프 규격</div>", unsafe_allow_html=True)
                        c1, c2 = st.columns(2)
                        sel_jarip_inch = c1.selectbox("파이프 직경", ["4인치", "5인치"], key=f"j_inch_{rk}")
                        sel_jarip_hei = c2.selectbox("파이프 높이", ["0.5M", "1M", "1.5M"], key=f"j_hei_{rk}")
                        
                        clean_inch = sel_jarip_inch.replace(" ", "")
                        target_hei_num = float(sel_jarip_hei.replace("M", "").replace(" ", ""))
                        
                        matched_price = 0
                        # 엑셀 데이터를 한 줄씩 읽어서 정확하게 일치하는지 숫자로 수학적 검사를 합니다.
                        for _, r_row in fix_df.iterrows():
                            c1_val = str(r_row.get('추가 선택-1', '')).replace(" ", "")
                            c2_val = str(r_row.get('추가 선택-2', '')).replace(" ", "")
                            c3_val = str(r_row.get('길이/규격', ''))
                            
                            try:
                                excel_hei_num = float(c3_val.replace("M", "").replace(" ", ""))
                            except:
                                excel_hei_num = -1.0
                                
                            # 글자가 포함(contains)된 게 아니라, 완벽히 똑같을 때(==)만 단가를 가져옵니다.
                            if c1_val == "자립식" and c2_val == clean_inch and excel_hei_num == target_hei_num:
                                matched_price = int(r_row['단가'])
                                break
                                
                        p = matched_price
                        final_fix_name = f"자립식 ({sel_jarip_inch} {sel_jarip_hei})"
                        
                    # 💡 3. 벽부형, 스텐(서스)밴드형 등 기타 방식
                    else:
                        clean_sel_fix = sel_fix.replace(" ", "")
                        match = fix_df[fix_df['추가 선택-1'].astype(str).str.replace(" ", "", regex=False) == clean_sel_fix]
                        if not match.empty:
                            p = int(match.iloc[0]['단가'])
                        else:
                            p = 0
                            
                    priced_options.append({"cart_name": f"고정방식: {final_fix_name}", "display_name": f"고정 방식: {final_fix_name}", "unit_price": p, "qty_per_main": 1, "total_per_main": p, "group": "고정방식"})

            else:
                # 함체가 아닌 일반 제품들의 옵션 렌더링
                utils.render_generic_groups(cat_no_space, options_df, rk, priced_options, zero_options, preview_images)
            
            # 우측에 표출되는 3D 도면 이미지 검색 로직
            if not combo_names: combo_names = [cat_no_space]
            valid_paths = utils.display_images(combo_names, priced_options, zero_options, preview_images, img_col, cat_no_space)
            return is_main_ready, base_price, product_specs, valid_paths, priced_options, zero_options

    return False, 0, "", [], [], []