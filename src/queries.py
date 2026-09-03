from __future__ import annotations

import sqlite3

from src.db import fetch_all, fetch_dataframe, fetch_one


def next_id(table_name: str, id_column: str) -> int:
    row = fetch_one(f"SELECT COALESCE(MAX({id_column}), 0) + 1 AS next_id FROM {table_name}")
    return int(row["next_id"])


# ---------------------------------------------------------
# item / item_spec
# ---------------------------------------------------------

def items(keyword: str = "", item_type: str = "전체"):
    params: list[str] = []
    where = ["1 = 1"]

    if keyword:
        where.append("(i.item_code LIKE ? OR i.item_name LIKE ?)")
        params.extend([f"%{keyword}%", f"%{keyword}%"])

    if item_type != "전체":
        where.append("i.item_type = ?")
        params.append(item_type)

    return fetch_dataframe(
        f"""
        SELECT
            i.item_id,
            i.item_code,
            i.item_name,
            i.item_type,
            i.unit,
            i.is_active,
            s.drawing_no,
            s.drawing_rev
        FROM item AS i
        LEFT JOIN item_spec AS s
            ON i.item_id = s.item_id
        WHERE {' AND '.join(where)}
        ORDER BY i.item_type, i.item_code
        """,
        tuple(params),
    )


def item_type_counts():
    return fetch_dataframe(
        """
        SELECT item_type, COUNT(*) AS item_count
        FROM item
        GROUP BY item_type
        ORDER BY item_type
        """
    )


def active_items_for_select(item_type: str | None = None):
    params: tuple = ()
    where = "WHERE is_active = 'Y'"
    if item_type:
        where += " AND item_type = ?"
        params = (item_type,)

    return fetch_all(
        f"""
        SELECT item_id, item_code, item_name, item_type, unit
        FROM item
        {where}
        ORDER BY item_code
        """,
        params,
    )


def all_items_for_select():
    """활성/비활성 모두 포함한 전체 품목 목록 (수정 화면 선택용)."""
    return fetch_all(
        """
        SELECT item_id, item_code, item_name, item_type, unit, is_active
        FROM item
        ORDER BY item_type, item_code
        """
    )


def item_by_id(item_id: int) -> sqlite3.Row | None:
    return fetch_one(
        "SELECT item_id, item_code, item_name, item_type, unit, is_active FROM item WHERE item_id = ?",
        (item_id,),
    )


def item_code_exists(item_code: str) -> bool:
    row = fetch_one("SELECT item_id FROM item WHERE item_code = ?", (item_code,))
    return row is not None


def item_spec_by_item_id(item_id: int) -> sqlite3.Row | None:
    return fetch_one(
        """
        SELECT item_spec_id, item_id, drawing_no, drawing_rev, material_spec, tolerance_note
        FROM item_spec
        WHERE item_id = ?
        """,
        (item_id,),
    )


# ---------------------------------------------------------
# partner (거래처)
# ---------------------------------------------------------

def partners(keyword: str = "", partner_type: str = "전체"):
    params: list[str] = []
    where = ["1 = 1"]

    if keyword:
        where.append("p.partner_name LIKE ?")
        params.append(f"%{keyword}%")

    if partner_type != "전체":
        where.append("p.partner_type = ?")
        params.append(partner_type)

    return fetch_dataframe(
        f"""
        SELECT partner_id, partner_name, partner_type, contact
        FROM partner AS p
        WHERE {' AND '.join(where)}
        ORDER BY partner_type, partner_name
        """,
        tuple(params),
    )


def active_partners_for_select(partner_type: str | None = None):
    params: tuple = ()
    where = "WHERE 1 = 1"
    if partner_type:
        where += " AND partner_type = ?"
        params = (partner_type,)

    return fetch_all(
        f"""
        SELECT partner_id, partner_name, partner_type, contact
        FROM partner
        {where}
        ORDER BY partner_name
        """,
        params,
    )


def partner_by_id(partner_id: int) -> sqlite3.Row | None:
    return fetch_one(
        "SELECT partner_id, partner_name, partner_type, contact FROM partner WHERE partner_id = ?",
        (partner_id,),
    )


# ---------------------------------------------------------
# process_master (공정 종류)
# ---------------------------------------------------------

def process_list():
    return fetch_dataframe(
        """
        SELECT process_code, process_name
        FROM process_master
        ORDER BY process_code
        """
    )


def active_process_for_select():
    return fetch_all(
        """
        SELECT process_code, process_name
        FROM process_master
        ORDER BY process_code
        """
    )


def process_code_exists(process_code: str) -> bool:
    row = fetch_one("SELECT process_code FROM process_master WHERE process_code = ?", (process_code,))
    return row is not None


# ---------------------------------------------------------
# equipment (설비)
# ---------------------------------------------------------

