"""
APLICATIVO DE CÁLCULO HIDROSTÁTICO - PROJETO INTEGRADOR AP1.1 (UEA/EST)
Desenvolvido em Python com Streamlit.
"""

import io
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from scipy.interpolate import interp1d, PchipInterpolator

# Configuração da Página
st.set_page_config(
    page_title="Cálculo Hidrostático Naval | AP1.1 UEA",
    page_icon="🚢",
    layout="wide"
)

# ==============================================================================
# 1. MOTOR DE INTEGRAÇÃO NUMÉRICA MANUAL (Item 9 do Edital)
# ==============================================================================
def trapz_rule(x, y):
    """Regra dos Trapézios."""
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    if len(x) < 2: return 0.0
    return float(np.sum(0.5 * (y[:-1] + y[1:]) * np.diff(x)))

def simpson_13_rule(y, h):
    """Regra de Simpson 1/3 (Número ímpar de pontos)."""
    if len(y) < 3 or (len(y) % 2 == 0):
        raise ValueError("Simpson 1/3 requer número ímpar de pontos.")
    s = y[0] + y[-1] + 4.0 * np.sum(y[1:-1:2]) + 2.0 * np.sum(y[2:-2:2])
    return float((h / 3.0) * s)

def simpson_38_rule(y, h):
    """Regra de Simpson 3/8 (Exatamente 4 pontos / 3 intervalos)."""
    if len(y) != 4:
        raise ValueError("Simpson 3/8 requer exatamente 4 pontos.")
    return float((3.0 * h / 8.0) * (y[0] + 3.0 * y[1] + 3.0 * y[2] + y[3]))

def integrate_dataset(x, y):
    """
    Integrador Híbrido com Trilha de Auditoria (Simpson 1/3 + 3/8 + Trapézios).
    """
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    n = len(x)
    if n < 2:
        return 0.0, [{"segment": "Indefinido", "method": "Pontos insuficientes", "area": 0.0}]
    
    if n == 2:
        area = trapz_rule(x, y)
        return area, [{"segment": f"[{x[0]:.2f} a {x[1]:.2f}]", "method": "Trapézio", "area": area}]
    
    dx = np.diff(x)
    is_uniform = np.allclose(dx, dx[0], rtol=1e-3)
    h = float(np.mean(dx))
    
    if not is_uniform:
        area = trapz_rule(x, y)
        return area, [{"segment": f"[{x[0]:.2f} a {x[-1]:.2f}]", "method": "Trapézio Não-Uniforme", "area": area}]
    
    # Estratégia Híbrida
    audit_log = []
    total_area = 0.0
    intervals = n - 1
    idx = 0
    
    while idx < intervals:
        rem = intervals - idx
        if rem % 2 == 0:
            sub_y = y[idx:]
            a = simpson_13_rule(sub_y, h)
            total_area += a
            audit_log.append({"segment": f"Ponto {idx} a {n-1} [x={x[idx]:.2f} a {x[-1]:.2f}]", "method": "Simpson 1/3", "area": a})
            break
        elif rem == 3 or rem > 3:
            sub_y = y[idx:idx+4]
            a = simpson_38_rule(sub_y, h)
            total_area += a
            audit_log.append({"segment": f"Ponto {idx} a {idx+3} [x={x[idx]:.2f} a {x[idx+3]:.2f}]", "method": "Simpson 3/8", "area": a})
            idx += 3
        else:
            sub_x, sub_y = x[idx:idx+2], y[idx:idx+2]
            a = trapz_rule(sub_x, sub_y)
            total_area += a
            audit_log.append({"segment": f"Ponto {idx} a {idx+1} [x={x[idx]:.2f} a {x[idx+1]:.2f}]", "method": "Trapézio", "area": a})
            idx += 1
            
    return float(total_area), audit_log

