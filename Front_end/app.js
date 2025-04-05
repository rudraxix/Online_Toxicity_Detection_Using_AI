async function checkToxicity() {
    const text = document.getElementById("userInput").value;
  
    const response = await fetch("http://127.0.0.1:8000/predict", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ text: text })
    });
  
    const data = await response.json();
    const resultDiv = document.getElementById("result");
  
    if (data && data.toxicity_score) {
      resultDiv.innerHTML = `<strong>Toxicity Score:</strong> ${data.toxicity_score.toFixed(2)}<br />
        <strong>Classification:</strong> ${data.predicted_label}`;
    } else {
      resultDiv.textContent = "Error fetching toxicity score.";
    }
  }  