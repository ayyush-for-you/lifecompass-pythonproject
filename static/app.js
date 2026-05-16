const noteMap = {
    build_app: "You seem drawn to making useful digital things. That often points toward tech, product thinking, or applied AI.",
    run_experiment: "Curiosity about evidence and experiments is a strong science signal.",
    make_song: "Creative expression is showing up clearly. That can become a serious path when paired with practice.",
    train_match: "Discipline and performance matter to you. Sports or fitness-related paths deserve space in your result.",
    launch_idea: "You are noticing independence and initiative. Business paths may fit your style.",
    logic: "You enjoy structure and clear reasoning. That strengthens tech and science recommendations.",
    people: "People-centered problem solving is valuable in business, content, management, and communication roles.",
    expression: "Your answers are leaning toward expressive work. Creative careers may not be a side note here.",
    performance: "You seem comfortable with improvement under pressure, which is useful in sports and performance fields.",
    systems: "You may like building order out of complexity. That is useful in tech, business, and leadership roles.",
    exhausted: "Today may call for recovery first. The plan can start smaller than your ambition.",
    stretched: "You do not need a dramatic reset. You may need protected space and a lighter rhythm.",
    flat: "Feeling flat is information, not failure. Gentle re-entry can help you test what still matters.",
    restless: "There is energy here. The result can help turn restlessness into a practical experiment.",
    ready: "Good. The plan can be a little more active while still staying balanced.",
    creative_play: "Creative play without judgment can be a real recovery tool, not a distraction.",
    physical_reset: "Your body may be asking to be part of the plan. That matters.",
    structured_plan: "A clear structure can reduce decision fatigue and turn scattered energy into progress.",
};

function initParallaxWorld() {
    const field = document.createElement("div");
    field.className = "parallax-field";
    field.setAttribute("aria-hidden", "true");
    field.innerHTML = `
        <div class="parallax-layer route-lines route-lines-one"></div>
        <div class="parallax-layer route-lines route-lines-two"></div>
        <div class="parallax-layer compass-rings"></div>
        <div class="parallax-layer drifting-marks">
            <span></span><span></span><span></span><span></span><span></span>
        </div>
    `;
    document.body.prepend(field);

    let ticking = false;

    function paint() {
        const scroll = window.scrollY || 0;
        document.documentElement.style.setProperty("--scroll-depth", `${scroll}px`);
        document.documentElement.style.setProperty("--hero-shift", `${Math.min(scroll * 0.18, 120)}px`);
        ticking = false;
    }

    function requestPaint() {
        if (!ticking) {
            window.requestAnimationFrame(paint);
            ticking = true;
        }
    }

    window.addEventListener("scroll", requestPaint, { passive: true });
    window.addEventListener("pointermove", (event) => {
        const x = event.clientX / window.innerWidth - 0.5;
        const y = event.clientY / window.innerHeight - 0.5;
        document.documentElement.style.setProperty("--pointer-x", x.toFixed(3));
        document.documentElement.style.setProperty("--pointer-y", y.toFixed(3));
    });
    paint();
}

function initGuidedForm(form) {
    const progressBar = form.querySelector("[data-progress-bar]");
    const progressCount = form.querySelector("[data-progress-count]");
    const note = form.querySelector("[data-compass-note]");
    const questionNames = [
        ...new Set([...form.querySelectorAll('input[type="radio"][name^="q_"]')].map((input) => input.name)),
    ];
    let latestAnswer = "";

    function update() {
        const answered = questionNames.filter((name) => form.querySelector(`input[name="${name}"]:checked`));
        const percent = questionNames.length ? (answered.length / questionNames.length) * 100 : 0;

        if (progressBar) {
            progressBar.style.width = `${percent}%`;
        }

        if (progressCount) {
            progressCount.textContent = answered.length;
        }

        form.querySelectorAll(".answer-grid label, .pill-grid label").forEach((label) => {
            const input = label.querySelector("input");
            label.classList.toggle("is-selected", Boolean(input && input.checked));
        });

        if (note && latestAnswer && noteMap[latestAnswer]) {
            note.textContent = noteMap[latestAnswer];
        }
    }

    form.addEventListener("change", (event) => {
        if (event.target.matches('input[type="radio"]')) {
            latestAnswer = event.target.value;
            const label = event.target.closest("label");
            if (label) {
                label.classList.remove("choice-pop");
                window.requestAnimationFrame(() => label.classList.add("choice-pop"));
            }
        }
        update();
    });
    update();
}

