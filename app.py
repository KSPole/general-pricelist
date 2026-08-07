# =============================================================================
# 📌 한국시스템폴 디지털 단가표 - 메인 대시보드 (완벽 최적화 버전)
# =============================================================================

import os
import re
import datetime
import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import utils
import prod_cctv
import prod_wall
import prod_band
import prod_sus_band
import prod_roof
import prod_ceiling
import prod_hari
import prod_lobby
import prod_bullet_angle
import prod_anchor_base
import prod_base_cover
import prod_cctv_panel
import prod_enclosure
import prod_others
import prod_i_bracket

APP_VERSION = "v1.2.12"

# 파비콘 및 기본 설정
st.set_page_config(page_title="한국시스템폴 디지털 단가표", layout="wide", page_icon="🔵")

components.html("""
<script>
document.addEventListener("DOMContentLoaded", function() {
    const parentDoc = window.parent.document;
    
    const svgIcon = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect width="100" height="100" fill="%23004b9b" rx="20"/><text x="50%25" y="55%25" dominant-baseline="middle" text-anchor="middle" font-size="38" font-family="Arial" font-weight="bold" fill="white">KSP</text></svg>';
    
    let link = parentDoc.querySelector("link[rel~='icon']");
    if (!link) {
        link = parentDoc.createElement('link');
        link.rel = 'icon';
        parentDoc.head.appendChild(link);
    }
    link.href = svgIcon;

    let appleLink = parentDoc.querySelector("link[rel='apple-touch-icon']");
    if (!appleLink) {
        appleLink = parentDoc.createElement('link');
        appleLink.rel = 'apple-touch-icon';
        parentDoc.head.appendChild(appleLink);
    }
    appleLink.href = svgIcon;
    
    // 파일 업로더 영어 텍스트 강제 한글화
    function translateUploader() {
        const elements = parentDoc.querySelectorAll('span, div, small');
        elements.forEach(el => {
            if (el.childNodes.length === 1 && el.childNodes[0].nodeType === 3) {
                const text = el.textContent.trim();
                if (text === "Drag and drop file here" || text === "Drag and drop files here") el.textContent = "📁 여기에 파일을 드래그 앤 드롭 하세요";
                else if (text === "Browse files") el.textContent = "첨부하기";
                else if (text.includes("Limit 200MB per file")) el.textContent = "파일당 최대 200MB";
            }
        });
    }

    // ⭐ 선택 메뉴(Selectbox) 터치 시 모바일 키보드 팝업 완벽 차단
    function disableKeyboardOnSelect() {
        const selectInputs = parentDoc.querySelectorAll('div[data-testid="stSelectbox"] input');
        selectInputs.forEach(input => {
            input.setAttribute("inputmode", "none"); 
            input.setAttribute("readonly", "readonly"); 
        });
    }

    const observer = new MutationObserver(() => { 
        translateUploader(); 
        disableKeyboardOnSelect(); 
    });
    observer.observe(parentDoc.body, { childList: true, subtree: true });
});
</script>
""", height=0, width=0)

