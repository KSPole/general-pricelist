import streamlit as st
import pandas as pd
import utils
import re

def render(filtered_products, options_df, rk, cat_no_space):
    def get_opt_price(group_name, option_name):
        g_clean = re.sub(r'\s+', '', str(group_name))
        o_clean = re.sub(r'\s+', '', str(option_name))
        
        # 💡 수정사항 1: 적용 카테고리 필터링을 유연하게 처리하여 "벽부형 브라켓, 스텐(서스)밴드형 브라켓"을 모두 포함하도록 합니다.
        df = options_df[
            options_df['적용 카테고리'].astype(str).str.replace(" ", "").str.contains("벽부형|밴드형|" + cat_no_space, na=False)
        ]
        
        for idx, row in df.iterrows():
            row_g = re.sub(r'\s+', '', str(row.get('옵션 구분(그룹명)', '')))
            row_o = re.sub(r'\s+', '', str(row.get('추가 선택-1', '')))
            
            # 💡 수정사항 2: 엑셀 옵션명(뷸렛카메라박스)과 코드상의 옵션명(뷸렛카메라박스(변경))이 다를 경우도 상호 호환되도록 매칭 강화
            if row_g == g_clean:
                if row_o == o_clean or o_clean.startswith(row_o) or row_o.startswith(o_clean):
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
                # 💡 오직 "뷸렛카메라박스"일 때만 단가를 조회하여 화면에 표시합니다.
                if p == "뷸렛카메라박스":
                    price = get_opt_price("카메라 부착 부품", "뷸렛카메라박스(변경)")
                    if price > 0:
                        display_parts.append(f"{p} (+{price:,}원)")
                    else:
                        display_parts.append(p)
                else:
                    display_parts.append(p)
                        
            st.markdown(f"<div style='font-size:14px; margin-top:5px; margin-bottom:2px; color:#555;'>└ {position_label} 부품 선택</div>", unsafe_allow_html=True)
            sel_display = st.radio(f"{position_label} 부품", display_parts, index=0, horizontal=True, key=f"cpart_{rk_suffix}", label_visibility="collapsed")
            
            if sel_display == "선택 안 함": return None
            return sel_display.split(" (+")[0]
        return None

    is_main_ready, base_price, product_specs = False, 0, ""
    preview_images, priced_options, zero_options = [], [], []
    
    # --- 1. 기본 제품 선택 ---
    st.markdown("<div class='option-group-title'>📁 제품 선택</div>", unsafe_allow_html=True)
    prod_names = sorted(filtered_products['제품명'].dropna().unique())
    sel_prod = st.selectbox("제품 모델 선택", options=prod_names, index=None, placeholder="선택 유형을 고르세요", key=f"prod_{rk}")
    
    if sel_prod:
        row = filtered_products[filtered_products['제품명'] == sel_prod].iloc[0]
        base_price = int(row['단가'])
        product_specs = f"제품명: {sel_prod}"
        is_main_ready = True
        if pd.notna(row.get('이미지파일명')): 
            preview_images.append(str(row['이미지파일명']).strip())

    if is_main_ready:
        st.markdown("<h2>2. 옵션 선택</h2>", unsafe_allow_html=True)
        opt_col, img_col = st.columns([5.5, 4.5])
        with opt_col:
            
            # --- 카메라 형태 선택 ---
            st.markdown("<div class='option-group-title'>📁 설치할 카메라의 형태</div>", unsafe_allow_html=True)
            cam_opts = ["설치 안 함", "뷸렛카메라", "하우징카메라", "스피드돔카메라"]
            cam_main = st.radio("설치할 카메라의 형태", cam_opts, index=0, horizontal=True, key=f"cam_main_{rk}", label_visibility="collapsed")
            
            main_part = None
            if cam_main != "설치 안 함": 
                main_part = render_custom_cctv_camera_parts(cam_main, "카메라 부착", f"main_{rk}")
                
            if main_part:
                # 옵션 단가 매칭 시도
                search_name = "뷸렛카메라박스(변경)" if main_part == "뷸렛카메라박스" else ("알루미늄 각도기(기본)" if main_part == "알루미늄 각도기" else main_part)
                part_price = get_opt_price("카메라 부착 부품", search_name)
                
                if part_price > 0:
                    priced_options.append({
                        "cart_name": main_part, 
                        "display_name": f"{main_part} (1EA)", 
                        "unit_price": part_price, 
                        "qty_per_main": 1, 
                        "total_per_main": part_price, 
                        "group": "카메라 부착 부품"
                    })
                else:
                    zero_options.append({
                        "cart_name": main_part, 
                        "display_name": f"{main_part} (1EA)"
                    })

            # 기타 특별 주문 사항 등 공통 그룹 렌더링
            utils.render_generic_groups(cat_no_space, options_df, rk, priced_options, zero_options, preview_images)

        # 이미지 조합 및 출력 로직
        combo_names = [sel_prod, cat_no_space]
        if cam_main != "설치 안 함":
            combo_names.insert(0, f"{cat_no_space}-{cam_main.replace('카메라', '')}")
            if main_part:
                combo_names.insert(0, f"{cat_no_space}-{cam_main.replace('카메라', '')}-{main_part}")
                
        valid_paths = utils.display_images(combo_names, priced_options, zero_options, preview_images, img_col, cat_no_space)
        return is_main_ready, base_price, product_specs, valid_paths, priced_options, zero_options

    return False, 0, "", [], [], []