from flask import Flask, jsonify, request, render_template
import threading, json, os

app = Flask(__name__)

# ============================
# Classe Distributore
# ============================
class Distributore:
    def __init__(self, id, provincia, citta, benzina, diesel, prezzo_benzina, prezzo_diesel, lat, lon):
        self.id = id
        self.provincia = provincia
        self.citta = citta
        self.benzina = benzina
        self.diesel = diesel
        self.prezzo_benzina = prezzo_benzina
        self.prezzo_diesel = prezzo_diesel
        self.lat = lat
        self.lon = lon

    def to_dict(self):
        return {
            "id": self.id,
            "provincia": self.provincia,
            "citta": self.citta,
            "benzina": self.benzina,
            "diesel": self.diesel,
            "prezzo_benzina": self.prezzo_benzina,
            "prezzo_diesel": self.prezzo_diesel,
            "lat": self.lat,
            "lon": self.lon
        }

# ============================
# Lista distributori in memoria
# ============================
_db_lock = threading.Lock()
DATA_FILE = "data.json"

_distributori = []

# 5 distributori iniziali
iniziali = [
    Distributore(1, "Milano", "Milano", 5000, 3000, 1.85, 1.75, 45.4642, 9.19),
    Distributore(2, "Roma", "Roma", 4000, 2500, 1.83, 1.70, 41.9028, 12.4964),
    Distributore(3, "Napoli", "Napoli", 3500, 2000, 1.80, 1.68, 40.8522, 14.2681),
    Distributore(4, "Torino", "Torino", 4500, 2800, 1.82, 1.72, 45.0703, 7.6869),
    Distributore(5, "Palermo", "Palermo", 3000, 1500, 1.78, 1.65, 38.1157, 13.3615)
]

# Carica i distributori iniziali se il file non esiste
if not os.path.exists(DATA_FILE):
    _distributori.extend(iniziali)
else:
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            arr = json.load(f)
            for o in arr:
                _distributori.append(Distributore(
                    int(o["id"]), o["provincia"], o["citta"],
                    float(o["benzina"]), float(o["diesel"]),
                    float(o["prezzo_benzina"]), float(o["prezzo_diesel"]),
                    float(o["lat"]), float(o["lon"])
                ))
        except:
            _distributori.extend(iniziali)  # fallback se il JSON è corrotto

# ============================
# Funzioni di supporto
# ============================
def find_by_id(id):
    return next((d for d in _distributori if d.id == id), None)

def save_to_file():
    with _db_lock:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([d.to_dict() for d in _distributori], f, indent=2, ensure_ascii=False)

# ============================
# API Endpoints
# ============================

@app.route("/")
def homepage():
    return render_template("index.html")

@app.route("/api/distributori", methods=["GET"])
def lista_distributori():
    with _db_lock:
        return jsonify([d.to_dict() for d in sorted(_distributori, key=lambda x: x.id)])

@app.route("/api/distributori/<int:id>", methods=["GET"])
def get_distributore(id):
    d = find_by_id(id)
    if not d:
        return jsonify({"error": "Distributore non trovato"}), 404
    return jsonify(d.to_dict())

@app.route("/api/distributori", methods=["POST"])
def add_distributore():
    data = request.get_json()
    required = ["id","provincia","citta","benzina","diesel","prezzo_benzina","prezzo_diesel","lat","lon"]
    for f in required:
        if f not in data:
            return jsonify({"error": f"Manca campo: {f}"}), 400
    if find_by_id(int(data["id"])):
        return jsonify({"error": "ID già esistente"}), 409
    nuovo = Distributore(
        int(data["id"]), data["provincia"], data["citta"],
        float(data["benzina"]), float(data["diesel"]),
        float(data["prezzo_benzina"]), float(data["prezzo_diesel"]),
        float(data["lat"]), float(data["lon"])
    )
    with _db_lock:
        _distributori.append(nuovo)
    save_to_file()
    return jsonify({"message": "Distributore aggiunto", "distributore": nuovo.to_dict()}), 201

@app.route("/api/search")
def search():
    q = request.args.get("q","").strip().lower()
    if not q:
        return jsonify({"error":"Parametro q richiesto"}),400
    results = []
    for d in _distributori:
        if q == str(d.id).lower() or q in d.citta.lower() or q in d.provincia.lower():
            results.append(d.to_dict())
    if not results:
        return jsonify({"error":"Nessun distributore trovato"}),404
    return jsonify(results)

@app.route("/api/provincia/prezzi", methods=["PUT"])
def update_prezzi_provincia():
    data = request.get_json()
    provincia = data.get("provincia", "").strip()
    prezzo_benzina = data.get("prezzo_benzina")
    prezzo_diesel = data.get("prezzo_diesel")

    if not provincia:
        return jsonify({"error": "Provincia richiesta"}), 400

    updated = 0
    for d in _distributori:
        if d.provincia.lower() == provincia.lower():
            if prezzo_benzina is not None:
                d.prezzo_benzina = float(prezzo_benzina)
            if prezzo_diesel is not None:
                d.prezzo_diesel = float(prezzo_diesel)
            updated += 1

    if updated == 0:
        return jsonify({"error": "Nessun distributore trovato per questa provincia"}), 404

    save_to_file()
    return jsonify({"message": f"Prezzi aggiornati per {updated} distributori in {provincia}"})


# ============================
# Avvio
# ============================
if __name__ == "__main__":
    app.run(debug=True)
