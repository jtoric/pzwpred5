#!/usr/bin/env python3
"""
Skripta za dodavanje test podataka u MongoDB
Generira 50 oglasa s različitim kategorijama i datuma
"""

from faker import Faker
from pymongo import MongoClient
from datetime import datetime, timedelta
import random
import sys

# Inicijalizacija faker-a
fake = Faker('hr_HR')  # Hrvatski jezik

# MongoDB konekcija
client = MongoClient('mongodb://localhost:27017/')
db = client['pzw']
ads_collection = db['ads']

# Kategorije oglasa
CATEGORIES = [
    'Elektronika', 'Dom i vrt', 'Automobili', 'Odjeća', 
    'Sport', 'Knjige', 'Ostalo'
]

def generate_ad():
    """Generira jedan oglas s nasumičnim podacima"""
    # Nasumični datum u zadnjih 30 dana
    days_ago = random.randint(0, 30)
    created_at = datetime.now() - timedelta(days=days_ago)
    
    # Nasumična kategorija
    category = random.choice(CATEGORIES)
    
    # Generiraj oglas
    ad = {
        'title': fake.sentence(nb_words=random.randint(1,3)).rstrip('.'),
        'description': fake.paragraph(nb_sentences=random.randint(2, 5)),
        'price': round(random.uniform(10, 5000), 2),
        'category': category,
        'location': fake.city(),
        'seller': fake.name(),
        'cellNo': fake.phone_number().replace(' ', ''),
        'created_at': created_at,
        'image_id': None  # Bez slika
    }
    
    return ad

def add_test_data(num_ads):
    """Dodaje test podatke u bazu"""
    print(f"Generiram {num_ads} test oglasa...")
    
    # Generiraj sve oglase
    ads = []
    for i in range(num_ads):
        ad = generate_ad()
        ads.append(ad)
    
    # Batch insert u bazu
    print("Dodajem oglase u bazu...")
    result = ads_collection.insert_many(ads)
    
    print(f"✅ Uspješno dodano {len(result.inserted_ids)} oglasa!")
    

def clear_test_data():
    """Briše sve test podatke iz baze"""
    print("Brišem sve oglase iz baze...")
    result = ads_collection.delete_many({})
    print(f"✅ Obrisano {result.deleted_count} oglasa!")

def main():
    """Glavna funkcija"""

    
    if len(sys.argv) > 1 and sys.argv[1] == 'clear':
        clear_test_data()
        return
    
    try:
        add_test_data(100)
        
    except Exception as e:
        print(f"❌ Greška: {e}")
        sys.exit(1)
    finally:
        client.close()

if __name__ == '__main__':
    main()