import streamlit as st
import pdfplumber
import pandas as pd
import re
import io

st.title("📄 PDF zu Excel - Dokumentenanalyse")

uploaded_files = st.file_uploader("Lade eine oder mehrere PDF-Dateien hoch", accept_multiple_files=True)

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

    if extracted_data:
        df = pd.DataFrame(extracted_data)
        st.write("### Extrahierte Daten", df)

        # Excel-Datei zum Download erstellen
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        excel_data = output.getvalue()

        st.download_button(
            label="📥 Excel-Datei herunterladen",
            data=excel_data,
            file_name='extrahierte_daten.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    else:
        st.warning("❗️ Keine verwertbaren Daten gefunden.")


