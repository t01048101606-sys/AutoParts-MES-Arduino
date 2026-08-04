from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import sqlite3

from src.auth import hash_password, verify_password
from src.db import get_connection
from src.queries import (
    item_code_exists,
    item_by_id,
    process_code_exists,
    equipment_code_exists,
    equipment_by_id,
    user_id_exists,
    user_by_id,
)


# ---------------------------------------------------------
# 품목 등록/수정 (+ 스펙)
# ---------------------------------------------------------

@dataclass
class ItemRegistration:
    item_code: str
    item_name: str
    item_type: str
    unit: str
    drawing_no: str | None = None
    drawing_rev: str | None = None
    material_spec: str | None = None
    tolerance_note: str | None = None


def validate_item_registration(data: ItemRegistration) -> list[str]:
    errors: list[str] = []

    if not data.item_code.strip():
        errors.append("품목 코드를 입력하세요.")
    if not data.item_name.strip():
        errors.append("품목명을 입력하세요.")
    if not data.unit.strip():
        errors.append("단위를 입력하세요.")
    if data.item_type not in ("PRODUCT", "SEMI_PRODUCT", "MATERIAL"):
        errors.append("품목 유형이 올바르지 않습니다.")
    if data.item_code.strip() and item_code_exists(data.item_code.strip()):
        errors.append("이미 존재하는 품목 코드입니다.")

    return errors


def register_item(data: ItemRegistration) -> dict:
    errors = validate_item_registration(data)
    if errors:
        raise ValueError("\n".join(errors))

    connection = get_connection()
    try:
        connection.execute("BEGIN IMMEDIATE")
        cursor = connection.cursor()

        existing = cursor.execute(
            "SELECT item_id FROM item WHERE item_code = ?", (data.item_code.strip(),)
        ).fetchone()
        if existing is not None:
            raise ValueError(
                "이미 존재하는 품목 코드입니다. (다른 작업에서 먼저 등록되었을 수 있습니다.)"
            )

        cursor.execute(
            """
            INSERT INTO item (item_code, item_name, item_type, unit, is_active)
            VALUES (?, ?, ?, ?, 'Y')
            """,
            (data.item_code.strip(), data.item_name.strip(), data.item_type, data.unit.strip()),
        )
        item_id = cursor.lastrowid

        # 스펙 정보 중 하나라도 입력되어 있으면 item_spec도 같이 생성
        if any([data.drawing_no, data.drawing_rev, data.material_spec, data.tolerance_note]):
            cursor.execute(
                """
                INSERT INTO item_spec (item_id, drawing_no, drawing_rev, material_spec, tolerance_note)
                VALUES (?, ?, ?, ?, ?)
                """,
                (item_id, data.drawing_no, data.drawing_rev, data.material_spec, data.tolerance_note),
            )

        connection.commit()
        return {
            "item_id": item_id,
            "item_code": data.item_code.strip(),
            "item_name": data.item_name.strip(),
        }
    except sqlite3.IntegrityError as exc:
        connection.rollback()
        raise ValueError("데이터베이스 제약조건을 만족하지 못해 저장하지 못했습니다.") from exc
    except sqlite3.OperationalError as exc:
        connection.rollback()
        raise ValueError("다른 작업이 진행 중입니다. 잠시 후 다시 시도해주세요.") from exc
    except ValueError:
        connection.rollback()
        raise
    finally:
        connection.close()


@dataclass
class ItemUpdate:
    item_id: int
    item_name: str
    unit: str
    is_active: str
    drawing_no: str | None = None
    drawing_rev: str | None = None
    material_spec: str | None = None
    tolerance_note: str | None = None


def validate_item_update(data: ItemUpdate) -> list[str]:
    errors: list[str] = []

    if not data.item_name.strip():
        errors.append("품목명을 입력하세요.")
    if not data.unit.strip():
        errors.append("단위를 입력하세요.")
    if data.is_active not in ("Y", "N"):
        errors.append("사용여부 값이 올바르지 않습니다.")
    if item_by_id(data.item_id) is None:
        errors.append("존재하지 않는 품목입니다.")

    return errors


def update_item(data: ItemUpdate) -> dict:
    errors = validate_item_update(data)
    if errors:
        raise ValueError("\n".join(errors))

    connection = get_connection()
    try:
        connection.execute("BEGIN IMMEDIATE")
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE item
            SET item_name = ?, unit = ?, is_active = ?
            WHERE item_id = ?
            """,
            (data.item_name.strip(), data.unit.strip(), data.is_active, data.item_id),
        )

        existing_spec = cursor.execute(
            "SELECT item_spec_id FROM item_spec WHERE item_id = ?", (data.item_id,)
        ).fetchone()

        if existing_spec is not None:
            cursor.execute(
                """
                UPDATE item_spec
                SET drawing_no = ?, drawing_rev = ?, material_spec = ?, tolerance_note = ?
                WHERE item_id = ?
                """,
                (data.drawing_no, data.drawing_rev, data.material_spec, data.tolerance_note, data.item_id),
            )
        elif any([data.drawing_no, data.drawing_rev, data.material_spec, data.tolerance_note]):
            cursor.execute(
                """
                INSERT INTO item_spec (item_id, drawing_no, drawing_rev, material_spec, tolerance_note)
                VALUES (?, ?, ?, ?, ?)
                """,
                (data.item_id, data.drawing_no, data.drawing_rev, data.material_spec, data.tolerance_note),
            )

        connection.commit()
        return {
            "item_id": data.item_id,
            "item_name": data.item_name.strip(),
            "is_active": data.is_active,
        }
    except sqlite3.IntegrityError as exc:
        connection.rollback()
        raise ValueError("데이터베이스 제약조건을 만족하지 못해 저장하지 못했습니다.") from exc
    except sqlite3.OperationalError as exc:
        connection.rollback()
        raise ValueError("다른 작업이 진행 중입니다. 잠시 후 다시 시도해주세요.") from exc
    except ValueError:
        connection.rollback()
        raise
    finally:
        connection.close()


# ---------------------------------------------------------
# 거래처 등록/수정
# ---------------------------------------------------------

@dataclass
class PartnerRegistration:
    partner_name: str
    partner_type: str
    contact: str | None = None


def validate_partner_registration(data: PartnerRegistration) -> list[str]:
    errors: list[str] = []

    if not data.partner_name.strip():
        errors.append("거래처명을 입력하세요.")
    if data.partner_type not in ("SUPPLIER", "CUSTOMER"):
        errors.append("거래처 유형이 올바르지 않습니다.")

    return errors


def register_partner(data: PartnerRegistration) -> dict:
    errors = validate_partner_registration(data)
    if errors:
        raise ValueError("\n".join(errors))

    connection = get_connection()
    try:
        connection.execute("BEGIN IMMEDIATE")
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO partner (partner_name, partner_type, contact)
            VALUES (?, ?, ?)
            """,
            (data.partner_name.strip(), data.partner_type, data.contact),
        )
        partner_id = cursor.lastrowid

        connection.commit()
        return {"partner_id": partner_id, "partner_name": data.partner_name.strip()}
    except sqlite3.IntegrityError as exc:
        connection.rollback()
        raise ValueError("데이터베이스 제약조건을 만족하지 못해 저장하지 못했습니다.") from exc
    except sqlite3.OperationalError as exc:
        connection.rollback()
        raise ValueError("다른 작업이 진행 중입니다. 잠시 후 다시 시도해주세요.") from exc
    finally:
        connection.close()


