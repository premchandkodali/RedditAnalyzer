document.getElementById('analyzeForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const link = document.getElementById('redditLink').value;
    const resultDiv = document.getElementById('personaResult');
    resultDiv.style.display = 'none';
    resultDiv.innerHTML = '<em>Analyzing...</em>';
    resultDiv.style.display = 'block';

    try {
        const response = await fetch('http://localhost:5000/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ link })
        });
        if (!response.ok) throw new Error('Failed to analyze');
        let data = await response.json();
        // If data is a stringified JSON, parse it
        if (typeof data === 'string') {
            try { data = JSON.parse(data); } catch {}
        }
        // If data.raw is a stringified JSON, parse it
        if (data && typeof data.raw === 'string' && data.raw.trim().startsWith('{')) {
            try { data = JSON.parse(data.raw); } catch {}
        }
        if (data.error) {
            resultDiv.innerHTML = `<span style="color:red;font-size:1.2rem;">${data.error}</span>`;
        } else {
            resultDiv.innerHTML = renderPersona(data);
        }
    } catch (err) {
        resultDiv.innerHTML = '<span style="color:red">Error: ' + err.message + '</span>';
    }
});

function renderPersona(data) {
    if (data.raw) {
        // Fallback: show raw text if structured fields are missing
        return `<pre>${data.raw}</pre>`;
    }
    // Helper for bar chart (simulate values for demo)
    function renderBarList(items) {
        if (!Array.isArray(items)) return '';
        return `<ul class="bar-list">` + items.map((item, i) => {
            // Simulate bar width (descending)
            const width = 90 - i * 10;
            return `<li><span class="bar-label">${item}</span><span class="bar"><span class="bar-inner" style="width:${width}%"></span></span></li>`;
        }).join('') + `</ul>`;
    }
    return `
    <div class="persona-left">
        <div class="persona-title">${data.name || ""}</div>
        <ul class="persona-meta-list">
            <li><span>Age:</span> <span>${data.age || ""}</span></li>
            <li><span>Occupation:</span> <span>${data.occupation || ""}</span></li>
            <li><span>Status:</span> <span>${data.status || ""}</span></li>
            <li><span>Location:</span> <span>${data.location || ""}</span></li>
            <li><span>Tier:</span> <span>${data.tier || ""}</span></li>
            <li><span>Archetype:</span> <span>${data.archetype || ""}</span></li>
        </ul>
        <div class="persona-quote">${data.quote || ""}</div>
        <div class="persona-section">
            <h3>Motivations</h3>
            ${renderBarList(data.motivations)}
        </div>
        <div class="persona-section">
            <h3>Personality</h3>
            ${renderBarList(data.personality)}
        </div>
    </div>
    <div class="persona-right">
        <div class="persona-section">
            <h3>Behaviour & Habits</h3>
            <ul>${(data.behaviour && Array.isArray(data.behaviour)) ? data.behaviour.map(b=>`<li>${b}</li>`).join('') : (data.behaviour || "")}</ul>
        </div>
        <div class="persona-section">
            <h3>Goals & Needs</h3>
            <ul>${(data.goals && Array.isArray(data.goals)) ? data.goals.map(g=>`<li>${g}</li>`).join('') : (data.goals || "")}</ul>
        </div>
        <div class="persona-section">
            <h3>Frustrations</h3>
            <ul>${(data.frustrations && Array.isArray(data.frustrations)) ? data.frustrations.map(f=>`<li>${f}</li>`).join('') : (data.frustrations || "")}</ul>
        </div>
    </div>
    `;
}
