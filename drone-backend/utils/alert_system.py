"""
Alert system with cooldown and auto-expiry
"""
import time
from typing import Dict, List, Optional

class AlertSystem:
    def __init__(self, cooldown: int = 5, max_alerts: int = 10):
        self.cooldown = cooldown
        self.max_alerts = max_alerts
        self.last_alert_time: Dict[str, float] = {}
        self.recent_alerts: List[Dict] = []

    def should_alert(self, detection_key: str) -> bool:
        """Check if enough time has passed since last alert for this key"""
        current_time = time.time()
        last_time = self.last_alert_time.get(detection_key, 0)
        
        if current_time - last_time >= self.cooldown:
            self.last_alert_time[detection_key] = current_time
            return True
        return False

    def create_alert(self, detection: Dict) -> Dict:
        """Create a standardized alert payload for the frontend"""
        alert = {
            "type": "alert",
            "class": detection.get("class_name", "unknown"),
            "confidence": round(detection.get("confidence", 0.0), 2),
            "mode": "thermal" if detection.get("is_thermal") else "normal",
            "timestamp": time.time(),
            "bbox": detection.get("bbox", [])
        }
        
        # Keep only last N alerts in memory
        self.recent_alerts.insert(0, alert)
        self.recent_alerts = self.recent_alerts[:self.max_alerts]
        
        return alert

    def get_recent_alerts(self, count: int = 10) -> List[Dict]:
        return self.recent_alerts[:count]

    def clear_expired(self, expiry_seconds: int = 60):
        """Remove alerts older than expiry_seconds"""
        cutoff = time.time() - expiry_seconds
        self.recent_alerts = [a for a in self.recent_alerts if a["timestamp"] > cutoff]