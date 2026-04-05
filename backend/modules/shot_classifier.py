"""Shot Classifier — ResNet18-based cricket shot type classification."""

import random
from typing import Optional

try:
    import torch
    import torch.nn as nn
    from torchvision import models, transforms
    from PIL import Image
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


SHOT_CLASSES = [
    "cover_drive", "pull_shot", "cut", "sweep",
    "straight_drive", "defensive", "flick", "hook",
]


class ShotClassifier:
    """Classify cricket shots from video frames using ResNet18."""

    def __init__(self, model_path: Optional[str] = None):
        self.model = None
        self.transform = None

        if TORCH_AVAILABLE:
            self._init_model(model_path)

    def _init_model(self, model_path: Optional[str]):
        """Initialize ResNet18 with custom head for shot classification."""
        try:
            model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
            num_features = model.fc.in_features
            model.fc = nn.Linear(num_features, len(SHOT_CLASSES))
            model.eval()

            if model_path:
                try:
                    state_dict = torch.load(model_path, map_location="cpu")
                    model.load_state_dict(state_dict)
                except Exception:
                    pass  # Use pretrained features with random classifier head

            self.model = model
            self.transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225],
                ),
            ])
        except Exception:
            pass

    def classify(self, frame_path: str) -> dict:
        """Classify the shot type from a single frame."""
        if not self.model or not self.transform:
            return self._mock_classify()

        try:
            image = Image.open(frame_path).convert("RGB")
            tensor = self.transform(image).unsqueeze(0)

            with torch.no_grad():
                outputs = self.model(tensor)
                probs = torch.softmax(outputs, dim=1)[0]
                top_idx = torch.argmax(probs).item()
                confidence = probs[top_idx].item()

            return {
                "shot_type": SHOT_CLASSES[top_idx],
                "confidence": round(confidence, 3),
                "all_scores": {
                    SHOT_CLASSES[i]: round(probs[i].item(), 3)
                    for i in range(len(SHOT_CLASSES))
                },
            }
        except Exception:
            return self._mock_classify()

    def classify_sequence(self, frames: list) -> list:
        """Classify shots for a list of frame dicts."""
        results = []
        for frame in frames:
            path = frame.get("path", "")
            result = self.classify(path)
            result["timestamp"] = frame.get("timestamp", 0)
            result["frame_index"] = frame.get("index", 0)
            results.append(result)
        return results

    def _mock_classify(self) -> dict:
        """Mock classification when model is unavailable."""
        shot = random.choice(SHOT_CLASSES)
        scores = {}
        remaining = 1.0
        for s in SHOT_CLASSES:
            if s == shot:
                scores[s] = round(random.uniform(0.4, 0.8), 3)
                remaining -= scores[s]
            else:
                val = round(random.uniform(0.01, remaining / len(SHOT_CLASSES)), 3)
                scores[s] = val
                remaining -= val

        return {
            "shot_type": shot,
            "confidence": scores[shot],
            "all_scores": scores,
        }
