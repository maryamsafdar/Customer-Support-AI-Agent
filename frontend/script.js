
const API = localStorage.getItem("BASE_URL") || "https://web-production-b381e.up.railway.app/";
document.getElementById("ask").addEventListener("click", async () => {
  const q = document.getElementById("q").value.trim();
  if (!q) return;
  const out = document.getElementById("out");
  out.textContent = "Thinking...";
  try {
    const r = await fetch(`${API}/ask`, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({question: q})
    });
    const data = await r.json();
    out.textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    out.textContent = "API error: " + e;
  }
});
