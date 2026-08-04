import plotly.express as px
import streamlit as st

from src import queries
from src.services import authenticate_user
from src.ui import (
    alert_badge,
    kpi_row,
    setup_page,
    show_database_status,
    show_dataframe,
)


setup_page("홈 / 로그인")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = ""
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "user_role" not in st.session_state:
    st.session_state.user_role = ""

show_database_status()

if not st.session_state.logged_in:
    st.title("Auto Parts MES LOGIN", text_alignment="center")

    col_left, col_center, col_right = st.columns([1, 2, 1])

    with col_center:
        st.write("")
        with st.form("login_form"):
            st.subheader(" 사용자 인증")
            user_id_input = st.text_input("아이디", placeholder="아이디 입력")
            password_input = st.text_input(
                "비밀번호", type="password", placeholder="비밀번호 입력"
            )
            login_button = st.form_submit_button("로그인", use_container_width=True)

        if login_button:
            user = authenticate_user(user_id_input, password_input)
            if user is not None:
                st.session_state.logged_in = True
                st.session_state.user_id = user["user_id"]
                st.session_state.user_name = user["user_name"]
                st.session_state.user_role = user["role"]
                st.success("로그인되었습니다!")
                st.rerun()
            else:
                st.error("아이디 또는 비밀번호가 올바르지 않거나, 비활성화된 계정입니다.")

