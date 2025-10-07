import sys
import pandas as pd
import streamlit as st
from pathlib import Path
from typing import Dict, Tuple, Optional
from datetime import datetime

# Importar el módulo del modelo existente
sys.path.append(str(Path(__file__).parent.parent / "scripts"))
from scripts.model import Processing, build_model

class ModelRunner:
    """Clase para ejecutar el modelo de optimización"""

    def __init__(self):
        self.processing = None
        self.model = None
        self.solution = None

    def initialize_from_dataframes(self, dataframes: Dict[str, pd.DataFrame]) -> bool:
        """Inicializa el Processing desde los DataFrames cargados"""
        try:
            # Mapear nombres de hojas a nombres esperados
            df_turnos = dataframes.get("Turnos")
            df_disponibilidad = dataframes.get("Disponibilidad Maquinas")
            df_productividad = dataframes.get("Productividad Máquina_Caja")
            df_setup = dataframes.get("Tiempo de Setup por máquina")
            df_duracion = dataframes.get("Duracion Turno")

            if not all([df_turnos is not None, df_disponibilidad is not None,
                       df_productividad is not None, df_setup is not None,
                       df_duracion is not None]):
                st.error("Faltan algunos DataFrames necesarios")
                return False

            self.processing = Processing(
                df_turnos=df_turnos,
                df_disponibilidad_maquinas=df_disponibilidad,
                df_setup=df_setup,
                df_duracion_turno_dia=df_duracion,
                df_productividad_maquina_caja=df_productividad
            )

            return True

        except Exception as e:
            st.error(f"Error al inicializar Processing: {str(e)}")
            return False

    def extract_parameters(self) -> Optional[Dict]:
        """Extrae los parámetros procesados del Processing"""
        if not self.processing:
            st.error("Processing no inicializado")
            return None

        try:
            T_turnos = self.processing.process_turnos()
            Disp = self.processing.process_disponibilidad_maquinas()
            Setup = self.processing.process_tiempo_setup()
            Tturn_dt = self.processing.process_turn_duration()
            Prod, Tipo, M, B = self.processing.process_productividad_y_tipo()

            D = sorted(T_turnos.keys())
            S_segmentos = [1, 2]

            params = {
                'M': M,
                'B': B,
                'D': D,
                'T_turnos': T_turnos,
                'S_segmentos': S_segmentos,
                'Disp': Disp,
                'Prod': Prod,
                'Tipo': Tipo,
                'Setup': Setup,
                'Tturn_dt': Tturn_dt
            }

            return params

        except Exception as e:
            st.error(f"Error al extraer parámetros: {str(e)}")
            return None

    def build_and_solve(
        self,
        params: Dict,
        Dem: Dict,
        Tturn: float = 8.0,
        enforce_tipo: bool = True,
        Tseg: Optional[float] = None,
        restrict_w_by_tipo: bool = True,
        time_limit: int = 60,
        mip_gap: float = 0.01
    ) -> Tuple[bool, Optional[Dict]]:
        """Construye y resuelve el modelo de optimización"""

        try:
            with st.spinner("🔨 Construyendo modelo..."):
                mdl, x, y, Tsetup = build_model(
                    M=params['M'],
                    B=params['B'],
                    D=params['D'],
                    T_turnos=params['T_turnos'],
                    S_segmentos=params['S_segmentos'],
                    Disp=params['Disp'],
                    Prod=params['Prod'],
                    Tipo=params['Tipo'],
                    Setup=params['Setup'],
                    Dem=Dem,
                    Tturn=Tturn,
                    enforce_tipo=enforce_tipo,
                    Tseg=Tseg,
                    restrict_w_by_tipo=restrict_w_by_tipo
                )

                # Configurar parámetros del solver
                mdl.parameters.timelimit = time_limit
                mdl.parameters.mip.tolerances.mipgap = mip_gap

            with st.spinner("⚙️ Resolviendo modelo..."):
                progress_bar = st.progress(0)
                status_text = st.empty()

                # Simular progreso (CPLEX no proporciona callbacks fáciles en Streamlit)
                import time
                for i in range(100):
                    time.sleep(time_limit / 100)
                    progress_bar.progress(i + 1)
                    status_text.text(f"Optimizando... {i + 1}%")

                sol = mdl.solve(log_output=False)

                progress_bar.empty()
                status_text.empty()

            if sol is None:
                st.error("❌ Modelo infactible. Revisa las restricciones.")
                return False, None

            # Extraer resultados
            results = self._extract_solution(mdl, x, y, Tsetup, params, Dem)
            results['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            self.solution = results

            return True, results

        except Exception as e:
            st.error(f"Error al resolver el modelo: {str(e)}")
            import traceback
            st.error(traceback.format_exc())
            return False, None

    def _extract_solution(self, mdl, x, y, Tsetup, params, Dem) -> Dict:
        """Extrae la solución del modelo en un formato estructurado"""

        from itertools import product

        M = params['M']
        B = params['B']
        D = params['D']
        T_turnos = params['T_turnos']
        S_segmentos = params['S_segmentos']
        Prod = params['Prod']

        # Información general
        obj_value = mdl.objective_value
        total_prod_h = sum(v.solution_value for v in y.values())
        total_setup_h = sum(v.solution_value for v in Tsetup.values())

        # Asignaciones activas (x = 1)
        asignaciones = []
        for m, b, d, t, s in product(M, B, D, T_turnos, S_segmentos):
            if x[(m, b, d, t, s)].solution_value > 0.5:  # Binario
                horas = y[(m, b, d, t, s)].solution_value
                cajas = horas * Prod.get((m, b), 0)

                asignaciones.append({
                    'Maquina': m,
                    'TipoCaja': b,
                    'Dia': d,
                    'Turno': t,
                    'Segmento': s,
                    'Horas': round(horas, 2),
                    'Cajas': round(cajas, 2)
                })

        # Setup por turno
        setups = []
        for m, d, t in product(M, D, T_turnos):
            setup_time = Tsetup[(m, d, t)].solution_value
            if setup_time > 0.01:
                setups.append({
                    'Maquina': m,
                    'Dia': d,
                    'Turno': t,
                    'TiempoSetup': round(setup_time, 2)
                })

        # Verificar demanda
        demanda_cumplida = []
        for b, d in product(B, D):
            producido = sum(
                y[(m, b, d, t, s)].solution_value * Prod.get((m, b), 0)
                for m in M for t in T_turnos for s in S_segmentos
            )
            demandado = Dem.get((b, d), 0)

            demanda_cumplida.append({
                'TipoCaja': b,
                'Dia': d,
                'Demanda': demandado,
                'Producido': round(producido, 2),
                'Diferencia': round(producido - demandado, 2),
                'Cumplimiento': round((producido / demandado * 100) if demandado > 0 else 100, 1)
            })

        # Utilización de máquinas
        utilizacion = []
        for m, d in product(M, D):
            total_horas = sum(
                y[(m, b, d, t, s)].solution_value
                for b in B for t in T_turnos for s in S_segmentos
            )
            setup_horas = sum(
                Tsetup[(m, d, t)].solution_value
                for t in T_turnos
            )

            utilizacion.append({
                'Maquina': m,
                'Dia': d,
                'HorasProduccion': round(total_horas, 2),
                'HorasSetup': round(setup_horas, 2),
                'HorasTotal': round(total_horas + setup_horas, 2)
            })

        results = {
            'objetivo': round(obj_value, 2),
            'total_produccion_h': round(total_prod_h, 2),
            'total_setup_h': round(total_setup_h, 2),
            'asignaciones': asignaciones,
            'setups': setups,
            'demanda': demanda_cumplida,
            'utilizacion': utilizacion,
            'parametros': params
        }

        return results

    def get_solution_summary(self, results: Dict) -> str:
        """Genera un resumen en texto de la solución"""
        if not results:
            return "No hay solución disponible"

        summary = f"""
        ### 📊 Resumen de la Solución

        **Objetivo (Minimizar Setup):** {results['objetivo']} horas

        **Tiempos:**
        - Horas de producción: {results['total_produccion_h']} h
        - Horas de setup: {results['total_setup_h']} h

        **Asignaciones:**
        - Total de asignaciones: {len(results['asignaciones'])}
        - Cambios de setup: {len(results['setups'])}

        **Cumplimiento de Demanda:**
        - Items procesados: {len(results['demanda'])}
        """

        return summary
