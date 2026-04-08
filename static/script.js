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
            } else {
                alert(`Prediction Error: \n${result.error}`);
            }
        } catch (error) {
            console.error("Fetch Error:", error);
            alert("Failed to connect to the server. Ensure Flask API is running!");
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

});
