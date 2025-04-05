(() => {
    function extractTextFromPage() {
      const tags = document.querySelectorAll("p, span, div");
      const textContent = [...tags]
        .map(el => el.innerText)
        .filter(Boolean)
        .join(" ")
        .trim();
      return textContent.slice(0, 500);
    }
  
    async function analyzeText(text) {
      try {
        const response = await fetch("http://localhost:8000/analyze", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text, threshold: 0.75 })
        });
  
        if (!response.ok) throw new Error("Server error");
  
        const result = await response.json();
        console.log("Analysis Result:", result);
        showOverlay(result);
      } catch (error) {
        console.error("Failed to analyze:", error);
      }
    }
  
    function showOverlay(result) {
      const overlay = document.createElement("div");
      overlay.style.position = "fixed";
      overlay.style.bottom = "20px";
      overlay.style.right = "20px";
      overlay.style.padding = "10px";
      overlay.style.background = "#111";
      overlay.style.color = "#eee";
      overlay.style.borderRadius = "8px";
      overlay.style.zIndex = 9999;
      overlay.style.fontSize = "14px";
      overlay.style.maxWidth = "300px";
      overlay.style.lineHeight = "1.4";
      overlay.innerHTML = `
        <strong>Toxicity:</strong> ${result.is_toxic ? "⚠️ Likely Toxic" : "✅ Clean"}<br/>
        <strong>Scores:</strong><br/>
        ${Object.entries(result.scores)
          .map(([key, value]) => `${key}: ${(value * 100).toFixed(1)}%`)
          .join("<br/>")}
      `;
      document.body.appendChild(overlay);
      setTimeout(() => overlay.remove(), 10000);
    }
  
    // Wrapped in an IIFE to prevent global scope pollution
    const pageText = extractTextFromPage();
    if (pageText.length > 20) {
      analyzeText(pageText);
    }
  })();  