def equipment_list(process_code: str = "전체"):
    params: list[str] = []
    where = ["1 = 1"]

    if process_code != "전체":
        where.append("e.process_code = ?")
        params.append(process_code)

    return fetch_dataframe(
        f"""
        SELECT
            e.equipment_id,
            e.equipment_code,
            e.equipment_name,
            e.process_code,
            pm.process_name,
            e.is_active
        FROM equipment AS e
        JOIN process_master AS pm
            ON e.process_code = pm.process_code
        WHERE {' AND '.join(where)}
        ORDER BY e.process_code, e.equipment_code
        """,
        tuple(params),
    )


def active_equipment_for_select(process_code: str | None = None):
    params: list[str] = ["Y"]
    where = "WHERE e.is_active = ?"
    if process_code:
        where += " AND e.process_code = ?"
        params.append(process_code)

    return fetch_all(
        f"""
        SELECT e.equipment_id, e.equipment_code, e.equipment_name, e.process_code
        FROM equipment AS e
        {where}
        ORDER BY e.equipment_code
        """,
        tuple(params),
    )


def equipment_code_exists(equipment_code: str) -> bool:
    row = fetch_one(
        "SELECT equipment_id FROM equipment WHERE equipment_code = ?", (equipment_code,)
    )
    return row is not None


def equipment_by_id(equipment_id: int) -> sqlite3.Row | None:
    return fetch_one(
        """
        SELECT equipment_id, equipment_code, equipment_name, process_code, is_active
        FROM equipment
        WHERE equipment_id = ?
        """,
        (equipment_id,),
    )


# ---------------------------------------------------------
# user (사용자 계정)
# ---------------------------------------------------------

def user_by_id(user_id: str):
    return fetch_one(
        "SELECT user_id, user_name, password_hash, role, is_active FROM user WHERE user_id = ?",
        (user_id,),
    )


def user_id_exists(user_id: str) -> bool:
    row = fetch_one("SELECT user_id FROM user WHERE user_id = ?", (user_id,))
    return row is not None


def all_users():
    return fetch_dataframe(
        """
        SELECT user_id, user_name, role, is_active
        FROM user
        ORDER BY user_id
        """
    )


# ---------------------------------------------------------
# routing / routing_step / bom
# ---------------------------------------------------------

def routing_by_product(product_item_id: int):
    return fetch_one(
        """
        SELECT routing_id, product_item_id, routing_name, is_active
        FROM routing
        WHERE product_item_id = ?
        """,
        (product_item_id,),
    )


def products_with_routing_status():
    """제품별로 라우팅 등록 여부/공정 단계 수를 함께 보여준다."""
    return fetch_dataframe(
        """
        SELECT
            i.item_id AS product_item_id,
            i.item_code,
            i.item_name,
            r.routing_id,
            r.routing_name,
            COUNT(rs.routing_step_id) AS step_count
        FROM item AS i
        LEFT JOIN routing AS r
            ON i.item_id = r.product_item_id
        LEFT JOIN routing_step AS rs
            ON r.routing_id = rs.routing_id
        WHERE i.item_type = 'PRODUCT'
        GROUP BY i.item_id, i.item_code, i.item_name, r.routing_id, r.routing_name
        ORDER BY i.item_code
        """
    )


def routing_steps(routing_id: int):
    return fetch_dataframe(
        """
        SELECT
            rs.routing_step_id,
            rs.step_no,
            rs.process_code,
            pm.process_name,
            rs.output_item_id,
            oi.item_code AS output_item_code,
            oi.item_name AS output_item_name,
            oi.item_type AS output_item_type
        FROM routing_step AS rs
        JOIN process_master AS pm
            ON rs.process_code = pm.process_code
        JOIN item AS oi
            ON rs.output_item_id = oi.item_id
        WHERE rs.routing_id = ?
        ORDER BY rs.step_no
        """,
        (routing_id,),
    )


def next_step_no(routing_id: int) -> int:
    row = fetch_one(
        "SELECT COALESCE(MAX(step_no), 0) + 1 AS next_no FROM routing_step WHERE routing_id = ?",
        (routing_id,),
    )
    return int(row["next_no"])


def routing_step_by_id(routing_step_id: int):
    return fetch_one(
        """
        SELECT routing_step_id, routing_id, step_no, process_code, output_item_id
        FROM routing_step
        WHERE routing_step_id = ?
        """,
        (routing_step_id,),
    )


def routing_step_bom_count(routing_step_id: int) -> int:
    row = fetch_one(
        "SELECT COUNT(*) AS cnt FROM bom WHERE routing_step_id = ?", (routing_step_id,)
    )
    return int(row["cnt"])


def routing_step_operation_count(routing_step_id: int) -> int:
    row = fetch_one(
        "SELECT COUNT(*) AS cnt FROM operation WHERE routing_step_id = ?", (routing_step_id,)
    )
    return int(row["cnt"])


def bom_for_routing_step(routing_step_id: int):
    return fetch_dataframe(
        """
        SELECT
            b.bom_id,
            b.material_item_id,
            m.item_code AS material_code,
            m.item_name AS material_name,
            m.unit AS material_unit,
            b.qty_per_unit
        FROM bom AS b
        JOIN item AS m
            ON b.material_item_id = m.item_id
        WHERE b.routing_step_id = ?
        ORDER BY m.item_code
        """,
        (routing_step_id,),
    )


