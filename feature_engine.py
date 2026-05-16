from datetime import date, datetime, timedelta
from io import BytesIO
from textwrap import wrap
from urllib.parse import quote_plus

from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt


DOMAIN_SKILLS = {
    "Technology": ["python", "logic", "problem solving", "portfolio projects", "data literacy"],
    "Science": ["biology", "research reading", "documentation", "observation", "scientific writing"],
    "Creative Fields": ["creativity", "editing", "storytelling", "audience building", "portfolio"],
    "Sports": ["discipline", "fitness tracking", "teamwork", "nutrition awareness", "performance analysis"],
    "Business": ["communication", "marketing", "sales", "basic finance", "leadership"],
}

CAREER_REALITY = {
    "Computer Science Engineer": {
        "salary": "Rs 4-18 LPA early to mid career, higher with strong projects",
        "education_cost": "Rs 0-8 lakh using public colleges, online learning, or private degree routes",
        "demand": "High demand, high competition",
        "scholarships": "NSP, AICTE schemes, state scholarships, college fee waivers",
        "freelance": "Websites, automation scripts, tutoring: Rs 5k-80k/month depending on portfolio",
        "transition_months": 8,
    },
    "AI and Data Science Specialist": {
        "salary": "Rs 5-22 LPA when Python, statistics, SQL, and projects are strong",
        "education_cost": "Rs 0-2 lakh for self-learning; more for degree or bootcamp routes",
        "demand": "High demand, expects proof of skill",
        "scholarships": "NSP, AICTE, free NPTEL/SWAYAM learning support",
        "freelance": "Dashboards, data cleaning, ML prototypes: Rs 10k-1 lakh/month",
        "transition_months": 10,
    },
    "Music Producer": {
        "salary": "Income varies: studio assistant to producer can range from project-based pay to full-time roles",
        "education_cost": "Rs 0-3 lakh depending on software, gear, and short courses",
        "demand": "Growing with creators, ads, films, podcasts, and indie artists",
        "scholarships": "Look for state arts scholarships, college cultural grants, and creator grants",
        "freelance": "Beats, mixing, jingles, podcast audio: Rs 3k-70k/month early stage",
        "transition_months": 6,
    },
    "Content Creator": {
        "salary": "Unstable early; brand/content roles can become steady with proof of audience or editing skill",
        "education_cost": "Rs 0-1 lakh for phone, mic, editing tools, and optional courses",
        "demand": "High opportunity, platform risk is real",
        "scholarships": "Use free creator courses, Skill India Digital, and college media clubs",
        "freelance": "Editing, scripts, thumbnails, social media: Rs 5k-75k/month",
        "transition_months": 4,
    },
    "Cricketer": {
        "salary": "Highly variable; earnings depend on selection level, coaching, clubs, and sponsorships",
        "education_cost": "Coaching, gear, travel, fitness: can be low to high depending on city and level",
        "demand": "Very competitive, requires backup planning",
        "scholarships": "Sports quota, state sports scholarships, Khelo India opportunities",
        "freelance": "Coaching juniors, fitness content, local tournaments: Rs 3k-50k/month",
        "transition_months": 18,
    },
    "Digital Marketer": {
        "salary": "Rs 3-12 LPA early to mid career, higher with performance proof",
        "education_cost": "Rs 0-80k using free certifications and portfolio projects",
        "demand": "High demand across startups, agencies, and small businesses",
        "scholarships": "Skill India Digital, free platform certifications, state skilling programs",
        "freelance": "SEO, ads, content, social media retainers: Rs 5k-1 lakh/month",
        "transition_months": 5,
    },
}

