import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json, os, sys

sys.stdout.reconfigure(encoding='utf-8')
st.set_page_config(page_title="Casa Gracia - Diagnostico", layout="wide")

# ─── Colors (previous palette - professional blue/orange/red) ─
CG    = "#4C72B0"  # blue - Casa Gracia
COMP  = "#DD8452"  # orange - competidores
MKT   = "#C44E52"  # red - mercado
POS   = "#55A868"  # green - positivo
WARN  = "#DD8452"  # orange - warning
NEG   = "#C44E52"  # red - negativo

# ─── Load Data ───────────────────────────────────────────────
@st.cache_data
def load_reviews():
    for p in [os.path.join("..", "data", "booking_reviews_clean.json"),
              os.path.join("data", "booking_reviews_clean.json")]:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
    return []

@st.cache_data
def load_airbnb_prices():
    for p in [os.path.join("..", "data", "airbnb_prices.csv"),
              os.path.join("data", "airbnb_prices.csv")]:
        if os.path.exists(p):
            return pd.read_csv(p)
    return None

# ─── Common Data ─────────────────────────────────────────────
months = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
cg_prices   = [62, 62, 65, 66, 62, 62, 66, 80, 69, 66, 66, 89]
# Bahia Azul: real from Booking calendar (Jun-Dec), estimated Jan-May based on low-season pattern
ba_prices   = [61, 61, 64, 64, 61, 61, 61, 64, 68, 72, 73, 75]
mkt_prices  = [192,192,192,216,216,192,192,192,192,192,216,230]
occ   = [0.78,0.55,0.75,0.65,0.60,0.66,0.68,0.66,0.60,0.62,0.72,0.80]
sug   = [71, 71, 75, 76, 71, 71, 76, 92, 79, 76, 76, 102]  # CG +15%

# ─── Sidebar ─────────────────────────────────────────────────
st.sidebar.markdown(
    '<div style="background:linear-gradient(135deg,#4C72B0,#1a3a6a);border-radius:8px;padding:20px;text-align:center">'
    '<h3 style="color:white;margin:0">Casa Gracia</h3>'
    '<p style="color:#ccc;margin:4px 0 0 0">Hotel Boutique</p>'
    "</div>",
    unsafe_allow_html=True,
)
st.sidebar.markdown("## Casa Gracia Hotel Boutique")
st.sidebar.markdown("Cra. 17 #26-133, Manga, Cartagena")
st.sidebar.markdown("---")
st.sidebar.markdown("**:material/database: Datos recolectados**")
for item in [
    ":green[REAL] Booking: 49 resenas + sub-scores",
    ":green[REAL] Booking: calendario CG (200+ dias)",
    ":green[REAL] Instagram: 1,787 seguidores",
    ":green[REAL] Booking: 25 hoteles x temporada",
    ":green[REAL] Booking: Bahia Azul sub-scores",
    ":green[REAL] Booking: Bahia Azul precios mensuales (calendario)",
    ":green[REAL] Google: 45 reviews + distribucion",
    ":blue[DOC] Ocupacion: Cotelco (referencia)",
    ":orange[EST] Ingresos: proyeccion propia",
    ":orange[EST] RevPAR: calculo estimado",
]:
    st.sidebar.markdown(f":material/check: {item}")
st.sidebar.markdown("---")
st.sidebar.caption("Diagnostico - 17 Jun 2026")

# ─── Title ───────────────────────────────────────────────────
st.title("Casa Gracia Hotel Boutique — Diagnostico de Datos")
st.caption("Analisis de pricing, resenas, competencia y presencia digital")
st.divider()

tab_dash, tab_data = st.tabs([
    ":material/dashboard: Dashboard",
    ":material/table_chart: Datos Detallados",
])

