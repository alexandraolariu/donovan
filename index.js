const FILE_PATH = 'water-licence-attributes.csv'; // Numele fișierului creat de robot
const searchInput = document.getElementById('searchInput');
const resultsDiv = document.getElementById('results');
const statusDiv = document.getElementById('status');

let database = [];
let index = new FlexSearch.Document({
    document: { id: "id", index: ["ClientLegalName", "AuthorisationReference"] },
    tokenize: "forward"
});

// Citim fișierul descărcat de robot
Papa.parse(FILE_PATH, {
    download: true,
    header: true,
    skipEmptyLines: true,
    complete: function(results) {
        database = results.data.map((item, idx) => ({ id: idx, ...item }));
        database.forEach(doc => index.add(doc));
        
        statusDiv.innerHTML = `✅ <b>${database.length.toLocaleString()}</b> înregistrări la zi.`;
        searchInput.disabled = false;
    },
    error: function() {
        statusDiv.innerHTML = "❌ Eroare: Fișierul CSV nu a fost găsit. Rulează 'Actions' pe GitHub!";
    }
});

searchInput.addEventListener('input', function() {
    const val = this.value;
    resultsDiv.innerHTML = '';
    if (val.length < 3) return;

    const results = index.search(val, { limit: 30, enrich: true });
    if (results.length > 0 && results[0].result) {
        results[0].result.forEach(id => {
            const item = database[id];
            const div = document.createElement('div');
            div.className = 'card';
            div.innerHTML = `
                <strong>${item.ClientLegalName}</strong><br>
                <small>REF: ${item.AuthorisationReference} | Adresă: ${item.PostalAddressLine1 || 'N/A'}</small>
            `;
            resultsDiv.appendChild(div);
        });
    }
});
