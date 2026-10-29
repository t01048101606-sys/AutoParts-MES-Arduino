# 1단계. PLC 제어 (OpenPLC + 가상 설비)

자동차부품 브라켓 미니 라인의 시퀀스를 OpenPLC로 구현하고, Python 가상 설비와 Modbus TCP로 연결한다.

## 폴더 구성

```
phase1/
├─ plc/bracket_line.st      OpenPLC에 올리는 ST 프로그램
├─ sim/line_sim.py          가상 설비 + AI 대역 + MES 대역 + 시나리오 검증기
├─ sim/requirements.txt     pymodbus
└─ results/                 실제 OpenPLC 런타임에서 돌린 검증 로그 3종
```

## 공정 흐름

입고 감지(10) → 프레스(20) → 검사 위치 이송(30) → AI 판정 대기(40) → 양품 이송(50) 또는 불량 배출(60) → 수량 확인(70) → 반복, 목표 수량 도달 시 작업완료(80). 비상정지, 타임아웃, 정의되지 않은 단계는 경보(99).

## Modbus 주소 계약

OpenPLC 슬레이브는 코일 n을 `%QX(n/8).(n%8)`, 홀딩 레지스터 n을 `%QWn`에 대응한다.

| 구분 | 신호 | 주소 | IEC 변수 | 쓰는 쪽 |
| --- | --- | --- | --- | --- |
| 코일 | S_IN 입고 감지 | 0 | %QX0.0 | 가상 설비 |
| 코일 | S_PRESS_DONE 프레스 완료 | 1 | %QX0.1 | 가상 설비 |
| 코일 | S_VISION_POS 검사 위치 도착 | 2 | %QX0.2 | 가상 설비 |
| 코일 | S_PASS_BIN 양품 적재함 | 3 | %QX0.3 | 가상 설비 |
| 코일 | S_NG_BIN 불량 적재함 | 4 | %QX0.4 | 가상 설비 |
| 코일 | ESTOP 비상정지 | 5 | %QX0.5 | 가상 설비 |
| 코일 | CMD_START 작업 시작 | 8 | %QX1.0 | MES |
| 코일 | CMD_RESET 경보 해제, 초기화 | 9 | %QX1.1 | MES |
| 코일 | Y_CONV 컨베이어 | 16 | %QX2.0 | PLC |
| 코일 | Y_PRESS 프레스 | 17 | %QX2.1 | PLC |
| 코일 | Y_DIVERT 불량 배출 실린더 | 18 | %QX2.2 | PLC |
| 코일 | LAMP_RUN 가동 램프 | 19 | %QX2.3 | PLC |
| 코일 | LAMP_ALARM 경보 램프 | 20 | %QX2.4 | PLC |
| 홀딩 | SP_TARGET_QTY 목표 수량 | 0 | %QW0 | MES |
| 홀딩 | VISION_RESULT 0대기 1양품 2불량 | 1 | %QW1 | AI, PLC가 소비 후 0 |
| 홀딩 | CNT_IN 입고 누적 | 8 | %QW8 | PLC |
| 홀딩 | CNT_OK 양품 누적 | 9 | %QW9 | PLC |
| 홀딩 | CNT_NG 불량 누적 | 10 | %QW10 | PLC |
| 홀딩 | LINE_STATE 0정지 1가동 2경보 3완료 | 11 | %QW11 | PLC |
| 홀딩 | STEP_NO 현재 단계 | 12 | %QW12 | PLC |

## 실행 방법 (Ubuntu 리눅스 VM 기준)

1. OpenPLC Runtime v3 설치
   ```
   git clone https://github.com/thiagoralves/OpenPLC_v3.git
   cd OpenPLC_v3
   ./install.sh linux
   ```
2. 웹 화면(기본 포트 8080)에서 `plc/bracket_line.st`를 업로드하고 컴파일한 뒤 PLC를 시작한다.
3. 설정 화면에서 Modbus 서버를 켠다. (포트 502, 메뉴 이름은 버전에 따라 다를 수 있다.)
4. 시뮬레이터 실행
   ```
   pip install -r sim/requirements.txt
   python3 sim/line_sim.py --host 127.0.0.1 --port 502 --parts 10 --target 10 --speed 0.25
   ```
5. 시나리오 옵션: `--scenario normal`(기본), `estop`, `press_stall`. 끝에 `PASS`가 나오면 통과.

비상정지나 경보 시나리오를 실행한 뒤에는 PLC가 경보 상태로 남을 수 있으므로, 다음 시험 전에 RESET(코일 9)을 보내거나 PLC를 다시 시작한다.

## 검증 결과

실제 OpenPLC 런타임을 소스에서 빌드해 시험했다. 로그는 `results/`에 있다.

| 시나리오 | 확인한 내용 | 결과 |
| --- | --- | --- |
| normal | 부품 10개 처리, PLC 카운트와 설비 정답 일치(입고 10, 양품 6, 불량 4), 오배출 0, RESET 초기화 | 통과 |
| estop | 이송 중 비상정지 시 경보 진입, 구동 출력 모두 OFF, 해제 후 RESET으로 정지 복귀 | 통과 |
| press_stall | 프레스 완료 신호가 없을 때 약 10초 후 경보 진입 | 통과 |

## 알려진 한계

- 가상 설비는 부품이 1개씩 흐르는 단순 모델이다.
- AI 판정은 불량률 난수로 대신하며 4단계에서 YOLO로 교체한다.
- MES 동작은 시뮬레이터가 대신하며 2단계에서 Spring Boot로 교체한다.