st.markdown("""
<style>
    /* 스마트폰 제스처(새로고침, 뒤로가기) 강제 차단 */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        overscroll-behavior: none !important;
        overscroll-behavior-y: none !important;
        overscroll-behavior-x: none !important;
        touch-action: pan-y !important; 
    }
    
    .block-container { padding-top: 1rem !important; padding-bottom: 1.5rem !important; }
    
    /* 스트림릿 기본 UI 마크, 워터마크 완벽 숨김 */
    div[data-testid="InputInstructions"] { display: none !important; }
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important; display: none !important;}
    header {visibility: hidden !important; display: none !important;}
    .viewerBadge_container {display: none !important;} 
    .stDeployButton {display: none !important;}
    
    /* 타이틀 및 UI 디자인 */
    h1 { text-align: center !important; line-height: 1.2 !important; font-size: 28px !important; color: #333; margin-top: -10px !important; margin-bottom: 15px !important; font-weight: 900; }
    h2 { font-size: 22px !important; border-bottom: 2px solid #2e6c80; padding-bottom: 6px; margin-top: 10px !important; margin-bottom: 10px !important; color: #2e6c80; }
    
    div[data-testid="stSelectbox"] label p, div[data-testid="stNumberInput"] label p, div[data-testid="stTextInput"] label p, div[data-testid="stRadio"] label p { 
        font-size: 15px !important; font-weight: bold !important; color: #333; margin-bottom: 2px !important; 
    }
    .cart-card { background-color: #fff; border: 1px solid #e0e0e0; border-radius: 12px; padding: 16px; margin-bottom: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.04); position: relative; }
    .summary-box { background-color: #fff; border: 2px solid #2e6c80; border-radius: 12px; padding: 20px; margin-top: 15px; margin-bottom: 15px; text-align: center; box-shadow: 0 4px 10px rgba(46,108,128,0.15); }
    .summary-price { font-size: 32px; font-weight: 900; color: #e53935; letter-spacing: -1px; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 1. 상태 로드 및 변수 초기화
# -----------------------------------------------------------------------------
products_df, options_df = utils.load_data()
categories = list(products_df['카테고리'].dropna().unique())

if "뷸렛카메라박스" in categories: categories[categories.index("뷸렛카메라박스")] = "뷸렛카메라박스 / 각도기"

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'cart' not in st.session_state: st.session_state.cart = []
if 'selected_cat' not in st.session_state: st.session_state.selected_cat = None
if 'rk_main' not in st.session_state: st.session_state.rk_main = 0       
if 'rk_lvl1' not in st.session_state: st.session_state.rk_lvl1 = 0       
if 'rk_lvl2' not in st.session_state: st.session_state.rk_lvl2 = 0       

# 수령인 및 동적 알림 변수 초기화
for field in ['c_name', 'p_phone', 'c_email', 'd_addr', 'd_branch', 'r_name', 'r_phone']:
    if field not in st.session_state: st.session_state[field] = ""

if 'show_skip_checkbox' not in st.session_state:
    st.session_state.show_skip_checkbox = False

rk = st.session_state.rk_main

# -----------------------------------------------------------------------------
# 2. 로그인 폼 (일반 고객 및 톱니바퀴)
# -----------------------------------------------------------------------------
if not st.session_state.logged_in:
    # 우측 상단에 버전 정보 배치
    st.markdown(f"<div style='text-align: right; font-size: 13px; color: #888; font-weight: bold; margin-bottom: 5px;'>{APP_VERSION}</div>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([2.5, 5, 2.5])
    with c2:
        st.markdown("<h1 style='color: #2e6c80;'>한국시스템폴<br>제품 단가표</h1>", unsafe_allow_html=True)

    if st.session_state.get('show_admin', False):
        st.markdown("<div style='max-width: 600px; margin: 0 auto; background-color:#f1f5f9; padding:15px; border-radius:10px; margin-bottom:20px; text-align:center;'>", unsafe_allow_html=True)
        admin_pw = st.text_input("본사 직원 비밀번호", placeholder="비밀번호를 입력하세요")
        if st.button("관리자 접속", type="primary", width="stretch"):
            if admin_pw.lower() == "locker1092***":
                st.session_state.update({"c_name":"한국시스템폴", "p_phone":"010-3304-2221", "logged_in":True, "is_admin": True})
                st.rerun()
            else:
                st.error("❌ 비밀번호 불일치")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='max-width: 600px; margin: 0 auto; text-align: center;'>", unsafe_allow_html=True)
    with st.form("login_form"):
        c_name = st.text_input("업체명 (상호) *", placeholder="예: 한국시스템폴")
        p_phone_str = st.text_input("연락처 *", placeholder="연락처 숫자만 입력")
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("단가표 접속하기", type="primary", width="stretch")
        
        if submitted:
            p_phone = re.sub(r'[^0-9]', '', p_phone_str) 
            if not c_name.strip() or not p_phone: st.warning("⚠️ 업체명과 연락처를 모두 입력해 주세요.")
            elif len(p_phone) < 9: st.warning("⚠️ 연락처를 정확하게 입력해 주세요.")
            else:
                st.session_state.update({"c_name":c_name, "p_phone":p_phone, "logged_in":True, "is_admin": False})
                st.rerun()
                
    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    if st.button("⚙️ 관리자 설정", width="stretch"):
        st.session_state.show_admin = not st.session_state.get('show_admin', False)
        st.rerun()
        
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# -----------------------------------------------------------------------------
# 3. 메인 대시보드 (단가표 화면)
# -----------------------------------------------------------------------------
logout_col1, logout_col2 = st.columns([7, 3])
with logout_col1:
    st.markdown(f"<div style='font-size:14px; font-weight:bold; color:#004b9b; padding-top:10px;'>🟢 접속중: {st.session_state.c_name}</div>", unsafe_allow_html=True)
with logout_col2:
    st.markdown(f"<div style='text-align: right; font-size: 12px; color: #888; font-weight: bold;'>{APP_VERSION}</div>", unsafe_allow_html=True)
    if st.button("로그아웃", width="stretch"):
        st.session_state.logged_in = False
        st.session_state.is_admin = False
        st.session_state.cart = []
        st.rerun()

st.markdown("<hr style='margin-top:5px; margin-bottom:20px;'>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)

if st.session_state.is_admin:
    st.markdown("<h1 style='color: #2e6c80;'>한국시스템폴<br>제품 단가표 <span style='font-size:18px; color:#d9534f; vertical-align:middle;'>(관리자)</span></h1>", unsafe_allow_html=True)
    with st.expander("👑 고객 접속 및 장바구니 로그 확인"):
        if os.path.exists("access_log.csv"):
            try:
                # dtype=str 로 읽어와서 0이 잘리는 것을 1차로 방지
                df_log = pd.read_csv("access_log.csv", on_bad_lines='skip', dtype=str).fillna("")
                
                if "연락처" in df_log.columns:
                    def fix_phone(x):
                        s = str(x).replace('.0', '').strip()
                        # 이미 0이 날아갔을 경우 복구
                        if len(s) == 10 and not s.startswith('0'):
                            s = '0' + s
                        if len(s) > 8 and "-" not in s:
                            return utils.format_phone(s)
                        return s
                    df_log["연락처"] = df_log["연락처"].apply(fix_phone)
                
                if "시간" in df_log.columns:
                    df_log = df_log.sort_values(by="시간", ascending=False)
                elif "접속일시" in df_log.columns:
                    df_log = df_log.sort_values(by="접속일시", ascending=False)
                
                st.dataframe(df_log, use_container_width=True)
                csv = df_log.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
                st.download_button(label="📥 접속 명단 엑셀 다운로드", data=csv, file_name='고객주문이력.csv', mime='text/csv', width="stretch")
            except Exception as e: 
                st.error(f"기록 정렬 중 문제가 발생했습니다: {e}")
        else: 
            st.info("아직 기록이 없습니다.")
else:
    st.markdown("<h1 style='color: #2e6c80;'>한국시스템폴<br>제품 단가표</h1>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

is_main_ready, base_price, product_specs, valid_paths, priced_options, zero_options = False, 0, "", [], [], []

if st.session_state.selected_cat is None:
    num_cols = 3 
    for i in range(0, len(categories), num_cols):
        cols = st.columns(num_cols)
        for j in range(num_cols):
            if i + j < len(categories):
                cat = categories[i + j]
                if cols[j].button(cat, width="stretch", type="secondary", key=f"cat_{cat}_{rk}"):
                    st.session_state.selected_cat = cat
                    st.session_state.rk_main += 1
                    st.rerun()
else:
    if st.button(f"⬅️ {st.session_state.selected_cat} (뒤로가기)", type="primary", width="stretch"):
        st.session_state.selected_cat = None
        st.rerun()

    excel_cat_name = "뷸렛카메라박스" if st.session_state.selected_cat == "뷸렛카메라박스 / 각도기" else st.session_state.selected_cat
    cat_no_space = excel_cat_name.replace(" ", "")
    filtered = products_df[products_df['카테고리'] == excel_cat_name]

    if cat_no_space == "CCTV폴": res = prod_cctv.render(filtered, options_df, rk, cat_no_space)
    elif cat_no_space == "벽부형브라켓": res = prod_wall.render(filtered, options_df, rk, cat_no_space)
    elif cat_no_space == "밴드형브라켓": res = prod_band.render(filtered, options_df, rk, cat_no_space)
    elif cat_no_space == "스텐(서스)밴드형브라켓": res = prod_sus_band.render(filtered, options_df, rk, cat_no_space)
    elif cat_no_space == "옥상브라켓": res = prod_roof.render(filtered, options_df, rk, cat_no_space)
    elif cat_no_space == "천장형브라켓": res = prod_ceiling.render(filtered, options_df, rk, cat_no_space)
    elif cat_no_space == "하리형브라켓": res = prod_hari.render(filtered, options_df, rk, cat_no_space)
    elif "로비폰" in cat_no_space or "보강판" in cat_no_space: res = prod_lobby.render(filtered, options_df, rk, cat_no_space)
    elif "뷸렛카메라박스" in cat_no_space or "각도기" in cat_no_space: res = prod_bullet_angle.render(filtered, options_df, rk, cat_no_space)
    elif "앙카베이스" in cat_no_space: res = prod_anchor_base.render(filtered, options_df, rk, cat_no_space)
    elif "i형(수직)브라켓" in cat_no_space or "i형" in cat_no_space:
       res = prod_i_bracket.render(filtered, options_df, rk, cat_no_space)
    elif "베이스커버" in cat_no_space: res = prod_base_cover.render(filtered, options_df, rk, cat_no_space)
    elif "CCTV작동중판넬" in cat_no_space: res = prod_cctv_panel.render(filtered, options_df, rk, cat_no_space)
    elif "함체" in cat_no_space: res = prod_enclosure.render(filtered, options_df, rk, cat_no_space)
    else: res = prod_others.render(filtered, options_df, rk, cat_no_space)
        
    is_main_ready, base_price, product_specs, valid_paths, priced_options, zero_options = res

# -----------------------------------------------------------------------------
# 4. 장바구니 및 하단 로직 
# -----------------------------------------------------------------------------
if is_main_ready:
    st.markdown("<h2>3. 단가 확인 및 파일(사진) 첨부</h2>", unsafe_allow_html=True)
    mc1, mc2, mc3, mc4 = st.columns([4.5, 2, 2.5, 1])
    quantity = mc4.number_input("수량", min_value=1, step=1, value=1, key=f"q_main_{rk}", label_visibility="collapsed")
    
    ui_img_html = ""
    if valid_paths:
        img_tags = [f"<img src='data:image/jpeg;base64,{utils.get_image_base64(p)}' height='50' style='border-radius:4px; border:1px solid #ddd; margin-right:5px; margin-top:5px;'>" for p in valid_paths if utils.get_image_base64(p)]
        ui_img_html = f"<div>{''.join(img_tags)}</div>"
        
    mc1.markdown(f"<b>[{st.session_state.selected_cat}]</b> {product_specs}{ui_img_html}", unsafe_allow_html=True)
    mc2.markdown(f"<div style='padding-top:2px; color:#555;'>단가: <b>{utils.format_price(base_price, product_specs)}</b></div>", unsafe_allow_html=True)
    mc3.markdown(f"<div style='padding-top:2px; color:#d9534f; font-weight:bold;'>금액: {utils.format_price(base_price * quantity, product_specs)}</div>", unsafe_allow_html=True)
    
    for o in zero_options: st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;💡 {o['display_name']}")
    for idx, o in enumerate(priced_options):
        c1, c2, c3, c4 = st.columns([4.5, 2, 2.5, 1])
        
        qty_val = int(o.get('qty_per_main', 1) * quantity)
        unique_key = f"q_opt_{idx}_{rk}_{o.get('cart_name', '')}_{o.get('qty_per_main', 1)}_{quantity}"
        
        opt_q = c4.number_input("수량", min_value=0, value=qty_val, key=unique_key, label_visibility="collapsed")
        o['current_cart_q'], o['total_per_main'] = opt_q, o['unit_price'] * opt_q
        
        c1.markdown(f"<div style='padding-top:8px;'>└ {o['display_name']}</div>", unsafe_allow_html=True)
        c2.markdown(f"<div style='padding-top:8px; color:#555;'>단가: <b>{utils.format_price(o['unit_price'], o['display_name'])}</b></div>", unsafe_allow_html=True)
        c3.markdown(f"<div style='padding-top:8px; color:#d9534f; font-weight:bold;'>금액: {utils.format_price(o['total_per_main'], o['display_name'])}</div>", unsafe_allow_html=True)
    
    total = base_price * quantity + sum([o['total_per_main'] for o in priced_options])
    uploaded_files = st.file_uploader("도면, 스케치, 현장 사진 등 첨부", accept_multiple_files=True, key=f"file_upl_{rk}")
    st.markdown(f"<div class='summary-box'><div class='summary-price'>{utils.format_price(total, product_specs)}</div></div>", unsafe_allow_html=True)

    if st.button("🛒 장바구니에 담기", type="primary", width="stretch"):
        import time
        bid, files_data = str(time.time()), []
        if uploaded_files:
            for f in uploaded_files: files_data.append({"name": f.name, "type": f.type, "bytes": f.getvalue()})
        opts_txt = "<br>".join([o['display_name'] for o in zero_options])
        
        item_summary = f"[{st.session_state.selected_cat}] {product_specs} ({quantity}개)"
        opt_str = ", ".join([f"{o['display_name']}({o['current_cart_q']}개)" for o in priced_options if o['current_cart_q'] > 0])
        if opt_str: item_summary += f" / 옵션: {opt_str}"
            
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_data = pd.DataFrame([{
            "시간": now, 
            "구분": "장바구니 담기",
            "업체명": st.session_state.c_name, 
            "연락처": utils.format_phone(st.session_state.p_phone), 
            "내용/담은제품": item_summary,
            "배송지_및_방법": "",
            "수령인_정보": ""
        }])
        try:
            if not os.path.exists("access_log.csv"): 
                log_data.to_csv("access_log.csv", index=False, encoding='utf-8-sig')
            else: 
                old_df = pd.read_csv("access_log.csv", on_bad_lines='skip', dtype=str)
                new_df = pd.concat([old_df, log_data], ignore_index=True)
                new_df.to_csv("access_log.csv", index=False, encoding='utf-8-sig')
        except: pass
        
        st.session_state.cart.append({"bid": bid, "is_opt": False, "p": st.session_state.selected_cat, "s": product_specs, "o": opts_txt, "q": quantity, "u": base_price, "t": base_price * quantity, "files": files_data, "img_paths": valid_paths})
        for o in priced_options:
            st.session_state.cart.append({"bid": bid, "is_opt": True, "p": o.get('group', '옵션'), "o": o['cart_name'], "q": o['current_cart_q'], "u": o['unit_price'], "t": o['total_per_main'], "q_per": o['qty_per_main']})
        st.session_state.selected_cat = None
        st.rerun()

cart_trs, total_sum, all_ext_img_paths = "", 0, []
if st.session_state.cart:
    st.markdown("<h2>🛒 장바구니 요약</h2>", unsafe_allow_html=True)
    for item in st.session_state.cart:
        if not item.get('is_opt'):
            st.markdown("<div class='cart-card'>", unsafe_allow_html=True)
            c1, c2 = st.columns([9, 1])
            c1.markdown(f"<div class='cart-header'>{item['p']}</div>", unsafe_allow_html=True)
            if c2.button("삭제", key=f"del_{item['bid']}"):
                st.session_state.cart = [x for x in st.session_state.cart if x['bid'] != item['bid']]
                st.rerun()
            
            if item['o']: st.markdown(f"**기본사항:** {item['o']}", unsafe_allow_html=True)
            if item.get('files'): st.markdown(f"<div style='font-size:13px; color:#17a2b8; margin-top:5px;'>📎 첨부파일: {', '.join([f['name'] for f in item['files']])}</div>", unsafe_allow_html=True)
            st.markdown("<hr style='margin: 10px 0px;'>", unsafe_allow_html=True)
            
            mc1, mc2, mc3, mc4 = st.columns([4.5, 2, 2.5, 1])
            new_q = mc4.number_input("수량", min_value=0, value=item['q'], key=f"cq_{item['bid']}", label_visibility="collapsed")
            ui_img_html = ""
            if item.get('img_paths'):
                img_tags = [f"<img src='data:image/jpeg;base64,{utils.get_image_base64(p)}' height='50' style='border-radius:4px; border:1px solid #ddd; margin-right:5px; margin-top:5px;'>" for p in item['img_paths'] if utils.get_image_base64(p)]
                ui_img_html = f"<div>{''.join(img_tags)}</div>"
                for p in item['img_paths']:
                    if p not in all_ext_img_paths: all_ext_img_paths.append(p)
                
            mc1.markdown(f"<div style='padding-top:8px;'><b>[메인]</b> {item['s']}{ui_img_html}</div>", unsafe_allow_html=True)
            mc2.markdown(f"<div style='padding-top:8px; color:#555;'>단가: <b>{utils.format_price(item['u'], item['s'])}</b></div>", unsafe_allow_html=True)
            
            if new_q == 0: 
                st.session_state.cart = [x for x in st.session_state.cart if x['bid'] != item['bid']]
                st.rerun()
            elif new_q != item['q']:
                item['q'], item['t'] = new_q, item['u'] * new_q
                for sub in st.session_state.cart:
                    if sub.get('is_opt') and sub['bid'] == item['bid']:
                        sub['q'] = int(sub.get('q_per', 1) * new_q)
                        sub['t'] = sub['u'] * sub['q']
                st.rerun()
            
            mc3.markdown(f"<div style='padding-top:8px; color:#d9534f; font-weight:bold;'>금액: {utils.format_price(item['t'], item['s'])}</div>", unsafe_allow_html=True)    
            total_sum += item['t']
            cart_trs += f"<tr><td>메인 제품</td><td>[{item['p']}] {item['s']}</td><td>{item['q']}</td><td style='text-align:right;'>{utils.format_price(item['u'], item['s'])}</td><td style='text-align:right;'>{utils.format_price(item['t'], item['s'])}</td></tr>"
            
            for sub in [x for x in st.session_state.cart if x.get('is_opt') and x['bid'] == item['bid']]:
                sc1, sc2, sc3, sc4 = st.columns([4.5, 2, 2.5, 1])
                nsq = sc4.number_input("수량", min_value=0, value=sub['q'], key=f"cq_opt_{sub['bid']}_{sub['o']}", label_visibility="collapsed")
                sc1.markdown(f"<div style='padding-top:8px;'>└ {sub['o']}</div>", unsafe_allow_html=True)
                sc2.markdown(f"<div style='padding-top:8px; color:#555;'>단가: <b>{utils.format_price(sub['u'], sub['o'])}</b></div>", unsafe_allow_html=True)
                if nsq != sub['q']:
                    sub['q'], sub['t'] = nsq, sub['u'] * nsq
                    if item['q'] > 0: sub['q_per'] = nsq / item['q']
                    st.rerun()
                sc3.markdown(f"<div style='padding-top:8px; color:#d9534f; font-weight:bold;'>금액: {utils.format_price(sub['t'], sub['o'])}</div>", unsafe_allow_html=True)
                total_sum += sub['t']
                if sub['q'] > 0: cart_trs += f"<tr style='color:#666; font-size:13px;'><td>└ 추가/옵션</td><td>[{sub['p']}] {sub['o']}</td><td>{sub['q']}</td><td style='text-align:right;'>{utils.format_price(sub['u'], sub['o'])}</td><td style='text-align:right;'>{utils.format_price(sub['t'], sub['o'])}</td></tr>"
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"<div style='background-color:#333; color:white; border-radius:8px; padding:20px; text-align:center; margin-bottom:20px;'><div style='font-size:32px; font-weight:900;'>총 합계: {int(total_sum):,}원</div></div>", unsafe_allow_html=True)
    
    st.markdown("<h2>✉️ 주문 접수 및 견적서 메일 받기</h2>", unsafe_allow_html=True)
    
    # 💡 [핵심] 모바일 줄바꿈 방지를 위해 텍스트 길이 최소화
    st.markdown("<div style='display:flex; justify-content:space-between; align-items:flex-end; margin-top:10px;'><p style='font-size:15px; font-weight:bold; color:#333; margin-bottom:2px;'>배송지 주소</p><a href='https://www.juso.go.kr/openIndexPage.do' target='_blank' style='font-size:13px; color:#004b9b; text-decoration:none; background:#e8f4f8; padding:3px 8px; border-radius:4px; border:1px solid #c4e3ed;'>🔍 도로명 주소 검색</a></div>", unsafe_allow_html=True)
    st.session_state.d_addr = st.text_input("배송지 주소", value=st.session_state.get("d_addr", ""), placeholder="주문을 위해 배송받으실 주소를 정확히 입력해 주세요", label_visibility="collapsed")
    
    d_method = st.radio("배송 방법", ["택배", "경동화물", "용달", "방문"], horizontal=True)
    
    if d_method == "경동화물": 
        # 💡 [핵심] 모바일 줄바꿈 방지를 위해 텍스트 길이 최소화
        st.markdown("<div style='display:flex; justify-content:space-between; align-items:flex-end; margin-top:10px;'><p style='font-size:15px; font-weight:bold; color:#333; margin-bottom:2px;'>경동화물 지점명</p><a href='https://kdexp.com/network/office.do' target='_blank' style='font-size:13px; color:#004b9b; text-decoration:none; background:#e8f4f8; padding:3px 8px; border-radius:4px; border:1px solid #c4e3ed;'>🔍 가까운 영업소 찾기</a></div>", unsafe_allow_html=True)
        st.session_state.d_branch = st.text_input("경동화물 지점명", value=st.session_state.d_branch, placeholder="모르실 경우 현장 주소를 입력해 주시면 확인 후 발송합니다.", label_visibility="collapsed")
        
    d_pay = st.radio("배송비 결제", ["선불", "착불"], horizontal=True)
    
    # 수령인 정보 입력칸
    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
    r_c1, r_c2 = st.columns(2)
    with r_c1:
        st.session_state.r_name = st.text_input("받는 사람 이름 (필수)", value=st.session_state.get("r_name", ""), placeholder="수령인 이름 입력")
    with r_c2:
        st.session_state.r_phone = st.text_input("받는 사람 연락처 (필수)", value=st.session_state.get("r_phone", ""), placeholder="수령인 연락처 입력")
    
    # 사업자등록증 첨부 파일 업로더
    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
    biz_reg_file = st.file_uploader("🏢 사업자등록증 사본 첨부 (선택사항 / 스마트폰에서는 카메라 촬영 지원)", type=['png', 'jpg', 'jpeg', 'pdf'])
    
    st.markdown("<hr style='margin:20px 0;'>", unsafe_allow_html=True)
    
    st.markdown("<p style='font-size:16px; font-weight:bold; color:#2e6c80; margin-bottom:5px;'>📧 견적서 수신용 이메일 주소</p>", unsafe_allow_html=True)
    
    email_col1, email_col2 = st.columns(2)
    with email_col1:
        email_id = st.text_input("이메일 아이디", placeholder="예: kspole", key="email_id", label_visibility="collapsed")
    with email_col2:
        email_domain = st.selectbox("도메인", ["선택/직접입력", "@naver.com", "@daum.net", "@hanmail.net", "@gmail.com"], key="email_domain", label_visibility="collapsed")
    
    custom_domain = ""
    if email_domain == "선택/직접입력":
        custom_domain = st.text_input("도메인 직접입력", placeholder="예: @kspole.com", key="custom_domain", label_visibility="collapsed")
        
    final_email = ""
    if email_id:
        domain_part = custom_domain.strip() if email_domain == "선택/직접입력" else email_domain
        final_email = f"{email_id.strip()}{domain_part}"
        st.session_state.c_email = final_email
    else:
        st.session_state.c_email = ""
        
    if st.session_state.c_email:
        st.session_state.show_skip_checkbox = False

    if st.session_state.show_skip_checkbox and not st.session_state.c_email:
        st.markdown("<div style='background-color:#fff3cd; color:#856404; padding:15px; border-radius:5px; border:1px solid #ffeeba; margin-bottom:15px;'>", unsafe_allow_html=True)
        st.markdown("<b>⚠️ 주문서만 보내겠습니까?</b><br>견적서를 메일로 받으시려면 <b>위의 메일 주소</b>를 입력해주세요.<br>견적서 수신 없이 주문서만 발송하시려면 <b>아래 체크박스를 선택</b> 후 다시 버튼을 눌러주세요.", unsafe_allow_html=True)
        skip_email_checked = st.checkbox("☑️ 주문서만 발송", key="skip_email_checked")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        skip_email_checked = st.session_state.get("skip_email_checked", False)

    # 견적서 HTML 생성
    if d_method == "경동화물":
        if st.session_state.d_branch:
            d_branch_str = f"({st.session_state.d_branch})"
        else:
            d_branch_str = "(지점 미입력 - 본사에서 현장 주소 확인 후 발송)"
    else:
        d_branch_str = ""
        
    biz_attached_str = "첨부됨" if biz_reg_file is not None else "없음"
    
    html_template = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap" rel="stylesheet">
        <title>견적서</title>
        <style>
            body {{ font-family: 'Noto Sans KR', sans-serif; padding: 20px; line-height: 1.6; color: #333; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 20px; font-size: 14px; }}
            th, td {{ border: 1px solid #000; padding: 10px; text-align: center; }}
            th {{ background-color: #f4f4f4; }}
            h1, h2, h3 {{ color: #2e6c80; font-family: 'Noto Sans KR', sans-serif; }}
            .total-price {{ color: #d9534f; font-size: 22px; font-weight: bold; margin-top: 20px; text-align: right; }}
        </style>
    </head>
    <body>
        <h1 style="text-align:center; font-size:30px;">견 적 서</h1>
        <p style="text-align:right;">발행일: {pd.Timestamp.now().strftime('%Y-%m-%d')}<br>공급자: 한국시스템폴</p>
        
        <h3>👤 고객 및 배송 정보</h3>
        <ul>
            <li><b>주문자:</b> <span id="val_cname"></span> (<span id="val_phone"></span>)</li>
            <li><b>받는 사람:</b> {st.session_state.r_name} ({st.session_state.r_phone})</li>
            <li><b>배송지 주소:</b> {st.session_state.d_addr}</li>
            <li><b>배송 방법:</b> {d_method} {d_branch_str}</li>
            <li><b>배송비 결제:</b> {d_pay}</li>
            <li><b>사업자등록증:</b> {biz_attached_str}</li>
        </ul>

        <table>
            <thead>
                <tr>
                    <th>구분</th>
                    <th>제품 및 옵션명</th>
                    <th>수량</th>
                    <th>단가</th>
                    <th>합계</th>
                </tr>
            </thead>
            <tbody>
                {cart_trs}
            </tbody>
        </table>
        
        <div class="total-price">최종 합계: {int(total_sum):,}원 (VAT 별도)</div>
        
        <div style="margin-top:20px; font-size:14px; background:#f9f9f9; padding:15px; border-left:4px solid #2e6c80;">
            ※ 주문제작건은 별도 단가가 적용되어 청구됩니다.<br>
            ※ 위 내용은 담당자와 통화 후 변동될 수 있습니다.<br>
            <b>담당자 : 이사 이 현 욱 (010-3304-2221)</b>
        </div>
    </body>
    </html>
    """

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    btn_c1, btn_c2, btn_c3 = st.columns([1.2, 1, 1.2])
    with btn_c1: submit_btn = st.button("🚀 주문서 보내기 / 내 메일로도 견적서 받기", type="primary", width="stretch")
    with btn_c2: send_quote_btn = st.button("📧 내 메일로 견적서만 받기", width="stretch")
    with btn_c3:
        prt = f"""
        <button onclick='openP()' style='width:100%;height:42px;background:#2e6c80;color:white;border:none;border-radius:8px;cursor:pointer;font-weight:bold;'>🖨️ 견적서 인쇄/저장 (PC권장)</button>
        <script>
        function openP(){{
            var html = `{html_template}`;
            html = html.replace('<span id="val_cname"></span>', '{st.session_state.c_name}');
            html = html.replace('<span id="val_phone"></span>', '{st.session_state.p_phone}');
            
            var isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
            if (isMobile) {{
                var blob = new Blob([html], {{type: "text/html;charset=utf-8"}});
                var url = URL.createObjectURL(blob);
                var a = document.createElement("a");
                a.href = url;
                a.download = "KSP_견적서.html";
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                alert("모바일에서는 파일 앱에 HTML 문서로 다운로드되었습니다.");
            }} else {{
                var win = window.open('','_blank');
                win.document.write(html);
                win.document.write('<div style="text-align:center; margin-top:30px;"><button onclick="window.print()" style="padding:10px 20px; cursor:pointer;">인쇄 / PDF저장</button></div>');
                win.document.close();
            }}
        }}
        </script>
        """
        components.html(prt, height=45)

    # 버튼 클릭 시 방어 로직 및 메일 발송
    if submit_btn or send_quote_btn:
        if not st.session_state.c_name or not st.session_state.p_phone:
            st.warning("⚠️ 업체명과 연락처 정보가 누락되었습니다. 새로고침 후 다시 로그인해 주세요.")
        elif submit_btn and d_method != "경동화물" and not st.session_state.d_addr:
            st.warning("⚠️ 주문을 처리하기 위해 '배송지 주소'를 입력해 주세요.")
        elif submit_btn and d_method == "경동화물" and not st.session_state.d_addr and not st.session_state.d_branch:
            st.warning("⚠️ 경동화물 배송을 위해 '배송지 주소' 또는 '경동화물 지점명' 중 하나를 반드시 입력해 주세요.")
        elif submit_btn and not st.session_state.r_name:
            st.warning("⚠️ '받는 사람 이름'을 입력해 주세요.")
        elif submit_btn and not st.session_state.r_phone:
            st.warning("⚠️ '받는 사람 연락처'를 입력해 주세요.")
        elif send_quote_btn and not st.session_state.c_email:
            st.warning("⚠️ 견적서를 받으실 이메일 주소를 입력해 주세요.")
        elif submit_btn and not st.session_state.c_email and not skip_email_checked:
            st.session_state.show_skip_checkbox = True
            st.rerun() 
        else:
            if submit_btn:  
                mail_cname = st.session_state.c_name
                mail_phone = st.session_state.p_phone
                subject = f"🔔 [주문] {mail_cname}"
                to_emails = f"kspole@naver.com"
                if st.session_state.c_email: to_emails += f",{st.session_state.c_email}"
            else:  
                mail_cname = "한국시스템폴 (내부보관용)"
                mail_phone = "010-3304-2221"
                subject = f"📄 [견적서 보관용] 한국시스템폴 제품 단가표"
                to_emails = st.session_state.c_email
            
            email_html_body = html_template.replace('<span id="val_cname"></span>', mail_cname)
            email_html_body = email_html_body.replace('<span id="val_phone"></span>', mail_phone)
            
            # 주문 발송 시 로그 엑셀에도 기록 저장 (배송, 수령인 추가)
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            order_items = " / ".join([f"[{item['p']}] {item['s']} ({item['q']}개)" for item in st.session_state.cart if not item.get('is_opt')])
            delivery_str = f"{d_method} {d_branch_str} ({d_pay})" if d_method else ""
            receiver_str = f"{st.session_state.r_name} / {st.session_state.r_phone}" if st.session_state.r_name else ""
            
            log_type = "주문 발송 완료" if submit_btn else "견적서 발송 완료"
            log_data = pd.DataFrame([{
                "시간": now, 
                "구분": log_type,
                "업체명": st.session_state.c_name, 
                "연락처": utils.format_phone(st.session_state.p_phone), 
                "내용/담은제품": order_items,
                "배송지_및_방법": f"{st.session_state.d_addr} | {delivery_str}",
                "수령인_정보": receiver_str
            }])
            try:
                if not os.path.exists("access_log.csv"): 
                    log_data.to_csv("access_log.csv", index=False, encoding='utf-8-sig')
                else: 
                    old_df = pd.read_csv("access_log.csv", on_bad_lines='skip', dtype=str)
                    new_df = pd.concat([old_df, log_data], ignore_index=True)
                    new_df.to_csv("access_log.csv", index=False, encoding='utf-8-sig')
            except: pass

            try:
                import smtplib
                from email.message import EmailMessage
                
                EMAIL_SENDER = "leehw05221092@gmail.com"
                EMAIL_PASSWORD = "vrwfpdbmshemnljp" 
                
                msg = EmailMessage()
                msg['Subject'] = subject
                msg['From'] = EMAIL_SENDER
                recipient_list = [email.strip() for email in to_emails.split(",") if email.strip()]
                msg['To'] = ", ".join(recipient_list)
                
                msg.add_alternative(email_html_body, subtype='html')
                
                attachment_data = email_html_body.encode('utf-8')
                msg.add_attachment(attachment_data, maintype='text', subtype='html', filename="KSP_견적서.html")
                
                if biz_reg_file is not None:
                    file_bytes = biz_reg_file.getvalue()
                    file_type = biz_reg_file.type if biz_reg_file.type else 'application/octet-stream'
                    if '/' in file_type:
                        maintype, subtype = file_type.split('/', 1)
                    else:
                        maintype, subtype = 'application', 'octet-stream'
                    msg.add_attachment(file_bytes, maintype=maintype, subtype=subtype, filename=f"사업자등록증_{biz_reg_file.name}")
                
                srv = smtplib.SMTP('smtp.gmail.com', 587)
                srv.starttls()
                srv.login(EMAIL_SENDER, EMAIL_PASSWORD)
                srv.send_message(msg)
                srv.quit()
                
                st.session_state.mail_sent = True
                
                if submit_btn:
                    if st.session_state.c_email:
                        st.success("✅ 주문서 메일 발송이 완료되었습니다! (입력하신 메일로도 견적서가 함께 발송되었습니다)")
                    else:
                        st.success("✅ 본사로 주문서 발송이 완료되었습니다!")
                        st.session_state.show_skip_checkbox = False
                else:
                    st.success("✅ 입력하신 메일로 견적서 발송이 완료되었습니다!")
                    
            except Exception as e: 
                st.error(f"❌ 발송 실패: {e}")