-- Shop-management database of demo seed v1 (schema shop, 31 tables).
-- Loads on Postgres 15 with no extension. The database itself carries no comments.

CREATE SCHEMA shop;

CREATE TABLE shop.location (
    location_id   integer PRIMARY KEY,
    name          text NOT NULL UNIQUE,
    address       text NOT NULL,
    phone         text NOT NULL,
    time_zone     text NOT NULL,
    tax_rate      numeric(5,3) NOT NULL CHECK (tax_rate >= 0),
    bays          smallint NOT NULL CHECK (bays > 0),
    latitude      numeric(9,6) NOT NULL,
    longitude     numeric(9,6) NOT NULL,
    opened_on     date NOT NULL
);

CREATE TABLE shop.employee (
    employee_id   integer PRIMARY KEY,
    location_id   integer REFERENCES shop.location,
    first_name    text NOT NULL,
    middle_name   text,
    last_name     text NOT NULL,
    role          text NOT NULL CHECK (role IN ('owner', 'office', 'manager', 'advisor', 'foreman', 'technician', 'parts')),
    title         text NOT NULL,
    pay_type      text NOT NULL CHECK (pay_type IN ('salary', 'hourly', 'flat_rate')),
    hired_on      date NOT NULL,
    left_on       date,
    CHECK (left_on IS NULL OR left_on >= hired_on)
);

CREATE TABLE shop.referral_source (
    referral_source_id integer PRIMARY KEY,
    name               text NOT NULL UNIQUE
);

CREATE TABLE shop.customer (
    customer_id          integer PRIMARY KEY,
    kind                 text NOT NULL CHECK (kind IN ('person', 'company')),
    name                 text NOT NULL,
    phone                text,
    email                text,
    address              text,
    price_class          text NOT NULL DEFAULT 'standard' CHECK (price_class IN ('standard', 'company_account')),
    payment_terms_days   smallint CHECK (payment_terms_days > 0),
    credit_limit         numeric(12,2) CHECK (credit_limit > 0),
    referral_source_id   integer REFERENCES shop.referral_source,
    created_location_id  integer NOT NULL REFERENCES shop.location,
    created_at           timestamp NOT NULL,
    notes                text
);

CREATE TABLE shop.customer_contact (
    customer_contact_id integer PRIMARY KEY,
    customer_id         integer NOT NULL REFERENCES shop.customer,
    name                text NOT NULL,
    role                text NOT NULL,
    phone               text,
    email               text,
    started_on          date NOT NULL,
    ended_on            date,
    CHECK (ended_on IS NULL OR ended_on >= started_on)
);

CREATE TABLE shop.vehicle (
    vehicle_id     integer PRIMARY KEY,
    customer_id    integer NOT NULL REFERENCES shop.customer,
    vin            text CHECK (vin IS NULL OR length(vin) = 17),
    plate          text,
    year           smallint NOT NULL CHECK (year BETWEEN 1950 AND 2100),
    make           text NOT NULL,
    model          text NOT NULL,
    engine         text,
    vehicle_class  text NOT NULL CHECK (vehicle_class IN ('car', 'suv', 'truck', 'van')),
    unit_number    text
);

CREATE TABLE shop.service_category (
    service_category_id integer PRIMARY KEY,
    code                text NOT NULL UNIQUE,
    name                text NOT NULL
);

CREATE TABLE shop.canned_job (
    canned_job_id        integer PRIMARY KEY,
    code                 text NOT NULL UNIQUE,
    service_category_id  integer NOT NULL REFERENCES shop.service_category,
    name                 text NOT NULL,
    hours                numeric(5,2) NOT NULL CHECK (hours >= 0),
    labor_pricing        text NOT NULL CHECK (labor_pricing IN ('hourly', 'menu')),
    menu_price           numeric(12,2),
    CHECK ((labor_pricing = 'menu') = (menu_price IS NOT NULL))
);

