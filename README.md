# Funkplaner für Home Assistant

Plane die Funkabdeckung deines Hauses über mehrere Geschosse – Zigbee, Thread/Matter,
WLAN, Bluetooth, 868 MHz (Z-Wave, Homematic IP, EnOcean) und die Netzwerkverkabelung
inklusive PoE-Budget und Kamerasichtfeldern. Alles läuft lokal auf deinem
Home-Assistant-Server, nichts verlässt dein Netz.

Entwickelt von [Smart Dome Solutions e.U.](https://www.youtube.com/@SmartDome)

## Was die Integration kann

- **Eigener Punkt in der Seitenleiste** mit dem vollständigen Funkplaner
- **Pläne auf dem Server**: alle Projekte liegen in `.storage`, nicht im Browser –
  damit sind sie von jedem Gerät aus erreichbar und landen im Backup
- **Geräte aus Home Assistant übernehmen**: der Planer liest das Geräteregister und
  schlägt deine echten Geräte zum Platzieren vor, samt Bereich, Etage und Rolle
- **Gerätedatenbank** mit über 650 Modellen, falls ein Gerät noch nicht existiert
- **Wände automatisch erkennen**: der Planer sucht im Grundrissbild nach Wänden
  samt Wandstärke, setzt Lücken als Türen und Fenster ein und zeigt alles zuerst
  als Vorschau, bevor es übernommen wird (Werkzeug *Wände erkennen*, Taste `D`)
- **Rechnet mit Wand- und Deckenmaterialien**, Montagehöhen, Störquellen und
  Kanalüberschneidungen

## Installation über HACS (eigenes Repository)

1. In Home Assistant **HACS** öffnen
2. Oben rechts auf die drei Punkte → **Benutzerdefinierte Repositories**
3. Als Repository `https://github.com/19DMO89/funkplanner` eintragen,
   als Kategorie **Integration** wählen und hinzufügen
4. Danach in HACS nach **Funkplaner** suchen und installieren
5. Home Assistant neu starten
6. Unter **Einstellungen → Geräte & Dienste → Integration hinzufügen** nach
   **Funkplaner** suchen und einrichten

Danach erscheint **Funkplaner** in der Seitenleiste.

### Installation von Hand

Den Ordner `custom_components/funkplaner` in das `config`-Verzeichnis von
Home Assistant kopieren, sodass `config/custom_components/funkplaner/manifest.json`
existiert, dann neu starten und die Integration hinzufügen.

## Geräte übernehmen

Im Planer rechts im Abschnitt **Geräte aus Home Assistant** auf *Geräte laden*
klicken. Es erscheinen alle Geräte des gerade gewählten Netzes, die noch nicht im
Plan sind. Ein Klick wählt ein Gerät aus, der nächste Klick in den Grundriss setzt es.

Die Zuordnung zum Netz erfolgt über die Integration des Geräts:

| Integration | Netz im Planer |
|---|---|
| ZHA, Zigbee2MQTT (über MQTT), deCONZ | Zigbee |
| Matter, Thread, OpenThread Border Router | Thread / Matter |
| Z-Wave JS, Homematic IP | 868 MHz |
| Bluetooth, BTHome, SwitchBot, Xiaomi BLE, Govee BLE | Bluetooth |
| ESPHome, Shelly, Tasmota, Tuya, WLED, TP-Link | WLAN |
| UniFi, UniFi Protect, Synology, Reolink, ONVIF, KNX | Netzwerk |

Die Rolle wird geschätzt: Geräte mit Batteriesensor gelten als Endgerät, netzbetriebene
als Router, und Geräte mit „Coordinator“, „Bridge“, „Gateway“ oder „Hub“ im Namen als
Zentrale. Im Planer lässt sich das jederzeit ändern.

Die **Position** kennt Home Assistant nicht – die setzt du einmal pro Gerät selbst.
Bereich und Etage werden aber mit angezeigt, damit die Zuordnung schnell geht.

## Was noch nicht enthalten ist

- **Automatische Kalibrierung** aus gemessenen LQI- und RSSI-Werten. Die
  WebSocket-Schnittstelle `funkplaner/signal` liefert die Messwerte bereits,
  der Planer rechnet sie noch nicht in die Wanddämpfung zurück.
- **Zigbee2MQTT-Netzwerkkarte** als Quelle für echte Nachbarbeziehungen.

## Schnittstelle

Die Integration stellt folgende WebSocket-Befehle bereit:

| Befehl | Zweck |
|---|---|
| `funkplaner/list` | Liste aller Projekte |
| `funkplaner/get` | Ein Projekt laden (`project_id`) |
| `funkplaner/save` | Projekt speichern (`project_id`, `name`, `state`, `images`) |
| `funkplaner/delete` | Projekt löschen (`project_id`) |
| `funkplaner/devices` | Geräte, Bereiche und Etagen aus dem Register |
| `funkplaner/signal` | Vorhandene LQI- und RSSI-Werte |

## Hinweise

- Grundrissbilder werden als Teil des Projekts gespeichert. Mehrere große Pläne
  können die Datei in `.storage` auf einige Megabyte anwachsen lassen.
- Die Berechnung ist ein Mehrwand-Modell mit Richtwerten. Sie zeigt zuverlässig,
  **wo** es eng wird, nicht auf das Dezibel genau **wie stark**. Plane mit Reserve.

## Lizenz

MIT – siehe [LICENSE](LICENSE).
