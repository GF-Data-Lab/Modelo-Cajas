import sys, subprocess, importlib



from docplex.mp.model import Model
from itertools import product
import random
import pandas as pd

class Processing:
    def __init__(self, df_turnos, df_disponibilidad_maquinas, df_setup,
                 df_duracion_turno_dia, df_productividad_maquina_caja):
        self.df_turnos = df_turnos
        self.df_disponibilidad_maquinas = df_disponibilidad_maquinas
        self.df_setup = df_setup
        self.df_duracion_turno_dia = df_duracion_turno_dia
        self.df_productividad_maquina_caja = df_productividad_maquina_caja
        self.M = sorted(self.df_disponibilidad_maquinas["Maquina"].astype(str).unique().tolist())
        self.D = sorted(self.df_disponibilidad_maquinas["Dia"].astype(int).unique().tolist())
        self.B = sorted(self.df_productividad_maquina_caja['TIPO_CAJA'].unique())
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


    def process_disponibilidad_maquinas(self):
        M = self.M
        D = self.D
        """Construye Disp sobre todo el dominio M×D, rellenando faltantes con 0."""
        df = self.df_disponibilidad_maquinas.copy()
        df["Maquina"] = df["Maquina"].astype(str)
        df["Dia"] = pd.to_numeric(df["Dia"], errors="coerce").astype("Int64")
        df["Disponibilidad"] = pd.to_numeric(df["Disponibilidad"], errors="coerce").fillna(0).astype(int)
    
        # base todo a 0
        Disp = {(m, int(d)): 0 for m in M for d in D}
    
        # sobreescribe con lo que venga en el DF (sólo si el día pertenece a D)
        for _, r in df.dropna(subset=["Dia"]).iterrows():
            m = str(r["Maquina"])
            d = int(r["Dia"])
            if m in M and d in D:
                Disp[(m, d)] = int(r["Disponibilidad"])
        return Disp

    def process_tiempo_setup(self):
        # columnas ["MAQUINA","TIPO_CAJA_ACTUAL","TIPO_CAJA_A_CAMBIAR","SETUP"]
        Setup = {
            (str(r["MAQUINA"]).strip(),
             str(r["TIPO_CAJA_ACTUAL"]).strip(),
             str(r["TIPO_CAJA_A_CAMBIAR"]).strip()): float(r["SETUP"])
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


import pandas as pd

# Lee los CSV desde la raíz del working dir del runtime
df_turnos = pd.read_csv("Turnos.csv", dtype=str, encoding="utf-8-sig")
df_disponibilidad_maquinas = pd.read_csv("Disponibilidad_Maquinas.csv", dtype=str, encoding="utf-8-sig")
df_productividad_maquina_caja = pd.read_csv("Productividad_Maquina_Caja.csv", dtype=str, encoding="utf-8-sig")
df_tiempo_setup_por_maquina = pd.read_csv("Tiempo_de_Setup_por_maquina.csv", dtype=str, encoding="utf-8-sig")
df_duracion_turno_dia = pd.read_csv("Duracion_Turno.csv", dtype=str, encoding="utf-8-sig")


def build_model(
    M, B, D, T_turnos, S_segmentos,
    Disp,     # {(m,d): 0/1}
    Prod,     # {(m,b): float>0} cajas/h
    Tipo,     # {(m,b): 0/1}
    Setup,    # {(m,b1,b2): float>=0} horas
    Dem,      # {(b,d): float>=0} cajas
    Tturn,    # float>0 horas/turno
    enforce_tipo=True,
    Tseg=None,              # float o dict {s: float}; si None => Tturn/|S|
    restrict_w_by_tipo=True # crea w sólo si ambos tipos compatibles en m
):
    assert len(S_segmentos) == 2, "Se asumen exactamente 2 segmentos por turno."
    s1, s2 = S_segmentos[0], S_segmentos[1]

    # Duración segmento
    if Tseg is None:
        seg_len = {s: Tturn/len(S_segmentos) for s in S_segmentos}
    elif isinstance(Tseg, dict):
        seg_len = dict(Tseg)
    else:
        seg_len = {s: float(Tseg) for s in S_segmentos}

    mdl = Model(name="Optimizacion_Cajas")

    # ---------------- Variables ----------------
    x = mdl.binary_var_dict(((m,b,d,t,s) for m,b,d,t,s in product(M,B,D,T_turnos,S_segmentos)), name="x")
    y = mdl.continuous_var_dict(((m,b,d,t,s) for m,b,d,t,s in product(M,B,D,T_turnos,S_segmentos)), lb=0, name="y")
    Tsetup = mdl.continuous_var_dict(((m,d,t) for m,d,t in product(M,D,T_turnos)), lb=0, name="T")

    # ---------------- R1: Demanda ----------------
    for b,d in product(B,D):
        mdl.add_constraint(
            mdl.sum(y[(m,b,d,t,s)] * Prod[(m,b)] for m in M for t in T_turnos for s in S_segmentos) >= Dem[(b,d)],
            ctname=f"R1_dem[{b},{d}]"
        )

    # ---------------- R2: Tiempo por turno ----------------
    for m,d,t in product(M,D,T_turnos):
        mdl.add_constraint(
            mdl.sum(y[(m,b,d,t,s)] for b in B for s in S_segmentos) + Tsetup[(m,d,t)]
            <= Tturn * Disp[(m,d)],
            ctname=f"R2_time[{m},{d},{t}]"
        )

    # ---------------- R3 (corregida): y <= Tseg * x ----------------
    for m,b,d,t,s in product(M,B,D,T_turnos,S_segmentos):
        mdl.add_constraint(
            y[(m,b,d,t,s)] <= seg_len[s] * x[(m,b,d,t,s)],
            ctname=f"R3_link[{m},{b},{d},{t},{s}]"
        )

    # ---------------- R4: Máx 1 tipo por segmento ----------------
    for m,d,t,s in product(M,D,T_turnos,S_segmentos):
        mdl.add_constraint(
            mdl.sum(x[(m,b,d,t,s)] for b in B) <= 1,
            ctname=f"R4_oneType[{m},{d},{t},{s}]"
        )

    # ---------------- R5: Se asigna primero el segmento 1 ----------------
    for m,d,t in product(M,D,T_turnos):
        mdl.add_constraint(
            mdl.sum(x[(m,b,d,t,s2)] for b in B) <= mdl.sum(x[(m,b,d,t,s1)] for b in B),
            ctname=f"R5_order[{m},{d},{t}]"
        )

    # ---------------- R6: Setup exacto con variables w ----------------
    # w(m,b1,b2,d,t) ≈ x(m,b1,s1) AND x(m,b2,s2)
    # T(m,d,t) >= sum_{b1,b2} Setup(m,b1,b2) * w(m,b1,b2,d,t)
    w_keys = []
    for m,b1,b2,d,t in product(M,B,B,D,T_turnos):
        if (m,b1,b2) not in Setup:
            continue
        if b1 == b2 and Setup[(m,b1,b2)] <= 1e-9:
            continue  # mismo tipo y setup=0: no aporta
        if restrict_w_by_tipo and (Tipo[(m,b1)] == 0 or Tipo[(m,b2)] == 0):
            continue
        w_keys.append((m,b1,b2,d,t))

    w = mdl.continuous_var_dict(w_keys, lb=0, ub=1, name="w")

    for (m,b1,b2,d,t) in w_keys:
        mdl.add_constraint(w[(m,b1,b2,d,t)] <= x[(m,b1,d,t,s1)], ctname=f"R6_w_le_s1[{m},{b1},{b2},{d},{t}]")
        mdl.add_constraint(w[(m,b1,b2,d,t)] <= x[(m,b2,d,t,s2)], ctname=f"R6_w_le_s2[{m},{b1},{b2},{d},{t}]")
        mdl.add_constraint(w[(m,b1,b2,d,t)] >= x[(m,b1,d,t,s1)] + x[(m,b2,d,t,s2)] - 1,
                           ctname=f"R6_w_ge_summinus1[{m},{b1},{b2},{d},{t}]")

    for m,d,t in product(M,D,T_turnos):
        relevant_pairs = [(bb1,bb2) for (mm,bb1,bb2,dd,tt) in w_keys if (mm,dd,tt) == (m,d,t)]
        if relevant_pairs:
            mdl.add_constraint(
                Tsetup[(m,d,t)] >= mdl.sum(Setup[(m,bb1,bb2)] * w[(m,bb1,bb2,d,t)]
                                           for (bb1,bb2) in relevant_pairs),
                ctname=f"R6_T_def[{m},{d},{t}]"
            )

    # ---------------- Compatibilidad opcional ----------------
    if enforce_tipo:
        for m,b,d,t,s in product(M,B,D,T_turnos,S_segmentos):
            if Tipo[(m,b)] == 0:
                mdl.add_constraint(x[(m,b,d,t,s)] == 0, ctname=f"Compat[{m},{b},{d},{t},{s}]")

    # ---------------- Función objetivo ----------------
    mdl.minimize(mdl.sum(Tsetup[(m,d,t)] for m,d,t in product(M,D,T_turnos)))

    return mdl, x, y, Tsetup


# 3) Obtener insumos
# 2) Instanciar Processing
proc = Processing(
df_turnos=df_turnos,
df_disponibilidad_maquinas=df_disponibilidad_maquinas,
df_setup=df_tiempo_setup_por_maquina,
df_duracion_turno_dia=df_duracion_turno_dia,
df_productividad_maquina_caja=df_productividad_maquina_caja
)

# 3) Obtener insumos
T_turnos = proc.process_turnos()                 # {d: [1..k_d]}
Disp = proc.process_disponibilidad_maquinas()          # {(m,d): 0/1}
Setup = proc.process_tiempo_setup()                    # {(m,b1,b2): horas}
Tturn_dt = proc.process_turn_duration()                # {(d,t): horas}
Prod, Tipo, M, B = proc.process_productividad_y_tipo() # dicts y dominios
Tturn = 9
# 4) Armar conjuntos para el modelo
D = sorted(T_turnos.keys())
DT = [(d, t) for d in D for t in T_turnos[d]]    # pares (día, turno) activos
S_segmentos = [1, 2]

# 5) Demanda (ejemplo: si aún no la traes de un DF, pon 0 o carga tu DF)
Dem = {(b, d): 9.0 for b in B for d in D}  # <-- reemplaza por tu lectura real de demanda


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