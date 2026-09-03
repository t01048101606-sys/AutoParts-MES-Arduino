import time

import streamlit as st

from src import queries
from src.sensor import read_latest_reading
from src.services import log_handling_event
from src.ui import alert_badge, kpi_row, require_role, setup_page, show_dataframe


setup_page("현장 모니터링")
require_role("ADMIN", "OPERATOR", "INSPECTOR")
st.title("현장 모니터링 (센서)")
st.caption("아두이노(충격/초음파/온습도 센서)로 완제품 출하 대기 구역의 취급 품질을 실시간으로 감시.")

with st.expander("이 페이지는 왜 필요한가 (설계 배경 보기)", expanded=False):
    st.markdown("#### 센서별 의미")
    st.table(
        {
            " 센서 ": ["충격(틸트) 센서", "초음파 거리센서", "DHT11 온습도", "부저 + LCD"],
            "자동차 부품 MES에서의 의미": [
                "LOT/부품 운반·적재 중 낙하·충격 감지 — 도장된 부품이나 정밀부품은 충격으로 외관 불량이 생길 수 있음",
                "특정 구역(예: 출하 대기 랙)에 LOT가 실제로 놓여있는지 감지 — 물리적 재고 확인",
                "도료·접착제 원자재는 보관 온습도가 품질에 영향 → 보관 조건 이력 기록",
                "현장 작업자에게 즉시 경보 — 화면 안 봐도 이상 상황 인지 가능",
            ],
        }
    )

    st.markdown("#### 가장 자연스러운 스토리 — \u201c출하 전 마지막 관문\u201d 자동화")
    st.markdown(
        "지금 시스템에는 이미 **\u201cFAIL 판정 LOT는 출하 자동 차단\u201d** 기능이 있음. "
        "이 센서 조합은 그 개념을 한 단계 확장."
    )

    col_before, col_after = st.columns(2)
    with col_before:
        st.markdown("**기존**")
        st.markdown("검사자가 사람이 눈으로 보고 PASS/FAIL 입력 → 출하 시 그 결과로 차단")
    with col_after:
        st.markdown("**확장**")
        st.markdown(
            "출하 대기 구역에 이 장치를 놓고, 완제품 LOT가 거기 머무는 동안 충격이 감지되면 "
            "자동으로 \u201c재검사 필요\u201d 플래그가 붙어서 사람이 놓치더라도 센서가 잡아냄."
        )

st.markdown("---")

tab_monitor, tab_history, tab_alerts = st.tabs(["실시간 모니터링", "LOT별 이력", "최근 경보"])

with tab_monitor:
    lots = queries.monitorable_lots()
    lot_options = {"(LOT 선택 안 함 - 구역 모니터링만)": None}
    for lot in lots:
        lot_options[f"{lot['lot_no']} | {lot['item_name']} ({lot['lot_type']})"] = lot["lot_id"]

    selected_label = st.selectbox("모니터링할 LOT", list(lot_options.keys()))
    selected_lot_id = lot_options[selected_label]

    col1, col2 = st.columns(2)
    duration = col1.number_input("모니터링 시간(초)", min_value=5, max_value=120, value=20, step=5)
    start = col2.button("모니터링 시작", type="primary")

    placeholder = st.empty()
    log_placeholder = st.empty()

    if start:
        readings = []
        progress = st.progress(0)
        for i in range(int(duration)):
            reading = read_latest_reading()
            if reading is not None:
                try:
                    result = log_handling_event(
                        lot_id=selected_lot_id,
                        distance_cm=reading["distance_cm"],
                        shock_detected=reading["shock_detected"],
                        temperature=reading["temperature"],
                        humidity=reading["humidity"],
                    )
                    readings.append(reading)

                    with placeholder.container():
                        kpi_row(
                            [
                                ("거리", f"{reading['distance_cm']:.0f} cm", "kpi-blue"),
                                ("온도", f"{reading['temperature']:.1f} °C", "kpi-teal"),
                                ("습도", f"{reading['humidity']:.0f} %", "kpi-purple"),
                            ]
                        )
                        if result["alert"]:
                            alert_badge(
                                f"⚠ 경보 발생! (충격감지: {'예' if reading['shock_detected'] else '아니오'}, "
                                f"거리 {reading['distance_cm']:.0f}cm)",
                                "danger",
                            )
                        else:
                            alert_badge("정상", "ok")
                except ValueError as exc:
                    st.error(str(exc))

            progress.progress((i + 1) / duration)
            time.sleep(1)

        st.success(f"모니터링 종료. {len(readings)}건 기록됨.")
        if selected_lot_id:
            log_placeholder.dataframe(
                queries.handling_events_for_lot(selected_lot_id, limit=int(duration)),
                use_container_width=True,
                hide_index=True,
            )
    else:
        st.info("LOT을 선택하고 '모니터링 시작'을 누르면 지정한 시간 동안 센서값을 실시간으로 기록합니다.")

with tab_history:
    lots = queries.monitorable_lots()
    if not lots:
        st.info("모니터링 이력을 조회할 LOT가 없습니다.")
    else:
        lot_options2 = {f"{lot['lot_no']} | {lot['item_name']}": lot["lot_id"] for lot in lots}
        hist_label = st.selectbox("조회할 LOT", list(lot_options2.keys()), key="hist_lot_select")
        hist_lot_id = lot_options2[hist_label]

        if queries.lot_has_shock_alert(hist_lot_id):
            alert_badge("이 LOT에는 충격 감지 이력이 있습니다. 재검사를 권장합니다.", "danger")

        show_dataframe(queries.handling_events_for_lot(hist_lot_id), "이 LOT에 대한 모니터링 기록이 없습니다.")

with tab_alerts:
    alerts_df = queries.recent_handling_alerts(limit=30)
    show_dataframe(alerts_df, "최근 경보 이력이 없습니다.")

st.markdown("---")
st.caption(
    "충격이 감지된 LOT은 출하 관리 페이지에서 경고 배지로 표시됩니다. "
    "필요 시 검사 페이지에서 'SHOCK_DAMAGE(충격 손상 의심)' 사유로 재검사를 등록하세요."
)
