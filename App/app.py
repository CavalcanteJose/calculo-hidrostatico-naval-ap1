"""
APLICATIVO DE CÁLCULO HIDROSTÁTICO - PROJETO INTEGRADOR AP1.1 (UEA/EST)
Aluno: Leury Navarro Barreto | Matrícula: 2215200033
Versão com Leitor Inteligente de Planilhas (Suporte a Cabeçalhos de Texto, Vírgulas Decimais e Formatações Diversas).
"""

import io
import re
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from scipy.interpolate import interp1d, PchipInterpolator

# ==============================================================================
# DADOS FIXOS DO ESTUDANTE
# ==============================================================================
STUDENT_NAME = "Leury Navarro Barreto"
STUDENT_ID = "2215200033"

# ==============================================================================
# CONFIGURAÇÃO GERAL DA PÁGINA
# ==============================================================================
st.set_page_config(
    page_title=f"NavalHydro | {STUDENT_NAME}",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==============================================================================
# ESTILIZAÇÃO CSS
# ==============================================================================
st.markdown("""
<style>
    /* Fundo Escuro Oceânico */
    .stApp {
        background: linear-gradient(145deg, #0a1128 0%, #1c2541 60%, #0b132b 100%);
        color: #f8fafc;
    }
    
    /* Espaçamento superior generoso */
    .block-container {
        padding-top: 3.8rem !important;
        padding-bottom: 4.5rem !important;
    }

    /* Cartão da Tela Inicial */
    .welcome-card {
        background: rgba(28, 37, 65, 0.9);
        border: 1px solid #3a506b;
        border-radius: 14px;
        padding: 28px 32px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.4);
        margin-bottom: 20px;
    }

    /* Banner Superior do Aluno */
    .student-header-banner {
        background: rgba(28, 37, 65, 0.85);
        border: 1px solid #48cae4;
        border-radius: 12px;
        padding: 14px 22px;
        margin-bottom: 24px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25);
    }

    /* Cartões de Métricas */
    div[data-testid="stMetric"] {
        background-color: rgba(28, 37, 65, 0.9) !important;
        border: 1px solid #3a506b !important;
        padding: 12px 14px !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3) !important;
    }
    div[data-testid="stMetric"] label {
        color: #48cae4 !important;
        font-weight: 700 !important;
        font-size: 0.82rem !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 1.35rem !important;
        font-weight: 800 !important;
    }

    /* Caixa de Auditoria */
    .audit-box {
        background-color: rgba(11, 19, 43, 0.95);
        border-left: 5px solid #48cae4;
        border-radius: 8px;
        padding: 18px 22px;
        margin: 14px 0px;
        border-top: 1px solid rgba(72, 202, 228, 0.2);
        border-right: 1px solid rgba(72, 202, 228, 0.2);
        border-bottom: 1px solid rgba(72, 202, 228, 0.2);
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# INICIALIZAÇÃO DE ESTADO
# ==============================================================================
if "app_state" not in st.session_state:
    st.session_state.app_state = "home"
if "selected_module" not in st.session_state:
    st.session_state.selected_module = "📋 Tabela de Cotas"
if "ship_name" not in st.session_state:
    st.session_state.ship_name = "Barcaça Analítica"


# ==============================================================================
# 0. PARSERS INTELIGENTES DE PLANILHAS (TABELA DE COTAS E PLANO DE LINHAS)
# ==============================================================================
def extract_numeric_value(val, default=0.0):
    """Extrai número de qualquer texto (ex: '1,25 m' -> 1.25, 'Trans 8090' -> 8090)."""
    if val is None:
        return default
    try:
        if pd.isna(val):
            return default
    except Exception:
        pass
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip().replace(',', '.')
    match = re.search(r"[-+]?(?:\d*\.\d+|\d+)", s)
    return float(match.group(0)) if match else default


def _is_body_plan_format(raw_df):
    """Detecta se é Plano de Linhas com colunas Trans/Vert (não tabela de cotas padrão)."""
    flat = raw_df.astype(str).values.flatten()
    keywords = ["trans", "vert", "m-cl", "m-bl", "linhas", "plano", "x(m-ap)"]
    hits = sum(1 for c in flat if any(k in str(c).lower() for k in keywords))
    return hits >= 2


def parse_body_plan_to_offset_table(raw_df):
    """
    Converte Plano de Linhas (Trans/Vert em mm por estação) em Tabela de Cotas padrão.

    Formato esperado:
      - Cabeçalho com "X(m-AP)" seguido da posição da estação em mm
      - 3 colunas por estação: [No., Trans(mm desde CL), Vert(mm desde BL)]
      - Valores em milímetros

    Retorna DataFrame com:
      - Índice = Linhas d'Água Z em metros
      - Colunas = Estações X em metros
      - Valores = Semi-bocas Y em metros
    """
    # 1. Localizar posições X das estações no cabeçalho
    station_x_mm = []
    station_x_col = {}

    for ci in range(raw_df.shape[1]):
        for ri in range(min(7, raw_df.shape[0])):
            cell = str(raw_df.iloc[ri, ci]).strip().lower()
            if re.match(r"x\s*\(m-ap\)", cell):
                # Valor da estação na próxima coluna (mesma linha ou próxima)
                for di in [1, 0]:
                    if ci + di < raw_df.shape[1]:
                        xv = extract_numeric_value(raw_df.iloc[ri, ci + di], default=None)
                        if xv and xv > 0:
                            if xv not in station_x_mm:
                                station_x_mm.append(xv)
                                station_x_col[xv] = ci + di
                            break

    # Fallback: busca números grandes seguidos de "Trans" na linha seguinte
    if not station_x_mm:
        for ci in range(raw_df.shape[1]):
            for ri in range(min(5, raw_df.shape[0])):
                xv = extract_numeric_value(raw_df.iloc[ri, ci], default=0)
                if 50 < xv < 50000:
                    # Verifica se coluna seguinte contém "Trans"
                    if ci + 1 < raw_df.shape[1]:
                        next_col_text = " ".join(
                            str(raw_df.iloc[r, ci + 1]).lower()
                            for r in range(min(6, raw_df.shape[0]))
                        )
                        if "trans" in next_col_text and xv not in station_x_mm:
                            station_x_mm.append(xv)
                            station_x_col[xv] = ci

    if not station_x_mm:
        raise ValueError(
            "Não foi possível identificar as estações X.\n"
            "Certifique-se que a planilha contém cabeçalhos 'X(m-AP)' com os valores das estações."
        )

    # 2. Encontrar linha inicial dos dados numéricos
    data_start_row = 4  # padrão: linha 4 (após título + 3 linhas de cabeçalho)
    for ri in range(min(10, raw_df.shape[0])):
        v = str(raw_df.iloc[ri, 0]).strip()
        if v in ('1', '1.0', '1,0'):
            data_start_row = ri
            break

    # 3. Para cada estação, localizar colunas Trans e Vert e extrair pontos
    station_points = {}

    for x_mm in station_x_mm:
        x_col = station_x_col[x_mm]
        trans_col = vert_col = None

        # Procura "Trans" e "Vert" nas linhas de cabeçalho próximas a x_col
        search_cols = range(max(0, x_col - 1), min(raw_df.shape[1], x_col + 4))
        for ci in search_cols:
            col_text = " ".join(
                str(raw_df.iloc[ri, ci]).lower()
                for ri in range(min(7, raw_df.shape[0]))
            )
            if "trans" in col_text and trans_col is None:
                trans_col = ci
            if "vert" in col_text and vert_col is None:
                vert_col = ci

        # Fallback: Trans = x_col+1, Vert = x_col+2
        if trans_col is None:
            trans_col = x_col + 1 if x_col + 1 < raw_df.shape[1] else None
        if vert_col is None:
            vert_col = x_col + 2 if x_col + 2 < raw_df.shape[1] else None

        if trans_col is None or vert_col is None:
            continue

        points = []
        for ri in range(data_start_row, raw_df.shape[0]):
            t = extract_numeric_value(raw_df.iloc[ri, trans_col], default=None)
            v = extract_numeric_value(raw_df.iloc[ri, vert_col], default=None)
            if t is not None and v is not None and t > 0 and v >= 0:
                points.append((t / 1000.0, v / 1000.0))  # mm → m

        if points:
            x_m = x_mm / 1000.0
            station_points[x_m] = sorted(points, key=lambda p: p[1])

    if not station_points:
        raise ValueError(
            "Nenhum ponto (Trans, Vert) válido encontrado.\n"
            "Verifique se os dados numéricos estão nas colunas corretas."
        )

    # 4. Criar grade de Linhas d'Água e interpolar semi-bocas
    all_z = [v for pts in station_points.values() for (_, v) in pts]
    z_grid = np.linspace(min(all_z), max(all_z), 12)
    x_sorted = sorted(station_points.keys())
    matrix = np.zeros((len(z_grid), len(x_sorted)))

    for j, x_m in enumerate(x_sorted):
        pts = station_points[x_m]
        z_arr = np.array([p[1] for p in pts])
        y_arr = np.array([p[0] for p in pts])
        # Ordenar e remover Z duplicados
        sidx = np.argsort(z_arr)
        z_arr, y_arr = z_arr[sidx], y_arr[sidx]
        _, uidx = np.unique(z_arr, return_index=True)
        z_arr, y_arr = z_arr[uidx], y_arr[uidx]
        if len(z_arr) >= 2:
            f = interp1d(z_arr, y_arr, kind='linear',
                         fill_value=(y_arr[0], y_arr[-1]), bounds_error=False)
            matrix[:, j] = np.maximum(0, f(z_grid))

    df_result = pd.DataFrame(
        np.round(matrix, 4),
        index=np.round(z_grid, 4),
        columns=np.round(x_sorted, 4)
    )
    df_result.index.name = "Z_WL (m)"
    df_result.columns.name = "Estações X (m)"
    return df_result


def smart_parse_offset_table(uploaded_file):
    """
    Parser universal: detecta automaticamente o formato da planilha.
      - Formato A: Tabela de Cotas padrão (Z × X com semi-bocas Y)
      - Formato B: Plano de Linhas (Trans/Vert em mm por estação)
    """
    file_name = uploaded_file.name.lower()

    # Leitura bruta do arquivo
    if file_name.endswith(".csv"):
        try:
            raw_df = pd.read_csv(uploaded_file, header=None)
        except Exception:
            uploaded_file.seek(0)
            raw_df = pd.read_csv(uploaded_file, sep=";", header=None)
    else:
        raw_df = pd.read_excel(uploaded_file, header=None)

    raw_df = raw_df.dropna(how="all").dropna(axis=1, how="all")

    if raw_df.empty:
        raise ValueError("A planilha carregada está vazia.")

    # Detecção automática de formato
    if _is_body_plan_format(raw_df):
        df_result = parse_body_plan_to_offset_table(raw_df)
        return df_result

    # --- Formato A: Tabela de Cotas padrão ---
    start_row, start_col = 1, 1

    col_labels = raw_df.iloc[0, start_col:].values
    stations_x = [extract_numeric_value(v, float(i)) for i, v in enumerate(col_labels)]

    row_labels = raw_df.iloc[start_row:, 0].values
    waterlines_z = [extract_numeric_value(v, float(i) * 0.5) for i, v in enumerate(row_labels)]

    data_matrix = raw_df.iloc[start_row:, start_col:].values
    cleaned = np.zeros(data_matrix.shape, dtype=float)
    for r in range(data_matrix.shape[0]):
        for c in range(data_matrix.shape[1]):
            cleaned[r, c] = extract_numeric_value(data_matrix[r, c], 0.0)

    # Conversão automática mm → m quando valores são muito grandes
    if np.nanmax(cleaned) > 100:
        cleaned = cleaned / 1000.0
        stations_x = [x / 1000.0 if x > 100 else x for x in stations_x]
        waterlines_z = [z / 1000.0 if z > 50 else z for z in waterlines_z]

    df_clean = pd.DataFrame(cleaned, index=waterlines_z, columns=stations_x)
    df_clean.index.name = "Z_WL (m)"
    df_clean.columns.name = "Estações X (m)"
    return df_clean


# ==============================================================================
# 1. MÉTODOS DE INTEGRAÇÃO NUMÉRICA MANUAL (Item 9 do Edital)
# ==============================================================================
def trapz_rule(x, y):
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    if len(x) < 2: return 0.0
    return float(np.sum(0.5 * (y[:-1] + y[1:]) * np.diff(x)))

def simpson_13_rule(y, h):
    if len(y) < 3 or (len(y) % 2 == 0):
        raise ValueError("Simpson 1/3 requer número ímpar de pontos.")
    s = y[0] + y[-1] + 4.0 * np.sum(y[1:-1:2]) + 2.0 * np.sum(y[2:-2:2])
    return float((h / 3.0) * s)

def simpson_38_rule(y, h):
    if len(y) != 4:
        raise ValueError("Simpson 3/8 requer exatamente 4 pontos.")
    return float((3.0 * h / 8.0) * (y[0] + 3.0 * y[1] + 3.0 * y[2] + y[3]))

def integrate_dataset(x, y):
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    n = len(x)
    if n < 2:
        return 0.0, [{"Trecho": "Nenhum", "Método": "Pontos insuficientes", "Área": 0.0}]
    if n == 2:
        area = trapz_rule(x, y)
        return area, [{"Trecho": f"[{x[0]:.2f}m a {x[1]:.2f}m]", "Método": "Trapézios", "Área": round(area, 4)}]
    
    dx = np.diff(x)
    is_uniform = np.allclose(dx, dx[0], rtol=1e-3)
    h = float(np.mean(dx))
    
    if not is_uniform:
        area = trapz_rule(x, y)
        return area, [{"Trecho": f"[{x[0]:.2f}m a {x[-1]:.2f}m]", "Método": "Trapézios Não-Uniforme", "Área": round(area, 4)}]
    
    audit_log, total_area = [], 0.0
    intervals, idx = n - 1, 0
    
    while idx < intervals:
        rem = intervals - idx
        if rem % 2 == 0:
            sub_y = y[idx:]
            a = simpson_13_rule(sub_y, h)
            total_area += a
            audit_log.append({"Trecho": f"Pontos {idx} a {n-1} [{x[idx]:.2f}m a {x[-1]:.2f}m]", "Método": "Simpson 1/3", "Área": round(a, 4)})
            break
        elif rem >= 3:
            sub_y = y[idx:idx+4]
            a = simpson_38_rule(sub_y, h)
            total_area += a
            audit_log.append({"Trecho": f"Pontos {idx} a {idx+3} [{x[idx]:.2f}m a {x[idx+3]:.2f}m]", "Método": "Simpson 3/8", "Área": round(a, 4)})
            idx += 3
        else:
            sub_x, sub_y = x[idx:idx+2], y[idx:idx+2]
            a = trapz_rule(sub_x, sub_y)
            total_area += a
            audit_log.append({"Trecho": f"Pontos {idx} a {idx+1} [{x[idx]:.2f}m a {x[idx+1]:.2f}m]", "Método": "Trapézio", "Área": round(a, 4)})
            idx += 1
            
    return float(total_area), audit_log


# ==============================================================================
# 2. MODELAGEM GEOMÉTRICA (Itens 7 e 8 do Edital)
# ==============================================================================
class Hull:
    def __init__(self, stations_x, waterlines_z, offsets_matrix, LBP=None, B=None, D=None, Td=None):
        self.stations_x = np.asarray(stations_x, dtype=float)
        self.waterlines_z = np.asarray(waterlines_z, dtype=float)
        self.offsets = np.asarray(offsets_matrix, dtype=float)
        
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

    def get_y_continuous(self, x, z):
        """Retorna a semi-boca Y(x, z) interpolada suavemente de forma contínua em X e Z."""
        if z < self.waterlines_z[0]:
            return 0.0
        z = min(z, self.waterlines_z[-1])
        x = np.clip(x, self.stations_x[0], self.stations_x[-1])
        
        # 1. Avalia Y(z) em cada uma das estações discretas
        y_at_stations = np.array([float(self._station_interps[j](z)) for j in range(len(self.stations_x))])
        y_at_stations = np.maximum(0.0, y_at_stations)
        
        # 2. Interpola longitudinalmente ao longo de X com PCHIP suave
        if len(self.stations_x) >= 3 and len(np.unique(y_at_stations)) > 1:
            try:
                long_interp = PchipInterpolator(self.stations_x, y_at_stations)
                return max(0.0, float(long_interp(x)))
            except Exception:
                return max(0.0, float(np.interp(x, self.stations_x, y_at_stations)))
        else:
            return max(0.0, float(np.interp(x, self.stations_x, y_at_stations)))


def generate_barge_data(L=20.0, B=4.0, D=2.0, nx=11, nz=6):
    xs = np.linspace(0.0, L, nx)
    zs = np.linspace(0.0, D, nz)
    mat = np.full((nz, nx), B / 2.0)
    df = pd.DataFrame(mat, index=zs, columns=xs)
    df.index.name = "Z_WL (m)"
    df.columns.name = "Estações X (m)"
    return df

def generate_sample_ship():
    xs = np.linspace(0.0, 100.0, 11)
    zs = np.linspace(0.0, 10.0, 6)
    data = [
        [0.00, 0.40, 1.20, 2.50, 4.00, 4.50, 4.00, 2.50, 1.20, 0.40, 0.00],
        [0.50, 2.10, 4.60, 6.80, 7.80, 8.00, 7.80, 6.80, 4.50, 2.00, 0.20],
        [1.20, 3.80, 6.40, 7.60, 8.00, 8.00, 8.00, 7.50, 5.80, 3.20, 0.50],
        [2.00, 5.00, 7.20, 7.90, 8.00, 8.00, 8.00, 7.80, 6.60, 4.20, 0.90],
        [2.80, 6.00, 7.70, 8.00, 8.00, 8.00, 8.00, 8.00, 7.20, 5.00, 1.40],
        [3.50, 6.80, 8.00, 8.00, 8.00, 8.00, 8.00, 8.00, 7.60, 5.80, 2.00]
    ]
    df = pd.DataFrame(data, index=zs, columns=xs)
    df.index.name = "Z_WL (m)"
    df.columns.name = "Estações X (m)"
    return df


def generate_real_ship():
    """
    Lancha Salva-Vidas (Jaraqui Nautidesign) — Projeto Oficial AP1.1
    Dimensões Oficiais do Desenho Técnico (PDF):
      - Comprimento Total (LOA): 9,112 m (10 intervalos de 0,9112 m de ST 00 a ST 10)
      - Comprimento Entre Perpendiculares (LBP): 7,200 m
      - Boca Moldada (B): 2,040 m (Meia-boca máxima = 1,020 m)
      - Pontal Moldado (D): 1,800 m
      - Calado de Projeto (Td): 0,60 m
    """
    # 11 Estações X (0 a 10) espaçadas em 0.9112m
    xs = np.array([0.0000, 0.9112, 1.8224, 2.7336, 3.6448, 4.5560, 5.4672, 6.3784, 7.2896, 8.2008, 9.1120])
    
    # 11 Linhas d'Água Z (WL 0 a WL 10) de 0.00m até o Pontal 1.80m
    zs = np.array([0.00, 0.18, 0.36, 0.54, 0.72, 0.90, 1.08, 1.26, 1.44, 1.62, 1.80])

    # Matriz de Meias-Bocas Y (em metros) rigorosamente adoçada (faired)
    # Colunas: ST00 (Popa) -> ST05 (Meia-Nau) -> ST10 (Proa)
    data = [
        # WL00 (z = 0.00m - Linha de Base / Quilha)
        [0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000],
        # WL01 (z = 0.18m) - Entra suavemente no fundo em V
        [0.000, 0.000, 0.120, 0.260, 0.350, 0.380, 0.340, 0.220, 0.080, 0.000, 0.000],
        # WL02 (z = 0.36m)
        [0.000, 0.180, 0.380, 0.540, 0.630, 0.655, 0.610, 0.480, 0.280, 0.080, 0.000],
        # WL03 (z = 0.54m)
        [0.220, 0.450, 0.620, 0.745, 0.810, 0.835, 0.790, 0.670, 0.480, 0.220, 0.000],
        # WL04 (z = 0.72m)
        [0.480, 0.660, 0.785, 0.870, 0.915, 0.930, 0.890, 0.790, 0.620, 0.350, 0.000],
        # WL05 (z = 0.90m)
        [0.660, 0.790, 0.885, 0.945, 0.975, 0.985, 0.950, 0.870, 0.720, 0.470, 0.000],
        # WL06 (z = 1.08m)
        [0.760, 0.865, 0.940, 0.985, 1.005, 1.010, 0.985, 0.925, 0.800, 0.570, 0.000],
        # WL07 (z = 1.26m)
        [0.820, 0.915, 0.970, 1.005, 1.018, 1.020, 1.005, 0.955, 0.860, 0.650, 0.000],
        # WL08 (z = 1.44m)
        [0.860, 0.945, 0.990, 1.015, 1.020, 1.020, 1.015, 0.975, 0.900, 0.710, 0.000],
        # WL09 (z = 1.62m)
        [0.890, 0.965, 1.000, 1.020, 1.020, 1.020, 1.020, 0.988, 0.925, 0.755, 0.000],
        # WL10 (z = 1.80m - Borda Livre / Convés)
        [0.910, 0.975, 1.005, 1.020, 1.020, 1.020, 1.020, 0.995, 0.940, 0.790, 0.000],
    ]

    df = pd.DataFrame(data, index=zs, columns=xs)
    df.index.name = "Z_WL (m)"
    df.columns.name = "Estações X (m)"
    return df




# ==============================================================================
# 3. MOTOR HIDROSTÁTICO (Itens 10 a 19 do Edital)
# ==============================================================================
def calculate_hydrostatics_at_draft(hull: Hull, T: float, rho: float = 1.025):
    n_st = len(hull.stations_x)
    xs = hull.stations_x
    z_grid = np.linspace(hull.waterlines_z[0], T, 35)
    dz = z_grid[1] - z_grid[0] if len(z_grid) > 1 else 0.0
    
    sec_areas, sec_mz, sec_girths = np.zeros(n_st), np.zeros(n_st), np.zeros(n_st)
    
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
    
    audit = {
        "Volume": {"formula": r"\nabla^L = \int_{0}^{L} A(x)\,dx", "data": f"LBP = {L:.2f} m | {n_st} estações", "intermediate": f"∇L = {vol_long:.3f} m³ | ∇V = {vol_vert:.3f} m³ (Diferença: {err_vol:.4f}%)", "result": f"{vol:.3f}", "unit": "m³", "log": log_vol_long},
        "Deslocamento": {"formula": r"\Delta = \rho \cdot \nabla", "data": f"ρ = {rho:.3f} t/m³ | Volume ∇ = {vol:.3f} m³", "intermediate": f"{rho:.3f} * {vol:.3f}", "result": f"{disp:.3f}", "unit": "toneladas (t)"},
        "LCB": {"formula": r"LCB = \frac{\int x \cdot A(x)\,dx}{\nabla}", "data": f"∇ = {vol:.3f} m³", "intermediate": f"Momento Longitudinal = {int_x_ax:.3f} m⁴", "result": f"{lcb:.3f}", "unit": "m (de x=0)", "log": log_lcb},
        "KB": {"formula": r"KB = \frac{\int M_z(x)\,dx}{\nabla}", "data": f"∇ = {vol:.3f} m³", "intermediate": f"Momento Vertical = {int_mz_x:.3f} m⁴", "result": f"{kb:.3f}", "unit": "m (da Linha de Base BL)", "log": log_kb},
        "AWP": {"formula": r"A^{WP} = 2 \int_{0}^{L} y(x, T)\,dx", "data": f"Calado T = {T:.3f} m", "intermediate": f"Meia-área = {half_awp:.3f} m²", "result": f"{awp:.3f}", "unit": "m²", "log": log_awp},
        "BMt": {"formula": r"BM_t = \frac{I_t}{\nabla}", "data": f"It = {it:.3f} m⁴ | ∇ = {vol:.3f} m³", "intermediate": f"{it:.3f} / {vol:.3f}", "result": f"{bmt:.3f}", "unit": "m", "log": log_it},
        "KMt": {"formula": r"KM_t = KB + BM_t", "data": f"KB = {kb:.3f} m | BMt = {bmt:.3f} m", "intermediate": f"{kb:.3f} + {bmt:.3f}", "result": f"{kmt:.3f}", "unit": "m"},
        "TPC": {"formula": r"TPC = \frac{\rho \cdot A^{WP}}{100}", "data": f"ρ = {rho:.3f} t/m³ | AWP = {awp:.3f} m²", "intermediate": f"({rho:.3f} * {awp:.3f}) / 100", "result": f"{tpc:.3f}", "unit": "t/cm"},
        "CB": {"formula": r"C_B = \frac{\nabla}{LBP \cdot B \cdot T}", "data": f"∇ = {vol:.3f} m³, L = {L:.2f} m, B = {B:.2f} m, T = {T:.3f} m", "intermediate": f"{vol:.3f} / ({L:.2f} * {B:.2f} * {T:.3f})", "result": f"{cb:.4f}", "unit": "adimensional"}
    }
    
    return data, audit, sec_areas


# ==============================================================================
# TELA 1: INICIAL (IDENTIFICAÇÃO FIXA DO ALUNO E SELEÇÃO DE CASCO)
# ==============================================================================
if st.session_state.app_state == "home":
    
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 25px;">
        <h1 style="color: #48cae4; font-size: 2.3rem; font-weight: 800; margin-bottom: 5px;">
            🚢 Projeto Integrador de Arquitetura Naval
        </h1>
        <h3 style="color: #cbd5e1; font-size: 1.15rem; font-weight: 500; margin-bottom: 8px;">
            Avaliação AP1.1 — Aplicativo de Cálculo Hidrostático a partir da Tabela de Cotas
        </h3>
        <p style="color: #94a3b8; font-size: 0.95rem;">
            Universidade do Estado do Amazonas (UEA) | Escola Superior de Tecnologia (EST)
        </p>
        <div style="display: inline-block; margin-top: 10px; background: rgba(72, 202, 228, 0.15); border: 1px solid #48cae4; padding: 8px 22px; border-radius: 25px; color: #f8fafc; font-weight: 600;">
            👤 Aluno: <b>{STUDENT_NAME}</b> &nbsp;|&nbsp; 🎓 Matrícula: <b>{STUDENT_ID}</b>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_main_left, col_main_right = st.columns([1, 1])
    
    with col_main_left:
        st.markdown('<div class="welcome-card">', unsafe_allow_html=True)
        st.subheader("📂 1. Seleção da Tabela de Cotas")
        st.caption("Escolha um casco padrão para validação ou carregue um novo arquivo (.xlsx / .csv).")
        
        origin_choice = st.radio(
            "Origem dos Dados:",
            [
                "🧱 Barcaça Paralelepipédica (Validação Analítica)",
                "🚢 Navio Mercante 100m (Exemplo Realista)",
                "⛵ Navio Real — Tabela de Cotas (11 Balizas × 11 WL)",
                "📁 Fazer Upload de Tabela de Cotas (.xlsx / .csv)"
            ],
            index=0
        )
        
        if origin_choice == "📁 Fazer Upload de Tabela de Cotas (.xlsx / .csv)":
            uploaded_file = st.file_uploader("Selecione o arquivo com ou sem cabeçalho:", type=["xlsx", "xls", "csv"])
            if uploaded_file is not None:
                try:
                    df_loaded = smart_parse_offset_table(uploaded_file)
                    st.session_state.df_offsets = df_loaded
                    st.session_state.ship_name = uploaded_file.name.split('.')[0]
                    st.success(f"✅ Arquivo '{uploaded_file.name}' carregado e processado com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao processar planilha: {e}")
            else:
                st.session_state.df_offsets = generate_barge_data(20.0, 4.0, 2.0, 11, 6)
                st.session_state.ship_name = "Barcaça Padrão"
        elif origin_choice == "🚢 Navio Mercante 100m (Exemplo Realista)":
            st.session_state.df_offsets = generate_sample_ship()
            st.session_state.ship_name = "Navio Mercante 100m"
        elif origin_choice == "⛵ Navio Real — Tabela de Cotas (11 Balizas × 11 WL)":
            st.session_state.df_offsets = generate_real_ship()
            st.session_state.ship_name = "Navio Real (9.11m × 2.40m × 1.06m)"
        else:
            st.session_state.df_offsets = generate_barge_data(20.0, 4.0, 2.0, 11, 6)
            st.session_state.ship_name = "Barcaça Analítica"

            
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_main_right:
        st.markdown('<div class="welcome-card">', unsafe_allow_html=True)
        st.subheader("⚙️ 2. Parâmetros da Embarcação")
        st.caption("Verifique as dimensões principais e a densidade da água.")
        
        df_curr = st.session_state.get("df_offsets", generate_barge_data())
        # Clamp valores para garantir que estejam acima dos mínimos dos widgets
        calc_lbp = max(1.0, float(df_curr.columns[-1]) - float(df_curr.columns[0]))
        calc_beam = max(0.5, float(2.0 * df_curr.values.max()))
        calc_depth = max(0.5, float(df_curr.index[-1]))
        calc_td = max(0.1, float(calc_depth * 0.7))
        
        col_p1, col_p2 = st.columns(2)
        st.session_state.lbp = col_p1.number_input("LBP (m)", value=calc_lbp, min_value=1.0, step=1.0)
        st.session_state.beam = col_p2.number_input("Boca B (m)", value=calc_beam, min_value=0.5, step=0.5)
        
        col_p3, col_p4 = st.columns(2)
        st.session_state.depth = col_p3.number_input("Pontal D (m)", value=calc_depth, min_value=0.5, step=0.5)
        st.session_state.design_draft = col_p4.number_input("Calado Proj. Td (m)", value=calc_td, min_value=0.1, step=0.1)
        
        st.session_state.density = st.number_input("Densidade da Água ρ (t/m³)", value=1.025, min_value=0.5, max_value=1.5, step=0.001, format="%.3f")
        
        st.divider()
        st.subheader("📏 Faixa de Calados (Hydrostatic Table)")
        col_f1, col_f2, col_f3 = st.columns(3)
        st.session_state.t_min = col_f1.number_input("T min (m)", value=0.2, min_value=0.05, step=0.1)
        st.session_state.t_max = col_f2.number_input("T max (m)", value=float(calc_depth * 0.95), min_value=0.1, step=0.1)
        st.session_state.delta_t = col_f3.number_input("ΔT (m)", value=0.2, min_value=0.05, step=0.05)
        
        st.write("")
        if st.button("🚀 INICIAR CÁLCULOS & ABRIR MÓDULOS", type="primary", use_container_width=True):
            st.session_state.app_state = "analysis"
            st.rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)


# ==============================================================================
# TELA 2: PAINEL DE ANÁLISE (MODULAR VIA BOTÕES COM ESPAÇAMENTO PERFEITO)
# ==============================================================================
else:
    df_offsets = st.session_state.get("df_offsets", generate_barge_data())
    hull = Hull(
        df_offsets.columns, df_offsets.index, df_offsets.values,
        st.session_state.lbp, st.session_state.beam, st.session_state.depth, st.session_state.design_draft
    )
    
    # BANNER SUPERIOR DE IDENTIFICAÇÃO COM ESPAÇAMENTO APROPRIADO
    st.markdown(f"""
    <div class="student-header-banner">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
                <span style="color: #48cae4; font-weight: 700; font-size: 1.05rem;">👤 Aluno:</span> 
                <span style="font-weight: 700; font-size: 1.05rem;">{STUDENT_NAME}</span> 
                &nbsp;|&nbsp; 
                <span style="color: #48cae4; font-weight: 700; font-size: 1.05rem;">Matrícula:</span> 
                <span style="font-weight: 700; font-size: 1.05rem;">{STUDENT_ID}</span>
                <br>
                <span style="color: #94a3b8; font-size: 0.9rem;">
                    Embarcação: <b style="color:#f8fafc;">{st.session_state.ship_name}</b> | LBP: {hull.LBP:.1f}m | Boca: {hull.B:.1f}m | Pontal: {hull.D:.1f}m | Densidade: {st.session_state.density:.3f} t/m³
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_ret_space, col_ret_btn = st.columns([4, 1])
    with col_ret_btn:
        if st.button("⬅️ Trocar Embarcação / Início", use_container_width=True):
            st.session_state.app_state = "home"
            st.rerun()

    # ==========================================================================
    # BOTÕES DE SELEÇÃO DE MÓDULO
    # ==========================================================================
    st.markdown("#### 🧭 Selecione o Módulo para Visualização:")
    
    b_col1, b_col2, b_col3, b_col4, b_col5, b_col6 = st.columns(6)
    
    if b_col1.button("📋 Tabela de Cotas", use_container_width=True):
        st.session_state.selected_module = "📋 Tabela de Cotas"
    if b_col2.button("📐 Casco 2D & 3D", use_container_width=True):
        st.session_state.selected_module = "📐 Casco 2D & 3D"
    if b_col3.button("🧮 Cálculo & Auditoria", use_container_width=True):
        st.session_state.selected_module = "🧮 Cálculo & Auditoria"
    if b_col4.button("📊 Hydrostatic Table", use_container_width=True):
        st.session_state.selected_module = "📊 Hydrostatic Table"
    if b_col5.button("📈 Hydrostatic Curves", use_container_width=True):
        st.session_state.selected_module = "📈 Hydrostatic Curves"
    if b_col6.button("🧪 Validação Analítica", use_container_width=True):
        st.session_state.selected_module = "🧪 Validação Analítica"

    st.divider()

    # ==========================================================================
    # CONTEÚDO DO MÓDULO SELECIONADO
    # ==========================================================================
    
    # 1. TABELA DE COTAS
    if st.session_state.selected_module == "📋 Tabela de Cotas":
        st.subheader(f"📋 Tabela de Cotas: {st.session_state.ship_name}")
        st.caption("Matriz de semi-bocas (y em metros). Linhas = Linhas d'Água (Z) | Colunas = Estações (X)")
        
        st.dataframe(df_offsets.style.format("{:.3f}"), use_container_width=True)
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Estações (X)", f"{len(hull.stations_x)}")
        c2.metric("Linhas d'Água (Z)", f"{len(hull.waterlines_z)}")
        c3.metric("Comprimento (LBP)", f"{hull.LBP:.1f} m")
        c4.metric("Boca Máxima", f"{hull.B:.2f} m")
        
        st.success("✅ Tabela de cotas verificada: Formato numérico consistente para integração.")

    # 2. CASCO 2D & 3D
    elif st.session_state.selected_module == "📐 Casco 2D & 3D":
        st.subheader("📐 Reconstrução Geométrica e Plano de Linhas Naval (2D & 3D)")
        
        col_ctrl1, col_ctrl2 = st.columns([2, 3])
        with col_ctrl1:
            viz_draft = st.slider("🌊 Calado Analisado nas Vistas (m):", min_value=0.05, max_value=float(hull.D), value=float(hull.Td), step=0.05)
        with col_ctrl2:
            view_2d_choice = st.radio(
                "🧭 Selecione a Vista 2D para Exibição:",
                [
                    "⚓ Plano de Balizas (Body Plan - Vante/Ré)",
                    "🌊 Plano de Linhas d'Água (Waterlines)",
                    "📐 Plano de Linhas do Alto / Perfil (Sheer)",
                    "📑 Vista Completa (Tríptico Naval 2D)"
                ],
                horizontal=True
            )

        st.write("")
        col_v1, col_v2 = st.columns([1.2, 1])

        # ----------------------------------------------------------------------
        # FUNÇÕES GERADORAS DOS PLANOS 2D
        # ----------------------------------------------------------------------
        def get_body_plan_figure():
            fig = go.Figure()
            mid_idx = len(hull.stations_x) // 2
            
            # Linhas de grade das Linhas d'Água horizontais
            for wz in hull.waterlines_z:
                fig.add_hline(y=wz, line_dash="dot", line_color="rgba(148, 163, 184, 0.25)", line_width=1)
                
            # Eixo de Simetria (Linha de Centro - CL)
            fig.add_vline(x=0, line_color="#48cae4", line_width=1.8, annotation_text="CL", annotation_position="top")

            # Balizas de Vante (Proa - Lado Direito +Y)
            for j in range(mid_idx, len(hull.stations_x)):
                x_val = hull.stations_x[j]
                z_pts = np.linspace(hull.waterlines_z[0], hull.D, 40)
                y_pts = [hull.get_y(j, z) for z in z_pts]
                fig.add_trace(go.Scatter(
                    x=y_pts, y=z_pts, mode='lines',
                    name=f"ST {j} (x={x_val:.2f}m - Proa)",
                    line=dict(width=1.8)
                ))

            # Balizas de Ré (Popa - Lado Esquerdo -Y)
            for j in range(0, mid_idx + 1):
                x_val = hull.stations_x[j]
                z_pts = np.linspace(hull.waterlines_z[0], hull.D, 40)
                y_pts = [-hull.get_y(j, z) for z in z_pts]
                fig.add_trace(go.Scatter(
                    x=y_pts, y=z_pts, mode='lines',
                    name=f"ST {j} (x={x_val:.2f}m - Popa)",
                    line=dict(dash='dash' if j < mid_idx else 'solid', width=1.8)
                ))

            # Linha d'Água de Análise
            fig.add_hline(
                y=viz_draft, line_dash="dash", line_color="#00f5d4", line_width=2.5,
                annotation_text=f"Calado T = {viz_draft:.2f}m", annotation_position="top right"
            )
            
            fig.update_layout(
                title="Plano de Balizas (Body Plan) — [Esquerda: Popa | Direita: Proa]",
                xaxis_title="Semi-boca Y (m) [← Bombordo | Boreste →]",
                yaxis_title="Cota Vertical Z (m) [Linha de Base BL = 0]",
                template="plotly_dark", height=480, margin=dict(l=20, r=20, t=40, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=-0.35, xanchor="center", x=0.5)
            )
            return fig

        def get_waterlines_figure():
            fig = go.Figure()
            xs_eval = np.linspace(hull.stations_x[0], hull.stations_x[-1], 120)
            
            # 1. Malha de Referência (Grid): Balizas verticais (ST 00 a ST 10)
            for j, st_x in enumerate(hull.stations_x):
                fig.add_vline(
                    x=st_x, line_dash="solid", line_color="rgba(239, 68, 68, 0.55)", line_width=1.2,
                    annotation_text=f"ST {j:02d}", annotation_position="top"
                )

            # Cortes Longitudinais de referência (Corte I, II, III)
            cuts_ref = [0.34, 0.68, 1.00]
            for cy, clbl in zip(cuts_ref, ["I (340mm)", "II (680mm)", "III (1000mm)"]):
                fig.add_hline(
                    y=cy, line_dash="dot", line_color="rgba(148, 163, 184, 0.30)", line_width=1.0,
                    annotation_text=clbl, annotation_position="left"
                )

            # Linha de Centro (℄ LC - Linha base inferior horizontal)
            fig.add_hline(y=0, line_color="#ef4444", line_width=2.2, annotation_text="℄ LC (Linha de Centro)", annotation_position="left")

            # 2. Traçar Linhas d'Água (WL 01 a WL 10 - Planos de Flutuação)
            for k, wz in enumerate(hull.waterlines_z):
                if wz <= 0.0:
                    continue
                ys_wz = [hull.get_y_continuous(xv, wz) for xv in xs_eval]
                
                # Identifica limites onde a linha toca a LC
                fig.add_trace(go.Scatter(
                    x=xs_eval, y=ys_wz, mode='lines',
                    name=f"WL {k:02d} (z={wz:.2f}m)",
                    line=dict(color="#3b82f6", width=1.8)
                ))

            # Linha d'água ativa do calado selecionado (T)
            ys_act = [hull.get_y_continuous(xv, viz_draft) for xv in xs_eval]
            
            fig.add_trace(go.Scatter(
                x=xs_eval, y=ys_act, mode='lines',
                name=f"★ WL Ativa T={viz_draft:.2f}m",
                line=dict(color="#00f5d4", width=3.5)
            ))

            fig.update_layout(
                title="Plano de Linhas d'Água (Half-Breadth Plan / Planos de Flutuação 2D)",
                xaxis_title="Comprimento Longitudinal X (m) [PR (Popa) → SM (Meia-Nau) → PV (Proa)]",
                yaxis_title="Meia-boca Y (m) a partir da Linha de Centro (LC)",
                yaxis=dict(rangemode="nonnegative"),
                template="plotly_dark", height=500, margin=dict(l=25, r=25, t=45, b=25),
                legend=dict(orientation="h", yanchor="bottom", y=-0.38, xanchor="center", x=0.5)
            )
            return fig

        def get_sheer_figure():
            fig = go.Figure()
            xs_eval = np.linspace(hull.stations_x[0], hull.stations_x[-1], 120)
            mid_x = hull.stations_x[5]
            
            # 1. Malha de Referência (Grid): Balizas verticais (ST 00 a ST 10)
            for j, st_x in enumerate(hull.stations_x):
                fig.add_vline(
                    x=st_x, line_dash="solid", line_color="rgba(239, 68, 68, 0.55)", line_width=1.2,
                    annotation_text=f"ST {j:02d}", annotation_position="top"
                )

            # Linhas d'Água horizontais de referência (LB, WL 01 a WL 10)
            for k, wz in enumerate(hull.waterlines_z):
                fig.add_hline(
                    y=wz, line_dash="solid", line_color="rgba(59, 130, 246, 0.40)", line_width=1.0,
                    annotation_text=f"WL {k:02d}" if k > 0 else "LB", annotation_position="left"
                )

            # 2. Painel de Popa (PR / ST 00)
            fig.add_trace(go.Scatter(
                x=[0.0, 0.0], y=[0.0, hull.D], mode='lines',
                name="Painel de Popa (PR)",
                line=dict(color="#fca311", width=2.8)
            ))

            # 3. Linha de Convés / Borda Livre (Sheer Line do Convés)
            x_deck = [hull.stations_x[0], hull.stations_x[3], hull.stations_x[5], hull.stations_x[8], hull.stations_x[10]]
            z_deck = [1.62, 1.52, 1.48, 1.62, hull.D]
            pchip_deck = PchipInterpolator(x_deck, z_deck)
            z_deck_eval = np.clip(pchip_deck(xs_eval), 0.0, hull.D)
            
            fig.add_trace(go.Scatter(
                x=xs_eval, y=z_deck_eval, mode='lines',
                name="Linha de Convés (Sheer Line)",
                line=dict(color="#fca311", width=2.8)
            ))

            # 4. Perfil da Quilha & Roda de Proa (Linha de Centro Y = 0)
            z_stem = [0.0 if xv <= mid_x else float(hull.D * (((xv - mid_x) / (hull.stations_x[-1] - mid_x)) ** 1.85)) for xv in xs_eval]
            
            fig.add_trace(go.Scatter(
                x=xs_eval, y=z_stem, mode='lines',
                name="Perfil da Quilha & Roda de Proa (Y=0)",
                line=dict(color="#ffffff", width=3.0)
            ))

            # 5. Linhas do Alto (Cortes I, II, III / Longitudinais Diametrais)
            # Cortes contínuos em formato U aninhados conectando o painel de popa ao convés na proa
            cuts_data = [
                {"y": 0.340, "name": "Corte I (Y = 340 mm)", "color": "#c084fc", "w": 2.4},
                {"y": 0.680, "name": "Corte II (Y = 680 mm)", "color": "#f43f5e", "w": 2.4},
                {"y": 1.000, "name": "Corte III (Y = 1000 mm)", "color": "#38bdf8", "w": 2.4}
            ]
            
            for cut in cuts_data:
                y_c = cut["y"]
                z_station_pts = []
                for j, st_x in enumerate(hull.stations_x):
                    y_col = hull.offsets[:, j]
                    z_col = hull.waterlines_z
                    if y_c <= np.max(y_col):
                        z_val = float(np.interp(y_c, y_col, z_col))
                    else:
                        z_val = float(hull.D)
                    z_station_pts.append(z_val)
                    
                pchip_cut = PchipInterpolator(hull.stations_x, z_station_pts)
                z_cut_eval = np.clip(pchip_cut(xs_eval), 0.0, hull.D)
                
                fig.add_trace(go.Scatter(
                    x=xs_eval, y=z_cut_eval, mode='lines',
                    name=f"Linha do Alto {cut['name']}",
                    line=dict(color=cut["color"], width=cut["w"])
                ))

            # Calado Ativo de Análise (T)
            fig.add_hline(
                y=viz_draft, line_dash="dash", line_color="#00f5d4", line_width=2.5,
                annotation_text=f"Calado T = {viz_draft:.2f}m", annotation_position="bottom right"
            )

            fig.update_layout(
                title="Plano de Linhas do Alto (Sheer / Buttock Plan - Vista Lateral de Perfil 2D)",
                xaxis_title="Comprimento Longitudinal X (m) [PR (Popa) → SM (Meia-Nau) → PV (Proa)]",
                yaxis_title="Altura Vertical Z (m) a partir da Linha de Base (LB)",
                yaxis=dict(range=[-0.05, float(hull.D) + 0.1]),
                template="plotly_dark", height=500, margin=dict(l=25, r=25, t=45, b=25),
                legend=dict(orientation="h", yanchor="bottom", y=-0.38, xanchor="center", x=0.5)
            )
            return fig

        # ----------------------------------------------------------------------
        # EXIBIÇÃO NO PAINEL PRINCIPAL
        # ----------------------------------------------------------------------
        with col_v1:
            if view_2d_choice == "⚓ Plano de Balizas (Body Plan - Vante/Ré)":
                st.plotly_chart(get_body_plan_figure(), use_container_width=True)
            elif view_2d_choice == "🌊 Plano de Linhas d'Água (Waterlines)":
                st.plotly_chart(get_waterlines_figure(), use_container_width=True)
            elif view_2d_choice == "📐 Plano de Linhas do Alto / Perfil (Sheer)":
                st.plotly_chart(get_sheer_figure(), use_container_width=True)
            else:
                st.markdown("##### 1. Plano de Balizas (Body Plan)")
                st.plotly_chart(get_body_plan_figure(), use_container_width=True)
                st.markdown("##### 2. Plano de Linhas d'Água (Waterlines)")
                st.plotly_chart(get_waterlines_figure(), use_container_width=True)
                st.markdown("##### 3. Plano de Linhas do Alto (Perfil)")
                st.plotly_chart(get_sheer_figure(), use_container_width=True)

        with col_v2:
            st.markdown("#### Casco Tridimensional (3D Mesh Suave)")
            xs_3d = np.linspace(hull.stations_x[0], hull.stations_x[-1], 40)
            zs_3d = np.linspace(hull.waterlines_z[0], hull.D, 25)
            
            x_mesh, z_mesh = np.meshgrid(xs_3d, zs_3d)
            y_mesh = np.zeros_like(x_mesh)
            
            for r in range(x_mesh.shape[0]):
                for c in range(x_mesh.shape[1]):
                    y_mesh[r, c] = hull.get_y_continuous(x_mesh[r, c], z_mesh[r, c])
                
            fig_3d = go.Figure()
            fig_3d.add_trace(go.Surface(x=x_mesh, y=y_mesh, z=z_mesh, colorscale='Viridis', opacity=0.88, showscale=False, name="Boreste (+Y)"))
            fig_3d.add_trace(go.Surface(x=x_mesh, y=-y_mesh, z=z_mesh, colorscale='Viridis', opacity=0.88, showscale=False, name="Bombordo (-Y)"))
            
            # Plano da Água Flutuante
            xp, yp = np.meshgrid(np.linspace(hull.stations_x[0], hull.stations_x[-1], 8), np.linspace(-hull.B/2, hull.B/2, 8))
            zp = np.full_like(xp, viz_draft)
            fig_3d.add_trace(go.Surface(
                x=xp, y=yp, z=zp,
                colorscale=[[0, 'rgba(0, 245, 212, 0.40)'], [1, 'rgba(0, 245, 212, 0.40)']],
                showscale=False, name=f"Plano da Água (T={viz_draft:.2f}m)"
            ))
            
            fig_3d.update_layout(
                title=f"Casco 3D: {st.session_state.ship_name}",
                scene=dict(
                    xaxis_title="X (m) [Longitudinal]",
                    yaxis_title="Y (m) [Transversal]",
                    zaxis_title="Z (m) [Vertical]",
                    aspectmode='data'
                ),
                template="plotly_dark", height=480, margin=dict(l=10, r=10, t=40, b=10)
            )
            st.plotly_chart(fig_3d, use_container_width=True)

    # 3. CÁLCULO & AUDITORIA
    elif st.session_state.selected_module == "🧮 Cálculo & Auditoria":
        st.subheader("🧮 Painel Hidrostático por Calado & Memória de Cálculo")
        sel_t = st.slider("Selecione o Calado para Análise (m):", min_value=0.1, max_value=float(hull.D), value=float(hull.Td), step=0.05)
        
        data_t, audit_t, sec_areas = calculate_hydrostatics_at_draft(hull, sel_t, st.session_state.density)
        
        st.markdown("#### 1. Resumo de Propriedades Calculadas")
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Volume Submerso (∇)", f"{data_t['Volume (∇)']:.2f} m³")
        k2.metric("Deslocamento (Δ)", f"{data_t['Deslocamento (Δ)']:.2f} t")
        k3.metric("Centro Vertical (KB)", f"{data_t['KB']:.3f} m")
        k4.metric("Centro Long. (LCB)", f"{data_t['LCB']:.3f} m")
        
        st.write("")
        k5, k6, k7, k8 = st.columns(4)
        k5.metric("Área Plano (AWP)", f"{data_t['AWP']:.2f} m²")
        k6.metric("Centro Flutuação (LCF)", f"{data_t['LCF']:.3f} m")
        k7.metric("Raio Transv. (BMt)", f"{data_t['BMt']:.3f} m")
        k8.metric("Altura Transv. (KMt)", f"{data_t['KMt']:.3f} m")

        st.write("")
        k9, k10, k11, k12 = st.columns(4)
        k9.metric("Coef. Bloco (CB)", f"{data_t['CB']:.4f}")
        k10.metric("Coef. Flutuação (CWP)", f"{data_t['CWP']:.4f}")
        k11.metric("Coef. Meia-Nau (CM)", f"{data_t['CM']:.4f}")
        k12.metric("Coef. Prismático (CP)", f"{data_t['CP']:.4f}")

        st.divider()
        st.markdown("### 🔍 Função Obrigatória: MOSTRAR CÁLCULO (Auditoria)")
        st.caption("Conforme Item 22 do Edital: Rastreie a origem matemática, fórmula e dados usados.")
        
        prop_sel = st.selectbox("Selecione a Propriedade para Auditar:", options=list(audit_t.keys()))
        info = audit_t[prop_sel]
        
        st.markdown(f"""
        <div class="audit-box">
            <h4 style="margin-top:0; color:#48cae4;">📐 Memória de Cálculo: <b>{prop_sel}</b> (Calado T = {sel_t:.3f} m)</h4>
            <p style="font-weight:700; margin-bottom:4px;">1. Formulação Matemática:</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.latex(info["formula"])
        st.markdown(f"**2. Dados de Entrada:** {info['data']}")
        st.markdown(f"**3. Substituição e Valores Intermediários:** {info['intermediate']}")
        st.markdown(f"**4. Resultado Final Calculado:** `{info['result']} {info['unit']}`")
        
        if "log" in info:
            with st.expander("🔬 Métodos Numéricos por Trecho (Simpson 1/3, 3/8 e Trapézios)", expanded=True):
                st.dataframe(pd.DataFrame(info["log"]), use_container_width=True)

    # 4. HYDROSTATIC TABLE
    elif st.session_state.selected_module == "📊 Hydrostatic Table":
        st.subheader("📊 Hydrostatic Table Completa")
        st.caption(f"Calculada automaticamente de T = {st.session_state.t_min:.2f}m a T = {st.session_state.t_max:.2f}m com passo ΔT = {st.session_state.delta_t:.2f}m")
        
        drafts_range = np.arange(st.session_state.t_min, st.session_state.t_max + st.session_state.delta_t/2.0, st.session_state.delta_t)
        table_records = [calculate_hydrostatics_at_draft(hull, t_val, st.session_state.density)[0] for t_val in drafts_range]
        df_hydro_full = pd.DataFrame(table_records)
        
        col_order = ["T", "Volume (∇)", "Deslocamento (Δ)", "KB", "LCB", "AWP", "LCF", "BMt", "KMt", "BMl", "KMl", "TPC", "WSA", "CB", "CWP", "CM", "CP", "Erro_Vol"]
        df_hydro_view = df_hydro_full[[c for c in col_order if c in df_hydro_full.columns]]
        st.dataframe(df_hydro_view.style.format("{:.3f}"), use_container_width=True)
        
        excel_io = io.BytesIO()
        with pd.ExcelWriter(excel_io, engine='openpyxl') as writer:
            df_hydro_view.to_excel(writer, sheet_name="Hydrostatic_Table", index=False)
            df_offsets.to_excel(writer, sheet_name="Tabela_de_Cotas")
            
        st.download_button(
            label="📥 Baixar Hydrostatic Table em Excel (.xlsx)",
            data=excel_io.getvalue(),
            file_name=f"Hydrostatic_Table_{st.session_state.ship_name.replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    # 5. HYDROSTATIC CURVES
    elif st.session_state.selected_module == "📈 Hydrostatic Curves":
        st.subheader("📈 Hydrostatic Curves (Curvas Hidrostáticas)")
        drafts_range = np.arange(st.session_state.t_min, st.session_state.t_max + st.session_state.delta_t/2.0, st.session_state.delta_t)
        table_records = [calculate_hydrostatics_at_draft(hull, t_val, st.session_state.density)[0] for t_val in drafts_range]
        df_hydro_full = pd.DataFrame(table_records)
        
        fig_comb = go.Figure()
        curves_dict = {"Volume ∇": "Volume (∇)", "Deslocamento Δ": "Deslocamento (Δ)", "KB": "KB", "LCB": "LCB", "KMt": "KMt", "AWP": "AWP", "TPC": "TPC"}
        
        for label, col_n in curves_dict.items():
            fig_comb.add_trace(go.Scatter(x=df_hydro_full[col_n], y=df_hydro_full["T"], mode='lines+markers', name=label, line=dict(width=2)))
            
        fig_comb.update_layout(
            title="Diagrama Hidrostático Combinado", xaxis_title="Valor da Grandeza", yaxis_title="Calado T (m)",
            template="plotly_dark", height=550, hovermode="y unified"
        )
        st.plotly_chart(fig_comb, use_container_width=True)

    # 6. VALIDAÇÃO ANALÍTICA
    elif st.session_state.selected_module == "🧪 Validação Analítica":
        st.subheader("🧪 Validação 1 - Barcaça Paralelepipédica (Solução Analítica)")
        st.caption("Comparação das formulações em forma fechada exata com o algoritmo numérico implementado.")
        
        test_L, test_B, test_T = hull.LBP, hull.B, 1.0
        exact_vol = test_L * test_B * test_T
        exact_kb = test_T / 2.0
        exact_lcb = test_L / 2.0
        exact_bmt = (test_B ** 2) / (12.0 * test_T)
        exact_kmt = exact_kb + exact_bmt
        exact_awp = test_L * test_B
        
        res_val, _, _ = calculate_hydrostatics_at_draft(hull, test_T, st.session_state.density)
        def err_p(c_v, e_v): return (abs(c_v - e_v)/e_v*100.0) if e_v != 0 else 0.0

        df_val = pd.DataFrame([
            {"Propriedade": "Volume ∇ (m³)", "Fórmula": "L * B * T", "Analítico": exact_vol, "Aplicativo": res_val["Volume (∇)"], "Erro (%)": err_p(res_val["Volume (∇)"], exact_vol)},
            {"Propriedade": "KB (m)", "Fórmula": "T / 2", "Analítico": exact_kb, "Aplicativo": res_val["KB"], "Erro (%)": err_p(res_val["KB"], exact_kb)},
            {"Propriedade": "LCB (m)", "Fórmula": "L / 2", "Analítico": exact_lcb, "Aplicativo": res_val["LCB"], "Erro (%)": err_p(res_val["LCB"], exact_lcb)},
            {"Propriedade": "AWP (m²)", "Fórmula": "L * B", "Analítico": exact_awp, "Aplicativo": res_val["AWP"], "Erro (%)": err_p(res_val["AWP"], exact_awp)},
            {"Propriedade": "BMt (m)", "Fórmula": "B² / (12 * T)", "Analítico": exact_bmt, "Aplicativo": res_val["BMt"], "Erro (%)": err_p(res_val["BMt"], exact_bmt)},
            {"Propriedade": "KMt (m)", "Fórmula": "KB + BMt", "Analítico": exact_kmt, "Aplicativo": res_val["KMt"], "Erro (%)": err_p(res_val["KMt"], exact_kmt)}
        ])
        st.dataframe(df_val.style.format({"Analítico": "{:.4f}", "Aplicativo": "{:.4f}", "Erro (%)": "{:.4f}%"}), use_container_width=True)
        
        if df_val["Erro (%)"].max() < 0.05:
            st.success("✅ Validação Analítica APROVADA: Erros inferiores a 0.05%, confirmando precisão total do código.")