def bom_line_exists(routing_step_id: int, material_item_id: int) -> bool:
    row = fetch_one(
        "SELECT bom_id FROM bom WHERE routing_step_id = ? AND material_item_id = ?",
        (routing_step_id, material_item_id),
    )
    return row is not None


# ---------------------------------------------------------
# lot (입고)
# ---------------------------------------------------------

def lot_no_exists(lot_no: str) -> bool:
    row = fetch_one("SELECT lot_id FROM lot WHERE lot_no = ?", (lot_no,))
    return row is not None


def lots(keyword: str = "", lot_type: str = "전체", item_id: int | None = None):
    params: list[object] = []
    where = ["1 = 1"]

    if keyword:
        where.append("l.lot_no LIKE ?")
        params.append(f"%{keyword}%")

    if lot_type != "전체":
        where.append("l.lot_type = ?")
        params.append(lot_type)

    if item_id:
        where.append("l.item_id = ?")
        params.append(item_id)

    return fetch_dataframe(
        f"""
        SELECT
            l.lot_id,
            l.lot_no,
            i.item_code,
            i.item_name,
            i.item_type,
            l.lot_type,
            l.qty,
            l.received_date,
            l.produced_date,
            l.expire_date,
            p.partner_name
        FROM lot AS l
        JOIN item AS i
            ON l.item_id = i.item_id
        LEFT JOIN partner AS p
            ON l.partner_id = p.partner_id
        WHERE {' AND '.join(where)}
        ORDER BY
            COALESCE(l.received_date, l.produced_date) DESC,
            l.lot_no
        """,
        tuple(params),
    )


def lots_for_select(lot_type: str | None = None, item_id: int | None = None):
    params: list[object] = []
    where = []
    if lot_type:
        where.append("l.lot_type = ?")
        params.append(lot_type)
    if item_id:
        where.append("l.item_id = ?")
        params.append(item_id)
    where_clause = ("WHERE " + " AND ".join(where)) if where else ""

    return fetch_all(
        f"""
        SELECT
            l.lot_id,
            l.lot_no,
            l.item_id,
            i.item_name,
            l.lot_type,
            l.qty
        FROM lot AS l
        JOIN item AS i
            ON l.item_id = i.item_id
        {where_clause}
        ORDER BY l.lot_no
        """,
        tuple(params),
    )


# ---------------------------------------------------------
# work_order (작업지시)
# ---------------------------------------------------------

def work_order_no_exists(work_order_no: str) -> bool:
    row = fetch_one(
        "SELECT work_order_id FROM work_order WHERE work_order_no = ?", (work_order_no,)
    )
    return row is not None


def products_with_active_routing():
    """라우팅이 등록되어 있는(is_active='Y') 완제품 목록 (작업지시 등록 선택용)."""
    return fetch_all(
        """
        SELECT
            i.item_id AS product_item_id,
            i.item_code,
            i.item_name,
            r.routing_id,
            r.routing_name
        FROM item AS i
        JOIN routing AS r
            ON i.item_id = r.product_item_id AND r.is_active = 'Y'
        WHERE i.item_type = 'PRODUCT' AND i.is_active = 'Y'
        ORDER BY i.item_code
        """
    )


def work_orders(keyword: str = "", status_filter: str = "전체"):
    params: list[str] = []
    where = ["1 = 1"]

    if keyword:
        where.append("(w.work_order_no LIKE ? OR i.item_name LIKE ?)")
        params.extend([f"%{keyword}%", f"%{keyword}%"])

    if status_filter != "전체":
        where.append("w.status = ?")
        params.append(status_filter)

    return fetch_dataframe(
        f"""
        SELECT
            w.work_order_id,
            w.work_order_no,
            i.item_code,
            i.item_name,
            r.routing_name,
            w.planned_qty,
            w.plan_date,
            w.status
        FROM work_order AS w
        JOIN item AS i
            ON w.product_item_id = i.item_id
        JOIN routing AS r
            ON w.routing_id = r.routing_id
        WHERE {' AND '.join(where)}
        ORDER BY w.plan_date DESC, w.work_order_id DESC
        """,
        tuple(params),
    )


def work_order_by_id(work_order_id: int):
    return fetch_one(
        """
        SELECT work_order_id, work_order_no, product_item_id, routing_id, planned_qty, plan_date, status
        FROM work_order
        WHERE work_order_id = ?
        """,
        (work_order_id,),
    )


def work_order_operation_count(work_order_id: int) -> int:
    row = fetch_one(
        "SELECT COUNT(*) AS cnt FROM operation WHERE work_order_id = ?", (work_order_id,)
    )
    return int(row["cnt"])


# ---------------------------------------------------------
# operation (공정 실행)
# ---------------------------------------------------------

