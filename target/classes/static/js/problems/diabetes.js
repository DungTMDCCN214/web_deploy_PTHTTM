document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("diabetesForm");
  const resultCard = document.getElementById("resultCard");

  const parseNumber = (value, fallback = 0) => {
    const parsed = Number.parseFloat((value || "").toString().replace(",", "."));
    return Number.isFinite(parsed) ? parsed : fallback;
  };

  const parseInteger = (value, fallback = 0) => {
    const parsed = Number.parseInt(value, 10);
    return Number.isFinite(parsed) ? parsed : fallback;
  };

  if (!form) {
    return;
  }

  form.addEventListener("submit", async function (e) {
    e.preventDefault();

    const formData = new FormData(form);
    const data = {
      pregnancies: parseInteger(formData.get("pregnancies")),
      glucose: parseNumber(formData.get("glucose")),
      bloodPressure: parseNumber(formData.get("bloodPressure")),
      skinThickness: 0,
      insulin: 0,
      bmi: parseNumber(formData.get("bmi")),
      diabetesPedigreeFunction: 0.47,
      age: parseInteger(formData.get("age")),
    };

    try {
      const response = await fetch("/api/diabetes/predict", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      const responseData = await response.json();

      if (!response.ok) {
        throw new Error(responseData.message || responseData.error || "API du doan bi loi.");
      }

      resultCard.classList.remove("d-none");
      document.getElementById("riskLevel").innerText =
        "Muc do nguy co: " + responseData.riskLevel;
      document.getElementById("probability").innerText =
        ((responseData.probability || 0) * 100).toFixed(1) + "%";
      document.getElementById("advice").innerText =
        responseData.advice || "Khong co loi khuyen.";
    } catch (err) {
      console.error("Loi API du doan:", err);
      resultCard.classList.remove("d-none");
      document.getElementById("riskLevel").innerText = "Khong du doan duoc";
      document.getElementById("probability").innerText = "0%";
      document.getElementById("advice").innerText = err.message;
    }
  });
});
