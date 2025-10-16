"""
Sistema de Optimización de Cajas - Ejecución del Modelo
Este script procesa los datos de demanda y parámetros para una planta específica,
empaqueta el modelo y lo ejecuta en IBM Watson Machine Learning.
"""

import os
import sys
import tarfile
import time
import json
import base64
import pandas as pd
from pathlib import Path

# Import IBM Watson ML solo cuando sea necesario para evitar errores si no está instalado
try:
    from ibm_watson_machine_learning import APIClient
    WATSON_ML_AVAILABLE = True
except ImportError:
    WATSON_ML_AVAILABLE = False
    APIClient = None

# =============================================================================
# CONFIGURACIÓN
# =============================================================================

# Rutas de archivos
EXCEL_PARAMETROS = Path("inputs/Parametros.xlsx")
EXCEL_DEMANDA = Path("inputs/Libro7.xlsx")
OUT_DIR = Path("inputs/csv")
MODEL_TAR = "modelo.tar.gz"

# Credenciales IBM Watson ML
WML_API_KEY = "kI0O5Y3O037SXJ3_1wiDBKFABLKAIrEaAsicdjI0Hu0t"
SPACE_ID = "5b4f04fa-0a13-4793-8922-e0228341aa72"
WML_URL = "https://us-south.ml.cloud.ibm.com"

# Nombres del modelo y deployment
MODEL_NAME = "modelo-cajas"
DEPLOYMENT_NAME = "Modelo Transportistas Deployment"

# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================

def b64_to_file(b64_content, path):
    """Convierte contenido base64 a archivo."""
    with open(path, "wb") as f:
        f.write(base64.b64decode(b64_content))


def print_if_exists(path, max_chars=2000):
    """Imprime el contenido de un archivo si existe."""
    if os.path.exists(path):
        print(f"\n{'='*60}")
        print(f"{path}")
        print('='*60)
        with open(path, "r", errors="ignore") as f:
            text = f.read()
        print(text[:max_chars] + ("\n...[truncado]..." if len(text) > max_chars else ""))


def reset(tarinfo):
    """Resetea permisos para empaquetado tar."""
    tarinfo.uid = tarinfo.gid = 0
    tarinfo.uname = tarinfo.gname = "root"
    return tarinfo


# =============================================================================
# PROCESAMIENTO DE DATOS
# =============================================================================

