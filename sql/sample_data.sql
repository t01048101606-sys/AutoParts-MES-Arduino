INSERT INTO process_master (process_code, process_name) VALUES
    ('PRESS', '프레스'),
    ('WELD', '용접'),
    ('PAINT', '도장');


INSERT INTO equipment (equipment_code, equipment_name, process_code, is_active) VALUES
    ('EQ-PRESS-01', '프레스기 1호', 'PRESS', 'Y'),
    ('EQ-WELD-01', '용접기 1호', 'WELD', 'Y'),
    ('EQ-PAINT-01', '도장기 1호', 'PAINT', 'Y');


INSERT INTO item (item_code, item_name, item_type, unit, is_active) VALUES
    ('RM-STEEL', '냉연강판 1.2T', 'MATERIAL', 'KG', 'Y'),
    ('RM-BOLT', '육각볼트 M8', 'MATERIAL', 'EA', 'Y'),
    ('RM-PAINT', '전착도료', 'MATERIAL', 'L', 'Y');


INSERT INTO item (item_code, item_name, item_type, unit, is_active) VALUES
    ('SP-BRKA-PRS', '브라켓A-프레스품', 'SEMI_PRODUCT', 'EA', 'Y'),
    ('SP-BRKA-WLD', '브라켓A-용접품', 'SEMI_PRODUCT', 'EA', 'Y');


INSERT INTO item (item_code, item_name, item_type, unit, is_active) VALUES
    ('FG-BRKA', '브라켓 A', 'PRODUCT', 'EA', 'Y');


INSERT INTO item_spec (item_id, drawing_no, drawing_rev, material_spec, tolerance_note)
SELECT item_id, 'DWG-BRKA-001', 'Rev.C', 'SPCC 1.2T', '±0.1mm'
FROM item WHERE item_code = 'FG-BRKA';


INSERT INTO partner (partner_name, partner_type, contact) VALUES
    ('한국제철', 'SUPPLIER', '02-1234-5678'),
    ('대한볼트산업', 'SUPPLIER', '031-222-3333'),
    ('삼성도료', 'SUPPLIER', '032-444-5555'),
    ('현대파츠', 'CUSTOMER', '02-9876-5432');


INSERT INTO routing (product_item_id, routing_name, is_active)
SELECT item_id, '브라켓A 표준공정', 'Y' FROM item WHERE item_code = 'FG-BRKA';


INSERT INTO routing_step (routing_id, step_no, process_code, output_item_id)
SELECT
    (SELECT routing_id FROM routing WHERE product_item_id = (SELECT item_id FROM item WHERE item_code = 'FG-BRKA')),
    1, 'PRESS',
    (SELECT item_id FROM item WHERE item_code = 'SP-BRKA-PRS');

INSERT INTO routing_step (routing_id, step_no, process_code, output_item_id)
SELECT
    (SELECT routing_id FROM routing WHERE product_item_id = (SELECT item_id FROM item WHERE item_code = 'FG-BRKA')),
    2, 'WELD',
    (SELECT item_id FROM item WHERE item_code = 'SP-BRKA-WLD');

INSERT INTO routing_step (routing_id, step_no, process_code, output_item_id)
SELECT
    (SELECT routing_id FROM routing WHERE product_item_id = (SELECT item_id FROM item WHERE item_code = 'FG-BRKA')),
    3, 'PAINT',
    (SELECT item_id FROM item WHERE item_code = 'FG-BRKA');


INSERT INTO bom (routing_step_id, material_item_id, qty_per_unit)
SELECT
    (SELECT routing_step_id FROM routing_step WHERE step_no = 1
        AND routing_id = (SELECT routing_id FROM routing WHERE product_item_id = (SELECT item_id FROM item WHERE item_code = 'FG-BRKA'))),
    (SELECT item_id FROM item WHERE item_code = 'RM-STEEL'),
    0.5;


INSERT INTO bom (routing_step_id, material_item_id, qty_per_unit)
SELECT
    (SELECT routing_step_id FROM routing_step WHERE step_no = 2
        AND routing_id = (SELECT routing_id FROM routing WHERE product_item_id = (SELECT item_id FROM item WHERE item_code = 'FG-BRKA'))),
    (SELECT item_id FROM item WHERE item_code = 'RM-BOLT'),
    4;