# ==============================================================================
# 2. MODELAGEM GEOMÉTRICA (Item 7 e 8 do Edital)
# ==============================================================================
class Hull:
    def __init__(self, stations_x, waterlines_z, offsets_matrix, LBP=None, B=None, D=None, Td=None):
        self.stations_x = np.asarray(stations_x, dtype=float)
        self.waterlines_z = np.asarray(waterlines_z, dtype=float)
        self.offsets = np.asarray(offsets_matrix, dtype=float)
        
        # Ordenação de segurança
        ox = np.argsort(self.stations_x)
        self.stations_x = self.stations_x[ox]
        self.offsets = self.offsets[:, ox]
        
        oz = np.argsort(self.waterlines_z)
        self.waterlines_z = self.waterlines_z[oz]
        self.offsets = self.offsets[oz, :]
        
        self.LBP = LBP or float(self.stations_x[-1] - self.stations_x[0])
        self.B = B or float(2.0 * np.max(self.offsets))
        self.D = D or float(self.waterlines_z[-1])
        self.Td = Td or float(self.D * 0.7)
        
        # Interpolação vertical por baliza
        self._station_interps = []
        for j in range(len(self.stations_x)):
            y_col = self.offsets[:, j]
            if len(self.waterlines_z) >= 3 and len(np.unique(y_col)) > 1:
                try:
                    interp = PchipInterpolator(self.waterlines_z, y_col)
                except Exception:
                    interp = interp1d(self.waterlines_z, y_col, kind='linear', fill_value='extrapolate')
            else:
                interp = interp1d(self.waterlines_z, y_col, kind='linear', fill_value='extrapolate')
            self._station_interps.append(interp)

    def get_y(self, station_idx, z):
        if z < self.waterlines_z[0]: return 0.0
        z = min(z, self.waterlines_z[-1])
        return max(0.0, float(self._station_interps[station_idx](z)))

def generate_barge_data(L=20.0, B=4.0, D=2.0, nx=11, nz=6):
    """Gera tabela de cotas sintética da barcaça retangular."""
    xs = np.linspace(0.0, L, nx)
    zs = np.linspace(0.0, D, nz)
    mat = np.full((nz, nx), B / 2.0)
    df = pd.DataFrame(mat, index=zs, columns=xs)
    df.index.name = "Z_WL"
    return df

