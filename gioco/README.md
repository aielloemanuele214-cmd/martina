# gioco/ — motore e produzione SempreAddue

Sei nella cartella che **costruisce e consegna** le avventure.
**Lancia i comandi da qui** (`cd gioco`):

```bash
python3 tools/sad.py ordine <slug>            # nuovo ordine → clienti/<slug>/
python3 tools/sad.py build clienti/<slug>/ordine.json   # costruisci (valida da sola)
python3 tools/sad.py qa dist/stanza-<slug>.html         # QA automatica
python3 tools/sad.py consegna <slug> --push   # build + QA + pubblica su Cloudflare
```

Guida completa passo-passo: **`../docs/README-PRODUZIONE.md`**
Specifiche per gli asset AI: `../docs/GENERAZIONE-ASSET.md`

## Regola d'oro
Il motore (`engine/`) **non si tocca mai** per un cliente. Per una nuova
avventura si cambiano solo i **template** in `packs/` e i dati dell'ordine in
`clienti/<slug>/`. I giochi finiti non restano qui: vanno nella repo privata
`sempreaddue-giochi` (Cloudflare Pages), fuori da questa repo pubblica.