INSERT INTO bom (routing_step_id, material_item_id, qty_per_unit)
SELECT
    (SELECT routing_step_id FROM routing_step WHERE step_no = 3
        AND routing_id = (SELECT routing_id FROM routing WHERE product_item_id = (SELECT item_id FROM item WHERE item_code = 'FG-BRKA'))),
    (SELECT item_id FROM item WHERE item_code = 'RM-PAINT'),
    0.05;


INSERT INTO defect_reason_code (reason_code, reason_name, is_active) VALUES
    ('DIM_OUT', '치수 불량', 'Y'),
    ('WELD_CRACK', '용접 균열', 'Y'),
    ('PAINT_RUN', '도장 흘림', 'Y'),
    ('SCRATCH', '외관 스크래치', 'Y');


INSERT INTO lot (lot_no, item_id, lot_type, qty, received_date, partner_id)
SELECT 'RM-20260101-0001', item_id, 'RECEIPT', 500, '2026-01-01',
       (SELECT partner_id FROM partner WHERE partner_name = '한국제철')
FROM item WHERE item_code = 'RM-STEEL';

INSERT INTO lot (lot_no, item_id, lot_type, qty, received_date, partner_id)
SELECT 'RM-20260101-0002', item_id, 'RECEIPT', 2000, '2026-01-01',
       (SELECT partner_id FROM partner WHERE partner_name = '대한볼트산업')
FROM item WHERE item_code = 'RM-BOLT';

INSERT INTO lot (lot_no, item_id, lot_type, qty, received_date, partner_id)
SELECT 'RM-20260101-0003', item_id, 'RECEIPT', 100, '2026-01-01',
       (SELECT partner_id FROM partner WHERE partner_name = '삼성도료')
FROM item WHERE item_code = 'RM-PAINT';


INSERT INTO work_order (work_order_no, product_item_id, routing_id, planned_qty, plan_date, status)
SELECT
    'WO-20260102-0001',
    (SELECT item_id FROM item WHERE item_code = 'FG-BRKA'),
    (SELECT routing_id FROM routing WHERE product_item_id = (SELECT item_id FROM item WHERE item_code = 'FG-BRKA')),
    100, '2026-01-02', 'PLANNED';


INSERT INTO lot (lot_no, item_id, lot_type, qty, produced_date)
SELECT 'WIP-20260103-00001', item_id, 'WIP', 100, '2026-01-03'
FROM item WHERE item_code = 'SP-BRKA-PRS';

INSERT INTO operation (work_order_id, routing_step_id, equipment_id, operation_date, qty, output_lot_id, status)
SELECT
    (SELECT work_order_id FROM work_order WHERE work_order_no = 'WO-20260102-0001'),
    (SELECT routing_step_id FROM routing_step WHERE step_no = 1
        AND routing_id = (SELECT routing_id FROM routing WHERE product_item_id = (SELECT item_id FROM item WHERE item_code = 'FG-BRKA'))),
    (SELECT equipment_id FROM equipment WHERE equipment_code = 'EQ-PRESS-01'),
    '2026-01-03', 100,
    (SELECT lot_id FROM lot WHERE lot_no = 'WIP-20260103-00001'),
    'COMPLETED';

INSERT INTO operation_material (operation_id, material_item_id, material_lot_id, qty)
SELECT
    (SELECT operation_id FROM operation WHERE output_lot_id = (SELECT lot_id FROM lot WHERE lot_no = 'WIP-20260103-00001')),
    (SELECT item_id FROM item WHERE item_code = 'RM-STEEL'),
    (SELECT lot_id FROM lot WHERE lot_no = 'RM-20260101-0001'),
    50;


INSERT INTO lot (lot_no, item_id, lot_type, qty, produced_date)
SELECT 'WIP-20260104-00001', item_id, 'WIP', 100, '2026-01-04'
FROM item WHERE item_code = 'SP-BRKA-WLD';

INSERT INTO operation (work_order_id, routing_step_id, equipment_id, operation_date, qty, output_lot_id, status)
SELECT
    (SELECT work_order_id FROM work_order WHERE work_order_no = 'WO-20260102-0001'),
    (SELECT routing_step_id FROM routing_step WHERE step_no = 2
        AND routing_id = (SELECT routing_id FROM routing WHERE product_item_id = (SELECT item_id FROM item WHERE item_code = 'FG-BRKA'))),
    (SELECT equipment_id FROM equipment WHERE equipment_code = 'EQ-WELD-01'),
    '2026-01-04', 100,
    (SELECT lot_id FROM lot WHERE lot_no = 'WIP-20260104-00001'),
    'COMPLETED';

