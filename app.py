import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from io import BytesIO

st.set_page_config(page_title="Proff.dk Udtræk", page_icon="🏢", layout="centered")

st.title("🏢 Proff.dk Virksomhedsudtræk")
st.markdown("Hent virksomhedsdata fra [proff.dk](https://www.proff.dk) baseret på en branchekode (NACE).")

# ── Sidebar settings ──────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Indstillinger")
    max_pages = st.slider("Maks. antal sider", min_value=1, max_value=500, value=50,
                          help="Hver side indeholder ~20 virksomheder. Sæt lavt under test.")
    delay_min = st.slider("Min. ventetid mellem sider (sek)", 0.5, 3.0, 1.2, step=0.1)
    delay_max = st.slider("Maks. ventetid mellem sider (sek)", 0.5, 5.0, 2.5, step=0.1)
    st.markdown("---")
    st.caption("Ventetid forhindrer at proff.dk blokerer scriptet.")

# ── Main input ────────────────────────────────────────────────────────────────
nace_input = st.text_input(
    "Branchekode (NACE)",
    value="47.55",
    placeholder="F.eks. 47.55 eller 62.01",
    help="Find din kode på https://www.proff.dk/segmentering"
)

col1, col2 = st.columns([2, 1])
with col1:
    start_btn = st.button("▶ Start udtræk", type="primary", use_container_width=True)

# ── Scraping logic ────────────────────────────────────────────────────────────
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def scrape_page(page: int, nace: str) -> tuple[list[dict], bool]:
    """Scrape a single results page. Returns (rows, has_more)."""
    if page == 1:
        url = f"https://www.proff.dk/segmentering?sort=profitDesc&naceIndustry={nace}"
    else:
        url = f"https://www.proff.dk/segmentering?page={page}&naceIndustry={nace}&sort=profitDesc"

    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        st.warning(f"Netværksfejl på side {page}: {e}")
        return [], False

    soup = BeautifulSoup(response.content, "html.parser")
    company_blocks = soup.select('div[class*="SegmentationSearchResultCard-card"]')

    if not company_blocks:
        return [], False

    rows = []
    for block in company_blocks:
        try:
            name_tag = block.select_one("h2 a")
            name = name_tag.text.strip() if name_tag else ""

            # CVR
            cvr = ""
            cvr_container = block.find("span", class_="CardHeader-propertyList")
            if cvr_container:
                text = cvr_container.get_text(separator=" ", strip=True)
                for part in text.split():
                    if part.isdigit() and len(part) == 8:
                        cvr = part
                        break

            if not cvr:
                continue

            # Postnummer
            postal = ""
            loc_icon = block.find("svg", {"data-icon": "location-dot"})
            if loc_icon:
                parent = loc_icon.find_parent("span")
                if parent:
                    postal = parent.get_text(strip=True)

            # Bruttofortjeneste
            brutto = ""
            brutto_label = block.find("div", string=lambda s: s and "Bruttofortjeneste" in s)
            if brutto_label:
                container = brutto_label.find_parent()
                if container:
                    for t in container.find_all(string=True):
                        if t.strip().replace(".", "").isdigit():
                            brutto = t.strip().replace(".", "")
                            break

            # Antal ansatte
            ansatte = ""
            ansatte_label = block.find("div", string=lambda s: s and "Antal ansatte" in s)
            if ansatte_label:
                container = ansatte_label.find_parent()
                if container:
                    for t in container.find_all(string=True):
                        cleaned = t.strip().replace(".", "")
                        if cleaned.isdigit():
                            ansatte = cleaned
                            break

            # Branche-tags
            branches = block.select("div.IndustryTags-tags a")
            branche = ", ".join(tag.text.strip() for tag in branches)

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
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Virksomheder")
        ws = writer.sheets["Virksomheder"]
        # Auto-size columns
        for col in ws.columns:
            max_len = max((len(str(cell.value or "")) for cell in col), default=10)
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 50)
    return output.getvalue()


# ── Run scrape ────────────────────────────────────────────────────────────────
if start_btn:
    nace = nace_input.strip()
    if not nace:
        st.error("Indtast venligst en branchekode.")
        st.stop()

    st.info(f"Starter udtræk for NACE-kode **{nace}** — maks. {max_pages} sider...")

    results: list[dict] = []
    seen_cvrs: set[str] = set()

    progress_bar = st.progress(0)
    status_text = st.empty()
    table_placeholder = st.empty()

    for page in range(1, max_pages + 1):
        status_text.markdown(f"⏳ Henter side **{page}** / {max_pages} &nbsp;|&nbsp; Fundet **{len(results)}** virksomheder")
        progress_bar.progress(page / max_pages)

        rows, has_more = scrape_page(page, nace)

        # Deduplicate
        new_rows = [r for r in rows if r["CVR-nr"] not in seen_cvrs]
        for r in new_rows:
            seen_cvrs.add(r["CVR-nr"])
        results.extend(new_rows)

        if not has_more:
            status_text.markdown(f"✅ Ingen flere sider. Fundet **{len(results)}** virksomheder totalt.")
            progress_bar.progress(1.0)
            break

        # Live preview every 5 pages
        if page % 5 == 0 and results:
            table_placeholder.dataframe(pd.DataFrame(results).head(20), use_container_width=True)

        if page < max_pages:
            time.sleep(random.uniform(delay_min, delay_max))

    # ── Results ───────────────────────────────────────────────────────────────
    if results:
        df = pd.DataFrame(results)

        st.success(f"✅ Udtræk færdigt — **{len(df)} virksomheder** hentet.")
        st.dataframe(df, use_container_width=True, height=400)

        col_dl1, col_dl2 = st.columns(2)

        xlsx_data = to_excel(df)
        col_dl1.download_button(
            label="⬇️ Download Excel (.xlsx)",
            data=xlsx_data,
            file_name=f"proff_nace_{nace.replace('.', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

        csv_data = df.to_csv(index=False, sep=";", encoding="utf-8-sig")
        col_dl2.download_button(
            label="⬇️ Download CSV",
            data=csv_data,
            file_name=f"proff_nace_{nace.replace('.', '_')}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    else:
        st.warning("Ingen virksomheder fundet. Tjek at branchekoden er korrekt.")