@dataclass
class PartnerUpdate:
    partner_id: int
    partner_name: str
    contact: str | None = None


def validate_partner_update(data: PartnerUpdate) -> list[str]:
    errors: list[str] = []
    if not data.partner_name.strip():
        errors.append("거래처명을 입력하세요.")
    return errors


def update_partner(data: PartnerUpdate) -> dict:
    errors = validate_partner_update(data)
    if errors:
        raise ValueError("\n".join(errors))

    connection = get_connection()
    try:
        connection.execute("BEGIN IMMEDIATE")
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE partner SET partner_name = ?, contact = ? WHERE partner_id = ?",
            (data.partner_name.strip(), data.contact, data.partner_id),
        )
        connection.commit()
        return {"partner_id": data.partner_id, "partner_name": data.partner_name.strip()}
    except sqlite3.OperationalError as exc:
        connection.rollback()
        raise ValueError("다른 작업이 진행 중입니다. 잠시 후 다시 시도해주세요.") from exc
    finally:
        connection.close()


# ---------------------------------------------------------
# 공정 종류 등록
# ---------------------------------------------------------

@dataclass
class ProcessRegistration:
    process_code: str
    process_name: str


def validate_process_registration(data: ProcessRegistration) -> list[str]:
    errors: list[str] = []

    if not data.process_code.strip():
        errors.append("공정 코드를 입력하세요.")
    if not data.process_name.strip():
        errors.append("공정명을 입력하세요.")
    if data.process_code.strip() and process_code_exists(data.process_code.strip()):
        errors.append("이미 존재하는 공정 코드입니다.")

    return errors


def register_process(data: ProcessRegistration) -> dict:
    errors = validate_process_registration(data)
    if errors:
        raise ValueError("\n".join(errors))

    connection = get_connection()
    try:
        connection.execute("BEGIN IMMEDIATE")
        cursor = connection.cursor()

        existing = cursor.execute(
            "SELECT process_code FROM process_master WHERE process_code = ?",
            (data.process_code.strip(),),
        ).fetchone()
        if existing is not None:
            raise ValueError("이미 존재하는 공정 코드입니다.")

        cursor.execute(
            "INSERT INTO process_master (process_code, process_name) VALUES (?, ?)",
            (data.process_code.strip().upper(), data.process_name.strip()),
        )

        connection.commit()
        return {"process_code": data.process_code.strip().upper(), "process_name": data.process_name.strip()}
    except sqlite3.IntegrityError as exc:
        connection.rollback()
        raise ValueError("데이터베이스 제약조건을 만족하지 못해 저장하지 못했습니다.") from exc
    except sqlite3.OperationalError as exc:
        connection.rollback()
        raise ValueError("다른 작업이 진행 중입니다. 잠시 후 다시 시도해주세요.") from exc
    except ValueError:
        connection.rollback()
        raise
    finally:
        connection.close()


# ---------------------------------------------------------
# 설비 등록/수정
# ---------------------------------------------------------

@dataclass
class EquipmentRegistration:
    equipment_code: str
    equipment_name: str
    process_code: str


def validate_equipment_registration(data: EquipmentRegistration) -> list[str]:
    errors: list[str] = []

    if not data.equipment_code.strip():
        errors.append("설비 코드를 입력하세요.")
    if not data.equipment_name.strip():
        errors.append("설비명을 입력하세요.")
    if not data.process_code:
        errors.append("공정을 선택하세요.")
    if data.equipment_code.strip() and equipment_code_exists(data.equipment_code.strip()):
        errors.append("이미 존재하는 설비 코드입니다.")

    return errors


def register_equipment(data: EquipmentRegistration) -> dict:
    errors = validate_equipment_registration(data)
    if errors:
        raise ValueError("\n".join(errors))

    connection = get_connection()
    try:
        connection.execute("BEGIN IMMEDIATE")
        cursor = connection.cursor()

        existing = cursor.execute(
            "SELECT equipment_id FROM equipment WHERE equipment_code = ?",
            (data.equipment_code.strip(),),
        ).fetchone()
        if existing is not None:
            raise ValueError("이미 존재하는 설비 코드입니다.")

        cursor.execute(
            """
            INSERT INTO equipment (equipment_code, equipment_name, process_code, is_active)
            VALUES (?, ?, ?, 'Y')
            """,
            (data.equipment_code.strip(), data.equipment_name.strip(), data.process_code),
        )
        equipment_id = cursor.lastrowid

        connection.commit()
        return {"equipment_id": equipment_id, "equipment_code": data.equipment_code.strip()}
    except sqlite3.IntegrityError as exc:
        connection.rollback()
        raise ValueError("데이터베이스 제약조건을 만족하지 못해 저장하지 못했습니다.") from exc
    except sqlite3.OperationalError as exc:
        connection.rollback()
        raise ValueError("다른 작업이 진행 중입니다. 잠시 후 다시 시도해주세요.") from exc
    except ValueError:
        connection.rollback()
        raise
    finally:
        connection.close()