CREATE TABLE shop.labor_rate (
    labor_rate_id  integer PRIMARY KEY,
    location_id    integer NOT NULL REFERENCES shop.location,
    price_class    text NOT NULL CHECK (price_class IN ('standard', 'company_account')),
    rate           numeric(10,2) NOT NULL CHECK (rate > 0),
    valid_from     date NOT NULL,
    valid_to       date,
    UNIQUE (location_id, price_class, valid_from),
    CHECK (valid_to IS NULL OR valid_to >= valid_from)
);

CREATE TABLE shop.vendor (
    vendor_id           integer PRIMARY KEY,
    name                text NOT NULL UNIQUE,
    kind                text NOT NULL CHECK (kind IN ('parts', 'sublet')),
    payment_terms_days  smallint NOT NULL CHECK (payment_terms_days > 0),
    phone               text NOT NULL,
    email               text
);

CREATE TABLE shop.part (
    part_id      integer PRIMARY KEY,
    part_number  text,
    brand        text NOT NULL,
    description  text NOT NULL,
    unit         text NOT NULL,
    cost         numeric(12,2) NOT NULL CHECK (cost >= 0),
    list_price   numeric(12,2) NOT NULL CHECK (list_price >= 0)
);
CREATE UNIQUE INDEX part_brand_number_key ON shop.part (brand, part_number) WHERE part_number IS NOT NULL;

CREATE TABLE shop.statement (
    statement_id  integer PRIMARY KEY,
    customer_id   integer NOT NULL REFERENCES shop.customer,
    number        text NOT NULL UNIQUE,
    issued_on     date NOT NULL,
    due_on        date NOT NULL,
    total         numeric(12,2) NOT NULL CHECK (total >= 0),
    status        text NOT NULL CHECK (status IN ('open', 'sent', 'paid', 'overdue')),
    dispute_note  text,
    CHECK (due_on >= issued_on)
);

CREATE TABLE shop.repair_order (
    repair_order_id          integer PRIMARY KEY,
    number                   text NOT NULL UNIQUE,
    location_id              integer NOT NULL REFERENCES shop.location,
    customer_id              integer NOT NULL REFERENCES shop.customer,
    vehicle_id               integer NOT NULL REFERENCES shop.vehicle,
    advisor_id               integer NOT NULL REFERENCES shop.employee,
    order_type               text NOT NULL CHECK (order_type IN ('customer_pay', 'warranty', 'goodwill', 'internal')),
    status                   text NOT NULL CHECK (status IN ('estimate', 'approved', 'in_progress', 'waiting_parts', 'waiting_sublet', 'completed', 'invoiced', 'paid', 'declined', 'void')),
    comeback_of_id           integer REFERENCES shop.repair_order,
    opened_at                timestamp NOT NULL,
    promised_at              timestamp,
    mileage_in               integer CHECK (mileage_in >= 0),
    mileage_out              integer CHECK (mileage_out >= 0),
    complaint                text,
    purchase_order_number    text,
    labor_total              numeric(12,2) NOT NULL DEFAULT 0,
    parts_total              numeric(12,2) NOT NULL DEFAULT 0,
    sublet_total             numeric(12,2) NOT NULL DEFAULT 0,
    fees_total               numeric(12,2) NOT NULL DEFAULT 0,
    discount_total           numeric(12,2) NOT NULL DEFAULT 0 CHECK (discount_total >= 0),
    tax_rate                 numeric(5,3) NOT NULL CHECK (tax_rate >= 0),
    tax_included             boolean NOT NULL,
    tax_total                numeric(12,2) NOT NULL DEFAULT 0 CHECK (tax_total >= 0),
    total                    numeric(12,2) NOT NULL DEFAULT 0,
    discount_reason          text,
    discount_approved_by_id  integer REFERENCES shop.employee,
    statement_id             integer REFERENCES shop.statement,
    voided_at                timestamp,
    voided_by_id             integer REFERENCES shop.employee,
    void_reason              text,
    CHECK (comeback_of_id IS NULL OR order_type IN ('warranty', 'goodwill')),
    CHECK (comeback_of_id IS NULL OR comeback_of_id <> repair_order_id),
    CHECK ((status = 'void') = (voided_at IS NOT NULL)),
    CHECK (voided_at IS NOT NULL OR (voided_by_id IS NULL AND void_reason IS NULL)),
    CHECK (discount_approved_by_id IS NULL OR discount_total > 0)
);