initParallaxWorld();

document.querySelectorAll("[data-guided-form]").forEach(initGuidedForm);

document.querySelectorAll(".question-card, .soft-section, .chart-section, .option-list, .plan-list, .skill-pills").forEach((item, index) => {
    item.setAttribute("data-reveal", "");
    item.style.setProperty("--reveal-delay", `${Math.min(index * 45, 260)}ms`);
});

const revealItems = document.querySelectorAll("[data-reveal]");
if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("is-visible");
                    observer.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.14 }
    );

    revealItems.forEach((item) => observer.observe(item));
} else {
    revealItems.forEach((item) => item.classList.add("is-visible"));
}

document.querySelectorAll(".interactive-card").forEach((card) => {
    card.addEventListener("pointermove", (event) => {
        const rect = card.getBoundingClientRect();
        const x = ((event.clientX - rect.left) / rect.width - 0.5) * 6;
        const y = ((event.clientY - rect.top) / rect.height - 0.5) * -6;
        card.style.setProperty("--tilt-x", `${y}deg`);
        card.style.setProperty("--tilt-y", `${x}deg`);
    });

    card.addEventListener("pointerleave", () => {
        card.style.setProperty("--tilt-x", "0deg");
        card.style.setProperty("--tilt-y", "0deg");
    });
});

document.querySelectorAll(".question-card, .soft-section, .chart-section, .journey-band").forEach((surface) => {
    surface.addEventListener("pointermove", (event) => {
        const rect = surface.getBoundingClientRect();
        const x = ((event.clientX - rect.left) / rect.width) * 100;
        const y = ((event.clientY - rect.top) / rect.height) * 100;
        surface.style.setProperty("--surface-x", `${x}%`);
        surface.style.setProperty("--surface-y", `${y}%`);
    });
});

document.addEventListener("click", (event) => {
    const target = event.target.closest(".button, .answer-grid label, .pill-grid label, .journey-steps span");
    if (!target) {
        return;
    }

    target.classList.remove("choice-pop");
    window.requestAnimationFrame(() => target.classList.add("choice-pop"));
});

const darkToggle = document.querySelector("[data-dark-toggle]");
if (darkToggle) {
    darkToggle.addEventListener("click", () => {
        document.body.classList.toggle("dark-mode");
        localStorage.setItem("lifecompass-dark", document.body.classList.contains("dark-mode") ? "yes" : "no");
    });
}

if (localStorage.getItem("lifecompass-dark") === "yes") {
    document.body.classList.add("dark-mode");
}

const chatForm = document.querySelector("[data-chat-form]");
if (chatForm) {
    const log = document.querySelector("[data-chat-log]");
    chatForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const input = chatForm.querySelector("input[name='message']");
        const message = input.value.trim();
        if (!message) {
            return;
        }
        const userBubble = document.createElement("div");
        userBubble.className = "chat-message user";
        userBubble.textContent = message;
        log.appendChild(userBubble);
        input.value = "";
        const waiting = document.createElement("div");
        waiting.className = "chat-message bot";
        waiting.textContent = "Thinking...";
        log.appendChild(waiting);
        const response = await fetch("/api/mentor", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message }),
        });
        const data = await response.json();
        waiting.textContent = data.reply;
        log.scrollTop = log.scrollHeight;
    });
}
