from datetime import date
import time

import streamlit as st

from src import queries
from src.sensor import read_latest_count, reset_counter
from src.services import OperationRegistration, register_operation
from src.ui import require_role, setup_page, show_dataframe


setup_page("공정 실행")
require_role("ADMIN", "OPERATOR")
st.title("공정 실행")
st.caption("작업지시를 골라 라우팅의 다음 단계를 실행합니다. 단계는 순서대로만 진행할 수 있습니다.")
st.markdown("---")

if "last_operation_result" in st.session_state:
    st.success("공정이 정상적으로 완료 처리되었습니다.")
    st.write(st.session_state.pop("last_operation_result"))
    st.markdown("---")

wo_df = queries.work_orders(status_filter="전체")
active_wo_df = wo_df[wo_df["status"].isin(["PLANNED", "IN_PROGRESS"])] if not wo_df.empty else wo_df

if active_wo_df.empty:
    st.info("공정을 실행할 수 있는 작업지시(PLANNED/IN_PROGRESS)가 없습니다.")
    st.stop()

wo_options = {
    f"{row['work_order_no']} | {row['item_name']} | {row['planned_qty']:,.0f} | {row['status']}": int(
        row["work_order_id"]
    )
    for _, row in active_wo_df.iterrows()
}
wo_label = st.selectbox("작업지시 선택", list(wo_options.keys()))
work_order_id = wo_options[wo_label]

st.subheader("진행 현황")
routing_row = queries.work_order_by_id(work_order_id)
progress_df = queries.operations_for_work_order(work_order_id)
show_dataframe(progress_df, "아직 실행된 공정이 없습니다. 아래에서 첫 단계를 실행하세요.")

next_step = queries.next_routing_step_for_work_order(work_order_id)

st.markdown("---")

if next_step is None:
    st.success("🟢 이 작업지시의 모든 공정이 완료되었습니다.")
    st.stop()

st.subheader(f"다음 실행할 단계: {next_step['step_no']}단계 — {next_step['process_name']}")
st.caption(f"산출 품목: {next_step['output_item_code']} | {next_step['output_item_name']} ({next_step['output_item_type']})")

equipment_candidates = queries.active_equipment_for_select(next_step["process_code"])
equipment_options = {"(선택 안 함)": None}
for eq in equipment_candidates:
    equipment_options[f"{eq['equipment_code']} | {eq['equipment_name']}"] = eq["equipment_id"]

operation_date = st.date_input("작업일자", value=date.today())

st.markdown("##### 자동 생산 카운터 (리드 스위치)")
st.caption("작업대의 리드 스위치가 자석 통과를 셀 때마다 값이 올라감. 새 단계를 시작하기 전엔 카운터를 리셋.")

with st.expander("이 카운터는 왜 필요한가 (설계 배경 보기)", expanded=False):
    st.markdown(
        "리드 센서를 부품이 지나가는 자리에 두고, 부품(또는 부품을 담은 지그)에 자석을 붙여두면 "
        "**부품이 하나 지나갈 때마다 자동으로 1씩 카운트**"
    )

    col_before, col_after = st.columns(2)
    with col_before:
        st.markdown("**기존**")
        st.markdown(
            "작업자가 완료된 개수를 직접 세어서 \u201c이번 단계 산출수량\u201d에 손으로 입력. "
            "바쁘거나 개수가 많을수록 세는 도중 실수가 생기기 쉬움."
        )
    with col_after:
        st.markdown("**확장**")
        st.markdown(
            "리드 센서가 실제로 지나간 개수를 실시간으로 집계 → 그 값이 산출수량 입력란에 "
            "자동으로 채워짐. 사람은 확인만 하면 되고, 필요하면 직접 수정도 가능."
        )

    st.markdown(
        "센서 하나가 \u201c사람이 세는 일\u201d을 대신해주는 가장 단순한 형태의 자동화이지만, "
        "생산수량은 이후 BOM 소요량 계산과 재고 차감의 기준이 되기 때문에 "
        "**입력 정확도가 시스템 전체 데이터 신뢰성에 직결**된다는 점에서 의미가 있음."
    )

counter_col1, counter_col2, counter_col3 = st.columns([1, 1, 2])
with counter_col1:
    if st.button("카운터 리셋"):
        reset_counter()
        st.session_state["reed_counter_value"] = 0
        st.success("카운터를 0으로 초기화.")
