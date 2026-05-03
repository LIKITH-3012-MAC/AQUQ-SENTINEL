import logging
from sqlalchemy import text
from .database import engine

logger = logging.getLogger(__name__)

def fix_database_schema():
    """
    Ensures that the database schema matches the models by adding missing columns.
    This is a lightweight migration tool for AquaSentinel.
    """
    logger.info("[DB-FIX] Starting schema verification...")
    
    commands = [
        # Marine Reports fixes
        "ALTER TABLE marine_reports ADD COLUMN IF NOT EXISTS is_simulated BOOLEAN DEFAULT FALSE",
        "ALTER TABLE marine_reports ADD COLUMN IF NOT EXISTS simulation_id UUID",
        
        # Alerts fixes
        "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS target_scope VARCHAR DEFAULT 'global'",
        "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS verified_by_admin BOOLEAN DEFAULT FALSE",
        "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS is_simulated BOOLEAN DEFAULT FALSE",
        "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS simulation_id UUID",
        "ALTER TABLE alerts ADD COLUMN IF NOT EXISTS related_scenario_id UUID",
        
        # Missions fixes (checking for simulated fields)
        "ALTER TABLE missions ADD COLUMN IF NOT EXISTS is_simulated BOOLEAN DEFAULT FALSE",
        "ALTER TABLE missions ADD COLUMN IF NOT EXISTS simulation_id UUID",
        
        # Risk Scores fixes
        "ALTER TABLE risk_scores ADD COLUMN IF NOT EXISTS is_simulated BOOLEAN DEFAULT FALSE",
        "ALTER TABLE risk_scores ADD COLUMN IF NOT EXISTS simulation_id UUID",

        # User Profile Images fixes
        "ALTER TABLE user_profile_images ADD COLUMN IF NOT EXISTS binary_data BYTEA",
        "ALTER TABLE user_profile_images ALTER COLUMN binary_data TYPE BYTEA USING binary_data::bytea", # Ensure type is bytea
        
        # Simulated Incidents fixes (Ensuring all mission-critical fields exist)
        "ALTER TABLE simulated_incidents ADD COLUMN IF NOT EXISTS message_title VARCHAR",
        "ALTER TABLE simulated_incidents ADD COLUMN IF NOT EXISTS message_body TEXT",
        "ALTER TABLE simulated_incidents ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE",
        "ALTER TABLE simulated_incidents ADD COLUMN IF NOT EXISTS health_impact_enabled BOOLEAN DEFAULT TRUE",
        "ALTER TABLE simulated_incidents ADD COLUMN IF NOT EXISTS alert_broadcast_enabled BOOLEAN DEFAULT TRUE",
        "ALTER TABLE simulated_incidents ADD COLUMN IF NOT EXISTS mission_flow_enabled BOOLEAN DEFAULT TRUE",
        "ALTER TABLE simulated_incidents ADD COLUMN IF NOT EXISTS judge_note TEXT",
        "ALTER TABLE simulated_incidents ADD COLUMN IF NOT EXISTS expires_at TIMESTAMP WITH TIME ZONE",
    ]
    
    with engine.connect() as conn:
        for cmd in commands:
            try:
                conn.execute(text(cmd))
                conn.commit()
                logger.info(f"[DB-FIX] Executed: {cmd}")
            except Exception as e:
                logger.error(f"[DB-FIX] Failed to execute {cmd}: {e}")
                
    logger.info("[DB-FIX] Schema verification complete.")
