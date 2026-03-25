import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from io import BytesIO

st.set_page_config(
    page_title="Wulff Consulting – Virksomhedsudtræk",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"], .stApp {
  font-family: 'Inter', sans-serif !important;
  background-color: #F0F4FF !important;
  color: #0F172A !important;
}

/* Navbar */
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 32px;
  background: #ffffff;
  border-bottom: 1px solid #E2E8F0;
  margin: -1rem -1rem 2rem -1rem;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.logo-wrap { display: flex; align-items: center; gap: 12px; }
.logo-box {
  width: 38px; height: 38px;
  background: #0F172A;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.logo-box span {
  color: #fff;
  font-size: 20px;
  font-weight: 800;
  font-family: Georgia, serif;
  letter-spacing: -2px;
  line-height: 1;
}
.brand-name {
  font-size: 17px;
  font-weight: 700;
  color: #0F172A;
  letter-spacing: -0.01em;
}
.brand-light { font-weight: 300; }
.badge {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #fff;
  background: #1D4ED8;
  padding: 4px 12px;
  border-radius: 20px;
}

/* Hero */
.hero {
  background: linear-gradient(130deg, #1D4ED8 0%, #1E3A8A 100%);
  border-radius: 14px;
  padding: 36px 40px;
  margin-bottom: 24px;
  color: #fff;
}
.hero-title {
  font-size: 26px;
  font-weight: 700;
  margin: 0 0 8px 0;
  letter-spacing: -0.02em;
  color: #fff;
}
.hero-sub {
  font-size: 14px;
  color: rgba(255,255,255,0.75);
  margin: 0;
}

/* Section label */
.section-label {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #64748B;
  margin-bottom: 12px;
}

/* Input */
.stTextInput > div > div > input {
  background: #fff !important;
  border: 1.5px solid #CBD5E1 !important;
  border-radius: 8px !important;
  color: #0F172A !important;
  font-size: 15px !important;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.stTextInput > div > div > input:focus {
  border-color: #1D4ED8 !important;
  box-shadow: 0 0 0 3px rgba(29,78,216,0.1) !important;
}
.stTextInput label {
  font-weight: 500 !important;
  font-size: 14px !important;
  color: #374151 !important;
}

/* Primary button */
.stButton > button[kind="primary"] {
  background: #1D4ED8 !important;
  color: #fff !important;
  border: none !important;
  border-radius: 8px !important;
  font-weight: 600 !important;
  font-size: 14px !important;
  letter-spacing: 0.01em;
  transition: background 0.15s, box-shadow 0.15s !important;
}
.stButton > button[kind="primary"]:hover {
  background: #1E40AF !important;
  box-shadow: 0 4px 14px rgba(29,78,216,0.28) !important;
}

/* Download buttons */
.stDownloadButton > button {
  background: #fff !important;
  color: #1D4ED8 !important;
  border: 1.5px solid #1D4ED8 !important;
  border-radius: 8px !important;
  font-weight: 600 !important;
  font-size: 14px !important;
  transition: background 0.15s !important;
}
.stDownloadButton > button:hover {
  background: #EFF6FF !important;
}

/* Progress */
.stProgress > div > div > div {
  background: linear-gradient(90deg, #1D4ED8, #3B82F6) !important;
  border-radius: 4px !important;
}
.stProgress > div > div {
  background: #E2E8F0 !important;
  border-radius: 4px !important;
}

/* Alerts */
div[data-testid="stAlert"] {
  border-radius: 10px !important;
  font-size: 14px !important;
}

/* Dataframe */
.stDataFrame {
  border-radius: 10px !important;
  overflow: hidden !important;
  border: 1px solid #E2E8F0 !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
  background: #fff !important;
  border-right: 1px solid #E2E8F0 !important;
}
[data-testid="stSidebar"] * { color: #374151 !important; }
[data-testid="stSidebar"] .stSlider > div > div > div { background: #1D4ED8 !important; }

/* Metric boxes */
.metrics {
  display: flex;
  gap: 14px;
  margin: 20px 0;
}
.metric-box {
  flex: 1;
  background: #fff;
  border: 1px solid #E2E8F0;
  border-top: 3px solid #1D4ED8;
  border-radius: 10px;
  padding: 16px 20px;
}
.metric-label {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #64748B;
  margin-bottom: 6px;
}
.metric-value {
  font-size: 24px;
  font-weight: 700;
  color: #0F172A;
  letter-spacing: -0.02em;
}

/* Footer */
.footer {
  text-align: center;
  padding: 24px 0 8px;
  font-size: 12px;
  color: #94A3B8;
  border-top: 1px solid #E2E8F0;
  margin-top: 40px;
}

#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Navbar ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="navbar">'
      '<div class="logo-wrap">'
        '<div class="logo-box"><span>W</span></div>'
        '<div class="brand-name">Wulff <span class="brand-light">Consulting</span></div>'
      '</div>'
      '<div class="badge">Internt v&aelig;rkt&oslash;j</div>'
    '</div>',
    unsafe_allow_html=True
)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="hero">'
      '<div class="hero-title">Virksomhedsudtr&aelig;k</div>'
      '<div class="hero-sub">Hent virksomhedsdata fra proff.dk baseret p&aring; en NACE-branchekode og eksporter til Excel med &eacute;t klik.</div>'
    '</div>',
    unsafe_allow_html=True
)

# ── Hardcoded delays ──────────────────────────────────────────────────────────
delay_min = 1.2
delay_max = 2.5

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Indstillinger")
    st.markdown("---")
    max_pages = st.slider(
        "Maks. antal sider",
        min_value=1, max_value=1000, value=50,
        help="Hver side indeholder ca. 20 virksomheder."
    )
    estimat = max_pages * 20
    st.markdown(
        f'<div style="background:#EFF6FF;border-radius:8px;padding:12px 14px;'
        f'margin-top:4px;border-left:3px solid #1D4ED8;">'
        f'<div style="font-size:11px;color:#1D4ED8;font-weight:600;margin-bottom:4px;">ESTIMAT</div>'
        f'<div style="font-size:13px;color:#1E3A8A;">Op til <b>{estimat:,}</b> virksomheder</div>'
        f'</div>',
        unsafe_allow_html=True
    )
    st.markdown("---")
    st.markdown(
        '<div style="font-size:12px;color:#94A3B8;line-height:1.7;">'
        'Data hentes fra proff.dk.<br>'
        'Udtræk med mange sider kan tage flere minutter.'
        '</div>',
        unsafe_allow_html=True
    )
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:11px;color:#CBD5E1;text-align:center;letter-spacing:0.06em;">'
        'WULFF CONSULTING &copy; 2025'
        '</div>',
        unsafe_allow_html=True
    )

# ── Input ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">S&oslash;geparametre</div>', unsafe_allow_html=True)

col_input, col_btn = st.columns([3, 1])
with col_input:
    nace_input = st.text_input(
        "Branchekode (NACE)",
        value="47.55",
        placeholder="F.eks. 47.55 eller 62.01",
        help="Find din kode på proff.dk/segmentering"
    )
with col_btn:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    start_btn = st.button("Start udtræk", type="primary", use_container_width=True)

# ── Scraping ──────────────────────────────────────────────────────────────────
REQ_HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def scrape_page(page: int, nace: str) -> tuple[list[dict], bool]:
    url = (
        f"https://www.proff.dk/segmentering?sort=profitDesc&naceIndustry={nace}"
        if page == 1
        else f"https://www.proff.dk/segmentering?page={page}&naceIndustry={nace}&sort=profitDesc"
    )
    try:
        resp = requests.get(url, headers=REQ_HEADERS, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        st.warning(f"Netværksfejl side {page}: {e}")
        return [], False

    soup = BeautifulSoup(resp.content, "html.parser")
    blocks = soup.select('div[class*="SegmentationSearchResultCard-card"]')
    if not blocks:
        return [], False

    rows = []
    for block in blocks:
        try:
            name_tag = block.select_one("h2 a")
            name = name_tag.text.strip() if name_tag else ""

            cvr = ""
            cvr_cont = block.find("span", class_="CardHeader-propertyList")
            if cvr_cont:
                for part in cvr_cont.get_text(separator=" ", strip=True).split():
                    if part.isdigit() and len(part) == 8:
                        cvr = part
                        break
            if not cvr:
                continue

            postal = ""
            loc = block.find("svg", {"data-icon": "location-dot"})
            if loc:
                p = loc.find_parent("span")
                if p:
                    postal = p.get_text(strip=True)

            brutto = ""
            bl = block.find("div", string=lambda s: s and "Bruttofortjeneste" in s)
            if bl:
                for t in (bl.find_parent() or bl).find_all(string=True):
                    if t.strip().replace(".", "").isdigit():
                        brutto = t.strip().replace(".", "")
                        break

            ansatte = ""
            al = block.find("div", string=lambda s: s and "Antal ansatte" in s)
            if al:
                for t in (al.find_parent() or al).find_all(string=True):
                    if t.strip().replace(".", "").isdigit():
                        ansatte = t.strip().replace(".", "")
                        break

            branche = ", ".join(
                tag.text.strip() for tag in block.select("div.IndustryTags-tags a")
            )

            rows.append({
                "Navn": name,
                "CVR-nr": cvr,
                "Postnummer": postal,
                "Bruttofortjeneste": brutto,
                "Antal ansatte": ansatte,
                "Branche": branche,
            })
        except Exception:
            continue

    return rows, True


def to_excel(df: pd.DataFrame) -> bytes:
    out = BytesIO()
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Virksomheder")
        ws = writer.sheets["Virksomheder"]
        for col in ws.columns:
            max_len = max((len(str(c.value or "")) for c in col), default=10)
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 50)
    return out.getvalue()


# ── Run ───────────────────────────────────────────────────────────────────────
if start_btn:
    nace = nace_input.strip()
    if not nace:
        st.error("Indtast venligst en branchekode.")
        st.stop()

    results: list[dict] = []
    seen: set[str] = set()

    st.markdown("---")
    progress_bar = st.progress(0)
    status = st.empty()

    for page in range(1, max_pages + 1):
        status.markdown(
            f"<div style='font-size:14px;color:#374151;padding:6px 0'>"
            f"Side <b>{page}</b> / {max_pages} &nbsp;&middot;&nbsp; "
            f"<span style='color:#1D4ED8;font-weight:600'>{len(results)} virksomheder fundet</span>"
            f"</div>",
            unsafe_allow_html=True
        )
        progress_bar.progress(page / max_pages)

        rows, has_more = scrape_page(page, nace)
        new = [r for r in rows if r["CVR-nr"] not in seen]
        for r in new:
            seen.add(r["CVR-nr"])
        results.extend(new)

        if not has_more:
            progress_bar.progress(1.0)
            status.empty()
            break

        if page < max_pages:
            time.sleep(random.uniform(delay_min, delay_max))

    if results:
        df = pd.DataFrame(results)

        st.markdown(
            f'<div class="metrics">'
            f'<div class="metric-box"><div class="metric-label">Virksomheder</div><div class="metric-value">{len(df)}</div></div>'
            f'<div class="metric-box"><div class="metric-label">Sider hentet</div><div class="metric-value">{min(page, max_pages)}</div></div>'
            f'<div class="metric-box"><div class="metric-label">Branchekode</div><div class="metric-value" style="font-size:20px">{nace}</div></div>'
            f'</div>',
            unsafe_allow_html=True
        )

        st.dataframe(df, use_container_width=True, height=420)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        c1.download_button(
            "Download Excel (.xlsx)",
            data=to_excel(df),
            file_name=f"wulff_nace_{nace.replace('.','_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
        c2.download_button(
            "Download CSV",
            data=df.to_csv(index=False, sep=";", encoding="utf-8-sig"),
            file_name=f"wulff_nace_{nace.replace('.','_')}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    else:
        st.warning("Ingen virksomheder fundet. Tjek at branchekoden er korrekt.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="footer">Wulff Consulting &nbsp;&middot;&nbsp; Internt v&aelig;rkt&oslash;j &nbsp;&middot;&nbsp; Data fra proff.dk</div>',
    unsafe_allow_html=True
)
