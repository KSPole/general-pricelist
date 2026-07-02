import streamlit as st
import pandas as pd
import utils

def render(filtered_products, options_df, rk, cat_no_space):
    is_main_ready, base_price, product_specs = False, 0, ""
    preview_images, priced_options, zero_options, selected_cam_parts = [], [], [], []
    
    if cat_no_space == "천장형브라켓":
        st.markdown("<div style='font-size:15px; font-weight:bold; color:#2e6c80; margin-bottom:5px;'>1️⃣ 규격 선택</div>", unsafe_allow_html=True)
        
        outers = sorted(filtered_products['겉봉(상봉)'].dropna().unique())
        c1, c2 = st.columns(2)
        
        # 👉 1. 겉봉 / 속봉 선택 메뉴
        sel_out = c1.selectbox("겉봉(상봉)", options=[f"{int(x)}" for x in outers], index=None, placeholder="길이를 선택해주세요", key=f"o_{rk}")
        if sel_out:
            inners_list = filtered_products[filtered_products['겉봉(상봉)'] == float(sel_out)]['속봉(하봉)'].dropna().unique()
            inners = sorted(inners_list)
            sel_in = c2.selectbox("속봉(하봉)", options=[f"{int(x)}" for x in inners], index=None, placeholder="길이를 선택해주세요", key=f"i_{rk}")
        else:
            sel_in = c2.selectbox("속봉(하봉)", options=[], index=None, placeholder="겉봉을 먼저 선택해주세요", key=f"i_{rk}")
            
        # 👉 2. 맞춤 규격 추천기 (항상 표시)
        with st.expander("🎯 맞춤 규격 추천기 (길이 입력 시 자동 추천)", expanded=True):
            st.markdown("<div style='font-size:13px; color:#555; margin-bottom:10px;'>👇 현장에서 필요한 조절 길이를 입력해 주시면 최적의 규격을 찾아드립니다. (딱 맞는 규격이 없으면 가장 가까운 근사치를 추천합니다)</div>", unsafe_allow_html=True)
            tc1, tc2 = st.columns(2)
            
            # 👉 [핵심 수정 1] 길이 입력 시 이전 선택값을 초기화하여 하단 단가 확인창이 뜨지 않도록 막음
            def reset_selections():
                st.session_state[f"o_{rk}"] = None
                st.session_state[f"i_{rk}"] = None

            t_min = tc1.number_input("👉 최소 조절 길이 (mm)", min_value=0, step=10, value=0, key=f"t_min_{rk}", on_change=reset_selections)
            t_max = tc2.number_input("👉 최대 조절 길이 (mm)", min_value=0, step=10, value=0, key=f"t_max_{rk}", on_change=reset_selections)
            
            if t_min > 0 and t_max > 0:
                valid_combos = []
                approx_combos = []
                for out_val in outers:
                    inners_for_out = filtered_products[filtered_products['겉봉(상봉)'] == out_val]['속봉(하봉)'].dropna().unique()
                    for in_val in inners_for_out:
                        o_val, i_val = int(out_val), int(in_val)
                        
                        # 공식 적용
                        if i_val >= o_val:
                            min_l = o_val + (i_val - o_val) + 120
                            max_l = o_val + (i_val - 80) + 60
                        else:
                            min_l = o_val + 60
                            max_l = o_val + (i_val - 80) + 60
                            
                        # 추천 원칙: 속봉이 겉봉보다 길지 않도록 (단, 최대 조절 구간 2380 이상은 예외)
                        if (i_val <= o_val) or (max_l >= 2380):
                            combo_info = {'outer': o_val, 'inner': i_val, 'min': min_l, 'max': max_l}
                            
                            # 조건 100% 만족
                            if min_l <= t_min and max_l >= t_max:
                                valid_combos.append(combo_info)
                            
                            # 조건 불만족 시, 모자란 길이를 계산하여 페널티(근사치 오차) 부여
                            penalty = max(0, min_l - t_min) + max(0, t_max - max_l)
                            extra = max(0, t_min - min_l) + max(0, max_l - t_max)
                            combo_info['penalty'] = penalty
                            combo_info['extra'] = extra
                            approx_combos.append(combo_info)
                
                best = None
                is_approx = False
                
                if valid_combos:
                    valid_combos.sort(key=lambda x: (0 if x['outer'] == 600 else 1, -x['outer']))
                    best = valid_combos[0]
                elif approx_combos:
                    approx_combos.sort(key=lambda x: (x['penalty'], 0 if x['outer'] == 600 else 1, x['extra'], -x['outer']))
                    best = approx_combos[0]
                    is_approx = True
                
                if best:
                    if is_approx:
                        st.markdown(f"<div style='color:#e67e22; font-size:16px; font-weight:bold; margin-top:10px; margin-bottom:10px;'>💡 추천 조합 (근사치): 겉봉 {best['outer']} / 속봉 {best['inner']} &nbsp;<span style='color:#666; font-size:14px;'>(실제 조절 가능: {best['min']} ~ {best['max']}mm)</span></div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div style='color:#d9534f; font-size:16px; font-weight:bold; margin-top:10px; margin-bottom:10px;'>💡 최적 추천 조합: 겉봉 {best['outer']} / 속봉 {best['inner']} &nbsp;<span style='color:#666; font-size:14px;'>(조절 가능 구간: {best['min']} ~ {best['max']}mm)</span></div>", unsafe_allow_html=True)
                    
                    def apply_recommended_size(o_val, i_val):
                        st.session_state[f"o_{rk}"] = str(o_val)
                        st.session_state[f"i_{rk}"] = str(i_val)

                    st.button("🚀 추천 규격 적용하기", type="primary", use_container_width=True, on_click=apply_recommended_size, args=(best['outer'], best['inner']))
                else:
                    st.markdown("<div style='color:#888; font-size:14px; margin-top:8px;'>⚠️ 알맞은 기성품 조합을 찾을 수 없습니다.</div>", unsafe_allow_html=True)
        
        # 규격 선택이 완료된 경우
        if sel_out and sel_in:
            cond_out = (filtered_products['겉봉(상봉)'] == float(sel_out))
            cond_in = (filtered_products['속봉(하봉)'] == float(sel_in))
            row = filtered_products[cond_out & cond_in]
            
            if not row.empty:
                base_price = int(row.iloc[0]['단가'])
                # 👉 [핵심 수정 2] 장바구니 및 단가 확인 창에 표시되는 텍스트 깔끔하게 수정
                product_specs = f"겉봉(상봉) {int(float(sel_out))} / 속봉(하봉) {int(float(sel_in))}"
                is_main_ready = True
                
                img_val = row.iloc[0].get('이미지파일명')
                if pd.notna(img_val):
                    preview_images.append(str(img_val).strip())
    else:
        p_list = filtered_products.apply(utils.build_spec_string, axis=1).tolist()
        sel_prod = st.selectbox("상세 규격 선택", options=p_list, index=None, placeholder="길이를 선택해주세요", key=f"p_{rk}")
        if sel_prod:
            idx = p_list.index(sel_prod)
            row = filtered_products.iloc[idx]
            base_price, product_specs, is_main_ready = int(row['단가']), f"{sel_prod}", True
            
            img_val = row.get('이미지파일명')
            if pd.notna(img_val):
                preview_images.append(str(img_val).strip())

    if is_main_ready:
        st.markdown("<h2>2. 옵션 선택</h2>", unsafe_allow_html=True)
        opt_col, img_col = st.columns([5.5, 4.5])
        with opt_col:
            st.markdown("<div class='option-group-title'>📁 기본형 / T형 선택</div>", unsafe_allow_html=True)
            brk_opts = ["기본형", "T형"]
            brk_shape = st.radio("기본형 / T형 선택", brk_opts, index=0, horizontal=True, key=f"brk_shape_{rk}", label_visibility="collapsed")
            
            if brk_shape == "T형":
                cond_cat = (options_df['적용 카테고리'].astype(str).str.replace(" ", "") == cat_no_space)
                cond_t = (options_df['추가 선택-1'].astype(str).str.contains("T형", na=False))
                t_row = options_df[cond_cat & cond_t]
                
                t_price = int(t_row.iloc[0]['단가']) if not t_row.empty else 25000
                priced_options.append({"cart_name": "T형", "display_name": "형태: T형", "unit_price": t_price, "qty_per_main": 1, "total_per_main": t_price, "group": "브라켓형태"})
            
            st.markdown("<div class='option-group-title'>📁 카메라 형태</div>", unsafe_allow_html=True)
            cam_opts = ["뷸렛카메라", "돔카메라", "하우징카메라"]
            cam_type = st.radio("카메라 형태", cam_opts, index=0, horizontal=True, key=f"cam_other_{rk}", label_visibility="collapsed")
            
            box_height = ""
            if cam_type in ["뷸렛카메라", "돔카메라"]:
                st.markdown("<div class='option-group-title'>📁 뷸렛카메라박스 높이</div>", unsafe_allow_html=True)
                box_opts = ["높이 60mm", "높이 120mm"]
                box_height = st.radio("뷸렛카메라박스 높이", box_opts, index=0, horizontal=True, key=f"box_hei_{rk}", label_visibility="collapsed")
                
                cond_cat = (options_df['적용 카테고리'].astype(str).str.replace(" ", "") == cat_no_space)
                cond_box = (options_df['추가 선택-1'].astype(str).str.contains(box_height.replace("높이 ", ""), na=False))
                h_row = options_df[cond_cat & cond_box]
                
                h_price = int(h_row.iloc[0]['단가']) if not h_row.empty else 5000
                priced_options.append({"cart_name": box_height, "display_name": f"박스 높이: {box_height}", "unit_price": h_price, "qty_per_main": 1, "total_per_main": h_price, "group": "박스사이즈"})
            
            elif cam_type == "하우징카메라":
                zero_options.append({"cart_name": "각도기(기본)", "display_name": "각도기(기본 포함)"})
            
            utils.render_generic_groups(cat_no_space, options_df, rk, priced_options, zero_options, preview_images)

            # 👉 4. 천장형 브라켓 조절 구간 공식 안내
            if cat_no_space == "천장형브라켓":
                outer_val = int(sel_out)
                inner_val = int(sel_in)
                
                box_h = 0
                if box_height == "높이 60mm": box_h = 60
                elif box_height == "높이 120mm": box_h = 120
                
                min_len, max_len = 0, 0
                
                if cam_type in ["뷸렛카메라", "돔카메라"]:
                    if inner_val >= outer_val:
                        min_len = outer_val + (inner_val - outer_val) + (box_h + 60)
                        max_len = outer_val + (inner_val - 80) + box_h
                    else:
                        min_len = outer_val + box_h
                        max_len = outer_val + (inner_val - 80) + box_h
                        
                elif cam_type == "하우징카메라":
                    if inner_val >= outer_val:
                        min_len = outer_val + (inner_val - outer_val) + 120
                        max_len = outer_val + (inner_val - 80) + 60
                    else:
                        min_len = outer_val + 60
                        max_len = outer_val + (inner_val - 80) + 60
                
                if min_len > 0 and max_len > 0:
                    st.markdown(f"<div style='background-color:#e8f4f8; border-left:4px solid #2e6c80; padding:10px; margin-top:15px; margin-bottom:15px; font-size:14px; font-weight:bold; color:#2e6c80; border-radius:4px;'>💡 고객님 선택 규격 조절 가능 구간: 천장에서 최소 {min_len}mm ~ 최대 {max_len}mm 조절 가능합니다.</div>", unsafe_allow_html=True)

        combo_names = []
        base_brk = "천장형브라켓"
        t_prefix = "T형-" if brk_shape == "T형" else ""
        
        box_kw = ""
        if box_height == "높이 60mm": box_kw = "60"
        elif box_height == "높이 120mm": box_kw = "120"
            
        if cam_type == "뷸렛카메라":
            if box_kw: combo_names.append(f"{base_brk}-{t_prefix}뷸렛-{box_kw}")
            combo_names.append(f"{base_brk}-{t_prefix}뷸렛")
        elif cam_type == "돔카메라":
            if box_kw: combo_names.append(f"{base_brk}-{t_prefix}돔-{box_kw}")
            combo_names.append(f"{base_brk}-{t_prefix}돔")
        elif cam_type == "하우징카메라":
            combo_names.append(f"{base_brk}-{t_prefix}하우징")
            
        if brk_shape == "T형": combo_names.append(f"{base_brk}-T형")
        
        combo_names.append(base_brk)
        combo_names.append(cat_no_space)
        combo_names = list(dict.fromkeys(combo_names))

        valid_paths = utils.display_images(combo_names, priced_options, zero_options, preview_images, img_col, cat_no_space)
        return is_main_ready, base_price, product_specs, valid_paths, priced_options, zero_options

    return False, 0, "", [], [], []