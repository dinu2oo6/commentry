"""Context Engine — Maintain match state and generate contextual cues."""

from typing import List, Optional
from config import CONTEXT_HISTORY_SIZE


class ContextEngine:
    """Tracks match state and generates contextual commentary cues."""

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset match state."""
        self.score = 0
        self.wickets = 0
        self.overs = 0.0
        self.balls_in_over = 0
        self.run_rate = 0.0
        self.batsman = "Batsman"
        self.bowler = "Bowler"
        self.partnership = 0
        self.last_events: List[dict] = []
        self.consecutive_dots = 0
        self.consecutive_boundaries = 0
        self.over_runs = 0

    def update(self, event: dict) -> dict:
        """Update match state with a new event and return enriched context."""
        event_type = event.get("event", "DOT")
        runs = self._event_to_runs(event_type)

        # Update score
        self.score += runs
        self.partnership += runs
        self.over_runs += runs

        # Update ball count
        if event_type not in ("WIDE", "NO_BALL"):
            self.balls_in_over += 1
            if self.balls_in_over >= 6:
                self.overs = int(self.overs) + 1
                self.balls_in_over = 0
                self.over_runs = 0

        # Track consecutive patterns
        if event_type == "DOT":
            self.consecutive_dots += 1
            self.consecutive_boundaries = 0
        elif event_type in ("FOUR", "SIX"):
            self.consecutive_boundaries += 1
            self.consecutive_dots = 0
        else:
            self.consecutive_dots = 0
            self.consecutive_boundaries = 0

        # Wicket
        if event_type == "WICKET":
            self.wickets += 1
            self.partnership = 0

        # Run rate
        total_balls = int(self.overs) * 6 + self.balls_in_over
        self.run_rate = round((self.score / total_balls) * 6, 2) if total_balls > 0 else 0

        # Store event in history
        enriched = {
            **event,
            "runs": runs,
            "score": f"{self.score}/{self.wickets}",
            "overs": f"{int(self.overs)}.{self.balls_in_over}",
            "run_rate": self.run_rate,
            "partnership": self.partnership,
        }
        self.last_events.append(enriched)
        if len(self.last_events) > CONTEXT_HISTORY_SIZE:
            self.last_events.pop(0)

        return enriched

    def get_context_phrases(self) -> List[str]:
        """Generate context-aware phrases for commentary."""
        phrases = []

        if self.consecutive_dots >= 3:
            phrases.append("pressure building on the batsman")
        if self.consecutive_dots >= 5:
            phrases.append("incredibly tight bowling spell")
        if self.consecutive_boundaries >= 2:
            phrases.append("back-to-back boundaries")
        if self.consecutive_boundaries >= 3:
            phrases.append("the batsman is on fire")
        if self.wickets == 0 and self.score > 50:
            phrases.append("solid opening partnership")
        if self.run_rate > 8:
            phrases.append("scoring rate well above 8 an over")
        elif self.run_rate < 4 and int(self.overs) > 2:
            phrases.append("run rate under pressure")
        if self.over_runs == 0 and self.balls_in_over >= 4:
            phrases.append("maiden over on the cards")

        return phrases

    def get_match_summary(self) -> dict:
        """Return current match state summary."""
        return {
            "score": f"{self.score}/{self.wickets}",
            "overs": f"{int(self.overs)}.{self.balls_in_over}",
            "run_rate": self.run_rate,
            "partnership": self.partnership,
            "context_phrases": self.get_context_phrases(),
            "recent_events": [
                {"event": e["event"], "shot": e.get("shot", ""), "runs": e.get("runs", 0)}
                for e in self.last_events[-5:]
            ],
        }

    def set_players(self, batsman: str = "Batsman", bowler: str = "Bowler"):
        """Set current player names."""
        self.batsman = batsman
        self.bowler = bowler

    @staticmethod
    def _event_to_runs(event_type: str) -> int:
        return {
            "DOT": 0, "SINGLE": 1, "DOUBLE": 2, "TRIPLE": 3,
            "FOUR": 4, "SIX": 6, "WICKET": 0, "WIDE": 1, "NO_BALL": 1,
        }.get(event_type, 0)