DOMAIN_REALITY_FALLBACK = {
    "Technology": CAREER_REALITY["Computer Science Engineer"],
    "Science": {
        "salary": "Rs 3-12 LPA depending on degree, lab exposure, and specialization",
        "education_cost": "Can require degree or higher study; public institutions reduce cost",
        "demand": "Stable in healthcare, research support, biotech, and education",
        "scholarships": "NSP, state scholarships, research internships, institute aid",
        "freelance": "Tutoring, science writing, data entry for labs: Rs 3k-40k/month",
        "transition_months": 12,
    },
    "Creative Fields": CAREER_REALITY["Content Creator"],
    "Sports": CAREER_REALITY["Cricketer"],
    "Business": CAREER_REALITY["Digital Marketer"],
}

FREE_RESOURCES = {
    "Technology": ["freeCodeCamp", "CS50", "Kaggle Learn", "NPTEL Python/Data courses"],
    "Science": ["NPTEL biology courses", "PubMed reading practice", "SWAYAM", "iGEM/college lab clubs"],
    "Creative Fields": ["YouTube Creator Academy", "Canva Design School", "BandLab", "DaVinci Resolve tutorials"],
    "Sports": ["Khelo India resources", "NIS coaching basics", "fitness tracking templates", "local academy trial sessions"],
    "Business": ["Google Digital Garage", "HubSpot Academy", "Meta Blueprint", "Startup India Learning"],
}

PEER_STORIES = [
    {
        "age": 19,
        "background": "Class 12 science student with music hobby",
        "path": "Started producing beats on free tools, sold small tracks online, then assisted a local studio.",
        "lesson": "Kept academics as backup while building a public portfolio every week.",
    },
    {
        "age": 21,
        "background": "B.Com student with cricket interest",
        "path": "Could not enter pro cricket, shifted to fitness coaching plus cricket analytics content.",
        "lesson": "Converted sports knowledge into adjacent earning paths instead of dropping the passion.",
    },
    {
        "age": 26,
        "background": "IT support employee",
        "path": "Built Python automation projects at night, moved into data analyst role after 7 months.",
        "lesson": "A bridge portfolio made the switch less risky than quitting immediately.",
    },
    {
        "age": 24,
        "background": "Engineering graduate who liked writing",
        "path": "Built a technical writing portfolio, then moved into SaaS content and documentation.",
        "lesson": "A non-traditional path still needs proof, consistency, and a backup income plan.",
    },
]

INDIA_DATA = {
    "schemes": [
        {
            "name": "National Career Service",
            "detail": "Government career and job services portal with jobs, counselling, and job fairs.",
            "url": "https://www.ncs.gov.in/",
        },
        {
            "name": "National Scholarship Portal",
            "detail": "Central place to check and apply for many government scholarships.",
            "url": "https://scholarships.gov.in/",
        },
        {
            "name": "Skill India Digital",
            "detail": "Digital skilling, learning, employment, and entrepreneurship ecosystem.",
            "url": "https://www.skillindiadigital.gov.in/",
        },
        {
            "name": "Apprenticeship India",
            "detail": "Apprenticeship opportunities and training pathways.",
            "url": "https://www.apprenticeshipindia.gov.in/",
        },
    ],
    "entrance_exams": [
        {"name": "NID DAT", "for": "Design", "url": "https://www.nid.edu/"},
        {"name": "NIFT Entrance Exam", "for": "Fashion/design", "url": "https://www.nift.ac.in/"},
        {"name": "CLAT", "for": "Law", "url": "https://consortiumofnlus.ac.in/"},
        {"name": "JEE Main", "for": "Engineering", "url": "https://jeemain.nta.nic.in/"},
        {"name": "NEET UG", "for": "Medicine", "url": "https://neet.nta.nic.in/"},
    ],
    "internships": [
        "Internshala for private internships",
        "AICTE internship portal for technical students",
        "NCS job fairs and apprenticeship listings",
        "College clubs, local startups, sports academies, creator studios",
    ],
}

