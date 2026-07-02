import streamlit as st
import pandas as pd
import utils
import re

def render(filtered_products, options_df, rk, cat_no_space):
    def get_opt_price(group_name, option_name):
        g_clean = re.sub(r'\s+', '', str(group_name))
        o_clean = re.sub(r'\s+', '', str(option_name))
        
        # 👉 regex=False 추가
        df = options_df[options_df['적용 카테고리'].astype(str).str.replace(" ", "").str.contains(cat_no_space, regex=False)]
        for idx, row in df.iterrows():
            row_g = re.sub(r'\s+', '', str(row.get('옵션 구분(그룹명)', '')))
            row_o = re.sub(r'\s+', '', str(row.get('추가 선택-1', '')))
            if row_g == g_clean and row_o == o_clean:
                val = row.get('단가', 0)
                if pd.isna(val): return 0
                return int(float(val))
                
        for idx, row in options_df.iterrows():
            row_g = re.sub(r'\s+', '', str(row.get('옵션 구분(그룹명)', '')))
            row_o = re.sub(r'\s+', '', str(row.get('추가 선택-1', '')))
            if row_g == g_clean and row_o == o_clean:
                val = row.get('단가', 0)
                if pd.isna(val): return 0
                return int(float(val))
        return 0

    def render_custom_camera_parts(cam_type, position_label, rk_suffix):
        if cam_type == "선택 안 함": return None
        
        parts = ["선택 안 함"] 
        if cam_type == "뷸렛카메라":
            parts.append("뷸렛카메라박스(120*120*120)")
        elif cam_type == "하우징카메라":
            parts.extend(["알루미늄 각도기(기본)", "스텐 각도기", "번호인식 각도기"])
        elif cam_type == "스피드돔카메라" or cam_type == "스피드돔 카메라":
            parts.extend(["스피드돔 브라켓 부착용 판재", "40A소켓 (회전형으로 부착시)"])
            
        if len(parts) > 1:
            display_parts = []
            for p in parts:
                if p == "선택 안 함":
                    display_parts.append(p)
                else:
                    price = get_opt_price("카메라 부착 부품", p)
                    if price > 0:
                        display_parts.append(f"{p} (+{price:,}원)")
                    else:
                        display_parts.append(p)
                        
            st.markdown(f"<div style='font-size:14px; margin-top:5px; margin-bottom:2px; color:#555;'>└ {position_label} 부품 선택</div>", unsafe_allow_html=True)
            sel_display = st.radio(f"{position_label} 부품", display_parts, index=0, horizontal=True, key=f"cpart_{rk_suffix}", label_visibility="collapsed")
            
            if sel_display == "선택 안 함": return None
            return sel_display.split(" (+")[0]
        return None

    is_main_ready, base_price, product_specs = False, 0, ""
    preview_images, priced_options, zero_options, selected_cam_parts = [], [], [], []
    
    st.markdown("<div style='font-size:15px; font-weight:bold; color:#2e6c80; margin-bottom:5px;'>1️⃣ 브라켓 규격 선택</div>", unsafe_allow_html=True)
    p_list = filtered_products.apply(utils.build_spec_string, axis=1).tolist()
    sel_prod = st.selectbox("규격 선택", options=p_list, index=None, placeholder="규격을 선택해주세요", key=f"p_{rk}", label_visibility="collapsed")
    
    if sel_prod:
        idx = p_list.index(sel_prod)
        row = filtered_products.iloc[idx]
        base_price, product_specs, is_main_ready = int(row['단가']), f"{sel_prod}", True
        if pd.notna(row.get('이미지파일명')): preview_images.append(str(row['이미지파일명']).strip())

    if is_main_ready:
        st.markdown("<h2>2. 옵션 선택</h2>", unsafe_allow_html=True)
        opt_col, img_col = st.columns([5.5, 4.5])
        with opt_col:
            st.markdown("<div class='option-group-title'>📁 카메라 형태</div>", unsafe_allow_html=True)
            cam_opts = ["선택 안 함", "뷸렛카메라", "하우징카메라", "스피드돔카메라"]
            cam_type = st.radio("카메라 형태", cam_opts, index=0, horizontal=True, key=f"cam_{rk}", label_visibility="collapsed")
            
            sel_cam_part = None
            if cam_type != "선택 안 함":
                sel_cam_part = render_custom_camera_parts(cam_type, "카메라 부착", f"main_{rk}")
                
                curr_cam_state = str(sel_cam_part)
                prev_key = f"prev_cam_{rk}"
                if st.session_state.get(prev_key) != curr_cam_state:
                    st.session_state[prev_key] = curr_cam_state
                    rk_str = str(rk)
                    keys_to_delete = []
                    for k in st.session_state.keys():
                        k_str = str(k).lower()
                        if 'cart' in k_str: continue 
                        if rk_str in k_str and any(x in k_str for x in ['qty', '수량']):
                            keys_to_delete.append(k)
                    for k in keys_to_delete:
                        try: del st.session_state[k]
                        except: pass

                if sel_cam_part:
                    if sel_cam_part == "알루미늄 각도기(기본)":
                        base_name = "알루미늄 각도기(기본)"
                        zero_options.append({"cart_name": base_name, "display_name": f"{base_name}(1EA - 포함)"})
                        product_specs += f" / {base_name}(1EA 포함)"
                        
                    elif sel_cam_part == "뷸렛카메라박스(120*120*120)":
                        p_price = get_opt_price("카메라 부착 부품", "뷸렛카메라박스(120*120*120)")
                        priced_options.append({"cart_name": sel_cam_part, "display_name": f"{sel_cam_part} (1EA)", "unit_price": p_price, "qty_per_main": 1, "total_per_main": p_price, "group": "카메라 부착 부품"})
                        
                    else:
                        p_price = get_opt_price("카메라 부착 부품", sel_cam_part)
                        if p_price == 0:
                            zero_options.append({"cart_name": sel_cam_part, "display_name": f"{sel_cam_part} (1EA)"})
                        else:
                            priced_options.append({"cart_name": sel_cam_part, "display_name": f"{sel_cam_part} (1EA)", "unit_price": p_price, "qty_per_main": 1, "total_per_main": p_price, "group": "카메라 부착 부품"})
                            
                    selected_cam_parts.append(sel_cam_part)

            st.markdown("<div class='option-group-title'>📁 흔들림 방지 (선택)</div>", unsafe_allow_html=True)
            # 👉 regex=False 추가
            shake_df = options_df[options_df['적용 카테고리'].astype(str).str.replace(" ", "").str.contains(cat_no_space, regex=False) & 
                                  (options_df['옵션 구분(그룹명)'].astype(str).str.replace(" ","") == "흔들림방지")]
            
            shake_opts = ["선택 안 함"]
            if not shake_df.empty:
                shake_opts += [str(x) for x in shake_df['추가 선택-2'].dropna().unique().tolist() if str(x).strip()]
            else:
                shake_opts += ["와이어고리", "삼각파이프 받침", "와이어고리&삼각파이프받침"]

            sel_shake = st.radio("흔들림 방지", shake_opts, index=0, horizontal=True, key=f"shake_{rk}", label_visibility="collapsed")
            
            shake_kws = []
            if sel_shake != "선택 안 함":
                s_price = 0
                if not shake_df.empty:
                    s_clean = sel_shake.replace(" ", "")
                    for _, s_row in shake_df.iterrows():
                        if str(s_row.get('추가 선택-2', '')).replace(" ", "") == s_clean:
                            s_price = int(s_row.get('단가', 0))
                            break
                
                priced_options.append({
                    "cart_name": f"흔들림방지: {sel_shake}", 
                    "display_name": f"흔들림방지: {sel_shake}", 
                    "unit_price": s_price, 
                    "qty_per_main": 1, 
                    "total_per_main": s_price, 
                    "group": "흔들림 방지"
                })
                
                if "와이어" in sel_shake and "삼각" in sel_shake: shake_kws.append("-와이어-삼각파이프")
                elif "와이어" in sel_shake: shake_kws.append("-와이어")
                elif "삼각" in sel_shake: shake_kws.append("-삼각파이프")

            utils.render_generic_groups(cat_no_space, options_df, rk, priced_options, zero_options, preview_images)

        combo_names = []
        cam_kw = cam_type.replace("카메라", "") if cam_type != "선택 안 함" else ""
        shake_suffix = shake_kws[0] if shake_kws else ""
        
        base_combo = f"{cat_no_space}-{cam_kw}" if cam_kw else cat_no_space
        
        if cam_kw:
            if sel_cam_part:
                part_kw = re.sub(r'\(.*?\)', '', sel_cam_part).strip()
                combo_names.append(f"{base_combo}-{part_kw}{shake_suffix}")
                combo_names.append(f"{base_combo}-{part_kw}")
            combo_names.append(f"{base_combo}{shake_suffix}")
            combo_names.append(base_combo)
        else:
            combo_names.append(f"{cat_no_space}{shake_suffix}")
            
        combo_names.append(cat_no_space)
        combo_names = list(dict.fromkeys(combo_names))

        valid_paths = utils.display_images(combo_names, priced_options, zero_options, preview_images, img_col, cat_no_space)
        return is_main_ready, base_price, product_specs, valid_paths, priced_options, zero_options

    return False, 0, "", [], [], []