const form = document.getElementById("recommendation-form");
const budgetInput = document.getElementById("budget");
const budgetRange = document.getElementById("budget-range");
const budgetDisplay = document.getElementById("budget-display");
const menuList = document.getElementById("menu-list");
const statusText = document.getElementById("status-text");
const summaryBadge = document.getElementById("summary-badge");
const totalCost = document.getElementById("total-cost");
const remainingBudget = document.getElementById("remaining-budget");
const totalValue = document.getElementById("total-value");
const estimatedPeople = document.getElementById("estimated-people");
const thinkingPanel = document.getElementById("thinking-panel");
const generateButton = document.getElementById("generate-button");
const themeToggle = document.getElementById("theme-toggle");
const scrollButtons = document.querySelectorAll("[data-scroll-target]");

const formatCurrency = (value) => `Rs ${Number(value).toFixed(2)}`;

const updateRangeFill = (value) => {
    const min = Number(budgetRange.min);
    const max = Number(budgetRange.max);
    const percent = ((Number(value) - min) / (max - min)) * 100;
    budgetRange.style.background = `linear-gradient(90deg, var(--accent) ${percent}%, rgba(211, 122, 61, 0.18) ${percent}%)`;
};

const syncBudget = (value, source = "input") => {
    const normalized = Math.max(1, Number(value || 0));
    if (source === "range") {
        budgetInput.value = normalized;
    } else {
        budgetInput.value = normalized;
        budgetRange.value = Math.min(Number(budgetRange.max), normalized);
    }
    budgetDisplay.textContent = formatCurrency(budgetInput.value);
    updateRangeFill(budgetInput.value);
};

const renderEmptyState = (title, message) => {
    menuList.innerHTML = `
        <div class="empty-state">
            <h3>${title}</h3>
            <p>${message}</p>
        </div>
    `;
};

const renderError = (message) => {
    menuList.innerHTML = `<div class="error-banner">${message}</div>`;
    statusText.textContent = "Unable to generate menu.";
    summaryBadge.textContent = "Check input";
    totalCost.textContent = "Rs 0";
    remainingBudget.textContent = "Rs 0";
    totalValue.textContent = "0";
    estimatedPeople.textContent = "0";
};

const createMenuCard = (item) => `
    <article class="menu-card tilt-card">
        <div class="menu-image-wrap">
            <img src="${item.image}" alt="${item.name}">
        </div>
        <div class="menu-content">
            <div class="menu-top">
                <div>
                    <div class="menu-meta">
                        <span>${item.category}</span>
                        <span class="type-pill ${item.type}">${item.type}</span>
                    </div>
                    <h3>${item.name}</h3>
                </div>
                <span class="qty-pill">Qty ${item.quantity}</span>
            </div>
            <p>${item.description}</p>
            <div class="menu-price">
                <strong>${formatCurrency(item.subtotal)}</strong>
                <small>${formatCurrency(item.price)} each • Total value ${item.total_value}</small>
            </div>
        </div>
    </article>
`;

const setLoadingState = (loading) => {
    thinkingPanel.hidden = !loading;
    generateButton.disabled = loading;
    generateButton.querySelector(".button-label").textContent = loading
        ? "Generating Smart Menu..."
        : "Get Recommendation";
    if (loading) {
        summaryBadge.textContent = "AI thinking...";
    }
};

const renderRecommendation = (data) => {
    statusText.textContent = data.message;
    summaryBadge.textContent = `${data.cycle_count} greedy cycle(s)`;
    totalCost.textContent = formatCurrency(data.total_cost);
    remainingBudget.textContent = formatCurrency(data.remaining_budget);
    totalValue.textContent = data.total_value;
    estimatedPeople.textContent = data.total_portions;

    if (!data.selected_items.length) {
        renderEmptyState(
            "No affordable combination found",
            "Try increasing the budget or reducing the selected filters."
        );
        return;
    }

    menuList.innerHTML = data.selected_items.map(createMenuCard).join("");
};

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const payload = {
        budget: budgetInput.value,
        people: form.people.value,
        preference: form.preference.value,
        categories: Array.from(form.querySelectorAll('input[name="categories"]:checked')).map(
            (input) => input.value
        ),
    };

    setLoadingState(true);
    statusText.textContent = "Evaluating menu combinations with the greedy algorithm.";
    summaryBadge.textContent = "AI thinking...";

    try {
        const response = await fetch("/recommend", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(payload),
        });

        const data = await response.json();

        if (!response.ok) {
            renderError(data.error || "Something went wrong while generating the menu.");
            return;
        }

        renderRecommendation(data);
    } catch (error) {
        renderError("Server connection failed. Please make sure the Flask app is running.");
    } finally {
        setLoadingState(false);
    }
});

budgetRange.addEventListener("input", () => {
    syncBudget(budgetRange.value, "range");
});

budgetInput.addEventListener("input", () => {
    syncBudget(budgetInput.value, "input");
});

scrollButtons.forEach((button) => {
    button.addEventListener("click", () => {
        const target = document.querySelector(button.dataset.scrollTarget);
        if (target) {
            target.scrollIntoView({ behavior: "smooth", block: "start" });
        }
    });
});

document.querySelectorAll(".ripple-button").forEach((button) => {
    button.addEventListener("click", (event) => {
        const ripple = document.createElement("span");
        ripple.className = "ripple";
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        ripple.style.width = `${size}px`;
        ripple.style.height = `${size}px`;
        ripple.style.left = `${event.clientX - rect.left - size / 2}px`;
        ripple.style.top = `${event.clientY - rect.top - size / 2}px`;
        button.appendChild(ripple);
        window.setTimeout(() => ripple.remove(), 650);
    });
});

themeToggle.addEventListener("click", () => {
    document.body.classList.toggle("dark-mode");
    const isDark = document.body.classList.contains("dark-mode");
    localStorage.setItem("catering-theme", isDark ? "dark" : "light");
});

const savedTheme = localStorage.getItem("catering-theme");
if (savedTheme === "dark") {
    document.body.classList.add("dark-mode");
}

syncBudget(budgetInput.value);
renderEmptyState(
    "No menu generated yet",
    "Submit your input to view the recommended catering menu."
);
