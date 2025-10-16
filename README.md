# 🏫 UNIZD Oglasnik

Jednostavna web aplikacija za objavu i pregled oglasa napravljena u **Flasku**.  
Projekt je razvijen kao dio kolegija **Programiranje za Web (SIT UNIZD)**.

---

## ✨ Funkcionalnosti
- Dodavanje novog oglasa putem forme
- **Uređivanje postojećih oglasa**
- **Brisanje oglasa**
- Polja: naslov, opis, prodavač, broj mobitela, cijena, kategorija, lokacija, slika
- Validacija unosa (obavezna polja, duljina, email/telefon format…)
- CSRF zaštita (Flask-WTF)
- Flash poruke za obavijesti o uspjehu/neuspjehu
- PRG (Post → Redirect → Get) obrazac
- Bootstrap 5 za izgled i layout
- Spremanje oglasa u **MongoDB bazu podataka**
- Spremanje slika u **GridFS** (MongoDB datotečni sustav)
- Prikaz oglasa u listi (Bootstrap kartice)
- Filtriranje po kategorijama

---

## ⚙️ Instalacija i pokretanje

### Preduslovi
- Python 3.8+
- MongoDB (instaliraj lokalno ili koristi Docker)

### MongoDB instalacija
- **Windows/macOS/Linux**: [MongoDB Community Server](https://www.mongodb.com/try/download/community)

### Koraci instalacije

1. Kloniraj repozitorij:
   ```bash
   git clone https://github.com/jtoric/pzwpred2.git
   cd pzwpred2
   ```

2. Kreiraj virtualno okruženje i instaliraj pakete:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Linux / macOS
   .venv\Scripts\Activate.ps1      # Windows PowerShell

   pip install -r requirements.txt
   ```

3. Osiguraj da MongoDB radi:
   ```bash
   # Provjeri da li MongoDB radi na localhost:27017
   # Ako ne radi, pokreni MongoDB server
   ```

4. Pokreni aplikaciju:
   ```bash
   python app.py
   ```

5. Otvori u browseru:
   ```
   http://127.0.0.1:5000/
   ```

---


## 👨‍🏫 Autor
mag.ing. Josip Torić  
Studij informacijskih tehnologija — Sveučilište u Zadru
