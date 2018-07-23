## Prequesites
in order to build smart-assets (with can-link attribtute) which can implement permissions the repo smart-assets is
needed and also the specific branch kyber-master of bigchaindb

so:
clone smart-asset repo
cd smart-asset repo
clone bigchaindb
cd bigchaindb
checkout branch kyber-master
cd ..

und:
pip install bigchaindb-driver
oder: pip install -e .[dev] -> installiert alle benötigten site-packages

damit das alles funktioniert wird die Transaction SPec v1 benötigt
Leider nicht für Transaction Spec v2 implementiert


authentication funktioniert nocht nicht -> würde laut bigchaindb viel zu lange dauern (vgl git)


abändern...
server mithilfe von Docker starten ist hier nicht mehr so kompliziert bzw kein fehler mehr
-> trotzdem drin lassen? oder nur kurz erwähnen?

vermutlich drin lassen, da:
* ist die neueste version von bigchaindb
* den Fehler gibt es bei dieser Version nicht: Hintergrund?
* applikation im besten Fall auf dem neuesten Server laufen sollte..
    * smart-asset gibt es aber leider nur hier..