import streamlit as st
import pandas as pd
import utils

def render(filtered_products, options_df, rk, cat_no_space):
    is_main_ready, base_price, product_specs = False, 0, ""
    preview_images, priced_options, zero_options = [], [], []
    combo_names = []

    # 1. 레이스웨이 브라켓 전용
    if "레이스웨이브라켓" in cat_no_space or "레이스웨이" in cat_no_space:
        st.markdown("<div style='font-size:15px; font-weight:bold; color:#2e6c80; margin-bottom:5px;'>1️⃣ 레이스웨이 브라켓 형태 선택</div>", unsafe_allow_html=True)
        
        # 💡 1. 형태 선택
        r_type = st.radio("👉 형태 선택", ["측면 설치형", "하부 설치형"], horizontal=True, key=f"rw_type_{rk}")
        
        # 💡 2. 카메라박스 높이 선택
        r_height = st.radio("👉 카메라박스 높이 선택", ["높이 60mm", "높이 120mm"], horizontal=True, key=f"rw_hei_{rk}")
        
        # 💡 3. 레이스웨이 가로, 세로 입력 (선택사항으로 변경)
        st.markdown("<div style='margin-top:10px; font-weight:bold; color:#555;'>👉 레이스웨이 규격 입력 <span style='font-size:13px; color:#888;'>(선택사항)</span> (mm)</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        rw_w = c1.number_input("가로", min_value=0, step=10, value=None, placeholder="가로 입력", key=f"rw_w_{rk}")
        rw_h = c2.number_input("세로", min_value=0, step=10, value=None, placeholder="세로 입력", key=f"rw_h_{rk}")

        # 💡 [핵심] 가로, 세로 규격 입력과 상관없이 바로 단가/이미지 준비 완료 처리
        is_main_ready = True
        
        # [단가 매칭] 엑셀의 제품명과 동일하게 조립 (예: "레이스웨이 하부 설치용 브라켓 (높이 60mm)")
        target_prod_name = f"레이스웨이 {r_type.replace('설치형', '설치용')} 브라켓 ({r_height})"
        
        base_price = 0
        s_clean = target_prod_name.replace(" ", "")
        
        # 엑셀 데이터에서 정확한 이름 탐색
        for idx, row in filtered_products.iterrows():
            r_prod = str(row.get('제품명', '')).replace(" ", "")
            if s_clean == r_prod:
                val = row.get('단가', 0)
                if pd.notna(val): 
                    base_price = int(float(val))
                break
                
        # (보험용 코드) 완벽 일치가 없을 경우 포함 여부로 한 번 더 탐색
        if base_price == 0:
            for idx, row in filtered_products.iterrows():
                r_prod = str(row.get('제품명', '')).replace(" ", "")
                if s_clean in r_prod or r_prod in s_clean:
                    val = row.get('단가', 0)
                    if pd.notna(val): 
                        base_price = int(float(val))
                    break

        # 스펙 텍스트 정리 (사이즈 입력 여부에 따라 동적 표시)
        if rw_w and rw_h:
            product_specs = f"[{target_prod_name}] 레이스웨이 규격: 가로 {int(rw_w)}x세로 {int(rw_h)}"
        else:
            product_specs = f"[{target_prod_name}] 레이스웨이 규격: 사이즈 협의"
        
        # 💡 [이미지 매칭] 요청하신 규칙대로 파일명 조립
        type_img = "측면형" if "측면" in r_type else "하부형"
        hei_img = "60mm" if "60" in r_height else "120mm"
        
        combo_names = [f"레이스웨이브라켓-{type_img}-{hei_img}", "레이스웨이브라켓"]

    # 2. 기타 (나머지 기성품들)
    else:
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
            combo_names = [cat_no_space]

    # 공통 옵션 출력 및 이미지 매칭
    if is_main_ready:
        st.markdown("<h2>2. 옵션 선택</h2>", unsafe_allow_html=True)
        opt_col, img_col = st.columns([5.5, 4.5])
        with opt_col:
            utils.render_generic_groups(cat_no_space, options_df, rk, priced_options, zero_options, preview_images)
            
        if not combo_names: combo_names = [cat_no_space]
        valid_paths = utils.display_images(combo_names, priced_options, zero_options, preview_images, img_col, cat_no_space)
        return is_main_ready, base_price, product_specs, valid_paths, priced_options, zero_options

    return False, 0, "", [], [], []