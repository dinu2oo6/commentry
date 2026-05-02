"""Commentary Generator — LLM + template-based cricket commentary with style modes."""

import random
from typing import List, Optional

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import ollama as ollama_client
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

from config import (
    OPENAI_API_KEY, LLM_MODEL, DEFAULT_STYLE,
    LLM_PROVIDER, OLLAMA_BASE_URL, OLLAMA_VISION_MODEL,
)


# ── Style Prompts ─────────────────────────────────────────────────────
STYLE_PROMPTS = {
    "professional": (
        "You are Harsha Bhogle, one of the most respected cricket commentators. "
        "Your commentary is measured, insightful, and articulate. You mix cricketing "
        "wisdom with elegant phrasing. You appreciate good cricket from both sides."
    ),
    "hype": (
        "You are an IPL-style commentator — MAXIMUM ENERGY! Every boundary is ELECTRIC, "
        "every six is OUT OF THE PARK. Use exclamation marks, capitalize key words, "
        "add crowd reactions. Think Danny Morrison meets Ravi Shastri at peak hype."
    ),
    "funny": (
        "You are a casual, funny cricket commentator who uses humor, memes, and pop culture "
        "references. You make witty observations, use playful language, and keep the audience "
        "entertained with relatable jokes. Think social media cricket banter."
    ),
    "analytical": (
        "You are a stats-heavy analytical commentator. You reference strike rates, averages, "
        "wagon wheel patterns, and historical data. You analyze technique, field placements, "
        "and bowling strategies. Think Michael Atherton meets data science."
    ),
}

# ── Template Commentary ───────────────────────────────────────────────
TEMPLATES = {
    "DOT": [
        "Good delivery, {bowler} keeps it tight. {batsman} defends solidly.",
        "Dot ball. {bowler} hitting the right areas. Score stays at {score}.",
        "Beaten outside off! {bowler} is testing {batsman} here.",
        "Played straight back to {bowler}. Good contest brewing.",
    ],
    "SINGLE": [
        "{batsman} nudges it for a single. Score ticks along to {score}.",
        "Quick single taken by {batsman}. Smart cricket.",
        "Worked away for one. {batsman} rotating the strike well.",
    ],
    "DOUBLE": [
        "Two runs! {batsman} finds the gap and they come back for a second.",
        "Good running between the wickets. {score} now.",
    ],
    "FOUR": [
        "FOUR! Beautiful {shot} by {batsman}! That races to the boundary!",
        "BOUNDARY! {batsman} middled that {shot} perfectly! {score}!",
        "That's FOUR! {batsman} punishes {bowler} with a gorgeous {shot}!",
        "Cracking shot! The {shot} by {batsman} is pure timing! FOUR!",
    ],
    "SIX": [
        "SIX! MASSIVE hit by {batsman}! That's gone into the stands!",
        "HUGE SIX! {batsman} sends it miles with that {shot}! {score}!",
        "That's OUT OF HERE! {batsman} clears the rope with authority! SIX!",
        "MAXIMUM! What a shot! {batsman} dispatches {bowler} into the crowd!",
    ],
    "WICKET": [
        "WICKET! {bowler} strikes! What a moment! Score: {score}.",
        "OUT! {batsman} has to go! {bowler} breaks through! {score}.",
        "Gone! {bowler} picks up a crucial wicket! The partnership is broken!",
    ],
    "WIDE": [
        "Wide called. {bowler} strays down leg. Extra run added.",
        "That's a wide. {bowler} needs to find the right line.",
    ],
    "NO_BALL": [
        "No ball! {bowler} overstepped. Free hit coming up!",
        "No ball called! {batsman} gets a free hit opportunity!",
    ],
}

CONTEXT_ADDONS = {
    "pressure building on the batsman": [
        " The pressure is really mounting now.",
        " Dot balls piling up — something has to give.",
    ],
    "back-to-back boundaries": [
        " Back-to-back boundaries! The momentum has shifted!",
        " Boundaries flowing now! The crowd is loving this!",
    ],
    "the batsman is on fire": [
        " The batsman is absolutely ON FIRE right now!",
        " This is destructive batting at its finest!",
    ],
    "maiden over on the cards": [
        " A maiden over could be on the cards here.",
    ],
}