def lots_with_balance_for_item(item_id: int, lot_type: str):
    """특정 품목의 특정 lot_type(RECEIPT/WIP) LOT별 원본수량과 현재 잔량."""
    return fetch_all(
        """
        SELECT
            l.lot_id,
            l.lot_no,
            l.item_id,
            i.item_name,
            l.qty AS original_qty,
            l.qty - COALESCE(SUM(om.qty), 0) AS remaining_qty
        FROM lot AS l
        JOIN item AS i ON l.item_id = i.item_id
        LEFT JOIN operation_material AS om ON om.material_lot_id = l.lot_id
        WHERE l.lot_type = ? AND l.item_id = ?
        GROUP BY l.lot_id, l.lot_no, l.item_id, i.item_name, l.qty
        HAVING remaining_qty > 0
        ORDER BY l.lot_no
        """,
        (lot_type, item_id),
    )


def routing_step_max_no(routing_id: int) -> int:
    row = fetch_one(
        "SELECT COALESCE(MAX(step_no), 0) AS max_no FROM routing_step WHERE routing_id = ?",
        (routing_id,),
    )
    return int(row["max_no"])


def next_routing_step_for_work_order(work_order_id: int):
    """이 작업지시에서 아직 완료되지 않은 단계 중 가장 먼저 와야 할 단계를 반환한다. 다 끝났으면 None."""
    return fetch_one(
        """
        SELECT rs.routing_step_id, rs.routing_id, rs.step_no, rs.process_code,
               pm.process_name, rs.output_item_id, oi.item_code AS output_item_code,
               oi.item_name AS output_item_name, oi.item_type AS output_item_type
        FROM routing_step AS rs
        JOIN process_master AS pm ON rs.process_code = pm.process_code
        JOIN item AS oi ON rs.output_item_id = oi.item_id
        WHERE rs.routing_id = (SELECT routing_id FROM work_order WHERE work_order_id = ?)
          AND rs.routing_step_id NOT IN (
              SELECT routing_step_id FROM operation
              WHERE work_order_id = ? AND status = 'COMPLETED'
          )
        ORDER BY rs.step_no
        LIMIT 1
        """,
        (work_order_id, work_order_id),
    )


def operations_for_work_order(work_order_id: int):
    return fetch_dataframe(
        """
        SELECT
            o.operation_id,
            rs.step_no,
            pm.process_name,
            e.equipment_name,
            o.operation_date,
            o.qty,
            l.lot_no AS output_lot_no,
            l.lot_type AS output_lot_type,
            o.status
        FROM operation AS o
        JOIN routing_step AS rs ON o.routing_step_id = rs.routing_step_id
        JOIN process_master AS pm ON rs.process_code = pm.process_code
        LEFT JOIN equipment AS e ON o.equipment_id = e.equipment_id
        JOIN lot AS l ON o.output_lot_id = l.lot_id
        WHERE o.work_order_id = ?
        ORDER BY rs.step_no
        """,
        (work_order_id,),
    )


def operation_materials(operation_id: int):
    return fetch_dataframe(
        """
        SELECT
            i.item_code,
            i.item_name,
            l.lot_no,
            om.qty
        FROM operation_material AS om
        JOIN item AS i ON om.material_item_id = i.item_id
        JOIN lot AS l ON om.material_lot_id = l.lot_id
        WHERE om.operation_id = ?
        ORDER BY i.item_code
        """,
        (operation_id,),
    )


# ---------------------------------------------------------
# defect_reason_code / inspection
# ---------------------------------------------------------

def active_defect_reason_codes():
    return fetch_all(
        """
        SELECT reason_code, reason_name
        FROM defect_reason_code
        WHERE is_active = 'Y'
        ORDER BY reason_code
        """
    )


def all_defect_reason_codes():
    return fetch_dataframe(
        """
        SELECT reason_code, reason_name, is_active
        FROM defect_reason_code
        ORDER BY reason_code
        """
    )


def defect_reason_code_exists(reason_code: str) -> bool:
    row = fetch_one(
        "SELECT reason_code FROM defect_reason_code WHERE reason_code = ?", (reason_code,)
    )
    return row is not None


def lot_qty(lot_id: int) -> float | None:
    row = fetch_one("SELECT qty FROM lot WHERE lot_id = ?", (lot_id,))
    return float(row["qty"]) if row is not None else None


def inspection_lot_exists(lot_id: int) -> bool:
    row = fetch_one("SELECT inspection_id FROM inspection WHERE lot_id = ?", (lot_id,))
    return row is not None


def uninspected_lots(lot_type: str | None = None):
    """아직 검사 이력이 없는 LOT 목록."""
    params: list[str] = []
    where = ["insp.inspection_id IS NULL"]
    if lot_type:
        where.append("l.lot_type = ?")
        params.append(lot_type)

    return fetch_all(
        f"""
        SELECT
            l.lot_id,
            l.lot_no,
            l.item_id,
            i.item_name,
            l.lot_type,
            l.qty
        FROM lot AS l
        JOIN item AS i ON l.item_id = i.item_id
        LEFT JOIN inspection AS insp ON insp.lot_id = l.lot_id
        WHERE {' AND '.join(where)}
        ORDER BY l.lot_no
        """,
        tuple(params),
    )