INSERT INTO operation_material (operation_id, material_item_id, material_lot_id, qty)
SELECT
    (SELECT operation_id FROM operation WHERE output_lot_id = (SELECT lot_id FROM lot WHERE lot_no = 'WIP-20260104-00001')),
    (SELECT item_id FROM item WHERE item_code = 'RM-BOLT'),
    (SELECT lot_id FROM lot WHERE lot_no = 'RM-20260101-0002'),
    400;

INSERT INTO operation_material (operation_id, material_item_id, material_lot_id, qty)
SELECT
    (SELECT operation_id FROM operation WHERE output_lot_id = (SELECT lot_id FROM lot WHERE lot_no = 'WIP-20260104-00001')),
    (SELECT item_id FROM item WHERE item_code = 'SP-BRKA-PRS'),
    (SELECT lot_id FROM lot WHERE lot_no = 'WIP-20260103-00001'),
    100;


INSERT INTO lot (lot_no, item_id, lot_type, qty, produced_date)
SELECT 'FG-20260105-00001', item_id, 'FINISHED', 100, '2026-01-05'
FROM item WHERE item_code = 'FG-BRKA';

INSERT INTO operation (work_order_id, routing_step_id, equipment_id, operation_date, qty, output_lot_id, status)
SELECT
    (SELECT work_order_id FROM work_order WHERE work_order_no = 'WO-20260102-0001'),
    (SELECT routing_step_id FROM routing_step WHERE step_no = 3
        AND routing_id = (SELECT routing_id FROM routing WHERE product_item_id = (SELECT item_id FROM item WHERE item_code = 'FG-BRKA'))),
    (SELECT equipment_id FROM equipment WHERE equipment_code = 'EQ-PAINT-01'),
    '2026-01-05', 100,
    (SELECT lot_id FROM lot WHERE lot_no = 'FG-20260105-00001'),
    'COMPLETED';

INSERT INTO operation_material (operation_id, material_item_id, material_lot_id, qty)
SELECT
    (SELECT operation_id FROM operation WHERE output_lot_id = (SELECT lot_id FROM lot WHERE lot_no = 'FG-20260105-00001')),
    (SELECT item_id FROM item WHERE item_code = 'RM-PAINT'),
    (SELECT lot_id FROM lot WHERE lot_no = 'RM-20260101-0003'),
    5;

INSERT INTO operation_material (operation_id, material_item_id, material_lot_id, qty)
SELECT
    (SELECT operation_id FROM operation WHERE output_lot_id = (SELECT lot_id FROM lot WHERE lot_no = 'FG-20260105-00001')),
    (SELECT item_id FROM item WHERE item_code = 'SP-BRKA-WLD'),
    (SELECT lot_id FROM lot WHERE lot_no = 'WIP-20260104-00001'),
    100;


UPDATE work_order SET status = 'COMPLETED' WHERE work_order_no = 'WO-20260102-0001';

INSERT INTO inspection (lot_id, inspection_type, inspection_date, checked_qty, defect_qty, result)
SELECT lot_id, 'FINISHED', '2026-01-05', 100, 0, 'PASS'
FROM lot WHERE lot_no = 'FG-20260105-00001';


INSERT INTO unit_serial (lot_id, serial_no, status, created_date)
SELECT
    (SELECT lot_id FROM lot WHERE lot_no = 'FG-20260105-00001'),
    'FG-20260105-00001-' || printf('%05d', value),
    'COMPLETED',
    '2026-01-05'
FROM (
    WITH RECURSIVE seq(value) AS (
        SELECT 1
        UNION ALL
        SELECT value + 1 FROM seq WHERE value < 100
    )
    SELECT value FROM seq
);


INSERT INTO shipment (shipment_no, partner_id, shipment_date, status)
SELECT 'SHP-20260106-0001', partner_id, '2026-01-06', 'COMPLETED'
FROM partner WHERE partner_name = '현대파츠';

INSERT INTO shipment_item (shipment_id, lot_id, qty)
SELECT
    (SELECT shipment_id FROM shipment WHERE shipment_no = 'SHP-20260106-0001'),
    (SELECT lot_id FROM lot WHERE lot_no = 'FG-20260105-00001'),
    60;
