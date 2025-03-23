import time
import json
import os
import pyAesCrypt
import pyotp
import qrcode
import getpass
import subprocess
from PIL import Image, ImageTk
import tkinter as tk
import sqlite3
#from datetime import datetime


# Farben für Konsole
TGREEN = '\033[32m'  # Green Text
TRED = '\033[31m'  # Red Text
ENDC = '\033[m'  # Reset

# Klasse für Benutzer
class User:
    def __init__(self, usr_id, usr_pin, secret):
        self.usr_id = usr_id
        self.usr_pin = usr_pin
        self.secret = secret
        self.balance = 0.0
        self.transactions = []
        last_login = 0.0

    def add_transaction(self, amount, typ):
        self.transactions.append(f"{typ}: {amount:.2f} € Datum: {time.strftime('%d.%m.%Y %H:%M:%S')}")
    
# Klasse für die Verwaltung von SQLite Datenbank
class SQLiteDataManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.setup_database() # einrichten falls noch nicht vorhanden

    def get_connection(self): # Verbindung zu Datenbank
        return sqlite3.connect(self.db_path)
    
    def setup_database(self):
        conn = self.get_connection()
        c = conn.cursor()
        # Tabellen
        c.execute('''CREATE TABLE IF NOT EXISTS 
                users(
                    usr_id TEXT PRIMARY KEY,
                    usr_pin TEXT,
                    secret TEXT,
                    balance REAL,
                    last_login REAL
                    )
                ''')
        c.execute('''CREATE TABLE IF NOT EXISTS
                  transactions(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usr_id TEXT,
                    amount REAL,
                    type TEXT,
                    date TEXT,
                    FOREIGN KEY(usr_id) REFERENCES users(usr_id)
                  )
                ''')
        conn.commit()
        conn.close()
    
    def load_users(self):
        conn = self.get_connection()
        c = conn.cursor
        c.execute("SELCT * from users")
        users = {row[0]: 
                 {'usr_id': row[0], 'usr_pin': row[1], 'secret': row[2], 'balance': row[3], 'last_login': row[4]} 
                 for row in c.fetchall()}
        conn.close()
        return users

    def save_user(self, user):
        conn = self.get_connection()
        c = conn.cursor
        c.execute('''INSERT OR REPLACE INTO users (usr_id, usr_pin, secret, balance, last_login)
                     VALUES                       (     ?,       ?,       ?,      ?,          ?)''', 
                  (user['usr_id'], user['usr_pin'], user['secret'], user['balance'], user['last_login']))
        conn.commit()
        conn.close()

    def add_transaction(self, usr_id, amount, type):
        conn = self.get_connection()
        c = conn.cursor
        c.execute('''INSERT INTO transactions (usr_id, amount, type, date)
                     VALUES                   (     ?,      ?,    ?,    ?)''',
                                              (usr_id, amount, type, time.strftime('%d.%m.%Y %H%M%S')))
        conn.commit
        conn.close()
    
    def get_transactions(self, usr_id):
        conn = self.get_connection()
        c = conn.cursor
        c.execute("SELECT * FROM transactions WHERE usr_id = ?", (usr_id))
        transactions = [f"{row[3]}: {row[2]:.2f} € Datum: {row[4]}" for row in c.fetchall()]
        conn.close
        return transactions

"""
OLD DATAMANAGER
# Klasse für Datenmanagement
class DataManager:
    def __init__(self, db_path, db_password):
        self.db_path = db_path
        self.db_password = db_password

    def load_users(self):
        try:
            if os.path.exists(self.db_path + ".aes"):
                pyAesCrypt.decryptFile(self.db_path + ".aes", self.db_path, self.db_password)
                with open(self.db_path, 'r') as file:
                    return json.load(file)
            else:
                return {}
        except Exception as e:
            print(TRED + f"Fehler beim Laden der Daten: {e}" + ENDC)
            return {}

    def save_users(self, users):
        try:
            with open(self.db_path, 'w') as file:
                json.dump(users, file, indent=4)
            pyAesCrypt.encryptFile(self.db_path, self.db_path + ".aes", self.db_password)
            os.remove(self.db_path)
        except Exception as e:
            print(TRED + f"Fehler beim Speichern der Daten: {e}" + ENDC)"
"""

