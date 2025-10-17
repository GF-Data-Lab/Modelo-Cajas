"""
Módulo para mapear códigos del modelo a nombres reales.
Este módulo lee los archivos CSV generados y crea diccionarios de mapeo.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Optional


class MapeadorNombres:
    """Clase para mapear códigos del modelo a nombres reales."""

    def __init__(self, csv_dir: str = "inputs/csv"):
        """
        Inicializa el mapeador cargando los datos desde los CSVs.

        Args:
            csv_dir: Directorio donde están los archivos CSV
        """
        self.csv_dir = Path(csv_dir)
        self.mapeo_maquinas = {}
        self.mapeo_cajas = {}
        self.mapeo_dias = {
            '1': 'Lunes',
            '2': 'Martes',
            '3': 'Miércoles',
            '4': 'Jueves',
            '5': 'Viernes',
            '6': 'Sábado',
            '7': 'Domingo'
        }
        self.planta = None
        self._cargar_mapeos()

    def _cargar_mapeos(self):
        """Carga los mapeos desde los archivos CSV."""
        try:
            # Cargar mapeo de máquinas desde Productividad
            prod_path = self.csv_dir / "Productividad_Maquina_Caja.csv"
            if prod_path.exists():
                df_prod = pd.read_csv(prod_path)

                # Obtener planta
                if 'PLANTA' in df_prod.columns:
                    self.planta = df_prod['PLANTA'].iloc[0] if len(df_prod) > 0 else None

                # Mapeo de máquinas: m1 -> M1, m2 -> M2, etc.
                if 'MAQUINA' in df_prod.columns:
                    maquinas_unicas = df_prod['MAQUINA'].unique()
                    for maq in maquinas_unicas:
                        # Convertir M1 -> m1 para el mapeo inverso
                        codigo = maq.lower()
                        self.mapeo_maquinas[codigo] = maq

                # Mapeo de tipos de caja: c1 -> TIPO_CAJA_1, c2 -> TIPO_CAJA_2, etc.
                if 'TIPO_CAJA' in df_prod.columns:
                    tipos_caja_unicos = df_prod['TIPO_CAJA'].unique()
                    for idx, tipo_caja in enumerate(sorted(tipos_caja_unicos), start=1):
                        codigo = f"c{idx}"
                        self.mapeo_cajas[codigo] = tipo_caja

                # Crear mapeo alternativo desde máquina a su tipo de caja principal
                self.mapeo_maquina_a_caja = {}
                if 'MAQUINA' in df_prod.columns and 'TIPO_CAJA' in df_prod.columns:
                    for _, row in df_prod.iterrows():
                        maq_codigo = row['MAQUINA'].lower()
                        self.mapeo_maquina_a_caja[maq_codigo] = row['TIPO_CAJA']

        except Exception as e:
            print(f"Error cargando mapeos: {e}")

    def mapear_maquina(self, codigo: str) -> str:
        """
        Mapea código de máquina a nombre real.

        Args:
            codigo: Código de máquina (ej: 'm1', 'm2')

        Returns:
            Nombre de máquina (ej: 'M1 - BLISS 500*300')
        """
        codigo_limpio = codigo.lower().strip()

        # Si el código está en el mapeo directo
        if codigo_limpio in self.mapeo_maquinas:
            nombre_base = self.mapeo_maquinas[codigo_limpio]

            # Intentar agregar el tipo de caja principal
            if codigo_limpio in self.mapeo_maquina_a_caja:
                tipo_caja = self.mapeo_maquina_a_caja[codigo_limpio]
                return f"{nombre_base} - {tipo_caja}"

            return nombre_base

        # Si no está, devolver el código capitalizado
        return codigo.upper()

    def mapear_caja(self, codigo: str) -> str:
        """
        Mapea código de tipo de caja a nombre real.

        Args:
            codigo: Código de caja (ej: 'c1', 'c2')

        Returns:
            Nombre de tipo de caja
        """
        codigo_limpio = codigo.lower().strip()
        return self.mapeo_cajas.get(codigo_limpio, codigo.upper())

    def mapear_dia(self, codigo: str) -> str:
        """
        Mapea código de día a nombre del día.

        Args:
            codigo: Código de día (ej: '1', '2')

        Returns:
            Nombre del día (ej: 'Lunes', 'Martes')
        """
        return self.mapeo_dias.get(str(codigo), f"Día {codigo}")

    def mapear_variable_completa(self, nombre_variable: str) -> str:
        """
        Mapea una variable completa a su descripción legible.

        Args:
            nombre_variable: Nombre de variable (ej: 'x_m1_c2_3_4_1')

        Returns:
            Descripción legible
        """
        partes = nombre_variable.split('_')

        if len(partes) < 3:
            return nombre_variable

        tipo_var = partes[0]  # x o y

        # Parsear componentes
        maquina_cod = partes[1] if len(partes) > 1 else ''
        caja_cod = partes[2] if len(partes) > 2 else ''
        dia_cod = partes[3] if len(partes) > 3 else ''
        turno_cod = partes[4] if len(partes) > 4 else ''

        # Mapear cada componente
        maquina = self.mapear_maquina(maquina_cod)
        caja = self.mapear_caja(caja_cod)
        dia = self.mapear_dia(dia_cod)
        turno = f"Turno {turno_cod}"

        if tipo_var == 'x':
            return f"Asignación: {maquina} → {caja} | {dia}, {turno}"
        elif tipo_var == 'y':
            return f"Producción: {maquina} → {caja} | {dia}, {turno}"
        else:
            return nombre_variable

    def obtener_descripcion_componentes(self, nombre_variable: str) -> Dict[str, str]:
        """
        Extrae y mapea todos los componentes de una variable.

        Args:
            nombre_variable: Nombre de variable (ej: 'x_m1_c2_3_4_1')

        Returns:
            Diccionario con componentes mapeados
        """
        partes = nombre_variable.split('_')

        if len(partes) < 3:
            return {'variable_original': nombre_variable}

        tipo_var = partes[0]
        maquina_cod = partes[1] if len(partes) > 1 else ''
        caja_cod = partes[2] if len(partes) > 2 else ''
        dia_cod = partes[3] if len(partes) > 3 else ''
        turno_cod = partes[4] if len(partes) > 4 else ''

        return {
            'variable_original': nombre_variable,
            'tipo': 'Asignación' if tipo_var == 'x' else 'Producción',
            'maquina_codigo': maquina_cod.upper(),
            'maquina_nombre': self.mapear_maquina(maquina_cod),
            'caja_codigo': caja_cod.upper(),
            'caja_nombre': self.mapear_caja(caja_cod),
            'dia_codigo': dia_cod,
            'dia_nombre': self.mapear_dia(dia_cod),
            'turno': turno_cod,
            'descripcion_completa': self.mapear_variable_completa(nombre_variable)
        }

    def obtener_info_planta(self) -> Optional[str]:
        """Retorna el nombre de la planta actual."""
        return self.planta

    def obtener_mapeo_maquinas(self) -> Dict[str, str]:
        """Retorna el diccionario completo de mapeo de máquinas."""
        return self.mapeo_maquinas.copy()

    def obtener_mapeo_cajas(self) -> Dict[str, str]:
        """Retorna el diccionario completo de mapeo de cajas."""
        return self.mapeo_cajas.copy()


# Crear instancia global para uso fácil
_mapeador_global = None

def obtener_mapeador(csv_dir: str = "inputs/csv") -> MapeadorNombres:
    """
    Obtiene la instancia global del mapeador (singleton).

    Args:
        csv_dir: Directorio de CSVs

    Returns:
        Instancia del mapeador
    """
    global _mapeador_global
    if _mapeador_global is None:
        _mapeador_global = MapeadorNombres(csv_dir)
    return _mapeador_global


def mapear_nombre(codigo: str, tipo: str = 'auto') -> str:
    """
    Función de conveniencia para mapear un código a nombre.

    Args:
        codigo: Código a mapear
        tipo: Tipo de código ('maquina', 'caja', 'dia', 'auto')

    Returns:
        Nombre mapeado
    """
    mapeador = obtener_mapeador()

    if tipo == 'auto':
        # Detectar automáticamente el tipo
        codigo_lower = codigo.lower()
        if codigo_lower.startswith('m'):
            tipo = 'maquina'
        elif codigo_lower.startswith('c'):
            tipo = 'caja'
        elif codigo_lower.isdigit():
            tipo = 'dia'

    if tipo == 'maquina':
        return mapeador.mapear_maquina(codigo)
    elif tipo == 'caja':
        return mapeador.mapear_caja(codigo)
    elif tipo == 'dia':
        return mapeador.mapear_dia(codigo)
    else:
        return codigo
