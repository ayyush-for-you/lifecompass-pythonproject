from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class UserProfile:
    """Structured answers collected from the questionnaire."""

    name: str
    mode: str
    interests: Dict[str, int] = field(default_factory=dict)
    hobbies: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    personality: List[str] = field(default_factory=list)
    current_field: str = ""
    stress_level: int = 0
    energy_level: int = 0
    available_time: str = ""
    support_preference: str = ""


@dataclass
class CareerRecommendation:
    title: str
    domain: str
    category: str
    description: str
    effort: str
    risk: str
    backup: str
    score: float
    reason: str


@dataclass
class RecommendationResult:
    mode: str
    headline: str
    summary: str
    scores: Dict[str, float]
    primary_paths: List[CareerRecommendation] = field(default_factory=list)
    secondary_paths: List[CareerRecommendation] = field(default_factory=list)
    balance_plan: List[str] = field(default_factory=list)
    side_skills: List[str] = field(default_factory=list)
    chart_filename: str = ""