# ==============================================================================
# 3. MOTOR HIDROSTÁTICO (Itens 10 a 19 do Edital)
# ==============================================================================
def calculate_hydrostatics_at_draft(hull: Hull, T: float, rho: float = 1.025):
    """Calcula todas as grandezas para o calado T."""
    n_st = len(hull.stations_x)
    xs = hull.stations_x
    z_grid = np.linspace(hull.waterlines_z[0], T, 35)
    dz = z_grid[1] - z_grid[0] if len(z_grid) > 1 else 0.0
    
    sec_areas = np.zeros(n_st)
    sec_mz = np.zeros(n_st)
    sec_girths = np.zeros(n_st)
    
    for j in range(n_st):
        y_vals = np.array([hull.get_y(j, z) for z in z_grid])
        half_a, _ = integrate_dataset(z_grid, y_vals)
        sec_areas[j] = 2.0 * half_a
        
        half_mz, _ = integrate_dataset(z_grid, z_grid * y_vals)
        sec_mz[j] = 2.0 * half_mz
        
        if len(y_vals) > 1 and dz > 0:
            sec_girths[j] = 2.0 * np.sum(np.sqrt(dz**2 + np.diff(y_vals)**2))
        else:
            sec_girths[j] = 2.0 * y_vals[-1]

    # Plano d'água
    y_wp = np.array([hull.get_y(j, T) for j in range(n_st)])
    half_awp, log_awp = integrate_dataset(xs, y_wp)
    awp = 2.0 * half_awp
    
    int_x_2y, _ = integrate_dataset(xs, xs * 2.0 * y_wp)
    lcf = (int_x_2y / awp) if awp > 1e-6 else float(np.mean(xs))
    
    it, log_it = integrate_dataset(xs, (2.0 / 3.0) * (y_wp ** 3))
    il, log_il = integrate_dataset(xs, 2.0 * ((xs - lcf) ** 2) * y_wp)
    
    # Volumes
    vol_long, log_vol_long = integrate_dataset(xs, sec_areas)
    
    # Volume Vertical
    z_steps = np.linspace(hull.waterlines_z[0], T, 15)
    awp_z = []
    for zi in z_steps:
        y_zi = np.array([hull.get_y(j, zi) for j in range(n_st)])
        h_a, _ = integrate_dataset(xs, y_zi)
        awp_z.append(2.0 * h_a)
    vol_vert, _ = integrate_dataset(z_steps, np.array(awp_z))
    
    err_vol = abs(vol_long - vol_vert) / vol_long * 100.0 if vol_long > 1e-6 else 0.0
    vol = vol_long
    
    # Centros
    int_x_ax, log_lcb = integrate_dataset(xs, xs * sec_areas)
    lcb = (int_x_ax / vol) if vol > 1e-6 else float(np.mean(xs))
    
    int_mz_x, log_kb = integrate_dataset(xs, sec_mz)
    kb = (int_mz_x / vol) if vol > 1e-6 else (T / 2.0)
    
    # Metacentros
    bmt = (it / vol) if vol > 1e-6 else 0.0
    kmt = kb + bmt
    bml = (il / vol) if vol > 1e-6 else 0.0
    kml = kb + bml
    
    # Deslocamento e Coeficientes
    disp = rho * vol
    tpc = (rho * awp) / 100.0
    wsa, _ = integrate_dataset(xs, sec_girths)
    
    mid_idx = n_st // 2
    am = float(sec_areas[mid_idx])
    L, B = hull.LBP, hull.B
    cb = (vol / (L * B * T)) if (L * B * T) > 1e-6 else 0.0
    cwp = (awp / (L * B)) if (L * B) > 1e-6 else 0.0
    cm = (am / (B * T)) if (B * T) > 1e-6 else 0.0
    cp = (vol / (am * L)) if (am * L) > 1e-6 else 0.0
    
    data = {
        "T": T, "Volume (∇)": vol, "Volume_Long": vol_long, "Volume_Vert": vol_vert, "Erro_Vol": err_vol,
        "Deslocamento (Δ)": disp, "LCB": lcb, "LCF": lcf, "KB": kb, "BMt": bmt, "KMt": kmt,
        "BMl": bml, "KMl": kml, "AWP": awp, "TPC": tpc, "WSA": wsa, "CB": cb, "CWP": cwp, "CM": cm, "CP": cp
    }
    
    # Dicionário de Auditoria para "Mostrar Cálculo"
    audit = {
        "Volume": {"formula": r"\nabla^L = \int_{0}^{L} A(x)\,dx", "data": f"L = {L:.2f} m, {n_st} estações", "intermediate": f"∇L = {vol_long:.3f} m³, ∇V = {vol_vert:.3f} m³ (Diferença: {err_vol:.4f}%)", "result": f"{vol:.3f}", "unit": "m³", "log": log_vol_long},
        "Deslocamento": {"formula": r"\Delta = \rho \cdot \nabla", "data": f"ρ = {rho:.3f} t/m³, ∇ = {vol:.3f} m³", "intermediate": f"{rho:.3f} * {vol:.3f}", "result": f"{disp:.3f}", "unit": "toneladas (t)"},
        "LCB": {"formula": r"LCB = \frac{\int x \cdot A(x)\,dx}{\nabla}", "data": f"∇ = {vol:.3f} m³", "intermediate": f"Momento Longitudinal = {int_x_ax:.3f} m⁴", "result": f"{lcb:.3f}", "unit": "m (da Perpendicular de Ré)", "log": log_lcb},
        "KB": {"formula": r"KB = \frac{\int M_z(x)\,dx}{\nabla}", "data": f"∇ = {vol:.3f} m³", "intermediate": f"Momento Vertical = {int_mz_x:.3f} m⁴", "result": f"{kb:.3f}", "unit": "m (da Linha de Base)", "log": log_kb},
        "AWP": {"formula": r"A^{WP} = 2 \int y(x, T)\,dx", "data": f"Calado T = {T:.3f} m", "intermediate": f"Meia-área = {half_awp:.3f} m²", "result": f"{awp:.3f}", "unit": "m²", "log": log_awp},
        "BMt": {"formula": r"BM_t = \frac{I_t}{\nabla}", "data": f"It = {it:.3f} m⁴, ∇ = {vol:.3f} m³", "intermediate": f"{it:.3f} / {vol:.3f}", "result": f"{bmt:.3f}", "unit": "m", "log": log_it},
        "KMt": {"formula": r"KM_t = KB + BM_t", "data": f"KB = {kb:.3f} m, BMt = {bmt:.3f} m", "intermediate": f"{kb:.3f} + {bmt:.3f}", "result": f"{kmt:.3f}", "unit": "m"},
        "TPC": {"formula": r"TPC = \frac{\rho \cdot A^{WP}}{100}", "data": f"ρ = {rho:.3f} t/m³, AWP = {awp:.3f} m²", "intermediate": f"({rho:.3f} * {awp:.3f}) / 100", "result": f"{tpc:.3f}", "unit": "t/cm"},
        "CB": {"formula": r"C_B = \frac{\nabla}{L \cdot B \cdot T}", "data": f"∇ = {vol:.3f} m³, L = {L:.2f} m, B = {B:.2f} m, T = {T:.3f} m", "intermediate": f"{vol:.3f} / ({L:.2f} * {B:.2f} * {T:.3f})", "result": f"{cb:.4f}", "unit": "adimensional"}
    }
    
    return data, audit, sec_areas