CREATE TABLE shop.order_status_history (
    order_status_history_id  integer PRIMARY KEY,
    repair_order_id          integer NOT NULL REFERENCES shop.repair_order,
    status                   text NOT NULL CHECK (status IN ('estimate', 'approved', 'in_progress', 'waiting_parts', 'waiting_sublet', 'completed', 'invoiced', 'paid', 'declined', 'void')),
    changed_at               timestamp NOT NULL
);

CREATE TABLE shop.order_job (
    order_job_id     integer PRIMARY KEY,
    repair_order_id  integer NOT NULL REFERENCES shop.repair_order,
    canned_job_id    integer NOT NULL REFERENCES shop.canned_job,
    description      text NOT NULL,
    status           text NOT NULL CHECK (status IN ('pending', 'approved', 'declined')),
    approval_method  text CHECK (approval_method IN ('counter', 'phone', 'link', 'message')),
    decided_at       timestamp,
    authorized_by    text,
    approved_amount  numeric(12,2),
    deferred         boolean NOT NULL DEFAULT false,
    CHECK ((status = 'pending') = (decided_at IS NULL)),
    CHECK (status <> 'pending' OR approval_method IS NULL),
    CHECK (NOT deferred OR status = 'declined'),
    CHECK (approved_amount IS NULL OR status = 'approved')
);

CREATE TABLE shop.order_labor (
    order_labor_id  integer PRIMARY KEY,
    order_job_id    integer NOT NULL REFERENCES shop.order_job,
    technician_id   integer REFERENCES shop.employee,
    hours           numeric(5,2) NOT NULL CHECK (hours > 0),
    rate            numeric(10,2) NOT NULL CHECK (rate >= 0),
    amount          numeric(12,2) NOT NULL CHECK (amount >= 0),
    discount        numeric(12,2) NOT NULL DEFAULT 0 CHECK (discount >= 0 AND discount <= amount)
);

CREATE TABLE shop.order_part (
    order_part_id  integer PRIMARY KEY,
    order_job_id   integer NOT NULL REFERENCES shop.order_job,
    part_id        integer REFERENCES shop.part,
    description    text NOT NULL,
    brand          text,
    quantity       numeric(8,2) NOT NULL CHECK (quantity > 0),
    unit_cost      numeric(12,2) NOT NULL CHECK (unit_cost >= 0),
    unit_price     numeric(12,2) NOT NULL CHECK (unit_price >= 0),
    vendor_id      integer REFERENCES shop.vendor
);

CREATE TABLE shop.order_sublet (
    order_sublet_id  integer PRIMARY KEY,
    order_job_id     integer NOT NULL REFERENCES shop.order_job,
    vendor_id        integer NOT NULL REFERENCES shop.vendor,
    description      text NOT NULL,
    cost             numeric(12,2) NOT NULL CHECK (cost >= 0),
    price            numeric(12,2) NOT NULL CHECK (price >= 0)
);

CREATE TABLE shop.order_fee (
    order_fee_id     integer PRIMARY KEY,
    repair_order_id  integer NOT NULL REFERENCES shop.repair_order,
    kind             text NOT NULL CHECK (kind IN ('shop_supplies', 'tyre_disposal', 'tyre_storage')),
    description      text NOT NULL,
    amount           numeric(12,2) NOT NULL CHECK (amount >= 0)
);

CREATE TABLE shop.inspection (
    inspection_id    integer PRIMARY KEY,
    repair_order_id  integer NOT NULL UNIQUE REFERENCES shop.repair_order,
    technician_id    integer NOT NULL REFERENCES shop.employee,
    completed_at     timestamp NOT NULL
);