def set_equipment_active(equipment_id: int, is_active: str) -> dict:
    if is_active not in ("Y", "N"):
        raise ValueError("사용여부 값이 올바르지 않습니다.")
    if equipment_by_id(equipment_id) is None:
        raise ValueError("존재하지 않는 설비입니다.")

    connection = get_connection()
    try:
        connection.execute("BEGIN IMMEDIATE")
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE equipment SET is_active = ? WHERE equipment_id = ?", (is_active, equipment_id)
        )
        connection.commit()
        return {"equipment_id": equipment_id, "is_active": is_active}
    except sqlite3.OperationalError as exc:
        connection.rollback()
        raise ValueError("다른 작업이 진행 중입니다. 잠시 후 다시 시도해주세요.") from exc
    finally:
        connection.close()


# ---------------------------------------------------------
# 사용자 계정 등록/인증
# ---------------------------------------------------------

@dataclass
class UserRegistration:
    user_id: str
    user_name: str
    password: str
    role: str


def validate_user_registration(data: UserRegistration) -> list[str]:
    errors: list[str] = []

    if not data.user_id.strip():
        errors.append("아이디를 입력하세요.")
    if not data.user_name.strip():
        errors.append("이름을 입력하세요.")
    if len(data.password) < 4:
        errors.append("비밀번호는 4자 이상이어야 합니다.")
    if data.role not in ("ADMIN", "OPERATOR", "INSPECTOR"):
        errors.append("권한 값이 올바르지 않습니다.")
    if data.user_id.strip() and user_id_exists(data.user_id.strip()):
        errors.append("이미 존재하는 아이디입니다.")

    return errors


def register_user(data: UserRegistration) -> dict:
    errors = validate_user_registration(data)
    if errors:
        raise ValueError("\n".join(errors))

    connection = get_connection()
    try:
        connection.execute("BEGIN IMMEDIATE")
        cursor = connection.cursor()

        existing = cursor.execute(
            "SELECT user_id FROM user WHERE user_id = ?", (data.user_id.strip(),)
        ).fetchone()
        if existing is not None:
            raise ValueError("이미 존재하는 아이디입니다.")

        cursor.execute(
            """
            INSERT INTO user (user_id, user_name, password_hash, role, is_active)
            VALUES (?, ?, ?, ?, 'Y')
            """,
            (
                data.user_id.strip(),
                data.user_name.strip(),
                hash_password(data.password),
                data.role,
            ),
        )

        connection.commit()
        return {"user_id": data.user_id.strip(), "user_name": data.user_name.strip()}
    except sqlite3.IntegrityError as exc:
        connection.rollback()
        raise ValueError("데이터베이스 제약조건을 만족하지 못해 저장하지 못했습니다.") from exc
    except sqlite3.OperationalError as exc:
        connection.rollback()
        raise ValueError("다른 작업이 진행 중입니다. 잠시 후 다시 시도해주세요.") from exc
    except ValueError:
        connection.rollback()
        raise
    finally:
        connection.close()


def set_user_active(user_id: str, is_active: str) -> dict:
    if is_active not in ("Y", "N"):
        raise ValueError("사용여부 값이 올바르지 않습니다.")

    connection = get_connection()
    try:
        connection.execute("BEGIN IMMEDIATE")
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE user SET is_active = ? WHERE user_id = ?", (is_active, user_id)
        )
        connection.commit()
        return {"user_id": user_id, "is_active": is_active}
    except sqlite3.OperationalError as exc:
        connection.rollback()
        raise ValueError("다른 작업이 진행 중입니다. 잠시 후 다시 시도해주세요.") from exc
    finally:
        connection.close()


def authenticate_user(user_id: str, password: str) -> dict | None:
    """아이디/비밀번호가 맞고 활성 상태인 사용자면 정보를 반환하고, 아니면 None."""
    user = user_by_id(user_id.strip())
    if user is None:
        return None
    if user["is_active"] != "Y":
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    return {"user_id": user["user_id"], "user_name": user["user_name"], "role": user["role"]}


# ---------------------------------------------------------
# 라우팅 / 라우팅 단계 / 단계별 BOM
# ---------------------------------------------------------

def get_or_create_routing(product_item_id: int, routing_name: str) -> dict:
    """제품에 라우팅이 없으면 새로 만들고, 있으면 이름만 갱신 후 반환한다.
    (제품 1개당 라우팅은 1개만 허용)"""
    if not routing_name.strip():
        raise ValueError("라우팅 이름을 입력하세요.")

    connection = get_connection()
    try:
        connection.execute("BEGIN IMMEDIATE")
        cursor = connection.cursor()

        existing = cursor.execute(
            "SELECT routing_id FROM routing WHERE product_item_id = ?", (product_item_id,)
        ).fetchone()

        if existing is not None:
            cursor.execute(
                "UPDATE routing SET routing_name = ? WHERE routing_id = ?",
                (routing_name.strip(), existing["routing_id"]),
            )
            routing_id = existing["routing_id"]
        else:
            cursor.execute(
                """
                INSERT INTO routing (product_item_id, routing_name, is_active)
                VALUES (?, ?, 'Y')
                """,
                (product_item_id, routing_name.strip()),
            )
            routing_id = cursor.lastrowid

        connection.commit()
        return {"routing_id": routing_id, "routing_name": routing_name.strip()}
    except sqlite3.IntegrityError as exc:
        connection.rollback()
        raise ValueError("데이터베이스 제약조건을 만족하지 못해 저장하지 못했습니다.") from exc
    except sqlite3.OperationalError as exc:
        connection.rollback()
        raise ValueError("다른 작업이 진행 중입니다. 잠시 후 다시 시도해주세요.") from exc
    finally:
        connection.close()


@dataclass
class RoutingStepRegistration:
    routing_id: int
    process_code: str
    output_item_id: int


def validate_routing_step(data: RoutingStepRegistration) -> list[str]:
    errors: list[str] = []
    if not data.process_code:
        errors.append("공정을 선택하세요.")
    if not data.output_item_id:
        errors.append("이 단계의 산출 품목을 선택하세요.")
    return errors


