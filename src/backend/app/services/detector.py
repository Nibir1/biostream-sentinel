import numpy as np
import polars as pl
from sklearn.ensemble import IsolationForest
import logging

logger = logging.getLogger(__name__)

class AnomalyDetector:
    def __init__(self):
        self.model = None
        self.is_ready = False

    def train_baseline(self):
        """
        Trains a lightweight Isolation Forest on synthetic 'normal' data.
        In a real production system, this would load a pre-trained .joblib file.
        """
        logger.info("TRAINING: Initializing baseline anomaly model...")
        
        # 1. Generate 1000 'Normal' records (Heart Rate 60-100, SPO2 95-100)
        rng = np.random.RandomState(42)
        X_normal = np.column_stack((
            rng.uniform(60, 100, 1000),  # Heart Rate
            rng.uniform(95, 100, 1000),  # SPO2
            rng.uniform(20, 100, 1000)   # Battery (irrelevant for health but used as feature)
        ))

        # 2. Train the model
        # contamination=0.01 means we expect ~1% of data to be anomalous
        self.model = IsolationForest(n_estimators=100, contamination=0.01, random_state=42)
        self.model.fit(X_normal)
        
        self.is_ready = True
        logger.info("TRAINING: Model ready. Baseline established.")

    def predict(self, heart_rate: int, spo2: float, battery: float) -> dict:
        """
        Returns anomaly score and risk level.
        """
        if not self.is_ready:
            return {"risk": "UNKNOWN", "score": 0.0}

        # Reshape for sklearn (single sample)
        features = np.array([[heart_rate, spo2, battery]])
        
        # predict() returns -1 for outlier, 1 for inlier
        prediction = self.model.predict(features)[0]
        
        # decision_function() returns negative for anomalies, positive for normal
        score = self.model.decision_function(features)[0]

        if prediction == -1:
            risk = "HIGH"
        elif score < 0.1: # Close to boundary
            risk = "MEDIUM"
        else:
            risk = "LOW"

        return {
            "risk_level": risk,
            "anomaly_score": float(score)
        }

# Global singleton instance
detector = AnomalyDetector()