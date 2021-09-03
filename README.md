# LED Matrix

A library and web app for having fun with an [Adafruit RGB LED Matrix](https://www.adafruit.com/products/1484)

Depends on [rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix)




![alt text](https://github.com/731mat/led-display/blob/master/photos/i1.JPG)
![alt text](https://github.com/731mat/led-display/blob/master/photos/i2.JPG)
![alt text](https://github.com/731mat/led-display/blob/master/photos/i6.jpeg)

Led panely propojeny sběrnicí HUB75-D | raspberry s modulem
--- | ---
![alt text](https://github.com/731mat/led-display/blob/master/photos/i4.JPG) | ![alt text](https://github.com/731mat/led-display/blob/master/photos/i3.JPG)

![alt text](https://github.com/731mat/led-display/blob/master/photos/i5.jpg)





## Running

```sh
# Install dependencies, build submodules, install nginx config
make setup

# restart nginx
sudo service nginx reload

# start the server
sudo ./pyvenv/bin/python server.py
```

# Co je cíl ?
Cílem projektu je vytvořit display, který bude jednoduše ovladatelný a přívětivý pro uživatele. Display by měl mít celou řadu použití. Od zobrazení textu přes časovače, po vyrendrování jpeg obrázku.
GUI bude přes webové rozhraní.
# dovednosti
- [ ] zobrazit cokoliv ... (v gui si zvolím text a barvu a umístění)
- [ ] zobrazit běžící text
- [ ] Zobrazit odpočet časový ... a po ukončení vypsat text
- [ ] dotazovat se okolního serveru a zobrazovat data (v různých provedení)
- [ ] zobrazi jpeg
- [ ] práce s ikony
- [ ] stopky
- [ ] Závodní systém (na webu si zasám seznam zavodniku a display napise na start se pripravi zavodnik1 přes web se odstartuje poběží stopky .. a cíly se vypnou stopky .. vypíše se finální čas. ... a výzva pro dalšího závodníka .... čas se zaeviduje na webu ...    (web: export import závodníků))
- [ ] Pro závodní systém naprogramovat START a STOP přes GPIO na jako PullUp spínače 
- [ ] možnost až třech závodníků najednou ...   (stačí dvou ... )

# co je potřeba udělat ?
- [x] nainstalovat OS na raspberry pi
- [x] zprovoznit komunikaci DISPLAY <> raspberry
- [x] upravit zobrazovací skript pro potřeby
- [ ]  opravit skritp z pohledu FLASK knihovny
- [ ]  aktualizovat JS a bootstrap
- [ ]  vytvořit jednoduchou auth na web
- [ ]  vymyslet zobrazení .. chápu že bez loop smyčky to asi nepůjde ale v aktuální skriptu to není úplně šťastné řešení ... jelikož né vždy ta loop smyčka jde ukončit
- [ ]  implemntovat funkce ze sekce "dovednosti" (z 60% je to hotové)
- [ ]  vytvořit službu v Linuxu aby hlídala python ... (spuštění, restart, error)
- [ ]  Ovládání Linux serveru přes gui (restat, shutdown..., reload python)