def add_routing_step(data: RoutingStepRegistration) -> dict:
    errors = validate_routing_step(data)
    if errors:
        raise ValueError("\n".join(errors))

    connection = get_connection()
    try:
        connection.execute("BEGIN IMMEDIATE")
        cursor = connection.cursor()

        next_no_row = cursor.execute(
            "SELECT COALESCE(MAX(step_no), 0) + 1 AS next_no FROM routing_step WHERE routing_id = ?",
            (data.routing_id,),
        ).fetchone()
        step_no = int(next_no_row["next_no"])

        cursor.execute(
            """
            INSERT INTO routing_step (routing_id, step_no, process_code, output_item_id)
            VALUES (?, ?, ?, ?)
            """,
            (data.routing_id, step_no, data.process_code, data.output_item_id),
        )
        routing_step_id = cursor.lastrowid

        connection.commit()
        return {"routing_step_id": routing_step_id, "step_no": step_no}
    except sqlite3.IntegrityError as exc:
        connection.rollback()
        raise ValueError("데이터베이스 제약조건을 만족하지 못해 저장하지 못했습니다.") from exc
    except sqlite3.OperationalError as exc:
        connection.rollback()
        raise ValueError("다른 작업이 진행 중입니다. 잠시 후 다시 시도해주세요.") from exc
    finally:
        connection.close()


def remove_routing_step(routing_step_id: int) -> dict:
    """이 단계에 연결된 BOM이나 실제 공정 실행 이력이 있으면 삭제를 막는다."""
    from src.queries import routing_step_bom_count, routing_step_operation_count

    if routing_step_bom_count(routing_step_id) > 0:
        raise ValueError("이 단계에 등록된 BOM이 있어 삭제할 수 없습니다. BOM을 먼저 삭제하세요.")
    if routing_step_operation_count(routing_step_id) > 0:
        raise ValueError("이 단계는 이미 실제 공정 실행 이력이 있어 삭제할 수 없습니다.")

    connection = get_connection()
    try:
        connection.execute("BEGIN IMMEDIATE")
        cursor = connection.cursor()
        cursor.execute("DELETE FROM routing_step WHERE routing_step_id = ?", (routing_step_id,))
        connection.commit()
        return {"routing_step_id": routing_step_id, "deleted": True}
    except sqlite3.OperationalError as exc:
        connection.rollback()
        raise ValueError("다른 작업이 진행 중입니다. 잠시 후 다시 시도해주세요.") from exc
    finally:
        connection.close()


@dataclass
class BomLineRegistration:
    routing_step_id: int
    material_item_id: int
    qty_per_unit: float


def validate_bom_line(data: BomLineRegistration) -> list[str]:
    from src.queries import bom_line_exists

    errors: list[str] = []
    if data.qty_per_unit <= 0:
        errors.append("단위당 소요량은 0보다 커야 합니다.")
    if bom_line_exists(data.routing_step_id, data.material_item_id):
        errors.append("이미 이 단계에 등록된 원자재입니다.")
    return errors


def add_bom_line(data: BomLineRegistration) -> dict:
    errors = validate_bom_line(data)
    if errors:
        raise ValueError("\n".join(errors))

    connection = get_connection()
    try:
        connection.execute("BEGIN IMMEDIATE")
        cursor = connection.cursor()

        existing = cursor.execute(
            "SELECT bom_id FROM bom WHERE routing_step_id = ? AND material_item_id = ?",
            (data.routing_step_id, data.material_item_id),
        ).fetchone()
        if existing is not None:
            raise ValueError("이미 이 단계에 등록된 원자재입니다.")

        cursor.execute(
            """
            INSERT INTO bom (routing_step_id, material_item_id, qty_per_unit)
            VALUES (?, ?, ?)
            """,
            (data.routing_step_id, data.material_item_id, data.qty_per_unit),
        )
        bom_id = cursor.lastrowid

        connection.commit()
        return {"bom_id": bom_id}
    except sqlite3.IntegrityError as exc:
        connection.rollback()
        raise ValueError("데이터베이스 제약조건을 만족하지 못해 저장하지 못했습니다.") from exc
    except sqlite3.OperationalError as exc:
        connection.rollback()
        raise ValueError("다른 작업이 진행 중입니다. 잠시 후 다시 시도해주세요.") from exc
    finally:
        connection.close()


def remove_bom_line(bom_id: int) -> dict:
    connection = get_connection()
    try:
        connection.execute("BEGIN IMMEDIATE")
        cursor = connection.cursor()
        cursor.execute("DELETE FROM bom WHERE bom_id = ?", (bom_id,))
        connection.commit()
        return {"bom_id": bom_id, "deleted": True}
    except sqlite3.OperationalError as exc:
        connection.rollback()
        raise ValueError("다른 작업이 진행 중입니다. 잠시 후 다시 시도해주세요.") from exc
    finally:
        connection.close()


# ---------------------------------------------------------
# 원자재 입고 등록
# ---------------------------------------------------------

@dataclass
class ReceiptRegistration:
    material_item_id: int
    lot_no: str
    received_date: date
    qty: float
    partner_id: int | None = None
    expire_date: date | None = None


def validate_receipt(data: ReceiptRegistration) -> list[str]:
    from src.queries import lot_no_exists

    errors: list[str] = []
    if not data.lot_no.strip():
        errors.append("입고 LOT 번호를 입력하세요.")
    if data.qty <= 0:
        errors.append("입고수량은 0보다 커야 합니다.")
    if data.lot_no.strip() and lot_no_exists(data.lot_no.strip()):
        errors.append("이미 존재하는 LOT 번호입니다.")
    return errors


def register_receipt(data: ReceiptRegistration) -> dict:
    errors = validate_receipt(data)
    if errors:
        raise ValueError("\n".join(errors))

    connection = get_connection()
    try:
        connection.execute("BEGIN IMMEDIATE")
        cursor = connection.cursor()

        existing = cursor.execute(
            "SELECT lot_id FROM lot WHERE lot_no = ?", (data.lot_no.strip(),)
        ).fetchone()
        if existing is not None:
            raise ValueError(
                "이미 존재하는 LOT 번호입니다. (다른 작업에서 먼저 등록되었을 수 있습니다.)"
            )

        cursor.execute(
            """
            INSERT INTO lot (lot_no, item_id, lot_type, qty, received_date, produced_date, expire_date, partner_id)
            VALUES (?, ?, 'RECEIPT', ?, ?, NULL, ?, ?)
            """,
            (
                data.lot_no.strip(),
                data.material_item_id,
                data.qty,
                str(data.received_date),
                str(data.expire_date) if data.expire_date else None,
                data.partner_id,
            ),
        )
        lot_id = cursor.lastrowid

        connection.commit()
        return {"lot_id": lot_id, "lot_no": data.lot_no.strip(), "qty": data.qty}
    except sqlite3.IntegrityError as exc:
        connection.rollback()
        raise ValueError("데이터베이스 제약조건을 만족하지 못해 저장하지 못했습니다.") from exc
    except sqlite3.OperationalError as exc:
        connection.rollback()
        raise ValueError("다른 작업이 진행 중입니다. 잠시 후 다시 시도해주세요.") from exc
    except ValueError:
        connection.rollback()
        raise
    finally:
        connection.close()


