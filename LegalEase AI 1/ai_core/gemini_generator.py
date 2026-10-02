from google import genai

from config import GEMINI_API_KEY, GEMINI_MODEL

_SKIP = ("image", "live", "audio", "tts", "lite", "embedding", "robotics")


class GeminiDocumentGenerator:
    def __init__(self, model_name: str | None = None):
        if not GEMINI_API_KEY or GEMINI_API_KEY == "PASTE_YOUR_KEY_HERE":
            raise RuntimeError(
                "GEMINI_API_KEY is missing. Add your key to the .env file."
            )
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model_name = model_name or GEMINI_MODEL or self._pick_model()

    def _pick_model(self) -> str:
        """Pick a text-generation Flash model that your API key can use."""
        names = []
        for m in self.client.models.list():
            name = (m.name or "").replace("models/", "")
            actions = getattr(m, "supported_actions", None) or []
            if ("generateContent" in actions and "flash" in name
                    and not any(s in name for s in _SKIP)):
                names.append(name)
        if not names:
            raise RuntimeError(
                "No usable Gemini model found for your API key. "
                "Set GEMINI_MODEL in .env to a model listed in Google AI Studio."
            )
        stable = [n for n in names if "preview" not in n]
        pool = stable or names
        return sorted(pool, reverse=True)[0]

    def _generate(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.model_name, contents=prompt
        )
        if not response.text:
            raise RuntimeError("The model returned an empty response.")
        return response.text

    def generate_document(self, document_type: str, parties: str,
                          terms: str, dates: str) -> str:
        prompt = (
            f"Generate a comprehensive legal document titled '{document_type}'.\n"
            f"Involved parties: {parties}\n"
            f"Effective Date: {dates}\n"
            f"Terms and conditions (semicolon-separated): {terms}\n\n"
            "Formatting rules:\n"
            "- Use a formal legal structure with numbered sections, for example "
            "'1. Services:' on its own line, followed by the clause text.\n"
            "- Include a preamble, definitions where relevant, the user's terms, "
            "confidentiality, termination, governing law, severability, "
            "entire agreement, and a signature block.\n"
            "- Use placeholders in [square brackets] for any missing details.\n"
            "- Output PLAIN TEXT only. Do not use Markdown (no #, no **, no tables).\n"
            "- Do not add commentary before or after the document."
        )
        try:
            return self._generate(prompt)
        except Exception as exc:
            msg = str(exc)
            if "404" in msg or "NOT_FOUND" in msg or "not found" in msg.lower():
                # Configured model is gone: switch to one that exists and retry.
                self.model_name = self._pick_model()
                return self._generate(prompt)
            raise