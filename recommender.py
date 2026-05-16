import json
import re
from pathlib import Path
from typing import Dict, Iterable, List

import numpy as np
import pandas as pd

from models import CareerRecommendation, RecommendationResult, UserProfile


DOMAIN_LABELS = {
    "technology": "Technology",
    "science": "Science",
    "creative": "Creative Fields",
    "sports": "Sports",
    "business": "Business",
}

KEYWORD_DOMAIN_MAP = {
    "coding": "technology",
    "programming": "technology",
    "ai": "technology",
    "robotics": "technology",
    "gaming": "technology",
    "biology": "science",
    "research": "science",
    "medicine": "science",
    "experiment": "science",
    "music": "creative",
    "singing": "creative",
    "writing": "creative",
    "photography": "creative",
    "drawing": "creative",
    "video": "creative",
    "cricket": "sports",
    "football": "sports",
    "fitness": "sports",
    "gym": "sports",
    "athletics": "sports",
    "startup": "business",
    "selling": "business",
    "marketing": "business",
    "money": "business",
    "finance": "business",
}

PERSONALITY_BOOSTS = {
    "analytical": {"technology": 1.2, "science": 1.1, "business": 0.5},
    "creative": {"creative": 1.4, "business": 0.4, "technology": 0.4},
    "social": {"business": 1.0, "creative": 0.7, "sports": 0.5},
    "disciplined": {"sports": 1.0, "science": 0.5, "technology": 0.4},
    "curious": {"science": 1.0, "technology": 0.8, "creative": 0.4},
    "independent": {"business": 0.9, "creative": 0.6, "technology": 0.4},
}

SIDE_SKILLS = {
    "technology": ["Python basics", "portfolio projects", "data literacy"],
    "science": ["research reading", "lab documentation", "scientific writing"],
    "creative": ["content planning", "editing", "audience building"],
    "sports": ["fitness tracking", "coaching basics", "nutrition awareness"],
    "business": ["communication", "digital marketing", "basic finance"],
}


