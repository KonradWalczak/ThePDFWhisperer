import streamlit as st
import requests

st.set_page_config(page_title="Odwołania2JSON Parser", layout="wide")

st.title("📄 The PDF Whisperer (Odwołania2JSON)")
st.write("Wgraj dokument (PDF) z systemu zamówień publicznych, aby automatycznie sklasyfikować go i wyciągnąć kluczowe informacje do ustrukturyzowanego formatu JSON.")

uploaded_file = st.file_uploader("Wybierz plik PDF", type=["pdf"])

if uploaded_file is not None:
    st.write("Plik załadowano:", uploaded_file.name)
    
    if st.button("Analizuj dokument 🚀"):
        with st.spinner("Czytam dokument i analizuję za pomocą AI..."):
            # Pakujemy plik i wysyłamy do Twojego lokalnego backendu
            files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
            try:
                # Uderzamy pod adres, pod którym działa Twój uvicorn
                response = requests.post("http://127.0.0.1:8000/ekstrakcja", files=files)
                
                if response.status_code == 200:
                    wynik = response.json()
                    st.success("Analiza zakończona sukcesem!")
                    st.subheader("Wyodrębniony JSON")
                    st.json(wynik)
                else:
                    st.error(f"Błąd serwera. Kod błędu: {response.status_code}")
                    st.write(response.text)
                    
            except requests.exceptions.RequestException as e:
                 st.error(f"Błąd połączenia z backendem. Upewnij się, że serwer uvicorn działa. Szczegóły: {e}")