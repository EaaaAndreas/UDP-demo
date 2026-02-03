Denne demo demonstrer, hvordan du kan sætte din RP2 til at lytte på port og modtage input.

Den bliver sat til at lytte på port `0.0.0.0:12345`.

`0.0.0.0` betyder at den skal bruge dens egen ip (den IP, den får tildelt af DHCP serveren).

`12345` er en arbitrær port. Her kan du selv vælge en vilkårlig port. Men undgå porte imellem 0-1023, samt andre
registrerede porte. F.eks. `1883`: MQTT, `5683`: CoAP, `5353`: mDNS, `8080`: HTTP.

> Det sikreste er at vælge porte imellem **49152 - 65535**.

# Kør koden
For at køre koden, uploader du `main.py` til din RP2 og laver *hard reset*, eller kører den direkte i REPL.
> Husk at erstatte variablene i koden (*SSID*, *PASSWORD*, *Pin-nr.*)

Når koden kører, vil boardets integrerede LED lyse, og der skrives `Listening for UDP on <IP-address>:5001` i REPL.

Du kan så kommandere enheden, ved at sende en besked fra din PC, til den port som enheden lytter på.

## Send kommando
Åben en ***Linux terminal*** og skriv
```bash
echo "toggle" | nc -u <IP-ADDRESS> 12345`
```
***Note:** Det kan være nødvendigt at gå ud af kommandoen med `ctrl+C` før du skriver igen.*

Du vil så se, at LED'en skifter imellem tændt og slukket.
Du kan også bruge forskellige kommandoer: "toggle", "on", "off".

### HUSK!
- erstat `<IP-ADDRESS>` med din RP2's IP-adresse!
- At være tilsluttet samme netværk (og subnet)!

# Gennemgang
### Import
Vi starter med at importere de moduler der skal bruges.
```python
from network import WLAN
import socket
from machine import Pin, idle
```
### LED'er
Vi opretter så 2 LED'er. Den ene, `board_led`, bruges udelukkende som status LED, for at vise, at programmet kører og
at enheden aktivt lytter.
Den anden, `led`, er den LED, vi tænder og slukker
```python
board_led = Pin("LED", Pin.OUT, value=0)
led = Pin(2, Pin.OUT, value=0)
```
### WLAN
Der skal opsættes en forbindelse til WLAN, før vi kan starte et socket. Vi skal derfor bruge `network.WLAN`, som er
MicroPython's modul til at styre netværk på RP2.
```python

# Setup WIFI
wlan = WLAN(WLAN.IF_STA)

wlan.active(True)
wlan.connect("SSID", "PASSWORD")

while not wlan.isconnected():
    idle()
```
`wlan = WLAN(WLAN.IF_STA)` starter et netværks interface, som skal sættes op som `IF_STA`, STAtion InterFace, så vi kan
oprette forbindelse til andre access points.

Vi starter så interfacet med `wlan.active(True)`, og forbinder til det ønskede netværk med
`wlan.connect('SSID', 'PASSWORD')`. *Husk at ændre SSID og PASSWORD, til værdierne for dit eget netværk.*

Vi fanger så programmet i et while-loop, indtil der er oprettet forbindelse. ***Note:** Det kan være farligt at gøre
som her, hvis du f.eks. skriver forkert kodeord!*
Imens vi venter, kører vi `machine.idle()`, som reducerer maskinens clock-speed, for at spare på strømmen.

### Opret socket
Vi skal nu oprette et socket, som bruger **internettet** og **User Datagram Protocol (UDP)**.

```python
soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

soc.bind(("0.0.0.0", 12345))
```
`socket.socket()` tager 2 argumenter, når vi kalder det.

Det første argument bestemmer, hvilken [socket familie](https://docs.python.org/3.5/library/socket.html#socket-families)
vi bruger. Her bruger vi `AF_INET`, som fortæller vores socket at vi vil bruge enten et *internet domæne* og en *port*,
eller en *IPv4-adresse* og en *port*. Altså `('www.example.com', 12345)` eller `('10.110.12.34', 12345)`.

Vi binder så vores socket til en adresse med `socket.bind()`. Her bruger vi `0.0.0.0`, som er enhedens egen IP, og
`12345` som er en arbitrær port.

Vi annoncerer så, at enheden er klar til at tage imod kommandoer.
```python
print(f'Listening for UDP on {wlan.ipconfig('addr4')[0]}:12345')

board_led.on()
```
### Lyt
```python
try:
    while True:
        data, addr = soc.recvfrom(1024)
        print("Received from", addr, ":", data)
        data = data.decode('ascii').strip('\n').lower()
        if data == 'toggle':
            led.toggle()
        elif data == 'on':
            led.on()
        elif data == 'off':
            led.off()


except Exception as e:
    soc.close()
    board_led.off()
    raise e
```
For at lytte, skal vi blot kalde `socket.recvfrom()`. Vi angiver en `buffsize=1024`, som angiver, hvor mange bit vi kan
modtage.
`socket.recvfrom()` returnerer en tuple med to værdier `(data, addr)`. `data` er den *bit-stream* der er modtaget,
`addr` er den IP-adresse, beskeden er kommet fra.

Vi udskriver så til REPL, at vi har modtaget en kommando.

Vi skal så huske, at `data` er et bytes-objekt. Derfor skal det omdannes til en streng, så vi kan operere på det.
Det gør vi med `data.decode('ascii')`. ***Note:** Det betyder at vores kommando skal være encoded med ASCII!*

Som udgangspunkt vil der blive sat et linieskift `'\n'` bagpå beskeden, så den fjerner vi med `.strip('\n')`. Og vi
sørger så for, at beskeden kun er små bogstaver, med `.lower()`.

Til sidst håndteres inputtet med en *if*-statement.

#### Try-except
Når vi åbner et socket, vil modulet ikke selv sørge for at lukke det igen, hvis programmet bliver afbrudt!
Derfor skal vi selv sørge for at lukke vores socket, hvis vi ikke ønsker at genstarte enheden, hver gang vi vil bruge
den samme port igen.

Derfor lytter vi efter fejl (f.eks. `KeyboardIntterrupt`, som kommer når du stopper programmet i REPL med `ctrl-C`), og
sørger for at socket bliver lukket, med `socket.close()`, inden vi hæver fejlen igen, så programmet stoppes. I samme
omgang slukker vi indikations-LED'en.