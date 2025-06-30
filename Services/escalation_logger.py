import json
from datetime import datetime
from pathlib import Path

ESCALATION_LOG_FILE = Path("logs/escalations.jsonl")

def log_escalation(sender_id: str, user_message: str, aya_reply: str):
    ESCALATION_LOG_FILE.parent.mkdir(exist_ok=True)
    with ESCALATION_LOG_FILE.open("a", encoding="utf-8") as f:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "sender_id": sender_id,
            "user_message": user_message,
            "aya_reply": aya_reply
        }
        f.write(json.dumps(log_entry) + "\n")
