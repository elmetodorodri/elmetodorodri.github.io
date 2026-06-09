import json, urllib.request, os
from datetime import datetime

COOKIES = os.environ.get("ONPE_COOKIES", "")

BASE = "https://resultadosegundavuelta.onpe.gob.pe/presentacion-backend"
HEADERS = {
    "accept": "*/*", "accept-language": "es-ES,es;q=0.9",
    "content-type": "application/json",
    "referer": "https://resultadosegundavuelta.onpe.gob.pe/main/resumen",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/148.0.0.0 Safari/537.36",
    "cookie": COOKIES,
}

def fetch(path):
    req = urllib.request.Request(BASE + path, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode())["data"]

def cand(arr, nombre):
    p = next((x for x in arr if nombre in x.get("nombreCandidato","")), None)
    return {"votos": p["totalVotosValidos"], "pct": p["porcentajeVotosValidos"]} if p else None

try:
    totales  = fetch("/resumen-general/totales?idEleccion=10&tipoFiltro=eleccion")
    part     = fetch("/resumen-general/participantes?idEleccion=10&tipoFiltro=eleccion")
    tots_nac = fetch("/resumen-general/totales?idEleccion=10&tipoFiltro=ambito_geografico&idAmbitoGeografico=1")
    part_nac = fetch("/resumen-general/participantes?idEleccion=10&tipoFiltro=ambito_geografico&idAmbitoGeografico=1")
    tots_ext = fetch("/resumen-general/totales?idEleccion=10&tipoFiltro=ambito_geografico&idAmbitoGeografico=2")
    part_ext = fetch("/resumen-general/participantes?idEleccion=10&tipoFiltro=ambito_geografico&idAmbitoGeografico=2")

    kf   = cand(part,     "FUJIMORI")
    rs   = cand(part,     "SANCHEZ")
    kf_n = cand(part_nac, "FUJIMORI")
    rs_n = cand(part_nac, "SANCHEZ")
    kf_e = cand(part_ext, "FUJIMORI")
    rs_e = cand(part_ext, "SANCHEZ")

    diff  = abs(kf["votos"] - rs["votos"])
    lider = "KF" if kf["pct"] > rs["pct"] else "RS"

    data = {
        "success": True,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "totales": totales,
        "kf": kf, "rs": rs,
        "tots_nac": tots_nac, "kf_nac": kf_n, "rs_nac": rs_n,
        "tots_ext": tots_ext, "kf_ext": kf_e, "rs_ext": rs_e,
        "diff": diff, "lider": lider,
    }
    print("OK —", datetime.now().strftime("%H:%M:%S"))

except Exception as e:
    print("ERROR:", e)
    # Si hay datos anteriores los mantenemos, si no creamos un placeholder
    if os.path.exists("datos.json"):
        print("Manteniendo datos anteriores")
        exit(0)
    data = {"success": False, "error": str(e), "timestamp": datetime.now().strftime("%H:%M:%S")}

with open("datos.json", "w") as f:
    json.dump(data, f, ensure_ascii=False)
