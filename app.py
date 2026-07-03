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

st.set_page_config(page_title="한국시스템폴 디지털 단가표", layout="wide", page_icon="🔵")

# 👉 KSP 파비콘 적용, 텍스트 변환, 그리고 "당겨서 새로고침 방지" 강제 JS 주입
components.html("""
<script>
document.addEventListener("DOMContentLoaded", function() {
    const parentDoc = window.parent.document;
    
    // 1. KSP 파비콘(아이콘) 생성 및 적용 (강제 덮어쓰기)
    let link = parentDoc.querySelector("link[rel~='icon']");
    if (!link) {
        link = parentDoc.createElement('link');
        link.rel = 'icon';
        parentDoc.head.appendChild(link);
    }
    link.href = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect width="100" height="100" fill="%23004b9b" rx="20"/><text x="50%25" y="55%25" dominant-baseline="middle" text-anchor="middle" font-size="38" font-family="Arial" font-weight="bold" fill="white">KSP</text></svg>';

    // 2. 모바일 '당겨서 새로고침' 강제 방지 (스크롤 아웃 방지)
    let startY = 0;
    parentDoc.addEventListener('touchstart', function(e) {
        startY = e.touches[0].clientY;
    }, {passive: false});

    parentDoc.addEventListener('touchmove', function(e) {
        let top = parentDoc.documentElement.scrollTop || parentDoc.body.scrollTop;
        if (top <= 0 && e.touches[0].clientY > startY) {
            e.preventDefault(); // 맨 위에서 아래로 당기는 동작 무효화
        }
    }, {passive: false});

    // 3. 자잘한 영어 텍스트 한글화
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

    const observer = new MutationObserver(() => { translateUploader(); });
    observer.observe(parentDoc.body, { childList: true, subtree: true });
});
</script>
""", height=0, width=0)

