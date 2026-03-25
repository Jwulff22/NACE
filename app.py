import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from io import BytesIO

st.set_page_config(
    page_title="Wulff Consulting – Virksomhedsudtræk",
    page_icon="https://i.imgur.com/placeholder.png",
    layout="centered",
)

# ── Brand CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* ── Google Font ── */
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

  html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
  }

  /* ── Page background ── */
  .stApp {
    background-color: #0F172A;
    color: #F8FAFC;
  }

  /* ── Header banner ── */
  .wc-header {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 28px 0 24px 0;
    border-bottom: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 32px;
  }
  .wc-logo-box {
    width: 48px;
    height: 48px;
    background: #0F172A;
    border: 2px solid #F8FAFC;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }
  .wc-logo-w {
    color: #F8FAFC;
    font-size: 26px;
    font-weight: 700;
    letter-spacing: -2px;
    font-family: Georgia, serif;
  }
  .wc-brand-text { line-height: 1.2; }
  .wc-brand-name {
    font-size: 20px;
    font-weight: 700;
    color: #F8FAFC;
    letter-spacing: 0.01em;
  }
  .wc-brand-name span { font-weight: 300; }
  .wc-brand-sub {
    font-size: 11px;
    color: rgba(248,250,252,0.45);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-top: 2px;
  }

  /* ── Section headings ── */
  h1, h2, h3 { color: #F8FAFC !important; }

  /* ── Input fields ── */
  .stTextInput > div > div > input {
    background-color: #1E293B !important;
    color: #F8FAFC !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 6px !important;
  }
  .stTextInput label { color: rgba(248,250,252,0.75) !important; }

  /* ── Primary button ── */
  .stButton > button[kind="primary"] {
    background-color: #F8FAFC !important;
    color: #0F172A !important;
    border: none !important;
    font-weight: 600 !important;
    border-radius: 6px !important;
    transition: opacity 0.15s ease;
  }
  .stButton > button[kind="primary"]:hover {
    opacity: 0.88 !important;
  }

  /* ── Download buttons ── */
  .stDownloadButton > button {
    background-color: #1E293B !important;
    color: #F8FAFC !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 6px !important;
    font-weight: 500 !important;
  }
  .stDownloadButton > button:hover {
    background-color: #273448 !important;
    border-color: rgba(255,255,255,0.3) !important;
  }

  /* ── Progress bar ── */
  .stProgress > div > div > div {
    background-color: #F8FAFC !important;
  }
  .stProgress > div > div {
    background-color: rgba(255,255,255,0.1) !important;
  }

  /* ── Info / success / warning boxes ── */
  .stAlert {
    background-color: #1E293B !important;
    border-color: rgba(255,255,255,0.12) !important;
    color: #F8FAFC !important;
    border-radius: 6px !important;
  }

  /* ── Dataframe ── */
  .stDataFrame { border-radius: 8px; overflow: hidden; }

  /* ── Sidebar ── */
  [data-testid="stSidebar"] {
    background-color: #0B1320 !important;
    border-right: 1px solid rgba(255,255,255,0.06);
  }
  [data-testid="stSidebar"] * { color: #CBD5E1 !important; }
  [data-testid="stSidebar"] h1,
  [data-testid="stSidebar"] h2,
  [data-testid="stSidebar"] h3 { color: #F8FAFC !important; }
  [data-testid="stSidebar"] .stSlider > div > div > div {
    background-color: #F8FAFC !important;
  }

  /* ── Divider ── */
  hr { border-color: rgba(255,255,255,0.08) !important; }

  /* ── Footer ── */
  .wc-footer {
    margin-top: 48px;
    padding-top: 16px;
    border-top: 1px solid rgba(255,255,255,0.06);
    text-align: center;
    font-size: 12px;
    color: rgba(248,250,252,0.3);
    letter-spacing: 0.05em;
  }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="wc-header">
  <div class="wc-logo-box">
    <span class="wc-logo-w">W</span>
  </div>
  <div class="wc-brand-text">
    <div class="wc-brand-name"><b>Wulff</b> <span>Consulting</span></div>
    <div class="wc-brand-sub">Virksomhedsudtræk</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("Hent virksomhedsdata fra **proff.dk** baseret på en branchekode (NACE) og download resultatet som Excel.")

# ── Hardcoded delay (not exposed to user) ─────────────────────────────────────
delay_min = 1.2
delay_max = 2.5

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Indstillinger")
    max_pages = st.slider("Maks. antal sider", 1, 1000, 50,
                          help="Hver side indeholder ~20 virksomheder.")
    st.markdown("---")
    st.markdown(
        '<div style="font-size:11px;color:rgba(255,255,255,0.3);letter-spacing:0.05em">'
        'WULFF CONSULTING © 2025'
        '</div>',
        unsafe_allow_html=True
    )

# ── Main input ────────────────────────────────────────────────────────────────
nace_input = st.text_input(
    "Branchekode (NACE)",
    value="47.55",
    placeholder="F.eks. 47.55 eller 62.01",
    help="Find koder på https://www.proff.dk/segmentering"
)

start_btn = st.button("▶  Start udtræk", type="primary", use_container_width=True)

# ── Scraping ──────────────────────────────────────────────────────────────────
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def scrape_page(page: int, nace: str) -> tuple[list[dict], bool]:
    if page == 1:
        url = f"https://www.proff.dk/segmentering?sort=profitDesc&naceIndustry={nace}"
    else:
        url = f"https://www.proff.dk/segmentering?page={page}&naceIndustry={nace}&sort=profitDesc"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
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

    st.info(f"Starter udtræk for NACE **{nace}** — maks. {max_pages} sider…")

    results: list[dict] = []
    seen: set[str] = set()
    progress_bar = st.progress(0)
    status = st.empty()
    preview = st.empty()

    for page in range(1, max_pages + 1):
        status.markdown(
            f"⏳ Side **{page}** / {max_pages} &nbsp;·&nbsp; **{len(results)}** virksomheder fundet"
        )
        progress_bar.progress(page / max_pages)

        rows, has_more = scrape_page(page, nace)
        new = [r for r in rows if r["CVR-nr"] not in seen]
        for r in new:
            seen.add(r["CVR-nr"])
        results.extend(new)

        if not has_more:
            status.markdown(f"✅ Færdig — **{len(results)}** virksomheder hentet.")
            progress_bar.progress(1.0)
            break

        if page % 5 == 0 and results:
            preview.dataframe(pd.DataFrame(results).head(20), use_container_width=True)

        if page < max_pages:
            time.sleep(random.uniform(delay_min, delay_max))

    if results:
        df = pd.DataFrame(results)
        st.success(f"✅ Udtræk færdigt — **{len(df)} virksomheder**")
        st.dataframe(df, use_container_width=True, height=400)

        c1, c2 = st.columns(2)
        c1.download_button(
            "⬇️  Download Excel (.xlsx)",
            data=to_excel(df),
            file_name=f"wulff_nace_{nace.replace('.','_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
        c2.download_button(
            "⬇️  Download CSV",
            data=df.to_csv(index=False, sep=";", encoding="utf-8-sig"),
            file_name=f"wulff_nace_{nace.replace('.','_')}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    else:
        st.warning("Ingen virksomheder fundet. Tjek at branchekoden er korrekt.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="wc-footer">Wulff Consulting &nbsp;·&nbsp; Internt værktøj</div>',
    unsafe_allow_html=True
)
