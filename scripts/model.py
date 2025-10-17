import sys, subprocess, importlib



from docplex.mp.model import Model
from itertools import product
import random
import pandas as pd
import numpy as np
class Processing:
    def __init__(self, df_turnos, df_disponibilidad_maquinas, df_setup,
                 df_duracion_turno_dia, df_productividad_maquina_caja, df_demanda, planta):
        self.df_turnos = df_turnos[df_turnos['PLANTA'] == planta]
        self.df_disponibilidad_maquinas = df_disponibilidad_maquinas[df_disponibilidad_maquinas['PLANTA'] == planta]
        self.df_setup = df_setup[df_setup['PLANTA'] == planta]
        self.df_duracion_turno_dia = df_duracion_turno_dia[df_duracion_turno_dia['PLANTA'] == planta]
        self.df_productividad_maquina_caja = df_productividad_maquina_caja[df_productividad_maquina_caja['PLANTA'] == planta]
        self.df_demanda = df_demanda[df_demanda['DES_PLANTA'] == planta]
        self.inverse_mapping = {
            'C8535133': ['BLISS 500*300'],
            'C0546070': ['BRASIL FO/TP'],
            'C0535096': ['FONDO 5 KILOS', 'TAPA 5 KILOS'],
            'C0635120': ['MALETA 2 KILOS ,YELLOW , RAINIER'],
            'C0535102': ['MALETA 2,5 KILOS'],
            'C4434125': ['MASTER 2 X 2,5 KILOS']
        }

        self.df_demanda['cod_envase'] = self.df_demanda['cod_envase'].map(lambda x: self.inverse_mapping[x] if x in self.inverse_mapping.keys() else 'KILL')
        self.df_demanda = self.df_demanda[self.df_demanda['cod_envase']!='KILL']
        self.M = sorted(self.df_disponibilidad_maquinas["MAQUINA"].astype(str).unique().tolist())
        self.D = list(self.df_demanda['fecha_planificación'].unique())
        self.B = list(self.df_demanda['cod_envase'].unique())
        self.P = list(self.df_demanda['DES_PLANTA'].unique())

        self.Dem = {}

    def getMachines(self):
        return self.M
    def getDays(self):
        return self.D
    def getBoxtypes(self):
        return self.B
    def process_turnos(self):
        # diccionario: día -> lista de turnos [1..k]
        turnos_por_dia = {
            int(row.DIA): list(range(1, int(row["CANTIDAD DE TURNOS"]) + 1))
            for _, row in self.df_turnos.iterrows()
        }
        return turnos_por_dia

    def process_demanda(self):
        agrupacion = (
            self.df_demanda
            .groupby(['cod_envase', 'DES_PLANTA', 'fecha_planificación'], as_index=False)
            .agg(SUM_CAJAS=('cant_cajas', 'sum'))
        )

        self.Dem = {}
        for d in self.D:
              for b in self.B:
                  serie = agrupacion.loc[
                        (agrupacion['fecha_planificación'] == d) &
                        (agrupacion['cod_envase'] == b),
                        'SUM_CAJAS'
                  ]
                  valor = float(serie.iloc[0]) if not serie.empty else 0.0
                  self.Dem[(d, b)] = valor
                  print(valor)  # si quieres verlo
        return self.Dem


    def process_disponibilidad_maquinas(self):
        M = self.M
        D = self.D
        """Construye Disp sobre todo el dominio M×D, rellenando faltantes con 0."""
        df = self.df_disponibilidad_maquinas.copy()
        df["MAQUINA"] = df["MAQUINA"].astype(str)
        df["DISPONIBILIDAD"] = pd.to_numeric(df["DISPONIBILIDAD"], errors="coerce").fillna(0).astype(int)

        # base todo a 0
        Disp = {(m, d): 0 for m in M for d in D}

        # sobreescribe con lo que venga en el DF (sólo si el día pertenece a D)
        for _, r in df.dropna(subset=["DIA"]).iterrows():
            m = str(r["MAQUINA"])
            d = int(r["DIA"])
            if m in M and d in D:
                Disp[(m, d)] = int(r["DISPONIBILIDAD"])
        return Disp

    def process_tiempo_setup(self):
        # columnas ["MAQUINA","TIPO_CAJA_ACTUAL","TIPO_CAJA_A_CAMBIAR","SETUP"]
        Setup = {
            (str(r["MAQUINA"]).strip(),
             str(r["TIPO_CAJA_ACTUAL"]).strip(),
             str(r["TIPO_CAJA_A_CAMBIAR"]).strip()): float(r["HORA_SETUP"])
            for _, r in self.df_setup.iterrows()
        }
        # añadir 0 para b1==b2 observados
        M_from_df = sorted(self.df_setup["MAQUINA"].astype(str).str.strip().unique().tolist())
        B_from_df = sorted(pd.unique(
            pd.concat([self.df_setup["TIPO_CAJA_ACTUAL"], self.df_setup["TIPO_CAJA_A_CAMBIAR"]])
              .astype(str).str.strip()
        ).tolist())
        for m in M_from_df:
            for b in B_from_df:
                Setup.setdefault((m, b, b), 0.0)
        return Setup

    def process_turn_duration(self):
        df = self.df_duracion_turno_dia.copy()

        def pick(colname_part):
            return next(c for c in df.columns if colname_part in c.upper())

        c_dia   = pick("DIA")
        c_turno = pick("TURNO")
        c_horas = pick("HORAS")

        df[c_dia]   = pd.to_numeric(df[c_dia], errors="coerce")
        df[c_turno] = pd.to_numeric(df[c_turno], errors="coerce")
        df[c_horas] = pd.to_numeric(df[c_horas], errors="coerce")
        df = df.dropna(subset=[c_dia, c_turno, c_horas]).astype({c_dia:int, c_turno:int})
        df = df[df[c_horas] > 0]
        df = df.drop_duplicates(subset=[c_dia, c_turno], keep="last")

        Tturn_dt = {(int(r[c_dia]), int(r[c_turno])): float(r[c_horas]) for _, r in df.iterrows()}
        return Tturn_dt

    # -------- NUEVO MÉTODO --------
    def process_productividad_y_tipo(self, dup_policy="last", zero_is_incompatible=True, min_prod=0.0):
        """
        Devuelve:
          - Prod: dict {(m,b): float} (cajas/h)
          - Tipo: dict {(m,b): 0/1}   (1 si p>0, si zero_is_incompatible=True)
          - M: lista de máquinas observadas
          - B: lista de tipos observados
        """
        df = self.df_productividad_maquina_caja.copy()

        # localizar columnas (tolerante a mayúsculas/espacios)
        def pick(substr):
            return next(c for c in df.columns if substr in c.upper())

        c_m = pick("MAQUINA")
        c_b = pick("TIPO_CAJA")
        c_p = pick("PRODUCTIVIDAD")

        # limpieza
        df[c_m] = df[c_m].astype(str).str.strip()
        df[c_b] = df[c_b].astype(str).str.strip()
        df[c_p] = pd.to_numeric(df[c_p], errors="coerce").fillna(0.0)

        # resolver duplicados (m,b)
        if dup_policy in ("first","last"):
            df = df.drop_duplicates(subset=[c_m, c_b], keep=dup_policy)
        elif dup_policy in ("min","max","mean"):
            agg = {"min":"min","max":"max","mean":"mean"}[dup_policy]
            df = df.groupby([c_m, c_b], as_index=False)[c_p].agg(agg)
        else:
            raise ValueError("dup_policy inválida. Usa: 'last','first','min','max','mean'.")

        M = sorted(df[c_m].unique().tolist())
        B = sorted(df[c_b].unique().tolist())

        Prod = {(m, b): float(p) for m, b, p in df[[c_m, c_b, c_p]].itertuples(index=False, name=None)}
        Tipo = {}
        for (m, b), p in list(Prod.items()):
            p = max(float(p), 0.0)
            if 0 < p < min_prod:
                p = float(min_prod)
            Prod[(m, b)] = p
            Tipo[(m, b)] = 0 if (zero_is_incompatible and p <= 0.0) else (1 if p > 0.0 else 0)

        # rellena pares faltantes con 0
        for m in M:
            for b in B:
                Prod.setdefault((m, b), 0.0)
                Tipo.setdefault((m, b), 0 if zero_is_incompatible else 1)

        return Prod, Tipo, M, B
    def generate_fake_demanda(self,
                              mode: str = "uniform",
                              low: float = 100.0,
                              high: float = 1000.0,
                              per_day_totals=None,
                              weights_per_envase=None,
                              sparsity: float = 0.0,
                              integer: bool = True,
                              seed: int | None = None,
                              return_df: bool = False):
        """
        Genera demanda ficticia sobre el dominio D×B y la guarda en self.Dem.

        Parámetros
        ----------
        mode : {"uniform","normal","poisson","dirichlet"}
            - "uniform": valores ~ U(low, high)
            - "normal":  valores ~ N(mu, sigma) con mu=(low+high)/2, sigma=(high-low)/6 (clip >=0)
            - "poisson": valores ~ Poisson(lam) con lam=(low+high)/2
            - "dirichlet": reparte un total por día (per_day_totals) según pesos por envase
        low, high : rangos base para los modos aleatorios (ignorado en "dirichlet", salvo defaults)
        per_day_totals : 
            - None: ignora (todos los modos salvo "dirichlet")
            - escalar: mismo total para cada día (solo "dirichlet")
            - dict {d: total} o Serie indexada por d (solo "dirichlet")
        weights_per_envase :
            - None: pesos iguales para todos los envases (solo "dirichlet")
            - dict {b: peso} o Serie indexada por b
        sparsity : [0..1] fracción esperada de ceros (envase/día sin demanda)
        integer : True para redondear a enteros (cajas)
        seed : semilla RNG reproducible
        return_df : True para devolver también un DataFrame (fila=día, col=envase)

        Retorna
        -------
        Dem : dict {(d,b): demanda_float}
        (opcional) df : DataFrame con índice días y columnas envases
        """
        rng = np.random.default_rng(seed)

        # Aseguramos listas ordenadas (opcional, pero ayuda a reproducibilidad)
        D = list(self.D)
        B = list(self.B)

        if len(D) == 0 or len(B) == 0:
            # Nada que generar
            self.Dem = {}
            return (self.Dem, pd.DataFrame(index=D, columns=B)) if return_df else self.Dem

        nD, nB = len(D), len(B)

        # --- Construye matriz base según el modo ---
        if mode not in {"uniform", "normal", "poisson", "dirichlet"}:
            raise ValueError("mode debe ser 'uniform', 'normal', 'poisson' o 'dirichlet'.")

        if mode == "uniform":
            mat = rng.uniform(low, high, size=(nD, nB))

        elif mode == "normal":
            mu = (low + high) / 2.0
            sigma = max((high - low) / 6.0, 1e-6)
            mat = rng.normal(mu, sigma, size=(nD, nB))
            mat = np.clip(mat, 0, None)

        elif mode == "poisson":
            lam = max((low + high) / 2.0, 1e-6)
            mat = rng.poisson(lam=lam, size=(nD, nB)).astype(float)

        else:  # "dirichlet"
            # Totales por día
            if per_day_totals is None:
                # default: usa (low+high) como total diario base
                base_total = max((low + high) / 2.0, 1.0)
                per_day_totals = {d: base_total for d in D}
            elif np.isscalar(per_day_totals):
                per_day_totals = {d: float(per_day_totals) for d in D}
            elif isinstance(per_day_totals, (pd.Series, dict)):
                per_day_totals = {d: float(per_day_totals[d]) if d in per_day_totals else 0.0 for d in D}
            else:
                raise ValueError("per_day_totals debe ser escalar, dict, Serie o None.")

            # Pesos por envase
            if weights_per_envase is None:
                alphas = np.ones(nB, dtype=float)
            elif isinstance(weights_per_envase, (pd.Series, dict)):
                alphas = np.array([float(weights_per_envase.get(b, 1.0)) for b in B], dtype=float)
                alphas[alphas <= 0] = 1e-6  # evitar ceros en Dirichlet
            else:
                raise ValueError("weights_per_envase debe ser dict/Serie o None.")

            mat = np.zeros((nD, nB), dtype=float)
            for i, d in enumerate(D):
                if per_day_totals[d] <= 0:
                    continue
                # proporciones por envase ese día
                p = rng.dirichlet(alphas)
                mat[i, :] = p * float(per_day_totals[d])

        # --- Aplica esparsidad (celdas sin demanda) ---
        if sparsity > 0:
            mask_zero = rng.random(size=(nD, nB)) < float(sparsity)
            mat[mask_zero] = 0.0

        # --- Redondeo a enteros si corresponde ---
        if integer:
            # Usamos round "bancario" de numpy; si prefieres floor, usa np.floor
            mat = np.rint(mat).astype(float)

        # --- Construye el diccionario Dem ---
        Dem = {}
        for i, d in enumerate(D):
            for j, b in enumerate(B):
                Dem[(d, b)] = float(mat[i, j])

        self.Dem = Dem

        if return_df:
            df = pd.DataFrame(mat, index=D, columns=B)
            return Dem, df
        return Dem