# ---------------------------------------------------------
# 작업지시 등록/취소
# ---------------------------------------------------------

@dataclass
class WorkOrderRegistration:
    work_order_no: str
    product_item_id: int
    routing_id: int
    planned_qty: float
    plan_date: date


def validate_work_order(data: WorkOrderRegistration) -> list[str]:
    from src.queries import work_order_no_exists

    errors: list[str] = []
    if not data.work_order_no.strip():
        errors.append("작업지시번호를 입력하세요.")
    if data.planned_qty <= 0:
        errors.append("계획수량은 0보다 커야 합니다.")
    if data.work_order_no.strip() and work_order_no_exists(data.work_order_no.strip()):
        errors.append("이미 존재하는 작업지시번호입니다.")
    return errors


def register_work_order(data: WorkOrderRegistration) -> dict:
    errors = validate_work_order(data)
    if errors:
        raise ValueError("\n".join(errors))

    connection = get_connection()
    try:
        connection.execute("BEGIN IMMEDIATE")
        cursor = connection.cursor()

        existing = cursor.execute(
            "SELECT work_order_id FROM work_order WHERE work_order_no = ?",
            (data.work_order_no.strip(),),
        ).fetchone()
        if existing is not None:
            raise ValueError("이미 존재하는 작업지시번호입니다.")

        cursor.execute(
            """
            INSERT INTO work_order (work_order_no, product_item_id, routing_id, planned_qty, plan_date, status)
            VALUES (?, ?, ?, ?, ?, 'PLANNED')
            """,
            (
                data.work_order_no.strip(),
                data.product_item_id,
                data.routing_id,
                data.planned_qty,
                str(data.plan_date),
            ),
        )
        work_order_id = cursor.lastrowid

        connection.commit()
        return {"work_order_id": work_order_id, "work_order_no": data.work_order_no.strip()}
    except sqlite3.IntegrityError as exc:
        connection.rollback()
        raise ValueError("데이터베이스 제약조건을 만족하지 못해 저장하지 못했습니다.") from exc
    except sqlite3.OperationalError as exc:
        connection.rollback()
        raise ValueError("다른 작업이 진행 중입니다. 잠시 후 다시 시도해주세요.") from exc
    except ValueError:
        connection.rollback()
        raise
    finally:
        connection.close()


def cancel_work_order(work_order_id: int) -> dict:
    from src.queries import work_order_by_id, work_order_operation_count

    wo = work_order_by_id(work_order_id)
    if wo is None:
        raise ValueError("존재하지 않는 작업지시입니다.")
    if wo["status"] not in ("PLANNED", "IN_PROGRESS"):
        raise ValueError("PLANNED 또는 IN_PROGRESS 상태인 작업지시만 취소할 수 있습니다.")
    if work_order_operation_count(work_order_id) > 0:
        raise ValueError("이미 공정 실행 이력이 있는 작업지시는 취소할 수 없습니다.")

    connection = get_connection()
    try:
        connection.execute("BEGIN IMMEDIATE")
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE work_order SET status = 'CANCELED' WHERE work_order_id = ? AND status IN ('PLANNED', 'IN_PROGRESS')",
            (work_order_id,),
        )
        if cursor.rowcount == 0:
            raise ValueError("이미 처리된 작업지시입니다. (다른 작업에서 먼저 변경되었을 수 있습니다.)")
        connection.commit()
        return {"work_order_id": work_order_id, "status": "CANCELED"}
    except sqlite3.OperationalError as exc:
        connection.rollback()
        raise ValueError("다른 작업이 진행 중입니다. 잠시 후 다시 시도해주세요.") from exc
    except ValueError:
        connection.rollback()
        raise
    finally:
        connection.close()


# ---------------------------------------------------------
# 공정 실행 (operation)
# ---------------------------------------------------------

@dataclass
class OperationRegistration:
    work_order_id: int
    routing_step_id: int
    equipment_id: int | None
    operation_date: date
    qty: float
    material_rows: list[dict]  # [{"material_item_id": int, "material_lot_id": int, "qty": float}, ...]


def validate_operation(data: OperationRegistration) -> list[str]:
    from src.queries import (
        work_order_by_id,
        next_routing_step_for_work_order,
        lots_with_balance_for_item,
        bom_for_routing_step,
    )

    errors: list[str] = []

    wo = work_order_by_id(data.work_order_id)
    if wo is None:
        errors.append("존재하지 않는 작업지시입니다.")
        return errors
    if wo["status"] not in ("PLANNED", "IN_PROGRESS"):
        errors.append("PLANNED 또는 IN_PROGRESS 상태의 작업지시만 공정을 실행할 수 있습니다.")

    next_step = next_routing_step_for_work_order(data.work_order_id)
    if next_step is None:
        errors.append("이 작업지시의 모든 공정이 이미 완료되었습니다.")
    elif next_step["routing_step_id"] != data.routing_step_id:
        errors.append(
            f"공정 순서를 건너뛸 수 없습니다. 다음에 실행해야 할 단계는 "
            f"{next_step['step_no']}단계({next_step['process_name']})입니다."
        )

    if data.qty <= 0:
        errors.append("생산수량은 0보다 커야 합니다.")

    if not data.material_rows:
        # BOM이 없는 단계(예: 단순 검사공정)는 원자재 투입 없이도 진행 가능하게 허용
        pass
    else:
        material_lot_ids = [row["material_lot_id"] for row in data.material_rows]
        if len(material_lot_ids) != len(set(material_lot_ids)):
            errors.append("동일한 LOT를 중복 선택할 수 없습니다.")

        bom_df = bom_for_routing_step(data.routing_step_id)
        bom_material_ids = set(bom_df["material_item_id"]) if not bom_df.empty else set()

        for row in data.material_rows:
            if row["qty"] <= 0:
                errors.append("투입수량은 모두 0보다 커야 합니다.")
                continue
            if row["material_item_id"] not in bom_material_ids:
                errors.append("이 단계의 BOM에 등록되지 않은 원자재/반제품은 투입할 수 없습니다.")
                continue

            lot_type = "RECEIPT"
            balance_rows = lots_with_balance_for_item(row["material_item_id"], "RECEIPT")
            balance_rows += lots_with_balance_for_item(row["material_item_id"], "WIP")
            balance_by_lot = {r["lot_id"]: r["remaining_qty"] for r in balance_rows}
            remaining = balance_by_lot.get(row["material_lot_id"])
            if remaining is None:
                errors.append(f"LOT ID {row['material_lot_id']}는 더 이상 사용할 수 없습니다.")
            elif row["qty"] > remaining:
                errors.append(
                    f"LOT ID {row['material_lot_id']}의 잔량({remaining:,.0f})보다 "
                    f"투입수량({row['qty']:,.0f})이 많습니다."
                )

    return errors