CREATE TABLE shop.inspection_item (
    inspection_item_id  integer PRIMARY KEY,
    inspection_id       integer NOT NULL REFERENCES shop.inspection,
    component           text NOT NULL,
    result              text NOT NULL CHECK (result IN ('good', 'watch', 'bad')),
    measurement         text,
    has_photo           boolean NOT NULL DEFAULT false,
    order_job_id        integer UNIQUE REFERENCES shop.order_job,
    CHECK (order_job_id IS NULL OR result <> 'good')
);

CREATE TABLE shop.time_entry (
    time_entry_id  integer PRIMARY KEY,
    technician_id  integer NOT NULL REFERENCES shop.employee,
    order_job_id   integer NOT NULL REFERENCES shop.order_job,
    clock_in       timestamp NOT NULL,
    clock_out      timestamp,
    CHECK (clock_out IS NULL OR clock_out > clock_in)
);

CREATE TABLE shop.appointment (
    appointment_id   integer PRIMARY KEY,
    location_id      integer NOT NULL REFERENCES shop.location,
    customer_id      integer REFERENCES shop.customer,
    vehicle_id       integer REFERENCES shop.vehicle,
    contact_name     text,
    contact_phone    text,
    starts_at        timestamp NOT NULL,
    duration_min     smallint NOT NULL CHECK (duration_min > 0),
    source           text NOT NULL CHECK (source IN ('phone', 'web_chat', 'messenger', 'walk_in')),
    status           text NOT NULL CHECK (status IN ('booked', 'confirmed', 'arrived', 'no_show', 'cancelled')),
    reason           text,
    booked_at        timestamp NOT NULL,
    booked_by_id     integer REFERENCES shop.employee,
    repair_order_id  integer UNIQUE REFERENCES shop.repair_order,
    CHECK (customer_id IS NOT NULL OR contact_phone IS NOT NULL),
    CHECK (repair_order_id IS NULL OR status = 'arrived')
);

CREATE TABLE shop.payment (
    payment_id       integer PRIMARY KEY,
    repair_order_id  integer REFERENCES shop.repair_order,
    statement_id     integer REFERENCES shop.statement,
    kind             text NOT NULL CHECK (kind IN ('payment', 'deposit', 'refund')),
    method           text NOT NULL CHECK (method IN ('cash', 'card', 'check', 'bank_transfer', 'fast_payment')),
    amount           numeric(12,2) NOT NULL CHECK (amount > 0),
    received_at      timestamp NOT NULL,
    taken_by_id      integer REFERENCES shop.employee,
    reference        text,
    CHECK ((repair_order_id IS NULL) <> (statement_id IS NULL)),
    CHECK (kind <> 'deposit' OR repair_order_id IS NOT NULL)
);

CREATE TABLE shop.cash_drawer_close (
    cash_drawer_close_id  integer PRIMARY KEY,
    location_id           integer NOT NULL REFERENCES shop.location,
    business_date         date NOT NULL,
    closed_by_id          integer NOT NULL REFERENCES shop.employee,
    second_counter_id     integer REFERENCES shop.employee,
    float_amount          numeric(12,2) NOT NULL CHECK (float_amount >= 0),
    expected_cash         numeric(12,2) NOT NULL,
    counted_cash          numeric(12,2) NOT NULL,
    difference            numeric(12,2) NOT NULL,
    note                  text,
    UNIQUE (location_id, business_date),
    CHECK (difference = counted_cash - expected_cash)
);

CREATE TABLE shop.purchase_order (
    purchase_order_id  integer PRIMARY KEY,
    number             text NOT NULL UNIQUE,
    location_id        integer NOT NULL REFERENCES shop.location,
    vendor_id          integer NOT NULL REFERENCES shop.vendor,
    repair_order_id    integer REFERENCES shop.repair_order,
    status             text NOT NULL CHECK (status IN ('ordered', 'partial', 'received', 'cancelled')),
    ordered_at         timestamp NOT NULL,
    promised_at        timestamp NOT NULL,
    received_at        timestamp,
    CHECK ((status = 'received') = (received_at IS NOT NULL)),
    CHECK (promised_at >= ordered_at)
);

