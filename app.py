import streamlit as st
import pdfplumber
import pandas as pd
import re
import io

st.set_page_config(page_title="PDF zu Excel", page_icon="📄")

st.title("PDF zu Excel - Dokumentenscan")

# Optionen in der Seitenleiste
st.sidebar.header("Anzeigeoptionen")
show_datum = st.sidebar.checkbox("Rechnungsdatum anzeigen", value=True)
show_betrag = st.sidebar.checkbox("Rechnungsbetrag anzeigen")

uploaded_files = st.file_uploader(
    "Lade eine oder mehrere PDF-Dateien hoch",
    type=["pdf"],
    accept_multiple_files=True,
)

if uploaded_files:
    extracted_data = []

    for uploaded_file in uploaded_files:
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    name_match = re.search(r'Name:\s*(.*)', text)
                    rechnung_match = re.search(r'Rechnungsnummer:\s*(\d+)', text)
                    datum_match = re.search(r'Datum:\s*(\d{2}\.\d{2}\.\d{4})', text)

                    if name_match and rechnung_match and datum_match:
                        extracted_data.append({
                            'Dateiname': uploaded_file.name,
                            'Name': name_match.group(1).strip(),
                            'Rechnungsnummer': rechnung_match.group(1).strip(),
                            'Datum': datum_match.group(1).strip()
                        })
        try:
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        name_match = re.search(r'Name:\s*(.*)', text)
                        rechnung_match = re.search(r'Rechnungsnummer:\s*(\d+)', text)
                        datum_match = re.search(r'Datum:\s*(\d{2}\.\d{2}\.\d{4})', text)
                        betrag_match = re.search(r'Rechnungsbetrag:\s*([\d,.]+)', text)

                        if name_match and rechnung_match:
                            entry = {
                                'Dateiname': uploaded_file.name,
                                'Name': name_match.group(1).strip(),
                                'Rechnungsnummer': rechnung_match.group(1).strip(),
                            }
                            if datum_match:
                                entry['Rechnungsdatum'] = datum_match.group(1).strip()
                            if betrag_match:
                                entry['Rechnungsbetrag'] = betrag_match.group(1).strip()
                            extracted_data.append(entry)
        except Exception as e:
            st.error(f"Fehler beim Verarbeiten von {uploaded_file.name}: {e}")

    if extracted_data:
        df = pd.DataFrame(extracted_data)
        st.write("### Extrahierte Daten", df)
        columns = ['Dateiname', 'Name', 'Rechnungsnummer']
        if show_datum and 'Rechnungsdatum' in df.columns:
            columns.append('Rechnungsdatum')
        if show_betrag and 'Rechnungsbetrag' in df.columns:
            columns.append('Rechnungsbetrag')


        # Excel-Datei zum Download erstellen
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
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
