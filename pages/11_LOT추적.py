import streamlit as st

from src import queries
from src.ui import require_role, setup_page, show_dataframe


setup_page("LOT 추적")
require_role("ADMIN", "OPERATOR", "INSPECTOR")
st.title("LOT 추적")
st.markdown("---")

tab_forward, tab_backward = st.tabs(["정방향 추적 (원자재 → 완제품)", "역방향 추적 (완제품 → 원자재)"])

with tab_forward:
    st.caption("원자재 LOT 하나를 골라, 이 원자재가 어떤 공정들을 거쳐 어떤 완제품이 되었는지 추적합니다.")

    material_lots = queries.lots_for_select(lot_type="RECEIPT")
    if not material_lots:
        st.warning("원자재 입고 LOT가 없습니다.")
    else:
        options = {
            f"{lot['lot_no']} | {lot['item_name']} | 수량 {lot['qty']:,.0f}": lot["lot_id"]
            for lot in material_lots
        }
        selected_label = st.selectbox("추적할 원자재 LOT", list(options.keys()), key="forward_select")
        lot_id = options[selected_label]

        nodes_df = queries.forward_trace_nodes(lot_id)
        edges_df = queries.forward_trace_edges(lot_id)
        shipments_df = queries.forward_trace_shipments(lot_id)

        st.subheader("추적 경로")
        if edges_df.empty:
            st.info("이 원자재 LOT를 사용한 공정 실행 이력이 아직 없습니다.")
        else:
            for _, row in edges_df.iterrows():
                st.markdown(
                    f"`{row['from_lot_no']}`({row['from_item_name']}) "
                    f"—[{row['step_no']}단계 {row['process_name']}, {row['used_qty']:,.1f} 투입]→ "
                    f"`{row['to_lot_no']}`({row['to_item_name']}, {row['produced_qty']:,.0f} 산출)"
                )

        st.subheader("영향을 받은 전체 LOT")
        show_dataframe(nodes_df)

        st.subheader("출하 이력")
        if shipments_df.empty:
            st.info("아직 출하까지 이어지지 않았습니다.")
        else:
            show_dataframe(shipments_df)

with tab_backward:
    st.caption("완제품(또는 반제품) LOT 하나를 골라, 이걸 만드는 데 어떤 원자재/반제품이 쓰였는지 역추적합니다.")

    output_lots = queries.lots_for_select(lot_type="FINISHED") + queries.lots_for_select(lot_type="WIP")
    if not output_lots:
        st.warning("완제품/반제품 LOT가 없습니다.")
    else:
        options = {
            f"{lot['lot_no']} | {lot['item_name']} | {lot['lot_type']} | 수량 {lot['qty']:,.0f}": lot["lot_id"]
            for lot in output_lots
        }
        selected_label = st.selectbox("추적할 완제품/반제품 LOT", list(options.keys()), key="backward_select")
        lot_id = options[selected_label]

        nodes_df = queries.backward_trace_nodes(lot_id)
        edges_df = queries.backward_trace_edges(lot_id)

        st.subheader("추적 경로")
        if edges_df.empty:
            st.info("이 LOT에 대한 공정 실행 이력이 없습니다.")
        else:
            for _, row in edges_df.iterrows():
                st.markdown(
                    f"`{row['to_lot_no']}`({row['to_item_name']}) "
                    f"←[{row['step_no']}단계 {row['process_name']}, {row['used_qty']:,.1f} 투입]— "
                    f"`{row['from_lot_no']}`({row['from_item_name']})"
                )

        st.subheader("이 LOT을 만드는 데 사용된 전체 원자재/반제품")
        show_dataframe(nodes_df)

st.markdown("---")
st.caption(
    "정방향 추적은 원자재 문제가 발생했을 때 영향받는 완제품/출하처를 찾는 데, "
    "역방향 추적은 완제품 품질 문제가 발생했을 때 원인이 된 원자재 LOT를 찾는 데 사용한다."
)
