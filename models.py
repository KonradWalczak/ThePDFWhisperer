from pydantic import BaseModel, Field
from typing import List, Optional

# --- MODELE DLA ODWOŁANIA ---

class PelnomocnikOdwolujacego(BaseModel):
    imie_nazwisko: Optional[str] = None
    nazwa: Optional[str] = None
    mail: Optional[str] = None

class Odwolujacy(BaseModel):
    krs: Optional[str] = None
    nazwa: str
    nip: Optional[str] = None
    regon: Optional[str] = None
    przez_pelnomocnika: int = Field(alias="przez-pelnomocnika")
    pelnomocnik: Optional[PelnomocnikOdwolujacego] = None

class Zamawiajacy(BaseModel):
    krs: Optional[str] = None
    nazwa: str
    nip: Optional[str] = None
    regon: Optional[str] = None
    prowadzacy_postepowanie: Optional[int] = None

class OdwolanieKIO(BaseModel):
    data: Optional[str] = None
    czynnosc_dzien: Optional[str] = None
    czynnosc_powod_id: Optional[int] = None
    czynnosc_opis: Optional[str] = None
    miejscowosc: Optional[str] = None

class ZamowieniePubliczne(BaseModel):
    numer_bzp: Optional[str] = None
    numer_postepowania: Optional[str] = None
    numer_ted: Optional[str] = None
    tytul: Optional[str] = None

class SchematOdwolania(BaseModel):
    OdwolanieKIO: OdwolanieKIO
    Odwolujacy: List[Odwolujacy]
    Zamawiajacy: List[Zamawiajacy]
    ZamowieniePubliczne: ZamowieniePubliczne


# --- MODELE DLA PEŁNOMOCNICTWA ---

class DaneMocodawcy(BaseModel):
    imie_nazwisko: Optional[str] = None
    krs: Optional[str] = None
    nazwa: str
    nip: Optional[str] = None
    typ: str

class Podpisujacy(BaseModel):
    imie_nazwisko: str

class Mocodawca(BaseModel):
    data: DaneMocodawcy
    podpisujacy: List[Podpisujacy]

class Pelnomocnik(BaseModel):
    imie_nazwisko: str
    pesel: Optional[int] = None

class SchematPelnomocnictwa(BaseModel):
    mocodawca: List[Mocodawca]
    pelnomocnicy: List[Pelnomocnik]


# --- MODELE DLA PRZELEWU ---

class DanePrzelewu(BaseModel):
    data_operacji: Optional[str] = None
    kwota: float
    na_rachunek: Optional[str] = None
    numer_transakcji: Optional[str] = None
    tytul: str
    z_rachunku: Optional[str] = None

class SchematPrzelewu(BaseModel):
    przelew_bankowy: DanePrzelewu