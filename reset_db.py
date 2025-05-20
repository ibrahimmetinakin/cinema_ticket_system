import os
import database

DB_FILE = database.DB_NAME  # Veritabanı dosyası adı

def delete_database_file():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"{DB_FILE} dosyası silindi. Veritabanı sıfırlandı.")
    else:
        print(f"{DB_FILE} bulunamadı. Zaten temiz.")

def recreate_database():
    database.create_tables()
    database.preload_films()
    print("Veritabanı tabloları yeniden oluşturuldu ve örnek filmler yüklendi.")

if __name__ == "__main__":
    while True:
        choice = input("Veritabanını tamamen sıfırlamak istiyor musunuz? (E/H): ").strip().lower()
        if choice == "e":
            delete_database_file()
            recreate_database()
            break
        elif choice == "h":
            print("İşlem iptal edildi.")
            break
        else:
            print("Lütfen sadece 'E' veya 'H' giriniz.")
