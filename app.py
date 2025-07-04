import streamlit as st
import pdfplumber
import pandas as pd
import re
import io

st.set_page_config(page_title="PDF zu Excel", page_icon="📄")

st.title("PDF zu Excel - Dokumentenscan")


col_upload, col_options = st.columns([2, 1])

with col_upload:
    uploaded_files = st.file_uploader(
        "Lade eine oder mehrere PDF-Dateien hoch",
        type=["pdf"],
        accept_multiple_files=True,
    )

with col_options:
    st.markdown("### Anzeigeoptionen")
    show_dateiname = st.checkbox("Dateiname", value=True)
    show_name = st.checkbox("Name", value=True)
    show_rechnungsnummer = st.checkbox("Rechnungsnummer", value=True)
    show_datum = st.checkbox("Rechnungsdatum", value=True)

if uploaded_files:
    extracted_data = []

    for uploaded_file in uploaded_files:
        try:
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if not text:
                        continue

                    name_match = re.search(r'Name:\s*(.*)', text)
                    rechnung_match = re.search(r'Rechnungsnummer:\s*(\d+)', text)
                    datum_match = re.search(r'Datum:\s*(\d{2}\.\d{2}\.\d{4})', text)
                  

                    if name_match and rechnung_match:
                        entry = {
                            'Dateiname': uploaded_file.name,
                            'Name': name_match.group(1).strip(),
                            'Rechnungsnummer': rechnung_match.group(1).strip(),
                        }
                        if datum_match:
                            entry['Rechnungsdatum'] = datum_match.group(1).strip()
                       
                        extracted_data.append(entry)
        except Exception as e:
            st.error(f"Fehler beim Verarbeiten von {uploaded_file.name}: {e}")

    if extracted_data:
        df = pd.DataFrame(extracted_data)
        columns = []
        if show_dateiname:
            columns.append('Dateiname')
        if show_name:
            columns.append('Name')
        if show_rechnungsnummer:
            columns.append('Rechnungsnummer')
        if show_datum and 'Rechnungsdatum' in df.columns:
            columns.append('Rechnungsdatum')
      

        st.write("### Extrahierte Daten", df[columns])

     
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df[columns].to_excel(writer, index=False)
        excel_data = output.getvalue()

        st.download_button(
            label="Excel-Datei herunterladen",
            data=excel_data,
            file_name='extrahierte_daten.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    else:
        st.warning("❗️ Keine verwertbaren Daten gefunden.")
