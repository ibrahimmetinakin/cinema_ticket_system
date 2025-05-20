import sqlite3

DB_NAME = "cinema_system.db"

def check_table(table_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name};")
    records = cursor.fetchall()
    conn.close()
    return records

def main():
    print("📢 Bilet Kayıtları (tickets):")
    tickets = check_table("tickets")
    if tickets:
        for ticket in tickets:
            print(ticket)
    else:
        print("➡️ Hiç kayıt yok. Tablon temiz!")

    print("\n📢 Rezervasyon Kayıtları (reservations):")
    reservations = check_table("reservations")
    if reservations:
        for reservation in reservations:
            print(reservation)
    else:
        print("➡️ Hiç rezervasyon yok. Tablon temiz!")

if __name__ == "__main__":
    main()