else:
    role_theme = {
        "ADMIN": ("#B0392B", "🛡️"),
        "OPERATOR": ("#2B5F8A", "⚙️"),
        "INSPECTOR": ("#2E8B57", "🔍"),
    }
    banner_color, banner_icon = role_theme.get(st.session_state.user_role, ("#6A4C93", "👤"))

    col_user, col_logout = st.columns([4, 1])
    with col_user:
        st.markdown(
            f"""
            <div style="background: linear-gradient(90deg, {banner_color}, {banner_color}CC);
                        border-radius: 12px; padding: 16px 20px; color: white; margin-bottom: 8px;">
                <div style="font-size: 22px; font-weight: 700;">
                    {banner_icon} {st.session_state.user_name} 님, 환영합니다!
                </div>
                <div style="font-size: 13px; opacity: 0.9;">
                    Auto Parts MES에 {st.session_state.user_role} 권한으로 접속 중입니다.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_logout:
        st.write("")
        if st.button(" 로그아웃", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_id = ""
            st.session_state.user_name = ""
            st.session_state.user_role = ""
            st.rerun()

    st.divider()

    st.subheader(" 주요 기능 메뉴")

    # ------------------------------------------------------------------
    # pages/ 폴더의 실제 파일명에 맞춰 경로를 조정해주세요.
    # 지금까지 만든 페이지: 01_품목관리, 02_거래처관리, 03_공정설비관리
    # ------------------------------------------------------------------
    ALL_ROLES = ("ADMIN", "OPERATOR", "INSPECTOR")
    menu_items = [
        ("품목 관리", "품목/도면스펙 조회·등록·수정", "pages/01_품목관리.py", ALL_ROLES),
        ("거래처 관리", "공급업체/고객사 등록", "pages/02_거래처관리.py", ("ADMIN", "OPERATOR")),
        ("공정/설비 관리", "공정 종류 및 설비 등록", "pages/03_공정설비관리.py", ("ADMIN", "OPERATOR")),
        ("라우팅/BOM 관리", "제품별 공정순서 및 단계별 BOM 등록", "pages/04_라우팅BOM관리.py", ("ADMIN", "OPERATOR")),
        ("원자재 입고", "원자재 RECEIPT LOT 등록", "pages/05_원자재입고.py", ("ADMIN", "OPERATOR")),
        ("작업지시", "생산 작업지시 등록/취소", "pages/06_작업지시.py", ("ADMIN", "OPERATOR")),
        ("공정 실행", "라우팅 단계별 공정 실행 및 LOT 생성", "pages/07_공정실행.py", ("ADMIN", "OPERATOR")),
        ("검사 관리", "입고·반제품·완제품 검사 및 불량률 통계", "pages/08_검사관리.py", ("ADMIN", "INSPECTOR")),
        ("개별 시리얼 관리", "LOT 내 개별 부품 시리얼 부여/상태관리", "pages/09_시리얼관리.py", ALL_ROLES),
        ("출하 관리", "완제품 LOT 출하 등록 / 이력 조회", "pages/10_출하관리.py", ("ADMIN", "OPERATOR")),
        ("LOT 추적", "다단계 정방향/역방향 추적", "pages/11_LOT추적.py", ALL_ROLES),
        ("사용자 관리", "계정 등록 / 권한 관리 (ADMIN 전용)", "pages/12_사용자관리.py", ("ADMIN",)),
    ]

    current_role = st.session_state.get("user_role")
    visible_menu_items = [
        (title, desc, path) for title, desc, path, roles in menu_items if current_role in roles
    ]

    menu_cols = st.columns(3)
    for idx, (title, desc, path) in enumerate(visible_menu_items):
        with menu_cols[idx % 3]:
            with st.container(border=True):
                st.markdown(f"**{title}**")
                st.caption(desc)
                st.page_link(path, label="이동", icon="➡️")

    st.markdown("---")

    st.subheader(" 시스템 현황 요약")
    counts = queries.table_counts()
    if not counts.empty:
        count_map = dict(zip(counts["table_name"], counts["row_count"]))
        kpi_row(
            [
                ("등록 품목 수", f"{count_map.get('item', 0):,} 개", "kpi-red"),
                ("보유 LOT 수", f"{count_map.get('lot', 0):,} 개", "kpi-blue"),
                ("등록 라우팅 수", f"{count_map.get('routing', 0):,} 개", "kpi-purple"),
                ("작업지시 수", f"{count_map.get('work_order', 0):,} 건", "kpi-gold"),
                ("공정 실행 건수", f"{count_map.get('operation', 0):,} 건", "kpi-green"),
                ("출하 건수", f"{count_map.get('shipment', 0):,} 건", "kpi-teal"),
            ]
        )
    else:
        alert_badge("아직 등록된 품목이 없습니다. 품목 관리 페이지에서 먼저 등록해주세요.", "warning")

    st.markdown("---")

    st.subheader("작업지시 진행 현황")
    wo_progress_df = queries.work_order_progress()
    if wo_progress_df.empty:
        st.info("진행 중인 작업지시가 없습니다.")
    else:
        for _, row in wo_progress_df.iterrows():
            total = int(row["total_steps"]) or 1
            done = int(row["completed_steps"])
            pct = min(done / total * 100, 100)
            bar_color = "#2E8B57" if done == total else ("#E0B84B" if done > 0 else "#B0392B")
            st.markdown(
                f"""
                <div class="stock-row">
                    <div class="stock-label">{row['work_order_no']} ({row['item_name']})</div>
                    <div class="stock-bar-bg">
                        <div class="stock-bar-fill" style="width:{pct:.0f}%; background:{bar_color};"></div>
                    </div>
                    <div class="stock-value">{done}/{total} 단계</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("---")

    st.subheader("원자재 재고 알림")
    stock_df = queries.material_stock_summary()
    alert_col1, alert_col2 = st.columns(2)
    with alert_col1:
        low_count = int((stock_df["remaining_qty"] <= 0).sum()) if not stock_df.empty else 0
        if low_count > 0:
            alert_badge(f"잔량 소진된 원자재 {low_count}건 — 원자재 입고가 필요합니다.", "danger")
        else:
            alert_badge("잔량 소진된 원자재가 없습니다.", "ok")
    with alert_col2:
        low_stock_count = (
            int(((stock_df["remaining_qty"] > 0) & (stock_df["remaining_qty"] < stock_df["total_received_qty"] * 0.2)).sum())
            if not stock_df.empty
            else 0
        )
        if low_stock_count > 0:
            alert_badge(f"입고량 대비 20% 미만으로 남은 원자재 {low_stock_count}건", "warning")
        else:
            alert_badge("재고 부족 경고 없음", "ok")

    if not stock_df.empty:
        fig_stock = px.bar(
            stock_df.sort_values("remaining_qty"),
            x="remaining_qty",
            y="item_name",
            orientation="h",
            color="remaining_qty",
            color_continuous_scale=["#B0392B", "#E0B84B", "#2E8B57"],
            labels={"item_name": "원자재", "remaining_qty": "잔량"},
        )
        fig_stock.update_layout(
            showlegend=False,
            coloraxis_showscale=False,
            margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            height=max(220, len(stock_df) * 32),
        )
        st.plotly_chart(fig_stock, use_container_width=True)

    st.markdown("---")

    st.subheader("최근 활동")
    activity_df = queries.recent_activity(limit=8)
    if activity_df.empty:
        st.info("최근 활동 이력이 없습니다.")
    else:
        tag_map = {
            "RECEIPT": ("tag-receipt", "dot-receipt", "입고"),
            "OPERATION": ("tag-production", "dot-production", "공정"),
            "SHIPMENT": ("tag-shipment", "dot-shipment", "출하"),
        }
        rows_html = []
        for _, row in activity_df.iterrows():
            tag_class, dot_class, tag_label = tag_map.get(
                row["event_type"], ("tag-production", "dot-production", row["event_type"])
            )
            qty_text = f"{row['qty']:,.0f}" if row["qty"] is not None else "-"
            rows_html.append(
                f"""
                <div class="timeline-item">
                    <div class="timeline-dot {dot_class}"></div>
                    <div style="flex:1;">
                        <span class="timeline-tag {tag_class}">{tag_label}</span>
                        <b>{row['ref_no']}</b>
                        &nbsp;|&nbsp; {row['item_name']}
                        &nbsp;|&nbsp; 수량 {qty_text}
                        &nbsp;|&nbsp; <span style="color:#888;">{row['event_date']}</span>
                    </div>
                </div>
                """
            )
        st.markdown("".join(rows_html), unsafe_allow_html=True)
