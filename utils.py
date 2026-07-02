import os
import base64
import re
import pandas as pd
import io
from PIL import Image
import streamlit as st

def format_phone(p):
    p = re.sub(r'[^0-9]', '', p)
    if len(p) == 11: return f"{p[:3]}-{p[3:7]}-{p[7:]}"
    elif len(p) == 10:
        if p.startswith('02'): return f"{p[:2]}-{p[2:6]}-{p[6:]}"
        else: return f"{p[:3]}-{p[3:6]}-{p[6:]}"
    return p

def get_image_base64(img_path):
    if os.path.exists(img_path):
        with open(img_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

def format_price(price, item_name=""):
    if int(price) == 0 and ("주문" in str(item_name) or "별도" in str(item_name)):
        return "주문제작 단가"
    return f"{int(price):,}원"

def get_def_idx(options_list, force_no_select=False):
    if not force_no_select:
        for i, opt in enumerate(options_list):
            if "기본" in str(opt): return i
    for i, opt in enumerate(options_list):
        if "선택 안 함" in str(opt): return i
    return 0

@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        p_df = pd.read_csv(os.path.join(base_dir, 'product_master.csv'), encoding='cp949')
        o_df = pd.read_csv(os.path.join(base_dir, 'options.csv'), encoding='cp949')
    except:
        p_df = pd.read_csv(os.path.join(base_dir, 'product_master.csv'), encoding='utf-8-sig')
        o_df = pd.read_csv(os.path.join(base_dir, 'options.csv'), encoding='utf-8-sig')
    for df in [p_df, o_df]:
        if '단가' in df.columns:
            df['단가'] = pd.to_numeric(df['단가'].astype(str).str.replace(',', '').replace('원', '').str.strip(), errors='coerce').fillna(0).astype(int)
    return p_df, o_df

def build_spec_string(row):
    try:
        parts = []
        if '제품명' in row and pd.notna(row['제품명']) and str(row['제품명']).strip() != "":
            parts.append(str(row['제품명']))
        cat_str = str(row.get('카테고리', '')).replace(" ", "")
        if "함체" in cat_str or "앙카" in cat_str:
            box_parts = []
            if '가로' in row and pd.notna(row['가로']) and str(row['가로']).strip() != "": box_parts.append(f"{int(row['가로'])}(가로)")
            if '세로' in row and pd.notna(row['세로']) and str(row['세로']).strip() != "": box_parts.append(f"{int(row['세로'])}(세로)")
            if '깊이' in row and pd.notna(row['깊이']) and str(row['깊이']).strip() != "": box_parts.append(f"{int(row['깊이'])}(깊이/높이)")
            if box_parts: parts.append(" * ".join(box_parts))
        else:
            for col in ['높이/길이(M)', '가로', '세로', '깊이', '겉봉(상봉)', '속봉(하봉)', '직경(인치)', '두께(T)']:
                if col in row and pd.notna(row[col]) and str(row[col]).strip() != "":
                    v = row[col]
                    if col == '높이/길이(M)': parts.append(f"{int(v)}M" if type(v) in [int, float] and v==int(v) else f"{v}M")
                    elif col == '가로': parts.append(f"W{int(v)}" if type(v) in [int, float] else f"W{v}")
                    elif col == '세로': parts.append(f"H{int(v)}" if type(v) in [int, float] else f"H{v}")
                    elif col == '깊이': parts.append(f"D{int(v)}" if type(v) in [int, float] else f"D{v}")
                    elif col == '겉봉(상봉)': parts.append(f"겉{int(v)}" if type(v) in [int, float] and v==int(v) else f"겉{v}")
                    elif col == '속봉(하봉)': 
                        if cat_str in ["하리형브라켓", "벽부형브라켓", "스탠드형브라켓", "밴드형브라켓", "스텐(서스)밴드형브라켓"]: parts.append(f"{int(v)}" if type(v) in [int, float] and v==int(v) else f"{v}")
                        else: parts.append(f"속{int(v)}" if type(v) in [int, float] and v==int(v) else f"속{v}")
        
        # 조절가능길이 처리 (천장형 등)
        adj_str = ""
        for col in row.index:
            if '조절' in col and pd.notna(row[col]):
                adj_str = f" (조절가능길이: {row[col]})"
                break
        if not adj_str and pd.notna(row.get('제품명')):
            if '조절' in str(row['제품명']):
                adj_str = f" [{row['제품명']}]"

        if not parts:
            for col in row.index:
                if col not in ['카테고리', '단가', '이미지파일명', '합산 최소', '합산 최대'] and pd.notna(row[col]):
                    parts.append(str(row[col]))
        
        return (" / ".join(parts[:5]) + adj_str) if parts else "기본 규격"
    except Exception: return "기본 규격"

def process_image_to_white_bg(img_path):
    try:
        img = Image.open(img_path).convert("RGBA")
        background = Image.new("RGBA", img.size, (255, 255, 255, 255))
        alpha_composite = Image.alpha_composite(background, img)
        rgb_img = alpha_composite.convert("RGB")
        img_byte_arr = io.BytesIO()
        rgb_img.save(img_byte_arr, format='JPEG')
        return img_byte_arr.getvalue()
    except Exception:
        with open(img_path, "rb") as f: return f.read()

def find_auto_image(*names):
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
    if not os.path.exists(base_dir): return None
    try: all_files = os.listdir(base_dir)
    except: return None
    file_map = {}
    for f in all_files:
        name_no_ext = os.path.splitext(f)[0]
        clean_f = re.sub(r'[\s\-_&]', '', name_no_ext).lower()
        file_map[clean_f] = os.path.join(base_dir, f)
    for raw_name in names:
        if not raw_name: continue
        target1 = re.sub(r'[\s\-_&]', '', str(raw_name)).lower()
        if target1 in file_map: return file_map[target1]
        target2 = re.sub(r'[\s\-_&]', '', re.sub(r'\(.*?\)', '', str(raw_name))).lower()
        if target2 in file_map: return file_map[target2]
    return None

# --- 옵션 렌더링 공통 모듈 ---

def render_camera_parts(c_type, prefix_label, qty_multi, options_df, cat_no_space, rk, priced_options, zero_options, preview_images, selected_cam_parts):
    if not c_type or c_type == "선택 안 함": return
    c_type_clean = c_type.replace(" ", "")
    target_list = []
    
    if "스피드돔" in c_type_clean: target_list = ["스피드돔 브라켓 부착용 판재", "40A소켓(회전형으로 부착시)"]
    elif "뷸렛" in c_type_clean or "돔" in c_type_clean: target_list = ["뷸렛카메라박스(120*120*120)"]
    elif "하우징" in c_type_clean: target_list = ["기본각도기(알루미늄 재질)", "스텐각도기", "번호인식각도기"]
        
    o_map = {}
    for _, r in options_df.iterrows():
        r_cat = str(r.get('적용 카테고리', '')).replace(" ", "")
        if r_cat != cat_no_space and r_cat not in ["공통", "CCTV폴", "카메라", "하우징카메라", "각도기", ""]: continue
        name = str(r.get('추가 선택-1', '')).strip().replace(" ", "")
        is_exact = (r_cat == cat_no_space)
        
        if "뷸렛카메라박스" in name:
            if is_exact: o_map["뷸렛카메라박스(120*120*120)"] = r
            elif "뷸렛카메라박스(120*120*120)" not in o_map: o_map["뷸렛카메라박스(120*120*120)"] = r
        elif "기본각도기" in name:
            if is_exact: o_map["기본각도기(알루미늄 재질)"] = r
            elif "기본각도기(알루미늄 재질)" not in o_map: o_map["기본각도기(알루미늄 재질)"] = r
        elif "스텐각도기" in name:
            if is_exact: o_map["스텐각도기"] = r
            elif "스텐각도기" not in o_map: o_map["스텐각도기"] = r
        elif "번호인식" in name:
            if is_exact: o_map["번호인식각도기"] = r
            elif "번호인식각도기" not in o_map: o_map["번호인식각도기"] = r
        elif "판재" in name:
            if is_exact: o_map["스피드돔 브라켓 부착용 판재"] = r
            elif "스피드돔 브라켓 부착용 판재" not in o_map: o_map["스피드돔 브라켓 부착용 판재"] = r
        elif "40A" in name:
            if is_exact: o_map["40A소켓(회전형으로 부착시)"] = r
            elif "40A소켓(회전형으로 부착시)" not in o_map: o_map["40A소켓(회전형으로 부착시)"] = r

    if "하우징" in c_type_clean and "기본각도기(알루미늄 재질)" not in o_map: o_map["기본각도기(알루미늄 재질)"] = pd.Series({'단가': 0, '추가 선택-1': '기본각도기(알루미늄 재질)'})
    if "하우징" in c_type_clean and "스텐각도기" not in o_map: o_map["스텐각도기"] = pd.Series({'단가': 15000, '추가 선택-1': '스텐각도기'})
    if "하우징" in c_type_clean and "번호인식각도기" not in o_map: o_map["번호인식각도기"] = pd.Series({'단가': 25000, '추가 선택-1': '번호인식각도기'})
    
    final_list = [t for t in target_list if t in o_map]
    if final_list:
        final_list = ["선택 안 함"] + final_list
        key_name = f"rd_cam_parts_{prefix_label}_{c_type}_{st.session_state.rk_lvl2}"
        sel_o = st.radio(f"{prefix_label} 부품 선택", final_list, index=get_def_idx(final_list), label_visibility="collapsed", key=key_name)
        if sel_o != "선택 안 함":
            row = o_map[sel_o]
            o_price = int(row.get('단가', 0))
            if pd.notna(row.get('이미지파일명')): preview_images.append(str(row['이미지파일명']).strip())
            selected_cam_parts.append(sel_o) 
            c_name = f"[{prefix_label}] {sel_o}" if ("상부" in prefix_label or "암" in prefix_label) else sel_o
            d_name = f"{prefix_label} 부품: {sel_o}" if ("상부" in prefix_label or "암" in prefix_label) else f"카메라 부품: {sel_o}"
            
            if o_price == 0: zero_options.append({"cart_name": c_name, "display_name": d_name})
            else: priced_options.append({"cart_name": c_name, "display_name": d_name, "unit_price": o_price, "qty_per_main": qty_multi, "total_per_main": o_price * qty_multi, "group": "카메라부착부품"})

def render_shake_prevention(cat_no_space, options_df, rk, sel_inch, priced_options, zero_options, preview_images):
    shake_kws = []
    _raw_shake = options_df[options_df['옵션 구분(그룹명)'].astype(str).str.replace(" ", "").str.contains("흔들림|흔들임", na=False)].copy()
    if cat_no_space == "밴드형브라켓" and sel_inch:
        inch_num = sel_inch.replace("인치", "").strip()
        _shake_opts = _raw_shake[(_raw_shake['적용 카테고리'].astype(str).str.replace(" ", "") == "밴드형브라켓") & (_raw_shake['추가 선택-1'].astype(str).str.contains(inch_num, na=False))]
    else:
        _shake_opts = _raw_shake[_raw_shake['적용 카테고리'].astype(str).str.replace(" ", "") == cat_no_space]
        if _shake_opts.empty: _shake_opts = _raw_shake[_raw_shake['적용 카테고리'].astype(str).str.replace(" ", "").isin(["공통"])]
        
    if not _shake_opts.empty:
        st.markdown("<div class='option-group-title'>📁 흔들림 방지</div>", unsafe_allow_html=True)
        shake_choices = []
        shake_map = {}
        for row_idx, r in _shake_opts.iterrows():
            name1, name2 = str(r.get('추가 선택-1', '')).strip(), str(r.get('추가 선택-2', '')).strip()
            name = name2 if (name2 and name2.lower() != 'nan') else (name1 if name1 and name1.lower() != 'nan' else "")
            if name: shake_choices.append(name); shake_map[name] = r
        s_opts = ["선택 안 함"] + shake_choices
        sel_shake = st.radio("흔들림 방지 선택", s_opts, index=get_def_idx(s_opts), label_visibility="collapsed", key=f"rd_shake_{st.session_state.rk_lvl2}")
        if sel_shake != "선택 안 함":
            r = shake_map[sel_shake]
            if pd.notna(r.get('이미지파일명')): preview_images.append(str(r['이미지파일명']).strip())
            priced_options.append({"cart_name": sel_shake, "display_name": f"흔들림 방지: {sel_shake}", "unit_price": int(r.get('단가', 0)), "qty_per_main": 1, "total_per_main": int(r.get('단가', 0)), "group": "흔들림 방지"})
            
            name = sel_shake
            if "와이어" in name and "삼각" in name: shake_kws.extend(["와이어", "삼각파이프"])
            elif "와이어" in name: shake_kws.append("와이어")
            elif "삼각" in name: shake_kws.append("삼각파이프")
            else: shake_kws.append(re.sub(r'\(.*?\)', '', name).strip())
            
    return shake_kws

# 👉 [수정됨] 기존 엑셀 추가선택 로직을 삭제하고 '특별 주문 사항' 텍스트에어리어로 대체
def render_generic_groups(cat_no_space, options_df, rk, priced_options, zero_options, preview_images):
    st.markdown("<div class='option-group-title'>📁 특별 주문 사항</div>", unsafe_allow_html=True)
    
    special_order = st.text_area(
        "특별 주문 사항 입력", 
        placeholder="👉 도장을 원하시는 경우 색상을 적어주시거나, 기타 특별한 제작 및 주문 요청 사항을 자유롭게 입력해 주세요.", 
        key=f"special_{st.session_state.rk_lvl2}",
        label_visibility="collapsed"
    )
    
    if special_order and special_order.strip() != "":
        zero_options.append({
            "cart_name": "특별주문사항", 
            "display_name": f"📌 특별 주문: {special_order.strip()}"
        })

def display_images(combo_names, priced_options, zero_options, preview_images, img_col, cat_no_space):
    with img_col:
        st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)
        valid_paths = []
        
        if cat_no_space in ["앙카", "앙카베이스"] and st.session_state.get('custom_anchor_val'): combo_names.insert(0, "주문제작앙카베이스")
        if cat_no_space == "베이스커버" and st.session_state.get('custom_anchor_val'): combo_names.insert(0, "주문제작베이스커버")
        
        for opt in priced_options + zero_options:
            cname = opt['cart_name']
            group = opt.get('group', '')
            if "베이스커버" in group or "베이스커버" in cname: cname = "베이스커버"
            elif "앙카베이스" in group: cname = "앙카베이스"
            elif "앙카" in group and "간격" in group: continue
            opt_img = find_auto_image(cname, opt['cart_name'])
            if opt_img and opt_img not in valid_paths: valid_paths.append(opt_img)

        main_img = find_auto_image(*combo_names)
        if main_img and main_img not in valid_paths: valid_paths.insert(0, main_img)
        for img in preview_images:
            p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images", img)
            if os.path.exists(p) and p not in valid_paths: valid_paths.append(p)

        if valid_paths:
            h = "455px" if any(x in cat_no_space for x in ["브라켓", "벽부"]) else "300px"
            cols = st.columns(2)
            for idx, path in enumerate(valid_paths):
                with cols[idx % 2]:
                    b64 = get_image_base64(path)
                    if b64: st.markdown(f'<div style="display:flex; justify-content:center; background:white; padding:5px; border-radius:8px; border:1px solid #eee; margin-bottom:10px;"><div style="height:{h}; display:flex; align-items:center;"><img src="data:image/jpeg;base64,{b64}" style="max-width:100%; max-height:100%; object-fit:contain;"></div></div>', unsafe_allow_html=True)
        else:
            st.info(f"💡 현재 폴더에 맞는 사진이 없습니다.\n\n사진 파일 이름을 아래 중 하나로 변경해 주세요:\n- {', '.join(combo_names[:3])}")
        return valid_paths