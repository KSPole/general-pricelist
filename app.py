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

# 👉 [수정됨] 파비콘(아이콘)으로 'favicon.png' 파일을 불러오도록 옵션(page_icon) 추가
st.set_page_config(page_title="한국시스템폴 디지털 단가표", page_icon="favicon.png", layout="wide")

# 👉 자바스크립트를 이용해 영어가 화면에 뜨자마자 한글로 강제 변환
components.html("""
<script>
document.addEventListener("DOMContentLoaded", function() {
    const parentDoc = window.parent.document;
    
    function enforceLowercaseKeyboard() {
        const pwInputs = parentDoc.querySelectorAll('input[type="text"]');
        pwInputs.forEach(input => {
            if (input.placeholder && input.placeholder.includes("비밀번호")) {
                input.setAttribute("autocapitalize", "none"); 
                input.setAttribute("autocorrect", "off");     
                input.setAttribute("spellcheck", "false");    
                input.setAttribute("inputmode", "verbatim");
            }
        });
    }

    // 💡 스트림릿 파일 첨부 영문 텍스트 강제 한글화 함수
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

    // 화면이 바뀔 때마다 실시간으로 감지해서 번역
    const observer = new MutationObserver(() => {
        enforceLowercaseKeyboard();
        translateUploader();
    });
    observer.observe(parentDoc.body, { childList: true, subtree: true });

    if (!parentDoc.getElementById("custom-enter-js")) {
        const script = parentDoc.createElement("script");
        script.id = "custom-enter-js";
        script.innerHTML = `
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Enter') {
                    const active = document.activeElement;
                    if (active && active.tagName === 'INPUT' && (active.type === 'text' || active.type === 'number' || active.type === 'email')) {
                        if (active.closest('form')) return;
                        if (active.placeholder && active.placeholder.includes("비밀번호")) return; 
                        e.preventDefault();
                        if (active.placeholder && active.placeholder.includes("연락처")) {
                            const clean_val = active.value.replace(/[^0-9]/g, '');
                            if (clean_val.length < 9) {
                                alert("⚠️ 연락처를 정확하게 입력해 주세요.");
                                return; 
                            }
                        }
                        const inputs = Array.from(document.querySelectorAll('input[type="text"], input[type="number"], input[type="email"]'));
                        const idx = inputs.indexOf(active);
                        if (idx > -1 && idx < inputs.length - 1) inputs[idx + 1].focus();
                        else active.blur();
                    }
                }
            }, true);
        `;
        parentDoc.head.appendChild(script);
    }
});
</script>
""", height=0, width=0)

