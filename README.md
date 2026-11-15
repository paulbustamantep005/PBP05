# Casa Olmo · Análisis de ventas y rentabilidad de un restaurante

Caso de ejemplo de análisis de datos para un restaurante **ficticio**, con un año de ventas **simuladas** (nov 2025 – oct 2026). El proyecto sigue el ciclo completo de un trabajo de datos: generar o preparar los datos, analizarlos, sacar conclusiones de negocio y convertirlas en recomendaciones con impacto en pesos.

> Todos los datos son simulados. Casa Olmo no es un negocio real.

## Pregunta de negocio

¿Dónde está perdiendo dinero el restaurante y qué ajustes concretos podrían aumentar su ganancia sin vender más?

## Hallazgos principales

| Indicador | Resultado |
| --- | --- |
| Ventas del año | $20.0 M MXN |
| Cuentas atendidas | 36,539 |
| Ticket promedio | $548 MXN |
| Margen tras insumos y comisiones | 62.6% |
| Comisiones pagadas a apps de delivery | $604 mil MXN |

- **Horarios muertos:** lunes y martes de 17 a 19 h llegan de 1 a 2 cuentas por hora, contra 4 a 5 en miércoles y jueves.
- **Delivery:** las apps pasaron de 9.1% a 15.8% de las ventas mensuales, pero de cada peso vendido por app queda 39.4%, contra 65.8% en el salón.
- **Menú:** 3 platillos estrella, 5 caballos de batalla (se venden mucho pero dejan poco), 4 enigmas y 2 perros.

## Recomendaciones

| # | Acción | Impacto anual estimado |
| --- | --- | --- |
| 1 | Subir 8% el precio de los caballos de batalla | +$253 mil |
| 2 | Mover 30% de los pedidos de apps a un canal directo (WhatsApp o pedido propio) | +$145 mil |
| 3 | Promoción de lunes y martes de 17 a 19 h | +$165 mil |
| 4 | Rediseñar o retirar los platillos "perro" | Por medir |
| | **Total estimado** | **+$563 mil al año** |

Cada impacto se calcula con un supuesto explícito en el código (por ejemplo, que las unidades bajan 5% al subir el precio).

## Análisis incluidos

1. **Indicadores generales:** ventas, cuentas, ticket promedio, margen y comisiones.
2. **Ventas mensuales** y participación de cada canal.
3. **Mapa de calor** de cuentas promedio por día de la semana y hora.
4. **Ingeniería de menú** (matriz de Kasavana y Smith): clasifica cada platillo por popularidad y ganancia por plato en Estrella, Caballo de batalla, Enigma o Perro.
5. **Rentabilidad por canal:** salón, para llevar y apps de delivery (25% de comisión).
6. **Recomendaciones** con impacto económico estimado.

## Cómo se simularon los datos

- Menú de 18 productos con precio y costo de insumos.
- Demanda diaria según día de la semana (viernes y sábado más altos), temporada (pico en diciembre, baja en enero y febrero) y una tendencia de crecimiento de 10% anual.
- Horas pico de comida y cena, y una caída intencional los lunes y martes por la tarde.
- La participación de delivery crece durante el año.
- Semilla aleatoria fija (`42`): cada ejecución produce exactamente los mismos datos.

Resultado: unas 178,000 líneas de venta.

## Estructura

```
├── generar_y_analizar.py     # Genera los datos, hace el análisis y exporta resultados
├── ventas_casa_olmo.csv      # Detalle de ventas simuladas (se genera al correr el script)
├── casa_olmo_analisis.xlsx   # Excel con el detalle y cada análisis (se genera)
├── resultados.json           # Resumen de resultados (se genera)
└── tablero/                  # Datos para el tablero interactivo (se genera)
```

## Cómo ejecutarlo

```bash
pip install pandas numpy openpyxl
python generar_y_analizar.py
```

## Tecnologías

Python · pandas · NumPy · openpyxl · tablero interactivo con D3.js

## Autor

**Paul Bustamante** · Noxa, consultoría de datos e IA para empresas