def register_operation(data: OperationRegistration) -> dict:
    from src.queries import routing_step_by_id, routing_step_max_no

    errors = validate_operation(data)
    if errors:
        raise ValueError("\n".join(errors))

    step = routing_step_by_id(data.routing_step_id)
    is_last_step = step["step_no"] == routing_step_max_no(step["routing_id"])
    output_lot_type = "FINISHED" if is_last_step else "WIP"

    connection = get_connection()
    try:
        connection.execute("BEGIN IMMEDIATE")
        cursor = connection.cursor()

        # 트랜잭션 안에서 잔량을 한 번 더 확인
        for row in data.material_rows:
            remaining = cursor.execute(
                """
                SELECT l.qty - COALESCE(SUM(om.qty), 0)
                FROM lot AS l
                LEFT JOIN operation_material AS om ON om.material_lot_id = l.lot_id
                WHERE l.lot_id = ?
                GROUP BY l.lot_id, l.qty
                """,
                (row["material_lot_id"],),
            ).fetchone()
            if remaining is None or row["qty"] > remaining[0]:
                raise ValueError(
                    f"LOT ID {row['material_lot_id']}의 재고가 부족합니다. "
                    "다른 작업에서 먼저 사용되었을 수 있습니다."
                )

        # 이 작업지시에서 같은 단계가 먼저 완료되지 않았는지 재확인 (동시 실행 경쟁 방지)
        already_done = cursor.execute(
            "SELECT operation_id FROM operation WHERE work_order_id = ? AND routing_step_id = ? AND status = 'COMPLETED'",
            (data.work_order_id, data.routing_step_id),
        ).fetchone()
        if already_done is not None:
            raise ValueError("이 단계는 이미 다른 작업에서 먼저 완료되었습니다.")

        # 새 출력 LOT 생성
        next_lot_id = cursor.execute(
            "SELECT COALESCE(MAX(lot_id), 0) + 1 AS next_id FROM lot"
        ).fetchone()["next_id"]
        prefix = "FG" if is_last_step else "WIP"
        output_lot_no = f"{prefix}-{str(data.operation_date)}-{next_lot_id:05d}"

        cursor.execute(
            """
            INSERT INTO lot (lot_no, item_id, lot_type, qty, received_date, produced_date, expire_date, partner_id)
            VALUES (?, ?, ?, ?, NULL, ?, NULL, NULL)
            """,
            (output_lot_no, step["output_item_id"], output_lot_type, data.qty, str(data.operation_date)),
        )
        output_lot_id = cursor.lastrowid

        cursor.execute(
            """
            INSERT INTO operation
                (work_order_id, routing_step_id, equipment_id, operation_date, qty, output_lot_id, status)
            VALUES (?, ?, ?, ?, ?, ?, 'COMPLETED')
            """,
            (
                data.work_order_id,
                data.routing_step_id,
                data.equipment_id,
                str(data.operation_date),
                data.qty,
                output_lot_id,
            ),
        )
        operation_id = cursor.lastrowid

        for row in data.material_rows:
            cursor.execute(
                """
                INSERT INTO operation_material (operation_id, material_item_id, material_lot_id, qty)
                VALUES (?, ?, ?, ?)
                """,
                (operation_id, row["material_item_id"], row["material_lot_id"], row["qty"]),
            )

        # 작업지시 상태 갱신: 첫 공정이면 IN_PROGRESS, 마지막 공정이면 COMPLETED
        current_status = cursor.execute(
            "SELECT status FROM work_order WHERE work_order_id = ?", (data.work_order_id,)
        ).fetchone()["status"]

        new_status = current_status
        if is_last_step:
            new_status = "COMPLETED"
        elif current_status == "PLANNED":
            new_status = "IN_PROGRESS"

        if new_status != current_status:
            cursor.execute(
                "UPDATE work_order SET status = ? WHERE work_order_id = ?",
                (new_status, data.work_order_id),
            )

        connection.commit()
        return {
            "operation_id": operation_id,
            "output_lot_id": output_lot_id,
            "output_lot_no": output_lot_no,
            "output_lot_type": output_lot_type,
            "work_order_status": new_status,
        }
    except sqlite3.IntegrityError as exc:
        connection.rollback()
        raise ValueError("데이터베이스 제약조건을 만족하지 못해 저장하지 못했습니다.") from exc
    except sqlite3.OperationalError as exc:
        connection.rollback()
        raise ValueError("다른 작업이 진행 중입니다. 잠시 후 다시 시도해주세요.") from exc
    except ValueError:
        connection.rollback()
        raise
    finally:
        connection.close()


# ---------------------------------------------------------
# 불량 사유 코드
# ---------------------------------------------------------

@dataclass
class DefectReasonCodeRegistration:
    reason_code: str
    reason_name: str


def validate_defect_reason_code(data: DefectReasonCodeRegistration) -> list[str]:
    from src.queries import defect_reason_code_exists

    errors: list[str] = []
    if not data.reason_code.strip():
        errors.append("사유 코드를 입력하세요.")
    if not data.reason_name.strip():
        errors.append("사유명을 입력하세요.")
    if data.reason_code.strip() and defect_reason_code_exists(data.reason_code.strip()):
        errors.append("이미 존재하는 사유 코드입니다.")
    return errors