st.markdown("""
<style>
    /* 1. 최상단 빈 여백 완벽 제거 */
    .block-container { padding-top: 1rem !important; padding-bottom: 1.5rem !important; }
    
    /* 2. Press Enter to apply 등 스트림릿 안내 문구 완벽 숨김 */
    div[data-testid="InputInstructions"] { display: none !important; }
    
    /* 3. 타이틀 정렬 및 여백 축소 */
    h1 { text-align: center !important; line-height: 1.2 !important; font-size: 30px !important; color: #333; margin-top: 0px !important; margin-bottom: 20px !important; font-weight: 900; }
    
    h2 { font-size: 24px !important; border-bottom: 2px solid #2e6c80; padding-bottom: 8px; margin-top: 15px !important; margin-bottom: 15px !important; color: #2e6c80; }
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

for field in ['c_name', 'p_name', 'p_phone', 'c_email', 'd_addr', 'd_branch']:
    if field not in st.session_state: st.session_state[field] = ""

rk = st.session_state.rk_main

# -----------------------------------------------------------------------------
# 2. 로그인 폼 (일반 고객 및 톱니바퀴)
# -----------------------------------------------------------------------------
if not st.session_state.logged_in:
    # 톱니바퀴 아이콘 우측 상단 배치
    c1, c2, c3 = st.columns([1, 8, 1])
    with c3:
        if st.button("⚙️", help="관리자 설정"):
            st.session_state.show_admin = not st.session_state.get('show_admin', False)
            st.rerun()
            
    with c2:
        st.markdown("<h1 style='color: #2e6c80;'>한국시스템폴<br>제품 단가표</h1>", unsafe_allow_html=True)

    if st.session_state.get('show_admin', False):
        st.markdown("<div style='background-color:#f1f5f9; padding:15px; border-radius:10px; margin-bottom:20px; text-align:center;'>", unsafe_allow_html=True)
        admin_pw = st.text_input("본사 직원 비밀번호", type="password")
        if st.button("관리자 접속", type="primary"):
            if admin_pw == "locker1092***":
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
        submitted = st.form_submit_button("단가표 접속하기", type="primary", use_container_width=True)
        
        if submitted:
            p_phone = re.sub(r'[^0-9]', '', p_phone_str) 
            if not c_name.strip() or not p_phone: st.warning("⚠️ 업체명과 연락처를 모두 입력해 주세요.")
            elif len(p_phone) < 9: st.warning("⚠️ 연락처를 정확하게 입력해 주세요.")
            else:
                st.session_state.update({"c_name":c_name, "p_phone":p_phone, "logged_in":True, "is_admin": False})
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# -----------------------------------------------------------------------------
# 3. 메인 대시보드
# -----------------------------------------------------------------------------
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
if st.session_state.is_admin:
    st.markdown("<h1 style='color: #2e6c80;'>한국시스템폴<br>제품 단가표 <span style='font-size:18px; color:#d9534f; vertical-align:middle;'>(관리자)</span></h1>", unsafe_allow_html=True)
    with st.expander("👑 고객 장바구니 로그 확인"):
        if os.path.exists("access_log.csv"):
            try:
                df_log = pd.read_csv("access_log.csv")
                st.dataframe(df_log.sort_values(by="시간", ascending=False), use_container_width=True)
                csv = df_log.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
                st.download_button(label="📥 접속 명단 엑셀 다운로드", data=csv, file_name='고객장바구니이력.csv', mime='text/csv')
            except: st.error("기록을 불러올 수 없습니다.")
        else: st.info("기록이 없습니다.")
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
    uploaded_files = st.file_uploader("도면, 스케치, 현장 사진 등 첨부", accept_multiple_files=True, key=f"file_upl_{rk}")
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
    
    st.markdown("<h2>✉️ 주문 접수 및 견적서 메일 받기</h2>", unsafe_allow_html=True)
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

    # 구글 웹 폰트를 삽입하여 모바일 인쇄/메일 글씨 깨짐 완벽 방지
    html_template = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap" rel="stylesheet">
        <title>견적서</title>
        <style>
            body {{ font-family: 'Noto Sans KR', 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif; padding: 20px; line-height: 1.6; color: #333; }}
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
        
        <h3>👤 고객 정보</h3>
        <ul>
            <li><b>업체명:</b> <span id="val_cname"></span></li>
            <li><b>담당자:</b> <span id="val_pname"></span></li>
            <li><b>연락처:</b> <span id="val_phone"></span></li>
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
    with btn_c1: submit_btn = st.button("🚀 주문 접수 메일 보내기", type="primary", use_container_width=True)
    with btn_c2: send_quote_btn = st.button("📧 내 메일로 견적서만 받기", use_container_width=True)
    with btn_c3:
        prt = f"""
        <button onclick='openP()' style='width:100%;height:42px;background:#2e6c80;color:white;border:none;border-radius:8px;cursor:pointer;font-weight:bold;'>🖨️ 견적서 인쇄/저장 (PC권장)</button>
        <script>
        function openP(){{
            var html = `{html_template}`;
            // 인쇄용 HTML에서는 실제 고객 데이터로 치환
            html = html.replace('<span id="val_cname"></span>', '{st.session_state.c_name}');
            html = html.replace('<span id="val_pname"></span>', '{st.session_state.get("p_name", "담당자미상")}');
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
                alert("모바일 기기에서는 글씨 깨짐 방지를 위해 견적서가 HTML 파일 형태로 다운로드 되었습니다. 파일 앱에서 열람해 주세요.");
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

    if submit_btn or send_quote_btn:
        if not st.session_state.c_name or not st.session_state.p_phone:
            st.warning("⚠️ 상호명과 연락처는 처음 로그인 시 필수 입력 사항입니다. (로그아웃됨)")
        elif send_quote_btn and not st.session_state.c_email:
            st.warning("⚠️ 내 메일로 견적서를 받으시려면 '이메일 주소'를 입력해 주세요.")
        else:
            # 요구사항: 나에게 보내기 vs 주문 보내기 데이터 분리
            if submit_btn:  # 주문서 보내기 (고객 정보 기준)
                mail_cname = st.session_state.c_name
                mail_pname = st.session_state.p_name if st.session_state.p_name else "담당자미상"
                mail_phone = st.session_state.p_phone
                subject = f"🔔 [주문] {mail_cname} ({mail_pname})"
                to_emails = f"kspole@naver.com"
                if st.session_state.c_email: to_emails += f",{st.session_state.c_email}"
            else:  # 내 메일로 보내기 (요청하신 대로 고정 데이터 적용)
                mail_cname = "한국시스템폴"
                mail_pname = "이사 이현욱"
                mail_phone = "010-3304-2221"
                subject = f"📄 [견적서 보관용] 한국시스템폴 제품 단가표"
                to_emails = st.session_state.c_email
            
            # 이메일용 HTML 내용 치환
            email_html_body = html_template.replace('<span id="val_cname"></span>', mail_cname)
            email_html_body = email_html_body.replace('<span id="val_pname"></span>', mail_pname)
            email_html_body = email_html_body.replace('<span id="val_phone"></span>', mail_phone)
            
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
                
                # 1. 본문에 예쁜 내용 추가
                msg.add_alternative(email_html_body, subtype='html')
                
                # 2. 깨짐 없는 견적서 전자문서(HTML)를 첨부파일로 추가
                attachment_data = email_html_body.encode('utf-8')
                msg.add_attachment(attachment_data, maintype='text', subtype='html', filename="KSP_견적서.html")
                
                srv = smtplib.SMTP('smtp.gmail.com', 587)
                srv.starttls()
                srv.login(EMAIL_SENDER, EMAIL_PASSWORD)
                srv.send_message(msg)
                srv.quit()
                
                if submit_btn: st.session_state.cart = []
                st.session_state.mail_sent = True
                st.success("✅ 메일 발송이 성공적으로 완료되었습니다! (견적서 파일 첨부 완료)")
                st.rerun()
            except Exception as e: 
                st.error(f"❌ 발송 실패: {e}")