# ==============================================================================
# 4. INTERFACE GRÁFICA STREAMLIT
# ==============================================================================
st.title("🚢 Aplicativo de Cálculo Hidrostático")
st.caption("Projeto Integrador de Arquitetura Naval (AP1.1) | UEA / EST")

# Barra Lateral
with st.sidebar:
    st.header("⚙️ Configurações")
    preset = st.radio("Carregar Exemplo:", ["Barcaça Analítica", "Upload de Arquivo"])
    
    if preset == "Barcaça Analítica":
        df_offsets = generate_barge_data(20.0, 4.0, 2.0, 11, 6)
        ship_name = "Barcaça Analítica"
        LBP, B, D, Td = 20.0, 4.0, 2.0, 1.0
    else:
        uploaded_file = st.file_uploader("Envie a Tabela de Cotas (.xlsx ou .csv)", type=["xlsx", "csv"])
        if uploaded_file is not None:
            if uploaded_file.name.endswith(".csv"):
                df_offsets = pd.read_csv(uploaded_file, index_col=0)
            else:
                df_offsets = pd.read_excel(uploaded_file, index_col=0)
            df_offsets = df_offsets.astype(float).fillna(0.0)
            ship_name = uploaded_file.name.split('.')[0]
        else:
            df_offsets = generate_barge_data(20.0, 4.0, 2.0, 11, 6)
            ship_name = "Barcaça Padrão"
        
        LBP = st.number_input("LBP (m)", value=float(df_offsets.columns[-1]) - float(df_offsets.columns[0]))
        B = st.number_input("Boca B (m)", value=float(2.0 * df_offsets.values.max()))
        D = st.number_input("Pontal D (m)", value=float(df_offsets.index[-1]))
        Td = st.number_input("Calado de Projeto (m)", value=float(D * 0.7))

    rho = st.number_input("Densidade da Água (t/m³)", value=1.025, step=0.001, format="%.3f")
    t_min = st.number_input("T min (m)", value=0.2, step=0.1)
    t_max = st.number_input("T max (m)", value=float(D * 0.9), step=0.1)
    dt = st.number_input("ΔT (m)", value=0.2, step=0.1)

# Construção da Geometria
hull = Hull(df_offsets.columns, df_offsets.index, df_offsets.values, LBP, B, D, Td)

# Abas Principais
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📋 Tabela de Cotas", "📐 Geometria 2D/3D", "🧮 Cálculo & Auditoria", 
    "📊 Hydrostatic Table", "📈 Curvas Hidrostáticas", "🧪 Validação Analítica"
])

with tab1:
    st.subheader(f"Tabela de Cotas: {ship_name}")
    st.dataframe(df_offsets.style.format("{:.3f}"), use_container_width=True)

with tab2:
    st.subheader("Visualização do Casco")
    c1, c2 = st.columns(2)
    with c1:
        fig_bp = go.Figure()
        for j, x in enumerate(hull.stations_x):
            z_pts = np.linspace(hull.waterlines_z[0], hull.D, 25)
            y_pts = [hull.get_y(j, z) for z in z_pts]
            fig_bp.add_trace(go.Scatter(x=y_pts, y=z_pts, mode='lines', name=f"x={x:.1f}m"))
            fig_bp.add_trace(go.Scatter(x=[-v for v in y_pts], y=z_pts, mode='lines', showlegend=False, line=dict(dash='dot')))
        fig_bp.update_layout(title="Plano de Balizas (Body Plan)", xaxis_title="Semi-boca (m)", yaxis_title="Cota Z (m)")
        st.plotly_chart(fig_bp, use_container_width=True)
    with c2:
        # Gráfico 3D
        x_mesh, y_mesh, z_mesh = [], [], []
        for z_val in hull.waterlines_z:
            xs_d = np.linspace(hull.stations_x[0], hull.stations_x[-1], 20)
            ys_d = [hull.get_y(np.searchsorted(hull.stations_x, x_val, side='right')-1, z_val) for x_val in xs_d]
            x_mesh.append(xs_d); y_mesh.append(ys_d); z_mesh.append(np.full_like(xs_d, z_val))
        fig_3d = go.Figure()
        fig_3d.add_trace(go.Surface(x=x_mesh, y=y_mesh, z=z_mesh, colorscale='Viridis', opacity=0.8))
        fig_3d.add_trace(go.Surface(x=x_mesh, y=[[-v for v in row] for row in y_mesh], z=z_mesh, colorscale='Viridis', opacity=0.8))
        fig_3d.update_layout(title="Casco 3D", scene=dict(aspectmode='data'), height=450)
        st.plotly_chart(fig_3d, use_container_width=True)