COMMUNITY = {
    "groups": [
        "Creative Builders Circle",
        "Tech Portfolio Sprint",
        "Sports & Fitness Discipline Group",
        "Career Switchers 25+ Bridge Room",
    ],
    "challenges": [
        "30-day portfolio streak",
        "7-day career trial sprint",
        "Daily 45-minute learning challenge",
        "Burnout reset: hobby + sleep consistency",
    ],
    "badges": ["Starter Spark", "7-Day Explorer", "Portfolio Builder", "Buddy Streak", "Pivot Planner"],
}

BURNOUT_RESOURCES = [
    "10-minute breathing or body scan after study/work",
    "One hobby block before phone scrolling",
    "Weekly energy review: sleep, mood, movement, connection",
    "Talk to a trusted person if burnout feels persistent or severe",
]


def _career_reality(career):
    return CAREER_REALITY.get(career["title"], DOMAIN_REALITY_FALLBACK.get(career["domain"], DOMAIN_REALITY_FALLBACK["Business"]))


def build_feature_pack(result, profile):
    primary = result.get("primary_paths", [])
    first = primary[0] if primary else {"title": "Digital Marketer", "domain": "Business"}
    profile_skills = set(skill.lower() for skill in profile.get("skills", []))
    required = DOMAIN_SKILLS.get(first["domain"], DOMAIN_SKILLS["Business"])
    matched = [skill for skill in required if skill.lower() in profile_skills or any(skill.lower() in item for item in profile_skills)]
    missing = [skill for skill in required if skill not in matched]
    transition_months = _career_reality(first)["transition_months"] + max(len(missing) - 2, 0)

    return {
        "skill_gap": build_skill_gap(first, profile, missing, matched, transition_months),
        "financials": [build_financial_card(career) for career in primary[:3]],
        "stories": PEER_STORIES,
        "timeline": build_timeline(first, transition_months),
        "trial": build_trial(first),
        "burnout": build_burnout_plan(profile),
        "community": COMMUNITY,
        "resume": build_resume(profile, first, missing),
        "india": INDIA_DATA,
        "dashboard": build_dashboard(result, transition_months),
        "second_life": build_second_life_preview(first),
        "whatsapp_text": quote_plus(f"LifeCompass suggested {first['title']} for me. I am exploring it with a 7-day trial and weekly roadmap."),
    }


def build_skill_gap(career, profile, missing, matched, transition_months):
    return {
        "career": career["title"],
        "matched": matched or ["interest alignment", "willingness to explore"],
        "missing": missing,
        "transition_time": f"{transition_months}-{transition_months + 3} months with 45 minutes daily",
        "roadmap": [
            {"week": "Week 1-2", "task": f"Learn fundamentals for {career['title']} and collect 3 example projects."},
            {"week": "Week 3-4", "task": f"Build one tiny public project using {missing[0] if missing else 'your strongest skill'}."},
            {"week": "Week 5-8", "task": "Ask for feedback, improve the project, and document what you learned."},
            {"week": "Month 3+", "task": "Apply for internships, freelance tasks, competitions, or mentorship."},
        ],
        "resources": FREE_RESOURCES.get(career["domain"], FREE_RESOURCES["Business"]),
    }


def build_financial_card(career):
    reality = _career_reality(career)
    return {"career": career["title"], **reality}


def build_timeline(career, transition_months):
    tasks = [
        "Research 3 people already doing this career.",
        "Complete one free lesson and write notes.",
        "Build or practice one tiny output for 45 minutes.",
        "Share your work with one trusted person.",
        "Improve the output using feedback.",
        "Find one internship, academy, job, or project listing.",
        "Reflect: energy, interest, difficulty, and next move.",
    ]
    weeks = []
    for week in range(1, 9):
        weeks.append(
            {
                "week": week,
                "focus": f"{career['title']} exploration sprint",
                "tasks": [f"Day {day}: {task}" for day, task in enumerate(tasks, start=1)],
            }
        )
    return {
        "daily_minutes": 45,
        "estimated_months": transition_months,
        "weeks": weeks,
        "calendar_url": google_calendar_url(career["title"], tasks[0]),
    }