# ═══════════════════════════════════════════════════════════════
# TAB 1 — DASHBOARD
# ═══════════════════════════════════════════════════════════════
with tab_dash:
    # ─── KPIs ──────────────────────────────────────────────
    cg_avg_price = round(sum(cg_prices) / 12)
    ba_avg_price = round(sum(ba_prices) / 12)
    revpar_act = round(cg_avg_price * 0.68)
    revpar_pot = round(max(sug) * 0.75)
    revpar_gap = revpar_pot - revpar_act
    price_gap = cg_avg_price - ba_avg_price

    st.markdown("**:material/star: Reputacion**")
    r1,r2,r3,r4 = st.columns(4)
    r1.metric("Booking Rating",  "9.0/10",       f"-{9.4-9.0:.1f} vs BA")
    r2.metric("Airbnb Rating",   "4.83/5",       "~56 evaluaciones")
    r3.metric("Google Rating",   "4.5/5",        "45 resenas")
    r4.metric("TripAdvisor",     "0 resenas",    "Perfil sin gestion")

    st.markdown("**:material/bar_chart: Performance**")
    p1,p2,p3,p4 = st.columns(4)
    p1.metric("Precio Promedio", f"${cg_avg_price}/noche", f"+{price_gap} vs BA ${ba_avg_price}")
    p2.metric("RevPAR Est.",     f"${revpar_act}",          f"+{revpar_gap} potencial ${revpar_pot}")
    p3.metric("Ocupacion Est.",  "68%",                    "ref. Cotelco")
    p4.metric("Instagram",       "1,787",                   "115 posts")

    st.caption(f"RevPAR = ADR ${cg_avg_price} x ocupacion 68% (ref. Cotelco Manga)")
    st.divider()

    # ─── ROW 2: Pricing (problem) + Revenue (opportunity) ──
    rc1, rc2 = st.columns([60, 40])

    with rc1:
        # --- PRICING LINE CHART - 12 months: Manga competitors ---
        months_12 = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
        # Casa Gracia: Booking calendar (real Jun-Dec, est Jan-May)
        cg_avg = [62, 62, 65, 66, 62, 62, 66, 80, 69, 66, 66, 89]
        cg_min = [60, 60, 63, 63, 60, 60, 60, 80, 66, 66, 66, 66]
        cg_max = [66, 66, 68, 68, 66, 66, 80, 83, 80, 66, 66, 132]
        # Bahia Azul: Booking calendar (real Jun-Dec from CSV, est Jan-May)
        ba_avg = ba_prices  # alias - same array used for revenue table
        ba_min = [60, 60, 63, 63, 60, 60, 60, 60, 68, 68, 68, 68]
        ba_max = [63, 63, 68, 68, 63, 63, 63, 68, 68, 85, 82, 106]

        fig1 = go.Figure()

        # --- Casa Gracia range band ---
        fig1.add_trace(go.Scatter(
            x=months_12, y=cg_min,
            mode='lines', name='CG (min)',
            line=dict(color='rgba(76,114,176,0)', width=0),
            showlegend=False, hoverinfo='skip',
        ))
        fig1.add_trace(go.Scatter(
            x=months_12, y=cg_max,
            mode='lines', fill='tonexty',
            name='Casa Gracia rango',
            line=dict(color='rgba(76,114,176,0)', width=0),
            fillcolor='rgba(76,114,176,0.15)',
            showlegend=True, legendgroup='cg',
        ))
        fig1.add_trace(go.Scatter(
            x=months_12, y=cg_avg,
            mode='lines+markers', name='Casa Gracia (prom.)',
            line=dict(color=CG, width=3),
            marker=dict(size=10, color=CG),
            legendgroup='cg',
        ))

        # --- Bahia Azul range band ---
        fig1.add_trace(go.Scatter(
            x=months_12, y=ba_min,
            mode='lines', name='BA (min)',
            line=dict(color='rgba(221,132,82,0)', width=0),
            showlegend=False, hoverinfo='skip',
        ))
        fig1.add_trace(go.Scatter(
            x=months_12, y=ba_max,
            mode='lines', fill='tonexty',
            name='Bahia Azul rango',
            line=dict(color='rgba(221,132,82,0)', width=0),
            fillcolor='rgba(221,132,82,0.15)',
            showlegend=True, legendgroup='ba',
        ))
        fig1.add_trace(go.Scatter(
            x=months_12, y=ba_avg,
            mode='lines+markers', name='Bahia Azul (prom.)',
            line=dict(color=COMP, width=2.5, dash='dash'),
            marker=dict(size=7, color=COMP),
            legendgroup='ba',
        ))

        fig1.update_layout(
            title="Precio por Noche Mensual — Manga (USD)",
            yaxis_title="USD / noche",
            hovermode="x unified", height=400,
            margin=dict(l=0, r=0, t=50, b=40),
            legend=dict(orientation="h", y=-0.4),
        )
        st.plotly_chart(fig1, width="stretch")
        st.caption(":green[CG + BA: Booking calendario] | Ene-May estimados, Jun-Dic reales | COP->USD @ 4,200")

    with rc2:
        # --- REVENUE GAP AREA CHART ---
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=months, y=cg_prices,
            mode='lines+markers', name='Actual (CG real)',
            line=dict(color=CG, width=2),
            marker=dict(size=6, color=CG),
        ))
        fig2.add_trace(go.Scatter(
            x=months, y=sug,
            mode='lines+markers', name='Potencial (CG +15%)',
            line=dict(color=POS, width=2, dash='dash'),
            marker=dict(size=6, color=POS),
            fill='tonexty',
            fillcolor='rgba(85,168,104,0.12)',
        ))
        for i, m in enumerate(months):
            gap = sug[i] - cg_prices[i]
            if gap > 5:
                fig2.add_annotation(x=m, y=sug[i], text=f"+${gap}",
                                    showarrow=False, font=dict(size=9, color=POS),
                                    yshift=8, yanchor="bottom")
        fig2.update_layout(
            title="Gap de Pricing: Precio Real CG vs Potencial (+15%)",
            yaxis_title="USD / noche",
            height=400,
            margin=dict(l=0, r=0, t=40, b=40),
            legend=dict(orientation="h", y=-0.2),
        )
        st.plotly_chart(fig2, width="stretch")
        st.caption(":green[CG precios reales Booking calendario] | Potencial: precio actual +15%")

    st.divider()

    # ─── ROW 3: Competition + Sentiment + Digital ──────────
    rc3, rc4, rc5 = st.columns([28, 40, 32])

    with rc3:
        # --- COMPETITION SCATTER ---
        comp = pd.DataFrame([
            dict(H="Casa Gracia",      R=9.0,  P=68,  N=270),
            dict(H="Bahia Azul",       R=9.4,  P=67,  N=39),
            dict(H="San Sebastian R.", R=8.7,  P=96,  N=126),
            dict(H="Casa Jaguar",      R=9.7,  P=93,  N=150),
            dict(H="Tierra Del Mar",   R=9.0,  P=55,  N=97),
        ])

        fig3 = go.Figure()
        cg_row = comp[comp.H == "Casa Gracia"].iloc[0]
        others = comp[comp.H != "Casa Gracia"]

        # Regression line (4 boutiques)
        xo, yo = others.R.values, others.P.values
        n = len(xo)
        m = (n * (xo*yo).sum() - xo.sum()*yo.sum()) / (n * (xo*xo).sum() - xo.sum()**2)
        b = (yo.sum() - m*xo.sum()) / n
        x_line = [7.5, 10.5]
        y_line = [m*x + b for x in x_line]
        fig3.add_trace(go.Scatter(
            x=x_line, y=y_line, mode='lines',
            line=dict(color='gray', width=1.5, dash='dot'),
            name='Tendencia', showlegend=False,
        ))

        # Casa Gracia
        fig3.add_trace(go.Scatter(
            x=[cg_row.R], y=[cg_row.P],
            mode='markers+text',
            marker=dict(symbol='circle', size=10, color=CG, line=dict(width=1, color='white')),
            text=["Casa Gracia"], textposition="top center",
            textfont=dict(size=9, color=CG),
        ))
        # Competitors
        fig3.add_trace(go.Scatter(
            x=others.R, y=others.P,
            mode='markers+text',
            marker=dict(symbol='circle', size=10, color=COMP,
                        line=dict(width=1, color='white'), opacity=0.8),
            text=others.H, textposition="top center",
            textfont=dict(size=9),
        ))

        fig3.update_layout(
            title="Rating vs Precio — Competencia Directa",
            xaxis_title="Booking Rating",
            yaxis_title="USD / noche",
            height=320,
            margin=dict(l=0, r=0, t=40, b=0),
            showlegend=False,
        )
        st.plotly_chart(fig3, width="stretch")
        st.caption(":green[REAL Booking.com] | :blue[DOC Booking/Expedia: Tierra Del Mar] | Tendencia: 4 boutiques comparables")

    with rc4:
        cats_ord = ["WiFi gratis","Relación calidad-precio","Instalaciones y servicios",
                     "Confort","Ubicación","Limpieza","Anfitrión"]
        cg_scores = [9.0, 9.1, 9.2, 9.2, 9.1, 9.4, 9.5]
        ba_scores = [8.8, 9.3, 8.9, 9.7, 9.6, 9.3, 9.6]

        fig4 = go.Figure()
        fig4.add_trace(go.Bar(
            y=cats_ord, x=cg_scores,
            orientation="h", name="Casa Gracia",
            marker_color=CG,
            text=[f"{s:.1f}" for s in cg_scores],
            textposition="outside",
            textfont=dict(size=9),
        ))
        fig4.add_trace(go.Bar(
            y=cats_ord, x=ba_scores,
            orientation="h", name="Bahia Azul",
            marker_color=COMP,
            text=[f"{s:.1f}" for s in ba_scores],
            textposition="outside",
            textfont=dict(size=9),
        ))
        fig4.update_layout(
            barmode="group",
            title="Puntuaciones Booking: Casa Gracia vs Bahia Azul",
            xaxis=dict(range=[7.5, 10.5], title="Puntuacion /10", dtick=0.5, title_font=dict(size=10)),
            yaxis_title="",
            height=360,
            margin=dict(l=90, r=15, t=40, b=60),
            legend=dict(orientation="h", y=-0.2),
        )
        st.plotly_chart(fig4, width="stretch")
        st.caption(":green[Sub-scores Booking.com reales]")

    with rc5:
        st.markdown("**:material/devices: Salud Digital por Canal**")
        ch_canales = ["Booking.com", "Airbnb", "Instagram", "TripAdvisor", "Google B.", "Facebook"]
        ch_metricas = ["Perfil", "Contenido", "Resenas", "Gestion"]
        ch_valores = [
            [1.0, 1.0, 1.0, 1.0],
            [1.0, 0.5, 1.0, 0.8],
            [1.0, 0.6, 0.5, 0.3],
            [0.5, 0.0, 0.0, 0.0],
            [1.0, 0.3, 1.0, 0.3],
            [0.0, 0.0, 0.0, 0.0],
        ]

        def _badge(v):
            if v >= 1.0:
                color = POS
            elif v >= 0.5:
                color = WARN
            else:
                color = NEG
            return (
                f'<span style="display:inline-flex;align-items:center;gap:5px;white-space:nowrap">'
                f'<span style="display:inline-block;width:10px;height:10px;border-radius:50%;'
                f'background:{color};flex-shrink:0"></span>'
                f'{v*100:.0f}%</span>'
            )

        rows_html = ""
        for i, canal in enumerate(ch_canales):
            cells = "".join(
                f'<td style="text-align:center;padding:5px 6px;border-bottom:1px solid #eee">'
                f'{_badge(ch_valores[i][j])}</td>'
                for j in range(len(ch_metricas))
            )
            rows_html += (
                f'<tr><td style="padding:5px 8px;border-bottom:1px solid #eee;font-weight:500">'
                f'{canal}</td>{cells}</tr>'
            )

        headers = "".join(
            f'<th style="text-align:center;padding:6px 6px;border-bottom:2px solid #ddd;'
            f'font-size:12px;color:#555;font-weight:500">{m}</th>'
            for m in ch_metricas
        )

        html = (
            f'<table style="width:100%;font-size:13px;border-collapse:collapse">'
            f'<tr><th style="text-align:left;padding:6px 8px;border-bottom:2px solid #ddd;'
            f'font-size:12px;color:#555;font-weight:500">Canal</th>{headers}</tr>'
            f'{rows_html}</table>'
        )
        st.markdown(html, unsafe_allow_html=True)
        st.caption("0% = inactivo / 100% = optimo | :green[Verificado manualmente]")

    st.divider()
    st.markdown("**:material/star: Google Reviews — 45 opiniones (Promedio 4.5/5)**")
    g1,g2,g3,g4,g5 = st.columns(5)
    g1.metric("5★", "35")
    g2.metric("4★", "3")
    g3.metric("3★", "3")
    g4.metric("2★", "2")
    g5.metric("1★", "2")
    st.success(
        ":material/thumb_up: **41% de las resenas en Booking mencionan al personal por nombre o cargo** (20 de 49)\n\n"
        "Este es el diferenciador mas fuerte de Casa Gracia: el servicio personalizado genera lealtad y recomendacion boca a boca."
    )

    st.divider()
    with st.expander("**:material/visibility: Con acceso a datos internos del hotel**"):
        st.markdown("""
| Situacion actual (datos publicos) | Con datos del PMS + Booking interno |
|---|---|
| RevPAR estimado ~$37 | RevPAR real por dia y habitacion |
| Ocupacion ~68% (estimado Cotelco) | Ocupacion real por mes, semana, dia |
| ADR ~$68 (Booking.com) | ADR real por canal (directo, OTA, web) |
| Revenue estimado ~$102K | Revenue real por mes + utilidad |
| Solo Booking + Airbnb visibles | Todos los canales medidos |
| Sin datos de cliente | Historial de huesped, preferencias, frecuencia |
""")

