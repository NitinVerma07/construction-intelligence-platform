-- SQLite schema for the Construction Intelligence Platform.
-- The backend creates this table automatically on startup (SQLAlchemy create_all);
-- this file documents it and lets you create the database manually:
--   sqlite3 db/construction.db < db/schema.sql

CREATE TABLE IF NOT EXISTS analyses (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    module      VARCHAR(32)  NOT NULL,   -- safety | cracks | valuation | planning | assistant | knowledge | weather
    summary     VARCHAR(255) NOT NULL,
    source      VARCHAR(16)  NOT NULL,   -- llm | mock | fallback
    result_json TEXT         NOT NULL,   -- full validated JSON contract returned to the client
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_analyses_module ON analyses (module);