CREATE TABLE shop.purchase_order_line (
    purchase_order_line_id  integer PRIMARY KEY,
    purchase_order_id       integer NOT NULL REFERENCES shop.purchase_order,
    part_id                 integer REFERENCES shop.part,
    description             text NOT NULL,
    quantity_ordered        numeric(8,2) NOT NULL CHECK (quantity_ordered > 0),
    quantity_received       numeric(8,2) NOT NULL DEFAULT 0 CHECK (quantity_received >= 0),
    unit_cost               numeric(12,2) NOT NULL CHECK (unit_cost >= 0)
);

CREATE TABLE shop.stock_level (
    stock_level_id    integer PRIMARY KEY,
    location_id       integer NOT NULL REFERENCES shop.location,
    part_id           integer NOT NULL REFERENCES shop.part,
    quantity_on_hand  numeric(10,2) NOT NULL,
    UNIQUE (location_id, part_id)
);

CREATE TABLE shop.part_return (
    part_return_id          integer PRIMARY KEY,
    purchase_order_line_id  integer NOT NULL REFERENCES shop.purchase_order_line,
    quantity                numeric(8,2) NOT NULL CHECK (quantity > 0),
    amount                  numeric(12,2) NOT NULL CHECK (amount >= 0),
    reason                  text NOT NULL,
    returned_on             date NOT NULL,
    status                  text NOT NULL CHECK (status IN ('sent', 'credited', 'rejected')),
    credited_on             date,
    CHECK ((status = 'credited') = (credited_on IS NOT NULL))
);

CREATE TABLE shop.stock_movement (
    stock_movement_id       integer PRIMARY KEY,
    location_id             integer NOT NULL REFERENCES shop.location,
    part_id                 integer NOT NULL REFERENCES shop.part,
    kind                    text NOT NULL CHECK (kind IN ('receipt', 'issue', 'transfer_in', 'transfer_out', 'vendor_return', 'adjustment')),
    quantity                numeric(10,2) NOT NULL CHECK (quantity <> 0),
    unit_cost               numeric(12,2) NOT NULL CHECK (unit_cost >= 0),
    moved_at                timestamp NOT NULL,
    employee_id             integer REFERENCES shop.employee,
    order_part_id           integer REFERENCES shop.order_part,
    purchase_order_line_id  integer REFERENCES shop.purchase_order_line,
    part_return_id          integer REFERENCES shop.part_return,
    note                    text,
    CHECK (kind <> 'receipt' OR quantity > 0),
    CHECK (kind NOT IN ('issue', 'transfer_out', 'vendor_return') OR quantity < 0),
    CHECK (order_part_id IS NULL OR kind = 'issue'),
    CHECK (part_return_id IS NULL OR kind = 'vendor_return')
);

CREATE TABLE shop.service_reminder (
    service_reminder_id   integer PRIMARY KEY,
    customer_id           integer NOT NULL REFERENCES shop.customer,
    vehicle_id            integer NOT NULL REFERENCES shop.vehicle,
    order_job_id          integer REFERENCES shop.order_job,
    kind                  text NOT NULL CHECK (kind IN ('deferred_work', 'maintenance_due')),
    description           text NOT NULL,
    due_on                date,
    due_mileage           integer,
    status                text NOT NULL CHECK (status IN ('pending', 'sent', 'done', 'dismissed')),
    sent_on               date,
    done_repair_order_id  integer REFERENCES shop.repair_order,
    created_on            date NOT NULL,
    CHECK ((kind = 'deferred_work') = (order_job_id IS NOT NULL)),
    CHECK (due_on IS NOT NULL OR due_mileage IS NOT NULL),
    CHECK ((status = 'done') = (done_repair_order_id IS NOT NULL))
);

