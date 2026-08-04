import streamlit as st

from src import queries
from src.services import (
    BomLineRegistration,
    RoutingStepRegistration,
    add_bom_line,
    add_routing_step,
    get_or_create_routing,
    remove_bom_line,
    remove_routing_step,
)
from src.ui import require_role, setup_page, show_dataframe


setup_page("라우팅 / BOM 관리")
require_role("ADMIN", "OPERATOR")
st.title("라우팅 / BOM 관리")
st.caption("제품이 어떤 공정을 어떤 순서로 거치는지(라우팅), 각 공정마다 어떤 원자재/반제품이 얼마나 필요한지(BOM)를 등록합니다.")
st.markdown("---")

st.subheader("제품별 라우팅 등록 현황")
show_dataframe(queries.products_with_routing_status(), "등록된 제품이 없습니다.")

st.markdown("---")

products = queries.active_items_for_select("PRODUCT")
if not products:
    st.warning("라우팅을 등록하려면 완제품(PRODUCT) 품목이 먼저 있어야 합니다.")
    st.stop()

product_options = {f"{p['item_code']} | {p['item_name']}": p["item_id"] for p in products}
product_label = st.selectbox("라우팅을 관리할 제품", list(product_options.keys()))
product_item_id = product_options[product_label]

existing_routing = queries.routing_by_product(product_item_id)

st.subheader("1. 라우팅 기본 정보")
with st.form("routing_form"):
    routing_name = st.text_input(
        "라우팅 이름",
        value=existing_routing["routing_name"] if existing_routing else f"{product_label} 표준 공정",
    )
    routing_submitted = st.form_submit_button(
        "라우팅 저장" if existing_routing else "라우팅 생성", type="primary"
    )

if routing_submitted:
    try:
        result = get_or_create_routing(product_item_id, routing_name)
        st.success("라우팅이 저장되었습니다.")
        st.write(result)
        st.rerun()
    except ValueError as exc:
        st.error(str(exc))

routing = queries.routing_by_product(product_item_id)

if routing is None:
    st.info("먼저 라우팅을 생성하세요.")
    st.stop()

routing_id = routing["routing_id"]

st.markdown("---")
st.subheader("2. 공정 단계 (라우팅 스텝)")

steps_df = queries.routing_steps(routing_id)
show_dataframe(steps_df, "등록된 공정 단계가 없습니다. 아래에서 첫 단계를 추가하세요.")

processes = queries.active_process_for_select()
# 산출 품목은 반제품 또는 완제품만 선택 가능 (원자재는 산출물이 될 수 없음)
output_candidates = queries.active_items_for_select("SEMI_PRODUCT") + queries.active_items_for_select(
    "PRODUCT"
)

if not processes:
    st.warning("공정 종류가 없습니다. '공정/설비 관리' 페이지에서 먼저 등록하세요.")
elif not output_candidates:
    st.warning("산출 가능한 반제품/완제품 품목이 없습니다. 품목 관리에서 먼저 등록하세요.")
else:
    process_options = {f"{p['process_code']} | {p['process_name']}": p["process_code"] for p in processes}
    output_options = {
        f"{o['item_code']} | {o['item_name']} ({o['item_type']})": o["item_id"] for o in output_candidates
    }
    next_no = queries.next_step_no(routing_id)

    with st.form("routing_step_form"):
        st.caption(f"다음 단계 번호: {next_no} (자동 부여, 항상 마지막에 추가됩니다)")
        step_process_label = st.selectbox("공정 선택", list(process_options.keys()))
        step_output_label = st.selectbox(
            "이 단계의 산출 품목 (마지막 단계라면 최종 완제품을 선택)", list(output_options.keys())
        )
        step_submitted = st.form_submit_button("공정 단계 추가", type="primary")

    if step_submitted:
        data = RoutingStepRegistration(
            routing_id=routing_id,
            process_code=process_options[step_process_label],
            output_item_id=output_options[step_output_label],
        )
        try:
            result = add_routing_step(data)
            st.success("공정 단계가 추가되었습니다.")
            st.write(result)
            st.rerun()
        except ValueError as exc:
            st.error(str(exc))

    if not steps_df.empty:
        st.markdown("---")
        st.caption("단계 삭제 (BOM이나 실제 공정 실행 이력이 없는 단계만 삭제 가능)")
        step_delete_options = {
            f"{int(row['step_no'])}단계 | {row['process_name']} → {row['output_item_name']}": int(
                row["routing_step_id"]
            )
            for _, row in steps_df.iterrows()
        }
        delete_label = st.selectbox("삭제할 단계", list(step_delete_options.keys()), key="step_delete_select")
        if st.button("선택한 단계 삭제", type="secondary"):
            try:
                remove_routing_step(step_delete_options[delete_label])
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))

st.markdown("---")
st.subheader("3. 단계별 BOM (공정마다 투입되는 원자재/반제품)")

if steps_df.empty:
    st.info("먼저 공정 단계를 하나 이상 추가하세요.")
else:
    step_bom_options = {
        f"{int(row['step_no'])}단계 | {row['process_name']} → {row['output_item_name']}": int(
            row["routing_step_id"]
        )
        for _, row in steps_df.iterrows()
    }
    bom_step_label = st.selectbox("BOM을 관리할 공정 단계", list(step_bom_options.keys()))
    selected_routing_step_id = step_bom_options[bom_step_label]

    bom_df = queries.bom_for_routing_step(selected_routing_step_id)
    show_dataframe(bom_df, "이 단계에 등록된 BOM이 없습니다.")

    materials = queries.active_items_for_select("MATERIAL") + queries.active_items_for_select(
        "SEMI_PRODUCT"
    )
    if not materials:
        st.warning("투입 가능한 원자재/반제품 품목이 없습니다.")
    else:
        material_options = {
            f"{m['item_code']} | {m['item_name']} ({m['item_type']}, {m['unit']})": m
            for m in materials
        }

        with st.form("bom_line_form"):
            material_label = st.selectbox("투입 원자재/반제품 선택", list(material_options.keys()))
            qty_per_unit = st.number_input("단위당 소요량", min_value=0.0, value=1.0, step=0.1)
            bom_submitted = st.form_submit_button("BOM 라인 추가", type="primary")

        if bom_submitted:
            material = material_options[material_label]
            data = BomLineRegistration(
                routing_step_id=selected_routing_step_id,
                material_item_id=material["item_id"],
                qty_per_unit=qty_per_unit,
            )
            try:
                result = add_bom_line(data)
                st.success("BOM 라인이 추가되었습니다.")
                st.write(result)
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))

        if not bom_df.empty:
            st.caption("BOM 라인 삭제")
            bom_delete_options = {
                f"{row['material_name']} ({row['qty_per_unit']} {row['material_unit']})": int(row["bom_id"])
                for _, row in bom_df.iterrows()
            }
            bom_delete_label = st.selectbox(
                "삭제할 BOM 라인", list(bom_delete_options.keys()), key="bom_delete_select"
            )
            if st.button("선택한 BOM 라인 삭제", type="secondary"):
                try:
                    remove_bom_line(bom_delete_options[bom_delete_label])
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))
