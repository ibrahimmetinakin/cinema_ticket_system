import database
from ui import main_window

# Önce tabloları oluştur!
database.create_tables()

# Sonra örnek filmleri ekle!
database.preload_films()

# Ana pencereyi başlat
main_window.start_main_window()