with tab3:
    st.subheader("Cálculo Pontual e Auditoria ('Mostrar Cálculo')")
    sel_t = st.slider("Escolha o Calado T (m):", min_value=0.1, max_value=float(hull.D), value=float(hull.Td), step=0.05)
    data_t, audit_t, sec_areas = calculate_hydrostatics_at_draft(hull, sel_t, rho)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Volume (∇)", f"{data_t['Volume (∇)']:.3f} m³")
    col2.metric("Deslocamento (Δ)", f"{data_t['Deslocamento (Δ)']:.3f} t")
    col3.metric("KB", f"{data_t['KB']:.3f} m")
    col4.metric("LCB", f"{data_t['LCB']:.3f} m")
    
    col5, col6, col7, col8 = st.columns(4)
    col5.metric("AWP", f"{data_t['AWP']:.3f} m²")
    col6.metric("BMt", f"{data_t['BMt']:.3f} m")
    col7.metric("KMt", f"{data_t['KMt']:.3f} m")
    col8.metric("TPC", f"{data_t['TPC']:.3f} t/cm")

    st.divider()
    st.markdown("### 🔍 Auditoria Passo a Passo (Item 22 do Edital)")
    sel_prop = st.selectbox("Selecione a Propriedade para Auditar:", list(audit_t.keys()))
    info = audit_t[sel_prop]
    
    st.latex(info["formula"])
    st.markdown(f"**Dados de Entrada:** {info['data']}")
    st.markdown(f"**Valores Intermediários:** {info['intermediate']}")
    st.markdown(f"**Resultado Final:** `{info['result']} {info['unit']}`")
    
    if "log" in info:
        st.markdown("**Trechos e Métodos Aplicados:**")
        st.dataframe(pd.DataFrame(info["log"]), use_container_width=True)

with tab4:
    st.subheader("Hydrostatic Table Completa")
    drafts = np.arange(t_min, t_max + dt/2.0, dt)
    table_rows = [calculate_hydrostatics_at_draft(hull, t, rho)[0] for t in drafts]
    df_table = pd.DataFrame(table_rows)
    st.dataframe(df_table.style.format("{:.3f}"), use_container_width=True)
    
    # Download Excel
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
        df_table.to_excel(writer, sheet_name="Hydrostatic_Table", index=False)
    st.download_button("📥 Baixar Planilha em Excel (.xlsx)", data=buf.getvalue(), file_name="Hydrostatic_Table.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

with tab5:
    st.subheader("Hydrostatic Curves")
    fig_hc = go.Figure()
    for col in ["Volume (∇)", "Deslocamento (Δ)", "AWP", "KB", "LCB", "KMt", "TPC"]:
        fig_hc.add_trace(go.Scatter(x=df_table[col], y=df_table["T"], mode='lines+markers', name=col))
    fig_hc.update_layout(xaxis_title="Valor da Propriedade", yaxis_title="Calado T (m)", height=550)
    st.plotly_chart(fig_hc, use_container_width=True)

with tab6:
    st.subheader("Validação 1 - Barcaça Paralelepipédica (Solução Analítica)")
    exact_v = LBP * B * 1.0
    exact_kb = 1.0 / 2.0
    exact_bmt = (B**2) / (12.0 * 1.0)
    
    val_t, _, _ = calculate_hydrostatics_at_draft(hull, 1.0, rho)
    
    comp_df = pd.DataFrame([
        {"Propriedade": "Volume ∇ (m³)", "Fórmula": "L*B*T", "Analítico": exact_v, "App": val_t["Volume (∇)"], "Erro (%)": abs(val_t["Volume (∇)"] - exact_v)/exact_v*100},
        {"Propriedade": "KB (m)", "Fórmula": "T/2", "Analítico": exact_kb, "App": val_t["KB"], "Erro (%)": abs(val_t["KB"] - exact_kb)/exact_kb*100},
        {"Propriedade": "BMt (m)", "Fórmula": "B²/(12T)", "Analítico": exact_bmt, "App": val_t["BMt"], "Erro (%)": abs(val_t["BMt"] - exact_bmt)/exact_bmt*100}
    ])
    st.dataframe(comp_df.style.format({"Analítico": "{:.4f}", "App": "{:.4f}", "Erro (%)": "{:.4f}%"}), use_container_width=True)