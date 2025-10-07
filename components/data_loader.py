import pandas as pd
import streamlit as st
from pathlib import Path
from typing import Dict, Optional, Tuple

class DataLoader:
    """Clase para cargar y validar datos de parámetros del modelo"""

    REQUIRED_SHEETS = {
        "Turnos": ["DIA", "CANTIDAD DE TURNOS"],
        "Disponibilidad Maquinas": ["Maquina", "Dia", "Disponibilidad"],
        "Productividad Máquina_Caja": ["MAQUINA", "TIPO_CAJA", "PRODUCTIVIDAD"],
        "Tiempo de Setup por máquina": ["MAQUINA", "TIPO_CAJA_ACTUAL", "TIPO_CAJA_A_CAMBIAR", "SETUP"],
        "Duracion Turno": ["DIA", "TURNO", "HORAS"]
    }

    @staticmethod
    def load_from_excel(file_path: str) -> Dict[str, pd.DataFrame]:
        """Carga datos desde un archivo Excel con múltiples hojas"""
        try:
            excel_file = pd.ExcelFile(file_path)
            dataframes = {}

            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name, dtype=str)
                dataframes[sheet_name] = df

            return dataframes
        except Exception as e:
            st.error(f"Error al cargar Excel: {str(e)}")
            return {}

    @staticmethod
    def load_from_csv_folder(folder_path: str) -> Dict[str, pd.DataFrame]:
        """Carga datos desde archivos CSV en una carpeta"""
        try:
            csv_files = {
                "Turnos": "Turnos.csv",
                "Disponibilidad Maquinas": "Disponibilidad_Maquinas.csv",
                "Productividad Máquina_Caja": "Productividad_Maquina_Caja.csv",
                "Tiempo de Setup por máquina": "Tiempo_de_Setup_por_maquina.csv",
                "Duracion Turno": "Duracion_Turno.csv"
            }

            dataframes = {}
            folder = Path(folder_path)

            for name, filename in csv_files.items():
                file_path = folder / filename
                if file_path.exists():
                    df = pd.read_csv(file_path, dtype=str, encoding="utf-8-sig")
                    dataframes[name] = df

            return dataframes
        except Exception as e:
            st.error(f"Error al cargar CSVs: {str(e)}")
            return {}

    @staticmethod
    def validate_dataframe(df: pd.DataFrame, required_columns: list, name: str) -> Tuple[bool, str]:
        """Valida que un DataFrame tenga las columnas requeridas"""
        if df is None or df.empty:
            return False, f"El DataFrame '{name}' está vacío"

        # Normalizar nombres de columnas para comparación (mayúsculas y sin espacios extras)
        df_columns_normalized = [col.upper().strip() for col in df.columns]
        required_normalized = [col.upper().strip() for col in required_columns]

        missing_columns = []
        for req_col in required_normalized:
            found = False
            for df_col in df_columns_normalized:
                if req_col in df_col or df_col in req_col:
                    found = True
                    break
            if not found:
                missing_columns.append(req_col)

        if missing_columns:
            return False, f"Faltan columnas en '{name}': {', '.join(missing_columns)}"

        return True, "OK"

    @staticmethod
    def validate_all_data(dataframes: Dict[str, pd.DataFrame]) -> Tuple[bool, list]:
        """Valida todos los DataFrames cargados"""
        errors = []

        for sheet_name, required_cols in DataLoader.REQUIRED_SHEETS.items():
            if sheet_name not in dataframes:
                errors.append(f"Falta la hoja/archivo: {sheet_name}")
                continue

            is_valid, message = DataLoader.validate_dataframe(
                dataframes[sheet_name],
                required_cols,
                sheet_name
            )

            if not is_valid:
                errors.append(message)

        return len(errors) == 0, errors

    @staticmethod
    def get_data_summary(dataframes: Dict[str, pd.DataFrame]) -> Dict[str, any]:
        """Genera un resumen de los datos cargados"""
        summary = {
            "total_sheets": len(dataframes),
            "sheets": {}
        }

        for name, df in dataframes.items():
            summary["sheets"][name] = {
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": list(df.columns)
            }

        return summary

    @staticmethod
    def upload_files_widget(key: str = "upload"):
        """Widget para cargar archivos Excel o CSV"""
        upload_type = st.radio(
            "Tipo de carga",
            ["Excel (un archivo)", "CSV (múltiples archivos)"],
            key=f"{key}_type",
            horizontal=True
        )

        if upload_type == "Excel (un archivo)":
            uploaded_file = st.file_uploader(
                "Sube el archivo Excel con todas las hojas",
                type=['xlsx', 'xls'],
                key=f"{key}_excel"
            )

            if uploaded_file:
                with st.spinner("Cargando datos desde Excel..."):
                    # Guardar temporalmente
                    temp_path = Path("temp_upload.xlsx")
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    dataframes = DataLoader.load_from_excel(str(temp_path))
                    temp_path.unlink()  # Eliminar archivo temporal

                    return dataframes
        else:
            st.info("Sube los 5 archivos CSV necesarios")

            uploaded_files = st.file_uploader(
                "Archivos CSV",
                type=['csv'],
                accept_multiple_files=True,
                key=f"{key}_csv"
            )

            if uploaded_files and len(uploaded_files) >= 5:
                with st.spinner("Cargando datos desde CSVs..."):
                    dataframes = {}

                    # Mapeo de nombres de archivo a nombres de hoja
                    file_mapping = {
                        "Turnos.csv": "Turnos",
                        "Disponibilidad_Maquinas.csv": "Disponibilidad Maquinas",
                        "Productividad_Maquina_Caja.csv": "Productividad Máquina_Caja",
                        "Tiempo_de_Setup_por_maquina.csv": "Tiempo de Setup por máquina",
                        "Duracion_Turno.csv": "Duracion Turno"
                    }

                    for uploaded_file in uploaded_files:
                        file_name = uploaded_file.name
                        sheet_name = file_mapping.get(file_name)

                        if sheet_name:
                            df = pd.read_csv(uploaded_file, dtype=str, encoding="utf-8-sig")
                            dataframes[sheet_name] = df

                    return dataframes
            elif uploaded_files:
                st.warning(f"Necesitas subir 5 archivos CSV. Has subido {len(uploaded_files)}.")

        return None
