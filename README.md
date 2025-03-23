# OpenBank
# Features
### Benutzerverwaltung
- Registrierung + 2FA
- Anmeldung mit 2FA (Timeout von 5 Minuten)
- Admin Konto der automatisch erstellt wird
### Sicherheit
- Zwei-Faktor-Authentifizierung
- Pin Zurücksetzung (mithilfe von 2FA)
- Kontonummer-Wiederherstellung
### Transaktionen
- Einzahlung
- Auszahlung
- Überweisung (mit Transaktionsgebühr von 1€)
- Kontoauszüge
### Kontoverwaltung
- Kontostand
- Transaktionshistorie
### Datenmanagement
~~- Verschlüsselte Datenspeicherung (JSON-Datei -> mit AES verschlüsselt und entschlüsselt)~~
- SQLite3 Database für besseres Datenmanagement
### Benutzeroberfläche
- Konsolenbasierte Menüs
- QR-Code-Anzeige (automatische Erscheinung und Erlöschung)
### Fehlerbehandlung
- Klare Fehlermeldungen
- Versuche (3 Versuche + Timer)
### Erweitbarkeit
- Modularer Code (Klassen wie User, DataManagement, AuthManager)

# To-Do
### GUI
- Modernes Design (customtkinter oder tkinter)
- Buttons, Eingabefelder und visuelle Elemente
- Dark Mode
- Responsive Layout
### Erweiterte Sicherheitsfeatures
- Passwortstärkeüberprüfung (Mindestlänger, Sonderzeichen..)
- Sicherheitsfragen 
### Mehrere Währungen
- Währungsumrechnung (Konten in verschiedene Währungen + Integration einer API für Echtzeit-Wechselkurse (Open Exchange Rates))
- Automatische Umrechnung (bei Überweisungen)
### Benachrichtigungen
- E-Mail-Benachrichtigungen (bei Transaktionen, Kontostandänderungen)
### Erweiterte Transaktionsfunktionen
- Daueraufträge
- Transaktionslimits
- Kreditverwaltung
### Erweiterte Admin-Funktionen
- Benutzerverwaltung 
- Transaktionsverwaltung
### Internationalisierung
- Mehrsprachigkeit (Deutsch, Englisch usw)
- Lokale Währunge  (basiert aufm Standort)
~~### Database~~
~~- SQLite3 Database für besseres Datenmanagement~~