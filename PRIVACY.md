# Privacyverklaring – VR-viewer starter

*Laatst bijgewerkt: oktober 2026*

VR-viewer starter is een gratis hulpmiddel, ontwikkeld in het kader van de masterproef *VR als leerhulpmiddel in bouwkundig onderwijs* (UGent). Met de app kun je VR-pagina's van bouwkundige constructies bekijken op een Meta Quest.

## Welke gegevens verzamelt de app?

Geen. De app verzamelt, verstuurt of verkoopt geen persoonsgegevens en bevat geen advertenties of statistieken.

## Wat bewaart de app op je computer?

Enkel op je eigen computer, in je gebruikersmap (`AppData\Local\VRViewerStarter`):

- de map met VR-modellen die je koos;
- de plaats van ngrok.exe;
- je ngrok-authtoken (in het configuratiebestand van ngrok).

Deze gegevens verlaten je computer niet, behalve het authtoken dat ngrok gebruikt om met je eigen ngrok-account te verbinden. Als je de app verwijdert, worden ze ook verwijderd.

## Diensten van derden: ngrok

Om je VR-pagina via een beveiligde https-link op de Quest te tonen, gebruikt de app **ngrok**, een aparte dienst van ngrok Inc. Je maakt daarvoor zelf een gratis account aan. Zolang je op **Start** hebt geklikt, zijn de bestanden in je gekozen map bereikbaar via die link. Klik op **Stop** of sluit de app om de link te stoppen.

Het verkeer via ngrok valt onder de privacyverklaring van ngrok: <https://ngrok.com/privacy>.

## Contact

Vragen? Maak een melding (issue) aan op de GitHub-pagina van dit project.
