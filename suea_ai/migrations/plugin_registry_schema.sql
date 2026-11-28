-- Plugin Registry Schema — รองรับ 10,000 entries
CREATE TABLE IF NOT EXISTS plugin_registry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plugin_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    category TEXT DEFAULT 'general',
    provider TEXT DEFAULT 'unknown',
    status TEXT DEFAULT 'REGISTERED',
    version TEXT DEFAULT '1.0',
    capabilities TEXT DEFAULT '[]',
    requires_auth INTEGER DEFAULT 0,
    risk_level TEXT DEFAULT 'R1',
    registered_at TEXT NOT NULL,
    updated_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_plugin_category ON plugin_registry(category);
CREATE INDEX IF NOT EXISTS idx_plugin_status ON plugin_registry(status);
CREATE INDEX IF NOT EXISTS idx_plugin_provider ON plugin_registry(provider);

-- Recovery Log
CREATE TABLE IF NOT EXISTS recovery_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module TEXT NOT NULL,
    error TEXT,
    severity TEXT DEFAULT 'medium',
    status TEXT DEFAULT 'IN_PROGRESS',
    attempts INTEGER DEFAULT 1,
    started_at TEXT,
    completed_at TEXT
);

-- ACK Command Log
CREATE TABLE IF NOT EXISTS ack_commands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    command_id TEXT UNIQUE NOT NULL,
    target TEXT NOT NULL,
    action TEXT NOT NULL,
    status TEXT DEFAULT 'PENDING',
    acked_by TEXT,
    evidence TEXT,
    sent_at TEXT,
    acked_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_ack_status ON ack_commands(status);

-- Lockdown History
CREATE TABLE IF NOT EXISTS lockdown_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT NOT NULL,
    reason TEXT,
    triggered_by TEXT DEFAULT 'system',
    timestamp TEXT NOT NULL
);
