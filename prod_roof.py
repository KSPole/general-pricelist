import streamlit as st
import pandas as pd
import utils
import re

def render(filtered_products, options_df, rk, cat_no_space):
    is_main_ready, base_price, product_specs = False, 0, ""
    preview_images, priced_options, zero_options = [], [], []

    def get_opt_price(group_name, option_name=""):
        g_clean = re.sub(r'\s+', '', str(group_name))
        o_clean = re.sub(r'\s+', '', str(option_name)) if option_name else ""
        
        # 1. 옥상 카테고리 우선 탐색
        df_roof = options_df[options_df['적용 카테고리'].astype(str).str.replace(" ", "").str.contains("옥상", regex=False)]
        for idx, row in df_roof.iterrows():
            row_g = re.sub(r'\s+', '', str(row.get('옵션 구분(그룹명)', '')))
            row_o = re.sub(r'\s+', '', str(row.get('추가 선택-1', '')))
            
            if o_clean == "":
                if row_g == g_clean:
                    val = row.get('단가', 0)
                    if pd.notna(val): return int(float(val))
            else:
                if row_g == g_clean and o_clean in row_o:
                    val = row.get('단가', 0)
                    if pd.notna(val): return int(float(val))
                
        # 2. 못 찾으면 전체 탐색
        for idx, row in options_df.iterrows():
            row_g = re.sub(r'\s+', '', str(row.get('옵션 구분(그룹명)', '')))
            row_o = re.sub(r'\s+', '', str(row.get('추가 선택-1', '')))
            
            if o_clean == "":
                if row_g == g_clean:
                    val = row.get('단가', 0)
                    if pd.notna(val): return int(float(val))
            else:
                if row_g == g_clean and o_clean in row_o:
                    val = row.get('단가', 0)
                    if pd.notna(val): return int(float(val))
        return 0

    st.markdown("<div style='font-size:15px; font-weight:bold; color:#2e6c80; margin-bottom:5px;'>1️⃣ 브라켓 형태 선택</div>", unsafe_allow_html=True)
    roof_base = st.radio("브라켓 형태 선택", ["i형", "ㄱ형"], index=0, horizontal=True, key=f"r_base_{rk}", label_visibility="collapsed")
    roof_g_type = "기본형" # 초기값
    
    if roof_base == "i형":
        i_len = st.number_input("👉 가로 (밖으로 나가는 길이) (mm)", min_value=0, step=10, value=None, placeholder="숫자만 입력하세요", key=f"i_len_{rk}")
        
        if i_len is not None and i_len > 0:
            sub_df = filtered_products[filtered_products['제품명'].astype(str).str.contains('i형', na=False)]
            row = sub_df[(sub_df['합산 최소'] <= i_len) & (sub_df['합산 최대'] >= i_len)]
            if not row.empty:
                base_price = int(row.iloc[0]['단가'])
                product_specs = f"i형 / 가로: {int(i_len)}mm"
                is_main_ready = True
            else:
                st.warning("⚠️ 입력하신 길이에 해당하는 기성품 단가가 없습니다. (단가표 범위 초과)")
                
    elif roof_base == "ㄱ형":
        g_opts = ["기본형", "일반 벽 이격 브라켓", "빗각 벽 이격 브라켓", "1단+2단형", "난간 샌드위치형"]
        roof_g_type = st.radio("👉 ㄱ형 세부 형태 선택", g_opts, index=0, horizontal=True, key=f"rg_type_{rk}")
        
        st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        
        g_h = c1.number_input("👉 세로 (벽 부착 길이) (mm)", min_value=0, step=10, value=None, placeholder="숫자만 입력하세요", key=f"g_h_{rk}")
        g_w = c2.number_input("👉 가로 (밖으로 나가는 길이) (mm)", min_value=0, step=10, value=None, placeholder="숫자만 입력하세요", key=f"g_w_{rk}")
        
        if roof_g_type == "일반 벽 이격 브라켓":
            st.text_input("👉 이격 길이 (mm)", placeholder="숫자만 입력하세요", key=f"gdist_{rk}")
        elif roof_g_type == "빗각 벽 이격 브라켓":
            c3, c4 = st.columns(2)
            c3.text_input("👉 빗각 벽의 각도", placeholder="숫자만 입력하세요", key=f"gang_{rk}")
            c4.text_input("👉 이격 길이 (mm)", placeholder="숫자만 입력하세요", key=f"gdist_{rk}")
        
        if g_w is not None and g_h is not None and g_w > 0 and g_h > 0:
            g_sum = g_w + g_h
            sub_df = filtered_products[filtered_products['제품명'].astype(str).str.contains('ㄱ형', na=False)]
            row = sub_df[(sub_df['합산 최소'] <= g_sum) & (sub_df['합산 최대'] >= g_sum)]
            if not row.empty:
                base_price = int(row.iloc[0]['단가'])
                product_specs = f"ㄱ형 ({roof_g_type}) / 세로: {int(g_h)}mm x 가로: {int(g_w)}mm (합산 {int(g_sum)}mm)"
                is_main_ready = True
            else:
                st.warning("⚠️ 입력하신 합산 길이에 해당하는 기성품 단가가 없습니다. (단가표 범위 초과)")

    st.markdown("<hr style='margin: 15px 0px;'>", unsafe_allow_html=True)
    opt_col, img_col = st.columns([5.5, 4.5])
    
    # 💡 이미지 파일명에 쓰일 접미사
    cam_suffix = "" 

    with opt_col:
        if is_main_ready:
            st.markdown("<h2>2. 옵션 선택</h2>", unsafe_allow_html=True)
            
            st.markdown("<div class='option-group-title'>📁 카메라 형태</div>", unsafe_allow_html=True)
            cam_opts = ["선택 안 함", "뷸렛카메라", "하우징카메라", "스피드돔카메라"]
            cam_type = st.radio("카메라 형태", cam_opts, index=0, horizontal=True, key=f"cam_{rk}", label_visibility="collapsed")
            
            sel_cam_part = None
            
            if cam_type != "선택 안 함":
                parts = []
                if cam_type == "뷸렛카메라":
                    parts = ["직결형", "뷸렛카메라박스"]
                elif cam_type == "하우징카메라":
                    parts = ["선택 안 함", "알루미늄 각도기", "스텐 각도기", "번호인식 각도기"]
                elif cam_type == "스피드돔카메라" or cam_type == "스피드돔 카메라":
                    parts = ["선택 안 함", "스피드돔 브라켓 부착용 판재", "40A소켓 (회전형으로 부착시)"]
                    
                if parts:
                    st.markdown(f"<div style='font-size:14px; margin-top:5px; margin-bottom:2px; color:#555;'>└ 카메라 부착 방식 선택</div>", unsafe_allow_html=True)
                    sel_cam_part = st.radio("카메라 부착 방식", parts, index=0, horizontal=True, key=f"cpart_{rk}", label_visibility="collapsed")
                    
                    if sel_cam_part == "선택 안 함":
                        sel_cam_part = None

            # 💡 [핵심] 카메라 및 옵션에 따른 파일명 매칭 단어(cam_suffix) 지정
            if cam_type != "선택 안 함":
                if cam_type == "뷸렛카메라":
                    if sel_cam_part == "뷸렛카메라박스":
                        cam_suffix = "뷸렛"
                    else: 
                        cam_suffix = "직결"
                elif cam_type == "하우징카메라":
                    cam_suffix = "하우징"
                elif cam_type in ["스피드돔카메라", "스피드돔 카메라"]:
                    if sel_cam_part and "40A" in sel_cam_part:
                        cam_suffix = "40"
                    elif sel_cam_part and "판재" in sel_cam_part:
                        cam_suffix = "스피드돔 판재"
                    else:
                        cam_suffix = "직결"

                if sel_cam_part:
                    if sel_cam_part == "직결형":
                        zero_options.append({"cart_name": "직결형", "display_name": "부착 방식: 직결형"})
                    else:
                        base_name_for_search = sel_cam_part
                            
                        p_price = get_opt_price("카메라 부착 방식", base_name_for_search)
                        
                        if p_price == 0 and "알루미늄" in base_name_for_search:
                            p_price = get_opt_price("카메라 부착 방식", "알류미늄 각도기")
                        if p_price == 0 and "알루미늄" in base_name_for_search:
                            p_price = get_opt_price("카메라 부착 방식", "기본각도기")
                            
                        if p_price == 0:
                            p_price = get_opt_price("카메라 부착 부품", base_name_for_search)

                        if p_price == 0 and "알루미늄" in base_name_for_search:
                            zero_options.append({"cart_name": sel_cam_part, "display_name": f"부착 방식: {sel_cam_part} (포함)", "qty": 1, "qty_per_main": 1})
                        elif p_price == 0:
                            zero_options.append({"cart_name": sel_cam_part, "display_name": f"부착 방식: {sel_cam_part}", "qty": 1, "qty_per_main": 1})
                        else:
                            priced_options.append({"cart_name": f"{sel_cam_part} (1EA)", "display_name": f"부착 방식: {sel_cam_part}", "unit_price": p_price, "qty_per_main": 1, "qty": 1, "total_per_main": p_price, "group": "카메라 부착 방식"})

            # [i형 추가 옵션]
            if roof_base == "i형":
                st.markdown("<div class='option-group-title'>📁 옥상가이드 브라켓</div>", unsafe_allow_html=True)
                rg_opts = ["200mm 가이드 (기본)", "120mm 가이드"]
                rg = st.radio("가이드", rg_opts, index=0, horizontal=True, label_visibility="collapsed", key=f"rg_{rk}")
                rg_p = get_opt_price("옥상가이드", "120" if "120" in rg else "200")
                priced_options.append({"cart_name": f"{rg} (1EA)", "display_name": f"옥상가이드: {rg}", "unit_price": rg_p, "qty_per_main": 1, "qty": 1, "total_per_main": rg_p, "group": "옥상가이드"})

            # [ㄱ형 추가 옵션]
            elif roof_base == "ㄱ형":
                if roof_g_type != "기본형":
                    p = 0
                    if roof_g_type == "일반 벽 이격 브라켓": p = get_opt_price("일반벽이격브라켓")
                    elif roof_g_type == "빗각 벽 이격 브라켓": p = get_opt_price("빗각벽이격브라켓")
                    elif roof_g_type == "1단+2단형": p = get_opt_price("1단/2단회전형")
                    
                    if p > 0: priced_options.append({"cart_name": f"{roof_g_type} (1EA)", "display_name": f"형태: {roof_g_type}", "unit_price": p, "qty_per_main": 1, "qty": 1, "total_per_main": p, "group": "ㄱ형형태"})
                    else: zero_options.append({"cart_name": roof_g_type, "display_name": f"형태: {roof_g_type}", "qty": 1, "qty_per_main": 1})
                
                if roof_g_type == "기본형":
                    st.markdown("<div class='option-group-title'>📁 옥상가이드 브라켓</div>", unsafe_allow_html=True)
                    rg_opts = ["200mm 가이드 (기본)", "120mm 가이드"]
                    rg = st.radio("가이드", rg_opts, index=0, horizontal=True, label_visibility="collapsed", key=f"rg_{rk}")
                    p = get_opt_price("옥상가이드", "120" if "120" in rg else "200")
                    priced_options.append({"cart_name": f"{rg} (1EA)", "display_name": f"옥상가이드: {rg}", "unit_price": p, "qty_per_main": 1, "qty": 1, "total_per_main": p, "group": "옥상가이드"})
                
                elif roof_g_type == "일반 벽 이격 브라켓":
                    gap_dist = st.session_state.get(f"gdist_{rk}", "")
                    if gap_dist: zero_options.append({"cart_name": f"일반벽 이격: {gap_dist}mm", "display_name": f"일반벽 이격: {gap_dist}mm"})

                elif roof_g_type == "빗각 벽 이격 브라켓":
                    gap_ang = st.session_state.get(f"gang_{rk}", "")
                    gap_dist = st.session_state.get(f"gdist_{rk}", "")
                    if gap_ang and gap_dist: zero_options.append({"cart_name": f"빗각벽 이격: 각도 {gap_ang} / 길이 {gap_dist}mm", "display_name": f"빗각벽 이격: 각도 {gap_ang} / 길이 {gap_dist}mm"})
                
                elif roof_g_type == "1단+2단형":
                    t_opts = ["옥상 바닥 설치형", "옥상 난간 설치형"]
                    tier_type = st.radio("설치 위치", t_opts, index=0, horizontal=True, key=f"tier_{rk}")
                    if tier_type == "옥상 난간 설치형":
                        t1, t2 = st.columns(2)
                        t_h = t1.text_input("👉 바닥 판재 1번(세로) 사이즈", placeholder="숫자만", key=f"th_{rk}")
                        t_w = t2.text_input("👉 2번(가로) 사이즈", placeholder="숫자만", key=f"tw_{rk}")
                        if t_h and t_w: zero_options.append({"cart_name": f"난간 판재: 세로{t_h} x 가로{t_w}", "display_name": f"난간 판재: 세로{t_h} x 가로{t_w}"})
                
                elif roof_g_type == "난간 샌드위치형":
                    st.info("💡 난간 구조에 대하여 담당자와 협의 필요")
                    zero_options.append({"cart_name": "난간 구조에 대하여 담당자와 협의 필요", "display_name": "난간 구조에 대하여 담당자와 협의 필요"})

            st.markdown("<div class='option-group-title'>📁 추가 부속 장치</div>", unsafe_allow_html=True)
            chk_hole = st.radio("점검구", ["선택 안 함", "점검구"], index=0, horizontal=True, key=f"chk_hole_{rk}")
            if chk_hole == "점검구":
                chk_p = get_opt_price("점검구")
                if chk_p == 0: chk_p = 5000
                priced_options.append({"cart_name": "점검구 (1EA)", "display_name": "추가: 점검구", "unit_price": chk_p, "qty_per_main": 1, "qty": 1, "total_per_main": chk_p, "group": "부속장치"})

            h_pipe = st.radio("가로파이프 고정 브라켓", ["선택 안 함", "가로파이프 고정 장치 추가"], index=0, horizontal=True, key=f"hpipe_{rk}")
            if h_pipe == "가로파이프 고정 장치 추가":
                hp_p = get_opt_price("가로파이프이중고정장치")
                if hp_p == 0: hp_p = 5000
                priced_options.append({"cart_name": "가로파이프 고정 (1EA)", "display_name": "추가: 가로파이프 이중 고정 장치", "unit_price": hp_p, "qty_per_main": 1, "qty": 1, "total_per_main": hp_p, "group": "부속장치"})

            utils.render_generic_groups(cat_no_space, options_df, rk, priced_options, zero_options, preview_images)
        else:
            st.info("💡 상단에서 가로/세로 규격(길이)을 입력하시면 상세 옵션 단가 조절창이 열립니다.")

    # -------------------------------------------------------------------------
    # 💡 [핵심] 옥상 브라켓 이미지 파일명 정밀 생성 로직
    # -------------------------------------------------------------------------
    combo_names = []
    
    if roof_base == "i형":
        if cam_suffix: combo_names.append(f"옥상브라켓-i형-{cam_suffix}")
        combo_names.append("옥상브라켓-i형")
        
    elif roof_base == "ㄱ형":
        if roof_g_type == "기본형":
            if cam_suffix: combo_names.append(f"옥상브라켓-ㄱ형-{cam_suffix}")
            
        elif roof_g_type == "일반 벽 이격 브라켓":
            if cam_suffix: 
                combo_names.append(f"옥상브라켓-ㄱ형-일반벽-{cam_suffix}")
                combo_names.append(f"옥상브라켓-ㄱ형-일반격-{cam_suffix}") # 오타 대비 안전장치
                
        elif roof_g_type == "빗각 벽 이격 브라켓":
            if cam_suffix: combo_names.append(f"옥상브라켓-ㄱ형-빗각벽-{cam_suffix}")
            
        elif roof_g_type == "1단+2단형":
            if cam_suffix: combo_names.append(f"옥상브라켓-ㄱ형-12단-{cam_suffix}")
            
        elif roof_g_type == "난간 샌드위치형":
            if cam_suffix: combo_names.append(f"옥상브라켓-ㄱ형-난간-{cam_suffix}")
            
        combo_names.append("옥상브라켓-ㄱ형")

    combo_names.append("옥상브라켓")
    combo_names = list(dict.fromkeys(combo_names))

    # 💡 각도기가 포함된 옵션 리스트는 이미지 표시 함수로 넘기지 않아서 화면에서 완전 차단합니다.
    display_priced_opts = [opt for opt in priced_options if "각도기" not in str(opt.get('cart_name', ''))]
    display_zero_opts = [opt for opt in zero_options if "각도기" not in str(opt.get('cart_name', ''))]

    valid_paths = utils.display_images(combo_names, display_priced_opts, display_zero_opts, preview_images, img_col, cat_no_space)
    
    if is_main_ready:
        return is_main_ready, base_price, product_specs, valid_paths, priced_options, zero_options

    return False, 0, "", [], [], []