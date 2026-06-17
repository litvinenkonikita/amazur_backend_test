CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- DO $$
-- BEGIN
--     IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'campaign_status') THEN
--         CREATE TYPE campaign_status AS ENUM ('active', 'paused');
--     END IF;
-- END $$;

-- CREATE TABLE IF NOT EXISTS campaigns (
--     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
--     name VARCHAR(255) NOT NULL,
--     current_status campaign_status NOT NULL DEFAULT 'active',
--     target_status campaign_status NOT NULL DEFAULT 'active',
--     is_managed BOOLEAN NOT NULL DEFAULT TRUE,
--     budget_limit NUMERIC(12, 2),
--     spend_today NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
--     stock_days_left INTEGER,
--     stock_days_min INTEGER,
--     schedule_enabled BOOLEAN NOT NULL DEFAULT FALSE,
--     created_at TIMESTAMP NOT NULL DEFAULT NOW(),
--     updated_at TIMESTAMP NOT NULL DEFAULT NOW()
-- );

-- CREATE TABLE IF NOT EXISTS campaign_schedules (
--     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
--     campaign_id UUID NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
--     day_of_week INTEGER NOT NULL CHECK (day_of_week BETWEEN 0 AND 6),
--     start_time TIME NOT NULL,
--     end_time TIME NOT NULL,
--     CONSTRAINT ck_campaign_schedules_time_range CHECK (end_time > start_time)
-- );

-- CREATE INDEX IF NOT EXISTS ix_campaign_schedules_campaign_id
--     ON campaign_schedules (campaign_id);

-- CREATE TABLE IF NOT EXISTS rule_evaluation_logs (
--     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
--     campaign_id UUID NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
--     triggered_rule VARCHAR(64),
--     previous_target campaign_status NOT NULL,
--     new_target campaign_status NOT NULL,
--     context JSONB NOT NULL,
--     created_at TIMESTAMP NOT NULL DEFAULT NOW()
-- );

-- CREATE INDEX IF NOT EXISTS ix_rule_evaluation_logs_campaign_id
--     ON rule_evaluation_logs (campaign_id);
