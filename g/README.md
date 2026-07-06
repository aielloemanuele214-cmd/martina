# g/ — giochi consegnati ai clienti

Ogni file è un'avventura completa, pubblicata a un indirizzo segreto
(`/g/<token>.html`, token casuale): solo chi riceve il link o il QR può trovarla.
`robots.txt` esclude questa cartella dai motori di ricerca.

I file vengono creati da `python3 tools/sad.py consegna <slug>` — non a mano.
Con il repo collegato a Netlify, il push pubblica automaticamente la consegna.