def google_calendar_url(title, details):
    start = datetime.now().replace(hour=18, minute=0, second=0, microsecond=0) + timedelta(days=1)
    end = start + timedelta(minutes=45)
    dates = f"{start:%Y%m%dT%H%M%S}/{end:%Y%m%dT%H%M%S}"
    return (
        "https://calendar.google.com/calendar/render?action=TEMPLATE"
        f"&text={quote_plus('LifeCompass: ' + title + ' micro-task')}"
        f"&dates={dates}&details={quote_plus(details)}"
    )


def build_trial(career):
    domain_tasks = {
        "Technology": ["Build a calculator", "Watch Python basics", "Fix one bug", "Make a GitHub note", "Clone a UI", "Automate a small task", "Rate your enjoyment"],
        "Science": ["Read one research summary", "Make biology notes", "Watch lab safety basics", "Explain a concept", "Find a local lab path", "Write experiment idea", "Rate your curiosity"],
        "Creative Fields": ["Create a 30-sec piece", "Study one creator", "Edit one draft", "Post privately/publicly", "Ask feedback", "Improve version 2", "Rate your energy"],
        "Sports": ["Fitness baseline", "Skill drill", "Watch technique", "Practice 45 minutes", "Track food/sleep", "Play or coach someone", "Rate discipline"],
        "Business": ["Find a problem", "Interview one person", "Draft offer", "Make a poster", "Test a price", "Pitch to someone", "Rate market interest"],
    }
    return [{"day": index, "task": task} for index, task in enumerate(domain_tasks.get(career["domain"], domain_tasks["Business"]), start=1)]


def build_burnout_plan(profile):
    energy = int(profile.get("energy_level") or 3)
    hobby = (profile.get("hobbies") or ["creative reset"])[0]
    load = "light" if energy <= 2 else "active"
    return {
        "load": load,
        "assessment": [
            "Sleep quality", "Screen overload", "Academic pressure", "Body energy", "Mood stability",
            "Social support", "Hobby connection", "Focus level", "Self-talk", "Hope about future",
        ],
        "schedule": [
            {"day": "Monday", "plan": "45-minute learning sprint + 10-minute walk"},
            {"day": "Tuesday", "plan": f"30-minute {hobby} block + simple journaling"},
            {"day": "Wednesday", "plan": "Skill practice + no-comparison social media rule"},
            {"day": "Thursday", "plan": "Restorative hobby or peer conversation"},
            {"day": "Friday", "plan": "Portfolio micro-task + mood score"},
            {"day": "Saturday", "plan": "Experiment day: try, record, review"},
            {"day": "Sunday", "plan": "Weekly reset and next-week planning"},
        ],
        "resources": BURNOUT_RESOURCES,
    }


def build_dashboard(result, transition_months):
    scores = result.get("scores", {})
    return {
        "match_cards": [{"domain": domain, "score": score} for domain, score in scores.items()],
        "weekly_progress": 18,
        "balance_reminders": ["45-minute sprint", "One visible output", "One hobby block", "One feedback request"],
        "transition_months": transition_months,
    }


def build_resume(profile, career, missing):
    skills = profile.get("skills", []) or ["communication", "self-learning"]
    hobbies = profile.get("hobbies", []) or ["career exploration"]
    return {
        "headline": f"Entry-level {career['title']} explorer",
        "summary": f"Motivated learner exploring {career['title']} with transferable skills in {', '.join(skills[:4])}.",
        "transferable_skills": skills,
        "projects": [
            f"Build a mini {career['title']} portfolio project",
            f"Document a 7-day trial around {hobbies[0]}",
            "Publish a learning log with before/after improvements",
        ],
        "courses": FREE_RESOURCES.get(career["domain"], FREE_RESOURCES["Business"])[:3],
        "keywords": [career["title"], career["domain"], *missing[:4]],
    }