def inspections(keyword: str = "", result_filter: str = "전체", inspection_type: str = "전체"):
    params: list[str] = []
    where = ["1 = 1"]

    if keyword:
        where.append("(l.lot_no LIKE ? OR i.item_name LIKE ?)")
        params.extend([f"%{keyword}%", f"%{keyword}%"])
    if result_filter != "전체":
        where.append("insp.result = ?")
        params.append(result_filter)
    if inspection_type != "전체":
        where.append("insp.inspection_type = ?")
        params.append(inspection_type)

    return fetch_dataframe(
        f"""
        SELECT
            insp.inspection_id,
            l.lot_no,
            i.item_code,
            i.item_name,
            insp.inspection_type,
            insp.inspection_date,
            insp.checked_qty,
            insp.defect_qty,
            insp.result,
            c.reason_name AS defect_reason_code_name,
            insp.defect_reason
        FROM inspection AS insp
        JOIN lot AS l ON insp.lot_id = l.lot_id
        JOIN item AS i ON l.item_id = i.item_id
        LEFT JOIN defect_reason_code AS c ON insp.reason_code = c.reason_code
        WHERE {' AND '.join(where)}
        ORDER BY insp.inspection_date DESC, insp.inspection_id DESC
        """,
        tuple(params),
    )


def defect_rate_by_item():
    return fetch_dataframe(
        """
        SELECT
            i.item_code,
            i.item_name,
            SUM(insp.checked_qty) AS total_checked_qty,
            SUM(insp.defect_qty) AS total_defect_qty,
            ROUND(SUM(insp.defect_qty) * 100.0 / NULLIF(SUM(insp.checked_qty), 0), 2) AS defect_rate_pct,
            COUNT(*) AS inspection_count
        FROM inspection AS insp
        JOIN lot AS l ON insp.lot_id = l.lot_id
        JOIN item AS i ON l.item_id = i.item_id
        GROUP BY i.item_id, i.item_code, i.item_name
        ORDER BY defect_rate_pct DESC
        """
    )


# ---------------------------------------------------------
# unit_serial (개별 시리얼)
# ---------------------------------------------------------

def lots_without_serial(lot_type: str | None = None):
    """아직 시리얼이 하나도 안 부여된 LOT 목록 (WIP/FINISHED만 의미 있음)."""
    params: list[str] = []
    where = ["us.unit_serial_id IS NULL"]
    if lot_type:
        where.append("l.lot_type = ?")
        params.append(lot_type)

    return fetch_all(
        f"""
        SELECT l.lot_id, l.lot_no, l.item_id, i.item_name, l.lot_type, l.qty
        FROM lot AS l
        JOIN item AS i ON l.item_id = i.item_id
        LEFT JOIN unit_serial AS us ON us.lot_id = l.lot_id
        WHERE {' AND '.join(where)}
        GROUP BY l.lot_id
        HAVING COUNT(us.unit_serial_id) = 0
        ORDER BY l.lot_no
        """,
        tuple(params),
    )


def serials_for_lot(lot_id: int):
    return fetch_dataframe(
        """
        SELECT unit_serial_id, serial_no, status, created_date
        FROM unit_serial
        WHERE lot_id = ?
        ORDER BY serial_no
        """,
        (lot_id,),
    )


def serial_by_no(serial_no: str):
    return fetch_one(
        """
        SELECT us.unit_serial_id, us.serial_no, us.status, us.created_date,
               l.lot_id, l.lot_no, i.item_code, i.item_name
        FROM unit_serial AS us
        JOIN lot AS l ON us.lot_id = l.lot_id
        JOIN item AS i ON l.item_id = i.item_id
        WHERE us.serial_no = ?
        """,
        (serial_no,),
    )


# ---------------------------------------------------------
# shipment (출하)
# ---------------------------------------------------------

def finished_lots_with_balance():
    """FINISHED LOT의 원본 생산량, 현재 출하 가능 잔량, 최종 검사 결과."""
    return fetch_all(
        """
        SELECT
            l.lot_id,
            l.lot_no,
            l.item_id,
            i.item_name,
            l.qty AS original_qty,
            l.qty - COALESCE(SUM(si.qty), 0) AS remaining_qty,
            insp.result AS inspection_result
        FROM lot AS l
        JOIN item AS i ON l.item_id = i.item_id
        LEFT JOIN shipment_item AS si ON si.lot_id = l.lot_id
        LEFT JOIN inspection AS insp ON insp.lot_id = l.lot_id
        WHERE l.lot_type = 'FINISHED'
        GROUP BY l.lot_id, l.lot_no, l.item_id, i.item_name, l.qty, insp.result
        HAVING remaining_qty > 0
        ORDER BY l.lot_no
        """
    )


