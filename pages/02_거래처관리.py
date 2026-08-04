import streamlit as st

from src import queries
from src.services import PartnerRegistration, PartnerUpdate, register_partner, update_partner
from src.ui import metric_row, require_role, setup_page, show_dataframe


setup_page("거래처 관리")
require_role("ADMIN", "OPERATOR")
st.title("거래처 관리")
st.markdown("---")

tab_search, tab_create, tab_edit = st.tabs(["조회", "신규 등록", "수정"])

with tab_search:
    keyword = st.text_input("거래처명 검색")
    partner_type = st.selectbox("거래처 유형", ["전체", "SUPPLIER", "CUSTOMER"])

    df = queries.partners(keyword=keyword, partner_type=partner_type)

    if not df.empty:
        metric_row(
            [
                ("전체 거래처", len(df)),
                ("공급업체", int((df["partner_type"] == "SUPPLIER").sum())),
                ("고객사", int((df["partner_type"] == "CUSTOMER").sum())),
            ]
        )

    st.subheader("조회 결과")
    show_dataframe(df)

with tab_create:
    if "last_partner_created" in st.session_state:
        st.success("거래처가 등록되었습니다.")
        st.write(st.session_state.pop("last_partner_created"))

    with st.form("partner_create_form"):
        new_partner_name = st.text_input("거래처명")
        new_partner_type = st.selectbox("거래처 유형", ["SUPPLIER", "CUSTOMER"])
        new_contact = st.text_input("담당자/연락처 (선택)")

        create_submitted = st.form_submit_button("거래처 등록", type="primary")

    if create_submitted:
        data = PartnerRegistration(
            partner_name=new_partner_name,
            partner_type=new_partner_type,
            contact=new_contact or None,
        )
        try:
            result = register_partner(data)
            st.session_state["last_partner_created"] = result
            st.rerun()
        except ValueError as exc:
            st.error(str(exc))

with tab_edit:
    if "last_partner_updated" in st.session_state:
        st.success("거래처 정보가 수정되었습니다.")
        st.write(st.session_state.pop("last_partner_updated"))

    all_partners = queries.active_partners_for_select()
    if not all_partners:
        st.info("등록된 거래처가 없습니다.")
    else:
        edit_options = {
            f"{p['partner_name']} ({p['partner_type']})": p["partner_id"] for p in all_partners
        }
        edit_label = st.selectbox("수정할 거래처", list(edit_options.keys()))
        edit_partner_id = edit_options[edit_label]
        current = queries.partner_by_id(edit_partner_id)

        with st.form("partner_edit_form"):
            st.text_input("거래처 유형 (수정 불가)", value=current["partner_type"], disabled=True)
            edit_partner_name = st.text_input("거래처명", value=current["partner_name"])
            edit_contact = st.text_input("담당자/연락처", value=current["contact"] or "")

            edit_submitted = st.form_submit_button("수정 저장", type="primary")

        if edit_submitted:
            data = PartnerUpdate(
                partner_id=edit_partner_id,
                partner_name=edit_partner_name,
                contact=edit_contact or None,
            )
            try:
                result = update_partner(data)
                st.session_state["last_partner_updated"] = result
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))
