
import time
import random
import sqlite3

from src.services import log_handling_event
from src.db import get_connection

def get_random_active_lot_id() -> int | None:
    """DB에서 무작위로 유효한 LOT ID 하나를 조회합니다."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        row = cursor.execute("SELECT lot_id FROM lot ORDER BY RANDOM() LIMIT 1").fetchone()
        conn.close()
        return row["lot_id"] if row else None
    except Exception:
        return None

def run_sensor_simulator(interval_sec: float = 2.0):
    """
    아두이노 센서를 가상화하여 주기적으로 DB에 센서 데이터를 전송하는 시뮬레이터
    """
    print("==================================================")
    print(" 센서 데이터 시뮬레이터(sender.py)가 시작되었습니다.")
    print(f"  전송 주기: {interval_sec}초 (종료하려며 Ctrl+C를 누르세요)")
    print("==================================================")

    try:
        while True:
            
            lot_id = get_random_active_lot_id()
            shock_detected = random.random() < 0.10  
            
            
            if random.random() < 0.15:
                distance_cm = round(random.uniform(1.0, 5.0), 1)
            else:
                distance_cm = round(random.uniform(5.1, 45.0), 1)

            temperature = round(random.uniform(18.0, 28.0), 1)
            humidity = round(random.uniform(30.0, 65.0), 1)

            
            result = log_handling_event(
                lot_id=lot_id,
                distance_cm=distance_cm,
                shock_detected=shock_detected,
                temperature=temperature,
                humidity=humidity
            )

            
            status_tag = "🚨 [ALERT]" if result["alert"] else "✅ [NORMAL]"
            print(f"{status_tag} Event ID: {result['handling_event_id']} | LOT: {lot_id} | "
                  f"거리: {distance_cm}cm | 충격: {shock_detected} | "
                  f"온도: {temperature}℃ | 습도: {humidity}%")

            time.sleep(interval_sec)

    except KeyboardInterrupt:
        print("\n 센서 시뮬레이터가 정상 종료되었습니다.")
    except Exception as e:
        print(f"\n 오류 발생: {e}")

if __name__ == "__main__":
    run_sensor_simulator(interval_sec=2.0)
