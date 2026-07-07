import streamlit as st
import pandas as pd
import utils
import re

def render(filtered_products, options_df, rk, cat_no_space):
    def get_opt_price(group_name, option_name):
        g_clean = re.sub(r'\s+', '', str(group_name))
        o_clean = re.sub(r'\s+', '', str(option_name))
        
        df = options_df[options_df['적용 카테고리'].astype(str).str.replace(" ", "").str.contains("CCTV폴")]
        
        for idx, row in df.iterrows():
            row_g = re.sub(r'\s+', '', str(row.get('옵션 구분(그룹명)', '')))
            row_o = re.sub(r'\s+', '', str(row.get('추가 선택-1', '')))
            if row_g == g_clean and row_o == o_clean:
                val = row.get('단가', 0)
                if pd.isna(val): return 0
                return int(float(val))
        return 0

    def render_custom_cctv_camera_parts(cam_type, position_label, rk_suffix):
        if cam_type == "설치 안 함": return None
        
        parts = ["선택 안 함"] 
        if cam_type == "뷸렛카메라":
            parts.append("뷸렛카메라박스")
        elif cam_type == "하우징카메라":
            parts.extend(["알루미늄 각도기", "스텐 각도기", "번호인식 각도기"])
        elif cam_type == "스피드돔카메라":
            parts.extend(["스피드돔 브라켓 부착용 판재", "40A소켓 (회전형으로 부착시)"])
            
        if len(parts) > 1:
            display_parts = []
            for p in parts:
                if p == "선택 안 함":
                    display_parts.append(p)
                else:
                    search_name = "뷸렛카메라박스(변경)" if p == "뷸렛카메라박스" else ("알루미늄 각도기(기본)" if p == "알루미늄 각도기" else p)
                    price = get_opt_price("카메라 부착 부품", search_name)
                    if price > 0: display_parts.append(f"{p} (+{price:,}원)")
                    else: display_parts.append(p)
                        
            st.markdown(f"<div style='font-size:14px; margin-top:5px; margin-bottom:2px; color:#555;'>└ {position_label} 부품 선택</div>", unsafe_allow_html=True)
            sel_display = st.radio(f"{position_label} 부품", display_parts, index=0, horizontal=True, key=f"cpart_{rk_suffix}", label_visibility="collapsed")
            
            if sel_display == "선택 안 함": return None
            return sel_display.split(" (+")[0]
        return None

    is_main_ready, base_price, product_specs = False, 0, ""
    preview_images, priced_options, zero_options, selected_cam_parts = [], [], [], []
    
    c1, c2, c3 = st.columns(3)
    diameters = sorted(filtered_products['직경(인치)'].dropna().unique())
    sel_dia = c1.selectbox("지름", options=[f"{int(d)}인치" for d in diameters], index=None, placeholder="선택 안 함", key=f"d_{rk}")
    
    if sel_dia:
        d_val = float(sel_dia.replace("인치", ""))
        thicknesses = sorted(filtered_products[filtered_products['직경(인치)'] == d_val]['두께(T)'].dropna().unique())
        sel_thi = c2.selectbox("두께", options=[f"{t}T" for t in thicknesses], index=None, placeholder="선택 안 함", key=f"t_{rk}")
        
        if sel_thi:
            t_val = float(sel_thi.replace("T", ""))
            pole_list = filtered_products[(filtered_products['직경(인치)'] == d_val) & (filtered_products['두께(T)'] == t_val)]
            actual_heights = sorted(pole_list['높이/길이(M)'].dropna().unique())
            max_h = max(actual_heights) if actual_heights else 6.0
            
            extended_heights = []
            h = 0.5
            while h <= max_h:
                extended_heights.append(h)
                h += 0.5
                
            hei_opts = [f"{int(h)}M" if h.is_integer() else f"{h}M" for h in extended_heights]
            sel_hei = c3.selectbox("높이 (0.5M 단위)", options=hei_opts, index=None, placeholder="선택 안 함", key=f"h_{rk}")
            
            if sel_hei:
                h_val = float(sel_hei.replace("M", ""))
                lookup_h = next((x for x in actual_heights if x >= h_val), actual_heights[-1])
                
                if lookup_h < 6.0:
                    row = pole_list[pole_list['높이/길이(M)'] == lookup_h].iloc[0]
                    base_price = int(row['단가'])
                    product_specs = f"지름: {sel_dia} / 두께: {sel_thi} / 높이: {sel_hei}"
                    is_main_ready = True
                    if pd.notna(row.get('이미지파일명')): preview_images.append(str(row['이미지파일명']).strip())
                else:
                    type_list = pole_list[pole_list['높이/길이(M)'] == lookup_h]['제품명'].dropna().unique().tolist()
                    st.markdown("<div style='margin-top:5px; font-size:15px; font-weight:bold; color:#d9534f;'>⚠️ 6M 이상 폴대 제작 방식을 선택해 주세요.</div>", unsafe_allow_html=True)
                    st.markdown("<div class='option-group-title'>📁 제작 방식 선택</div>", unsafe_allow_html=True)
                    r_opts = ["선택 안 함"] + type_list
                    sel_prod_name = st.radio("제작 방식 선택", r_opts, index=utils.get_def_idx(r_opts), horizontal=True, key=f"prod_name_{rk}", label_visibility="collapsed")
                    if sel_prod_name != "선택 안 함":
                        row = pole_list[(pole_list['높이/길이(M)'] == lookup_h) & (pole_list['제품명'] == sel_prod_name)].iloc[0]
                        base_price = int(row['단가'])
                        product_specs = f"지름: {sel_dia} / 두께: {sel_thi} / 높이: {sel_hei} / 방식: {sel_prod_name}"
                        is_main_ready = True
                        if pd.notna(row.get('이미지파일명')): preview_images.append(str(row['이미지파일명']).strip())

    if is_main_ready:
        st.markdown("<h2>2. 옵션 선택</h2>", unsafe_allow_html=True)
        opt_col, img_col = st.columns([5.5, 4.5])
        with opt_col:
            
            # --- 3. 앙카베이스 / 베이스커버 선택 ---
            st.markdown("<div class='option-group-title'>📁 앙카베이스 / 베이스커버 선택</div>", unsafe_allow_html=True)
            anchor_df = options_df[options_df['옵션 구분(그룹명)'].astype(str).str.contains("앙카베이스", na=False)]
            if not anchor_df.empty:
                anchor_opts = ["선택 안 함"] + anchor_df['추가 선택-1'].dropna().unique().tolist()
                sel_anchor = st.selectbox("앙카베이스 선택", anchor_opts, key=f"anchor_{rk}")
                if sel_anchor != "선택 안 함":
                    a_row = anchor_df[anchor_df['추가 선택-1'] == sel_anchor].iloc[0]
                    a_price = int(a_row.get('단가', 0))
                    priced_options.append({"cart_name": f"앙카베이스: {sel_anchor}", "display_name": f"앙카베이스: {sel_anchor}", "unit_price": a_price, "qty_per_main": 1, "total_per_main": a_price, "group": "하부 부속"})
            
            cover_df = options_df[options_df['옵션 구분(그룹명)'].astype(str).str.contains("베이스커버", na=False)]
            if not cover_df.empty:
                cover_opts = ["선택 안 함"] + cover_df['추가 선택-1'].dropna().unique().tolist()
                sel_cover = st.selectbox("베이스커버 선택", cover_opts, key=f"cover_{rk}")
                if sel_cover != "선택 안 함":
                    c_row = cover_df[cover_df['추가 선택-1'] == sel_cover].iloc[0]
                    c_price = int(c_row.get('단가', 0))
                    priced_options.append({"cart_name": f"베이스커버: {sel_cover}", "display_name": f"베이스커버: {sel_cover}", "unit_price": c_price, "qty_per_main": 1, "total_per_main": c_price, "group": "하부 부속"})

            # --- 1. 폴의 형태 선택 ---
            st.markdown("<div class='option-group-title'>📁 폴의 형태</div>", unsafe_allow_html=True)
            a_opts = ["기본형(I형)", "ㄱ형 (암 1EA)", "T형 (암 2EA)", "벽부형"]
            arm_type = st.radio("폴의 형태", a_opts, index=0, label_visibility="collapsed", key=f"at_{rk}")
            
            shake_kws = []
            
            if arm_type not in ["기본형(I형)", "벽부형"]:
                arm_df = options_df[(options_df['적용 카테고리'].astype(str).str.replace(" ", "") == "CCTV폴") & 
                                    (options_df['옵션 구분(그룹명)'].astype(str).str.replace(" ", "") == "암(Arm)")]
                arm_len_df = arm_df[arm_df['길이/규격'].notna()]
                
                if not arm_len_df.empty:
                    st.markdown("<div class='option-group-title'>📁 암(Arm) 길이 선택</div>", unsafe_allow_html=True)
                    def format_len(x):
                        try: return str(int(float(x)))
                        except: return str(x)
                    raw_lens = arm_len_df['길이/규격'].dropna().unique().tolist()
                    arm_len_opts = [format_len(x) for x in raw_lens]
                    
                    sel_arm_len = st.selectbox("암 길이", options=arm_len_opts, index=0, key=f"arm_len_{rk}", label_visibility="collapsed")
                    if sel_arm_len:
                        matched_row = None
                        for idx, row in arm_len_df.iterrows():
                            if format_len(row['길이/규격']) == sel_arm_len:
                                matched_row = row
                                break
                                
                        if matched_row is not None:
                            a_unit_price = int(matched_row.get('단가', 0))
                            arm_qty = 2 if "T형" in arm_type else 1
                            total_a_price = a_unit_price * arm_qty
                            priced_options.append({"cart_name": f"{sel_arm_len}mm ({arm_qty}개)", "display_name": f"암 길이: {sel_arm_len}mm (x{arm_qty})", "unit_price": a_unit_price, "qty_per_main": arm_qty, "total_per_main": total_a_price, "group": "암길이"})
                            
                    st.markdown("<div class='option-group-title'>📁 흔들림 방지 (선택)</div>", unsafe_allow_html=True)
                    shake_df = options_df[(options_df['적용 카테고리'].astype(str).str.replace(" ", "") == "CCTV폴") & 
                                          (options_df['옵션 구분(그룹명)'].astype(str).str.replace(" ", "") == "암(Arm)") & 
                                          (options_df['추가 선택-1'].astype(str).str.replace(" ", "") == "흔들림방지")]
                    
                    shake_opts = ["선택 안 함"]
                    if not shake_df.empty: shake_opts += [str(x) for x in shake_df['추가 선택-2'].dropna().unique().tolist() if str(x).strip()]
                    else: shake_opts += ["와이어고리", "삼각파이프 받침", "와이어고리&삼각파이프받침"]

                    sel_shake = st.radio("흔들림 방지", shake_opts, index=0, horizontal=True, key=f"shake_{rk}", label_visibility="collapsed")
                    if sel_shake != "선택 안 함":
                        s_price = 0
                        if not shake_df.empty:
                            s_row = shake_df[shake_df['추가 선택-2'] == sel_shake]
                            if not s_row.empty: s_price = int(s_row.iloc[0].get('단가', 0))
                        else:
                            if sel_shake == "와이어고리": s_price = 6000
                            elif sel_shake == "삼각파이프 받침": s_price = 45000
                            elif sel_shake == "와이어고리&삼각파이프받침": s_price = 50000
                            
                        arm_qty = 2 if "T형" in arm_type else 1
                        tot_s_price = s_price * arm_qty
                        priced_options.append({"cart_name": f"흔들림방지: {sel_shake}", "display_name": f"흔들림방지: {sel_shake} (x{arm_qty})", "unit_price": s_price, "qty_per_main": arm_qty, "total_per_main": tot_s_price, "group": "흔들림 방지"})
                        shake_kws.append(sel_shake.replace(" ", ""))

            # --- 2. 설치할 카메라의 형태 선택 ---
            main_part, arm_part = None, None
            cam_main, cam_arm = "설치 안 함", "설치 안 함"
            wall_arm_type = ""
            
            if arm_type == "기본형(I형)":
                st.markdown("<div class='option-group-title'>📁 설치할 카메라의 형태</div>", unsafe_allow_html=True)
                cam_opts = ["설치 안 함", "뷸렛카메라", "하우징카메라", "스피드돔카메라"]
                cam_main = st.radio("설치할 카메라의 형태", cam_opts, index=0, horizontal=True, key=f"cam_main_{rk}", label_visibility="collapsed")
                if cam_main != "설치 안 함": main_part = render_custom_cctv_camera_parts(cam_main, "카메라 부착", f"main_{rk}")
                    
            elif arm_type == "벽부형":
                st.markdown("<div class='option-group-title'>📁 벽부형 형태</div>", unsafe_allow_html=True)
                wall_arm_type = st.radio("벽부형 형태", ["I형", "L형"], index=0, horizontal=True, key=f"wall_arm_type_{rk}", label_visibility="collapsed")
                
                show_cam = False
                if wall_arm_type == "L형":
                    st.markdown("<div style='font-size:14px; margin-bottom:5px; color:#555;'>👉 벽 이격 거리(가로) (mm)</div>", unsafe_allow_html=True)
                    wc1, wc2 = st.columns([7, 3])
                    wall_dist = wc1.text_input("이격거리", placeholder="숫자 입력", key=f"wall_dist_{rk}", label_visibility="collapsed")
                    applied = wc2.button("확인", key=f"btn_wall_{rk}")
                    val_digits = "".join(filter(str.isdigit, str(st.session_state.get(f"wall_dist_{rk}", ""))))
                    if applied or val_digits:
                        if val_digits:
                            zero_options.append({"cart_name": f"이격거리: {val_digits}mm", "display_name": f"이격거리: {val_digits}mm"})
                            show_cam = True
                        elif applied: st.warning("⚠️ 숫자를 입력해 주세요.")
                else: show_cam = True
                    
                if show_cam:
                    st.markdown("<div class='option-group-title'>📁 설치할 카메라의 형태</div>", unsafe_allow_html=True)
                    cam_opts = ["설치 안 함", "뷸렛카메라", "하우징카메라", "스피드돔카메라"]
                    cam_main = st.radio("설치할 카메라의 형태", cam_opts, index=0, horizontal=True, key=f"cam_main_wall_{rk}", label_visibility="collapsed")
                    if cam_main != "설치 안 함": main_part = render_custom_cctv_camera_parts(cam_main, "카메라 부착", f"main_wall_{rk}")
                        
            else:
                st.markdown("<div class='option-group-title'>📁 설치할 카메라의 형태</div>", unsafe_allow_html=True)
                st.markdown("<div style='margin-top:10px; font-weight:bold; color:#555;'>👉 메인 폴 상부 설치할 카메라 형태</div>", unsafe_allow_html=True)
                main_cam_opts = ["설치 안 함", "뷸렛카메라", "하우징카메라"]
                cam_main = st.radio("메인 폴 상부 설치할 카메라 형태", main_cam_opts, index=0, horizontal=True, key=f"cam_main_{rk}", label_visibility="collapsed")
                if cam_main != "설치 안 함": main_part = render_custom_cctv_camera_parts(cam_main, "메인 폴 상부", f"main_{rk}")
                
                st.markdown("<div style='margin-top:15px; font-weight:bold; color:#555;'>👉 암(Arm)에 설치할 카메라 형태</div>", unsafe_allow_html=True)
                arm_cam_opts = ["설치 안 함", "뷸렛카메라", "하우징카메라", "스피드돔카메라"]
                cam_arm = st.radio("암(Arm)에 설치할 카메라 형태", arm_cam_opts, index=0, horizontal=True, key=f"cam_arm_{rk}", label_visibility="collapsed")
                if cam_arm != "설치 안 함": arm_part = render_custom_cctv_camera_parts(cam_arm, "암(Arm)", f"arm_{rk}")
            
            # 카메라 부품 단가 처리
            part_counts = {}
            if main_part: part_counts[main_part] = part_counts.get(main_part, 0) + 1
            if arm_part:
                arm_qty = 2 if "T형" in arm_type else 1
                part_counts[arm_part] = part_counts.get(arm_part, 0) + arm_qty
                
            selected_cam_parts = list(part_counts.keys())
            base_slot_used = True if "스피드돔카메라" in [cam_main, cam_arm] else False
                
            for part, count in part_counts.items():
                if part in ["뷸렛카메라박스", "알루미늄 각도기"]:
                    base_name, add_name = ("뷸렛카메라박스(변경)", "뷸렛카메라박스(추가)") if part == "뷸렛카메라박스" else ("알루미늄 각도기(기본)", "알루미늄 각도기(추가)")
                    base_p, add_p = get_opt_price("카메라 부착 부품", base_name), get_opt_price("카메라 부착 부품", add_name)
                    base_qty, add_qty = 0, 0
                    for _ in range(count):
                        if not base_slot_used: base_qty += 1; base_slot_used = True
                        else: add_qty += 1
                    if base_qty > 0:
                        if base_p == 0: zero_options.append({"cart_name": base_name, "display_name": f"{base_name} ({base_qty}EA)"})
                        else: priced_options.append({"cart_name": base_name, "display_name": f"{base_name} ({base_qty}EA)", "unit_price": base_p, "qty_per_main": base_qty, "total_per_main": base_p * base_qty, "group": "카메라 부착 부품"})
                    if add_qty > 0: priced_options.append({"cart_name": add_name, "display_name": f"{add_name} ({add_qty}EA)", "unit_price": add_p, "qty_per_main": add_qty, "total_per_main": add_p * add_qty, "group": "카메라 부착 부품"})
                else:
                    base_p = get_opt_price("카메라 부착 부품", part)
                    priced_options.append({"cart_name": part, "display_name": f"{part} (x{count})", "unit_price": base_p, "qty_per_main": count, "total_per_main": base_p * count, "group": "카메라 부착 부품"})

            # --- 4. 특별 주문 사항 (공통 유틸 로직) ---
            filtered_options_df = options_df[~options_df['옵션 구분(그룹명)'].astype(str).str.contains("앙카베이스|베이스커버", na=False)]
            utils.render_generic_groups(cat_no_space, filtered_options_df, rk, priced_options, zero_options, preview_images)

        # --- 5. 최종 이미지 파일명 매칭 로직 ---
        combo_names = []
        if arm_type == "벽부형": arm_kw = f"벽부형-{wall_arm_type}"
        else: arm_kw = "기본형" if "기본형" in str(arm_type) else ("ㄱ형" if "ㄱ형" in str(arm_type) else "T형")
        
        main_cam_kw = cam_main.replace("카메라", "") if cam_main and cam_main != "설치 안 함" else ""
        arm_cam_kw = cam_arm.replace("카메라", "") if cam_arm and cam_arm != "설치 안 함" else ""
        
        shake_suffix = ""
        if shake_kws:
            raw_shake = shake_kws[0]
            if "와이어" in raw_shake and "삼각" in raw_shake: shake_suffix = "-와이어-삼각파이프"
            elif "와이어" in raw_shake: shake_suffix = "-와이어"
            elif "삼각" in raw_shake: shake_suffix = "-삼각파이프"

        sd_parts = []
        for p in selected_cam_parts:
            if "40A소켓" in p: sd_parts.append("40A소켓")
            elif "스피드돔 브라켓" in p: sd_parts.append("스피드돔 브라켓 부착용 판재")

        if arm_kw != "기본형" and "벽부형" not in arm_kw:
            base_prefix = f"{cat_no_space}-{arm_kw}"
            if main_cam_kw: base_prefix += f"-{main_cam_kw}"
            else: base_prefix += "-없음"
            
            if arm_cam_kw == "스피드돔" and sd_parts:
                for sdp in sd_parts:
                    combo_names.append(f"{base_prefix}-{sdp}{shake_suffix}")
                    combo_names.append(f"{base_prefix}-{sdp}")
            elif arm_cam_kw:
                combo_names.append(f"{base_prefix}-{arm_cam_kw}{shake_suffix}")
                combo_names.append(f"{base_prefix}-{arm_cam_kw}")
            else:
                combo_names.append(f"{base_prefix}{shake_suffix}")
                combo_names.append(base_prefix)
        else:
            base_prefix = f"{cat_no_space}-{arm_kw}"
            if main_cam_kw: combo_names.append(f"{base_prefix}-{main_cam_kw}")
            else: combo_names.append(base_prefix)
                
        base_cctv = f"{cat_no_space}-{arm_kw}"
        if main_cam_kw: base_cctv += f"-{main_cam_kw}"
        elif arm_cam_kw: base_cctv += f"-없음-{arm_cam_kw}"
            
        cctv_combos = [base_cctv, f"{cat_no_space}-{arm_kw}"]
        
        for c in cctv_combos:
            combo_names.append(c)
            if shake_suffix: combo_names.append(f"{c}{shake_suffix}")
                
        part_kws = [re.sub(r'\(.*?\)', '', p).strip() for p in selected_cam_parts]
        if arm_cam_kw:
            for part in part_kws:
                combo_names.append(f"{base_cctv}-{arm_cam_kw}-{part}")
                combo_names.append(f"{base_cctv}-{part}")
        else:
            for part in part_kws:
                combo_names.append(f"{base_cctv}-{part}")

        combo_names.append(cat_no_space)
        combo_names = list(dict.fromkeys(combo_names))
        
        valid_paths = utils.display_images(combo_names, priced_options, zero_options, preview_images, img_col, cat_no_space)
        return is_main_ready, base_price, product_specs, valid_paths, priced_options, zero_options

    return False, 0, "", [], [], []