class CommentaryGenerator:
    """Generate cricket commentary using LLM or templates."""

    def __init__(self, style: str = DEFAULT_STYLE):
        self.style = style if style in STYLE_PROMPTS else DEFAULT_STYLE
        self.provider = LLM_PROVIDER
        self.client = None

        if self.provider == "ollama" and OLLAMA_AVAILABLE:
            self._ollama = ollama_client.Client(host=OLLAMA_BASE_URL)
        elif OPENAI_AVAILABLE and OPENAI_API_KEY:
            try:
                self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
            except Exception:
                pass
            self._ollama = None
        else:
            self._ollama = None

    def set_style(self, style: str):
        """Change commentary style."""
        if style in STYLE_PROMPTS:
            self.style = style

    def generate_from_event(self, event: dict, context: dict) -> str:
        """Generate commentary for a single event with context."""
        if self._ollama:
            return self._ollama_commentary(event, context)
        if self.client:
            return self._llm_commentary(event, context)
        return self._template_commentary(event, context)

    def generate_from_frames(self, frames_b64: List[str], duration: float,
                              context: Optional[dict] = None) -> str:
        """Generate commentary from video frames using a vision model."""
        prompt = (
            f"These are frames from a cricket match. "
            f"Create exciting cricket commentary in the style described. "
            f"Keep it to about {int(duration)} seconds of spoken commentary. "
            f"Use the scoreboard text visible in frames if any. "
            f"Match context: {context or 'No additional context'}"
        )

        if self._ollama:
            try:
                import base64
                images = []
                for b64 in frames_b64[:6]:  # llava handles fewer frames well
                    images.append(b64)
                response = self._ollama.chat(
                    model=OLLAMA_VISION_MODEL,
                    messages=[
                        {"role": "system", "content": STYLE_PROMPTS[self.style]},
                        {"role": "user", "content": prompt, "images": images},
                    ],
                )
                return response["message"]["content"].strip()
            except Exception as e:
                return f"Exciting action on the cricket field! {str(e)[:50]}"

        if not self.client:
            return "What a delivery! The action continues on this exciting cricket pitch."

        try:
            content = [{"type": "text", "text": prompt}]
            for b64 in frames_b64[:20]:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{b64}", "detail": "low"},
                })
            response = self.client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": STYLE_PROMPTS[self.style]},
                    {"role": "user", "content": content},
                ],
                max_tokens=300,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Exciting action on the cricket field! {str(e)[:50]}"

    def generate_batch(self, events: List[dict], context_engine) -> List[dict]:
        """Generate commentary for a batch of events."""
        results = []
        for event in events:
            enriched = context_engine.update(event)
            match_summary = context_engine.get_match_summary()
            commentary = self.generate_from_event(enriched, match_summary)
            results.append({
                **enriched,
                "commentary": commentary,
                "style": self.style,
            })
        return results

    def _ollama_commentary(self, event: dict, context: dict) -> str:
        """Generate commentary using local Ollama model."""
        try:
            prompt = (
                f"Generate 1-2 lines of cricket commentary for this event:\n"
                f"Event: {event.get('event', 'DOT')}\n"
                f"Shot: {event.get('shot', 'defensive')}\n"
                f"Score: {event.get('score', '0/0')}\n"
                f"Overs: {event.get('overs', '0.0')}\n"
                f"Context: {', '.join(context.get('context_phrases', []))}\n"
                f"Recent events: {context.get('recent_events', [])}\n\n"
                f"Be natural, avoid repetition. Reply with commentary only, no preamble."
            )
            response = self._ollama.chat(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": STYLE_PROMPTS[self.style]},
                    {"role": "user", "content": prompt},
                ],
                options={"temperature": 0.8, "num_predict": 100},
            )
            return response["message"]["content"].strip()
        except Exception:
            return self._template_commentary(event, context)

    def _llm_commentary(self, event: dict, context: dict) -> str:
        """Generate commentary using OpenAI."""
        try:
            prompt = (
                f"Generate 1-2 lines of cricket commentary for this event:\n"
                f"Event: {event.get('event', 'DOT')}\n"
                f"Shot: {event.get('shot', 'defensive')}\n"
                f"Score: {event.get('score', '0/0')}\n"
                f"Overs: {event.get('overs', '0.0')}\n"
                f"Context: {', '.join(context.get('context_phrases', []))}\n"
                f"Recent events: {context.get('recent_events', [])}\n\n"
                f"Be natural, avoid repetition from recent commentary."
            )
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": STYLE_PROMPTS[self.style]},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=100,
                temperature=0.8,
            )
            return response.choices[0].message.content.strip()
        except Exception:
            return self._template_commentary(event, context)

    def _template_commentary(self, event: dict, context: dict) -> str:
        """Generate commentary from templates."""
        event_type = event.get("event", "DOT")
        templates = TEMPLATES.get(event_type, TEMPLATES["DOT"])
        template = random.choice(templates)

        commentary = template.format(
            batsman=event.get("batsman", "the batsman"),
            bowler=event.get("bowler", "the bowler"),
            shot=event.get("shot", "shot").replace("_", " "),
            score=event.get("score", "0/0"),
        )

        # Add context-aware addon
        for phrase in context.get("context_phrases", []):
            if phrase in CONTEXT_ADDONS:
                commentary += random.choice(CONTEXT_ADDONS[phrase])
                break

        return commentary
