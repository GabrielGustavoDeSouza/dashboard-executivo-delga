import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import warnings, os, pickle, datetime

warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Dashboard Executivo — Grupo Delga 2026",
    page_icon="https://grupodelga.com.br/wp-content/uploads/2024/11/logo-fa-e-clientes-grupo-whatsapp-9-300x300.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── PALETA DELGA ──────────────────────────────────────────────────────────────
NAVY   = "#1C2B4A"
RED    = "#C8202E"
SILVER = "#8A9BB0"
LIGHT  = "#F4F6F9"
WHITE  = "#FFFFFF"
GREEN  = "#1A7A3A"
AMBER  = "#E8A838"
TEAL   = "#20C997"

# ── TIPOS VÁLIDOS DE PROJETO ───────────────────────────────────────────────────
# Entram no DRE: BSW, Kaizen, Kaizen - Ganho Recorrente, Redução de Custo, Você Resolve
# NÃO entram no DRE: Kaizen - Custo Evitado, Kaizen - Capital de Giro
DRE_TIPOS = {
    'BSW', 'Kaizen', 'Kaizen - Ganho Recorrente',
    'Redução de custo', 'Redução de Custo', 'Redução de Custo ',
    'Você Resolve', 'Você resolve',
    'Estratégia Comercial', 'kaizen'
}
NAO_DRE_TIPOS = {
    'Kaizen - Custo Evitado', 'Kaizen - Capital de Giro',
    'Meta Executiva', 'Meta Executiva '
}
VALID_TIPOS = DRE_TIPOS | NAO_DRE_TIPOS

# Agrupamento para o gráfico de pilares (exibe todos os subtipos de Kaizen)
PILARES_EXIBE = {
    'Kaizen': 'Kaizen',
    'kaizen': 'Kaizen',
    'Kaizen - Ganho Recorrente': 'Kaizen - Ganho Recorrente',
    'Kaizen - Custo Evitado':    'Kaizen - Custo Evitado',
    'Kaizen - Capital de Giro':  'Kaizen - Capital de Giro',
    'Redução de custo':          'Redução de Custo',
    'Redução de Custo':          'Redução de Custo',
    'Redução de Custo ':         'Redução de Custo',
    'Você Resolve':              'Você Resolve',
    'Você resolve':              'Você Resolve',
    'BSW':                       'BSW',
    'Meta Executiva':            'Meta Executiva',
    'Estratégia Comercial':      'Estratégia Comercial',
}

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── FORÇAR LIGHT MODE GLOBALMENTE ── */
:root {{
  color-scheme: light !important;
}}

html, body, [data-testid="stAppViewContainer"], .main {{
  background-color: #F4F6F9 !important;
  color: #1C2B4A !important;
  font-family: 'Inter', sans-serif;
}}

/* Forçar cor de texto em seletores nativos do Streamlit */
[data-testid="stMarkdownContainer"] p, 
[data-testid="stMarkdownContainer"] span, 
[data-testid="stMarkdownContainer"] div,
label, .stText, p, span, div {{
  color: #1C2B4A;
}}

.block-container{{padding-top:0!important;padding-bottom:2rem;max-width:1440px;}}

/* ── INPUTS E SELETORES NO DARK/LIGHT MODE ── */
input, textarea, select, [data-baseweb="select"] {{
  background-color: #FFFFFF !important;
  color: #1C2B4A !important;
}}

div[data-baseweb="select"] * {{
  color: #1C2B4A !important;
  background-color: #FFFFFF !important;
}}

