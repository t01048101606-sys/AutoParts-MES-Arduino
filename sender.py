import serial
import time
import random


PORT = '/dev/pts/1'
BAUDRATE = 9600

try:
    ser = serial.Serial(PORT, BAUDRATE, timeout=1)
    print(f"✅ 가상 아두이노(송신부) 연결 성공: {PORT}")
    time.sleep(2)  
except Exception as e:
    print(f"❌ 포트 연결 실패: {e}")
    print("💡 'socat -d -d pty,raw,echo=0 pty,raw,echo=0' 명령어가 실행 중인지 확인하세요.")
    exit(1)

reed_count = 100

while True:
    try:
        reed_count += 1
        dist = round(random.uniform(5.0, 30.0), 1)
        temp = round(random.uniform(20.0, 26.0), 1)
        shock = 'Y' if random.random() < 0.05 else 'N'  
        
        
        payload = f"COUNT:{reed_count},DIST:{dist},TEMP:{temp},SHOCK:{shock}\n"
        
        
        ser.write(payload.encode('utf-8'))
        print(f"📡 [가상 아두이노 송신 -> {PORT}] {payload.strip()}")
        
        time.sleep(2)
    except KeyboardInterrupt:
        print("\n송신을 중단합니다.")
        ser.close()
        break
    except Exception as e:
        print(f"전송 중 오류 발생: {e}")
        time.sleep(2)
