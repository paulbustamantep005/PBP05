"""
Noxa — Caso de portafolio: "Casa Olmo" (restaurante ficticio)
Genera 12 meses de ventas simuladas y produce el análisis:
  - KPIs generales
  - Ventas mensuales
  - Mapa de calor día x hora
  - Ingeniería de menú (popularidad vs. margen)
  - Rentabilidad por canal (salón, para llevar, apps de delivery)
  - Recomendaciones con impacto estimado
Todos los datos son ficticios.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
OUT = Path(__file__).parent

# ---------------------------------------------------------------- menú
# nombre, categoría, precio, costo, peso de popularidad
MENU = [
    ("Tacos de arrachera", "Platos fuertes", 189, 82, 9.0),
    ("Enchiladas suizas", "Platos fuertes", 165, 48, 7.5),
    ("Pozole rojo", "Platos fuertes", 155, 41, 6.0),
    ("Mole poblano con pollo", "Platos fuertes", 195, 58, 2.2),
    ("Filete de pescado a la talla", "Platos fuertes", 245, 118, 1.6),
    ("Costilla BBQ", "Platos fuertes", 275, 150, 1.4),
    ("Hamburguesa Olmo", "Platos fuertes", 179, 86, 8.0),
    ("Guacamole con totopos", "Entradas", 115, 38, 7.0),
    ("Queso fundido", "Entradas", 125, 36, 4.5),
    ("Tostadas de atún", "Entradas", 165, 52, 2.0),
    ("Sopa de tortilla", "Entradas", 95, 22, 3.0),
    ("Flan napolitano", "Postres", 75, 16, 4.0),
    ("Churros con chocolate", "Postres", 85, 21, 2.0),
    ("Pastel de tres leches", "Postres", 89, 34, 1.2),
    ("Agua fresca", "Bebidas", 45, 8, 12.0),
    ("Cerveza", "Bebidas", 65, 28, 8.0),
    ("Margarita", "Bebidas", 120, 30, 3.5),
    ("Café de olla", "Bebidas", 45, 9, 3.0),
]
menu = pd.DataFrame(MENU, columns=["platillo", "categoria", "precio", "costo", "peso"])
food = menu[menu.categoria != "Bebidas"].reset_index(drop=True)
drinks = menu[menu.categoria == "Bebidas"].reset_index(drop=True)

CANALES = ["Salón", "Para llevar", "App de delivery"]
COMISION = {"Salón": 0.0, "Para llevar": 0.0, "App de delivery": 0.25}

# --------------------------------------------------------- calendario
dias = pd.date_range("2025-11-01", "2026-10-31", freq="D")
factor_dia = {0: 0.62, 1: 0.70, 2: 0.85, 3: 0.95, 4: 1.30, 5: 1.45, 6: 1.15}  # lun..dom
factor_mes = {11: 1.00, 12: 1.25, 1: 0.80, 2: 0.88, 3: 0.95, 4: 1.00,
              5: 1.05, 6: 0.98, 7: 1.02, 8: 0.97, 9: 1.08, 10: 1.03}
horas = np.arange(13, 24)  # 13:00 a 23:00
peso_hora = np.array([0.6, 1.4, 1.6, 1.0, 0.45, 0.4, 0.6, 1.1, 1.5, 1.2, 0.5])

rows = []
ticket_id = 0
for i, d in enumerate(dias):
    tendencia = 1 + 0.10 * i / len(dias)  # crecimiento de 10% en el año
    base = 95 * factor_dia[d.dayofweek] * factor_mes[d.month] * tendencia
    n_tickets = rng.poisson(base)
    # lunes y martes por la tarde (17-19 h) casi muertos
    ph = peso_hora.copy()
    if d.dayofweek in (0, 1):
        ph[4:7] *= 0.45
    ph = ph / ph.sum()
    # la participación de delivery crece de 18% a 32% en el año
    p_deliv = 0.18 + 0.14 * i / len(dias)
    p_canal = [0.82 - p_deliv - 0.12 + 0.12, 0.12, p_deliv]
    p_canal[0] = 1 - p_canal[1] - p_canal[2]
    for _ in range(n_tickets):
        ticket_id += 1
        h = rng.choice(horas, p=ph)
        canal = rng.choice(CANALES, p=p_canal)
        personas = 1 if canal != "Salón" else rng.choice([1, 2, 3, 4, 5, 6],
                                                         p=[.12, .38, .2, .2, .06, .04])
        n_food = max(1, rng.poisson(personas * 1.2))
        n_drk = rng.poisson(personas * (1.1 if canal == "Salón" else 0.5))
        items = list(rng.choice(food.index, size=n_food, p=food.peso / food.peso.sum()))
        for idx in items:
            rows.append((ticket_id, d, h, canal, personas, food.loc[idx, "platillo"]))
        for idx in rng.choice(drinks.index, size=n_drk, p=drinks.peso / drinks.peso.sum()):
            rows.append((ticket_id, d, h, canal, personas, drinks.loc[idx, "platillo"]))

ventas = pd.DataFrame(rows, columns=["ticket", "fecha", "hora", "canal", "personas", "platillo"])
ventas = ventas.merge(menu[["platillo", "categoria", "precio", "costo"]], on="platillo")
ventas["comision"] = ventas.precio * ventas.canal.map(COMISION)
ventas["margen_neto"] = ventas.precio - ventas.costo - ventas.comision
ventas = ventas.sort_values(["ticket"]).reset_index(drop=True)
ventas.to_csv(OUT / "ventas_casa_olmo.csv", index=False)

# ------------------------------------------------------------- análisis
r = {}
venta_total = ventas.precio.sum()
tickets = ventas.ticket.nunique()
r["kpis"] = {
    "ventas_totales": round(float(venta_total)),
    "tickets": int(tickets),
    "ticket_promedio": round(float(venta_total / tickets), 1),
    "margen_bruto_pct": round(float((venta_total - ventas.costo.sum()) / venta_total * 100), 1),
    "comisiones_apps": round(float(ventas.comision.sum())),
    "margen_neto_pct": round(float(ventas.margen_neto.sum() / venta_total * 100), 1),
    "platillos_vendidos": int(len(ventas)),
}

ventas["mes"] = ventas.fecha.dt.to_period("M").astype(str)
mensual = ventas.groupby("mes").agg(ventas=("precio", "sum"),
                                    margen_neto=("margen_neto", "sum")).reset_index()
pm = ventas.groupby(["mes", "canal"]).precio.sum().unstack(fill_value=0)
mensual["pct_delivery"] = (pm["App de delivery"] / pm.sum(axis=1) * 100).values
r["mensual"] = [{"mes": m, "ventas": round(float(v)), "margen_neto": round(float(mn)),
                 "pct_delivery": round(float(p), 1)}
                for m, v, mn, p in mensual.itertuples(index=False)]

# mapa de calor: tickets promedio por día de semana y hora
tk = ventas.drop_duplicates("ticket")[["fecha", "hora"]].copy()
tk["dow"] = tk.fecha.dt.dayofweek
n_dias_dow = pd.Series(dias.dayofweek).value_counts()
heat = tk.groupby(["dow", "hora"]).size().unstack(fill_value=0)
heat = heat.div(n_dias_dow.sort_index(), axis=0)
nombres_dia = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
r["calor"] = [{"dia": nombres_dia[dw], "hora": int(h), "tickets": round(float(heat.loc[dw, h]), 2)}
              for dw in heat.index for h in heat.columns]

# ingeniería de menú (solo alimentos)
al = ventas[ventas.categoria != "Bebidas"]
me = al.groupby("platillo").agg(unidades=("precio", "size"), precio=("precio", "first"),
                                costo=("costo", "first"), categoria=("categoria", "first")).reset_index()
me["margen_unit"] = me.precio - me.costo
me["margen_total"] = me.margen_unit * me.unidades
umbral_pop = me.unidades.sum() / len(me) * 0.70
umbral_margen = me.margen_total.sum() / me.unidades.sum()


def clasif(row):
    alta_pop = row.unidades >= umbral_pop
    alto_mg = row.margen_unit >= umbral_margen
    if alta_pop and alto_mg:
        return "Estrella"
    if alta_pop:
        return "Caballo de batalla"
    if alto_mg:
        return "Enigma"
    return "Perro"


me["clase"] = me.apply(clasif, axis=1)
me["food_cost_pct"] = me.costo / me.precio * 100
r["menu"] = [{"platillo": x.platillo, "categoria": x.categoria, "unidades": int(x.unidades),
              "precio": int(x.precio), "margen_unit": int(x.margen_unit),
              "margen_total": int(x.margen_total), "food_cost_pct": round(float(x.food_cost_pct), 1),
              "clase": x.clase} for x in me.sort_values("margen_total", ascending=False).itertuples()]
r["umbrales"] = {"popularidad": round(float(umbral_pop)), "margen": round(float(umbral_margen), 1)}

# canales
ca = ventas.groupby("canal").agg(ventas=("precio", "sum"), costo=("costo", "sum"),
                                 comision=("comision", "sum"), margen_neto=("margen_neto", "sum"),
                                 tickets=("ticket", "nunique")).reset_index()
ca["margen_neto_pct"] = ca.margen_neto / ca.ventas * 100
ca["ticket_prom"] = ca.ventas / ca.tickets
r["canales"] = [{"canal": x.canal, "ventas": round(float(x.ventas)), "comision": round(float(x.comision)),
                 "margen_neto": round(float(x.margen_neto)),
                 "margen_neto_pct": round(float(x.margen_neto_pct), 1),
                 "ticket_prom": round(float(x.ticket_prom), 1), "tickets": int(x.tickets)}
                for x in ca.itertuples()]

# ---------------------------------------------------- recomendaciones
rec = []
# 1) Subir 8% el precio de los caballos de batalla (supuesto: caída de 5% en unidades)
cb = me[me.clase == "Caballo de batalla"]
nuevo = ((cb.precio * 1.08 - cb.costo) * cb.unidades * 0.95).sum()
actual = cb.margen_total.sum()
rec.append({"accion": "Subir 8% el precio de los caballos de batalla (" + ", ".join(cb.platillo) + ")",
            "supuesto": "Las unidades bajan 5% por el aumento",
            "impacto_anual": round(float(nuevo - actual))})
# 2) Pasar 30% de pedidos de app a canal directo (WhatsApp / pedido propio)
dl = ca[ca.canal == "App de delivery"].iloc[0]
rec.append({"accion": "Mover 30% de los pedidos de apps a un canal directo (WhatsApp o pedido en línea propio)",
            "supuesto": "Se ahorra la comisión de 25% en esos pedidos; se descuenta 5% por costo del canal propio",
            "impacto_anual": round(float(dl.ventas * 0.30 * (0.25 - 0.05)))})
# 3) Promoción lunes y martes de 17 a 19 h
tk_lm = tk[(tk.dow.isin([0, 1])) & (tk.hora.between(17, 19))]
n_lm_dias = int(n_dias_dow[0] + n_dias_dow[1])
tk_otros = tk[(tk.dow.isin([2, 3])) & (tk.hora.between(17, 19))]
n_otros_dias = int(n_dias_dow[2] + n_dias_dow[3])
gap = (len(tk_otros) / n_otros_dias - len(tk_lm) / n_lm_dias)
margen_ticket_salon = float(ca[ca.canal == "Salón"].margen_neto.iloc[0] / ca[ca.canal == "Salón"].tickets.iloc[0])
rec.append({"accion": "Promoción de lunes y martes de 17 a 19 h para cerrar la mitad de la brecha con miércoles y jueves",
            "supuesto": f"{gap / 2:.1f} tickets extra por día con 20% de descuento sobre el margen del ticket de salón",
            "impacto_anual": round(gap / 2 * n_lm_dias * margen_ticket_salon * 0.80)})
# 4) Rediseñar o retirar perros
pe = me[me.clase == "Perro"]
rec.append({"accion": "Rediseñar o retirar los perros (" + ", ".join(pe.platillo) + ")",
            "supuesto": "Menos mermas e inventario; impacto no cuantificado",
            "impacto_anual": None})
r["recomendaciones"] = rec
r["periodo"] = "nov 2025 – oct 2026"

(OUT / "resultados.json").write_text(json.dumps(r, ensure_ascii=False, indent=2))

with pd.ExcelWriter(OUT / "casa_olmo_analisis.xlsx") as xw:
    ventas.drop(columns=["mes"]).to_excel(xw, sheet_name="Ventas (detalle)", index=False)
    me.sort_values("margen_total", ascending=False).to_excel(xw, sheet_name="Ingeniería de menú", index=False)
    ca.to_excel(xw, sheet_name="Canales", index=False)
    mensual.to_excel(xw, sheet_name="Mensual", index=False)
    pd.DataFrame(rec).to_excel(xw, sheet_name="Recomendaciones", index=False)

# ------------------------------------------ archivos para el tablero
codigo = Path(__file__).read_text()
meta = [{"label": "generar_y_analizar.py", "value": codigo, "type": "code", "lang": "python"},
        {"label": "Datos", "value": "Simulados con semilla 42; restaurante ficticio"}]
k = dict(r["kpis"])
k["impacto_total"] = sum(x["impacto_anual"] or 0 for x in rec)
k["umbral_popularidad"] = r["umbrales"]["popularidad"]
k["umbral_margen"] = r["umbrales"]["margen"]
k["pct_delivery_inicio"] = r["mensual"][0]["pct_delivery"]
k["pct_delivery_fin"] = r["mensual"][-1]["pct_delivery"]
tablas = {"kpis": [k], "mensual": r["mensual"], "calor": r["calor"], "menu": r["menu"],
          "canales": r["canales"],
          "recomendaciones": [dict(x, orden=i + 1) for i, x in enumerate(rec)]}
(OUT / "tablero").mkdir(exist_ok=True)
for nombre, filas in tablas.items():
    (OUT / "tablero" / f"{nombre}.json").write_text(
        json.dumps({"rows": filas, "meta": meta}, ensure_ascii=False))

print(json.dumps({k: r[k] for k in ["kpis", "umbrales", "canales", "recomendaciones"]},
                 ensure_ascii=False, indent=1))
print(me.sort_values("margen_total", ascending=False)[["platillo", "unidades", "margen_unit", "clase"]].to_string())
