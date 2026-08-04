CREATE TABLE item (
    item_id INTEGER PRIMARY KEY,
    item_code TEXT NOT NULL UNIQUE,
    item_name TEXT NOT NULL,
    item_type TEXT NOT NULL CHECK (item_type IN ('PRODUCT', 'SEMI_PRODUCT', 'MATERIAL')),
    unit TEXT NOT NULL,
    is_active TEXT NOT NULL DEFAULT 'Y' CHECK (is_active IN ('Y', 'N'))
);


CREATE TABLE item_spec (
    item_spec_id INTEGER PRIMARY KEY,
    item_id INTEGER NOT NULL UNIQUE,
    drawing_no TEXT,
    drawing_rev TEXT,
    material_spec TEXT,
    tolerance_note TEXT,
    FOREIGN KEY (item_id) REFERENCES item (item_id)
);


CREATE TABLE partner (
    partner_id INTEGER PRIMARY KEY,
    partner_name TEXT NOT NULL,
    partner_type TEXT NOT NULL CHECK (partner_type IN ('SUPPLIER', 'CUSTOMER')),
    contact TEXT
);


CREATE TABLE process_master (
    process_code TEXT PRIMARY KEY,
    process_name TEXT NOT NULL
);


CREATE TABLE equipment (
    equipment_id INTEGER PRIMARY KEY,
    equipment_code TEXT NOT NULL UNIQUE,
    equipment_name TEXT NOT NULL,
    process_code TEXT NOT NULL,
    is_active TEXT NOT NULL DEFAULT 'Y' CHECK (is_active IN ('Y', 'N')),
    FOREIGN KEY (process_code) REFERENCES process_master (process_code)
);

CREATE TABLE user (
    user_id TEXT PRIMARY KEY,
    user_name TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('ADMIN', 'OPERATOR', 'INSPECTOR')),
    is_active TEXT NOT NULL DEFAULT 'Y' CHECK (is_active IN ('Y', 'N'))
);

CREATE TABLE defect_reason_code (
    reason_code TEXT PRIMARY KEY,
    reason_name TEXT NOT NULL,
    is_active TEXT NOT NULL DEFAULT 'Y' CHECK (is_active IN ('Y', 'N'))
);


CREATE TABLE routing (
    routing_id INTEGER PRIMARY KEY,
    product_item_id INTEGER NOT NULL UNIQUE,
    routing_name TEXT NOT NULL,
    is_active TEXT NOT NULL DEFAULT 'Y' CHECK (is_active IN ('Y', 'N')),
    FOREIGN KEY (product_item_id) REFERENCES item (item_id)
);


CREATE TABLE routing_step (
    routing_step_id INTEGER PRIMARY KEY,
    routing_id INTEGER NOT NULL,
    step_no INTEGER NOT NULL,
    process_code TEXT NOT NULL,
    output_item_id INTEGER NOT NULL,
    UNIQUE (routing_id, step_no),
    FOREIGN KEY (routing_id) REFERENCES routing (routing_id),
    FOREIGN KEY (process_code) REFERENCES process_master (process_code),
    FOREIGN KEY (output_item_id) REFERENCES item (item_id)
);


CREATE TABLE bom (
    bom_id INTEGER PRIMARY KEY,
    routing_step_id INTEGER NOT NULL,
    material_item_id INTEGER NOT NULL,
    qty_per_unit REAL NOT NULL CHECK (qty_per_unit > 0),
    UNIQUE (routing_step_id, material_item_id),
    FOREIGN KEY (routing_step_id) REFERENCES routing_step (routing_step_id),
    FOREIGN KEY (material_item_id) REFERENCES item (item_id)
);

CREATE TABLE lot (
    lot_id INTEGER PRIMARY KEY,
    lot_no TEXT NOT NULL UNIQUE,
    item_id INTEGER NOT NULL,
    lot_type TEXT NOT NULL CHECK (lot_type IN ('RECEIPT', 'WIP', 'FINISHED')),
    qty REAL NOT NULL CHECK (qty >= 0),
    received_date TEXT,
    produced_date TEXT,
    expire_date TEXT,
    partner_id INTEGER,
    FOREIGN KEY (item_id) REFERENCES item (item_id),
    FOREIGN KEY (partner_id) REFERENCES partner (partner_id)
);


