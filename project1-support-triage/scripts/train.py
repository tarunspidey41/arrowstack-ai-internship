"""Train and save the model:  python scripts/train.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from triage import model, config

if __name__ == "__main__":
    model.train()
    print(f"Model saved to {config.MODEL_PATH}")
