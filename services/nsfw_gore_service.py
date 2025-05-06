import torch
import clip

CATEGORIES = ["neutral", "drawings", "sexy", "porn", "hentai", "gore"]

class NSFWGoreClassifier:
    def __init__(self, device=None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model, self.preprocess = clip.load("ViT-B/32", device=self.device)
        self.categories = CATEGORIES
        self.text_inputs = torch.cat([clip.tokenize(c) for c in self.categories]).to(self.device)

    def predict(self, pil_image):
        image_input = self.preprocess(pil_image).unsqueeze(0).to(self.device)
        with torch.no_grad():
            logits_per_image, _ = self.model(image_input, self.text_inputs)
            probs = logits_per_image.softmax(dim=-1).cpu().numpy()[0]
        return {cat: float(prob) for cat, prob in zip(self.categories, probs)}