CREATE INDEX employee_location_idx ON shop.employee (location_id);
CREATE INDEX customer_phone_idx ON shop.customer (phone);
CREATE INDEX customer_name_idx ON shop.customer (lower(name));
CREATE INDEX customer_created_idx ON shop.customer (created_location_id, created_at);
CREATE INDEX customer_contact_customer_idx ON shop.customer_contact (customer_id);
CREATE INDEX customer_contact_phone_idx ON shop.customer_contact (phone);
CREATE INDEX vehicle_customer_idx ON shop.vehicle (customer_id);
CREATE INDEX vehicle_vin_idx ON shop.vehicle (vin);
CREATE INDEX vehicle_plate_idx ON shop.vehicle (plate);
CREATE INDEX canned_job_category_idx ON shop.canned_job (service_category_id);
CREATE INDEX part_number_idx ON shop.part (part_number);
CREATE INDEX statement_customer_idx ON shop.statement (customer_id, issued_on);
CREATE INDEX repair_order_location_opened_idx ON shop.repair_order (location_id, opened_at);
CREATE INDEX repair_order_customer_idx ON shop.repair_order (customer_id);
CREATE INDEX repair_order_vehicle_idx ON shop.repair_order (vehicle_id, opened_at);
CREATE INDEX repair_order_advisor_idx ON shop.repair_order (advisor_id, opened_at);
CREATE INDEX repair_order_status_idx ON shop.repair_order (status);
CREATE INDEX repair_order_comeback_idx ON shop.repair_order (comeback_of_id) WHERE comeback_of_id IS NOT NULL;
CREATE INDEX repair_order_statement_idx ON shop.repair_order (statement_id) WHERE statement_id IS NOT NULL;
CREATE INDEX order_status_history_order_idx ON shop.order_status_history (repair_order_id, changed_at);
CREATE INDEX order_status_history_status_idx ON shop.order_status_history (status, changed_at);
CREATE INDEX order_job_order_idx ON shop.order_job (repair_order_id);
CREATE INDEX order_job_canned_idx ON shop.order_job (canned_job_id);
CREATE INDEX order_labor_job_idx ON shop.order_labor (order_job_id);
CREATE INDEX order_labor_technician_idx ON shop.order_labor (technician_id);
CREATE INDEX order_part_job_idx ON shop.order_part (order_job_id);
CREATE INDEX order_part_part_idx ON shop.order_part (part_id);
CREATE INDEX order_sublet_job_idx ON shop.order_sublet (order_job_id);
CREATE INDEX order_fee_order_idx ON shop.order_fee (repair_order_id);
CREATE INDEX inspection_item_inspection_idx ON shop.inspection_item (inspection_id);
CREATE INDEX time_entry_job_idx ON shop.time_entry (order_job_id);
CREATE INDEX time_entry_technician_idx ON shop.time_entry (technician_id, clock_in);
CREATE INDEX appointment_location_starts_idx ON shop.appointment (location_id, starts_at);
CREATE INDEX appointment_customer_idx ON shop.appointment (customer_id);
CREATE INDEX payment_order_idx ON shop.payment (repair_order_id);
CREATE INDEX payment_statement_idx ON shop.payment (statement_id);
CREATE INDEX payment_received_idx ON shop.payment (received_at);
CREATE INDEX purchase_order_vendor_idx ON shop.purchase_order (vendor_id, ordered_at);
CREATE INDEX purchase_order_order_idx ON shop.purchase_order (repair_order_id) WHERE repair_order_id IS NOT NULL;
CREATE INDEX purchase_order_line_po_idx ON shop.purchase_order_line (purchase_order_id);
CREATE INDEX stock_movement_part_idx ON shop.stock_movement (location_id, part_id, moved_at);
CREATE INDEX stock_movement_order_part_idx ON shop.stock_movement (order_part_id) WHERE order_part_id IS NOT NULL;
CREATE INDEX part_return_line_idx ON shop.part_return (purchase_order_line_id);
CREATE INDEX service_reminder_vehicle_idx ON shop.service_reminder (vehicle_id);
CREATE INDEX service_reminder_status_idx ON shop.service_reminder (status, due_on);
