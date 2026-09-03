from datetime import date

import streamlit as st

from src import queries
from src.services import assign_serials, set_serial_status
from src.ui import metric_row, require_role, setup_page, show_dataframe


setup_page("시리얼 관리")
require_role("ADMIN", "OPERATOR", "INSPECTOR")
st.title("시리얼 관리")
st.markdown("---")

tab_assign, tab_lookup = st.tabs(["시리얼 부여", "시리얼 조회 / 상태 변경"])

with tab_assign:
    if "last_serial_result" in st.session_state:
        st.success("시리얼이 부여되었습니다.")
        st.write(st.session_state.pop("last_serial_result"))

    lot_type_label = st.radio("대상 LOT 유형", ["반제품 (WIP)", "완제품 (FINISHED)"], horizontal=True)
    lot_type = "WIP" if lot_type_label.startswith("반제품") else "FINISHED"

    candidates = queries.lots_without_serial(lot_type)
    if not candidates:
        st.info("시리얼을 부여할 수 있는 LOT가 없습니다. (모든 LOT에 이미 부여되었거나 대상이 없습니다)")
    else:
        lot_options = {
            f"{lot['lot_no']} | {lot['item_name']} | 수량 {lot['qty']:,.0f}": lot for lot in candidates
        }

        with st.form("serial_assign_form"):
            selected_label = st.selectbox("대상 LOT", list(lot_options.keys()))
            selected_lot = lot_options[selected_label]
            serial_prefix = st.text_input("시리얼 접두어", value=selected_lot["lot_no"])
            count = st.number_input(
                "부여할 개수", min_value=1, value=int(selected_lot["qty"]), step=1
            )
            created_date_input = st.date_input("부여일자", value=date.today())

            assign_submitted = st.form_submit_button("시리얼 일괄 부여", type="primary")

        if assign_submitted:
            try:
                result = assign_serials(
                    lot_id=selected_lot["lot_id"],
                    serial_prefix=serial_prefix,
                    count=int(count),
                    created_date=created_date_input,
                )
                st.session_state["last_serial_result"] = result
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))

with tab_lookup:
    all_lots = queries.lots(lot_type="전체")
    if all_lots.empty:
        st.info("등록된 LOT가 없습니다.")
    else:
        lot_no_input = st.text_input("LOT 번호로 검색 (부분 검색 가능)")
        filtered = (
            all_lots[all_lots["lot_no"].str.contains(lot_no_input, case=False, na=False)]
            if lot_no_input
            else all_lots
        )

        if filtered.empty:
            st.info("검색 결과가 없습니다.")
        else:
            lot_lookup_options = {
                f"{row['lot_no']} | {row['item_name']}": int(row["lot_id"]) for _, row in filtered.iterrows()
            }
            lookup_label = st.selectbox("LOT 선택", list(lot_lookup_options.keys()))
            serials_df = queries.serials_for_lot(lot_lookup_options[lookup_label])

            if not serials_df.empty:
                metric_row(
                    [
                        ("총 시리얼 수", len(serials_df)),
                        ("진행중", int((serials_df["status"] == "IN_PROCESS").sum())),
                        ("완료", int((serials_df["status"] == "COMPLETED").sum())),
                        ("폐기", int((serials_df["status"] == "SCRAPPED").sum())),
                    ]
                )

            show_dataframe(serials_df, "이 LOT에는 부여된 시리얼이 없습니다.")

            if not serials_df.empty:
                st.markdown("---")
                st.caption("개별 시리얼 상태 변경")
                serial_options = {
                    f"{row['serial_no']} ({row['status']})": int(row["unit_serial_id"])
                    for _, row in serials_df.iterrows()
                }
                serial_label = st.selectbox("상태 변경할 시리얼", list(serial_options.keys()))
                new_status = st.selectbox("변경할 상태", ["IN_PROCESS", "COMPLETED", "SCRAPPED"])
                if st.button("상태 변경 저장"):
                    try:
                        set_serial_status(serial_options[serial_label], new_status)
                        st.rerun()
                    except ValueError as exc:
                        st.error(str(exc))