import pandas as pd

# Las siguientes líneas se comentan para que no se carguen automáticamente
# Solo se usarán cuando se ejecute el modelo desde línea de comandos
#



import sys, subprocess, importlib
from docplex.mp.model import Model
from itertools import product
import random
import pandas as pd

from docplex.mp.model import Model

def build_model(
    M, B, D, T_turnos, S_segmentos,
    Disp, Prod, Tipo, Setup, Dem, Tturn,
    enforce_tipo=True,
    Tseg=None,                 # puede ser None, escalar, dict por s, dict por (d,t), dict por (d,t,s)
    restrict_w_by_tipo=True
):
    def align_Tturn(T_turnos, Tturn, default_hours=8.0):
        Tturn2 = dict(Tturn)  # copia
        for d, turns in T_turnos.items():
            for t in turns:
                Tturn2.setdefault((d, t), float(default_hours))
        return Tturn2

    # --- 0) Alinea Tturn y valida Disp ---
    Tturn = align_Tturn(T_turnos, Tturn, default_hours=8.0)
    missing_disp = [(m, d) for m in M for d in D if (m, d) not in Disp]
    if missing_disp:
        raise KeyError(f"Faltan claves en Disp, ej: {missing_disp[:5]} (total={len(missing_disp)})")

    # --- 1) Dominios correctos (t por día) ---
    xs_keys = []
    ys_keys = []
    for m in M:
        for b in B:
            for d in D:
                for t in T_turnos[d]:
                    for s in S_segmentos:
                        xs_keys.append((m, b, d, t, s))
                        ys_keys.append((m, b, d, t, s))

    Tsetup_keys = []
    for m in M:
        for d in D:
            for t in T_turnos[d]:
                Tsetup_keys.append((m, d, t))

    # --- 2) Duración por segmento: seg_len[(d,t,s)] ---
    # Admite:
    #   - Tseg=None              -> Tturn[(d,t)] / |S|
    #   - Tseg escalar           -> mismo valor por segmento
    #   - Tseg por s             -> dict {s: horas}
    #   - Tseg por (d,t)         -> dict {(d,t): horas_turno} que se reparte/usa
    #   - Tseg por (d,t,s)       -> dict {(d,t,s): horas_segmento}
    seg_len = {}
    if Tseg is None:
        for d in D:
            for t in T_turnos[d]:
                per_seg = Tturn[(d, t)] / len(S_segmentos)
                for s in S_segmentos:
                    seg_len[(d, t, s)] = float(per_seg)
    elif isinstance(Tseg, (int, float)):
        for d in D:
            for t in T_turnos[d]:
                for s in S_segmentos:
                    seg_len[(d, t, s)] = float(Tseg)
    elif isinstance(Tseg, dict):
        # detectar formato
        sample_key = next(iter(Tseg)) if Tseg else None
        if sample_key in S_segmentos:
            # {s: horas}
            for d in D:
                for t in T_turnos[d]:
                    for s in S_segmentos:
                        seg_len[(d, t, s)] = float(Tseg[s])
        elif isinstance(sample_key, tuple) and len(sample_key) == 2:
            # {(d,t): horas_turno} -> repartir equitativo
            for (d, t), horas in Tseg.items():
                per_seg = float(horas) / len(S_segmentos)
                for s in S_segmentos:
                    seg_len[(d, t, s)] = per_seg
            # si faltan (d,t), completa usando Tturn/|S|
            for d in D:
                for t in T_turnos[d]:
                    if (d, t, S_segmentos[0]) not in seg_len:
                        per_seg = Tturn[(d, t)] / len(S_segmentos)
                        for s in S_segmentos:
                            seg_len[(d, t, s)] = float(per_seg)
        elif isinstance(sample_key, tuple) and len(sample_key) == 3:
            # {(d,t,s): horas_segmento}
            for (d, t, s), horas in Tseg.items():
                seg_len[(d, t, s)] = float(horas)
            # opcional: completa faltantes con Tturn/|S|
            for d in D:
                for t in T_turnos[d]:
                    for s in S_segmentos:
                        seg_len.setdefault((d, t, s), float(Tturn[(d, t)] / len(S_segmentos)))
        else:
            raise TypeError("Formato de Tseg no reconocido. Usa None, escalar, {s:...}, {(d,t):...} o {(d,t,s):...}.")
    else:
        raise TypeError("Tseg debe ser None, escalar o dict.")

    # --- 3) Modelo y variables ---
    mdl = Model(name="Optimizacion_Cajas")

    x = mdl.binary_var_dict(xs_keys, name="x")
    y = mdl.continuous_var_dict(ys_keys, lb=0, name="y")
    Tsetup_var = mdl.continuous_var_dict(Tsetup_keys, lb=0, name="T")

    # --- 4) R1: Demanda (Dem indexado (d,b)) ---
    # Si tu Dem es (b,d), cambia a Dem.get((b,d),0.0)
    for d in D:
        for b in B:
            demand_db = Dem.get((d, b), 0.0)
            mdl.add_constraint(
                mdl.sum(y[(m, b, d, t, s)] * Prod[(m, b)]
                        for m in M for t in T_turnos[d] for s in S_segmentos) >= demand_db,
                ctname=f"R1_dem[{b},{d}]"
            )

    # --- 5) R2: Tiempo por turno ---
    for m in M:
        for d in D:
            for t in T_turnos[d]:
                mdl.add_constraint(
                    mdl.sum(y[(m, b, d, t, s)] for b in B for s in S_segmentos)
                    + Tsetup_var[(m, d, t)]
                    <= Tturn[(d, t)] * Disp[(m, d)],
                    ctname=f"R2_time[{m},{d},{t}]"
                )

    # --- 6) R3 (link): y <= seg_len[(d,t,s)] * x ---
    for (m, b, d, t, s) in ys_keys:
        mdl.add_constraint(
            y[(m, b, d, t, s)] <= seg_len[(d, t, s)] * x[(m, b, d, t, s)],
            ctname=f"R3_link[{m},{b},{d},{t},{s}]"
        )

    # --- 7) R4: Máx 1 tipo por segmento ---
    for m in M:
        for d in D:
            for t in T_turnos[d]:
                for s in S_segmentos:
                    mdl.add_constraint(
                        mdl.sum(x[(m, b, d, t, s)] for b in B) <= 1,
                        ctname=f"R4_oneType[{m},{d},{t},{s}]"
                    )

    # --- 8) R5: El segmento s2 sólo si hay algo en s1 ---
    assert len(S_segmentos) == 2, "Se asumen exactamente 2 segmentos por turno."
    s1, s2 = S_segmentos[0], S_segmentos[1]
    for m in M:
        for d in D:
            for t in T_turnos[d]:
                mdl.add_constraint(
                    mdl.sum(x[(m, b, d, t, s2)] for b in B)
                    <= mdl.sum(x[(m, b, d, t, s1)] for b in B),
                    ctname=f"R5_order[{m},{d},{t}]"
                )

    # --- 9) R6: Setup exacto con w ---
    w_keys = []
    for m in M:
        for d in D:
            for t in T_turnos[d]:
                for b1 in B:
                    for b2 in B:
                        if (m, b1, b2) not in Setup:
                            continue
                        if b1 == b2 and Setup[(m, b1, b2)] <= 1e-9:
                            continue
                        if restrict_w_by_tipo and (Tipo[(m, b1)] == 0 or Tipo[(m, b2)] == 0):
                            continue
                        w_keys.append((m, b1, b2, d, t))

    w = mdl.continuous_var_dict(w_keys, lb=0, ub=1, name="w")

    for (m, b1, b2, d, t) in w_keys:
        mdl.add_constraint(w[(m, b1, b2, d, t)] <= x[(m, b1, d, t, s1)], ctname=f"R6_w_le_s1[{m},{b1},{b2},{d},{t}]")
        mdl.add_constraint(w[(m, b1, b2, d, t)] <= x[(m, b2, d, t, s2)], ctname=f"R6_w_le_s2[{m},{b1},{b2},{d},{t}]")
        mdl.add_constraint(w[(m, b1, b2, d, t)] >= x[(m, b1, d, t, s1)] + x[(m, b2, d, t, s2)] - 1,
                           ctname=f"R6_w_ge_summinus1[{m},{b1},{b2},{d},{t}]")

    for m in M:
        for d in D:
            for t in T_turnos[d]:
                relevant_pairs = [(bb1, bb2) for (mm, bb1, bb2, dd, tt) in w_keys if (mm, dd, tt) == (m, d, t)]
                if relevant_pairs:
                    mdl.add_constraint(
                        Tsetup_var[(m, d, t)] >= mdl.sum(Setup[(m, bb1, bb2)] * w[(m, bb1, bb2, d, t)]
                                                         for (bb1, bb2) in relevant_pairs),
                        ctname=f"R6_T_def[{m},{d},{t}]"
                    )

    # --- 10) Compatibilidad opcional ---
    if enforce_tipo:
        for (m, b, d, t, s) in xs_keys:
            if Tipo[(m, b)] == 0:
                mdl.add_constraint(x[(m, b, d, t, s)] == 0, ctname=f"Compat[{m},{b},{d},{t},{s}]")

    # --- 11) Objetivo ---
    mdl.minimize(mdl.sum(Tsetup_var[(m, d, t)] for (m, d, t) in Tsetup_keys))

    return mdl, x, y, Tsetup_var


