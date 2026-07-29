import streamlit as st
import pandas as pd
import utils
import re

def render(filtered_products, options_df, rk, cat_no_space):
    def get_opt_price(group_name, option_name):
        g_clean = re.sub(r'\s+', '', str(group_name))
        o_clean = re.sub(r'\s+', '', str(option_name))
        
        # 💡 옵션 단가는 CCTV폴 공통 부품에서 가져옵니다
        df = options_df[options_df['적용 카테고리'].astype(str).str.replace(" ", "").str.contains(f"{cat_no_space}|CCTV폴", regex=True)]
        
        for idx, row in df.iterrows():
            row_g = re.sub(r'\s+', '', str(row.get('옵션 구분(그룹명)', '')))
            row_o = re.sub(r'\s+', '', str(row.get('추가 선택-1', '')))
            if row_g == g_clean and row_o == o_clean:
                val = row.get('단가', 0)
                if pd.isna(val): return 0
                return int(float(val))
        return 0

    # 💡 스피드돔 카메라 삭제 완료
    def render_custom_cctv_camera_parts(cam_type, position_label, rk_suffix):
        if cam_type == "설치 안 함": return None
        
        parts = [] 
        if cam_type == "뷸렛카메라":
            parts = ["뷸렛카메라박스", "알루미늄 각도기(기본)"]
        elif cam_type == "하우징카메라":
            parts = ["선택 안 함", "알루미늄 각도기(기본)", "스텐 각도기", "번호인식 각도기"]
            
        if parts:
            st.markdown(f"<div style='font-size:14px; margin-top:5px; margin-bottom:2px; color:#555;'>└ {position_label} 부품 선택</div>", unsafe_allow_html=True)
            sel_display = st.radio(f"{position_label} 부품", parts, index=0, horizontal=True, key=f"cpart_{rk_suffix}", label_visibility="collapsed")
            
            if sel_display == "선택 안 함": return None
            return sel_display
        return None

    is_main_ready, base_price, product_specs = False, 0, ""
    preview_images, priced_options, zero_options, selected_cam_parts = [], [], [], []
    
    st.markdown("<div style='font-size:15px; font-weight:bold; color:#2e6c80; margin-bottom:5px;'>1️⃣ 규격 선택</div>", unsafe_allow_html=True)
    
    # 💡 1. 지름 / 높이 선택 메뉴 (두께 삭제)
    c1, c2 = st.columns(2)
    
    pipe_opts = ["2.5인치", "3인치"]
    sel_dia = c1.selectbox("파이프 지름", options=pipe_opts, index=None, placeholder="지름을 선택해주세요", key=f"d_{rk}")
    
    if sel_dia:
        d_val = float(sel_dia.replace("인치", ""))
        # 직경(인치)가 2.5 또는 3인 제품만 필터링
        sub_df = filtered_products[filtered_products['직경(인치)'] == d_val]
        
        if sub_df.empty: 
            sub_df = filtered_products # 예외 처리
            
        p_list = sub_df.apply(utils.build_spec_string, axis=1).tolist()
        sel_hei = c2.selectbox("높이 선택", options=p_list, index=None, placeholder="높이를 선택해주세요", key=f"h_{rk}")
        
        if sel_hei:
            idx = p_list.index(sel_hei)
            row = sub_df.iloc[idx]
            base_price = int(row['단가'])
            product_specs = f"지름: {sel_dia} / 높이: {sel_hei}"
            is_main_ready = True
            if pd.notna(row.get('이미지파일명')): preview_images.append(str(row['이미지파일명']).strip())

    if is_main_ready:
        st.markdown("<h2>2. 옵션 선택</h2>", unsafe_allow_html=True)
        opt_col, img_col = st.columns([5.5, 4.5])
        with opt_col:
            
            # --- 2. 브라켓의 형태 (폴의 형태) 선택 ---
            st.markdown("<div class='option-group-title'>📁 브라켓의 형태</div>", unsafe_allow_html=True)
            a_opts = ["기본형(I형)", "ㄱ형 (암 1EA)", "T형 (암 2EA)", "벽부형"]
            arm_type = st.radio("브라켓의 형태", a_opts, index=0, label_visibility="collapsed", key=f"at_{rk}")
            
            wall_arm_type = ""
            wall_has_arm = "적용 안 함"
            show_cam = True
            
            if arm_type == "벽부형":
                st.markdown("<div class='option-group-title'>📁 벽부형 형태</div>", unsafe_allow_html=True)
                wall_arm_type = st.radio("벽부형 형태", ["I형", "L형"], index=0, horizontal=True, key=f"wall_arm_type_{rk}", label_visibility="collapsed")
                
                w_price = 0
                w_df = options_df[(options_df['적용 카테고리'].astype(str).str.replace(" ", "").str.contains(f"{cat_no_space}|CCTV폴", regex=True)) & 
                                  (options_df['옵션 구분(그룹명)'].astype(str).str.replace(" ", "") == sel_dia.replace(" ", "")) & 
                                  (options_df['추가 선택-1'].astype(str).str.replace(" ", "") == "벽부형") & 
                                  (options_df['추가 선택-2'].astype(str).str.replace(" ", "") == wall_arm_type.replace(" ", ""))]
                
                if not w_df.empty:
                    w_price = int(w_df.iloc[0].get('단가', 0))
                
                if w_price > 0:
                    priced_options.append({"cart_name": f"벽부형 브라켓 ({wall_arm_type})", "display_name": f"벽부형 브라켓 ({wall_arm_type})", "unit_price": w_price, "qty_per_main": 1, "total_per_main": w_price, "group": "폴의 형태"})
                else:
                    zero_options.append({"cart_name": f"벽부형 브라켓 ({wall_arm_type})", "display_name": f"벽부형 브라켓 ({wall_arm_type})"})
                
                st.markdown("<div style='margin-top:10px; font-weight:bold; color:#555;'>👉 암(Arm) 적용 여부</div>", unsafe_allow_html=True)
                wall_has_arm = st.radio("암(Arm) 적용", ["적용 안 함", "ㄱ형 암 적용"], index=0, horizontal=True, key=f"wall_has_arm_{rk}", label_visibility="collapsed")

                if wall_arm_type == "L형":
                    st.markdown("<div style='font-size:14px; margin-top:10px; margin-bottom:5px; color:#555;'>👉 벽 이격 거리(가로) (mm)</div>", unsafe_allow_html=True)
                    wc1, wc2 = st.columns([7, 3])
                    wall_dist = wc1.text_input("이격거리", placeholder="숫자 입력", key=f"wall_dist_{rk}", label_visibility="collapsed")
                    applied = wc2.button("확인", key=f"btn_wall_{rk}")
                    val_digits = "".join(filter(str.isdigit, str(st.session_state.get(f"wall_dist_{rk}", ""))))
                    if applied or val_digits:
                        if val_digits:
                            zero_options.append({"cart_name": f"이격거리: {val_digits}mm", "display_name": f"이격거리: {val_digits}mm"})
                            show_cam = True
                        elif applied: 
                            st.warning("⚠️ 숫자를 입력해 주세요.")
                            show_cam = False
                    else:
                        show_cam = False

            has_arm = (arm_type in ["ㄱ형 (암 1EA)", "T형 (암 2EA)"]) or (arm_type == "벽부형" and wall_has_arm == "ㄱ형 암 적용")

            if has_arm:
                arm_df = options_df[(options_df['적용 카테고리'].astype(str).str.replace(" ", "").str.contains(f"{cat_no_space}|CCTV폴", regex=True)) & 
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
                            arm_qty = 2 if arm_type == "T형 (암 2EA)" else 1
                            total_a_price = a_unit_price * arm_qty
                            priced_options.append({"cart_name": f"{sel_arm_len}mm ({arm_qty}개)", "display_name": f"암 길이: {sel_arm_len}mm (x{arm_qty})", "unit_price": a_unit_price, "qty_per_main": arm_qty, "total_per_main": total_a_price, "group": "암길이"})

            # --- 3. 설치할 카메라의 형태 선택 (스피드돔 완전 삭제) ---
            main_part, arm_part, arm_part_right, arm_part_left = None, None, None, None
            cam_main, cam_arm, cam_arm_right, cam_arm_left = "설치 안 함", "설치 안 함", "설치 안 함", "설치 안 함"
            
            # 카메라 형태 옵션 리스트 고정
            cam_opts = ["설치 안 함", "뷸렛카메라", "하우징카메라"]
            
            if arm_type == "기본형(I형)" or (arm_type == "벽부형" and wall_has_arm == "적용 안 함"):
                if arm_type == "기본형(I형)" or show_cam:
                    st.markdown("<div class='option-group-title'>📁 설치할 카메라의 형태</div>", unsafe_allow_html=True)
                    cam_main = st.radio("설치할 카메라의 형태", cam_opts, index=0, horizontal=True, key=f"cam_main_{rk}", label_visibility="collapsed")
                    if cam_main != "설치 안 함": main_part = render_custom_cctv_camera_parts(cam_main, "카메라 부착", f"main_{rk}")
            
            elif arm_type == "벽부형" and wall_has_arm == "ㄱ형 암 적용":
                if show_cam:
                    st.markdown("<div class='option-group-title'>📁 설치할 카메라의 형태</div>", unsafe_allow_html=True)
                    
                    st.markdown("<div style='margin-top:10px; font-weight:bold; color:#555;'>👉 메인 브라켓 상부에 설치할 카메라 형태</div>", unsafe_allow_html=True)
                    cam_main = st.radio("메인 브라켓 상부에 설치할 카메라 형태", cam_opts, index=0, horizontal=True, key=f"cam_main_wall_arm_{rk}", label_visibility="collapsed")
                    if cam_main != "설치 안 함": main_part = render_custom_cctv_camera_parts(cam_main, "메인 브라켓 상부", f"main_wall_arm_{rk}")
                    
                    st.markdown("<div style='margin-top:15px; font-weight:bold; color:#555;'>👉 암(Arm)에 설치할 카메라 형태</div>", unsafe_allow_html=True)
                    cam_arm = st.radio("암(Arm)에 설치할 카메라 형태", cam_opts, index=0, horizontal=True, key=f"cam_arm_wall_arm_{rk}", label_visibility="collapsed")
                    if cam_arm != "설치 안 함": arm_part = render_custom_cctv_camera_parts(cam_arm, "암(Arm)", f"arm_wall_arm_{rk}")
            else:
                st.markdown("<div class='option-group-title'>📁 설치할 카메라의 형태</div>", unsafe_allow_html=True)
                
                st.markdown("<div style='margin-top:10px; font-weight:bold; color:#555;'>👉 메인 브라켓 상부에 설치할 카메라 형태</div>", unsafe_allow_html=True)
                cam_main = st.radio("메인 브라켓 상부에 설치할 카메라 형태", cam_opts, index=0, horizontal=True, key=f"cam_main_{rk}", label_visibility="collapsed")
                if cam_main != "설치 안 함": main_part = render_custom_cctv_camera_parts(cam_main, "메인 브라켓 상부", f"main_{rk}")
                
                if arm_type == "T형 (암 2EA)":
                    st.markdown("<div style='margin-top:15px; font-weight:bold; color:#555;'>👉 우측 암(ARM)에 설치할 카메라의 형태</div>", unsafe_allow_html=True)
                    cam_arm_right = st.radio("우측 암(ARM)에 설치할 카메라의 형태", cam_opts, index=0, horizontal=True, key=f"cam_arm_r_{rk}", label_visibility="collapsed")
                    if cam_arm_right != "설치 안 함": arm_part_right = render_custom_cctv_camera_parts(cam_arm_right, "우측 암(ARM)", f"arm_r_{rk}")
                    
                    st.markdown("<div style='margin-top:15px; font-weight:bold; color:#555;'>👉 좌측 암(ARM)에 설치할 카메라의 형태</div>", unsafe_allow_html=True)
                    cam_arm_left = st.radio("좌측 암(ARM)에 설치할 카메라의 형태", cam_opts, index=0, horizontal=True, key=f"cam_arm_l_{rk}", label_visibility="collapsed")
                    if cam_arm_left != "설치 안 함": arm_part_left = render_custom_cctv_camera_parts(cam_arm_left, "좌측 암(ARM)", f"arm_l_{rk}")
                else: # ㄱ형
                    st.markdown("<div style='margin-top:15px; font-weight:bold; color:#555;'>👉 암(Arm)에 설치할 카메라 형태</div>", unsafe_allow_html=True)
                    cam_arm = st.radio("암(Arm)에 설치할 카메라 형태", cam_opts, index=0, horizontal=True, key=f"cam_arm_{rk}", label_visibility="collapsed")
                    if cam_arm != "설치 안 함": arm_part = render_custom_cctv_camera_parts(cam_arm, "암(Arm)", f"arm_{rk}")
            
            # 카메라 부품 단가 처리
            part_counts = {}
            if main_part: part_counts[main_part] = part_counts.get(main_part, 0) + 1
            
            if arm_type == "T형 (암 2EA)":
                if arm_part_right: part_counts[arm_part_right] = part_counts.get(arm_part_right, 0) + 1
                if arm_part_left: part_counts[arm_part_left] = part_counts.get(arm_part_left, 0) + 1
            else:
                if arm_part:
                    part_counts[arm_part] = part_counts.get(arm_part, 0) + 1
                
            selected_cam_parts = list(part_counts.keys())
                
            for part, count in part_counts.items():
                if part in ["뷸렛카메라박스", "알루미늄 각도기(기본)"]:
                    base_name, add_name = ("뷸렛카메라박스(변경)", "뷸렛카메라박스(추가)") if part == "뷸렛카메라박스" else ("알루미늄 각도기(기본)", "알루미늄 각도기(추가)")
                    base_p, add_p = get_opt_price("카메라 부착 부품", base_name), get_opt_price("카메라 부착 부품", add_name)
                    
                    # 스피드돔이 없어졌으므로 모든 부착물은 '추가' 옵션(단가 적용)으로 일괄 처리합니다.
                    if count > 0: 
                        priced_options.append({"cart_name": add_name, "display_name": f"{add_name} ({count}EA)", "unit_price": add_p, "qty_per_main": count, "total_per_main": add_p * count, "group": "카메라 부착 부품"})
                else:
                    base_p = get_opt_price("카메라 부착 부품", part)
                    priced_options.append({"cart_name": part, "display_name": f"{part} (x{count})", "unit_price": base_p, "qty_per_main": count, "total_per_main": base_p * count, "group": "카메라 부착 부품"})

            # --- 4. 특별 주문 사항 (흔들림 방지, 앙카베이스 제외됨) ---
            utils.render_generic_groups(cat_no_space, options_df, rk, priced_options, zero_options, preview_images)

        # --- 5. 최종 이미지 파일명 매칭 로직 ---
        combo_names = []
        if arm_type == "벽부형": arm_kw = f"벽부형-{wall_arm_type}"
        else: arm_kw = "기본형" if "기본형" in str(arm_type) else ("ㄱ형" if "ㄱ형" in str(arm_type) else "T형")
        
        def get_cam_img_kw(cam_val, part_val):
            if not cam_val or cam_val == "설치 안 함": return ""
            if cam_val == "뷸렛카메라" and part_val == "알루미늄 각도기(기본)":
                return "하우징"
            return cam_val.replace("카메라", "")

        main_cam_kw = get_cam_img_kw(cam_main, main_part)
        arm_cam_kw = get_cam_img_kw(cam_arm, arm_part)

        if arm_type == "벽부형":
            if wall_has_arm == "ㄱ형 암 적용":
                arm_kw += "-ㄱ형"
                main_k = main_cam_kw if main_cam_kw else "없음"
                arm_k = arm_cam_kw if arm_cam_kw else "없음"
                base_prefix = f"{cat_no_space}-{arm_kw}-{main_k}-{arm_k}"
                combo_names.extend([base_prefix, f"{cat_no_space}-{arm_kw}"])
                base_cctv = base_prefix
            else:
                base_prefix = f"{cat_no_space}-{arm_kw}"
                base_cctv = f"{base_prefix}-{main_cam_kw}" if main_cam_kw else base_prefix
                combo_names.extend([base_cctv, f"{cat_no_space}-{arm_kw}"])
                
        elif arm_kw != "기본형":
            if arm_kw == "T형":
                main_k = get_cam_img_kw(cam_main, main_part) if get_cam_img_kw(cam_main, main_part) else "없음"
                right_k = get_cam_img_kw(cam_arm_right, arm_part_right) if get_cam_img_kw(cam_arm_right, arm_part_right) else "없음"
                left_k = get_cam_img_kw(cam_arm_left, arm_part_left) if get_cam_img_kw(cam_arm_left, arm_part_left) else "없음"
                base_prefix = f"{cat_no_space}-{arm_kw}-{main_k}-{right_k}-{left_k}"
                combo_names.append(base_prefix)
                base_cctv = base_prefix
            else: # ㄱ형
                base_prefix = f"{cat_no_space}-{arm_kw}"
                base_prefix += f"-{main_cam_kw}" if main_cam_kw else "-없음"
                
                if arm_cam_kw:
                    combo_names.extend([f"{base_prefix}-{arm_cam_kw}", base_prefix])
                else:
                    combo_names.append(base_prefix)
                    
                base_cctv = f"{cat_no_space}-{arm_kw}"
                if main_cam_kw: base_cctv += f"-{main_cam_kw}"
                elif arm_cam_kw: base_cctv += f"-없음-{arm_cam_kw}"
                combo_names.append(f"{cat_no_space}-{arm_kw}")
        else: # 기본형
            base_prefix = f"{cat_no_space}-{arm_kw}"
            if main_cam_kw: combo_names.append(f"{base_prefix}-{main_cam_kw}")
            else: combo_names.append(base_prefix)
                
            base_cctv = f"{cat_no_space}-{arm_kw}"
            if main_cam_kw: base_cctv += f"-{main_cam_kw}"
            elif arm_cam_kw: base_cctv += f"-없음-{arm_cam_kw}"
            combo_names.append(f"{cat_no_space}-{arm_kw}")
            
        part_kws = [re.sub(r'\(.*?\)', '', p).strip() for p in selected_cam_parts]
        
        if arm_kw == "T형":
            for part in part_kws:
                combo_names.append(f"{base_cctv}-{part}")
        elif arm_cam_kw:
            for part in part_kws:
                combo_names.extend([f"{base_cctv}-{arm_cam_kw}-{part}", f"{base_cctv}-{part}"])
        else:
            for part in part_kws:
                combo_names.append(f"{base_cctv}-{part}")

        combo_names.append(cat_no_space)
        combo_names = list(dict.fromkeys(combo_names))
        
        valid_paths = utils.display_images(combo_names, priced_options, zero_options, preview_images, img_col, cat_no_space)
        return is_main_ready, base_price, product_specs, valid_paths, priced_options, zero_options

    return False, 0, "", [], [], []