def procesar_datos_planta(planta: str):
    """
    Procesa los datos de Excel para una planta específica.

    Args:
        planta: Nombre de la planta (MOSTAZAL, MALLOA, MOLINA)

    Returns:
        bool: True si el procesamiento fue exitoso
    """
    print(f"\n{'='*60}")
    print(f"PROCESANDO DATOS PARA PLANTA: {planta}")
    print('='*60)

    # Crear directorio de salida
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        # =====================================================================
        # 1. PROCESAR DEMANDA
        # =====================================================================
        print(f"\n[1/6] Procesando demanda desde {EXCEL_DEMANDA}...")

        if not EXCEL_DEMANDA.exists():
            print(f"[ERROR] ERROR: No se encontró {EXCEL_DEMANDA}")
            return False

        demanda = pd.read_excel(EXCEL_DEMANDA)
        print(f"   [OK] Leidos {len(demanda)} registros de demanda")

        # Filtrar por planta si existe la columna
        if 'DES_PLANTA' in demanda.columns:
            demanda_planta = demanda[demanda['DES_PLANTA'] == planta].copy()
            if len(demanda_planta) == 0:
                print(f"   [WARNING] ADVERTENCIA: No hay datos de demanda para {planta}")
                print(f"   Usando toda la demanda disponible")
                demanda_planta = demanda
            else:
                print(f"   [OK] Filtrados {len(demanda_planta)} registros para {planta}")
        else:
            print(f"   [WARNING] Columna 'DES_PLANTA' no encontrada, usando todos los datos")
            demanda_planta = demanda

        # Guardar demanda
        demanda_csv = OUT_DIR / "demanda.csv"
        demanda_planta.to_csv(demanda_csv, index=False, encoding="utf-8-sig")
        print(f"   [OK] Guardado: {demanda_csv}")

        # =====================================================================
        # 2. PROCESAR PARÁMETROS
        # =====================================================================
        print(f"\n[2/6] Procesando parámetros desde {EXCEL_PARAMETROS}...")

        if not EXCEL_PARAMETROS.exists():
            print(f"[ERROR] ERROR: No se encontró {EXCEL_PARAMETROS}")
            return False

        # Definir hojas a procesar
        sheets_map = {
            "Turnos": "Turnos.csv",
            "Disponibilidad Maquinas": "Disponibilidad_Maquinas.csv",
            "Productividad Máquina_Caja": "Productividad_Maquina_Caja.csv",
            "Tiempo de Setup por máquina": "Tiempo_de_Setup_por_maquina.csv",
            "Duracion Turno": "Duracion_Turno.csv",
        }

        # Procesar cada hoja
        for sheet_name, csv_name in sheets_map.items():
            print(f"\n   Procesando hoja: '{sheet_name}'")

            try:
                # Leer hoja
                df = pd.read_excel(EXCEL_PARAMETROS, sheet_name=sheet_name, dtype=str)
                print(f"      - Leídas {len(df)} filas")

                # Filtrar por planta si existe la columna
                if 'PLANTA' in df.columns:
                    df_planta = df[df['PLANTA'] == planta].copy()
                    if len(df_planta) == 0:
                        print(f"      [WARNING] No hay datos para {planta} en esta hoja, usando todos los datos")
                        df_planta = df
                    else:
                        print(f"      [OK] Filtradas {len(df_planta)} filas para {planta}")
                else:
                    print(f"      [INFO] No hay columna PLANTA, usando todos los datos")
                    df_planta = df

                # Limpiar datos
                df_planta = df_planta.map(lambda x: x.strip() if isinstance(x, str) else x)

                # Guardar CSV
                csv_path = OUT_DIR / csv_name
                df_planta.to_csv(csv_path, index=False, encoding="utf-8-sig")
                print(f"      [OK] Guardado: {csv_path}")

            except Exception as e:
                print(f"      [ERROR] ERROR procesando '{sheet_name}': {e}")
                return False

        print(f"\n   [OK] Todos los parámetros procesados correctamente")
        return True

    except Exception as e:
        print(f"\n[ERROR] ERROR GENERAL: {e}")
        import traceback
        traceback.print_exc()
        return False


# =============================================================================
# EMPAQUETADO
# =============================================================================

def empaquetar_modelo():
    """Empaqueta todos los archivos CSV y el modelo en un tar.gz."""
    print(f"\n[3/6] Empaquetando modelo...")

    # Archivos a incluir
    files_to_add = [
        ("./scripts/model.py", "model.py"),
        ("./inputs/csv/Turnos.csv", "Turnos.csv"),
        ("./inputs/csv/Disponibilidad_Maquinas.csv", "Disponibilidad_Maquinas.csv"),
        ("./inputs/csv/Productividad_Maquina_Caja.csv", "Productividad_Maquina_Caja.csv"),
        ("./inputs/csv/Tiempo_de_Setup_por_maquina.csv", "Tiempo_de_Setup_por_maquina.csv"),
        ("./inputs/csv/Duracion_Turno.csv", "Duracion_Turno.csv"),
        ("./inputs/csv/demanda.csv", "demanda.csv")
    ]

    # Verificar archivos
    for src, _ in files_to_add:
        if not Path(src).exists():
            print(f"   [ERROR] ERROR: Falta el archivo: {src}")
            return False

    # Eliminar tar anterior si existe
    if os.path.exists(MODEL_TAR):
        os.remove(MODEL_TAR)
        print(f"   [OK] Eliminado tar anterior")

    # Crear tar
    try:
        with tarfile.open(MODEL_TAR, "w:gz") as tar:
            for src, arc in files_to_add:
                tar.add(src, arcname=arc, filter=reset)
                print(f"   [OK] Agregado: {arc}")

        # Verificar contenido
        with tarfile.open(MODEL_TAR, "r:gz") as t:
            contents = t.getnames()
            print(f"\n   [OK] Tar creado con {len(contents)} archivos:")
            for item in contents:
                print(f"      - {item}")

        return True

    except Exception as e:
        print(f"   [ERROR] ERROR al crear tar: {e}")
        return False


