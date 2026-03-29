// CONFIGURAȚIE - Numele fișierului descărcat de robotul GitHub
const CSV_FILE = 'water-licence-attributes.csv';

// Elemente din pagină
const searchInput = document.getElementById('q');
const resultsDiv = document.getElementById('res');
const statusDiv = document.getElementById('status');

let database = [];
let index;

// 1. Inițializăm motorul de căutare ultra-rapid
index = new FlexSearch.Document({
    document: {
        id: "id",
        index: ["ClientLegalName", "AuthorisationReference"] // Căutăm în aceste coloane
    },
    tokenize: "forward", // Permite căutarea parțială (ex: "Smi" găsește "Smith")
    worker: true         // Rulează căutarea pe un fir separat pentru a nu bloca site-ul
});

// 2. Încărcăm și procesăm fișierul CSV
console.log("Se încearcă încărcarea datelor...");

Papa.parse(CSV_FILE, {
    download: true,
    header: true,
    skipEmptyLines: true,
    complete: function(results) {
        // Verificăm dacă fișierul are date
        if (!results.data || results.data.length === 0 || results.data[0].ClientLegalName === undefined) {
            statusDiv.innerHTML = "⚠️ Eroare: Fișierul de date este gol sau neformatat. Așteaptă update-ul robotului.";
            statusDiv.style.color = "red";
            return;
        }

        // Curățăm datele și le adăugăm în indexul de căutare
        database = results.data.map((item, idx) => ({
            id: idx,
            ClientLegalName: item.ClientLegalName || "Nespecificat",
            AuthorisationReference: item.AuthorisationReference || "N/A",
            Address: item.PostalAddressLine1 || "Fără adresă"
        }));

        // Adăugăm fiecare rând în motorul de căutare
        database.forEach(doc => index.add(doc));

        // Activăm interfața
        statusDiv.innerHTML = `✅ Date încărcate cu succes: <b>${database.length.toLocaleString()}</b> înregistrări.`;
        statusDiv.style.color = "green";
        searchInput.disabled = false;
        searchInput.placeholder = "Introdu minim 3 caractere...";
        console.log("Indexare finalizată.");
    },
    error: function(err) {
        statusDiv.innerHTML = "❌ Eroare critică la citirea fișierului. Verifică dacă fișierul există pe GitHub.";
        statusDiv.style.color = "red";
        console.error("Eroare PapaParse:", err);
    }
});

// 3. Logica de căutare (se declanșează când tastezi)
searchInput.oninput = function() {
    const val = this.value.trim();
    resultsDiv.innerHTML = '';

    if (val.length < 3) {
        return; // Nu căutăm dacă avem sub 3 litere
    }

    // Căutăm în index (limităm la 50 de rezultate pentru viteză)
    const results = index.search(val, { limit: 50, enrich: true });

    if (results.length > 0 && results[0].result.length > 0) {
        // FlexSearch returnează ID-urile rândurilor găsite
        results[0].result.forEach(id => {
            const item = database[id];
            renderResult(item);
        });
    } else {
        resultsDiv.innerHTML = '<p style="color: #999; text-align: center;">Niciun rezultat găsit.</p>';
    }
};

// 4. Funcție pentru afișarea rezultatelor sub formă de carduri
function renderResult(item) {
    const card = document.createElement('div');
    card.className = 'item'; // Asigură-te că ai stilul .item în HTML
    card.innerHTML = `
        <div style="margin-bottom: 10px; border-bottom: 1px solid #eee; padding-bottom: 10px;">
            <strong style="text-transform: uppercase; color: #0056b3;">${item.ClientLegalName}</strong><br>
            <span style="font-size: 0.85rem; background: #eef; padding: 2px 5px; border-radius: 3px;">Ref: ${item.AuthorisationReference}</span><br>
            <small style="color: #666;">📍 ${item.Address}</small>
        </div>
    `;
    resultsDiv.appendChild(card);
}
