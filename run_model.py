
import tarfile
from ibm_watson_machine_learning import APIClient
import time
import time, json, base64
import pandas as pd
import pandas as pd
from pathlib import Path

EXCEL_PATH = Path("inputs/Parametros.xlsx")   # ajusta si lo tienes en otra ruta
OUT_DIR = Path("inputs/csv")                  # generaremos aquí los CSV
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Mapea: nombre de hoja -> nombre de archivo CSV
SHEETS = {
    "Turnos": "Turnos.csv",
    "Disponibilidad Maquinas": "Disponibilidad_Maquinas.csv",
    "Productividad Máquina_Caja": "Productividad_Maquina_Caja.csv",
    "Tiempo de Setup por máquina": "Tiempo_de_Setup_por_maquina.csv",
    "Duracion Turno": "Duracion_Turno.csv",
}

# Lee y exporta cada hoja a CSV (UTF-8 con BOM para Excel-friendly)
for sheet, csv_name in SHEETS.items():
    print(f"Convirtiendo hoja '{sheet}' -> {csv_name}")
    df = pd.read_excel(EXCEL_PATH, sheet_name=sheet, dtype=str)
    # Limpieza opcional: normaliza espacios y NaN
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    df.to_csv(OUT_DIR / csv_name, index=False, encoding="utf-8-sig")
print("Listo. CSVs en:", OUT_DIR.resolve())
import pandas as pd
from pathlib import Path

EXCEL_PATH = Path("inputs/Parametros.xlsx")   # ajusta si lo tienes en otra ruta
OUT_DIR = Path("inputs/csv")                  # generaremos aquí los CSV
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Mapea: nombre de hoja -> nombre de archivo CSV
SHEETS = {
    "Turnos": "Turnos.csv",
    "Disponibilidad Maquinas": "Disponibilidad_Maquinas.csv",
    "Productividad Máquina_Caja": "Productividad_Maquina_Caja.csv",
    "Tiempo de Setup por máquina": "Tiempo_de_Setup_por_maquina.csv",
    "Duracion Turno": "Duracion_Turno.csv",
}

# Lee y exporta cada hoja a CSV (UTF-8 con BOM para Excel-friendly)
for sheet, csv_name in SHEETS.items():
    print(f"Convirtiendo hoja '{sheet}' -> {csv_name}")
    df = pd.read_excel(EXCEL_PATH, sheet_name=sheet, dtype=str)
    # Limpieza opcional: normaliza espacios y NaN
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    df.to_csv(OUT_DIR / csv_name, index=False, encoding="utf-8-sig")
print("Listo. CSVs en:", OUT_DIR.resolve())
WML_API_KEY = "kI0O5Y3O037SXJ3_1wiDBKFABLKAIrEaAsicdjI0Hu0t"
SPACE_ID = "5b4f04fa-0a13-4793-8922-e0228341aa72"
WML_URL = "https://us-south.ml.cloud.ibm.com"
# empaquetado_tar.py (o integra estos fragmentos en tu script actual)
import os, tarfile
from pathlib import Path

MODEL_TAR = "modelo.tar.gz"

def reset(tarinfo):
    tarinfo.uid = tarinfo.gid = 0
    tarinfo.uname = tarinfo.gname = "root"
    return tarinfo

# Archivos a incluir en la RAÍZ del tar
FILES_TO_ADD = [
    ("./scripts/model.py", "model.py"),
    ("./inputs/csv/Turnos.csv", "Turnos.csv"),
    ("./inputs/csv/Disponibilidad_Maquinas.csv", "Disponibilidad_Maquinas.csv"),
    ("./inputs/csv/Productividad_Maquina_Caja.csv", "Productividad_Maquina_Caja.csv"),
    ("./inputs/csv/Tiempo_de_Setup_por_maquina.csv", "Tiempo_de_Setup_por_maquina.csv"),
    ("./inputs/csv/Duracion_Turno.csv", "Duracion_Turno.csv"),
]

if os.path.exists(MODEL_TAR):
    os.remove(MODEL_TAR)

with tarfile.open(MODEL_TAR, "w:gz") as tar:
    for src, arc in FILES_TO_ADD:
        if not Path(src).exists():
            raise FileNotFoundError(f"Falta el archivo: {src}")
        tar.add(src, arcname=arc, filter=reset)

# (opcional) Verifica contenido del tar
with tarfile.open(MODEL_TAR, "r:gz") as t:
    print("[TAR] Contenido:", t.getnames())

MODEL_NAME = "modelo-cajas"
DEPLOYMENT_NAME = "Modelo Transportistas Deployment"

# ---------------- Utils ----------------
def b64_to_file(b64_content, path):
    with open(path, "wb") as f:
        f.write(base64.b64decode(b64_content))

def print_if_exists(path, max_chars=2000):
    if os.path.exists(path):
        print("\n===== {} =====".format(path))
        with open(path, "r", errors="ignore") as f:
            text = f.read()
        print(text[:max_chars] + ("\n...[truncado]..." if len(text) > max_chars else ""))

