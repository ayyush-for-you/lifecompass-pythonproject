# LifeCompass

LifeCompass is a Flask-based career and life guidance system that helps users make structured decisions across traditional and unconventional paths.

## Features

- Career Discovery questionnaire for confused students.
- Balance & Rediscovery questionnaire for burned-out users.
- OOP-based profile and recommendation models.
- Pandas and NumPy scoring engine.
- CSV-based career data and submission storage.
- Matplotlib interest distribution graph.
- Skill gap analysis with roadmap and free resources.
- Financial reality cards with salary, cost, demand, scholarship, and freelance signals.
- Anonymous peer success stories and 7-day career trials.
- Weekly timeline planner with `.ics` calendar export and Google Calendar link.
- AI Mentor chatbot with Gemini/Ollama integration and local fallback.
- Burnout recovery tracker and Second Life Mode for career switchers 25+.
- Community challenge mockups, badges, auto-generated resume PDF, report PDF, WhatsApp share, dark mode, and India-specific links.

## Run Locally

```bash
pip install -r requirements.txt
python app.py
```

Open:

```text
http://127.0.0.1:5000/
```

## Project Structure

```text
LifeCompass/
|-- app.py
|-- models.py
|-- recommender.py
|-- data/
|   |-- careers.csv
|-- templates/
|   |-- home.html
|   |-- mode1.html
|   |-- mode2.html
|   |-- result.html
|-- static/
|   |-- style.css
```