def register_defect_reason_code(data: DefectReasonCodeRegistration) -> dict:
    errors = validate_defect_reason_code(data)
    if errors:
        raise ValueError("\n".join(errors))

    connection = get_connection()
    try:
        connection.execute("BEGIN IMMEDIATE")
        cursor = connection.cursor()
        existing = cursor.execute(
            "SELECT reason_code FROM defect_reason_code WHERE reason_code = ?",
            (data.reason_code.strip(),),
        ).fetchone()
        if existing is not None:
            raise ValueError("이미 존재하는 사유 코드입니다.")
        cursor.execute(
            "INSERT INTO defect_reason_code (reason_code, reason_name, is_active) VALUES (?, ?, 'Y')",
            (data.reason_code.strip().upper(), data.reason_name.strip()),
        )
        connection.commit()
        return {"reason_code": data.reason_code.strip().upper(), "reason_name": data.reason_name.strip()}
    except sqlite3.IntegrityError as exc:
        connection.rollback()
        raise ValueError("데이터베이스 제약조건을 만족하지 못해 저장하지 못했습니다.") from exc
    except sqlite3.OperationalError as exc:
        connection.rollback()
        raise ValueError("다른 작업이 진행 중입니다. 잠시 후 다시 시도해주세요.") from exc
    except ValueError:
        connection.rollback()
        raise
    finally:
        connection.close()


def set_defect_reason_code_active(reason_code: str, is_active: str) -> dict:
    if is_active not in ("Y", "N"):
        raise ValueError("사용여부 값이 올바르지 않습니다.")
    connection = get_connection()
    try:
        connection.execute("BEGIN IMMEDIATE")
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE defect_reason_code SET is_active = ? WHERE reason_code = ?",
            (is_active, reason_code),
        )
        connection.commit()
        return {"reason_code": reason_code, "is_active": is_active}
    except sqlite3.OperationalError as exc:
        connection.rollback()
        raise ValueError("다른 작업이 진행 중입니다. 잠시 후 다시 시도해주세요.") from exc
    finally:
        connection.close()


# ---------------------------------------------------------
# 검사 등록
# ---------------------------------------------------------

@dataclass
class InspectionRegistration:
    lot_id: int
    inspection_type: str
    inspection_date: date
    checked_qty: float
    defect_qty: float
    result: str
    reason_code: str | None = None
    defect_reason: str | None = None


def validate_inspection(data: InspectionRegistration) -> list[str]:
    from src.queries import lot_qty, inspection_lot_exists, defect_reason_code_exists

    errors: list[str] = []
    if data.checked_qty <= 0:
        errors.append("검사수량은 0보다 커야 합니다.")
    if data.defect_qty < 0:
        errors.append("불량수량은 0 이상이어야 합니다.")
    if data.defect_qty > data.checked_qty:
        errors.append("불량수량은 검사수량보다 클 수 없습니다.")

    if data.result not in ("PASS", "FAIL", "PARTIAL"):
        errors.append("검사 결과 값이 올바르지 않습니다.")
    elif data.result == "PASS" and data.defect_qty > 0:
        errors.append("합격(PASS) 판정에는 불량수량이 0이어야 합니다.")
    elif data.result == "FAIL" and data.defect_qty != data.checked_qty:
        errors.append("불합격(FAIL) 판정은 불량수량이 검사수량과 같아야 합니다.")
    elif data.result == "PARTIAL" and not (0 < data.defect_qty < data.checked_qty):
        errors.append("부분불량(PARTIAL) 판정은 불량수량이 0과 검사수량 사이여야 합니다.")

    lot_total_qty = lot_qty(data.lot_id)
    if lot_total_qty is None:
        errors.append("존재하지 않는 LOT입니다.")
    elif data.checked_qty > lot_total_qty:
        errors.append(f"검사수량({data.checked_qty:,.0f})이 LOT 수량({lot_total_qty:,.0f})보다 많습니다.")

    if inspection_lot_exists(data.lot_id):
        errors.append("이미 검사 이력이 존재하는 LOT입니다.")

    if data.reason_code and not defect_reason_code_exists(data.reason_code):
        errors.append("존재하지 않는 불량 사유 코드입니다.")

    return errors


