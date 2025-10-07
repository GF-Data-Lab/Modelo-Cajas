import pandas as pd
import streamlit as st
from typing import Dict, List, Tuple
import re

class DataValidator:
    """Clase para validar la consistencia y calidad de los datos"""

    # Definición de formatos esperados para cada tipo de archivo
    EXPECTED_FORMATS = {
        "Turnos": {
            "columns": ["DIA", "CANTIDAD DE TURNOS"],
            "dtypes": {"DIA": "numeric", "CANTIDAD DE TURNOS": "numeric"},
            "constraints": {
                "DIA": {"min": 1, "type": "int"},
                "CANTIDAD DE TURNOS": {"min": 1, "type": "int"}
            }
        },
        "Disponibilidad Maquinas": {
            "columns": ["Maquina", "Dia", "Disponibilidad"],
            "dtypes": {"Maquina": "string", "Dia": "numeric", "Disponibilidad": "numeric"},
            "constraints": {
                "Dia": {"min": 1, "type": "int"},
                "Disponibilidad": {"min": 0, "max": 1, "type": "int"}
            }
        },
        "Productividad Máquina_Caja": {
            "columns": ["MAQUINA", "TIPO_CAJA", "PRODUCTIVIDAD"],
            "dtypes": {"MAQUINA": "string", "TIPO_CAJA": "string", "PRODUCTIVIDAD": "numeric"},
            "constraints": {
                "PRODUCTIVIDAD": {"min": 0, "type": "float"}
            }
        },
        "Tiempo de Setup por máquina": {
            "columns": ["MAQUINA", "TIPO_CAJA_ACTUAL", "TIPO_CAJA_A_CAMBIAR", "SETUP"],
            "dtypes": {"MAQUINA": "string", "TIPO_CAJA_ACTUAL": "string",
                      "TIPO_CAJA_A_CAMBIAR": "string", "SETUP": "numeric"},
            "constraints": {
                "SETUP": {"min": 0, "type": "float"}
            }
        },
        "Duracion Turno": {
            "columns": ["DIA", "TURNO", "HORAS"],
            "dtypes": {"DIA": "numeric", "TURNO": "numeric", "HORAS": "numeric"},
            "constraints": {
                "DIA": {"min": 1, "type": "int"},
                "TURNO": {"min": 1, "type": "int"},
                "HORAS": {"min": 0.1, "max": 24, "type": "float"}
            }
        }
    }

    @staticmethod
    def validate_file_format(df: pd.DataFrame, file_type: str) -> Tuple[bool, List[str]]:
        """Valida que el archivo tenga el formato correcto"""
        errors = []

        if file_type not in DataValidator.EXPECTED_FORMATS:
            errors.append(f"Tipo de archivo '{file_type}' no reconocido")
            return False, errors

        expected = DataValidator.EXPECTED_FORMATS[file_type]

        # Verificar columnas
        df_cols_normalized = [col.upper().strip() for col in df.columns]
        expected_cols_normalized = [col.upper().strip() for col in expected["columns"]]

        missing_cols = []
        for exp_col in expected_cols_normalized:
            if not any(exp_col in df_col or df_col in exp_col for df_col in df_cols_normalized):
                missing_cols.append(exp_col)

        if missing_cols:
            errors.append(f"Faltan columnas requeridas: {', '.join(missing_cols)}")
            return False, errors

        # Verificar tipos de datos y constraints
        for col_name, col_type in expected["dtypes"].items():
            # Buscar la columna (case insensitive)
            actual_col = None
            for df_col in df.columns:
                if col_name.upper().strip() in df_col.upper().strip():
                    actual_col = df_col
                    break

            if actual_col is None:
                continue

            # Validar tipo de dato
            if col_type == "numeric":
                try:
                    df_numeric = pd.to_numeric(df[actual_col], errors='coerce')
                    if df_numeric.isnull().sum() > 0:
                        null_count = df_numeric.isnull().sum()
                        errors.append(f"La columna '{col_name}' tiene {null_count} valores no numéricos")
                except:
                    errors.append(f"La columna '{col_name}' debe contener valores numéricos")

            # Validar constraints
            if col_name in expected.get("constraints", {}):
                constraint = expected["constraints"][col_name]
                try:
                    values = pd.to_numeric(df[actual_col], errors='coerce')

                    if "min" in constraint:
                        if (values < constraint["min"]).any():
                            errors.append(f"'{col_name}' tiene valores menores a {constraint['min']}")

                    if "max" in constraint:
                        if (values > constraint["max"]).any():
                            errors.append(f"'{col_name}' tiene valores mayores a {constraint['max']}")
                except:
                    pass

        return len(errors) == 0, errors

    @staticmethod
    def validate_turnos(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Valida el DataFrame de Turnos"""
        errors = []

        try:
            # Verificar que haya datos
            if df.empty:
                errors.append("El DataFrame de Turnos está vacío")
                return False, errors

            # Convertir columnas
            df_copy = df.copy()
            dia_col = next((c for c in df.columns if 'DIA' in c.upper()), None)
            cant_col = next((c for c in df.columns if 'CANTIDAD' in c.upper()), None)

            if not dia_col or not cant_col:
                errors.append("No se encontraron las columnas DIA o CANTIDAD DE TURNOS")
                return False, errors

            df_copy[dia_col] = pd.to_numeric(df_copy[dia_col], errors='coerce')
            df_copy[cant_col] = pd.to_numeric(df_copy[cant_col], errors='coerce')

            # Validar valores nulos
            if df_copy[dia_col].isnull().any():
                errors.append("Hay valores nulos en la columna DIA")

            if df_copy[cant_col].isnull().any():
                errors.append("Hay valores nulos en la columna CANTIDAD DE TURNOS")

            # Validar rangos
            if (df_copy[cant_col] <= 0).any():
                errors.append("La cantidad de turnos debe ser mayor a 0")

            if (df_copy[dia_col] <= 0).any():
                errors.append("Los días deben ser mayores a 0")

        except Exception as e:
            errors.append(f"Error al validar Turnos: {str(e)}")

        return len(errors) == 0, errors

    @staticmethod
    def validate_disponibilidad(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Valida el DataFrame de Disponibilidad de Máquinas"""
        errors = []

        try:
            if df.empty:
                errors.append("El DataFrame de Disponibilidad está vacío")
                return False, errors

            # Buscar columnas
            maq_col = next((c for c in df.columns if 'MAQUINA' in c.upper()), None)
            dia_col = next((c for c in df.columns if 'DIA' in c.upper()), None)
            disp_col = next((c for c in df.columns if 'DISPONIBILIDAD' in c.upper()), None)

            if not all([maq_col, dia_col, disp_col]):
                errors.append("Faltan columnas requeridas en Disponibilidad")
                return False, errors

            df_copy = df.copy()
            df_copy[dia_col] = pd.to_numeric(df_copy[dia_col], errors='coerce')
            df_copy[disp_col] = pd.to_numeric(df_copy[disp_col], errors='coerce')

            # Validar nulos
            if df_copy[maq_col].isnull().any():
                errors.append("Hay valores nulos en Máquina")

            if df_copy[dia_col].isnull().any():
                errors.append("Hay valores nulos en Día")

            # Validar que disponibilidad sea 0 o 1
            unique_disp = df_copy[disp_col].dropna().unique()
            if not all(val in [0, 1, 0.0, 1.0] for val in unique_disp):
                errors.append("La disponibilidad debe ser 0 o 1")

        except Exception as e:
            errors.append(f"Error al validar Disponibilidad: {str(e)}")

        return len(errors) == 0, errors

    @staticmethod
    def validate_productividad(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Valida el DataFrame de Productividad"""
        errors = []

        try:
            if df.empty:
                errors.append("El DataFrame de Productividad está vacío")
                return False, errors

            maq_col = next((c for c in df.columns if 'MAQUINA' in c.upper()), None)
            caja_col = next((c for c in df.columns if 'TIPO_CAJA' in c.upper()), None)
            prod_col = next((c for c in df.columns if 'PRODUCTIVIDAD' in c.upper()), None)

            if not all([maq_col, caja_col, prod_col]):
                errors.append("Faltan columnas requeridas en Productividad")
                return False, errors

            df_copy = df.copy()
            df_copy[prod_col] = pd.to_numeric(df_copy[prod_col], errors='coerce')

            # Validar nulos
            if df_copy[maq_col].isnull().any():
                errors.append("Hay valores nulos en Máquina")

            if df_copy[caja_col].isnull().any():
                errors.append("Hay valores nulos en Tipo de Caja")

            # Validar que productividad sea >= 0
            if (df_copy[prod_col] < 0).any():
                errors.append("La productividad no puede ser negativa")

            # Advertencia sobre productividad 0
            if (df_copy[prod_col] == 0).any():
                count_zeros = (df_copy[prod_col] == 0).sum()
                st.warning(f"⚠️ Hay {count_zeros} combinaciones máquina-caja con productividad 0 (incompatibles)")

        except Exception as e:
            errors.append(f"Error al validar Productividad: {str(e)}")

        return len(errors) == 0, errors

    @staticmethod
    def validate_setup(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Valida el DataFrame de Tiempos de Setup"""
        errors = []

        try:
            if df.empty:
                errors.append("El DataFrame de Setup está vacío")
                return False, errors

            maq_col = next((c for c in df.columns if 'MAQUINA' in c.upper()), None)
            actual_col = next((c for c in df.columns if 'ACTUAL' in c.upper()), None)
            cambiar_col = next((c for c in df.columns if 'CAMBIAR' in c.upper()), None)
            setup_col = next((c for c in df.columns if 'SETUP' in c.upper()), None)

            if not all([maq_col, actual_col, cambiar_col, setup_col]):
                errors.append("Faltan columnas requeridas en Setup")
                return False, errors

            df_copy = df.copy()
            df_copy[setup_col] = pd.to_numeric(df_copy[setup_col], errors='coerce')

            # Validar nulos
            if df_copy[maq_col].isnull().any():
                errors.append("Hay valores nulos en Máquina")

            # Validar que setup sea >= 0
            if (df_copy[setup_col] < 0).any():
                errors.append("El tiempo de setup no puede ser negativo")

        except Exception as e:
            errors.append(f"Error al validar Setup: {str(e)}")

        return len(errors) == 0, errors

    @staticmethod
    def validate_duracion_turno(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Valida el DataFrame de Duración de Turno"""
        errors = []

        try:
            if df.empty:
                errors.append("El DataFrame de Duración de Turno está vacío")
                return False, errors

            dia_col = next((c for c in df.columns if 'DIA' in c.upper()), None)
            turno_col = next((c for c in df.columns if 'TURNO' in c.upper()), None)
            horas_col = next((c for c in df.columns if 'HORAS' in c.upper()), None)

            if not all([dia_col, turno_col, horas_col]):
                errors.append("Faltan columnas requeridas en Duración de Turno")
                return False, errors

            df_copy = df.copy()
            df_copy[dia_col] = pd.to_numeric(df_copy[dia_col], errors='coerce')
            df_copy[turno_col] = pd.to_numeric(df_copy[turno_col], errors='coerce')
            df_copy[horas_col] = pd.to_numeric(df_copy[horas_col], errors='coerce')

            # Validar que horas sea > 0
            if (df_copy[horas_col] <= 0).any():
                errors.append("Las horas de turno deben ser mayores a 0")

        except Exception as e:
            errors.append(f"Error al validar Duración de Turno: {str(e)}")

        return len(errors) == 0, errors

    @staticmethod
    def validate_all(dataframes: Dict[str, pd.DataFrame]) -> Tuple[bool, Dict[str, List[str]]]:
        """Valida todos los DataFrames"""
        all_errors = {}

        validators = {
            "Turnos": DataValidator.validate_turnos,
            "Disponibilidad Maquinas": DataValidator.validate_disponibilidad,
            "Productividad Máquina_Caja": DataValidator.validate_productividad,
            "Tiempo de Setup por máquina": DataValidator.validate_setup,
            "Duracion Turno": DataValidator.validate_duracion_turno
        }

        for name, validator_func in validators.items():
            if name in dataframes:
                is_valid, errors = validator_func(dataframes[name])
                if not is_valid:
                    all_errors[name] = errors

        return len(all_errors) == 0, all_errors

    @staticmethod
    def check_consistency(dataframes: Dict[str, pd.DataFrame]) -> List[str]:
        """Verifica la consistencia entre diferentes DataFrames"""
        warnings = []

        try:
            # Obtener máquinas únicas de cada DataFrame
            maquinas_disp = set()
            maquinas_prod = set()
            maquinas_setup = set()

            if "Disponibilidad Maquinas" in dataframes:
                df = dataframes["Disponibilidad Maquinas"]
                maq_col = next((c for c in df.columns if 'MAQUINA' in c.upper()), None)
                if maq_col:
                    maquinas_disp = set(df[maq_col].astype(str).str.strip().unique())

            if "Productividad Máquina_Caja" in dataframes:
                df = dataframes["Productividad Máquina_Caja"]
                maq_col = next((c for c in df.columns if 'MAQUINA' in c.upper()), None)
                if maq_col:
                    maquinas_prod = set(df[maq_col].astype(str).str.strip().unique())

            if "Tiempo de Setup por máquina" in dataframes:
                df = dataframes["Tiempo de Setup por máquina"]
                maq_col = next((c for c in df.columns if 'MAQUINA' in c.upper()), None)
                if maq_col:
                    maquinas_setup = set(df[maq_col].astype(str).str.strip().unique())

            # Comparar conjuntos
            if maquinas_disp and maquinas_prod:
                solo_disp = maquinas_disp - maquinas_prod
                solo_prod = maquinas_prod - maquinas_disp

                if solo_disp:
                    warnings.append(f"Máquinas en Disponibilidad pero no en Productividad: {solo_disp}")
                if solo_prod:
                    warnings.append(f"Máquinas en Productividad pero no en Disponibilidad: {solo_prod}")

        except Exception as e:
            warnings.append(f"Error al verificar consistencia: {str(e)}")

        return warnings
