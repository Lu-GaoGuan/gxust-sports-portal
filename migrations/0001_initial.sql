CREATE TABLE department_profile (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    introduction TEXT NOT NULL DEFAULT '',
    welcome_slogan TEXT NOT NULL DEFAULT '',
    recruitment_info TEXT NOT NULL DEFAULT '',
    contact_info TEXT NOT NULL DEFAULT '',
    qq_group_qr_code TEXT,
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE TABLE members (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    major_class TEXT NOT NULL DEFAULT '',
    position TEXT NOT NULL,
    generation INTEGER NOT NULL CHECK (generation >= 1),
    tenure TEXT NOT NULL DEFAULT '',
    introduction TEXT NOT NULL DEFAULT '',
    welcome_message TEXT NOT NULL DEFAULT '',
    photo TEXT,
    sort_order INTEGER NOT NULL DEFAULT 0,
    is_visible INTEGER NOT NULL DEFAULT 1 CHECK (is_visible IN (0, 1)),
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX members_visible_sort_idx
ON members (is_visible, sort_order, generation, id);

CREATE TABLE activities (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    category_label TEXT NOT NULL,
    activity_date TEXT,
    introduction TEXT NOT NULL DEFAULT '',
    cover TEXT,
    sort_order INTEGER NOT NULL DEFAULT 0,
    is_visible INTEGER NOT NULL DEFAULT 1 CHECK (is_visible IN (0, 1)),
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX activities_visible_sort_idx
ON activities (is_visible, sort_order, activity_date, id);

CREATE TABLE activity_media (
    id INTEGER PRIMARY KEY,
    activity_id INTEGER NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
    file TEXT NOT NULL,
    media_type TEXT NOT NULL CHECK (media_type IN ('image', 'video')),
    description TEXT NOT NULL DEFAULT '',
    width INTEGER,
    height INTEGER,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX activity_media_sort_idx
ON activity_media (activity_id, sort_order, id);

CREATE TABLE faqs (
    id INTEGER PRIMARY KEY,
    question TEXT NOT NULL UNIQUE,
    answer TEXT NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0,
    is_visible INTEGER NOT NULL DEFAULT 1 CHECK (is_visible IN (0, 1)),
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX faqs_visible_sort_idx
ON faqs (is_visible, sort_order, id);

CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nickname TEXT NOT NULL CHECK (length(nickname) BETWEEN 1 AND 50),
    content TEXT NOT NULL CHECK (length(content) BETWEEN 2 AND 1000),
    review_status TEXT NOT NULL DEFAULT 'pending'
        CHECK (review_status IN ('pending', 'approved', 'rejected')),
    submitted_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    reviewed_at TEXT,
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    deleted_at TEXT
);

CREATE INDEX messages_public_idx
ON messages (review_status, is_deleted, submitted_at DESC, id DESC);

CREATE TABLE message_review_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id INTEGER NOT NULL REFERENCES messages(id),
    action TEXT NOT NULL,
    note TEXT NOT NULL DEFAULT '',
    operated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX message_review_log_message_idx
ON message_review_log (message_id, operated_at DESC);

CREATE TABLE message_rate_limits (
    client_key TEXT PRIMARY KEY,
    window_started_at INTEGER NOT NULL,
    request_count INTEGER NOT NULL DEFAULT 0
);
