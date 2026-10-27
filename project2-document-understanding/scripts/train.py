"""Train and save the document-type classifier:  python scripts/train.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from docassist import classifier, config

if __name__ == "__main__":
    classifier.train()
    print(f"Model saved to {config.MODEL_PATH}")