def build_second_life_preview(career):
    return {
        "pivot": career["title"],
        "bridge_courses": FREE_RESOURCES.get(career["domain"], [])[:3],
        "break_even": "Estimate 6-12 months if you keep income stable and build proof before switching.",
        "sunk_cost_note": "Past effort is data, not a prison. Reuse transferable skills before abandoning your current field.",
    }


def build_second_life_plan(form):
    monthly_income = int(form.get("monthly_income") or 0)
    monthly_cost = int(form.get("monthly_cost") or 0)
    savings = int(form.get("savings") or 0)
    runway = savings // max(monthly_cost, 1)
    target = form.get("target", "Digital Marketer")
    bridge_cost = 25000
    months_to_break_even = 6 if monthly_income and runway >= 6 else 12
    return {
        "target": target,
        "runway": runway,
        "sunk_cost_score": form.get("years_current", "0"),
        "bridge_courses": ["Free foundation course", "Portfolio sprint", "Internship/freelance test"],
        "break_even": f"{months_to_break_even}-{months_to_break_even + 4} months if bridge cost stays near Rs {bridge_cost:,}.",
        "advice": "Keep your current income while testing the pivot until you have proof, savings, or paid work.",
    }


def build_ics(timeline):
    start = date.today() + timedelta(days=1)
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//LifeCompass//Timeline//EN"]
    for index, week in enumerate(timeline["weeks"][:2]):
        for day_index, task in enumerate(week["tasks"]):
            event_date = start + timedelta(days=index * 7 + day_index)
            lines.extend(
                [
                    "BEGIN:VEVENT",
                    f"UID:lifecompass-{index}-{day_index}@local",
                    f"DTSTAMP:{datetime.utcnow():%Y%m%dT%H%M%SZ}",
                    f"DTSTART:{event_date:%Y%m%d}T180000",
                    f"DTEND:{event_date:%Y%m%d}T184500",
                    f"SUMMARY:{task[:60]}",
                    "END:VEVENT",
                ]
            )
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines)


def mentor_reply(message, result):
    message_lower = message.lower()
    first = (result.get("primary_paths") or [{"title": "a practical path", "backup": "a related backup option"}])[0]
    if "salary" in message_lower or "money" in message_lower:
        reality = _career_reality(first)
        return f"For {first['title']}, money can be good but uneven early. Reality check: {reality['salary']}. Build proof before depending on it fully."
    if "backup" in message_lower or "risk" in message_lower:
        return f"Your backup should be close to the same skill family: {first.get('backup', 'portfolio work, internships, or teaching basics')}. Do not make a high-risk switch without a bridge."
    if "start" in message_lower:
        return f"Start with a 7-day trial for {first['title']}: 45 minutes daily, one tiny output, and a Sunday review of energy, difficulty, and curiosity."
    return f"Honest mentor note: {first['title']} is worth exploring, but only trust it after small real experiments. Keep a backup, build proof, and compare your energy after 7 days."


def create_text_pdf(title, sections):
    buffer = BytesIO()
    with PdfPages(buffer) as pdf:
        fig = plt.figure(figsize=(8.27, 11.69))
        fig.patch.set_facecolor("white")
        y = 0.95
        fig.text(0.08, y, title, fontsize=20, weight="bold")
        y -= 0.05
        for heading, body in sections:
            fig.text(0.08, y, heading, fontsize=13, weight="bold")
            y -= 0.028
            lines = []
            if isinstance(body, list):
                for item in body:
                    lines.extend(wrap(f"- {item}", 90))
            else:
                lines = wrap(str(body), 90)
            for line in lines:
                if y < 0.08:
                    pdf.savefig(fig, bbox_inches="tight")
                    plt.close(fig)
                    fig = plt.figure(figsize=(8.27, 11.69))
                    fig.patch.set_facecolor("white")
                    y = 0.95
                fig.text(0.08, y, line, fontsize=10)
                y -= 0.022
            y -= 0.018
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)
    buffer.seek(0)
    return buffer
