chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "analyzeText") {
      fetch("http://localhost:8000/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: message.text,
          threshold: 0.75
        })
      })
      .then(res => res.json())
      .then(data => {
        console.log("Analysis result:", data);
  
        chrome.scripting.executeScript({
          target: { tabId: sender.tab.id },
          func: showTooltip,
          args: [message.text, data]
        });
      })
      .catch(err => console.error("Failed to analyze:", err));
    }
  });
  
  function showTooltip(text, analysis) {
    const tooltip = document.createElement("div");
    tooltip.style.position = "fixed";
    tooltip.style.bottom = "20px";
    tooltip.style.right = "20px";
    tooltip.style.padding = "10px";
    tooltip.style.background = "#222";
    tooltip.style.color = "#fff";
    tooltip.style.borderRadius = "8px";
    tooltip.style.zIndex = 9999;
    tooltip.style.boxShadow = "0 2px 8px rgba(0,0,0,0.3)";
    tooltip.style.maxWidth = "300px";
    tooltip.innerHTML = `
      <strong>Analysis:</strong><br>
      <em>${text}</em><br><br>
      Toxic: ${analysis.is_toxic ? "⚠️ Yes" : "✅ No"}<br>
      Scores: ${Object.entries(analysis.scores).map(([k, v]) => `${k}: ${(v * 100).toFixed(1)}%`).join("<br>")}
    `;
    document.body.appendChild(tooltip);
    setTimeout(() => tooltip.remove(), 8000);
  }  