# =============================================================================
# EJECUCIÓN EN IBM WATSON ML
# =============================================================================

def ejecutar_en_watson_ml():
    """Sube el modelo a IBM Watson ML y ejecuta la optimización."""

    print(f"\n[4/6] Conectando a IBM Watson ML...")

    # Verificar que Watson ML esté disponible
    if not WATSON_ML_AVAILABLE:
        print(f"\n[ERROR] ERROR: ibm-watson-machine-learning no está instalado")
        print(f"\nPara instalar, ejecuta:")
        print(f"   pip install ibm-watson-machine-learning")
        print(f"\nNota: Requiere pandas<2.2.0 que no es compatible con Python 3.13")
        print(f"Considera usar Python 3.11 o 3.12 para ejecutar este módulo")
        return False

    try:
        # Conectar a Watson ML
        client = APIClient({"apikey": WML_API_KEY, "url": WML_URL})
        client.set.default_space(SPACE_ID)
        print(f"   [OK] Conectado a Watson ML")

        # =====================================================================
        # Subir modelo
        # =====================================================================
        print(f"\n[5/6] Subiendo modelo...")

        spec_id = client.software_specifications.get_id_by_name("do_20.1")

        meta = {
            client.repository.ModelMetaNames.NAME: MODEL_NAME,
            client.repository.ModelMetaNames.TYPE: "do-docplex_20.1",
            client.repository.ModelMetaNames.SOFTWARE_SPEC_UID: spec_id,
        }

        model_details = client.repository.store_model(model=MODEL_TAR, meta_props=meta)
        model_uid = client.repository.get_model_id(model_details)
        print(f"   [OK] Modelo subido con UID: {model_uid}")

        # =====================================================================
        # Crear deployment
        # =====================================================================
        print(f"\n   Creando deployment...")

        deploy_props = {
            client.deployments.ConfigurationMetaNames.NAME: DEPLOYMENT_NAME,
            client.deployments.ConfigurationMetaNames.DESCRIPTION: "Modelo de optimización de cajas",
            client.deployments.ConfigurationMetaNames.BATCH: {},
            client.deployments.ConfigurationMetaNames.HARDWARE_SPEC: {"name": "S", "num_nodes": 1},
        }

        deployment_details = client.deployments.create(model_uid, meta_props=deploy_props)
        deployment_uid = client.deployments.get_id(deployment_details)
        print(f"   [OK] Deployment creado con UID: {deployment_uid}")

        # =====================================================================
        # Crear y ejecutar job
        # =====================================================================
        print(f"\n[6/6] Ejecutando optimización...")

        solve_payload = {
            "solve_parameters": {
                "oaas.logAttachmentName": "log.txt",
                "oaas.logTailEnabled": "true",
                "oaas.resultsFormat": "JSON"
            },
            client.deployments.DecisionOptimizationMetaNames.INPUT_DATA: [],
            client.deployments.DecisionOptimizationMetaNames.OUTPUT_DATA: [
                {"id": "solution.json"},
                {"id": "log.txt"},
                {"id": ".*\\.txt"},
                {"id": ".*"}
            ]
        }

        job_details = client.deployments.create_job(deployment_uid, solve_payload)
        job_uid = client.deployments.get_job_uid(job_details)
        print(f"   [OK] Job creado con UID: {job_uid}")

        # =====================================================================
        # Monitorear ejecución
        # =====================================================================
        print(f"\n   Monitoreando ejecución...")

        terminal_states = {"completed", "failed", "canceled", "error", "unknown"}
        while True:
            state = job_details["entity"]["decision_optimization"]["status"]["state"]
            print(f"      Estado: {state}...")
            if state in terminal_states:
                break
            time.sleep(5)
            job_details = client.deployments.get_job_details(job_uid)

        # =====================================================================
        # Obtener estado final
        # =====================================================================
        solve_state = job_details["entity"]["decision_optimization"].get("solve_state", {})
        solve_status = solve_state.get("solve_status", "n/a")
        print(f"\n   Estado final: {solve_status}")

        # =====================================================================
        # Descargar resultados
        # =====================================================================
        print(f"\n   Descargando resultados...")

        outputs = job_details["entity"]["decision_optimization"].get("output_data", [])
        saved = []

        for outp in outputs:
            out_id = outp.get("id")
            content_b64 = outp.get("content")
            if content_b64:
                local_name = out_id if out_id else "output.bin"
                local_name = os.path.basename(local_name)
                try:
                    b64_to_file(content_b64, local_name)
                    saved.append(local_name)
                    print(f"      [OK] Guardado: {local_name}")
                except Exception as e:
                    print(f"      [ERROR] Error guardando {local_name}: {e}")

        # Procesar attachments
        attachments = job_details["entity"]["decision_optimization"].get("attachments", [])
        for att in attachments:
            att_id = att.get("id", "attachment")
            if "content" in att:
                local_name = os.path.basename(att_id)
                try:
                    b64_to_file(att["content"], local_name)
                    saved.append(local_name)
                    print(f"      [OK] Guardado: {local_name}")
                except Exception as e:
                    print(f"      [ERROR] Error guardando adjunto {local_name}: {e}")

        # Mostrar logs si existen
        for candidate in ["log.txt", "job.log", "solve.log"]:
            if os.path.exists(candidate):
                print_if_exists(candidate, max_chars=4000)

        # Verificar solution.json
        if os.path.exists("solution.json"):
            try:
                with open("solution.json", "r") as f:
                    sol = json.load(f)
                print(f"\n   [OK] solution.json cargado correctamente")
                print(f"      Claves: {list(sol.keys())}")
            except Exception as e:
                print(f"   [ERROR] Error leyendo solution.json: {e}")

        print(f"\n{'='*60}")
        print(f"[OK] PROCESO COMPLETADO EXITOSAMENTE")
        print('='*60)
        return True

    except Exception as e:
        print(f"\n[ERROR] ERROR EN WATSON ML: {e}")
        import traceback
        traceback.print_exc()
        return False


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Función principal."""
    print(f"\n{'#'*60}")
    print(f"# SISTEMA DE OPTIMIZACIÓN DE CAJAS")
    print(f"# IBM Watson Machine Learning")
    print('#'*60)

    # Obtener planta desde argumentos
    if len(sys.argv) < 2:
        print(f"\n[ERROR] ERROR: Debes especificar una planta")
        print(f"\nUso: python run_model.py <PLANTA>")
        print(f"\nPlantas disponibles:")
        try:
            plantas_df = pd.read_excel(EXCEL_PARAMETROS, sheet_name='Planta')
            for planta in plantas_df['PLANTA']:
                print(f"   - {planta}")
        except:
            print(f"   - MOSTAZAL")
            print(f"   - MALLOA")
            print(f"   - MOLINA")
        return 1

    planta = sys.argv[1].upper()
    print(f"\nPlanta seleccionada: {planta}")

    # 1. Procesar datos
    if not procesar_datos_planta(planta):
        print(f"\n[ERROR] Error en el procesamiento de datos")
        return 1

    # 2. Empaquetar modelo
    if not empaquetar_modelo():
        print(f"\n[ERROR] Error en el empaquetado del modelo")
        return 1

    # 3. Ejecutar en Watson ML
    if not ejecutar_en_watson_ml():
        print(f"\n[ERROR] Error en la ejecución del modelo")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
