document.addEventListener("DOMContentLoaded", () => {
    
    // Pages / Views
    const landingPage = document.getElementById("landing-page");
    const predictionPage = document.getElementById("prediction-page");
    const resultPage = document.getElementById("result-page");

    // Buttons
    const startBtn = document.getElementById("start-btn");
    const backBtn = document.getElementById("back-btn");
    const resetBtn = document.getElementById("reset-btn");
    
    // Form & Overlays
    const form = document.getElementById("prediction-form");
    const loader = document.getElementById("loading-overlay");

    // Auth & Profile UI Elements
    const userStatusText = document.getElementById("user-status-text");
    const authTriggerBtn = document.getElementById("auth-trigger-btn");
    const logoutBtn = document.getElementById("logout-btn");
    const landingHistory = document.getElementById("landing-history");
    const historyTableBody = document.getElementById("history-table-body");

    // Modal elements
    const authModal = document.getElementById("auth-modal");
    const authForm = document.getElementById("auth-form");
    const tabLogin = document.getElementById("tab-login");
    const tabRegister = document.getElementById("tab-register");
    const authUsernameInput = document.getElementById("auth-username");
    const authPasswordInput = document.getElementById("auth-password");
    const authErrorMsg = document.getElementById("auth-error-msg");
    const authCloseBtn = document.getElementById("auth-close-btn");
    const authSubmitBtn = document.getElementById("auth-submit-btn");

    let authMode = "login"; // "login" or "register"
    let currentUser = JSON.parse(localStorage.getItem("currentUser")) || null;

    // Initialize UI based on current user state
    updateUserSessionUI();

    // Utility: Switch views smoothly
    function switchView(hideEl, showEl) {
        hideEl.classList.remove("active");
        setTimeout(() => {
            hideEl.classList.add("hidden");
            showEl.classList.remove("hidden");
            
            // Force reflow
            void showEl.offsetWidth; 
            showEl.classList.add("active");
        }, 400); // matches CSS transition time
    }

    // 1. Landing -> Form
    startBtn.addEventListener("click", () => {
        switchView(landingPage, predictionPage);
    });

    // 2. Form -> Landing (Back Button)
    backBtn.addEventListener("click", () => {
        form.reset();
        switchView(predictionPage, landingPage);
    });

    // 3. Form Submission
    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        // Show loading spinner
        loader.classList.remove("hidden");

        // Gather form data into JSON
        const formData = new FormData(form);
        const dataObj = {};
        formData.forEach((value, key) => { dataObj[key] = value; });

        // Add user_id if logged in
        if (currentUser) {
            dataObj["user_id"] = currentUser.user_id;
        }

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(dataObj)
            });

            const result = await response.json();

            if (response.ok) {
                // Display the results
                renderResults(result.prediction, result.confidence);
                // Switch view
                switchView(predictionPage, resultPage);
                // Refresh history if logged in
                if (currentUser) {
                    loadPredictionHistory();
                }
            } else {
                alert(`Prediction Error: \n${result.detail || "Server Error"}`);
            }
        } catch (error) {
            console.error("Fetch Error:", error);
            alert("Failed to connect to the server. Ensure the API backend is running!");
        } finally {
            // Hide loading spinner regardless of success/fail
            setTimeout(() => {
                loader.classList.add("hidden");
            }, 600); // slight minimum delay for visual smoothness
        }
    });

    // 4. Render Results Function
    function renderResults(prediction, confidence) {
        const badge = document.getElementById("risk-badge");
        const text = document.getElementById("risk-text");
        const confPercent = document.getElementById("confidence-percentage");
        const healthTip = document.getElementById("health-tip");

        // Reset badge classes
        badge.classList.remove("high-risk", "low-risk");

        if (prediction === "High Risk") {
            badge.classList.add("high-risk");
            text.textContent = "High Risk";
            confPercent.textContent = `${confidence}% Confidence`;
            
            // Subtle health tips
            healthTip.innerHTML = `
                Note: This AI flagged potential indicators pointing toward higher risk.<br>
                <em>Consult a licensed healthcare professional for a formal evaluation, comprehensive memory screening, and personalized care plan.</em>
            `;
        } else {
            badge.classList.add("low-risk");
            text.textContent = "Low Risk";
            confPercent.textContent = `${confidence}% Confidence`;
            
            healthTip.innerHTML = `
                Good news: The algorithm does not currently detect standard high-risk patterns.<br>
                <em>Maintain a healthy diet, stay physically active, and engage in regular cognitive exercises!</em>
            `;
        }
    }

    // 5. Result -> Form (Reset Flow)
    resetBtn.addEventListener("click", () => {
        form.reset();
        switchView(resultPage, predictionPage);
    });

    // --- Authentication Event Handlers ---

    // Open Modal
    authTriggerBtn.addEventListener("click", () => {
        authErrorMsg.classList.add("hidden");
        authForm.reset();
        setAuthMode("login");
        authModal.classList.remove("hidden");
    });

    // Close Modal
    authCloseBtn.addEventListener("click", () => {
        authModal.classList.add("hidden");
    });

    // Switch Tabs
    tabLogin.addEventListener("click", () => setAuthMode("login"));
    tabRegister.addEventListener("click", () => setAuthMode("register"));

    function setAuthMode(mode) {
        authMode = mode;
        authErrorMsg.classList.add("hidden");
        if (mode === "login") {
            tabLogin.classList.add("active");
            tabRegister.classList.remove("active");
            authSubmitBtn.textContent = "Login";
        } else {
            tabRegister.classList.add("active");
            tabLogin.classList.remove("active");
            authSubmitBtn.textContent = "Sign Up";
        }
    }

    // Submit Auth Form
    authForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        authErrorMsg.classList.add("hidden");

        const username = authUsernameInput.value;
        const password = authPasswordInput.value;
        const endpoint = authMode === "login" ? "/api/auth/login" : "/api/auth/register";

        try {
            const response = await fetch(endpoint, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password })
            });
            const result = await response.json();

            if (response.ok) {
                currentUser = {
                    user_id: result.user_id,
                    username: result.username
                };
                localStorage.setItem("currentUser", JSON.stringify(currentUser));
                updateUserSessionUI();
                authModal.classList.add("hidden");
            } else {
                authErrorMsg.textContent = result.detail || "Authentication failed.";
                authErrorMsg.classList.remove("hidden");
            }
        } catch (error) {
            console.error("Auth Error:", error);
            authErrorMsg.textContent = "Connection to authentication service failed.";
            authErrorMsg.classList.remove("hidden");
        }
    });

    // Logout Action
    logoutBtn.addEventListener("click", () => {
        currentUser = null;
        localStorage.removeItem("currentUser");
        updateUserSessionUI();
    });

    // Update UI based on auth state
    function updateUserSessionUI() {
        if (currentUser) {
            userStatusText.textContent = `User ID: ${currentUser.username}`;
            authTriggerBtn.classList.add("hidden");
            logoutBtn.classList.remove("hidden");
            loadPredictionHistory();
        } else {
            userStatusText.textContent = "Guest Mode";
            authTriggerBtn.classList.remove("hidden");
            logoutBtn.classList.add("hidden");
            landingHistory.classList.add("hidden");
            historyTableBody.innerHTML = "";
        }
    }

    // Load History records
    async function loadPredictionHistory() {
        if (!currentUser) return;
        try {
            const response = await fetch(`/api/predictions?user_id=${currentUser.user_id}`);
            const result = await response.json();

            if (response.ok && result.predictions.length > 0) {
                historyTableBody.innerHTML = "";
                result.predictions.forEach(p => {
                    const row = document.createElement("tr");
                    const dateCell = document.createElement("td");
                    dateCell.textContent = p.timestamp;

                    const metricsCell = document.createElement("td");
                    metricsCell.textContent = `Age: ${p.age}, BMI: ${p.bmi}, BP: ${p.blood_pressure}`;

                    const riskCell = document.createElement("td");
                    const riskBadge = document.createElement("span");
                    riskBadge.className = `history-badge ${p.prediction_label === "High Risk" ? "high-risk" : "low-risk"}`;
                    riskBadge.textContent = p.prediction_label;
                    riskCell.appendChild(riskBadge);

                    const confCell = document.createElement("td");
                    confCell.textContent = `${p.confidence_score}%`;

                    row.appendChild(dateCell);
                    row.appendChild(metricsCell);
                    row.appendChild(riskCell);
                    row.appendChild(confCell);
                    historyTableBody.appendChild(row);
                });
                landingHistory.classList.remove("hidden");
            } else {
                landingHistory.classList.add("hidden");
                historyTableBody.innerHTML = "";
            }
        } catch (error) {
            console.error("History fetch failed:", error);
        }
    }
});
