// CONFIGURARE
const FILE_PATH = 'water-licence-attributes.csv'; // Numele fișierului descarcat lângă index.html
const searchInput = document.getElementById('searchInput');
const resultsDiv = document.getElementById('results');
const statusText = document.getElementById('status-text');
const loader = document.getElementById('loader');

let database = [];
let index;

// Inițializare motor de căutare FlexSearch
// "Document" permite căutarea în mai multe coloane simultan
index = new FlexSearch.Document({
    document: {
        id: "id",
        index: ["ClientLegalName", "AuthorisationReference", "PostalAddressLine1", "PostalPropertyName"]
    },
    tokenize: "forward", // Permite căutarea parțială (ex: "STRAD" găsește "STRADBROKE")
    context: true
});

// Încărcarea datelor
console.log("Începe descărcarea CSV...");

Papa.parse(FILE_PATH, {
    download: true,
    header: true,
    dynamicTyping: true,
    skipEmptyLines: true,
    complete: function(results) {
        database = results.data.map((item, idx) => ({ id: idx, ...item }));
        
        // Populăm indexul de căutare
        database.forEach(doc => index.add(doc));
        
        // Update interfață
        statusText.innerHTML = `✅ <b>${database.length.toLocaleString()}</b> înregistrări active indexate.`;
        loader.classList.add('hidden');
        searchInput.disabled = false;
        searchInput.focus();
        console.log("Indexare completă.");
    },
    error: function(err) {
        statusText.innerText = "❌ Eroare la citirea fișierului CSV.";
        loader.classList.add('hidden');
        console.error(err);
    }
});

// Logica de căutare pe evenimentul de tastare
searchInput.addEventListener('input', function(e) {
    const query = e.target.value.trim();
    resultsDiv.innerHTML = '';

    if (query.length < 2) return;

    // Căutăm în index (limităm la 50 de rezultate pentru performanță vizuală)
    const searchResults = index.search(query, { 
        limit: 50, 
        enrich: true,
        suggest: true 
    });

    if (searchResults.length > 0) {
        // Combinăm rezultatele din toate câmpurile indexate
        const uniqueIds = new Set();
        searchResults.forEach(fieldResults => {
            fieldResults.result.forEach(id => uniqueIds.add(id));
        });

        uniqueIds.forEach(id => {
            renderCard(database[id]);
        });
    } else {
        resultsDiv.innerHTML = '<div class="no-results">Nu am găsit niciun rezultat pentru căutarea ta.</div>';
    }
});

// Funcție pentru a genera un card cu date
function renderCard(item) {
    const card = document.createElement('div');
    card.className = 'card';
    card.innerHTML = `
        <h3>${item.ClientLegalName || 'Fără Nume'}</h3>
        <p><span class="ref">REF: ${item.AuthorisationReference}</span></p>
        <p>📍 <b>Adresă:</b> ${item.PostalAddressLine1 || '-'}, ${item.PostalPropertyName || ''}</p>
        <p>📑 <b>Status:</b> ${item.AuthorisationStatus || 'Activ'}</p>
    `;
    resultsDiv.appendChild(card);
}