import streamlit as st

from src import queries
from src.services import (
    EquipmentRegistration,
    ProcessRegistration,
    register_equipment,
    register_process,
    set_equipment_active,
)
from src.ui import metric_row, require_role, setup_page, show_dataframe


setup_page("공정/설비 관리")
require_role("ADMIN", "OPERATOR")
st.title("공정 / 설비 관리")
st.markdown("---")

tab_process, tab_equipment = st.tabs(["공정 종류", "설비"])

with tab_process:
    st.caption("프레스, 용접, 도장, 조립, 검사처럼 라우팅에서 사용할 공정 종류를 등록합니다.")

    if "last_process_created" in st.session_state:
        st.success("공정이 등록되었습니다.")
        st.write(st.session_state.pop("last_process_created"))

    with st.form("process_create_form"):
        new_process_code = st.text_input("공정 코드 (예: PRESS, WELD, PAINT)")
        new_process_name = st.text_input("공정명 (예: 프레스, 용접, 도장)")
        process_submitted = st.form_submit_button("공정 등록", type="primary")

    if process_submitted:
        data = ProcessRegistration(process_code=new_process_code, process_name=new_process_name)
        try:
            result = register_process(data)
            st.session_state["last_process_created"] = result
            st.rerun()
        except ValueError as exc:
            st.error(str(exc))

    st.markdown("---")
    st.subheader("등록된 공정 목록")
    show_dataframe(queries.process_list(), "등록된 공정이 없습니다.")

with tab_equipment:
    st.caption("공정별로 사용하는 설비를 등록합니다.")

    if "last_equipment_created" in st.session_state:
        st.success("설비가 등록되었습니다.")
        st.write(st.session_state.pop("last_equipment_created"))

    processes = queries.active_process_for_select()
    if not processes:
        st.warning("먼저 공정 종류를 하나 이상 등록하세요.")
    else:
        process_options = {f"{p['process_code']} | {p['process_name']}": p["process_code"] for p in processes}

        with st.form("equipment_create_form"):
            new_equipment_code = st.text_input("설비 코드")
            new_equipment_name = st.text_input("설비명")
            new_process_label = st.selectbox("소속 공정", list(process_options.keys()))
            equipment_submitted = st.form_submit_button("설비 등록", type="primary")

        if equipment_submitted:
            data = EquipmentRegistration(
                equipment_code=new_equipment_code,
                equipment_name=new_equipment_name,
                process_code=process_options[new_process_label],
            )
            try:
                result = register_equipment(data)
                st.session_state["last_equipment_created"] = result
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))

    st.markdown("---")
    st.subheader("설비 목록")
    process_filter_options = ["전체"] + [p["process_code"] for p in processes]
    process_filter = st.selectbox("공정 필터", process_filter_options)
    equipment_df = queries.equipment_list(process_code=process_filter)

    if not equipment_df.empty:
        metric_row(
            [
                ("전체 설비 수", len(equipment_df)),
                ("사용 중", int((equipment_df["is_active"] == "Y").sum())),
                ("비활성", int((equipment_df["is_active"] == "N").sum())),
            ]
        )

    show_dataframe(equipment_df, "등록된 설비가 없습니다.")

    if not equipment_df.empty:
        st.markdown("---")
        toggle_options = {
            f"{row['equipment_code']} | {row['equipment_name']} "
            f"({'사용' if row['is_active'] == 'Y' else '비활성'})": row
            for _, row in equipment_df.iterrows()
        }
        toggle_label = st.selectbox("사용여부 변경할 설비", list(toggle_options.keys()))
        toggle_row = toggle_options[toggle_label]
        new_status = "N" if toggle_row["is_active"] == "Y" else "Y"
        action_label = "비활성화" if new_status == "N" else "다시 활성화"

        if st.button(f"{toggle_row['equipment_code']} {action_label}"):
            try:
                set_equipment_active(int(toggle_row["equipment_id"]), new_status)
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))
