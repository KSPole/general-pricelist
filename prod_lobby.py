import streamlit as st
import pandas as pd
import utils

def render(filtered_products, options_df, rk, cat_no_space):
    is_main_ready, base_price, product_specs = False, 0, ""
    preview_images, priced_options, zero_options, combo_names = [], [], [], []

    # 💡 엑셀의 제품명에서 단가를 찾아오는 함수
    def get_price_by_name(search_kw):
        s_clean = search_kw.replace(" ", "").replace("-", "")
        for idx, row in filtered_products.iterrows():
            r_prod = str(row.get('제품명', '')).replace(" ", "").replace("-", "")
            if s_clean == r_prod:
                val = row.get('단가', 0)
                if pd.notna(val): return int(float(val))
        for idx, row in filtered_products.iterrows():
            r_prod = str(row.get('제품명', '')).replace(" ", "").replace("-", "")
            if s_clean in r_prod:
                val = row.get('단가', 0)
                if pd.notna(val): return int(float(val))
        return 0

    st.markdown("<div style='font-size:15px; font-weight:bold; color:#2e6c80; margin-bottom:5px;'>1️⃣ 메뉴 선택</div>", unsafe_allow_html=True)
    
    main_menu = st.radio("메뉴 선택", ["로비폰/인터폰 함체", "로비폰 보강판"], horizontal=True, key=f"lobby_main_{rk}", label_visibility="collapsed")

    if main_menu == "로비폰/인터폰 함체":
        dev_type = st.radio("👉 기기 종류 선택", ["로비폰", "인터폰"], horizontal=True, key=f"dev_t_{rk}")
        
        st.markdown("<div style='margin-top:10px; font-weight:bold; color:#555;'>👉 로비폰/인터폰 외형 사이즈 <span style='font-size:13px; color:#888;'>(선택사항)</span> (mm)</div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        out_w = c1.number_input("가로", min_value=0, step=10, value=None, placeholder="외형 가로", key=f"ow_{rk}")
        out_h = c2.number_input("세로", min_value=0, step=10, value=None, placeholder="외형 세로", key=f"oh_{rk}")
        depth = c3.number_input("폭", min_value=0, step=10, value=None, placeholder="함체 폭", key=f"od_{rk}")

        st.markdown("<div style='margin-top:10px; font-weight:bold; color:#555;'>👉 로비폰/인터폰 타공 사이즈 <span style='font-size:13px; color:#888;'>(선택사항)</span> (mm)</div>", unsafe_allow_html=True)
        c4, c5 = st.columns(2)
        in_w = c4.number_input("가로 ", min_value=0, step=10, value=None, placeholder="타공 가로", key=f"iw_{rk}")
        in_h = c5.number_input("세로 ", min_value=0, step=10, value=None, placeholder="타공 세로", key=f"ih_{rk}")

        cover_opt = st.radio("👉 방우 커버 여부", ["방우 커버 없음", "방우 커버 있음"], horizontal=True, key=f"cov_{rk}")
        
        inst_type = st.radio("👉 설치 형태", ["벽부형", "자립식"], horizontal=True, key=f"inst_{rk}")
        z_h = None
        if inst_type == "자립식":
            z_h = st.number_input("👉 자립식 높이 (선택사항) (mm)", min_value=0, step=10, value=None, placeholder="자립식 높이", key=f"zh_{rk}")
        
        model_val = st.text_input("👉 로비폰/인터폰 제조사 / 모델명 (선택사항)", placeholder="예: 코맥스 DRC-40K", key=f"m_{rk}")

        # 💡 [핵심] 사이즈 입력과 상관없이 바로 기본 단가 적용 및 장바구니 활성화
        is_main_ready = True
        
        # 💡 기본 함체 단가 적용
        base_price = get_price_by_name(f"{dev_type} 함체")
        
        # 장바구니에 표시될 스펙 텍스트 조립
        specs = f"[{dev_type} 함체] {inst_type}"
        size_strs = []
        if out_w and out_h and depth:
            size_strs.append(f"외형: {int(out_w)}x{int(out_h)} / 폭: {int(depth)}")
        else:
            size_strs.append("외형/폭: 사이즈 협의")
            
        if in_w and in_h:
            size_strs.append(f"타공: {int(in_w)}x{int(in_h)}")
            
        specs += " / " + " / ".join(size_strs)

        if inst_type == "자립식" and z_h: 
            specs += f" / 높이: {int(z_h)}mm"
        if model_val: 
            specs += f" / 모델명: {model_val}"
            
        product_specs = specs
        
        # 💡 [단가 적용] 자립식 선택 시 "자립식 추가 단가" 적용
        if inst_type == "자립식":
            stand_p = get_price_by_name(f"{dev_type} 자립식")
            priced_options.append({
                "cart_name": f"{dev_type} 자립식 추가 (1EA)", 
                "display_name": f"추가: 자립식 스탠드", 
                "unit_price": stand_p, 
                "qty_per_main": 1, 
                "qty": 1, 
                "total_per_main": stand_p, 
                "group": "설치형태"
            })

        # 💡 [단가 적용] 방우 커버 단가 적용
        if cover_opt == "방우 커버 있음":
            cover_p = get_price_by_name(f"{dev_type} 함체 방우커버")
            priced_options.append({"cart_name": f"{dev_type} 방우커버 (1EA)", "display_name": f"추가: {dev_type} 방우 커버", "unit_price": cover_p, "qty_per_main": 1, "qty": 1, "total_per_main": cover_p, "group": "방우커버"})

        # 이미지 파일명 매칭
        if inst_type == "자립식":
            combo_names.append(f"자립식 {dev_type} 함체")
        else:
            if cover_opt == "방우 커버 있음":
                combo_names.append(f"{dev_type} 함체+방우커버")
            else:
                combo_names.append(f"{dev_type} 함체")

    elif main_menu == "로비폰 보강판":
        st.markdown("<div style='margin-top:10px; font-weight:bold; color:#555;'>👉 로비폰 보강판 사이즈 입력 <span style='font-size:13px; color:#888;'>(선택사항)</span> (mm)</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        bw_val = c1.number_input("가로", min_value=0, step=10, value=None, placeholder="가로 입력", key=f"bw_{rk}")
        bh_val = c2.number_input("세로", min_value=0, step=10, value=None, placeholder="세로 입력", key=f"bh_{rk}")

        model_val = st.text_input("👉 로비폰 제조사 / 모델명 (선택사항)", placeholder="예: 코맥스 DRC-40K", key=f"bm_{rk}")
        bend_opt = st.radio("👉 절곡 여부", ["사방 절곡 없음", "사방 절곡 있음"], horizontal=True, key=f"bb_{rk}")

        # 💡 [핵심] 사이즈 입력과 상관없이 바로 기본 단가 적용 및 장바구니 활성화
        is_main_ready = True
        
        # 가로/세로 중 하나라도 400을 초과하면 주문제작 단가로 전환 (단가 0원 표기)
        is_custom = False
        if bw_val is not None and bh_val is not None:
            if bw_val > 400 or bh_val > 400:
                is_custom = True
        
        if is_custom:
            base_price = 0
            product_specs = f"[로비폰 보강판] 가로 {int(bw_val)} x 세로 {int(bh_val)} / {bend_opt} 👉 [주문제작 단가]"
        else:
            search_correct = f"로비폰 보강판({bend_opt})"
            search_typo = f"로비폰 보강판({bend_opt.replace('사방', '사장')})"
            
            base_price = get_price_by_name(search_correct)
            if base_price == 0:
                base_price = get_price_by_name(search_typo)

            product_specs = f"[로비폰 보강판]"
            if bw_val and bh_val:
                product_specs += f" 가로 {int(bw_val)} x 세로 {int(bh_val)} /"
            else:
                product_specs += f" 사이즈 협의 /"
                
            product_specs += f" {bend_opt}"
            
        if model_val: 
            product_specs += f" / 모델명: {model_val}"

        # 이미지 파일명 매칭
        if bend_opt == "사방 절곡 없음":
            combo_names.append("사방절곡없음-로비폰 보강판")
        else:
            combo_names.append(" 사방절곡있음 로비폰 보강판")

    if is_main_ready:
        st.markdown("<h2>2. 추가 옵션 선택</h2>", unsafe_allow_html=True)
        opt_col, img_col = st.columns([5.5, 4.5])
        with opt_col:
            # 기타 공통 옵션 (마감캡, 도장 등)
            utils.render_generic_groups(cat_no_space, options_df, rk, priced_options, zero_options, preview_images)
        
        combo_names = list(dict.fromkeys(combo_names))
        valid_paths = utils.display_images(combo_names, priced_options, zero_options, preview_images, img_col, cat_no_space)
        return is_main_ready, base_price, product_specs, valid_paths, priced_options, zero_options

    return False, 0, "", [], [], []