# Klasse für 2FA
class AuthManager:
    @staticmethod
    def gen_2fa_secret():
        return pyotp.random_base32()

    @staticmethod
    def verify_2fa(secret, code):
        return pyotp.TOTP(secret).verify(code)

    @staticmethod
    def show_qr(secret, usr_id):
        uri = pyotp.totp.TOTP(secret).provisioning_uri(name=usr_id, issuer_name="Bank V2.0")
        qr = qrcode.make(uri)
        qr_file = os.path.join(os.getcwd(), f"{usr_id}_2fa.png")
        qr.save(qr_file)
        print(TGREEN + f"Scanne den QR-Code {qr_file} mit Google Authenticator." + ENDC)
        return qr_file

# Klasse für das Banksystem
class BankSystem:
    def __init__(self):
        self.data_manager = SQLiteDataManager('bank_database.db')
        self.auth_manager = AuthManager()
        self.users = self.data_manager.load_users()
        self.versuche = 3

        # Admin-Konto erstellen, falls nicht vorhanden
        if "admin" not in self.users:
            admin_user = {'usr_id': 'admin', 'usr_pin': 'admin', 'secret': None, 'balance': 0.0, 'last_login': 0.0}
            self.data_manager.save_user(admin_user)
            self.users["admin"] = admin_user
            print(TGREEN + "Admin-Konto erstellt. Verwenden Sie 'admin' als Kontonummer und 'admin' als PIN." + ENDC)

    def register(self):
        usr_id = input("Bitte geben Sie Ihre neue Kontonummer ein: ")
        if usr_id in self.users:
            print(TRED + "Diese Kontonummer ist schon vergeben." + ENDC)
            return

        usr_pin = getpass.getpass("Bitte geben Sie Ihren neuen PIN ein: ")
        secret = self.auth_manager.gen_2fa_secret()
        qr_file = self.auth_manager.show_qr(secret, usr_id)

        print(TGREEN + "Bitte scannen Sie den QR-Code mit Google Authenticator." + ENDC)
        print(TGREEN + "Geben Sie dann den 2FA-Code ein, um die Aktivierung abzuschließen." + ENDC)
        
        self.show_qr_window(qr_file) # QR-Code in einem tkinter fenster anzeigen

        while True:
            self.qr_window.update() # damit tkinter das programm nicht blockiert
            code = input("2FA Code aus der App: ")
            if self.auth_manager.verify_2fa(secret, code):
                print(TGREEN + "2FA erfolgreich aktiviert!" + ENDC)
                break
            else:
                print(TRED + "Falscher Code. Bitte versuchen Sie es erneut." + ENDC)

        # Benutzerdaten speichern
        new_user = {"usr_id": usr_id, "usr_pin": usr_pin, "secret": secret, "balance": 0.0, "last_login": 0.0}
        self.data_manager.save_user(new_user)
        self.users[usr_id] = new_user
        os.remove(qr_file)  # QR-Code aus Sicherheitsgründen löschen
        self.close_qr_window()

    def show_qr_window(self, qr_file):
        # fenster erstellen
        self.qr_window = tk.Tk()
        self.qr_window.title("QR-Code aus 2FA")
        
        # Bild laden UND ALS ATTRIBUT SPEICHERN
        self.qr_image = Image.open(qr_file) # Bild als Attribut speichern weil es sonst von dem Garbage Collector gelöscht wird XD
        self.img_tk = ImageTk.PhotoImage(self.qr_image) 

        # Bild in einem Label anzeigen
        label = tk.Label(self.qr_window, image = self.img_tk)
        label.pack()

        # Fenster aktualisieren
        self.qr_window.update_idletasks()
        self.qr_window.update()

    def close_qr_window(self):
        if hasattr(self, 'qr_window'):
            self.qr_window.destroy() 

    def authenticate(self):
        while self.versuche > 0:
            usr_id = input("Bitte geben Sie Ihre Kontonummer ein: ")
            usr_pin = getpass.getpass("Bitte geben Sie Ihren PIN ein: ")

            if self.check_user(usr_id, usr_pin):
                if usr_id == "admin":
                    print(TGREEN + "Admin-Anmeldung erfolgreich!" + ENDC)
                    self.main_menu(usr_id)
                    break
                else:
                    user_data = self.users[usr_id]
                    current_time = time.time()
                    last_login = user_data.get('last_login')
                    if (current_time - last_login) < 300:  # 300 sek = 5 min
                        print(TGREEN + "Automatische Anmeldung" + ENDC)
                        self.main_menu(usr_id)
                        break
                    else:
                        secret = user_data['secret']
                        code = input("Bitte geben Sie den 2FA Code aus der App ein: ")
                        if self.auth_manager.verify_2fa(secret, code):
                            self.users[usr_id]['last_login'] = current_time #update last login
                            self.data_manager.save_users(self.users)
                            print(TGREEN + "Authentifizierung erfolgreich!" + ENDC)
                            self.main_menu(usr_id)
                            break
                        else:
                            print(TRED + "Falscher 2FA Code!" + ENDC)
                            self.versuche -= 1
                    wartezeit = 3 * (2 ** (2 - self.versuche))
                    if self.versuche > 0:
                        print(TRED + f'Kontonummer oder PIN falsch. Sie haben noch {self.versuche} Versuche.' + ENDC)
                        print(f'Bitte warten Sie {wartezeit} Sekunden, bevor Sie es erneut versuchen.')
                        time.sleep(wartezeit)
                    else:
                        print(TRED + "Kontonummer oder PIN falsch. Ihr Konto wurde gesperrt." + ENDC)
                        print(f'Bitte warten Sie {wartezeit} Sekunden, bevor Sie es erneut versuchen.')
                        time.sleep(wartezeit)

    def check_user(self, usr_id, usr_pin):
        if usr_id in self.users and self.users[usr_id]['usr_pin'] == usr_pin:
            return True
        return False

    def find_user(self):
        code = input("Bitte geben Sie den OTP Code aus dem Authenticator ein: ")
        for usr_id, user_data in self.users.items():
            if self.auth_manager.verify_2fa(user_data['secret'], code):
                print(TGREEN + f"Ihre Kontonummer ist: {usr_id}" + ENDC)
                return
        print(TRED + "Kein Benutzer mit diesem OTP Code gefunden." + ENDC)

    def reset_pin(self):
        usr_id = input("Bitte geben Sie Ihre Kontonummer ein: ")
        if usr_id in self.users:
            secret = self.users[usr_id]['secret']
            code = input("Bitte geben Sie den 2FA Code aus dem Authenticator ein: ")
            if self.auth_manager.verify_2fa(secret, code):
                print(TGREEN + "Authentifizierung erfolgreich, bitte geben Sie Ihren neuen PIN ein: " + ENDC)
                new_pin = getpass.getpass()
                self.users[usr_id]['usr_pin'] = new_pin
                self.data_manager.save_users(self.users)
                print(TGREEN + "PIN erfolgreich aktualisiert" + ENDC)
            else:
                print(TRED + "Falscher 2FA Code" + ENDC)
        else:
            print(TRED + "Kontonummer nicht gefunden!" + ENDC)
    
    def balance(self, usr_id):
        print(f'Ihr Kontostand beträgt {self.users[usr_id]["balance"]:.2f} €')
    
    def deposit(self, usr_id):
        amount = float(input("Bitte geben Sie den gewünschten Einzahlungsbetrag ein: "))
        self.users[usr_id]["balance"] += amount
        self.data_manager.save_user(self.users[usr_id])
        self.data_manager.add_transaction(usr_id, amount, 'Einzahlung')
        print(f'Sie haben {amount:.2f} € eingezahlt. Der neue Kontostand beträgt jetzt {self.users[usr_id]["balance"]:.2f} €')
        
    def payout(self, usr_id):
        amount = float(input("Bitte geben Sie den gewünschten Auszahlungsbetrag ein: "))
        if amount > self.users[usr_id]["balance"]:
            print(TRED + f'Sie wollen mehr auszahlen als Sie auf dem Konto haben. Ihr Kontostand beträgt: {self.users[usr_id]["balance"]:.2f} €' + ENDC)
        else:
            self.data_manager.save_user(self.users[usr_id])
            self.data_manager.add_transaction(usr_id, -amount, 'Auszahlung')
            print(f'Sie haben {amount:.2f} € abgehoben')
            print(f'Ihr neuer Kontostand beträgt: {self.users[usr_id]["balance"]:.2f} €')

    def transactions(self, usr_id):
        print("Kontoauszug:")
        for statement in self.data_manager.get_transactions(usr_id):
            print(statement)

    def transfer(self, sender_id):
        print("\nTransaktionsgebühr: 1 €")
        receiver_id = input("Bitte geben Sie die Kontonummer des Empfängers ein: ")
        if receiver_id not in self.users:
            print(TRED + "Empfänger-Kontonummer nicht gefunden." + ENDC)
            return
        amount = float(input("Bitte geben Sie den Überweisungsbetrag ein: "))
        if (amount + 1) > self.users[sender_id]['balance']:
            print(TRED + "Sie haben nicht genug Guthaben." + ENDC)
            return
        
        # überweisung
        self.users[sender_id]['balance'] -= (amount + 1)
        self.users["admin"]['balance'] += 1
        self.users[receiver_id]['balance'] += amount

        #transaktionen speichern
        self.data_manager.save_user(self.users[sender_id])
        self.data_manager.save_user(self.users[receiver_id])
        self.data_manager.save_user(self.users["admin"])
        self.data_manager.add_transaction(sender_id, - (amount +1), 'Überweisung')
        self.data_manager.add_transaction(receiver_id, amount, 'Überweisung')
        
        print(TGREEN + f"Überweisung von {amount:.2f} € an {receiver_id} erfolgrecih." + ENDC)

    def main_menu(self, usr_id):
        while True:
            print("\nAuswahlmenu:")
            print("1. Kontostand")
            print("2. Einzahlung")
            print("3. Auszahlung")
            print("4. Überweisung")
            print("5. Kontoauszüge")
            print("6. Beenden")

            try:
                auswahl = int(input("Bitte wählen Sie eine Option: "))
            except ValueError:
                print(TRED + "Ungültige Eingabe. Bitte geben Sie eine Zahl ein." + ENDC)
                continue

            if auswahl == 1:
                self.balance(usr_id)
            elif auswahl == 2:
                self.deposit(usr_id)
            elif auswahl == 3:
                self.payout(usr_id)
            elif auswahl == 4:
                self.transfer(usr_id)
            elif auswahl == 5:
                self.transactions(usr_id)
            elif auswahl == 6:
                print("Auf Wiedersehen")
                break
            else:
                print(TRED + "Ungültige Auswahl. Bitte versuchen Sie es erneut." + ENDC)

    def auth_menu(self):
        while True:
            print("\nHauptmenu:")
            print("1. Registrierung")
            print("2. Anmeldung")
            print("3. Kontonr vergessen ?")
            print("4. PIN vergessen ?")
            print("5. Beenden")
            auswahl = input("Bitte wählen Sie eine Option: ")
            if auswahl == "1":
                self.register()
            elif auswahl == "2":
                self.authenticate()
            elif auswahl == "3":
                self.find_user()
            elif auswahl == "4":
                self.reset_pin()
            elif auswahl == "5":
                print("Auf Wiedersehen!")
                break
            else:
                print("Ungültige Auswahl.")

# Hauptprogramm
if __name__ == "__main__":
    bank_system = BankSystem()
    bank_system.auth_menu()