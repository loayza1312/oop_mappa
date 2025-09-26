let map = L.map('map').setView([41.8719, 12.5674], 6); // Centro Italia
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

let markers = [];

function showOnMap(distributors) {
    // Rimuove i vecchi marker
    markers.forEach(m => map.removeLayer(m));
    markers = [];

    distributors.forEach(d => {
        // Aggiunge marker con popup dettagliato
        let marker = L.marker([d.lat, d.lon]).addTo(map)
            .bindPopup(
                `<b>ID:</b> ${d.id}<br>` +
                `<b>Città:</b> ${d.citta}<br>` +
                `<b>Provincia:</b> ${d.provincia}<br>` +
                `<b>Benzina:</b> ${d.benzina} L<br>` +
                `<b>Diesel:</b> ${d.diesel} L<br>` +
                `<b>Prezzo Benzina:</b> €${d.prezzo_benzina.toFixed(2)}<br>` +
                `<b>Prezzo Diesel:</b> €${d.prezzo_diesel.toFixed(2)}`
            );
        markers.push(marker);
    });

    if (distributors.length > 0) {
        map.setView([distributors[0].lat, distributors[0].lon], 10);
    }
}

// Carica tutti i distributori
async function loadDistributors() {
    let res = await fetch('/api/distributori');
    let data = await res.json();
    showOnMap(data);
}

// Cerca per ID o città
async function searchDistributor() {
    let query = document.getElementById('searchInput').value.trim();

    if (!query) {
        alert("Inserisci un ID o una città!");
        return;
    }

    let res;
    if (!isNaN(query)) {
        res = await fetch(`/api/distributori/${query}`);
        if (res.status === 404) {
            alert("Nessun distributore trovato con questo ID");
            return;
        }
        let data = await res.json();
        showOnMap([data]);
    } else {
        res = await fetch(`/api/search?q=${query}`);
        let data = await res.json();
        if (data.error) {
            alert(data.error);
            return;
        }
        showOnMap(data);
    }
}

// Aggiungi distributore dalla pagina
async function addDistributor() {
    let id = parseInt(document.getElementById('add_id').value);
    let provincia = document.getElementById('add_provincia').value.trim();
    let citta = document.getElementById('add_citta').value.trim();
    let benzina = parseFloat(document.getElementById('add_benzina').value);
    let diesel = parseFloat(document.getElementById('add_diesel').value);
    let prezzo_benzina = parseFloat(document.getElementById('add_prezzo_benzina').value);
    let prezzo_diesel = parseFloat(document.getElementById('add_prezzo_diesel').value);
    let lat = parseFloat(document.getElementById('add_lat').value);
    let lon = parseFloat(document.getElementById('add_lon').value);

    let distributore = {
        id, provincia, citta, benzina, diesel, prezzo_benzina, prezzo_diesel, lat, lon
    };

    let res = await fetch('/api/distributori', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(distributore)
    });

    let data = await res.json();
    if (res.status === 201) {
        alert("Distributore aggiunto con successo!");
        loadDistributors();
    } else {
        alert("Errore: " + data.error);
    }
}

async function updatePrezziProvincia() {
    let provincia = document.getElementById('provincia_prezzi').value.trim();
    let prezzoB = parseFloat(document.getElementById('prezzo_benzina_prov').value);
    let prezzoD = parseFloat(document.getElementById('prezzo_diesel_prov').value);

    if (!provincia) {
        alert("Inserisci una provincia!");
        return;
    }

    let body = {};
    if (!isNaN(prezzoB)) body.prezzo_benzina = prezzoB;
    if (!isNaN(prezzoD)) body.prezzo_diesel = prezzoD;

    if (Object.keys(body).length === 0) {
        alert("Inserisci almeno un prezzo da aggiornare");
        return;
    }

    let res = await fetch('/api/provincia/prezzi', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provincia, ...body })
    });

    let data = await res.json();
    if (res.ok) {
        alert(data.message);
        loadDistributors(); // aggiorna la mappa con i nuovi prezzi
    } else {
        alert("Errore: " + data.error);
    }
}


// Carica tutti i distributori all'avvio
loadDistributors();
