from fastapi import FastAPI, UploadFile, File
import fitz  # PyMuPDF
from groq import Groq
import json

# Importujemy nasze struktury z pliku models.py
from models import SchematOdwolania, SchematPelnomocnictwa, SchematPrzelewu

app = FastAPI()

# Inicjalizacja klienta Groq
API_KEY = "TUTAJ_WPISZ_KLUCZ_GROQ"
client = Groq(api_key=API_KEY)

def wyciagnij_tekst_z_pdf(file_bytes: bytes) -> str:
    """Otwiera PDF w pamięci i wyciąga z niego czysty tekst."""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def rozpoznaj_dokument(tekst: str) -> str:
    """Szybki strzał do AI: rozpoznaje czy to Odwołanie, Pełnomocnictwo czy Przelew."""
    prompt = f"""
    Zidentyfikuj rodzaj poniższego dokumentu urzędowego. 
    Wybierz JEDNĄ z trzech opcji: ODWOLANIE, PELNOMOCNICTWO, PRZELEW.
    Odpowiedz tylko tym jednym słowem, bez kropek i wyjaśnień.
    
    Tekst dokumentu (fragment):
    {tekst[:1500]}
    """
    
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b", # Bardzo szybki model do klasyfikacji
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
    )
    return response.choices[0].message.content.strip().upper()

@app.post("/ekstrakcja")
async def ekstrakcja_danych(file: UploadFile = File(...)):
    # 1. Odczytanie pliku
    pdf_bytes = await file.read()
    tekst = wyciagnij_tekst_z_pdf(pdf_bytes)
    
    # --- LOGI DEBUGOWANIA (wyświetlą się w czarnym terminalu) ---
    print(f"\n[DEBUG] Wyciągnięto znaków z PDF: {len(tekst)}")
    print(f"[DEBUG] Początek tekstu: {tekst[:100]}")
    
    if len(tekst) < 50:
        return {"error": "Tekst jest za krótki. Prawdopodobnie to skan (wymaga OCR)."}

    # 2. Klasyfikacja dokumentu
    typ_dokumentu = rozpoznaj_dokument(tekst)
    print(f"[DEBUG] Model sklasyfikował jako: {typ_dokumentu}\n")
    
# 3. Wybór odpowiedniego modelu Pydantic
    if "ODWO" in typ_dokumentu:
        response_format = SchematOdwolania
    elif "PELNO" in typ_dokumentu or "PEŁNO" in typ_dokumentu:
        response_format = SchematPelnomocnictwa
    elif "PRZELEW" in typ_dokumentu:
        response_format = SchematPrzelewu
    else:
        return {"error": f"Nie rozpoznano formatu dokumentu. Odpowiedź modelu: {typ_dokumentu}"}

# 4. Główna ekstrakcja z wymuszeniem JSON
    oczekiwany_schemat = json.dumps(response_format.model_json_schema(), indent=2)
    
    # --- ZŁOTY PROMPT - Dynamiczne reguły na podstawie typu dokumentu ---
    if "ODWO" in typ_dokumentu:
        zlote_zasady = """
        SZCZEGÓŁOWE WYTYCZNE (ZASADY PUNKTACJI F1):
        - OdwolanieKIO.czynnosc_dzien: Data czynności dla pierwszego zarzutu (ISO YYYY-MM-DD). Brak wiarygodnej daty = null.
        - OdwolanieKIO.czynnosc_powod_id: ID powodu (1-12) ustalane WYŁĄCZNIE z pierwszego zarzutu.
        - Odwolujacy.nazwa: Dla konsorcjum podaj TYLKO nazwę Lidera.
        - Odwolujacy.pelnomocnik.nazwa: Nazwa podmiotu zatrudniającego pełnomocnika. ZAWSZE szukaj w tekście adresów do doręczeń, np. "Kancelaria Radców Prawnych", "Kancelaria Adwokacka Sp. z o.o.".
        - Zamawiajacy.prowadzacy_postepowanie: 1 jeśli lider, 0 jeśli nie lider, null jeśli brak danych.
        - ZamowieniePubliczne.numer_bzp: Format 'YYYY/BZP ########' (bez spacji po normalizacji). Nie wpisuj tu numerów TED!
        - ZamowieniePubliczne.numer_ted: Zwykle format 'NNNNNN-YYYY'.
        """
    elif "PELNO" in typ_dokumentu or "PEŁNO" in typ_dokumentu:
        zlote_zasady = """
        SZCZEGÓŁOWE WYTYCZNE (ZASADY PUNKTACJI F1):
        - Mocodawca.data.typ: Musi być dokładnie ciągiem znaków: "osoba_prawna" lub "osoba_fizyczna".
        - Jeśli mocodawca to osoba prawna (firma, spółka), ZAWSZE wpisz null w polu 'imie_nazwisko' mocodawcy.
        """
    else:
        zlote_zasady = """
        SZCZEGÓŁOWE WYTYCZNE (ZASADY PUNKTACJI F1):
        - Przelew: Zwróć absolutną uwagę na poprawny format kwoty (float) oraz usuń spacje z numerów rachunków bankowych.
        """

    system_prompt = f"""
    Jesteś wybitnym analitykiem prawnym z Urzędu Zamówień Publicznych. 
    Twoim zadaniem jest ekstrakcja danych z dokumentu i przypisanie ich DOKŁADNIE do poniższej struktury JSON.
    Nie wolno Ci tworzyć własnych kluczy, list ani dodawać nowych sekcji. Masz zwrócić tylko to, o co prosi schemat.
    Zwróć uwagę na formaty dat (YYYY-MM-DD), NIP, KRS oraz PESEL. Jeśli czegoś nie ma w tekście, przypisz wartość null.

    {zlote_zasady}
    
    Oto WYMAGANY schemat JSON (wygeneruj odpowiedź ściśle według niego):
    {oczekiwany_schemat}
    """
    
    chat_completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Wyodrębnij dane z tego tekstu, zachowując bezwzględną zgodność z formatem JSON: {tekst}"}
        ],
        temperature=0.0, # Zmniejszamy na 0.0 - zero kreatywności, 100% precyzji analitycznej
        response_format={"type": "json_object"}
    )
    
    dane_json = json.loads(chat_completion.choices[0].message.content)
    
    return dane_json