CREATE TABLE unit_serial (
    unit_serial_id INTEGER PRIMARY KEY,
    lot_id INTEGER NOT NULL,
    serial_no TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL CHECK (status IN ('IN_PROCESS', 'COMPLETED', 'SCRAPPED')) DEFAULT 'IN_PROCESS',
    created_date TEXT NOT NULL,
    FOREIGN KEY (lot_id) REFERENCES lot (lot_id)
);

CREATE TABLE work_order (
    work_order_id INTEGER PRIMARY KEY,
    work_order_no TEXT NOT NULL UNIQUE,
    product_item_id INTEGER NOT NULL,
    routing_id INTEGER NOT NULL,
    planned_qty REAL NOT NULL CHECK (planned_qty > 0),
    plan_date TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('PLANNED', 'IN_PROGRESS', 'COMPLETED', 'CANCELED')) DEFAULT 'PLANNED',
    FOREIGN KEY (product_item_id) REFERENCES item (item_id),
    FOREIGN KEY (routing_id) REFERENCES routing (routing_id)
);


CREATE TABLE operation (
    operation_id INTEGER PRIMARY KEY,
    work_order_id INTEGER NOT NULL,
    routing_step_id INTEGER NOT NULL,
    equipment_id INTEGER,
    operation_date TEXT NOT NULL,
    qty REAL NOT NULL CHECK (qty > 0),
    output_lot_id INTEGER NOT NULL UNIQUE,
    status TEXT NOT NULL CHECK (status IN ('COMPLETED', 'CANCELED')) DEFAULT 'COMPLETED',
    FOREIGN KEY (work_order_id) REFERENCES work_order (work_order_id),
    FOREIGN KEY (routing_step_id) REFERENCES routing_step (routing_step_id),
    FOREIGN KEY (equipment_id) REFERENCES equipment (equipment_id),
    FOREIGN KEY (output_lot_id) REFERENCES lot (lot_id)
);


CREATE TABLE operation_material (
    operation_material_id INTEGER PRIMARY KEY,
    operation_id INTEGER NOT NULL,
    material_item_id INTEGER NOT NULL,
    material_lot_id INTEGER NOT NULL,
    qty REAL NOT NULL CHECK (qty > 0),
    FOREIGN KEY (operation_id) REFERENCES operation (operation_id),
    FOREIGN KEY (material_item_id) REFERENCES item (item_id),
    FOREIGN KEY (material_lot_id) REFERENCES lot (lot_id)
);


CREATE TABLE inspection (
    inspection_id INTEGER PRIMARY KEY,
    lot_id INTEGER NOT NULL UNIQUE,
    inspection_type TEXT NOT NULL CHECK (inspection_type IN ('RECEIPT', 'WIP', 'FINISHED')),
    inspection_date TEXT NOT NULL,
    checked_qty REAL NOT NULL CHECK (checked_qty >= 0),
    defect_qty REAL NOT NULL DEFAULT 0 CHECK (defect_qty >= 0),
    result TEXT NOT NULL CHECK (result IN ('PASS', 'FAIL', 'PARTIAL')),
    reason_code TEXT REFERENCES defect_reason_code (reason_code),
    defect_reason TEXT,
    FOREIGN KEY (lot_id) REFERENCES lot (lot_id)
);


CREATE TABLE shipment (
    shipment_id INTEGER PRIMARY KEY,
    shipment_no TEXT NOT NULL UNIQUE,
    partner_id INTEGER,
    shipment_date TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('COMPLETED', 'CANCELED')) DEFAULT 'COMPLETED',
    FOREIGN KEY (partner_id) REFERENCES partner (partner_id)
);

CREATE TABLE shipment_item (
    shipment_item_id INTEGER PRIMARY KEY,
    shipment_id INTEGER NOT NULL,
    lot_id INTEGER NOT NULL,
    qty REAL NOT NULL CHECK (qty > 0),
    FOREIGN KEY (shipment_id) REFERENCES shipment (shipment_id),
    FOREIGN KEY (lot_id) REFERENCES lot (lot_id)
);