class LifeCompassRecommender:
    def __init__(self, career_csv_path: Path):
        self.career_csv_path = Path(career_csv_path)
        self.careers = pd.read_csv(self.career_csv_path, skipinitialspace=True)

    def recommend_careers(self, profile: UserProfile) -> RecommendationResult:
        scores = self._calculate_domain_scores(profile)
        ranked = self._rank_careers(profile, scores)
        primary = ranked[:3]
        secondary = ranked[3:6]

        top_domain = max(scores, key=scores.get)
        headline = f"Your strongest direction is {DOMAIN_LABELS[top_domain]}."
        summary = self._build_career_summary(profile, top_domain, primary)

        return RecommendationResult(
            mode="career",
            headline=headline,
            summary=summary,
            scores={DOMAIN_LABELS[key]: round(value, 2) for key, value in scores.items()},
            primary_paths=primary,
            secondary_paths=secondary,
        )

    def recommend_balance(self, profile: UserProfile) -> RecommendationResult:
        scores = self._calculate_domain_scores(profile)
        top_domains = sorted(scores, key=scores.get, reverse=True)[:2]
        stress = profile.stress_level
        energy = profile.energy_level

        balance_plan = [
            self._pace_advice(stress, energy, profile.available_time),
            f"Reconnect with {self._human_list(profile.hobbies) or 'one enjoyable activity'} through a fixed weekly slot.",
            f"Keep your current field stable while testing {DOMAIN_LABELS[top_domains[0]].lower()} as a parallel interest.",
            "Review progress every 30 days using energy, consistency, and learning as the main signals.",
        ]
        side_skills = []
        for domain in top_domains:
            side_skills.extend(SIDE_SKILLS[domain][:2])

        headline = "A balanced path is possible without quitting everything at once."
        summary = (
            "Your answers suggest that the next step should be gentle, practical, "
            "and measurable: protect recovery time, restart hobbies, and build one useful side skill."
        )

        return RecommendationResult(
            mode="balance",
            headline=headline,
            summary=summary,
            scores={DOMAIN_LABELS[key]: round(value, 2) for key, value in scores.items()},
            balance_plan=balance_plan,
            side_skills=side_skills,
        )

    def _calculate_domain_scores(self, profile: UserProfile) -> Dict[str, float]:
        scores = {key: float(profile.interests.get(key, 0)) for key in DOMAIN_LABELS}

        for item in profile.hobbies + profile.skills:
            domain = self._domain_from_text(item)
            if domain:
                scores[domain] += 1.4

        for trait in profile.personality:
            for domain, boost in PERSONALITY_BOOSTS.get(trait, {}).items():
                scores[domain] += boost

        if profile.mode == "balance":
            scores = {key: value + max(profile.energy_level, 1) * 0.15 for key, value in scores.items()}

        values = np.array(list(scores.values()), dtype=float)
        if values.max() == 0:
            values = np.ones_like(values)
        normalized = (values / values.max()) * 100
        return dict(zip(scores.keys(), normalized))

    def _rank_careers(self, profile: UserProfile, scores: Dict[str, float]) -> List[CareerRecommendation]:
        rows = []
        user_words = self._tokenize(" ".join(profile.hobbies + profile.skills + profile.personality))

        for _, row in self.careers.iterrows():
            domain_key = str(row["domain_key"])
            tag_words = self._tokenize(f"{row['tags']} {row['skills']}")
            overlap = len(user_words.intersection(tag_words))
            final_score = scores.get(domain_key, 0) + overlap * 7 + float(row.get("stability_score", 0))
            reason = self._reason_for(row, profile, overlap)
            rows.append(
                CareerRecommendation(
                    title=row["career"],
                    domain=DOMAIN_LABELS.get(domain_key, domain_key.title()),
                    category=row["category"],
                    description=row["description"],
                    effort=row["effort"],
                    risk=row["risk"],
                    backup=row["backup"],
                    score=round(final_score, 2),
                    reason=reason,
                )
            )

        rows.sort(key=lambda item: item.score, reverse=True)
        return rows

    def _reason_for(self, row: pd.Series, profile: UserProfile, overlap: int) -> str:
        domain = DOMAIN_LABELS.get(row["domain_key"], row["domain_key"])
        if overlap:
            return f"It matches your stated hobbies or skills and also fits the {domain.lower()} domain."
        if profile.personality:
            return f"It fits your {self._human_list(profile.personality)} personality pattern and gives a realistic growth route."
        return f"It is a practical option inside {domain.lower()} with backup paths available."

    def _build_career_summary(
        self,
        profile: UserProfile,
        top_domain: str,
        primary: Iterable[CareerRecommendation],
    ) -> str:
        hobbies = self._human_list(profile.hobbies)
        traits = self._human_list(profile.personality)
        careers = self._human_list([item.title for item in primary])
        parts = [
            f"Your responses show a strong inclination toward {DOMAIN_LABELS[top_domain].lower()}."
        ]
        if hobbies:
            parts.append(f"Your hobbies point toward {hobbies}.")
        if traits:
            parts.append(f"Your personality signals include {traits}.")
        parts.append(f"The best starting options are {careers}.")
        return " ".join(parts)

    def _pace_advice(self, stress: int, energy: int, available_time: str) -> str:
        if stress >= 4 and energy <= 2:
            return "Start with recovery first: choose one low-pressure hobby session per week for the next two weeks."
        if available_time == "low":
            return "Use a small routine: 20 minutes, three times a week, focused on one hobby or side skill."
        return "Create a weekly balance block with learning, rest, and one enjoyable activity."

    def _domain_from_text(self, text: str) -> str:
        lowered = text.lower()
        for keyword, domain in KEYWORD_DOMAIN_MAP.items():
            if keyword in lowered:
                return domain
        return ""

    def _tokenize(self, text: str) -> set:
        return set(re.findall(r"[a-zA-Z]+", text.lower()))

    def _human_list(self, values: Iterable[str]) -> str:
        cleaned = [str(value).replace("_", " ").strip() for value in values if str(value).strip()]
        if not cleaned:
            return ""
        if len(cleaned) == 1:
            return cleaned[0]
        return ", ".join(cleaned[:-1]) + f", and {cleaned[-1]}"


class SubmissionStore:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, profile: UserProfile, result: RecommendationResult) -> None:
        row = {
            "name": profile.name,
            "mode": profile.mode,
            "interests": json.dumps(profile.interests),
            "hobbies": json.dumps(profile.hobbies),
            "skills": json.dumps(profile.skills),
            "personality": json.dumps(profile.personality),
            "headline": result.headline,
            "top_scores": json.dumps(result.scores),
        }
        frame = pd.DataFrame([row])
        frame.to_csv(self.path, mode="a", index=False, header=not self.path.exists())