st.markdown("""
<style>
    .block-container { padding-top: 2.5rem !important; padding-bottom: 1.5rem !important; }
    h1 { text-align: center; line-height: 1.3; font-size: 32px !important; color: #333; margin-top: 10px !important; margin-bottom: 25px !important; letter-spacing: -1px; }
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

if 'show_admin' not in st.session_state: st.session_state.show_admin = False
if 'admin_auth' not in st.session_state: st.session_state.admin_auth = False
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'cart' not in st.session_state: st.session_state.cart = []
if 'selected_cat' not in st.session_state: st.session_state.selected_cat = None
if 'rk_main' not in st.session_state: st.session_state.rk_main = 0       
if 'rk_lvl1' not in st.session_state: st.session_state.rk_lvl1 = 0       
if 'rk_lvl2' not in st.session_state: st.session_state.rk_lvl2 = 0       
if 'admin_login_error' not in st.session_state: st.session_state.admin_login_error = False
if 'log_login_error' not in st.session_state: st.session_state.log_login_error = False

for field in ['c_name', 'p_name', 'p_phone', 'c_email', 'd_addr', 'd_branch']:
    if field not in st.session_state: st.session_state[field] = ""

rk = st.session_state.rk_main

# -----------------------------------------------------------------------------
# 4. 로그인 폼 
# -----------------------------------------------------------------------------
c1, c2 = st.columns([9.5, 0.5])
with c2:
    if st.button("⚙️", help="접속 로그 확인"):
        st.session_state.show_admin = not st.session_state.show_admin
        st.rerun()

if st.session_state.show_admin:
    st.markdown("<h2 style='text-align: center; color: #2e6c80;'>👑 접속 로그 확인 메뉴</h2>", unsafe_allow_html=True)
    if not st.session_state.admin_auth:
        st.markdown("<div style='max-width: 400px; margin: 0 auto; text-align: center;'>", unsafe_allow_html=True)
        def check_log_login():
            pw = st.session_state.get("admin_log_pw", "")
            if pw.lower() == "locker1092***": st.session_state.admin_auth = True
            elif pw: st.session_state.log_login_error = True
        admin_pw = st.text_input("관리자 비밀번호를 입력하세요", placeholder="비밀번호 입력", key="admin_log_pw", on_change=check_log_login)
        st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
        if st.button("로그 접속하기", type="primary", use_container_width=True) or (admin_pw and st.session_state.get('admin_log_pw') != ""):
            if admin_pw.lower() == "locker1092***":
                st.session_state.admin_auth = True
                st.rerun()
            elif admin_pw: st.error("비밀번호가 틀렸습니다.")
        if st.session_state.log_login_error:
            st.error("비밀번호가 틀렸습니다.")
            st.session_state.log_login_error = False
        if st.button("닫기 (메인 화면으로)", use_container_width=True):
            st.session_state.show_admin = False
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='max-width: 800px; margin: 0 auto;'>", unsafe_allow_html=True)
        if os.path.exists("access_log.csv"):
            try:
                df_log = pd.read_csv("access_log.csv")
                st.dataframe(df_log, use_container_width=True)
                csv = df_log.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
                st.download_button(label="📥 접속 명단 엑셀 다운로드", data=csv, file_name='고객접속명단.csv', mime='text/csv')
            except Exception: st.error("기록을 불러올 수 없습니다.")
        else: st.info("아직 접속한 고객이 없습니다.")
        st.markdown("<div style='margin-top:30px;'></div>", unsafe_allow_html=True)
        if st.button("닫기 (로그아웃 및 메인으로)", use_container_width=True):
            st.session_state.show_admin = False
            st.session_state.admin_auth = False
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop() 

if not st.session_state.logged_in:
    st.markdown("<div style='max-width: 600px; margin: 40px auto; text-align: center;'>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: #2e6c80; margin-bottom: 10px;'>🔒 단가표 열람</h2>", unsafe_allow_html=True)
    with st.form("login_form"):
        c_name = st.text_input("업체명 (상호) *", placeholder="예: 한국시스템폴 (입력 후 엔터)")
        p_name = st.text_input("담당자 성함 *", placeholder="예: 홍길동 (입력 후 엔터)")
        p_phone_str = st.text_input("연락처 *", placeholder="연락처 숫자만 입력 (정확하게 입력, 입력 후 엔터)")
        st.markdown("<p style='font-size: 15px; font-weight: bold; color: #333; margin-bottom: 2px; margin-top: 10px;'>이메일 주소 *</p>", unsafe_allow_html=True)
        email_col1, email_col2 = st.columns(2)
        email_id = email_col1.text_input("이메일 아이디", placeholder="예: kspole", label_visibility="collapsed")
        email_domain = email_col2.selectbox("도메인 선택", ["직접입력", "@naver.com", "@hanmail.net", "@daum.net", "@gmail.com"], label_visibility="collapsed")
        custom_domain = st.text_input("도메인 직접 입력", placeholder="예: @kspole.com (직접 입력 후 엔터)", label_visibility="collapsed") if email_domain == "직접입력" else ""
        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("단가표 접속하기", type="primary", use_container_width=True)
        if submitted:
            p_phone = re.sub(r'[^0-9]', '', p_phone_str) 
            domain_part = custom_domain.strip() if email_domain == "직접입력" else email_domain
            final_email = f"{email_id.strip()}{domain_part}"
            if not c_name.strip() or not p_name.strip() or not p_phone or not email_id.strip(): st.warning("⚠️ 모든 정보를 입력해 주셔야 접속이 가능합니다.")
            elif len(p_phone) < 9: st.warning("⚠️ 연락처를 정확하게 입력해 주세요. (9자리 이상)")
            elif "@" not in final_email or len(final_email.split("@")[1]) < 2: st.warning("⚠️ 올바른 이메일 주소(@ 포함)를 끝까지 입력해 주세요.")
            else:
                st.session_state.update({"c_name":c_name, "p_name":p_name, "p_phone":p_phone, "c_email":final_email, "logged_in":True})
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                try:
                    log_data = pd.DataFrame([{"접속일시": now, "업체명": c_name, "이름": p_name, "연락처": p_phone, "이메일": final_email}])
                    if not os.path.exists("access_log.csv"): log_data.to_csv("access_log.csv", index=False, encoding='utf-8-sig')
                    else: log_data.to_csv("access_log.csv", mode='a', header=False, index=False, encoding='utf-8-sig')
                except: pass 
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
    with st.expander("🛠️ 본사 직원 / 관리자 전용 바로 접속"):
        def do_admin_login():
            pw = st.session_state.get('pw_bypass', '')
            if pw.lower() == "locker1092***":
                st.session_state.update({"c_name":"한국시스템폴 (본사)", "p_name":"관리자", "p_phone":"010-0000-0000", "c_email":"admin@kspole.com", "logged_in":True})
            elif pw: st.session_state.admin_login_error = True
        admin_pw_bypass = st.text_input("직원 비밀번호 입력", placeholder="비밀번호 입력", key="pw_bypass", on_change=do_admin_login) 
        if st.button("비밀번호로 즉시 접속", type="primary", use_container_width=True) or (admin_pw_bypass and st.session_state.get('pw_bypass') != ""):
            do_admin_login()
            if st.session_state.get('logged_in'): st.rerun()
        if st.session_state.get('admin_login_error'):
            st.error("비밀번호가 틀렸습니다.")
            st.session_state.admin_login_error = False
    st.stop()

# -----------------------------------------------------------------------------
# 5. 메인 대시보드
# -----------------------------------------------------------------------------
st.markdown("<h1>한국시스템폴 디지털 단가표</h1>", unsafe_allow_html=True)

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
# 6. 장바구니 및 하단 로직 
# -----------------------------------------------------------------------------
if is_main_ready:
    st.markdown("<h2>3. 단가 확인 및 파일(사진) 첨부</h2>", unsafe_allow_html=True)
    mc1, mc2, mc3, mc4 = st.columns([4.5, 2, 2.5, 1])
    quantity = mc4.number_input("수량", min_value=1, step=1, value=1, key=f"q_main_{rk}", label_visibility="collapsed")
    
    ui_img_html = ""
    if valid_paths:
        import utils
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
                import utils
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
                cart_trs += f"<tr><td>옵션 부품</td><td>└ {sub['o']}</td><td>{sub['q']}</td><td style='text-align:right;'>{utils.format_price(sub['u'], sub['o'])}</td><td style='text-align:right;'>{utils.format_price(sub['t'], sub['o'])}</td></tr>"
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"<div class='summary-box'><div style='font-size:18px; font-weight:bold; color:#555;'>총 예상 견적 금액</div><div class='summary-price'>{total_sum:,}원</div><div style='font-size:13px; color:#777; margin-top:5px;'>(부가세, 배송비 별도)</div></div>", unsafe_allow_html=True)
    
    col_req1, col_req2 = st.columns(2)
    rcv_addr = col_req1.text_input("📍 현장/받으실 주소", placeholder="예: 서울시 강남구 역삼동 123", value=st.session_state.get('d_addr', ''))
    rcv_branch = col_req2.text_input("🏢 취급 지점", placeholder="예: KSP 서울지사", value=st.session_state.get('d_branch', ''))
    st.session_state.d_addr = rcv_addr
    st.session_state.d_branch = rcv_branch

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🗑️ 장바구니 비우기", use_container_width=True):
            st.session_state.cart = []
            st.rerun()
    with c2:
        if st.button("🚀 발주/견적 요청하기 (이메일 전송)", type="primary", use_container_width=True):
            st.info("메일을 발송 중입니다. 잠시만 기다려주세요...")
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            from email.mime.application import MIMEApplication
            from email.mime.image import MIMEImage

            SENDER_EMAIL = "systempole1092@gmail.com"
            SENDER_PW = "xmsv zxec uawh aoym" 
            RECV_EMAILS = ["systempole1092@gmail.com", st.session_state.c_email]
            
            msg = MIMEMultipart()
            msg['Subject'] = f"[{st.session_state.c_name}] 단가표 견적/발주 요청"
            msg['From'] = SENDER_EMAIL
            msg['To'] = ", ".join(RECV_EMAILS)

            html = f"""
            <html>
            <body style="font-family: 'Malgun Gothic', sans-serif;">
                <h2 style="color: #2e6c80;">📦 단가표 견적 및 발주 요청 내역</h2>
                <ul style="line-height: 1.6; font-size: 15px;">
                    <li><b>업체명:</b> {st.session_state.c_name}</li>
                    <li><b>담당자:</b> {st.session_state.p_name}</li>
                    <li><b>연락처:</b> {utils.format_phone(st.session_state.p_phone)}</li>
                    <li><b>회신 이메일:</b> {st.session_state.c_email}</li>
                    <li><b>현장/받으실 주소:</b> {rcv_addr if rcv_addr else '미입력'}</li>
                    <li><b>취급 지점:</b> {rcv_branch if rcv_branch else '미입력'}</li>
                    <li><b>총 예상 금액:</b> <span style="color:#d9534f; font-weight:bold; font-size:18px;">{total_sum:,}원</span> (부가세, 배송비 별도)</li>
                </ul>
                <table style="width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 14px;">
                    <tr style="background-color: #2e6c80; color: white;">
                        <th style="padding: 10px; border: 1px solid #ddd;">구분</th>
                        <th style="padding: 10px; border: 1px solid #ddd;">상세 내역</th>
                        <th style="padding: 10px; border: 1px solid #ddd;">수량</th>
                        <th style="padding: 10px; border: 1px solid #ddd;">단가</th>
                        <th style="padding: 10px; border: 1px solid #ddd;">금액</th>
                    </tr>
                    {cart_trs}
                </table>
                <br>
            """
            if all_ext_img_paths:
                html += "<h3 style='color: #2e6c80;'>📷 선택하신 제품 도면/이미지 참고</h3>"
                for idx, path in enumerate(all_ext_img_paths):
                    html += f"<img src='cid:img_{idx}' style='max-width:300px; max-height:300px; border:1px solid #ccc; margin-right:10px; margin-bottom:10px;'>"
            
            html += "</body></html>"
            msg.attach(MIMEText(html, 'html'))
            
            for idx, path in enumerate(all_ext_img_paths):
                try:
                    img_data = utils.process_image_to_white_bg(path)
                    img = MIMEImage(img_data)
                    img.add_header('Content-ID', f'<img_{idx}>')
                    img.add_header('Content-Disposition', 'inline', filename=os.path.basename(path))
                    msg.attach(img)
                except Exception: pass

            for item in st.session_state.cart:
                if item.get('files'):
                    for f in item['files']:
                        part = MIMEApplication(f['bytes'])
                        part.add_header('Content-Disposition', 'attachment', filename=f['name'])
                        msg.attach(part)
            try:
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(SENDER_EMAIL, SENDER_PW)
                server.send_message(msg)
                server.quit()
                st.session_state.cart = []
                st.success("✅ 견적/발주 요청 메일이 본사와 고객님의 이메일로 성공적으로 발송되었습니다!")
                st.balloons()
            except Exception as e:
                st.error(f"❌ 메일 발송 중 오류가 발생했습니다: {e}")