# ---------------- Cliente WML ----------------
client = APIClient({"apikey": WML_API_KEY, "url": WML_URL})
client.set.default_space(SPACE_ID)

# -------- Software spec y subida de modelo --------
spec_id = client.software_specifications.get_id_by_name("do_20.1")
meta = {
    client.repository.ModelMetaNames.NAME: MODEL_NAME,
    client.repository.ModelMetaNames.TYPE: "do-docplex_20.1",
    client.repository.ModelMetaNames.SOFTWARE_SPEC_UID: spec_id,
}
model_details = client.repository.store_model(model=MODEL_TAR, meta_props=meta)
model_uid = client.repository.get_model_id(model_details)
print("Modelo subido. UID:", model_uid)

# -------- Despliegue --------
deploy_props = {
    client.deployments.ConfigurationMetaNames.NAME: DEPLOYMENT_NAME,
    client.deployments.ConfigurationMetaNames.DESCRIPTION: "Modelo de DO",
    client.deployments.ConfigurationMetaNames.BATCH: {},
    client.deployments.ConfigurationMetaNames.HARDWARE_SPEC: {"name": "S", "num_nodes": 1},
}
deployment_details = client.deployments.create(model_uid, meta_props=deploy_props)
deployment_uid = client.deployments.get_id(deployment_details)
print("Despliegue creado. UID:", deployment_uid)

# -------- Payload con LOG como output + JSON results --------
solve_payload = {
    "solve_parameters": {
        "oaas.logAttachmentName": "log.txt",     # nombre del log
        "oaas.logTailEnabled": "true",
        "oaas.resultsFormat": "JSON"             # JSON facilita parsear solution.json
    },
    client.deployments.DecisionOptimizationMetaNames.INPUT_DATA: [
        # Si tu model.py espera archivos, puedes omitir aquí si los empaquetaste en el tar.
        # Si prefieres inyectar: {"id":"Parametros.xlsx","values": base64.b64encode(open("inputs/Parametros.xlsx","rb").read()).decode()}
    ],
    client.deployments.DecisionOptimizationMetaNames.OUTPUT_DATA: [
        {"id": "solution.json"},     # solución
        {"id": "log.txt"},           # <--- forzamos que el log se publique como output
        {"id": ".*\\.txt"},          # cualquier otro log de texto
        {"id": ".*"}                 # y cualquier otro adjunto por si acaso
    ]
}

# -------- Crear job --------
job_details = client.deployments.create_job(deployment_uid, solve_payload)
job_uid = client.deployments.get_job_uid(job_details)
print("Job UID:", job_uid)

# -------- Polling --------
terminal_states = {"completed", "failed", "canceled", "error", "unknown"}
while True:
    state = job_details["entity"]["decision_optimization"]["status"]["state"]
    print(state + "...")
    if state in terminal_states:
        break
    time.sleep(5)
    job_details = client.deployments.get_job_details(job_uid)

# -------- Estado del solver --------
solve_state = job_details["entity"]["decision_optimization"].get("solve_state", {})
solve_status = solve_state.get("solve_status", "n/a")
print("Estado del trabajo (solve_status):", solve_status)

# -------- Descargar outputs (incluye log.txt si existe) --------
outputs = job_details["entity"]["decision_optimization"].get("output_data", [])
saved = []
for outp in outputs:
    out_id = outp.get("id")
    content_b64 = outp.get("content")
    if content_b64:
        # Normalmente 'content' viene en base64 cuando el archivo es "pequeño/inline"
        local_name = out_id if out_id else "output.bin"
        # Evita path traversal
        local_name = os.path.basename(local_name)
        try:
            b64_to_file(content_b64, local_name)
            saved.append(local_name)
        except Exception as e:
            print(f"No pude guardar {local_name}: {e}")

# -------- A veces los logs aparecen en 'attachments' --------
attachments = job_details["entity"]["decision_optimization"].get("attachments", [])
for att in attachments:
    # Cuando el cliente los devuelve inline, suele venir 'content' base64;
    # si solo viene un 'href', el SDK los descarga automáticamente en output_data,
    # pero intentamos capturarlo por si está inline aquí.
    att_id = att.get("id", "attachment")
    if "content" in att:
        local_name = os.path.basename(att_id)
        try:
            b64_to_file(att["content"], local_name)
            saved.append(local_name)
        except Exception as e:
            print(f"No pude guardar adjunto {local_name}: {e}")

if saved:
    print("Archivos de salida guardados:", saved)

# -------- Mostrar log si está --------
for candidate in ["log.txt", "job.log", "solve.log"]:
    if os.path.exists(candidate):
        print_if_exists(candidate, max_chars=4000)

# -------- Guardar solution.json si existiera --------
if os.path.exists("solution.json"):
    try:
        with open("solution.json", "r") as f:
            sol = json.load(f)
        print("\nsolution.json cargado correctamente.")
    except Exception as e:
        print("solution.json no es JSON válido (o resultados estaban en XML).", e)