df_turnos = pd.read_csv("Turnos.csv", dtype=str, encoding="utf-8-sig")
df_disponibilidad_maquinas = pd.read_csv("Disponibilidad_Maquinas.csv", dtype=str, encoding="utf-8-sig")
df_productividad_maquina_caja = pd.read_csv("Productividad_Maquina_Caja.csv", dtype=str, encoding="utf-8-sig")
df_tiempo_setup_por_maquina = pd.read_csv("Tiempo_de_Setup_por_maquina.csv", dtype=str, encoding="utf-8-sig")
df_duracion_turno_dia = pd.read_csv("Duracion_Turno.csv", dtype=str, encoding="utf-8-sig")
df_estimacion = pd.read_csv("demanda.csv", dtype=str, encoding="utf-8-sig")
df_planta = pd.read_csv("planta.csv", dtype=str, encoding="utf-8-sig")

if __name__ == "__main__":
    # 3) Obtener insumos
    # 2) Instanciar Processing
    planta = df_planta['PLANTA'].iloc[0]
    proc = Processing(
    df_turnos=df_turnos,
    df_disponibilidad_maquinas=df_disponibilidad_maquinas,
    df_setup=df_tiempo_setup_por_maquina,
    df_duracion_turno_dia=df_duracion_turno_dia,
    df_productividad_maquina_caja=df_productividad_maquina_caja,
    df_demanda=df_estimacion,
    planta=planta
    )

    # 3) Obtener insumos
    T_turnos = proc.process_turnos()                 # {d: [1..k_d]}
    Disp = proc.process_disponibilidad_maquinas()          # {(m,d): 0/1}
    Setup = proc.process_tiempo_setup()                    # {(m,b1,b2): horas}
    Tturn_dt = proc.process_turn_duration()                # {(d,t): horas}
    Prod, Tipo, M, B = proc.process_productividad_y_tipo() # dicts y dominios
    Tturn = proc.process_turn_duration()
    # 4) Armar conjuntos para el modelo
    D = sorted(T_turnos.keys())
    DT = [(d, t) for d in D for t in T_turnos[d]]    # pares (día, turno) activos
    S_segmentos = [1, 2]

    # 5) Demanda (ejemplo: si aún no la traes de un DF, pon 0 o carga tu DF)
    Dem = proc.process_demanda()


    # Chequeo de slots (informativo)
    slots_por_dia = len(M)*len(T_turnos)*len(S_segmentos)
    print(f"[Info] Slots por día: {slots_por_dia} (6 máquinas × 2 turnos × 2 segmentos).")

    mdl, x, y, Tsetup = build_model(
    M,B,D,T_turnos,S_segmentos,
    Disp,Prod,Tipo,Setup,Dem,Tturn,
    enforce_tipo=True,
    Tseg=None,                # 8/2 = 4h por segmento
    restrict_w_by_tipo=True
    )

    # Parámetros del solver (puedes ajustarlos)
    mdl.parameters.timelimit = 60
    mdl.parameters.mip.tolerances.mipgap = 0.01

    sol = mdl.solve(log_output=True)
    if sol is None:
        print("No factible: si pasa, baja active_max, baja H_max, o sube compatibilidad.")
    else:
        print("\n========== RESUMEN ==========")
        print("OBJ (∑T):", round(mdl.objective_value, 4))
        total_prod_h = sum(v.solution_value for v in y.values())
        total_T_h    = sum(v.solution_value for v in Tsetup.values())
        print(f"Horas de producción totales: {total_prod_h:.2f} h")
        print(f"Horas de setup totales:      {total_T_h:.2f} h")

        # Verificación de algunas demandas
        sample_B = random.sample(B, min(5, len(B)))
        sample_D = random.sample(D, min(2, len(D)))
        for b in sample_B:
            for d in sample_D:
                producido = sum(y[(m,b,d,t,s)].solution_value * Prod[(m,b)]
                                for m in M for t in T_turnos for s in S_segmentos)
                print(f"Dem[{b},{d}] -> producido={producido:.1f}  demanda={Dem[(b,d)]}")