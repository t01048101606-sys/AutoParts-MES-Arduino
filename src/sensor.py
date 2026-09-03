import serial
import streamlit as st

DEFAULT_PORT = "/dev/ttyACM0"  # WSL: usbipd로 연결한 뒤 실제 확인된 포트명으로 교체
BAUD_RATE = 9600


@st.cache_resource
def get_serial_connection(port: str = DEFAULT_PORT, baud: int = BAUD_RATE):
    """시리얼 연결은 앱이 켜져있는 동안 한 번만 열어서 재사용한다."""
    try:
        return serial.Serial(port, baud, timeout=1)
    except serial.SerialException as exc:
        st.error(f"시리얼 포트 연결 실패: {exc}. 포트 이름과 아두이노 연결 상태를 확인하세요.")
        return None


def parse_data_line(line: str) -> dict | None:
    """"DATA,23,0,24.0,55.0" 형식의 문자열을 파싱한다. 형식이 안 맞으면 None."""
    parts = line.strip().split(",")
    if len(parts) != 5 or parts[0] != "DATA":
        return None
    try:
        return {
            "distance_cm": float(parts[1]),
            "shock_detected": parts[2] == "1",
            "temperature": float(parts[3]),
            "humidity": float(parts[4]),
        }
    except ValueError:
        return None


def read_latest_reading(port: str = DEFAULT_PORT, baud: int = BAUD_RATE) -> dict | None:
    """버퍼에 쌓인 라인 중 가장 최근 DATA 라인 1개를 파싱해서 반환한다."""
    conn = get_serial_connection(port, baud)
    if conn is None:
        return None

    latest = None
    while conn.in_waiting:
        try:
            line = conn.readline().decode("utf-8").strip()
        except UnicodeDecodeError:
            continue
        parsed = parse_data_line(line)
        if parsed is not None:
            latest = parsed
    return latest



COUNTER_PORT = DEFAULT_PORT  


def parse_count_line(line: str) -> int | None:
    parts = line.strip().split(",")
    if len(parts) != 2 or parts[0] != "COUNT":
        return None
    try:
        return int(parts[1])
    except ValueError:
        return None


def read_latest_count(port: str = COUNTER_PORT, baud: int = BAUD_RATE) -> int | None:
    
    conn = get_serial_connection(port, baud)
    if conn is None:
        return None

    latest = None
    while conn.in_waiting:
        try:
            line = conn.readline().decode("utf-8").strip()
        except UnicodeDecodeError:
            continue
        parsed = parse_count_line(line)
        if parsed is not None:
            latest = parsed
    return latest


def reset_counter(port: str = COUNTER_PORT, baud: int = BAUD_RATE) -> None:
    """아두이노에 RESET 명령을 보내 카운터를 0으로 초기화한다."""
    conn = get_serial_connection(port, baud)
    if conn is None:
        return
    conn.write(b"RESET\n")