# ═══════════════════════════════════════════════════════════════
# TAB 2 — DATOS DETALLADOS
# ═══════════════════════════════════════════════════════════════
with tab_data:
    st.markdown("**:material/bed: Precios Airbnb por Habitacion y Temporada**")
    df_airbnb = load_airbnb_prices()
    if df_airbnb is not None:
        d = df_airbnb.copy()
        d["price_usd_per_night"] = d["price_usd_per_night"].apply(
            lambda x: f"${x:.0f}" if pd.notna(x) else "N/A"
        )
        st.dataframe(
            d[["room","season","checkin","checkout","price_usd_per_night"]],
            hide_index=True, width="stretch",
            column_config={
                "room":"Habitacion","season":"Temporada",
                "checkin":"Check-in","checkout":"Check-out",
                "price_usd_per_night":"USD / noche",
            },
        )

    st.divider()
    st.markdown("**:material/trending_up: Oportunidad de Pricing por Mes**")
    rows = []
    tcr = tpr = 0
    for i,m in enumerate(months):
        noches = 8 * occ[i] * 30.4
        cr = noches * cg_prices[i]
        pr = noches * sug[i]
        tcr += cr; tpr += pr
        rows.append({
            "Mes": m, "Casa": f"${cg_prices[i]}",
            "BA": f"${ba_prices[i]}",
            "Dif BA-CG": f"${ba_prices[i]-cg_prices[i]:+d} USD",
            "Ocup": f"{occ[i]*100:.0f}%", "Sug": f"${sug[i]}",
            "Actual": f"${cr:,.0f}", "Potencial": f"${pr:,.0f}",
        })
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
    st.caption(":orange[Ene-May estimados por patron de temporada baja (Jun). No reflejan eventos atipicos.]")
    diff = tpr - tcr
    c1,c2,c3 = st.columns(3)
    c1.metric("Ingreso Anual Actual",   f"${tcr:,.0f}")
    c2.metric("Ingreso Anual Potencial",f"${tpr:,.0f}")
    c3.metric("Ingreso Adicional",      f"${diff:,.0f}", delta=f"+{diff/tcr*100:.0f}%")

    st.divider()
    st.markdown("**:material/competitor: Comparativa de Competidores**")
    st.dataframe(
        pd.DataFrame([
            dict(Hotel="Casa Gracia",         Booking=9.0, Airbnb=4.83, Precio=66,  Resenas=270, Ubica="Manga"),
            dict(Hotel="Bahia Azul",          Booking=9.4, Airbnb=4.94, Precio=67,  Resenas=39,  Ubica="Manga"),
            dict(Hotel="C.C. Tipica",         Booking=None, Airbnb=4.88, Precio=45,  Resenas=12,  Ubica="Manga"),
            dict(Hotel="San Sebastian Real",  Booking=8.7, Airbnb=None,  Precio=96,  Resenas=126, Ubica="Manga/Cabrero"),
            dict(Hotel="Kim",                 Booking=8.4, Airbnb=None,  Precio=147, Resenas=955, Ubica="Getsemani"),
            dict(Hotel="Lunala",              Booking=8.5, Airbnb=4.80, Precio=138, Resenas=547, Ubica="Centro"),
            dict(Hotel="Casa Jaguar",         Booking=9.7, Airbnb=4.90, Precio=93,  Resenas=150, Ubica="Getsemani"),
        ]),
        hide_index=True, width="stretch",
    )

    st.divider()
    st.markdown("**:material/reviews: Patrones en Comentarios — Booking.com (49 resenas)**")
    reviews = load_reviews()

    pos_pats = [
        ("Personal / Staff", ["personal","staff","anfitri","recepcion","amable","atento","servicio","recibimiento","tomo las molestias"]),
        ("Limpieza", ["limpio","limpia","limpieza","impecable"]),
        ("Ubicacion", ["ubicacion","ubicado","cerca","centro","playa","manga","getsemani","caminando","segura","centrica"]),
        ("Habitacion / Confort", ["habitacion","comoda","comodo","confort","comodidad","cama","amplia","espaciosa","tranquilo","acogedor","banos modernos"]),
        ("Instalaciones / Extras", ["instalacion","piscina","terraza","cocina","decoracion","bonito","lindo","hermoso","cafe","detalle","cortesia","utensilios"]),
    ]
    neg_data = [
        ("Ruido (recepcion/calle/pasillos)", 5,
         "Habitacion justo a 3 metros frente a la recepcion, se escucha todo, trabajadores con su movil, ruido de un ventilador constante",
         "Cortes", "1.0/10"),
        ("Habitacion sin ventana/ventilacion", 3,
         "La habitacion no tiene ventana, algo que ni siquiera se menciona. No hay ventilacion, solo aire acondicionado",
         "Marie-christine", "1.0/10"),
        ("Personal poco amable/idioma", 3,
         "El personal no habla ingles. Uno de los miembros del staff no fue amable, nisiquiera nos saludo, era lento e intransigente",
         "Sara", "5.0/10"),
        ("Sin servicios basicos (agua/toallas/maletas)", 3,
         "No te cambian las toallas en 3 dias y te cobran si quieres dejar las maletas. No hay agua de cortesia",
         "Cortes", "1.0/10"),
        ("Sobrevalorado/calidad-precio", 3,
         "Habitacion muy pequena, el precio de 45€ por noche definitivamente no lo vale. Decepcion total",
         "Stella", "1.0/10"),
    ]

    def classify_pos(reviews, patterns):
        res = {c:[] for c,_ in patterns}
        for r in reviews:
            txt = r.get("positive_text","").lower().strip()
            if not txt:
                continue
            for cat,kws in patterns:
                if any(kw in txt for kw in kws):
                    res[cat].append(r)
        return res

    pos_res = classify_pos(reviews, pos_pats)
    pos_total = sum(len(v) for v in pos_res.values())
    neg_total = sum(c for _,c,_,_,_ in neg_data)

    total = len(reviews)
    staff_n = len(pos_res.get("Personal / Staff", []))

    c1,c2,c3 = st.columns(3)
    c1.metric("Mencionan al personal", f"{staff_n}/{total}", f"{staff_n*100//total}%")
    c2.metric("Reviews con puntuacion < 7", "5/49", "10%")
    c3.metric("Calificacion promedio", "9.0/10")

    with st.expander("**:material/thumb_up: Patrones Positivos**", expanded=True):
        st.caption("Clasificacion por keywords (una review puede contar en varias categorias). No analiza sentimiento — una mencion negativa del personal apareceria aqui igual.")
        for cat,_ in pos_pats:
            items = pos_res[cat]
            if not items:
                continue
            pct = len(items) * 100 // pos_total
            st.markdown(f"**{cat}** — {pct}% de las menciones ({len(items)} reviews)")
            for r in items[:1]:
                st.markdown(f"> {r.get('positive_text','')}")
                st.caption(f"— {r.get('guest_name','?')} ({r.get('rating','?')}/10)")
            st.markdown("---")

    with st.expander("**:material/thumb_down: Patrones de Mejora**", expanded=True):
        st.caption("Basado en ~10 reviews con puntuacion baja en Booking.com | conteo absoluto sobre total de quejas")
        for cat, count, quote, name, rating in neg_data:
            st.markdown(f"**{cat}** — {count} de {neg_total} quejas")
            st.markdown(f"> {quote}")
            st.caption(f"— {name} ({rating})")
            st.markdown("---")

    st.divider()
    st.markdown("**:material/star: Sub-scores de Google Reviews**")
    st.caption("Promedios calculados de reviews que incluyen puntuacion por categoria")
    st.dataframe(
        pd.DataFrame([
            ("Habitaciones", 9.4),
            ("Servicio", 8.6),
            ("Ubicacion", 9.0),
        ], columns=["Categoria", "Score (1-10)"]),
        hide_index=True, width="stretch",
    )

    st.divider()
    st.caption(
        "Datos reales: 49 resenas Booking, Booking calendario CG (200+ dias), Instagram, "
        "TripAdvisor (0), Booking 25 hoteles x temporada, Booking sub-scores, "
        "Booking calendario Bahia Azul (200+ dias), 45 Google reviews. | "
        "Documentados: ocupacion Cotelco, calendario eventos. | "
        "Estimados: proyeccion de ingresos."
    )
