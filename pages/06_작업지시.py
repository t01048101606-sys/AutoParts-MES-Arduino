from datetime import date

import streamlit as st

from src import queries
from src.services import WorkOrderRegistration, cancel_work_order, register_work_order
from src.ui import metric_row, require_role, setup_page, show_dataframe


setup_page("작업지시")
require_role("ADMIN", "OPERATOR")
st.title("작업지시")
st.markdown("---")

tab_register, tab_list = st.tabs(["작업지시 등록", "작업지시 조회 / 취소"])

with tab_register:
    if "last_wo_created" in st.session_state:
        st.success("작업지시가 등록되었습니다.")
        st.write(st.session_state.pop("last_wo_created"))

    products = queries.products_with_active_routing()
    if not products:
        st.warning("라우팅이 등록된 제품이 없습니다. '라우팅/BOM 관리'에서 먼저 라우팅을 만드세요.")
    else:
        product_options = {
            f"{p['item_code']} | {p['item_name']} (라우팅: {p['routing_name']})": p for p in products
        }

        next_wo_id = queries.next_id("work_order", "work_order_id")

        with st.form("work_order_form"):
            product_label = st.selectbox("대상 제품", list(product_options.keys()))
            work_order_no = st.text_input(
                "작업지시번호",
                value=f"WO-{date.today().strftime('%Y%m%d')}-{next_wo_id:04d}",
            )
            plan_date = st.date_input("작업지시일자", value=date.today())
            planned_qty = st.number_input("계획수량", min_value=0.0, value=100.0, step=10.0)

            wo_submitted = st.form_submit_button("작업지시 등록", type="primary")

        if wo_submitted:
            selected_product = product_options[product_label]
            data = WorkOrderRegistration(
                work_order_no=work_order_no,
                product_item_id=selected_product["product_item_id"],
                routing_id=selected_product["routing_id"],
                planned_qty=planned_qty,
                plan_date=plan_date,
            )
            try:
                result = register_work_order(data)
                st.session_state["last_wo_created"] = result
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))

with tab_list:
    col1, col2 = st.columns(2)
    keyword = col1.text_input("작업지시번호 또는 품목명 검색")
    status_filter = col2.selectbox("상태", ["전체", "PLANNED", "IN_PROGRESS", "COMPLETED", "CANCELED"])

    wo_df = queries.work_orders(keyword=keyword, status_filter=status_filter)

    if not wo_df.empty:
        metric_row(
            [
                ("작업지시 건수", len(wo_df)),
                ("계획중(PLANNED)", int((wo_df["status"] == "PLANNED").sum())),
                ("진행중(IN_PROGRESS)", int((wo_df["status"] == "IN_PROGRESS").sum())),
                ("완료(COMPLETED)", int((wo_df["status"] == "COMPLETED").sum())),
            ]
        )

    show_dataframe(wo_df, "등록된 작업지시가 없습니다.")

    cancelable = wo_df[wo_df["status"].isin(["PLANNED", "IN_PROGRESS"])] if not wo_df.empty else wo_df
    if not cancelable.empty:
        st.markdown("---")
        st.subheader("작업지시 취소")
        st.caption("이미 공정이 하나라도 실행된 작업지시는 취소할 수 없습니다.")
        cancel_options = {
            f"{row['work_order_no']} | {row['item_name']} | {row['planned_qty']:,.0f}": int(
                row["work_order_id"]
            )
            for _, row in cancelable.iterrows()
        }
        cancel_label = st.selectbox("취소할 작업지시", list(cancel_options.keys()))
        if st.button("선택한 작업지시 취소", type="secondary"):
            try:
                cancel_work_order(cancel_options[cancel_label])
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))