/* ── HEADER ── */
.dh{{background:linear-gradient(135deg,{NAVY} 0%,#243B55 100%);
     padding:18px 32px;border-radius:0 0 12px 12px;
     display:flex;align-items:center;gap:18px;margin-bottom:20px;
     box-shadow:0 2px 12px rgba(28,43,74,.18);}}
.dh img{{height:44px;border-radius:6px;}}
.dh-t h1{{color:white !important;font-size:20px;font-weight:700;margin:0;letter-spacing:-.2px;}}
.dh-t p{{color:rgba(255,255,255,.75) !important;font-size:11px;margin:2px 0 0;}}
.dh-b{{margin-left:auto;background:rgba(255,255,255,.12);
       color:rgba(255,255,255,.85) !important;font-size:10px;
       font-weight:500;padding:5px 14px;border-radius:8px;white-space:nowrap;
       letter-spacing:.4px;border:1px solid rgba(255,255,255,.18);}}
.dh-b span.lbl{{font-size:9px;opacity:.7;display:block;letter-spacing:.6px;text-transform:uppercase;margin-bottom:1px;color:white !important;}}

/* ── KPI CARDS ── */
.kpi-wrap{{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;margin-bottom:20px;}}
.kpi-6{{grid-template-columns:repeat(6,1fr);}}
.kpi-card{{background:white !important;border-radius:12px;padding:18px 20px;
           border-left:4px solid {NAVY};
           box-shadow:0 1px 4px rgba(28,43,74,.06),0 4px 16px rgba(28,43,74,.04);
           transition:box-shadow .2s;}}
.kpi-card:hover{{box-shadow:0 2px 8px rgba(28,43,74,.1),0 8px 24px rgba(28,43,74,.06);}}
.kpi-card.cr{{border-left-color:{RED};}}
.kpi-card.cg{{border-left-color:{GREEN};}}
.kpi-card.ca{{border-left-color:{AMBER};}}
.kpi-card.cs{{border-left-color:{SILVER};}}
.kpi-l{{font-size:9px;font-weight:600;color:{SILVER} !important;text-transform:uppercase;
        letter-spacing:.9px;margin-bottom:6px;}}
.kpi-v{{font-size:24px;font-weight:700;color:{NAVY} !important;line-height:1.1;margin-bottom:3px;}}
.kpi-s{{font-size:11px;color:#555555 !important;margin-bottom:2px;}}
.kpi-d{{font-size:10px;color:{SILVER} !important;}}

/* ── SECTION CARD ── */
.sc{{background:white !important;border-radius:12px;padding:20px 22px;
     box-shadow:0 1px 4px rgba(28,43,74,.06),0 4px 16px rgba(28,43,74,.04);
     margin-bottom:16px;}}
.st{{font-size:11px;font-weight:700;color:{NAVY} !important;text-transform:uppercase;
     letter-spacing:.7px;border-bottom:2px solid {RED};
     padding-bottom:7px;margin-bottom:14px;display:inline-block;}}

/* ── NOTA ── */
.nota{{background:#FFFBF0 !important;border-left:3px solid {AMBER};border-radius:6px;
       padding:11px 16px;font-size:11px;color:#444444 !important;line-height:1.7;margin:14px 0;}}

/* ── TABELA ── */
.dt{{width:100%;border-collapse:collapse;font-size:12px;background:white !important;color:#1C2B4A !important;}}
.dt thead tr{{background:{NAVY} !important;}}
.dt thead th{{color:white !important;padding:10px 12px;text-align:left;font-weight:600;
              font-size:11px;white-space:nowrap;}}
.dt thead th:first-child{{border-radius:6px 0 0 0;}}
.dt thead th:last-child{{border-radius:0 6px 0 0;}}
.dt tbody tr{{background:white !important;color:#1C2B4A !important;}}
.dt tbody tr:nth-child(even){{background:#FAFBFC !important;}}
.dt tbody tr:hover{{background:#F0F4FA !important;transition:background .1s;}}
.dt tbody td{{padding:8px 12px;border-bottom:1px solid #EEF0F3;vertical-align:middle;color:#1C2B4A !important;}}
.dt tbody tr.tr-tot td{{background:{LIGHT} !important;font-weight:700;
                         border-top:2px solid {NAVY};border-bottom:none;color:#1C2B4A !important;}}

/* ── MACRO TABLE ── */
.mct{{width:100%;border-collapse:collapse;font-size:12px;background:white !important;color:#1C2B4A !important;}}
.mct td{{padding:10px 12px;border-bottom:1px solid #EEF0F3;vertical-align:middle;color:#1C2B4A !important;}}
.mct tr:hover{{background:#F7F9FC !important;}}
.mch th{{color:white !important;padding:10px 12px;font-weight:600;font-size:11px;
         text-align:left;white-space:nowrap;}}
.mc-tot td{{background:{LIGHT} !important;font-weight:700;border-top:2px solid {NAVY};color:#1C2B4A !important;}}

/* ── PROGRESS ── */
.pb{{display:flex;align-items:center;gap:8px;}}
.pb-bg{{height:7px;background:#E2E8F0;border-radius:4px;overflow:hidden;display:inline-block;}}
.pb-f{{height:100%;border-radius:4px;}}

/* ── BADGES ── */
.bdg{{display:inline-block;padding:2px 8px;border-radius:10px;font-size:10px;font-weight:600;}}
.bg{{background:#E6F4EC !important;color:{GREEN} !important;}}
.ba{{background:#FFF3E0 !important;color:{AMBER} !important;}}
.br{{background:#FDECEA !important;color:{RED} !important;}}
.bk{{background:#F2F3F5 !important;color:#555555 !important;}}
.bn{{background:#E8EDF5 !important;color:{NAVY} !important;}}

/* ── IMPEDIMENTO ── */
.imp{{background:#FFF8E1 !important;border-left:3px solid {AMBER};border-radius:4px;
      padding:3px 7px;font-size:10px;color:#555555 !important;margin-top:3px;line-height:1.5;}}

/* ── TOGGLE LABELS — sem quebra de linha ── */
[data-testid="stToggle"] label {{white-space:nowrap!important;font-size:12px!important;font-weight:500!important;color:#1C2B4A!important;}}
[data-testid="stToggle"] {{align-items:center!important;}}

/* ── SECTION TOGGLE — botão − / + minimalista (sem círculo) ── */
[data-testid="stColumn"]:last-child button[kind="secondary"]{{
  font-size:18px!important;font-weight:200!important;
  color:{SILVER}!important;
  background:transparent!important;
  border:none!important;
  border-bottom:1.5px solid #DDE2EA!important;
  border-radius:0!important;
  width:24px!important;height:24px!important;
  padding:0!important;min-width:unset!important;
  line-height:1!important;
  display:flex!important;align-items:center!important;justify-content:center!important;
  margin-top:4px;transition:color .15s,border-color .15s;
}}
[data-testid="stColumn"]:last-child button[kind="secondary"]:hover{{
  color:{NAVY}!important;border-bottom-color:{NAVY}!important;
}}

/* ── LOGIN ── */
.lw{{max-width:360px;margin:80px auto;padding:40px;background:white !important;
     border-radius:14px;box-shadow:0 8px 32px rgba(28,43,74,.14);text-align:center;color:#1C2B4A !important;}}

#MainMenu{{visibility:hidden;}}footer{{visibility:hidden;}}
.stDeployButton{{display:none;}}header[data-testid="stHeader"]{{display:none;}}

div[data-testid="stExpander"]{{
  background-color: white !important;
  border-radius: 8px !important;
}}
div[data-testid="stExpander"]>div:first-child{{
  background:{LIGHT}!important;border:1px solid #E2E8F0!important;
  border-radius:8px!important;padding:4px 10px!important;}}
div[data-testid="stExpander"] * {{
  color: #1C2B4A !important;
}}
</style>
""", unsafe_allow_html=True)

# ── SENHA ─────────────────────────────────────────────────────────────────────
SENHA = "Delga01"
DADOS_PATH = "/tmp/delga_dados.pkl"

def check_password():
    if st.session_state.get("auth"): return True
    st.markdown("""<div class="lw">
      <div style="font-size:44px;margin-bottom:12px;">📊</div>
      <div style="font-size:20px;font-weight:700;color:#1C2B4A !important;margin-bottom:4px;">Grupo Delga</div>
      <div style="font-size:12px;color:#8A9BB0 !important;margin-bottom:22px;">Dashboard Executivo 2026 — Acesso Restrito</div>
    </div>""", unsafe_allow_html=True)
    _, col, _ = st.columns([1,2,1])
    with col:
        pw = st.text_input("Senha", type="password", placeholder="Senha de acesso",
                           label_visibility="collapsed")
        if st.button("Entrar →", use_container_width=True, type="primary"):
            if pw == SENHA:
                st.session_state["auth"] = True; st.rerun()
            else:
                st.error("Senha incorreta.")
    return False

if not check_password(): st.stop()

# ── FORMATAÇÃO ────────────────────────────────────────────────────────────────
def fmt_mi(v):
    if pd.isna(v) or v is None: return "R$ 0"
    v = float(v)
    if abs(v) >= 1_000_000: return f"R$ {v/1_000_000:.2f} Mi"
    if abs(v) >= 1_000:     return "R$ " + f"{v:,.0f}".replace(",","X").replace(".",",").replace("X",".")
    return f"R$ {v:.0f}"

def fmt_brl(v):
    if pd.isna(v) or v is None or float(v)==0: return "—"
    return "R$ " + f"{float(v):,.0f}".replace(",","X").replace(".",",").replace("X",".")

def fmt_date(v):
    if pd.isna(v) or v is None or str(v).strip() in ("nan",""): return "—"
    s = str(v).strip()
    if s.upper() in ("N/A","NA","S/A"): return s
    try:
        if isinstance(v,(datetime.datetime,datetime.date)): return v.strftime("%m/%Y")
        if " " in s and ":" in s: return pd.to_datetime(s).strftime("%m/%Y")
        return s[:7]
    except: return s

def safe(v, d=0.0):
    try: return float(v) if pd.notna(v) else d
    except: return d

def pbar_html(pct, w=72):
    pc = min(float(pct)*100, 100)
    c = GREEN if pct>=.30 else (AMBER if pct>=.15 else RED)
    return (f'<div class="pb"><div class="pb-bg" style="width:{w}px;">'
            f'<div class="pb-f" style="width:{pc:.0f}%;background:{c};"></div></div>'
            f'<span style="font-size:11px;font-weight:600;color:#1C2B4A !important;">{pc:.1f}%</span></div>')

def bdg_status(pct):
    return ('<span class="bdg bg">DESTAQUE ✓</span>' if pct>=.30
            else '<span class="bdg ba">EM EXECUÇÃO</span>')

def bdg_custos(v):
    v=str(v).strip()
    if v=="OK":                       return '<span class="bdg bg">✓ OK</span>'
    if v in("Não Ok","NOK","Não OK"): return '<span class="bdg br">✗ NOK</span>'
    if v in("","nan"):                return '<span class="bdg bk">Pendente</span>'
    return f'<span class="bdg bk">{v}</span>'

def bdg_st(v):
    v=str(v)
    if "Concluído" in v: return '<span class="bdg bg">✓ Concluído</span>'
    if "Execução"  in v: return '<span class="bdg ba">⏳ Execução</span>'
    if "Não"       in v: return '<span class="bdg bk">Não iniciado</span>'
    return f'<span class="bdg bk">{v[:20]}</span>'

def bdg_tipo(v):
    v=str(v).strip()
    if "BSW"         in v: return f'<span class="bdg bn">BSW</span>'
    if "Capital"     in v: return f'<span class="bdg" style="background:#EDE7F6 !important;color:#512DA8 !important;">Cap. Giro</span>'
    if "Evitado"     in v: return f'<span class="bdg" style="background:#E3F2FD !important;color:#0D47A1 !important;">C. Evitado</span>'
    if "Recorrente"  in v: return f'<span class="bdg ba">Kaizen GR</span>'
    if "Kaizen"      in v or "kaizen" in v: return f'<span class="bdg ba">Kaizen</span>'
    if "Redução"     in v: return f'<span class="bdg bg">Red. Custo</span>'
    if "Você"        in v or "Voce" in v: return f'<span class="bdg bk">Você Resolve</span>'
    if "Meta"        in v: return f'<span class="bdg bn">Meta Exec.</span>'
    if "Estratégia"  in v: return f'<span class="bdg bn">Est. Comercial</span>'
    return f'<span class="bdg bk">{v[:15]}</span>'

def is_dre(tipo):
    """True se o tipo de projeto entra no DRE."""
    return str(tipo).strip() in DRE_TIPOS

# ── PERSISTÊNCIA ──────────────────────────────────────────────────────────────
def save_bytes(b):
    with open(DADOS_PATH,"wb") as f: pickle.dump(b,f)
def load_bytes():
    if os.path.exists(DADOS_PATH):
        with open(DADOS_PATH,"rb") as f: return pickle.load(f)
    return None

# ── CARGA DO EXCEL ────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_data(fb):
    import io
    def xls(sh): return pd.read_excel(io.BytesIO(fb), sheet_name=sh, header=None)
    d = {}
    d["u5"]  = xls("5 Unidades  +")
    d["par"] = xls("Pareto")
    for s in ["Diadema","Jarinu","Ferraz","São Leopoldo","Anchieta",
              "Compras ","Vendas","Corporativo"]:
        d[s] = xls(s)
    return d

# ── EXTRAÇÃO — KPIs GLOBAIS ───────────────────────────────────────────────────
def extract_kpis(d):
    df = d["u5"]
    return dict(
        meta      =safe(df.iloc[6,3]),
        portfolio =safe(df.iloc[6,5]),
        prev2026  =safe(df.iloc[6,6]),
        validado  =safe(df.iloc[6,7]),
        real      =safe(df.iloc[6,9]),
        extra_dre =safe(df.iloc[6,10]),
        pct_ating =safe(df.iloc[6,11]),
        inic      =int(safe(df.iloc[6,13])),
    )

def extract_plantas(d):
    df = d["u5"]
    cfg = [("Diadema",4,"Diadema"),("Ferraz",5,"Ferraz"),
           ("São Leopoldo",6,"São Leopoldo"),("Jarinu",7,"Jarinu"),("Anchieta",8,"Anchieta")]
    res=[]
    for nome,col,sh in cfg:
        res.append(dict(nome=nome,sheet=sh,
            meta    =safe(df.iloc[22,col]),
            prev    =safe(df.iloc[23,col]),
            prev2026=safe(df.iloc[24,col]),
            val     =safe(df.iloc[25,col]),
            real    =safe(df.iloc[26,col]),
            pct     =safe(df.iloc[27,col]),
            extra   =safe(df.iloc[28,col])))
    return res

def extract_areas(d):
    df = d["u5"]
    cfg = [("Corporativo",9,"Corporativo"),("Compras",10,"Compras "),("Vendas",11,"Vendas")]
    res=[]
    for nome,col,sh in cfg:
        res.append(dict(nome=nome,sheet=sh,
            meta    =safe(df.iloc[22,col]),
            prev    =safe(df.iloc[23,col]),
            prev2026=safe(df.iloc[24,col]),
            val     =safe(df.iloc[25,col]),
            real    =safe(df.iloc[26,col]),
            pct     =safe(df.iloc[27,col]),
            extra   =safe(df.iloc[28,col])))
    return res

def extract_pilares_global(d):
    df = d["u5"]
    res=[]
    for i in range(12,22):
        nome=df.iloc[i,3]
        if pd.notna(nome) and str(nome) not in ("TOTAL",""):
            try:
                res.append(dict(
                    nome=str(nome),qtd=int(safe(df.iloc[i,4])),
                    prev=safe(df.iloc[i,5]),val=safe(df.iloc[i,6]),
                    pct=safe(df.iloc[i,7])))
            except: pass
    return res

def extract_pilares_local(projetos):
    from collections import defaultdict
    qtd  = defaultdict(int)
    prev = defaultdict(float)
    real = defaultdict(float)
    for p in projetos:
        nome = PILARES_EXIBE.get(p["tipo"], p["tipo"])
        qtd[nome]  += 1
        prev[nome] += p["previsto"]
        real[nome] += p["real_ano"]
    ORDER = ["BSW","Kaizen","Kaizen - Ganho Recorrente",
             "Kaizen - Custo Evitado","Kaizen - Capital de Giro",
             "Redução de Custo","Você Resolve","Meta Executiva","Estratégia Comercial"]
    res=[]
    for k in ORDER:
        if k in qtd:
            entra_dre = k not in ("Kaizen - Custo Evitado","Kaizen - Capital de Giro","Meta Executiva","Meta Executiva ")
            res.append(dict(nome=k,qtd=qtd[k],prev=prev[k],real=real[k],dre=entra_dre))
    for k in sorted(qtd):
        if k not in ORDER:
            entra_dre = k not in ("Kaizen - Custo Evitado","Kaizen - Capital de Giro","Meta Executiva","Meta Executiva ")
            res.append(dict(nome=k,qtd=qtd[k],prev=prev[k],real=real[k],dre=entra_dre))
    return res

def extract_evolucao(d):
    df = d["u5"]
    meses=["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
    max_col = min(34, df.shape[1])
    def row(r): return [safe(df.iloc[r,c]) for c in range(22, max_col)]
    def pad(lst): return (lst + [0]*12)[:12]

    return dict(meses=meses,
                prev     =pad(row(55)),
                real     =pad(row(56)),
                acum_prev=pad(row(58)),
                acum_real=pad(row(59)),
                proj_meta=pad(row(60)))

# ── EXTRAÇÃO DE PROJETOS — FUNÇÃO CENTRAL ─────────────────────────────────────
def extract_projetos(df, start_row, col_tipo=0, col_nome=2, col_resp=5,
                     col_termino=7, col_custos=12, col_saving=13,
                     col_status=14, col_onde=15, col_data_lib=16,
                     col_prev_real=18, col_total_ano=36, col_previsto=8):
    res = []
    i = start_row
    max_row = min(start_row + 600, df.shape[0] - 1)
    while i <= max_row:
        tipo = str(df.iloc[i, col_tipo]).replace("\n"," ").replace("\r"," ").strip()
        nome = str(df.iloc[i, col_nome]).replace("\n"," ").replace("\r"," ").strip()
        c_pr = str(df.iloc[i, col_prev_real]).strip() if df.shape[1] > col_prev_real else ""

        if tipo in VALID_TIPOS and nome not in ("", "nan") and c_pr == "Previsto":
            tot_prev = safe(df.iloc[i, col_previsto])

            tot_real = 0.0
            if i+1 <= max_row:
                c_pr_next = str(df.iloc[i+1, col_prev_real]).strip() if df.shape[1] > col_prev_real else ""
                if c_pr_next == "Real":
                    tot_real = safe(df.iloc[i+1, col_total_ano])

            onde_parado = ""
            data_lib    = ""
            if col_onde is not None and df.shape[1] > col_onde:
                v_onde = df.iloc[i, col_onde]
                v_str = str(v_onde).strip() if pd.notna(v_onde) else ""
                if v_str not in ("", "nan"):
                    onde_parado = v_str
            if col_data_lib is not None and df.shape[1] > col_data_lib:
                v_dl = df.iloc[i, col_data_lib]
                v_str2 = str(v_dl).strip() if pd.notna(v_dl) else ""
                if v_str2 not in ("", "nan"):
                    data_lib = fmt_date(v_dl)

            res.append(dict(
                tipo       = tipo,
                nome       = nome,
                resp       = str(df.iloc[i, col_resp]).strip() if pd.notna(df.iloc[i, col_resp]) else "—",
                termino    = fmt_date(df.iloc[i, col_termino]),
                previsto   = tot_prev,
                real_ano   = tot_real,
                val_custos = str(df.iloc[i, col_custos]).strip() if pd.notna(df.iloc[i, col_custos]) else "",
                val_saving = safe(df.iloc[i, col_saving]),
                status     = str(df.iloc[i, col_status]).strip() if pd.notna(df.iloc[i, col_status]) else "",
                onde_parado= onde_parado,
                data_lib   = data_lib,
                entra_dre  = is_dre(tipo),
            ))
            i += 2
        elif tipo not in ("", "nan") and tipo not in VALID_TIPOS:
            break
        else:
            i += 1
    return res

def get_proj_planta(d, sheet_key):
    df = d.get(sheet_key)
    if df is None: return []
    return extract_projetos(df, start_row=54,
        col_tipo=0, col_nome=2, col_resp=5, col_termino=7,
        col_custos=12, col_saving=13, col_status=14,
        col_onde=15, col_data_lib=16,
        col_prev_real=18, col_total_ano=36, col_previsto=8)

def get_proj_compras(d):
    df = d.get("Compras ")
    if df is None: return []
    return extract_projetos(df, start_row=30,
        col_tipo=0, col_nome=3, col_resp=5, col_termino=7,
        col_custos=12, col_saving=13, col_status=14,
        col_onde=15, col_data_lib=16,
        col_prev_real=19, col_total_ano=37, col_previsto=8)

def get_proj_vendas(d):
    df = d.get("Vendas")
    if df is None: return []
    return extract_projetos(df, start_row=33,
        col_tipo=0, col_nome=1, col_resp=4, col_termino=6,
        col_custos=11, col_saving=12, col_status=13,
        col_onde=14, col_data_lib=15,
        col_prev_real=17, col_total_ano=35, col_previsto=7)

def extract_ranking(d):
    df = d["u5"]
    res=[]
    for i in range(53,137):
        uni=df.iloc[i,4]; nome=df.iloc[i,5]
        if not pd.notna(uni) or not pd.notna(nome): continue
        res.append(dict(
            pos=int(safe(df.iloc[i,3],i-52)),
            uni=str(uni),nome=str(nome),
            status=str(df.iloc[i,7]).strip() if pd.notna(df.iloc[i,7]) else "",
            custos=str(df.iloc[i,8]).strip() if pd.notna(df.iloc[i,8]) else "",
            prev26=safe(df.iloc[i,9]),prev_mo=safe(df.iloc[i,10]),real=safe(df.iloc[i,11]),
        ))
    return res

# ── GRÁFICOS ──────────────────────────────────────────────────────────────────
PAL = [NAVY,"#2C4F7C","#4A7AB5",SILVER,"#A8C8E8"]

def chart_funnel(kpis):
    stages = ["Meta do Grupo","Portfólio Previsto (Anualizado)","Previsto 2026","Validado Custos","Real DRE"]
    values = [kpis["meta"],kpis["portfolio"],kpis["prev2026"],kpis["validado"],kpis["real"]]
    pcts   = [f"{v/kpis['meta']*100:.1f}%" for v in values]
    colors = [NAVY,"#2C5F8A","#4A90D9",AMBER,GREEN]

    fig = go.Figure()
    for idx,(stage,val,pct,color) in enumerate(zip(stages,values,pcts,colors)):
        w = val/kpis["meta"]
        fig.add_trace(go.Bar(
            x=[val], y=[stage],
            orientation="h",
            marker=dict(color=color, line=dict(width=0)),
            text=f"  <b>{fmt_mi(val)}</b>  <span style='opacity:.7'>({pct})</span>",
            textposition="outside",
            textfont=dict(size=12,color="#1C2B4A"),
            hovertemplate=f"<b>{stage}</b><br>{fmt_mi(val)}<br>{pct} da meta<extra></extra>",
            showlegend=False,
            base=[(kpis["meta"]-val)/2],
        ))

    fig.update_layout(
        barmode="overlay",
        xaxis=dict(visible=False, range=[0, kpis["meta"]*1.3]),
        yaxis=dict(autorange="reversed",tickfont=dict(size=12,color="#1C2B4A")),
        margin=dict(l=130,r=150,t=10,b=10),
        height=310,
        paper_bgcolor="white", plot_bgcolor="white",
        font=dict(family="Inter", color="#1C2B4A"),
    )
    return fig

def chart_gauge(pct):
    clr = GREEN if pct>=.30 else (AMBER if pct>=.15 else RED)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pct*100,
        number=dict(suffix="%",font=dict(size=40,color=NAVY,family="Inter")),
        gauge=dict(
            axis=dict(range=[0,100],ticksuffix="%",tickfont=dict(size=10, color="#1C2B4A")),
            bar=dict(color=clr,thickness=0.28),
            bgcolor="white",borderwidth=0,
            steps=[dict(range=[0,30],color="#FFEBEE"),
                   dict(range=[30,70],color="#FFF3E0"),
                   dict(range=[70,100],color="#E8F5E9")],
            threshold=dict(line=dict(color=RED,width=3),thickness=.75,value=100),
        ),
        title=dict(text="<b>Atingimento da Meta</b>",font=dict(size=12,color=SILVER)),
    ))
    fig.update_layout(margin=dict(l=20,r=20,t=50,b=10),height=280,paper_bgcolor="white", font=dict(family="Inter", color="#1C2B4A"))
    return fig

import plotly.graph_objects as go
import pandas as pd

def chart_evolucao(ev, sel):
    # 1. Trava de segurança: se nenhuma série for selecionada ou o DataFrame estiver vazio
    if not sel or ev is None or (isinstance(ev, pd.DataFrame) and ev.empty):
        fig = go.Figure()
        fig.update_layout(
            xaxis={"visible": False},
            yaxis={"visible": False},
            annotations=[{
                "text": "Selecione ao menos uma série no filtro acima.",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {"size": 14, "color": "#1C2B4A", "family": "Inter"}
            }],
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        return fig

    # 2. Inicialização da figura do Plotly
    fig = go.Figure()

    # 3. Mapeamento e montagem das séries conforme a seleção 'sel'
    # Ajuste os nomes das colunas e os tipos de traço (bar/scatter) de acordo com o seu modelo:
    if "Acumulado Previsto" in sel and "acumulado_previsto" in ev.columns:
        fig.add_trace(go.Scatter(
            x=ev["mes"], y=ev["acumulado_previsto"],
            mode="lines+markers", name="Acumulado Previsto"
        ))

    if "Acumulado Real" in sel and "acumulado_real" in ev.columns:
        fig.add_trace(go.Scatter(
            x=ev["mes"], y=ev["acumulado_real"],
            mode="lines+markers", name="Acumulado Real"
        ))

    if "Projeção da Meta" in sel and "projecao_meta" in ev.columns:
        fig.add_trace(go.Scatter(
            x=ev["mes"], y=ev["projecao_meta"],
            mode="lines", line=dict(dash="dash"), name="Projeção da Meta"
        ))

    if "Previsto Mensal" in sel and "previsto_mensal" in ev.columns:
        fig.add_trace(go.Bar(
            x=ev["mes"], y=ev["previsto_mensal"], name="Previsto Mensal"
        ))

    if "Real Mensal" in sel and "real_mensal" in ev.columns:
        fig.add_trace(go.Bar(
            x=ev["mes"], y=ev["real_mensal"], name="Real Mensal"
        ))

    # 4. Estilização do Layout (Linha 614 do seu app.py)
    fig.update_layout(
        barmode="group",
        font=dict(family="Inter", color="#1C2B4A"),
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#E5E7EB")
    )

    return fig

def chart_donut(labels,values,colors):
    total = sum(values)
    if total == 0:
        total = 1
    txt = [f"  {labels[i]}  {values[i]/total*100:.1f}%  {fmt_mi(values[i])}"
           for i in range(len(labels))]
    fig = go.Figure(go.Pie(labels=txt,values=values,hole=0.62,
        marker=dict(colors=colors),textinfo="none",
        hovertemplate="<b>%{label}</b><extra></extra>"))
    fig.update_layout(showlegend=True,
        legend=dict(orientation="v",y=0.5,x=0.55,yanchor="middle",font=dict(size=11, color="#1C2B4A")),
        margin=dict(l=10,r=10,t=10,b=30),height=280,
        paper_bgcolor="white",plot_bgcolor="white",
        annotations=[dict(text=f"<b>{fmt_mi(sum(values))}</b>",x=0.22,y=-0.08,
                          font_size=12,showarrow=False,font=dict(color="#1C2B4A"))],
        font=dict(family="Inter", color="#1C2B4A"))
    return fig

def chart_pilares(pilares_global, real_total):
    labels=[p["nome"] for p in pilares_global]
    previsto=[p["prev"] for p in pilares_global]
    validado=[p["val"]  for p in pilares_global]
    tv=sum(validado)
    real_est=[v/tv*real_total if tv>0 else 0 for v in validado]
    fig=go.Figure()
    fig.add_trace(go.Bar(name="Previsto",x=labels,y=previsto,marker_color="#B8D4E8"))
    fig.add_trace(go.Bar(name="Validado",x=labels,y=validado,marker_color=NAVY))
    fig.add_trace(go.Bar(name="Real DRE",x=labels,y=real_est, marker_color=GREEN))
    fig.update_layout(barmode="group",
        yaxis=dict(tickformat=",.0f",showgrid=True,gridcolor="#F0F4F8",tickfont=dict(color="#1C2B4A")),
        xaxis=dict(tickfont=dict(color="#1C2B4A")),
        legend=dict(orientation="h",y=1.05,x=1,xanchor="right",font=dict(size=11, color="#1C2B4A")),
        margin=dict(l=60,r=20,t=40,b=60),height=300,
        paper_bgcolor="white",plot_bgcolor="white",
        bargap=0.28,font=dict(family="Inter", color="#1C2B4A"))
    return fig

# ── HTML HELPERS ──────────────────────────────────────────────────────────────
def th(*cols):
    ths = "".join(f"<th>{c}</th>" for c in cols)
    return f"<table class='dt'><thead><tr>{ths}</tr></thead><tbody>"

def render_proj_filtros(projetos, key_prefix=""):
    if not projetos:
        return projetos

    TIPOS_DISP   = sorted({p["tipo"] for p in projetos if p["tipo"]})
    STATUS_DISP  = sorted({p["status"] for p in projetos if p["status"]})
    CUSTOS_DISP  = sorted({p["val_custos"] for p in projetos if p["val_custos"]})

    fc1, fc2, fc3, fc4, fc5 = st.columns([2,2,2,2,3])

    with fc1:
        f_tipo = st.multiselect("Tipo", TIPOS_DISP, default=[],
                                key=f"{key_prefix}_ftipo", placeholder="Todos")
    with fc2:
        f_status = st.multiselect("Status", STATUS_DISP, default=[],
                                  key=f"{key_prefix}_fstatus", placeholder="Todos")
    with fc3:
        f_custos = st.multiselect("Custos", CUSTOS_DISP, default=[],
                                  key=f"{key_prefix}_fcustos", placeholder="Todos")
    with fc4:
        sort_col = st.selectbox("Ordenar por",
            ["Nome (A→Z)", "Nome (Z→A)",
             "V.Previsto ↓", "V.Previsto ↑",
             "V.Validado ↓", "V.Validado ↑",
             "V.Real ↓",    "V.Real ↑",
             "Status (A→Z)","Tipo (A→Z)"],
            index=0, key=f"{key_prefix}_sort")
    with fc5:
        f_nome = st.text_input("🔍 Buscar projeto", value="",
                               key=f"{key_prefix}_fnome", placeholder="Filtrar por nome...")

    res = projetos[:]
    if f_tipo:   res = [p for p in res if p["tipo"]       in f_tipo]
    if f_status: res = [p for p in res if p["status"]     in f_status]
    if f_custos: res = [p for p in res if p["val_custos"] in f_custos]
    if f_nome:   res = [p for p in res if f_nome.lower() in p["nome"].lower()]

    sort_map = {
        "Nome (A→Z)":    (lambda p: p["nome"].lower(),       False),
        "Nome (Z→A)":    (lambda p: p["nome"].lower(),       True),
        "V.Previsto ↓":  (lambda p: p["previsto"],           True),
        "V.Previsto ↑":  (lambda p: p["previsto"],           False),
        "V.Validado ↓":  (lambda p: p["val_saving"],         True),
        "V.Validado ↑":  (lambda p: p["val_saving"],         False),
        "V.Real ↓":      (lambda p: p["real_ano"],           True),
        "V.Real ↑":      (lambda p: p["real_ano"],           False),
        "Status (A→Z)":  (lambda p: p["status"].lower(),     False),
        "Tipo (A→Z)":    (lambda p: p["tipo"].lower(),       False),
    }
    key_fn, rev = sort_map.get(sort_col, (lambda p: p["nome"].lower(), False))
    res = sorted(res, key=key_fn, reverse=rev)

    return res


def projetos_por_pilar_html(projetos, key_prefix=""):
    if not projetos:
        return [], ""

    PILARES_ORDER = [
        "BSW","Kaizen","Kaizen - Ganho Recorrente","Kaizen - Custo Evitado",
        "Kaizen - Capital de Giro","Redução de Custo","Redução de custo",
        "Você Resolve","Você resolve","Meta Executiva","Meta Executiva ",
        "Estratégia Comercial",
    ]

    STATUS_DISP = sorted({p["status"] for p in projetos if p["status"]})
    fc1, fc2, fc3 = st.columns([3, 2, 4])
    with fc1:
        f_status = st.multiselect("Status:", STATUS_DISP, default=[],
                                  key=f"{key_prefix}_fstatus", placeholder="Todos")
    with fc2:
        sort_col = st.selectbox("Ordenar por",
            ["Nome (A→Z)","V.Previsto ↓","V.Previsto ↑","V.Real ↓","V.Real ↑"],
            index=0, key=f"{key_prefix}_sort")
    with fc3:
        f_nome = st.text_input("🔍 Buscar projeto", value="",
                               key=f"{key_prefix}_fnome", placeholder="Filtrar por nome...")

    res = projetos[:]
    if f_status: res = [p for p in res if p["status"] in f_status]
    if f_nome:   res = [p for p in res if f_nome.lower() in p["nome"].lower()]

    sort_map = {
        "Nome (A→Z)":   (lambda p: p["nome"].lower(), False),
        "V.Previsto ↓": (lambda p: p["previsto"],     True),
        "V.Previsto ↑": (lambda p: p["previsto"],     False),
        "V.Real ↓":     (lambda p: p["real_ano"],     True),
        "V.Real ↑":     (lambda p: p["real_ano"],     False),
    }
    key_fn, rev = sort_map.get(sort_col, (lambda p: p["nome"].lower(), False))
    res = sorted(res, key=key_fn, reverse=rev)

    from collections import OrderedDict
    grupos = OrderedDict()
    for tipo in PILARES_ORDER:
        grupos[tipo] = []
    for p in res:
        t = p["tipo"]
        if t not in grupos:
            grupos[t] = []
        grupos[t].append(p)

    for tipo, projs in grupos.items():
        if not projs:
            continue
        dre_flag = is_dre(tipo)
        dre_lbl  = "✓ DRE" if dre_flag else "↷ N/DRE"
        dre_clr  = "#7BDD9A" if dre_flag else "rgba(255,255,255,.45)"
        tot_prev = sum(p["previsto"]   for p in projs)
        tot_val  = sum(p["val_saving"] for p in projs)
        tot_real = sum(p["real_ano"]   for p in projs)
        n_p      = len(projs)

        header_html = f"""<div style="background:{NAVY};border-radius:8px;
            padding:10px 16px;display:flex;align-items:center;gap:16px;margin-top:12px;">
          <div>
            <span style="color:white !important;font-size:12px;font-weight:700;">{tipo}</span>
            <span style="color:{dre_clr} !important;font-size:9px;margin-left:8px;font-weight:600;">{dre_lbl}</span>
          </div>
          <div style="margin-left:auto;display:flex;gap:28px;align-items:center;">
            <div style="text-align:center;">
              <div style="color:rgba(255,255,255,.5) !important;font-size:9px;text-transform:uppercase;letter-spacing:.5px;">Projetos</div>
              <div style="color:white !important;font-size:14px;font-weight:700;">{n_p}</div>
            </div>
            <div style="text-align:center;">
              <div style="color:rgba(255,255,255,.5) !important;font-size:9px;text-transform:uppercase;letter-spacing:.5px;">Previsto</div>
              <div style="color:#C8D8EE !important;font-size:14px;font-weight:700;">{fmt_mi(tot_prev)}</div>
            </div>
            <div style="text-align:center;">
              <div style="color:rgba(255,255,255,.5) !important;font-size:9px;text-transform:uppercase;letter-spacing:.5px;">Validado</div>
              <div style="color:#7BDD9A !important;font-size:14px;font-weight:700;">{fmt_mi(tot_val)}</div>
            </div>
            <div style="text-align:center;">
              <div style="color:rgba(255,255,255,.5) !important;font-size:9px;text-transform:uppercase;letter-spacing:.5px;">Real Acum.</div>
              <div style="color:#7BDD9A !important;font-size:14px;font-weight:700;">{fmt_mi(tot_real)}</div>
            </div>
          </div>
        </div>"""

        st.markdown(header_html, unsafe_allow_html=True)

        with st.expander("", expanded=True):
            col_headers = "".join(
                f'<th style="padding:8px 12px;text-align:left;font-size:10px;font-weight:600;'
                f'color:{SILVER} !important;text-transform:uppercase;letter-spacing:.4px;background:#F4F6F9 !important;">{c}</th>'
                for c in ["Projeto","Responsável","Término","Previsto (R$)","Saving Validado",
                          "Real Acum.","Custos","Status","Onde Parado","Prev.Lib."]
            )
            rows = ""
            for p in projs:
                real_v = p["real_ano"]
                real_s = fmt_brl(real_v) if real_v and real_v != 0 else "—"
                rc     = GREEN if real_v > 0 else ("#DC3545" if real_v < 0 else "#999")
                concluido = "Concluído" in str(p.get("status",""))
                onde  = p.get("onde_parado","")
                dlib  = p.get("data_lib","")
                onde_html = f'<span style="font-size:10px;color:#555555 !important;">{onde}</span>' if (onde and not concluido) else '<span style="color:#ccc;font-size:10px;">—</span>'
                data_html = f'<span style="font-size:10px;color:{AMBER} !important;font-weight:600;">{dlib}</span>' if (dlib and not concluido) else '<span style="color:#ccc;font-size:10px;">—</span>'

                termo_str = str(p.get("termino","")).strip()
                atrasado = False
                if not concluido and termo_str and termo_str != "—":
                    try:
                        termo_dt = datetime.datetime.strptime(termo_str[:7], "%m/%Y")
                        hoje = datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                        if termo_dt < hoje:
                            atrasado = True
                    except:
                        pass

                row_style = "border-bottom:1px solid #EEF0F3; background:white !important; color:#1C2B4A !important;" + ("background:#FFF5F5 !important;" if atrasado else "")
                txt_style = "color:#C8202E !important;" if atrasado else "color:#1C2B4A !important;"

                rows += f"""<tr style="{row_style}">
                  <td style="padding:8px 12px;font-size:11px;{txt_style}"><b>{p['nome']}</b></td>
                  <td style="padding:8px 12px;font-size:11px;white-space:nowrap;{txt_style}">{p['resp']}</td>
                  <td style="padding:8px 12px;font-size:11px;white-space:nowrap;{txt_style}">{p['termino']}</td>
                  <td style="padding:8px 12px;text-align:right;font-size:11px;{txt_style}">{fmt_brl(p['previsto'])}</td>
                  <td style="padding:8px 12px;text-align:right;font-size:11px;color:{TEAL} !important;">{fmt_brl(p['val_saving'])}</td>
                  <td style="padding:8px 12px;text-align:right;font-size:11px;color:{rc} !important;font-weight:600;">{real_s}</td>
                  <td style="padding:8px 12px;">{bdg_custos(p['val_custos'])}</td>
                  <td style="padding:8px 12px;white-space:nowrap;">{bdg_st(p['status'])}</td>
                  <td style="padding:8px 12px;">{onde_html}</td>
                  <td style="padding:8px 12px;">{data_html}</td>
                </tr>"""

            st.markdown(
                f'<table style="width:100%;border-collapse:collapse;font-size:12px;background:white !important;">'
                f'<thead><tr>{col_headers}</tr></thead>'
                f'<tbody>{rows}</tbody></table>',
                unsafe_allow_html=True
            )

    tot_all_prev = sum(p["previsto"]   for p in res) if res else 0
    tot_all_val  = sum(p["val_saving"] for p in res) if res else 0
    tot_all_real = sum(p["real_ano"]   for p in res) if res else 0
    n_all        = len(res)
    st.markdown(f"""<div style="background:{NAVY};border-radius:8px;
        padding:10px 16px;display:flex;align-items:center;gap:16px;margin-top:16px;
        border:2px solid rgba(255,255,255,.12);">
      <span style="color:white !important;font-size:12px;font-weight:700;letter-spacing:.3px;">TOTAL</span>
      <div style="margin-left:auto;display:flex;gap:28px;align-items:center;">
        <div style="text-align:center;">
          <div style="color:rgba(255,255,255,.5) !important;font-size:9px;text-transform:uppercase;letter-spacing:.5px;">Projetos</div>
          <div style="color:white !important;font-size:14px;font-weight:700;">{n_all}</div>
        </div>
        <div style="text-align:center;">
          <div style="color:rgba(255,255,255,.5) !important;font-size:9px;text-transform:uppercase;letter-spacing:.5px;">Previsto</div>
          <div style="color:#C8D8EE !important;font-size:14px;font-weight:700;">{fmt_mi(tot_all_prev)}</div>
        </div>
        <div style="text-align:center;">
          <div style="color:rgba(255,255,255,.5) !important;font-size:9px;text-transform:uppercase;letter-spacing:.5px;">Validado</div>
          <div style="color:#7BDD9A !important;font-size:14px;font-weight:700;">{fmt_mi(tot_all_val)}</div>
        </div>
        <div style="text-align:center;">
          <div style="color:rgba(255,255,255,.5) !important;font-size:9px;text-transform:uppercase;letter-spacing:.5px;">Real Acum.</div>
          <div style="color:#7BDD9A !important;font-size:14px;font-weight:700;">{fmt_mi(tot_all_real)}</div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    return res, ""

def proj_table_html(projetos):
    if not projetos:
        return "<p style='color:#999;font-size:12px;padding:6px 0;'>Nenhum projeto encontrado.</p>"
    rows = ""
    for p in projetos:
        real_v = p["real_ano"]
        real_s = fmt_brl(real_v) if real_v and real_v != 0 else "—"
        real_c = GREEN if real_v and real_v > 0 else "#999"

        dre_icon = (f'<span title="Entra no DRE" style="color:{GREEN} !important;font-size:9px;">✓ DRE</span>'
                    if p["entra_dre"] else
                    f'<span title="Não entra no DRE" style="color:{SILVER} !important;font-size:9px;">↷ N/DRE</span>')

        concluido = "Concluído" in str(p.get("status",""))
        onde = p.get("onde_parado","")
        data_lib = p.get("data_lib","")
        if concluido:
            onde_html = '<span style="color:#ccc;font-size:10px;">—</span>'
            data_html = '<span style="color:#ccc;font-size:10px;">—</span>'
        else:
            onde_html = (f'<span style="font-size:10px;color:#555555 !important;">{onde}</span>' if onde
                         else '<span style="color:#ccc;font-size:10px;">—</span>')
            data_html = (f'<span style="font-size:10px;color:{AMBER} !important;font-weight:600;">{data_lib}</span>' if data_lib
                         else '<span style="color:#ccc;font-size:10px;">—</span>')

        rows += f"""<tr style="background:white !important; color:#1C2B4A !important;">
          <td style="white-space:nowrap;">{bdg_tipo(p['tipo'])}<br>{dre_icon}</td>
          <td style="max-width:220px;font-size:11px;color:#1C2B4A !important;"><b>{p['nome']}</b></td>
          <td style="font-size:11px;white-space:nowrap;color:#1C2B4A !important;">{p['resp']}</td>
          <td style="font-size:11px;white-space:nowrap;color:#1C2B4A !important;">{p['termino']}</td>
          <td style="text-align:right;font-size:11px;color:#1C2B4A !important;">{fmt_brl(p['previsto'])}</td>
          <td style="text-align:right;font-size:11px;color:{TEAL} !important;">{fmt_brl(p['val_saving'])}</td>
          <td style="text-align:right;font-size:11px;color:{real_c} !important;font-weight:600;">{real_s}</td>
          <td>{bdg_custos(p['val_custos'])}</td>
          <td style="white-space:nowrap;">{bdg_st(p['status'])}</td>
          <td style="max-width:160px;">{onde_html}</td>
          <td style="white-space:nowrap;">{data_html}</td>
        </tr>"""
    return (th("Tipo","Projeto","Responsável","Término",
               "Previsto (R$)","Saving Validado","Real Acum.","Custos","Status",
               "Onde Parado","Previsão Lib.")
            + rows + "</tbody></table>")

def pilar_resumo_html(projetos):
    pilares = extract_pilares_local(projetos)
    if not pilares: return ""
    rows = ""
    for p in pilares:
        dot_color = GREEN if p["dre"] else SILVER
        dre_txt   = "✓ DRE" if p["dre"] else "↷ N/DRE"
        dre_style = f"color:{GREEN} !important;font-size:9px;" if p["dre"] else f"color:{SILVER} !important;font-size:9px;"
        real_c = GREEN if p["real"] > 0 else SILVER
        rows += f"""<tr style="background:white !important; color:#1C2B4A !important;">
          <td style="font-size:11px;max-width:120px;color:#1C2B4A !important;">
            <b>{p['nome']}</b><br>
            <span style="{dre_style}">{dre_txt}</span>
          </td>
          <td style="text-align:center;font-size:11px;font-weight:700;color:{NAVY} !important;">{p['qtd']}</td>
          <td style="text-align:right;font-size:11px;color:#1C2B4A !important;">{fmt_mi(p['prev'])}</td>
          <td style="text-align:right;font-size:11px;color:{real_c} !important;font-weight:600;">{fmt_mi(p['real'])}</td>
        </tr>"""
    tot_qtd  = sum(p["qtd"]  for p in pilares)
    tot_prev = sum(p["prev"] for p in pilares)
    tot_real = sum(p["real"] for p in pilares)
    real_c_tot = GREEN if tot_real > 0 else ("#DC3545" if tot_real < 0 else SILVER)
    rows += f"""<tr class="tr-tot">
      <td style="font-size:11px;color:#1C2B4A !important;">TOTAL</td>
      <td style="text-align:center;font-size:11px;color:#1C2B4A !important;">{tot_qtd}</td>
      <td style="text-align:right;font-size:11px;color:#1C2B4A !important;">{fmt_mi(tot_prev)}</td>
      <td style="text-align:right;font-size:11px;color:{real_c_tot} !important;font-weight:700;">{fmt_mi(tot_real)}</td>
    </tr>"""
    return (th("Pilar","Qtd","Saving (R$)","Real Acum.") + rows + "</tbody></table>")

# Cabeçalho macro-tabela
MC_WIDTHS = ["16%","8%","8%","9%","9%","9%","8%","7%","6%"]

def render_macro_table(items, show_expander_fn=None):
    col_names = [
        "Unidade / Área",
        "Meta 2026",
        "Retorno Previsto (12M)",
        f'<span style="color:{AMBER} !important">Previsto 2026</span>',
        f'<span style="color:{TEAL} !important">Retorno Validado 2026</span>',
        f'<span style="color:{GREEN} !important">Retorno Real 2026</span>',
        f'<span style="color:#9B59B6 !important">Extra DRE</span>',
        "% Meta","Status"
    ]
    ths = "".join(
        f'<th style="background:{NAVY} !important;color:white !important;padding:10px 12px;'
        f'font-size:11px;font-weight:600;width:{w};text-align:left;">{c}</th>'
        for c,w in zip(col_names, MC_WIDTHS)
    )
    html = f'<table style="width:100%;border-collapse:collapse;table-layout:fixed;font-size:12px;background:white !important;"><thead><tr>{ths}</tr></thead><tbody>'

    for it in items:
        html += f"""<tr style="border-bottom:1px solid #EEF0F3; background:white !important; color:#1C2B4A !important;">
          <td style="padding:10px 12px;font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#1C2B4A !important;">{it['nome']}</td>
          <td style="padding:10px 12px;color:#1C2B4A !important;">{fmt_brl(it['meta'])}</td>
          <td style="padding:10px 12px;color:#F39C12 !important;">{fmt_brl(it.get('prev',0))}</td>
          <td style="padding:10px 12px;color:{AMBER} !important;">{fmt_brl(it.get('prev2026',0))}</td>
          <td style="padding:10px 12px;color:{TEAL} !important;">{fmt_brl(it['val'])}</td>
          <td style="padding:10px 12px;color:{GREEN} !important;font-weight:600;">{fmt_brl(it['real'])}</td>
          <td style="padding:10px 12px;color:#9B59B6 !important;">{fmt_brl(it.get('extra',0))}</td>
          <td style="padding:10px 12px;">{pbar_html(it['pct'])}</td>
          <td style="padding:10px 12px;">{bdg_status(it['pct'])}</td>
        </tr>"""

    tm=tp=tp26=tv=tr=te=0
    for it in items:
        tm+=it["meta"];tp+=it.get("prev",0);tp26+=it.get("prev2026",0)
        tv+=it["val"];tr+=it["real"];te+=it.get("extra",0)
    pt = tr/tm if tm>0 else 0
    html += f"""<tr style="background:{LIGHT} !important;border-top:2px solid {NAVY};font-weight:700;color:#1C2B4A !important;">
      <td style="padding:10px 12px;color:#1C2B4A !important;">TOTAL</td>
      <td style="padding:10px 12px;color:#1C2B4A !important;">{fmt_brl(tm)}</td>
      <td style="padding:10px 12px;color:#F39C12 !important;">{fmt_brl(tp)}</td>
      <td style="padding:10px 12px;color:{AMBER} !important;">{fmt_brl(tp26)}</td>
      <td style="padding:10px 12px;color:{TEAL} !important;">{fmt_brl(tv)}</td>
      <td style="padding:10px 12px;color:{GREEN} !important;">{fmt_brl(tr)}</td>
      <td style="padding:10px 12px;color:#9B59B6 !important;">{fmt_brl(te)}</td>
      <td style="padding:10px 12px;">{pbar_html(pt)}</td>
      <td style="padding:10px 12px;"></td>
    </tr>"""
    html += "</tbody></table>"
    return html

def mc_header(): return ""
def mc_row(it): return ""
def mc_total(items): return ""

# ── HELPERS DE SEÇÃO MINIMIZÁVEL ─────────────────────────────────────────────
def section_open(key, title, default_open=True, accent_color=None):
    sk = f"sec_{key}"
    if sk not in st.session_state:
        st.session_state[sk] = default_open
    is_open = st.session_state[sk]
    icon = "−" if is_open else "+"
    ac = accent_color or RED
    col_t, col_b = st.columns([11, 1])
    with col_t:
        st.markdown(f'<span class="st" style="border-bottom-color:{ac};">{title}</span>',
                    unsafe_allow_html=True)
    with col_b:
        if st.button(icon, key=f"btn_{key}", help="Expandir / Minimizar"):
            st.session_state[sk] = not is_open
            st.rerun()
    return st.session_state[sk]

def paired_section_open(key, title_left, title_right, default_open=True, accent_color=None):
    sk = f"sec_{key}"
    if sk not in st.session_state:
        st.session_state[sk] = default_open
    is_open = st.session_state[sk]
    icon = "−" if is_open else "+"
    ac = accent_color or RED
    c1, c2, c3 = st.columns([5, 5, 1])
    with c1:
        st.markdown(f'<span class="st" style="border-bottom-color:{ac};">{title_left}</span>',
                    unsafe_allow_html=True)
    with c2:
        st.markdown(f'<span class="st" style="border-bottom-color:{ac};">{title_right}</span>',
                    unsafe_allow_html=True)
    with c3:
        if st.button(icon, key=f"btn_{key}", help="Expandir / Minimizar"):
            st.session_state[sk] = not is_open
            st.rerun()
    return st.session_state[sk]

# ═══════════════════════════════════════════════════════════════════════════════
# INTERFACE PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

# HEADER
st.markdown(f"""<div class="dh">
  <img src="https://grupodelga.com.br/wp-content/uploads/2024/11/logo-fa-e-clientes-grupo-whatsapp-9-300x300.png"
       onerror="this.style.display='none'">
  <div class="dh-t">
    <h1>Dashboard Executivo — Grupo Delga 2026</h1>
    <p>Gestão Estratégica de Projetos e Redução de Custos</p>
  </div>
  <div class="dh-b"><span class="lbl">Atualizado em</span>{datetime.datetime.now().strftime("%d/%m/%Y")}</div>
</div>""", unsafe_allow_html=True)

# ADMIN UPLOAD
with st.expander("🔐 Administrador — Atualizar Planilha"):
    arquivo = st.file_uploader("Nova versão (.xlsx)", type=["xlsx"], key="up")
    if arquivo:
        b = arquivo.read(); save_bytes(b)
        st.cache_data.clear()
        for k in list(st.session_state.keys()):
            if k.startswith("_cache_"): del st.session_state[k]
        st.success("✅ Planilha atualizada! Todos os usuários verão os novos dados.")

# CARGA
fb = load_bytes()
if fb is None:
    st.warning("⚠️ Nenhuma planilha carregada. Expanda o painel Administrador para fazer o upload.")
    st.stop()
try:
    D = load_data(fb)
except Exception as e:
    st.error(f"Erro ao processar planilha: {e}"); st.stop()

# EXTRAÇÃO
kpis    = extract_kpis(D)
plantas = extract_plantas(D)
areas   = extract_areas(D)
p_glob  = extract_pilares_global(D)
ev      = extract_evolucao(D)
ranking = extract_ranking(D)

meta=kpis["meta"]; portfolio=kpis["portfolio"]; prev2026=kpis["prev2026"]
validado=kpis["validado"]; real=kpis["real"]; extra_dre=kpis.get("extra_dre",0.0); pct_ating=kpis["pct_ating"]

# ── KPI CARDS ──────────────────────────────────────────────────────────────────
cob = portfolio/meta*100 if meta>0 else 0
pp  = prev2026/portfolio*100 if portfolio>0 else 0
pv  = validado/prev2026*100 if prev2026>0 else 0

def kpi(cls,lbl,vb,sub,det):
    return (f'<div class="kpi-card {cls}"><div class="kpi-l">{lbl}</div>'
            f'<div class="kpi-v">{vb}</div><div class="kpi-s">{sub}</div>'
            f'<div class="kpi-d">{det}</div></div>')

st.markdown(f"""<div class="kpi-wrap kpi-6">
  {kpi("","Meta Anual do Grupo (2026)",fmt_mi(meta),"","Objetivo 2026 — 100%")}
  {kpi("cs","Portfólio Previsto (Anualizado)",fmt_mi(portfolio),"",f"{cob:.1f}% da meta coberta")}
  {kpi("ca","Previsto 2026",fmt_mi(prev2026),"",f"{pp:.1f}% do portfólio total")}
  {kpi("","Validado por Custos (2026)",fmt_mi(validado),"",f"{pv:.1f}% do Previsto 2026")}
  {kpi("cg","Retorno Real (DRE) (2026)",fmt_mi(real),"",f"{pct_ating*100:.1f}% de atingimento")}
  {kpi("cr","Extra DRE (Até o Momento)",fmt_mi(extra_dre),"","Ganho fora do DRE acumulado")}
</div>""", unsafe_allow_html=True)

st.markdown(f"""<div class="nota">
  <b>Metodologia:</b>&nbsp;
  <b style="color:{GREEN} !important;">✓ DRE</b>: BSW · Kaizen · Kaizen GR · Redução de Custo · Você Resolve — impacto direto e mensurável no DRE.&nbsp;
  <b style="color:{SILVER} !important;">↷ Não DRE</b>: Kaizen Custo Evitado · Kaizen Capital de Giro · Meta Executiva — geram valor operacional mas não reduzem GGF no DRE.
</div>""", unsafe_allow_html=True)

# ── EVOLUÇÃO ───────────────────────────────────────────────────────────────────
st.markdown('<div class="sc">', unsafe_allow_html=True)
is_ev = section_open("evolucao", "Evolução Mensal — Acumulado Previsto vs Real vs Meta")
if is_ev:
    series_all = ["Acumulado Previsto","Acumulado Real","Projeção da Meta","Previsto Mensal","Real Mensal"]
    sel = st.multiselect("Séries:", series_all,
                         default=["Acumulado Previsto","Acumulado Real","Projeção da Meta",
                                  "Previsto Mensal","Real Mensal"],
                         key="ev_sel")
    if sel:
        st.plotly_chart(chart_evolucao(ev,sel), use_container_width=True, config={"displayModeBar":False})
st.markdown('</div>', unsafe_allow_html=True)

# ── FUNIL + GAUGE — botão único para o par ─────────────────────────────────────
is_fg = paired_section_open("funil_gauge",
                             "Funil de Conversão — Portfólio → DRE",
                             "Atingimento da Meta")
cfu, cga = st.columns([3, 2])
with cfu:
    st.markdown('<div class="sc" style="min-height:60px;">', unsafe_allow_html=True)
    if is_fg:
        st.markdown(f'<p style="font-size:11px;color:{SILVER} !important;margin-bottom:8px;">Quanto do portfólio mapeado converte em resultado no DRE?</p>', unsafe_allow_html=True)
        st.plotly_chart(chart_funnel(kpis), use_container_width=True, config={"displayModeBar":False})
    st.markdown('</div>', unsafe_allow_html=True)
with cga:
    st.markdown('<div class="sc" style="min-height:60px;">', unsafe_allow_html=True)
    if is_fg:
        st.plotly_chart(chart_gauge(pct_ating), use_container_width=True, config={"displayModeBar":False})
        gap_val = meta - real
        st.markdown(f"""<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:4px;">
          <div style="background:{LIGHT} !important;border-radius:8px;padding:12px;text-align:center;">
            <div style="font-size:9px;font-weight:600;color:{SILVER} !important;text-transform:uppercase;letter-spacing:.5px;margin-bottom:4px;">GAP para Meta</div>
            <div style="font-size:16px;font-weight:700;color:{RED} !important;">{fmt_mi(gap_val)}</div>
          </div>
          <div style="background:{LIGHT} !important;border-radius:8px;padding:12px;text-align:center;">
            <div style="font-size:9px;font-weight:600;color:{SILVER} !important;text-transform:uppercase;letter-spacing:.5px;margin-bottom:4px;">Validado / Meta</div>
            <div style="font-size:16px;font-weight:700;color:{NAVY} !important;">{validado/meta*100:.1f}%</div>
          </div>
        </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── DONUTS — botão único para o par ────────────────────────────────────────────
is_dn = paired_section_open("donuts",
                             "Representatividade — Plantas",
                             "Representatividade — Áreas Funcionais")
cd1, cd2 = st.columns(2)
with cd1:
    st.markdown('<div class="sc" style="min-height:60px;">', unsafe_allow_html=True)
    if is_dn:
        st.plotly_chart(chart_donut([p["nome"] for p in plantas],[p["meta"] for p in plantas],PAL),
                        use_container_width=True, config={"displayModeBar":False})
    st.markdown('</div>', unsafe_allow_html=True)
with cd2:
    st.markdown('<div class="sc" style="min-height:60px;">', unsafe_allow_html=True)
    if is_dn:
        st.plotly_chart(chart_donut([a["nome"] for a in areas],[a["meta"] for a in areas],
                                    [NAVY,GREEN,"#20C997"]),
                        use_container_width=True, config={"displayModeBar":False})
    st.markdown('</div>', unsafe_allow_html=True)

# ── PILARES ────────────────────────────────────────────────────────────────────
st.markdown('<div class="sc">', unsafe_allow_html=True)
is_pil = section_open("pilares", "Distribuição por Tipo de Iniciativa — Grupo")

def chart_pilares_gerencial(pilares_global, real_total, show_prev, show_val, show_real):
    labels   = [p["nome"] for p in pilares_global]
    previsto = [p["prev"] for p in pilares_global]
    validado_l = [p["val"] for p in pilares_global]
    real_est = [p.get("real", 0) for p in pilares_global]
    if all(v == 0 for v in real_est):
        tv = sum(validado_l)
        real_est = [v/tv*real_total if tv>0 else 0 for v in validado_l]
    series = []
    if show_prev: series.append(dict(name="Previsto",  x=previsto,    color="#C8D8EE"))
    if show_val:  series.append(dict(name="Validado",  x=validado_l,  color=NAVY))
    if show_real: series.append(dict(name="Real DRE",  x=real_est,    color=GREEN))
    if not series: return None
    fig = go.Figure()
    for s in series:
        fig.add_trace(go.Bar(
            name=s["name"], y=labels, x=s["x"], orientation="h",
            marker=dict(color=s["color"], line=dict(width=0)),
            text=[fmt_mi(v) for v in s["x"]],
            textposition="outside", textfont=dict(size=10, color="#1C2B4A"),
            hovertemplate=f"<b>%{{y}}</b><br>{s['name']}: R$ %{{x:,.0f}}<extra></extra>",
        ))
    fig.update_layout(
        barmode="group",
        xaxis=dict(tickformat=",.0f", showgrid=True, gridcolor="#F0F4F8",
                   tickprefix="R$ ", zeroline=False, tickfont=dict(color="#1C2B4A")),
        yaxis=dict(autorange="reversed", tickfont=dict(size=12, color="#1C2B4A"),
                   gridcolor="#F0F4F8"),
        legend=dict(orientation="h", y=1.06, x=0.5, xanchor="center",
                    font=dict(size=12, color="#1C2B4A"), bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=160, r=100, t=44, b=20),
        height=max(220, len(labels)*62),
        paper_bgcolor="white", plot_bgcolor="white",
        bargap=0.35, bargroupgap=0.06,
        font=dict(family="Inter", color="#1C2B4A"),
    )
    return fig

@st.cache_data(show_spinner=False)
def build_pilares_grupo(fb_key):
    NAO_DRE_PIL = {"Kaizen - Custo Evitado","Kaizen - Capital de Giro",
                   "Meta Executiva","Meta Executiva "}
    df = D["u5"]
    res = []
    for ri in range(12, 21):
        nome = str(df.iloc[ri,3]).strip() if pd.notna(df.iloc[ri,3]) else ""
        if not nome or nome in ("TOTAL",""):
            continue
        qtd  = int(safe(df.iloc[ri,4]))
        prev = safe(df.iloc[ri,5])
        val  = safe(df.iloc[ri,6])
        real = safe(df.iloc[ri,7])
        dre  = nome not in NAO_DRE_PIL
        res.append(dict(nome=nome.strip(), qtd=qtd, prev=prev,
                        val=val, real=real, dre=dre))
    return res

if is_pil:
    cp1, cp2 = st.columns([5, 4])
    with cp1:
        _t1, _t2, _t3, _tsp = st.columns([2, 2, 2, 3])
        with _t1: show_prev = st.toggle("Previsto",  value=True,  key="tog_prev")
        with _t2: show_val  = st.toggle("Validado",  value=True,  key="tog_val")
        with _t3: show_real = st.toggle("Real DRE",  value=False, key="tog_real")
        p_grupo = build_pilares_grupo(hash(fb))
        fig_pil = chart_pilares_gerencial(p_grupo, real, show_prev, show_val, show_real)
        if fig_pil:
            st.plotly_chart(fig_pil, use_container_width=True, config={"displayModeBar":False})
        else:
            st.info("Selecione ao menos uma série.")
    with cp2:
        st.markdown(f'<p class="st" style="border-bottom-color:{RED};">Resumo por Pilar — Grupo</p>',
                    unsafe_allow_html=True)
        rows_p = ""
        for p in p_grupo:
            dre_s = f"color:{GREEN} !important;font-size:9px;font-weight:600;" if p["dre"] else f"color:{SILVER} !important;font-size:9px;"
            dre_t = "✓ DRE" if p["dre"] else "↷ N/DRE"
            rows_p += f"""<tr style="background:white !important; color:#1C2B4A !important;">
              <td style="font-size:11px;font-weight:600;color:#1C2B4A !important;">{p['nome']}<br>
                <span style="{dre_s}">{dre_t}</span></td>
              <td style="text-align:center;font-size:11px;font-weight:700;color:#1C2B4A !important;">{p['qtd']}</td>
              <td style="text-align:right;font-size:11px;color:#1C2B4A !important;">{fmt_mi(p['prev'])}</td>
              <td style="text-align:right;font-size:11px;color:{TEAL} !important;font-weight:600;">{fmt_mi(p['val'])}</td>
              <td style="text-align:right;font-size:11px;color:{GREEN} !important;font-weight:600;">{fmt_mi(p['real'])}</td>
            </tr>"""
        tot_qtd_g=sum(p["qtd"] for p in p_grupo)
        tot_prev_g=sum(p["prev"] for p in p_grupo)
        tot_val_g=sum(p["val"] for p in p_grupo)
        tot_real_g=sum(p["real"] for p in p_grupo)
        rows_p += f"""<tr class="tr-tot">
          <td style="font-size:11px;color:#1C2B4A !important;">TOTAL</td>
          <td style="text-align:center;font-size:11px;color:#1C2B4A !important;">{tot_qtd_g}</td>
          <td style="text-align:right;font-size:11px;color:#1C2B4A !important;">{fmt_mi(tot_prev_g)}</td>
          <td style="text-align:right;font-size:11px;color:{TEAL} !important;">{fmt_mi(tot_val_g)}</td>
          <td style="text-align:right;font-size:11px;color:{GREEN} !important;">{fmt_mi(tot_real_g)}</td>
        </tr>"""
        st.markdown(th("Pilar","Qtd","Saving (R$)","Saving Validado","Até o Momento")+rows_p+"</tbody></table>",
                    unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PLANTAS INDUSTRIAIS
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown('<div class="sc">', unsafe_allow_html=True)
is_plantas = section_open("plantas", "Plantas Industriais — Performance Consolidada")
if is_plantas:
    st.markdown(render_macro_table(plantas), unsafe_allow_html=True)

for p in plantas:
    if not is_plantas:
        break
    with st.expander(f"＋  Ver projetos de {p['nome']}", expanded=False):
        proj = get_proj_planta(D, p["sheet"])
        n = len(proj)
        if proj:
            proj_v, pilar_html = projetos_por_pilar_html(proj, key_prefix=f"plt_{p['nome']}")
            st.markdown(f"<p style='font-size:11px;color:{SILVER} !important;margin:4px 0 8px;'>"
                        f"<b>{len(proj_v)}</b> de {n} projetos</p>", unsafe_allow_html=True)
            st.markdown(pilar_html, unsafe_allow_html=True)
        else:
            st.markdown("<p style='color:#999;font-size:12px;'>Sem projetos.</p>",
                        unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# ÁREAS FUNCIONAIS
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sc">', unsafe_allow_html=True)
is_areas = section_open("areas", "Áreas Funcionais — Performance Consolidada")
area_fn = {"Compras": get_proj_compras, "Vendas": get_proj_vendas}
if is_areas:
    st.markdown(render_macro_table(areas), unsafe_allow_html=True)

for a in areas:
    if not is_areas:
        break
    with st.expander(f"＋  Ver projetos de {a['nome']}", expanded=False):
        fn = area_fn.get(a["nome"])
        proj = fn(D) if fn else []
        n = len(proj)
        if proj:
            proj_va, pilar_html_a = projetos_por_pilar_html(proj, key_prefix=f"area_{a['nome']}")
            st.markdown(f"<p style='font-size:11px;color:{SILVER} !important;margin:4px 0 8px;'>"
                        f"<b>{len(proj_va)}</b> de {n} projetos</p>", unsafe_allow_html=True)
            st.markdown(pilar_html_a, unsafe_allow_html=True)
        else:
            st.markdown("<p style='color:#999;font-size:12px;'>Sem projetos.</p>",
                        unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ── CLASSIFICAÇÃO DE GANHOS ────────────────────────────────────────────────────
st.markdown('<div class="sc">', unsafe_allow_html=True)
is_class = section_open("classificacao","Classificação de Ganhos — Impacto no DRE",default_open=False)
if is_class:
    cc1,cc2,cc3,cc4,cc5 = st.columns(5)
    ganhos = [
        (cc1,NAVY,   "🔵","BSW","Benchmark de peso bruto. Redução de MP — impacto direto no DRE.","✓ DRE",GREEN),
        (cc2,GREEN,  "🔥","Redução de Custo","Elimina custo direto na operação. Reduz GGF no DRE.","✓ DRE",GREEN),
        (cc3,AMBER,  "⚡","Kaizen / GR","Produtividade recorrente apurada. Entra no DRE quando validado.","✓ DRE",GREEN),
        (cc4,"#512DA8","↷","C. Evitado","MO realocada internamente — não reduz GGF no DRE.","↷ Não DRE",SILVER),
        (cc5,"#0D47A1","🏦","Cap. de Giro","Reduz estoque / melhora caixa. Impacto no balanço, não no DRE.","↷ Não DRE",SILVER),
    ]
    for col,cor,icon,titulo,texto,dre,dcor in ganhos:
        with col:
            st.markdown(f"""<div style="border:2px solid {cor};border-radius:8px;padding:12px 14px;height:100%;background:white !important;">
              <div style="font-weight:700;color:{cor} !important;margin-bottom:4px;font-size:12px;">{icon} {titulo}</div>
              <div style="font-size:10px;color:#444444 !important;line-height:1.5;margin-bottom:6px;">{texto}</div>
              <div style="font-size:10px;font-weight:700;color:{dcor} !important;">{dre}</div>
            </div>""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── RANKING ────────────────────────────────────────────────────────────────────
st.markdown('<div class="sc">', unsafe_allow_html=True)
is_rank = section_open("ranking","Ranking de Projetos — Todos os Pilares",default_open=False)
if is_rank:
    rk1,rk2,rk3 = st.columns([2,2,1])
    with rk1:
        f_uni = st.multiselect("Unidade:", sorted({r["uni"] for r in ranking}),
                               default=[], placeholder="Todas", key="rk_uni")
    with rk2:
        f_st  = st.multiselect("Status:", sorted({r["status"] for r in ranking if r["status"]}),
                               default=[], placeholder="Todos", key="rk_st")
    with rk3:
        n_lin = st.number_input("Linhas:", 5, 200, 25, 5)
    pf = ranking
    if f_uni: pf = [r for r in pf if r["uni"] in f_uni]
    if f_st:  pf  = [r for r in pf if r["status"] in f_st]
    st.markdown(f"<p style='font-size:11px;color:{SILVER} !important;margin-bottom:6px;'>"
                f"Exibindo {min(int(n_lin),len(pf))} de {len(pf)} projetos</p>",
                unsafe_allow_html=True)
    rows_rk = "".join(f"""<tr style="background:white !important; color:#1C2B4A !important;">
      <td style="text-align:center;color:{SILVER} !important;font-weight:700;font-size:11px;">{r['pos']}</td>
      <td style="font-weight:600;font-size:11px;color:#1C2B4A !important;">{r['uni']}</td>
      <td style="font-size:11px;color:#1C2B4A !important;">{r['nome']}</td>
      <td>{bdg_st(r['status'])}</td>
      <td>{bdg_custos(r['custos'])}</td>
      <td style="text-align:right;font-size:11px;color:#1C2B4A !important;">{fmt_brl(r['prev26'])}</td>
      <td style="text-align:right;font-size:11px;color:#1C2B4A !important;">{fmt_brl(r['prev_mo'])}</td>
      <td style="text-align:right;font-weight:700;color:{GREEN} !important;font-size:11px;">{fmt_brl(r['real'])}</td>
    </tr>""" for r in pf[:int(n_lin)])
    st.markdown(th("#","Unidade","Projeto","Status","Custos",
                   "Previsto 2026","Previsto Momento","Real DRE")+rows_rk+"</tbody></table>",
                unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── GAP ────────────────────────────────────────────────────────────────────────
st.markdown('<div class="sc">', unsafe_allow_html=True)
is_gap = section_open("gap","GAP — Projetos Aguardando Validação de Custos",
                      default_open=False, accent_color=AMBER)
if is_gap:
    st.markdown(f'<p style="font-size:11px;color:{SILVER} !important;margin-bottom:10px;">'
                f'Projetos com valor projetado mas ainda sem validação do depto de Custos.</p>',
                unsafe_allow_html=True)
    gap = [r for r in ranking if r["custos"] not in ("OK","Não Ok","NOK","Não OK") and r["prev26"]>0]
    by_uni = {}
    for r in gap: by_uni[r["uni"]] = by_uni.get(r["uni"],0)+r["prev26"]
    tot_gap = sum(by_uni.values()) if by_uni else 0
    rows_gap = "".join(f"""<tr style="background:white !important; color:#1C2B4A !important;">
      <td style="font-weight:600;color:#1C2B4A !important;">{u}</td>
      <td style="text-align:right;color:{AMBER} !important;font-weight:600;">{fmt_brl(v)}</td>
      <td style="text-align:right;color:#1C2B4A !important;">{v/tot_gap*100:.1f}%</td>
    </tr>""" for u,v in sorted(by_uni.items(),key=lambda x:-x[1]))
    rows_gap += f"""<tr class="tr-tot">
      <td style="color:#1C2B4A !important;">TOTAL GAP</td>
      <td style="text-align:right;color:{AMBER} !important;">{fmt_brl(tot_gap)}</td>
      <td style="text-align:right;color:#1C2B4A !important;">100%</td>
    </tr>"""
    st.markdown(f"<p style='font-size:11px;color:{SILVER} !important;'>{len(gap)} projetos aguardam validação</p>",
                unsafe_allow_html=True)
    st.markdown(th("Unidade",f'<span style="color:{AMBER} !important">Previsto 2026 (não validado)</span>',
                   "% do Gap")+rows_gap+"</tbody></table>",
                unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── FOOTER ─────────────────────────────────────────────────────────────────────
st.markdown(f"""<div style="text-align:center;padding:16px 0;border-top:1px solid #EEF0F3;margin-top:8px;">
  <span style="font-size:11px;color:{SILVER} !important;">
    Dashboard Executivo · Grupo Delga 2026 · Gestão Estratégica de Projetos e Redução de Custos
  </span>
</div>""", unsafe_allow_html=True)
_,cft = st.columns([5,1])
with cft:
    if st.button("🚪 Sair", key="logout"):
        st.session_state["auth"]=False; st.rerun()
