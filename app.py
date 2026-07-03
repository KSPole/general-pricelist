# =============================================================================
# 📌 한국시스템폴 디지털 단가표 - 메인 대시보드
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

st.set_page_config(page_title="한국시스템폴 디지털 단가표", layout="wide")

# 👉 KSP 파비콘 적용 및 자바스크립트 강제 제어
components.html("""
<script>
document.addEventListener("DOMContentLoaded", function() {
    const parentDoc = window.parent.document;
    
    // 1. KSP 파비콘(아이콘) 생성 및 적용
    let link = parentDoc.querySelector("link[rel~='icon']");
    if (!link) {
        link = parentDoc.createElement('link');
        link.rel = 'icon';
        parentDoc.head.appendChild(link);
    }
    // 파란 바탕에 흰색 KSP 글씨 SVG
    link.href = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect width="100" height="100" fill="%23004b9b" rx="20"/><text x="50%25" y="55%25" dominant-baseline="middle" text-anchor="middle" font-size="40" font-family="Arial" font-weight="bold" fill="white">KSP</text></svg>';

    // 2. 키보드 소문자 강제 및 번역
    function enforceLowercaseKeyboard() {
        const pwInputs = parentDoc.querySelectorAll('input[type="password"]');
        pwInputs.forEach(input => {
            input.setAttribute("autocapitalize", "none"); 
            input.setAttribute("autocorrect", "off");     
            input.setAttribute("spellcheck", "false");    
        });
    }

    function translateUploader() {
        const elements = parentDoc.querySelectorAll('span, div, small');
        elements.forEach(el => {
            if (el.childNodes.length === 1 && el.childNodes[0].nodeType === 3) {
                const text = el.textContent.trim();
                if (text === "Drag and drop file here" || text === "Drag and drop files here") {
                    el.textContent = "📁 여기에 파일을 드래그 앤 드롭 하세요";
                } else if (text === "Browse files") {
                    el.textContent = "첨부하기";
                } else if (text.includes("Limit 200MB per file")) {
                    el.textContent = "파일당 최대 200MB";
                }
            }
        });
    }

    enforceLowercaseKeyboard();
    translateUploader();

    const observer = new MutationObserver(() => {
        enforceLowercaseKeyboard();
        translateUploader();
    });
    observer.observe(parentDoc.body, { childList: true, subtree: true });
});
</script>
""", height=0, width=0)

