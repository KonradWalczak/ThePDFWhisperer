# 📄 The PDF Whisperer (Odwołania2JSON)

**Projekt zrealizowany w ramach hackathonu HackNation 2026 dla Urzędu Zamówień Publicznych.**

System rozwiązuje problem nieustrukturyzowanych danych spływających do Urzędu w formie plików PDF (często będących skanami). Aplikacja automatycznie klasyfikuje dokument (Odwołanie, Pełnomocnictwo, Przelew) i dokonuje precyzyjnej ekstrakcji kluczowych informacji do kanonicznego modelu JSON, zachowując rygorystyczne schematy ułatwiające dalsze procesowanie maszynowe.

## 🏗️ Architektura i Technologia
Projekt został podzielony na logiczne warstwy, aby zapewnić skalowalność i czytelność:
- `models.py` - Deklaratywne schematy danych (Pydantic), wymuszające poprawną strukturę JSON zgodną z wytycznymi UZP.
- `main.py` - Asynchroniczny serwer **FastAPI** odpowiadający za logikę biznesową. Wykorzystuje **PyMuPDF** do ekstrakcji tekstu oraz dwuetapowy routing AI (klasyfikacja + ekstrakcja ze "Złotym Promptem") przy pomocy modeli **OpenAI OSS (via Groq API)** dla maksymalnej szybkości i precyzji (wysoki F1 Score).
- `app.py` - Lekki, responsywny interfejs użytkownika zbudowany w **Streamlit**, umożliwiający wygodne testowanie i podgląd wyników przez użytkownika końcowego.

## ⚙️ Wymagania wstępne
- Środowisko Python 3.10 lub nowsze
- Ważny klucz API z platformy [Groq](https://console.groq.com/)

## 🚀 Jak uruchomić aplikację lokalnie? (Instrukcja dla Jury)

1. **Pobierz repozytorium:**
   ```bash
   git clone https://github.com/TwojaNazwa/ThePDFWhisperer.git
   cd ThePDFWhisperer
   ```
*(Zastąp link właściwym adresem repozytorium)*

2. **Zainstaluj wymagane pakiety:**
   ```bash
   pip install fastapi uvicorn groq pydantic pymupdf python-multipart streamlit requests
   ```

3. **Skonfiguruj klucz API:**
   Otwórz plik `main.py` i w linii 12 podmień wartość zmiennej `API_KEY`:
   ```python
   API_KEY = "TUTAJ_WPISZ_SWOJ_KLUCZ_GROQ"
   ```

4. **Uruchom serwer Backend (FastAPI):**
   Otwórz pierwszy terminal, upewnij się, że jesteś w folderze projektu i wpisz:
   ```bash
   python -m uvicorn main:app --reload
   ```
   *Serwer uruchomi się na porcie 8000.*

5. **Uruchom interfejs Frontend (Streamlit):**
   Otwórz drugie okno terminala, wejdź do folderu projektu i wpisz:
   ```bash
   python -m streamlit run app.py
   ```
   *Aplikacja powinna automatycznie otworzyć się w przeglądarce pod adresem `http://localhost:8501`.*

6. **Testowanie:**
   Wgraj dowolny dokument PDF z archiwum testowego UZP do interfejsu przeglądarkowego i kliknij "Analizuj dokument", aby wygenerować sformatowany plik JSON.