def shipment_no_exists(shipment_no: str) -> bool:
    row = fetch_one("SELECT shipment_id FROM shipment WHERE shipment_no = ?", (shipment_no,))
    return row is not None


def shipments(keyword: str = "", date_from=None, date_to=None):
    params: list[object] = []
    where = ["1 = 1"]

    if keyword:
        where.append("(s.shipment_no LIKE ? OR COALESCE(p.partner_name, '') LIKE ?)")
        params.extend([f"%{keyword}%", f"%{keyword}%"])
    if date_from:
        where.append("s.shipment_date >= ?")
        params.append(str(date_from))
    if date_to:
        where.append("s.shipment_date <= ?")
        params.append(str(date_to))

    return fetch_dataframe(
        f"""
        SELECT
            s.shipment_id,
            s.shipment_no,
            p.partner_name AS customer_name,
            s.shipment_date,
            s.status,
            COUNT(si.shipment_item_id) AS line_count,
            SUM(si.qty) AS total_qty
        FROM shipment AS s
        LEFT JOIN partner AS p ON s.partner_id = p.partner_id
        LEFT JOIN shipment_item AS si ON si.shipment_id = s.shipment_id
        WHERE {' AND '.join(where)}
        GROUP BY s.shipment_id, s.shipment_no, p.partner_name, s.shipment_date, s.status
        ORDER BY s.shipment_date DESC, s.shipment_no DESC
        """,
        tuple(params),
    )


def shipment_items(shipment_id: int):
    return fetch_dataframe(
        """
        SELECT l.lot_no, i.item_code, i.item_name, si.qty
        FROM shipment_item AS si
        JOIN lot AS l ON si.lot_id = l.lot_id
        JOIN item AS i ON l.item_id = i.item_id
        WHERE si.shipment_id = ?
        ORDER BY i.item_code, l.lot_no
        """,
        (shipment_id,),
    )


# ---------------------------------------------------------
# LOT 추적 (다단계 정방향/역방향, WITH RECURSIVE)
# ---------------------------------------------------------

def forward_trace_nodes(lot_id: int):
    """이 LOT(보통 원자재)가 공정을 거쳐 만들어낸 모든 하위 LOT을 단계 깊이와 함께 반환."""
    return fetch_dataframe(
        """
        WITH RECURSIVE forward(lot_id, depth) AS (
            SELECT ?, 0
            UNION ALL
            SELECT o.output_lot_id, f.depth + 1
            FROM forward AS f
            JOIN operation_material AS om ON om.material_lot_id = f.lot_id
            JOIN operation AS o ON om.operation_id = o.operation_id AND o.status = 'COMPLETED'
        )
        SELECT DISTINCT
            f.depth, l.lot_id, l.lot_no, l.lot_type, i.item_code, i.item_name, l.qty
        FROM forward AS f
        JOIN lot AS l ON f.lot_id = l.lot_id
        JOIN item AS i ON l.item_id = i.item_id
        ORDER BY f.depth, l.lot_no
        """,
        (lot_id,),
    )


def forward_trace_edges(lot_id: int):
    """정방향 추적 경로의 각 전환(어느 LOT이 어느 공정을 거쳐 어느 LOT이 되었는지)."""
    return fetch_dataframe(
        """
        WITH RECURSIVE forward(lot_id, depth) AS (
            SELECT ?, 0
            UNION ALL
            SELECT o.output_lot_id, f.depth + 1
            FROM forward AS f
            JOIN operation_material AS om ON om.material_lot_id = f.lot_id
            JOIN operation AS o ON om.operation_id = o.operation_id AND o.status = 'COMPLETED'
        )
        SELECT
            fl.lot_no AS from_lot_no, fi.item_name AS from_item_name,
            tl.lot_no AS to_lot_no, ti.item_name AS to_item_name,
            rs.step_no, pm.process_name,
            om.qty AS used_qty, o.qty AS produced_qty, o.operation_date
        FROM forward AS f
        JOIN operation_material AS om ON om.material_lot_id = f.lot_id
        JOIN operation AS o ON om.operation_id = o.operation_id AND o.status = 'COMPLETED'
        JOIN routing_step AS rs ON o.routing_step_id = rs.routing_step_id
        JOIN process_master AS pm ON rs.process_code = pm.process_code
        JOIN lot AS fl ON om.material_lot_id = fl.lot_id
        JOIN item AS fi ON fl.item_id = fi.item_id
        JOIN lot AS tl ON o.output_lot_id = tl.lot_id
        JOIN item AS ti ON tl.item_id = ti.item_id
        ORDER BY rs.step_no, o.operation_date
        """,
        (lot_id,),
    )