with counter_col2:
    count_duration = st.number_input(
        "카운트 시간(초)", min_value=5, max_value=300, value=30, step=5, key="count_duration"
    )
with counter_col3:
    start_counting = st.button("카운트 시작", type="secondary")

if start_counting:
    progress = st.progress(0)
    count_placeholder = st.empty()
    last_count = st.session_state.get("reed_counter_value", 0)
    for i in range(int(count_duration)):
        c = read_latest_count()
        if c is not None:
            last_count = c
        count_placeholder.metric("현재 카운트", last_count)
        progress.progress((i + 1) / count_duration)
        time.sleep(1)
    st.session_state["reed_counter_value"] = last_count
    st.success(f"카운트 종료: 총 {last_count}개 감지됨. 아래 산출수량에 자동 반영.")

default_qty = float(st.session_state.get("reed_counter_value") or 0) or float(routing_row["planned_qty"])
qty = st.number_input(
    "이번 단계 산출수량", min_value=0.0, value=default_qty, step=10.0,
    help="자동 카운터로 값을 채웠어도 필요하면 직접 수정 가능.",
)
equipment_label = st.selectbox("사용 설비 (선택)", list(equipment_options.keys()))

bom_df = queries.bom_for_routing_step(next_step["routing_step_id"])

material_rows = []

if bom_df.empty:
    st.info("이 단계에는 등록된 BOM이 없습니다. 원자재 투입 없이 바로 완료 처리됩니다.")
else:
    st.subheader("투입 원자재/반제품")
    for _, bom_row in bom_df.iterrows():
        material_item_id = int(bom_row["material_item_id"])
        required_qty = float(bom_row["qty_per_unit"]) * qty

        st.markdown(
            f"**{bom_row['material_name']}** ({bom_row['material_code']}) "
            f"— 필요수량 약 **{required_qty:,.1f} {bom_row['material_unit']}**"
        )

        
        material_item = queries.item_by_id(material_item_id)
        lot_type = "RECEIPT" if material_item["item_type"] == "MATERIAL" else "WIP"
        available_lots = queries.lots_with_balance_for_item(material_item_id, lot_type)

        if not available_lots:
            st.error(f"'{bom_row['material_name']}'의 사용 가능한 {lot_type} LOT가 없습니다.")
            st.markdown("---")
            continue

        lot_label_map = {
            f"{lot['lot_no']} | 잔량 {lot['remaining_qty']:,.0f}": lot for lot in available_lots
        }

        default_labels = []
        remaining_needed = required_qty
        for label, lot in lot_label_map.items():
            if remaining_needed <= 0:
                break
            default_labels.append(label)
            remaining_needed -= lot["remaining_qty"]

        selected_labels = st.multiselect(
            f"{bom_row['material_name']} 투입 LOT 선택",
            list(lot_label_map.keys()),
            default=default_labels,
            key=f"op_select_{material_item_id}",
        )

        remaining_needed = required_qty
        for label in selected_labels:
            lot = lot_label_map[label]
            default_use = min(lot["remaining_qty"], remaining_needed) if remaining_needed > 0 else 0.0
            used_qty = st.number_input(
                f"　└ {lot['lot_no']} 투입수량",
                min_value=0.0,
                value=float(default_use if default_use > 0 else lot["remaining_qty"]),
                step=1.0,
                key=f"op_qty_{lot['lot_id']}",
            )
            remaining_needed -= used_qty
            material_rows.append(
                {
                    "material_item_id": material_item_id,
                    "material_lot_id": lot["lot_id"],
                    "qty": used_qty,
                }
            )

        st.markdown("---")

if st.button("이 단계 완료 처리", type="primary"):
    data = OperationRegistration(
        work_order_id=work_order_id,
        routing_step_id=next_step["routing_step_id"],
        equipment_id=equipment_options[equipment_label],
        operation_date=operation_date,
        qty=qty,
        material_rows=material_rows,
    )
    try:
        result = register_operation(data)
        st.session_state["last_operation_result"] = result
        st.session_state.pop("reed_counter_value", None)
        st.rerun()
    except ValueError as exc:
        st.error(str(exc))