def register_inspection(data: InspectionRegistration) -> dict:
    errors = validate_inspection(data)
    if errors:
        raise ValueError("\n".join(errors))

    connection = get_connection()
    try:
        connection.execute("BEGIN IMMEDIATE")
        cursor = connection.cursor()

        existing = cursor.execute(
            "SELECT inspection_id FROM inspection WHERE lot_id = ?", (data.lot_id,)
        ).fetchone()
        if existing is not None:
            raise ValueError("이미 검사 이력이 존재하는 LOT입니다.")

        cursor.execute(
            """
            INSERT INTO inspection
                (lot_id, inspection_type, inspection_date, checked_qty, defect_qty, result, reason_code, defect_reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data.lot_id,
                data.inspection_type,
                str(data.inspection_date),
                data.checked_qty,
                data.defect_qty,
                data.result,
                data.reason_code,
                data.defect_reason,
            ),
        )
        inspection_id = cursor.lastrowid

        connection.commit()
        return {"inspection_id": inspection_id, "lot_id": data.lot_id, "result": data.result}
    except sqlite3.IntegrityError as exc:
        connection.rollback()
        raise ValueError("데이터베이스 제약조건을 만족하지 못해 저장하지 못했습니다.") from exc
    except sqlite3.OperationalError as exc:
        connection.rollback()
        raise ValueError("다른 작업이 진행 중입니다. 잠시 후 다시 시도해주세요.") from exc
    except ValueError:
        connection.rollback()
        raise
    finally:
        connection.close()


# ---------------------------------------------------------
# 개별 시리얼 부여
# ---------------------------------------------------------

def assign_serials(lot_id: int, serial_prefix: str, count: int, created_date: date) -> dict:
    if count <= 0:
        raise ValueError("부여할 시리얼 수는 0보다 커야 합니다.")
    if not serial_prefix.strip():
        raise ValueError("시리얼 접두어를 입력하세요.")

    connection = get_connection()
    try:
        connection.execute("BEGIN IMMEDIATE")
        cursor = connection.cursor()

        already = cursor.execute(
            "SELECT COUNT(*) AS cnt FROM unit_serial WHERE lot_id = ?", (lot_id,)
        ).fetchone()["cnt"]
        if already > 0:
            raise ValueError("이 LOT에는 이미 시리얼이 부여되어 있습니다.")

        created_ids = []
        for i in range(1, count + 1):
            serial_no = f"{serial_prefix.strip()}-{i:05d}"
            existing = cursor.execute(
                "SELECT unit_serial_id FROM unit_serial WHERE serial_no = ?", (serial_no,)
            ).fetchone()
            if existing is not None:
                raise ValueError(f"시리얼 번호 '{serial_no}'가 이미 존재합니다. 접두어를 바꿔주세요.")
            cursor.execute(
                """
                INSERT INTO unit_serial (lot_id, serial_no, status, created_date)
                VALUES (?, ?, 'IN_PROCESS', ?)
                """,
                (lot_id, serial_no, str(created_date)),
            )
            created_ids.append(cursor.lastrowid)

        connection.commit()
        return {"lot_id": lot_id, "created_count": len(created_ids)}
    except sqlite3.IntegrityError as exc:
        connection.rollback()
        raise ValueError("데이터베이스 제약조건을 만족하지 못해 저장하지 못했습니다.") from exc
    except sqlite3.OperationalError as exc:
        connection.rollback()
        raise ValueError("다른 작업이 진행 중입니다. 잠시 후 다시 시도해주세요.") from exc
    except ValueError:
        connection.rollback()
        raise
    finally:
        connection.close()


def set_serial_status(unit_serial_id: int, status: str) -> dict:
    if status not in ("IN_PROCESS", "COMPLETED", "SCRAPPED"):
        raise ValueError("상태 값이 올바르지 않습니다.")
    connection = get_connection()
    try:
        connection.execute("BEGIN IMMEDIATE")
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE unit_serial SET status = ? WHERE unit_serial_id = ?", (status, unit_serial_id)
        )
        connection.commit()
        return {"unit_serial_id": unit_serial_id, "status": status}
    except sqlite3.OperationalError as exc:
        connection.rollback()
        raise ValueError("다른 작업이 진행 중입니다. 잠시 후 다시 시도해주세요.") from exc
    finally:
        connection.close()


# ---------------------------------------------------------
# 출하
# ---------------------------------------------------------

@dataclass
class ShipmentRegistration:
    shipment_no: str
    partner_id: int | None
    shipment_date: date
    shipment_rows: list[dict]  # [{"lot_id": int, "qty": float}, ...]


def validate_shipment(data: ShipmentRegistration) -> list[str]:
    from src.queries import finished_lots_with_balance, shipment_no_exists

    errors: list[str] = []
    if not data.shipment_no.strip():
        errors.append("출하번호를 입력하세요.")
    if not data.shipment_rows:
        errors.append("출하할 완제품 LOT를 1개 이상 선택하세요.")

    lot_ids = [row["lot_id"] for row in data.shipment_rows]
    if len(lot_ids) != len(set(lot_ids)):
        errors.append("동일한 LOT를 중복 선택할 수 없습니다.")

    balance_by_lot = {row["lot_id"]: row for row in finished_lots_with_balance()}
    for row in data.shipment_rows:
        if row["qty"] <= 0:
            errors.append("출하수량은 모두 0보다 커야 합니다.")
            continue
        lot_info = balance_by_lot.get(row["lot_id"])
        if lot_info is None:
            errors.append(f"LOT ID {row['lot_id']}는 더 이상 출하할 수 없습니다.")
            continue
        if row["qty"] > lot_info["remaining_qty"]:
            errors.append(
                f"{lot_info['lot_no']}의 잔량({lot_info['remaining_qty']:,.0f})보다 "
                f"출하수량({row['qty']:,.0f})이 많습니다."
            )
        if lot_info["inspection_result"] == "FAIL":
            errors.append(f"{lot_info['lot_no']}는 불합격(FAIL) 판정된 LOT라 출하할 수 없습니다.")

    if data.shipment_no.strip() and shipment_no_exists(data.shipment_no.strip()):
        errors.append("이미 존재하는 출하번호입니다.")

    return errors


def register_shipment(data: ShipmentRegistration) -> dict:
    errors = validate_shipment(data)
    if errors:
        raise ValueError("\n".join(errors))

    connection = get_connection()
    try:
        connection.execute("BEGIN IMMEDIATE")
        cursor = connection.cursor()

        existing_no = cursor.execute(
            "SELECT shipment_id FROM shipment WHERE shipment_no = ?", (data.shipment_no.strip(),)
        ).fetchone()
        if existing_no is not None:
            raise ValueError("이미 존재하는 출하번호입니다.")

        for row in data.shipment_rows:
            check = cursor.execute(
                """
                SELECT
                    l.qty - COALESCE((
                        SELECT SUM(si.qty) FROM shipment_item AS si WHERE si.lot_id = l.lot_id
                    ), 0) AS remaining_qty,
                    (SELECT result FROM inspection WHERE lot_id = l.lot_id) AS inspection_result
                FROM lot AS l
                WHERE l.lot_id = ?
                """,
                (row["lot_id"],),
            ).fetchone()
            if check is None or row["qty"] > check["remaining_qty"]:
                raise ValueError(f"LOT ID {row['lot_id']}의 잔량이 부족합니다.")
            if check["inspection_result"] == "FAIL":
                raise ValueError(f"LOT ID {row['lot_id']}는 불합격 판정되어 출하할 수 없습니다.")

        cursor.execute(
            """
            INSERT INTO shipment (shipment_no, partner_id, shipment_date, status)
            VALUES (?, ?, ?, 'COMPLETED')
            """,
            (data.shipment_no.strip(), data.partner_id, str(data.shipment_date)),
        )
        shipment_id = cursor.lastrowid

        for row in data.shipment_rows:
            cursor.execute(
                "INSERT INTO shipment_item (shipment_id, lot_id, qty) VALUES (?, ?, ?)",
                (shipment_id, row["lot_id"], row["qty"]),
            )

        connection.commit()
        return {"shipment_id": shipment_id, "shipment_no": data.shipment_no.strip()}
    except sqlite3.IntegrityError as exc:
        connection.rollback()
        raise ValueError("데이터베이스 제약조건을 만족하지 못해 저장하지 못했습니다.") from exc
    except sqlite3.OperationalError as exc:
        connection.rollback()
        raise ValueError("다른 작업이 진행 중입니다. 잠시 후 다시 시도해주세요.") from exc
    except ValueError:
        connection.rollback()
        raise
    finally:
        connection.close()