def forward_trace_shipments(lot_id: int):
    """정방향 추적 결과 중 실제로 출하된 완제품 LOT이 있으면 그 출하 정보."""
    return fetch_dataframe(
        """
        WITH RECURSIVE forward(lot_id, depth) AS (
            SELECT ?, 0
            UNION ALL
            SELECT o.output_lot_id, f.depth + 1
            FROM forward AS f
            JOIN operation_material AS om ON om.material_lot_id = f.lot_id
            JOIN operation AS o ON om.operation_id = o.operation_id AND o.status = 'COMPLETED'
        )
        SELECT
            s.shipment_no, s.shipment_date, p.partner_name AS customer_name,
            l.lot_no, i.item_name, si.qty
        FROM forward AS f
        JOIN lot AS l ON f.lot_id = l.lot_id
        JOIN item AS i ON l.item_id = i.item_id
        JOIN shipment_item AS si ON si.lot_id = f.lot_id
        JOIN shipment AS s ON si.shipment_id = s.shipment_id
        LEFT JOIN partner AS p ON s.partner_id = p.partner_id
        ORDER BY s.shipment_date
        """,
        (lot_id,),
    )


def backward_trace_nodes(lot_id: int):
    """이 LOT(보통 완제품)을 만드는 데 쓰인 모든 상위 LOT을 단계 깊이와 함께 반환."""
    return fetch_dataframe(
        """
        WITH RECURSIVE backward(lot_id, depth) AS (
            SELECT ?, 0
            UNION ALL
            SELECT om.material_lot_id, b.depth + 1
            FROM backward AS b
            JOIN operation AS o ON o.output_lot_id = b.lot_id AND o.status = 'COMPLETED'
            JOIN operation_material AS om ON om.operation_id = o.operation_id
        )
        SELECT DISTINCT
            b.depth, l.lot_id, l.lot_no, l.lot_type, i.item_code, i.item_name, l.qty
        FROM backward AS b
        JOIN lot AS l ON b.lot_id = l.lot_id
        JOIN item AS i ON l.item_id = i.item_id
        ORDER BY b.depth, l.lot_no
        """,
        (lot_id,),
    )


def backward_trace_edges(lot_id: int):
    """역방향 추적 경로의 각 전환."""
    return fetch_dataframe(
        """
        WITH RECURSIVE backward(lot_id, depth) AS (
            SELECT ?, 0
            UNION ALL
            SELECT om.material_lot_id, b.depth + 1
            FROM backward AS b
            JOIN operation AS o ON o.output_lot_id = b.lot_id AND o.status = 'COMPLETED'
            JOIN operation_material AS om ON om.operation_id = o.operation_id
        )
        SELECT
            fl.lot_no AS from_lot_no, fi.item_name AS from_item_name,
            tl.lot_no AS to_lot_no, ti.item_name AS to_item_name,
            rs.step_no, pm.process_name,
            om.qty AS used_qty, o.qty AS produced_qty, o.operation_date
        FROM backward AS b
        JOIN operation AS o ON o.output_lot_id = b.lot_id AND o.status = 'COMPLETED'
        JOIN routing_step AS rs ON o.routing_step_id = rs.routing_step_id
        JOIN process_master AS pm ON rs.process_code = pm.process_code
        JOIN operation_material AS om ON om.operation_id = o.operation_id
        JOIN lot AS fl ON om.material_lot_id = fl.lot_id
        JOIN item AS fi ON fl.item_id = fi.item_id
        JOIN lot AS tl ON o.output_lot_id = tl.lot_id
        JOIN item AS ti ON tl.item_id = ti.item_id
        ORDER BY rs.step_no DESC, o.operation_date
        """,
        (lot_id,),
    )


# ---------------------------------------------------------
# 홈 대시보드용
# ---------------------------------------------------------

def table_counts():
    return fetch_dataframe(
        """
        SELECT 'item' AS table_name, COUNT(*) AS row_count FROM item
        UNION ALL SELECT 'lot', COUNT(*) FROM lot
        UNION ALL SELECT 'routing', COUNT(*) FROM routing
        UNION ALL SELECT 'bom', COUNT(*) FROM bom
        UNION ALL SELECT 'work_order', COUNT(*) FROM work_order
        UNION ALL SELECT 'operation', COUNT(*) FROM operation
        UNION ALL SELECT 'inspection', COUNT(*) FROM inspection
        UNION ALL SELECT 'unit_serial', COUNT(*) FROM unit_serial
        UNION ALL SELECT 'shipment', COUNT(*) FROM shipment
        """
    )


def work_order_progress():
    """각 작업지시가 라우팅 전체 단계 중 몇 단계까지 완료했는지."""
    return fetch_dataframe(
        """
        SELECT
            w.work_order_id,
            w.work_order_no,
            i.item_name,
            w.planned_qty,
            w.status,
            (SELECT COUNT(*) FROM routing_step WHERE routing_id = w.routing_id) AS total_steps,
            (SELECT COUNT(*) FROM operation
                WHERE work_order_id = w.work_order_id AND status = 'COMPLETED') AS completed_steps
        FROM work_order AS w
        JOIN item AS i ON w.product_item_id = i.item_id
        WHERE w.status IN ('PLANNED', 'IN_PROGRESS')
        ORDER BY w.plan_date
        """
    )