st.markdown("""
<style>
    /* 1. 화면 최상단 여백 줄이기 및 당겨서 새로고침(로그아웃) 방지 */
    .block-container { padding-top: 1rem !important; padding-bottom: 1.5rem !important; }
    body, .stApp { overscroll-behavior-y: none !important; }
    
    /* 2. Press Enter to apply 텍스트 완벽 숨김 */
    div[data-testid="InputInstructions"] { display: none !important; }
    
    /* 3. 타이틀 가운데 정렬 */
    h1 { text-align: center !important; line-height: 1.3; font-size: 32px !important; color: #333; margin-top: 0px !important; margin-bottom: 25px !important; letter-spacing: -1px; font-weight: 900; }
    
    h2 { font-size: 24px !important; border-bottom: 2px solid #2e6c80; padding-bottom: 8px; margin-top: 15px !important; margin-bottom: 15px !important; color: #2e6c80; }
    div[data-testid="stSelectbox"] label p, div[data-testid="stNumberInput"] label p, div[data-testid="stTextInput"] label p, div[data-testid="stRadio"] label p { 
        font-size: 15px !important; font-weight: bold !important; color: #333; margin-bottom: 2px !important; 
    }
    .option-group-title { font-size: 17px; font-weight: bold; color: #fff; background-color: #2e6c80; padding: 4px 10px; border-radius: 4px; margin-top: 10px; margin-bottom: 5px; }
    .cart-card { background-color: #fff; border: 1px solid #e0e0e0; border-radius: 12px; padding: 16px; margin-bottom: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.04); position: relative; }
    .cart-del-btn { position: absolute; top: 12px; right: 12px; z-index: 10; }
    .cart-header { font-size: 24px; font-weight: 900; color: #2e6c80; margin-bottom: 8px; letter-spacing: -0.5px; width: 80%; }
    .cart-price-row { text-align: right; margin-top: 5px; }
    .cart-total { font-size: 20px; font-weight: bold; color: #d9534f; }
    .summary-box { background-color: #fff; border: 2px solid #2e6c80; border-radius: 12px; padding: 20px; margin-top: 15px; margin-bottom: 15px; text-align: center; box-shadow: 0 4px 10px rgba(46,108,128,0.15); }
    .summary-price { font-size: 32px; font-weight: 900; color: #e53935; letter-spacing: -1px; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 1. 상태 로드 및 변수 초기화
# -----------------------------------------------------------------------------
products_df, options_df = utils.load_data()
categories = list(products_df['카테고리'].dropna().unique())

if "뷸렛카메라박스" in categories:
    categories[categories.index("뷸렛카메라박스")] = "뷸렛카메라박스 / 각도기"

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'cart' not in st.session_state: st.session_state.cart = []
if 'selected_cat' not in st.session_state: st.session_state.selected_cat = None
if 'rk_main' not in st.session_state: st.session_state.rk_main = 0       
if 'rk_lvl1' not in st.session_state: st.session_state.rk_lvl1 = 0       
if 'rk_lvl2' not in st.session_state: st.session_state.rk_lvl2 = 0       

for field in ['c_name', 'p_name', 'p_phone', 'c_email', 'd_addr', 'd_branch']:
    if field not in st.session_state: st.session_state[field] = ""

rk = st.session_state.rk_main

# -----------------------------------------------------------------------------
# 2. 로그인 폼 (일반 고객 및 상단 톱니바퀴 관리자)
# -----------------------------------------------------------------------------
if not st.session_state.logged_in:
    # 우측 상단 톱니바퀴 아이콘 (설정)
    col_empty, col_gear = st.columns([9.2, 0.8])
    with col_gear:
        if st.button("⚙️", help="관리자 전용"):
            st.session_state.show_admin = not st.session_state.get('show_admin', False)
            st.rerun()

    # 톱니바퀴 누르면 열리는 관리자 로그인 창
    if st.session_state.get('show_admin', False):
        st.markdown("<div style='background-color:#f1f5f9; padding:15px; border-radius:10px; margin-bottom:20px; border:1px solid #cbd5e1;'>", unsafe_allow_html=True)
        admin_pw = st.text_input("본사 직원 비밀번호", type="password")
        if st.button("관리자 접속", type="primary"):
            if admin_pw == "locker1092***":
                st.session_state.update({"c_name":"한국시스템폴 (본사)", "p_phone":"010-0000-0000", "logged_in":True, "is_admin": True})
                st.rerun()
            else:
                st.error("❌ 비밀번호가 틀렸습니다.")
        st.markdown("</div>", unsafe_allow_html=True)

    # 일반 로그인 폼 (타이틀 가운데 정렬)
    st.markdown("<div style='max-width: 600px; margin: 10px auto; text-align: center;'>", unsafe_allow_html=True)
    st.markdown("<h1 style='color: #2e6c80;'>한국시스템폴<br>제품 단가표</h1>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        c_name = st.text_input("업체명 (상호) *", placeholder="예: 한국시스템폴")
        p_phone_str = st.text_input("연락처 *", placeholder="연락처 숫자만 입력")
        
        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("단가표 접속하기", type="primary", use_container_width=True)
        
        if submitted:
            p_phone = re.sub(r'[^0-9]', '', p_phone_str) 
            if not c_name.strip() or not p_phone: 
                st.warning("⚠️ 업체명과 연락처를 모두 입력해 주셔야 접속이 가능합니다.")
            elif len(p_phone) < 9: 
                st.warning("⚠️ 연락처를 정확하게 입력해 주세요. (9자리 이상)")
            else:
                st.session_state.update({"c_name":c_name, "p_phone":p_phone, "logged_in":True, "is_admin": False})
                st.rerun()
                
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# -----------------------------------------------------------------------------
# 3. 메인 대시보드 (단가표 & 관리자 로그 확인)
# -----------------------------------------------------------------------------
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
if st.session_state.is_admin:
    st.markdown("<h1 style='color: #2e6c80;'>한국시스템폴<br>제품 단가표 <span style='font-size:18px; color:#d9534f; vertical-align:middle;'>(관리자 모드)</span></h1>", unsafe_allow_html=True)
    with st.expander("👑 고객 장바구니 로그 확인 (언제, 누가, 무엇을 담았는지)"):
        if os.path.exists("access_log.csv"):
            try:
                df_log = pd.read_csv("access_log.csv")
                st.dataframe(df_log.sort_values(by="시간", ascending=False), use_container_width=True)
                csv = df_log.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
                st.download_button(label="📥 접속 명단 엑셀 다운로드", data=csv, file_name='고객장바구니이력.csv', mime='text/csv')
            except Exception: 
                st.error("기록을 불러올 수 없습니다.")
        else: 
            st.info("아직 장바구니에 제품을 담은 이력이 없습니다.")
else:
    st.markdown("<h1 style='color: #2e6c80;'>한국시스템폴<br>제품 단가표</h1>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

is_main_ready = False
base_price = 0
product_specs = ""
valid_paths = []
priced_options = []
zero_options = []

if st.session_state.selected_cat is None:
    num_cols = 3 
    for i in range(0, len(categories), num_cols):
        cols = st.columns(num_cols)
        for j in range(num_cols):
            if i + j < len(categories):
                cat = categories[i + j]
                if cols[j].button(cat, use_container_width=True, type="secondary", key=f"cat_{cat}_{rk}"):
                    st.session_state.selected_cat = cat
                    st.session_state.rk_main += 1
                    st.rerun()
else:
    if st.button(f"⬅️ {st.session_state.selected_cat} (뒤로가기)", type="primary"):
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
    elif "로비폰보강판" in cat_no_space: res = prod_lobby.render(filtered, options_df, rk, cat_no_space)
    elif "뷸렛카메라박스" in cat_no_space or "각도기" in cat_no_space: res = prod_bullet_angle.render(filtered, options_df, rk, cat_no_space)
    elif "앙카베이스" in cat_no_space: res = prod_anchor_base.render(filtered, options_df, rk, cat_no_space)
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
        opt_q = c4.number_input("수량", min_value=0, value=int(o['qty_per_main'] * quantity), key=f"q_opt_{idx}_{rk}_{quantity}", label_visibility="collapsed")
        o['current_cart_q'], o['total_per_main'] = opt_q, o['unit_price'] * opt_q
        
        c1.markdown(f"<div style='padding-top:8px;'>└ {o['display_name']}</div>", unsafe_allow_html=True)
        c2.markdown(f"<div style='padding-top:8px; color:#555;'>단가: <b>{utils.format_price(o['unit_price'], o['display_name'])}</b></div>", unsafe_allow_html=True)
        c3.markdown(f"<div style='padding-top:8px; color:#d9534f; font-weight:bold;'>금액: {utils.format_price(o['total_per_main'], o['display_name'])}</div>", unsafe_allow_html=True)
    
    total = base_price * quantity + sum([o['total_per_main'] for o in priced_options])
    uploaded_files = st.file_uploader("도면, 스케치, 현장 사진, 사업자등록증등 첨부", accept_multiple_files=True, key=f"file_upl_{rk}")
    st.markdown(f"<div class='summary-box'><div class='summary-price'>{utils.format_price(total, product_specs)}</div></div>", unsafe_allow_html=True)

    if st.button("🛒 장바구니에 담기", type="primary", use_container_width=True):
        import time
        bid, files_data = str(time.time()), []
        if uploaded_files:
            for f in uploaded_files: files_data.append({"name": f.name, "type": f.type, "bytes": f.getvalue()})
        opts_txt = "<br>".join([o['display_name'] for o in zero_options])
        
        item_summary = f"[{st.session_state.selected_cat}] {product_specs} ({quantity}개)"
        opt_str = ", ".join([f"{o['display_name']}({o['current_cart_q']}개)" for o in priced_options if o['current_cart_q'] > 0])
        if opt_str: item_summary += f" / 옵션: {opt_str}"
            
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_data = pd.DataFrame([{"시간": now, "업체명": st.session_state.c_name, "연락처": st.session_state.p_phone, "담은 제품": item_summary}])
        try:
            if not os.path.exists("access_log.csv"): log_data.to_csv("access_log.csv", index=False, encoding='utf-8-sig')
            else: log_data.to_csv("access_log.csv", mode='a', header=False, index=False, encoding='utf-8-sig')
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
    
    if all_ext_img_paths:
        img_tags = [f"<img src='data:image/jpeg;base64,{utils.get_image_base64(p)}' style='max-width: 250px; max-height: 250px; object-fit: contain; margin: 10px; border: 1px solid #ccc; padding: 5px; background: white; border-radius: 8px;'>" for p in all_ext_img_paths if utils.get_image_base64(p)]
        if img_tags: 
            st.markdown(f"<div style='margin-top: 40px;'><h3 style='color: #2e6c80; border-bottom: 2px solid #2e6c80; padding-bottom: 8px;'>📷 선택 제품 및 옵션 참고 이미지</h3><div>{''.join(img_tags)}</div></div>", unsafe_allow_html=True)

    st.markdown("<h2>✉️ 주문 접수 및 견적서 메일 받기</h2>", unsafe_allow_html=True)
    st.session_state.c_name = st.text_input("업체명 (상호)", value=st.session_state.c_name)
    st.session_state.p_phone = st.text_input("연락처 (숫자만 입력)", value=st.session_state.p_phone)
    st.session_state.p_name = st.text_input("담당자 성함 (선택사항)", value=st.session_state.get("p_name", ""))
    st.session_state.d_addr = st.text_input("배송지 주소 (선택사항)", value=st.session_state.get("d_addr", ""))
    
    d_method = st.radio("배송 방법", ["택배", "경동화물", "용달", "방문"], horizontal=True)
    if d_method == "경동화물": st.session_state.d_branch = st.text_input("경동화물 지점명 (입력 후 엔터)", value=st.session_state.d_branch)
    d_pay = st.radio("배송비 결제", ["선불", "착불"], horizontal=True)
    
    st.markdown("<hr style='margin:20px 0;'>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:16px; font-weight:bold; color:#2e6c80; margin-bottom:5px;'>📧 견적서 수신용 이메일 주소 (내 메일로 받기 클릭 시 필수)</p>", unsafe_allow_html=True)
    
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

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    btn_c1, btn_c2, btn_c3 = st.columns([1.2, 1, 1.2])
    with btn_c1: submit_btn = st.button("🚀 주문 접수 메일 보내기", type="primary", use_container_width=True)
    with btn_c2: send_quote_btn = st.button("📧 내 메일로 견적서만 받기", use_container_width=True)
    with btn_c3:
        prt = f"""
        <button onclick='openP()' style='width:100%;height:42px;background:#2e6c80;color:white;border:none;border-radius:8px;cursor:pointer;font-weight:bold;'>🖨️ 견적서 인쇄/저장 (PC권장)</button>
        <script>
        function openP(){{
            var html = `<html><head><title>견적서</title>
            <style>
                body{{font-family:"Malgun Gothic",sans-serif;padding:20px;}}
                table{{width:100%;border-collapse:collapse;margin-bottom:20px;}}
                th,td{{border:1px solid #000;padding:8px;text-align:center; white-space: nowrap;}}
                th{{background:#f2f2f2;}}
            </style></head><body>
            <h1>견 적 서</h1>
            <p style="text-align:right;">발행일: {pd.Timestamp.now().strftime('%Y-%m-%d')}<br>공급자: 한국시스템폴</p>
            <table><thead><tr><th>구분</th><th>제품 및 옵션명</th><th>수량</th><th>단가</th><th>합계</th></tr></thead>
            <tbody>{cart_trs}</tbody>
            <tr style="font-weight:bold;"><td colspan="4">최종 합계 금액 (VAT 별도)</td><td style="text-align:right;">{int(total_sum):,}원</td></tr>
            </table>
            <div style="margin-top:20px; font-size:14px;">
                ※ 주문제작건은 별도 단가가 적용되어 청구됩니다.<br>
                ※ 위 내용은 담당자와 통화 후 변동될 수 있습니다.<br>
                <b>담당자 : 이사 이 현 욱 (010-3304-2221)</b>
            </div>
            <div style="text-align:center; margin-top:30px;"><button onclick="window.print()">인쇄 / PDF저장</button></div>
            </body></html>`;
            
            var isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
            if (isMobile) {{
                var blob = new Blob([html], {{type: "text/html;charset=utf-8"}});
                var url = URL.createObjectURL(blob);
                var a = document.createElement("a");
                a.href = url;
                a.download = "한국시스템폴_견적서.html";
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                alert("모바일에서는 브라우저 보안상 직접 인쇄가 어렵습니다.\\n'견적서.html' 파일이 다운로드 되었습니다.\\n💡가장 편한 방법은 옆의 '내 메일로 받기'를 누르시는 것입니다.");
            }} else {{
                var win=window.open('','_blank');
                win.document.write(html);
                win.document.close();
            }}
        }}
        </script>
        """
        components.html(prt, height=45)

    if submit_btn or send_quote_btn:
        if not st.session_state.c_name or not st.session_state.p_phone:
            st.warning("⚠️ 상호명과 연락처는 필수 입력 사항입니다.")
        elif send_quote_btn and not st.session_state.c_email:
            st.warning("⚠️ 내 메일로 견적서를 받으시려면 '이메일 주소'를 완벽하게 입력해 주세요.")
        else:
            is_order = submit_btn
            name_disp = st.session_state.p_name if st.session_state.p_name else "담당자미상"
            
            if is_order:
                subject = f"🔔 [주문] {st.session_state.c_name} ({name_disp})"
                to_emails = f"kspole@naver.com"
                if st.session_state.c_email:
                    to_emails += f",{st.session_state.c_email}"
            else:
                subject = f"📄 [견적서 보관용] 한국시스템폴 단가표 내역 ({st.session_state.c_name})"
                to_emails = st.session_state.c_email
            
            branch_info = f" (지점명: {st.session_state.d_branch})" if d_method == "경동화물" else ""
            
            html_body = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: 'Malgun Gothic', sans-serif; line-height: 1.6; color: #333; }}
                    table {{ border-collapse: collapse; width: 100%; margin-top: 15px; margin-bottom: 20px; font-size: 14px; }}
                    th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
                    th {{ background-color: #f4f4f4; color: #333; }}
                    h3 {{ color: #2e6c80; border-bottom: 1px solid #eee; padding-bottom: 5px; }}
                    .total-price {{ color: #d9534f; font-size: 22px; font-weight: bold; margin-top: 20px; }}
                </style>
            </head>
            <body>
                <h2 style='color:#2e6c80;'>📦 주문/견적 상세 내역</h2>
                
                <h3>👤 고객 및 배송 정보</h3>
                <ul>
                    <li><b>업체명(상호):</b> {st.session_state.c_name}</li>
                    <li><b>담당자명:</b> {name_disp}</li>
                    <li><b>연락처:</b> {st.session_state.p_phone}</li>
                    <li><b>이메일:</b> {st.session_state.c_email}</li>
                    <li><b>배송지 주소:</b> {st.session_state.d_addr}</li>
                    <li><b>배송 방법:</b> {d_method}{branch_info} ({d_pay})</li>
                </ul>

                <h3>🛒 상세 주문 내역</h3>
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
            </body>
            </html>
            """
            
            try:
                import smtplib
                from email.message import EmailMessage
                
                EMAIL_SENDER = "leehw05221092@gmail.com"
                EMAIL_PASSWORD = "vrwfpdbmshemnljp" 
                
                msg = EmailMessage()
                msg['Subject'] = subject
                msg['From'] = EMAIL_SENDER
                
                # 오류 방지를 위해 콤마로 구분된 여러 메일 주소를 완벽하게 리스트로 변환
                recipient_list = [email.strip() for email in to_emails.split(",") if email.strip()]
                msg['To'] = ", ".join(recipient_list)
                
                msg.add_alternative(html_body, subtype='html')
                
                srv = smtplib.SMTP('smtp.gmail.com', 587)
                srv.starttls()
                srv.login(EMAIL_SENDER, EMAIL_PASSWORD)
                srv.send_message(msg)
                srv.quit()
                
                if is_order: st.session_state.cart = []
                st.session_state.mail_sent = True
                st.success("✅ 메일 발송이 성공적으로 완료되었습니다!")
                st.rerun()
            except Exception as e: 
                st.error(f"❌ 발송 실패: {e}")
