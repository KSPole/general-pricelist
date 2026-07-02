import streamlit as st
import pandas as pd
import utils

def render(filtered_products, options_df, rk, cat_no_space):
    is_main_ready, base_price, product_specs = False, 0, ""
    preview_images, priced_options, zero_options = [], [], []

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

    # 👉 [핵심 변경 1] 화면 분할을 규격 완료 판단 바깥으로 배치 (이미지 실시간 선표시 목적)
    st.markdown("<hr style='margin: 15px 0px;'>", unsafe_allow_html=True)
    opt_col, img_col = st.columns([5.5, 4.5])
    
    # 👉 [핵심 변경 2] 카메라 부착 방식 선택 전 기본 표시용 키워드를 "직결"로 세팅
    cam_kw = "직결" 

    with opt_col:
        if is_main_ready:
            st.markdown("<h2>2. 옵션 선택</h2>", unsafe_allow_html=True)
            
            def get_opt_price(group_kw, opt_kw):
                try:
                    df_opt = options_df[(options_df['적용 카테고리'].astype(str).str.contains('옥상', na=False)) & 
                                        (options_df['추가 선택-1'].astype(str).str.contains(opt_kw, na=False))]
                    if not df_opt.empty: return int(df_opt.iloc[0]['단가'])
                except: pass
                return 0

            # 카메라 부착 방식 렌더링 함수
            def render_roof_cam():
                st.markdown("<div class='option-group-title'>📁 카메라 부착 방식</div>", unsafe_allow_html=True)
                cam_opts = ["직결형", "뷸렛박스형", "각도기"]
                cam_att = st.radio("카메라 부착 방식", cam_opts, index=0, horizontal=True, label_visibility="collapsed", key=f"rcam_{rk}")
                kw, p = "직결", 0
                if cam_att == "뷸렛박스형":
                    kw = "뷸렛박스"
                    row_opt = options_df[options_df['추가 선택-1'].astype(str).str.replace(" ","").str.contains("뷸렛카메라박스", na=False)]
                    if not row_opt.empty: p = int(row_opt.iloc[0]['단가'])
                elif cam_att == "각도기":
                    kw = "하우징"
                    row_opt = options_df[options_df['추가 선택-1'].astype(str).str.replace(" ","").str.contains("기본각도기", na=False)]
                    if not row_opt.empty: p = int(row_opt.iloc[0]['단가'])
                elif cam_att == "직결형":
                    kw = "직결"
                
                if cam_att in ["뷸렛박스형", "각도기"]: 
                    priced_options.append({"cart_name": cam_att, "display_name": f"부착 방식: {cam_att}", "unit_price": p, "qty_per_main": 1, "total_per_main": p, "group": "카메라부착방식"})
                elif cam_att == "직결형": 
                    zero_options.append({"cart_name": "직결형", "display_name": "부착 방식: 직결형"})
                return kw

            # [i형 추가 옵션]
            if roof_base == "i형":
                st.markdown("<div class='option-group-title'>📁 옥상가이드 브라켓</div>", unsafe_allow_html=True)
                rg_opts = ["200mm 가이드 (기본)", "120mm 가이드"]
                rg = st.radio("가이드", rg_opts, index=0, horizontal=True, label_visibility="collapsed", key=f"rg_{rk}")
                rg_p = get_opt_price("옥상가이드", "120" if "120" in rg else "200")
                priced_options.append({"cart_name": rg, "display_name": f"옥상가이드: {rg}", "unit_price": rg_p, "qty_per_main": 1, "total_per_main": rg_p, "group": "옥상가이드"})
                cam_kw = render_roof_cam()

            # [ㄱ형 추가 옵션]
            elif roof_base == "ㄱ형":
                if roof_g_type != "기본형":
                    p = get_opt_price("형태", roof_g_type[:2])
                    priced_options.append({"cart_name": roof_g_type, "display_name": f"형태: {roof_g_type}", "unit_price": p, "qty_per_main": 1, "total_per_main": p, "group": "ㄱ형형태"})
                
                if roof_g_type == "기본형":
                    st.markdown("<div class='option-group-title'>📁 옥상가이드 브라켓</div>", unsafe_allow_html=True)
                    rg_opts = ["200mm 가이드 (기본)", "120mm 가이드"]
                    rg = st.radio("가이드", rg_opts, index=0, horizontal=True, label_visibility="collapsed", key=f"rg_{rk}")
                    p = get_opt_price("옥상가이드", "120" if "120" in rg else "200")
                    priced_options.append({"cart_name": rg, "display_name": f"옥상가이드: {rg}", "unit_price": p, "qty_per_main": 1, "total_per_main": p, "group": "옥상가이드"})
                    cam_kw = render_roof_cam()
                
                elif roof_g_type == "일반 벽 이격 브라켓":
                    gap_dist = st.text_input("👉 이격 길이 (mm)", placeholder="숫자만 입력", key=f"gdist_{rk}")
                    if gap_dist: zero_options.append({"cart_name": f"일반벽 이격: {gap_dist}mm", "display_name": f"일반벽 이격: {gap_dist}mm"})
                    cam_kw = render_roof_cam()

                elif roof_g_type == "빗각 벽 이격 브라켓":
                    c1, c2 = st.columns(2)
                    gap_ang = c1.text_input("👉 빗각 벽의 각도", placeholder="숫자만", key=f"gang_{rk}")
                    gap_dist = c2.text_input("👉 이격 길이 (mm)", placeholder="숫자만", key=f"gdist_{rk}")
                    if gap_ang and gap_dist: zero_options.append({"cart_name": f"빗각벽 이격: 각도 {gap_ang} / 길이 {gap_dist}mm", "display_name": f"빗각벽 이격: 각도 {gap_ang} / 길이 {gap_dist}mm"})
                    cam_kw = render_roof_cam()
                
                elif roof_g_type == "1단+2단형":
                    t_opts = ["옥상 바닥 설치형", "옥상 난간 설치형"]
                    tier_type = st.radio("설치 위치", t_opts, index=0, horizontal=True, key=f"tier_{rk}")
                    if tier_type == "옥상 난간 설치형":
                        t1, t2 = st.columns(2)
                        t_h = t1.text_input("👉 바닥 판재 1번(세로) 사이즈", placeholder="숫자만", key=f"th_{rk}")
                        t_w = t2.text_input("👉 2번(가로) 사이즈", placeholder="숫자만", key=f"tw_{rk}")
                        if t_h and t_w: zero_options.append({"cart_name": f"난간 판재: 세로{t_h} x 가로{t_w}", "display_name": f"난간 판재: 세로{t_h} x 가로{t_w}"})
                    cam_kw = render_roof_cam()
                
                elif roof_g_type == "난간 샌드위치형":
                    st.info("💡 난간 구조에 대하여 담당자와 협의 필요")
                    zero_options.append({"cart_name": "난간 구조에 대하여 담당자와 협의 필요", "display_name": "난간 구조에 대하여 담당자와 협의 필요"})
                    cam_kw = render_roof_cam()

            # 추가 부속 장치 (점검구 및 가로파이프 이중 고정 장치)
            st.markdown("<div class='option-group-title'>📁 추가 부속 장치</div>", unsafe_allow_html=True)
            chk_hole = st.radio("점검구", ["선택 안 함", "점검구"], index=0, horizontal=True, key=f"chk_hole_{rk}")
            if chk_hole == "점검구":
                df_chk = options_df[(options_df['적용 카테고리'].astype(str).str.contains('옥상', na=False)) & (options_df['추가 선택-1'].astype(str).str.contains('점검구', na=False))]
                chk_p = int(df_chk.iloc[0]['단가']) if not df_chk.empty else 0
                priced_options.append({"cart_name": "점검구", "display_name": "추가: 점검구", "unit_price": chk_p, "qty_per_main": 1, "total_per_main": chk_p, "group": "부속장치"})

            h_pipe = st.radio("가로파이프 고정 브라켓", ["선택 안 함", "가로파이프 고정 장치 추가"], index=0, horizontal=True, key=f"hpipe_{rk}")
            if h_pipe == "가로파이프 고정 장치 추가":
                df_hp = options_df[(options_df['적용 카테고리'].astype(str).str.contains('옥상', na=False)) & (options_df['옵션 구분(그룹명)'].astype(str).str.contains('가로파이프', na=False))]
                hp_p = int(df_hp.iloc[0]['단가']) if not df_hp.empty else 5000
                priced_options.append({"cart_name": "가로파이프 고정", "display_name": "추가: 가로파이프 이중 고정 장치", "unit_price": hp_p, "qty_per_main": 1, "total_per_main": hp_p, "group": "부속장치"})

            # 추가 공통 옵션 (마감캡 등) 로드
            utils.render_generic_groups(cat_no_space, options_df, rk, priced_options, zero_options, preview_images)
        else:
            # 👉 길이 입력 전 안내 문구
            st.info("💡 상단에서 가로/세로 규격(길이)을 입력하시면 상세 옵션 단가 조절창이 열립니다.")

    # -------------------------------------------------------------------------
    # 👉 [핵심 변경 3] 지정하신 이미지 파일명 조합 조건 처리 (실시간 렌더링)
    # -------------------------------------------------------------------------
    combo_names = []
    
    cam_suffix = ""
    if cam_kw == "직결": cam_suffix = "직결"
    elif cam_kw == "뷸렛박스": cam_suffix = "뷸렛박스"
    elif cam_kw == "하우징": cam_suffix = "하우징"
    
    if roof_base == "i형":
        if cam_suffix: combo_names.append(f"옥상브라켓-{cam_suffix}")
        combo_names.append("옥상브라켓-i형")
        
    elif roof_base == "ㄱ형":
        if roof_g_type == "기본형":
            if cam_suffix: combo_names.append(f"옥상브라켓-ㄱ형-{cam_suffix}")
        elif roof_g_type == "일반 벽 이격 브라켓":
            if cam_suffix: combo_names.append(f"옥상브라켓-ㄱ형-일반벽-{cam_suffix}")
        elif roof_g_type == "빗각 벽 이격 브라켓":
            if cam_suffix: combo_names.append(f"옥상브라켓-ㄱ형-빗각벽-{cam_suffix}")
        elif roof_g_type == "1단+2단형":
            cam_suffix_12 = "직결형" if cam_kw == "직결" else cam_suffix
            if cam_suffix_12: combo_names.append(f"옥상브라켓-ㄱ형-12단-{cam_suffix_12}")
        elif roof_g_type == "난간 샌드위치형":
            if cam_suffix: combo_names.append(f"옥상브라켓-ㄱ형-샌드위치-{cam_suffix}")
            
        combo_names.append("옥상브라켓-ㄱ형")

    combo_names.append("옥상브라켓")
    combo_names = list(dict.fromkeys(combo_names))

    # 👉 이미지 컴포넌트를 호출하여 우측 컬럼(img_col)에 항상 실시간 표시
    valid_paths = utils.display_images(combo_names, priced_options, zero_options, preview_images, img_col, cat_no_space)
    
    if is_main_ready:
        return is_main_ready, base_price, product_specs, valid_paths, priced_options, zero_options

    return False, 0, "", [], [], []