def material_stock_summary():
    """원자재 품목별 총 입고량 / 총 사용량(공정투입) / 잔량."""
    return fetch_dataframe(
        """
        SELECT
            i.item_id, i.item_code, i.item_name, i.unit,
            COALESCE(receipt.total_qty, 0) AS total_received_qty,
            COALESCE(used.total_qty, 0) AS total_used_qty,
            COALESCE(receipt.total_qty, 0) - COALESCE(used.total_qty, 0) AS remaining_qty
        FROM item AS i
        LEFT JOIN (
            SELECT item_id, SUM(qty) AS total_qty FROM lot
            WHERE lot_type = 'RECEIPT' GROUP BY item_id
        ) AS receipt ON receipt.item_id = i.item_id
        LEFT JOIN (
            SELECT ml.item_id, SUM(om.qty) AS total_qty
            FROM operation_material AS om
            JOIN lot AS ml ON om.material_lot_id = ml.lot_id
            WHERE ml.lot_type = 'RECEIPT'
            GROUP BY ml.item_id
        ) AS used ON used.item_id = i.item_id
        WHERE i.item_type = 'MATERIAL' AND i.is_active = 'Y'
        ORDER BY i.item_code
        """
    )


def recent_activity(limit: int = 8):
    """최근 입고/공정실행/출하 이벤트를 하나로 합쳐 최신순으로 반환."""
    return fetch_dataframe(
        """
        SELECT 'RECEIPT' AS event_type, l.lot_no AS ref_no, l.received_date AS event_date,
               i.item_name, l.qty
        FROM lot AS l JOIN item AS i ON l.item_id = i.item_id
        WHERE l.lot_type = 'RECEIPT'
        UNION ALL
        SELECT 'OPERATION' AS event_type, l.lot_no AS ref_no, o.operation_date AS event_date,
               pm.process_name AS item_name, o.qty
        FROM operation AS o
        JOIN routing_step AS rs ON o.routing_step_id = rs.routing_step_id
        JOIN process_master AS pm ON rs.process_code = pm.process_code
        JOIN lot AS l ON o.output_lot_id = l.lot_id
        WHERE o.status = 'COMPLETED'
        UNION ALL
        SELECT 'SHIPMENT' AS event_type, s.shipment_no AS ref_no, s.shipment_date AS event_date,
               COALESCE(p.partner_name, '출하처 미지정') AS item_name,
               (SELECT SUM(qty) FROM shipment_item WHERE shipment_id = s.shipment_id) AS qty
        FROM shipment AS s
        LEFT JOIN partner AS p ON s.partner_id = p.partner_id
        ORDER BY event_date DESC, ref_no DESC
        LIMIT ?
        """,
        (limit,),
    )


# ---------------------------------------------------------
# handling_event (현장 모니터링: 충격/초음파/온습도 센서)
# ---------------------------------------------------------

def monitorable_lots():
    """모니터링 대상으로 고를 수 있는 LOT 목록 (WIP/FINISHED 전체, 최신순)."""
    return fetch_all(
        """
        SELECT l.lot_id, l.lot_no, l.lot_type, i.item_name
        FROM lot AS l
        JOIN item AS i ON l.item_id = i.item_id
        WHERE l.lot_type IN ('WIP', 'FINISHED')
        ORDER BY l.lot_id DESC
        LIMIT 100
        """
    )


def handling_events_for_lot(lot_id: int, limit: int = 50):
    return fetch_dataframe(
        """
        SELECT event_date, distance_cm, shock_detected, temperature, humidity, alert_triggered
        FROM handling_event
        WHERE lot_id = ?
        ORDER BY handling_event_id DESC
        LIMIT ?
        """,
        (lot_id, limit),
    )


def recent_handling_alerts(limit: int = 20):
    """최근 경보(alert_triggered='Y') 이력, 어느 LOT인지와 함께."""
    return fetch_dataframe(
        """
        SELECT
            he.event_date, he.distance_cm, he.shock_detected,
            he.temperature, he.humidity, l.lot_no, i.item_name
        FROM handling_event AS he
        LEFT JOIN lot AS l ON he.lot_id = l.lot_id
        LEFT JOIN item AS i ON l.item_id = i.item_id
        WHERE he.alert_triggered = 'Y'
        ORDER BY he.handling_event_id DESC
        LIMIT ?
        """,
        (limit,),
    )


def lot_has_shock_alert(lot_id: int) -> bool:
    """이 LOT에 충격 감지 이력이 한 번이라도 있는지."""
    row = fetch_one(
        "SELECT handling_event_id FROM handling_event WHERE lot_id = ? AND shock_detected = 'Y' LIMIT 1",
        (lot_id,),
    )
    return row is not None


def shock_alert_lot_ids() -> set:
    """충격 이력이 있는 LOT id 전체 (출하 페이지 배지 표시용)."""
    rows = fetch_all(
        "SELECT DISTINCT lot_id FROM handling_event WHERE shock_detected = 'Y' AND lot_id IS NOT NULL"
    )
    return {r["lot_id"] for r in rows}
