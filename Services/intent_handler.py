from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import torch

# Load tokenizer and model once at startup
MODEL_PATH = "models/distilbert-intent"
tokenizer = DistilBertTokenizer.from_pretrained(MODEL_PATH)
model = DistilBertForSequenceClassification.from_pretrained(MODEL_PATH)
model.eval()

# Intent labels (update if you added more)
LABELS = [
    "allowed_items",
    "booking",
    "check_allowed_items",
    "dropoff_location",
    "dropoff_policy",
    "loading_schedule",
    "pickup_policy",
    "rate",
    "tracking",
    "volumetric"
]

def detect_intent(text: str):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=1)
        confidence, predicted = torch.max(probs, dim=1)
        label = LABELS[predicted.item()]
        return label, confidence.item()
