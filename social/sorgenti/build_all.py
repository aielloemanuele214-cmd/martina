#!/usr/bin/env python3
"""Genera tutte le slide dei 3 caroselli + immagine profilo."""
from gen import *

SC = SCRATCH  # scratchpad (still frame gameplay)

# ---------- helper aggiuntivi ----------
def xmark(x, y):
    """croce pixel (per gli anti-esempi)"""
    p = 7
    cells = [(0,0),(1,1),(2,2),(3,3),(4,4),(4,0),(3,1),(1,3),(0,4)]
    r = ''.join(f'<rect x="{x+cx*p}" y="{y+cy*p}" width="{p}" height="{p}" fill="{ROSA}"/>'
                for cx, cy in cells)
    return f'<g opacity="0.95">{r}</g>'

def x_row(y, txt, sub, x=MX):
    r = xmark(x, y-30)
    r += (f'<text x="{x+64}" y="{y}" font-family="{BALOO}" font-weight="700" '
          f'font-size="44" fill="{CREMA}" opacity="0.88">{esc(txt)}</text>')
    r += (f'<text x="{x+64}" y="{y+44}" font-family="Nunito" font-size="33" '
          f'fill="{SOFT}">{esc(sub)}</text>')
    return r

def step_row(y, n, txt, sub, x=MX):
    r = num_badge(x, y-52, n)
    r += (f'<text x="{x+104}" y="{y}" font-family="{BALOO}" font-weight="700" '
          f'font-size="45" fill="{CREMA}">{esc(txt)}</text>')
    r += (f'<text x="{x+104}" y="{y+46}" font-family="Nunito" font-size="33" '
          f'fill="{SOFT}">{esc(sub)}</text>')
    return r

def overlay_defs():
    return f"""<linearGradient id="ovgrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{NOTTE}" stop-opacity="0.25"/>
      <stop offset="0.45" stop-color="{NOTTE}" stop-opacity="0.55"/>
      <stop offset="1" stop-color="{NOTTE}" stop-opacity="0.96"/>
    </linearGradient>"""

def svg_doc_full(content, extra_defs=''):
    """variante con defs extra (per slide full-bleed)"""
    doc = svg_doc(content)
    return doc.replace('<style>', extra_defs + '<style>', 1)

def phone(path, cx, cy, w=430, rotate=0):
    """mockup telefono con screenshot"""
    h = int(w * 2.05)
    x, y = cx - w/2, cy - h/2
    uri = datauri(path)
    cid = abs(hash((path, cx, cy))) % 99999
    rot = f' transform="rotate({rotate} {cx} {cy})"' if rotate else ''
    return f"""
  <g{rot}>
    <rect x="{x+14}" y="{y+26}" width="{w}" height="{h}" rx="64" fill="#000" opacity="0.5"/>
    <rect x="{x-10}" y="{y-10}" width="{w+20}" height="{h+20}" rx="72" fill="{NOTTE3}"
      stroke="{BORDO}" stroke-width="3"/>
    <clipPath id="ph{cid}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="56"/></clipPath>
    <image href="{uri}" x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice"
      clip-path="url(#ph{cid})"/>
    <rect x="{cx-60}" y="{y+16}" width="120" height="9" rx="4.5" fill="{NOTTE3}"/>
  </g>"""

# ══════════════════════════════════════════════════════════════
# CAROSELLO 1 — Cos'è SempreAddue
# ══════════════════════════════════════════════════════════════
def c1s1():
    c = [logo(), slide_index(1)]
    c.append(kicker(238, 'il regalo che non ti aspetti'))
    t, y = title(365, [[('Non si scarta.', CREMA)], [('Si gioca.', CORALLO)]], size=116)
    c.append(t)
    b, y = body(y+30, ['La vostra storia d’amore, trasformata in una',
                       'mini avventura pixel art. Fatta a mano, per voi due.'], size=38)
    c.append(b)
    c.append(image_frame(f'{IMG}/village-800.webp', MX, y+46, W-2*MX, 520, rotate=-1.2))
    c.append(sprite(f'{IMG}/ballo.webp', W-MX-190, y+46+520-268, 170))
    c.append(footer())
    return svg_doc('\n'.join(c))

def c1s2():
    c = [logo(), slide_index(2)]
    c.append(kicker(238, 'il problema'))
    t, y = title(360, [[('I regali di sempre', CREMA)], [('durano un attimo.', CORALLO)]], size=90)
    c.append(t)
    y += 60
    c.append(x_row(y, 'Un mazzo di fiori', 'bellissimo, per una settimana')); y += 150
    c.append(x_row(y, 'Un video con le foto', 'trenta secondi, poi si scorre oltre')); y += 150
    c.append(x_row(y, 'Un biglietto scritto a mano', 'dolce, il tempo di leggerlo')); y += 150
    b, y = body(y+40, [[('Belli. Ma poi finiscono. ', SOFT, 400),
                       ('La vostra storia merita di più.', CREMA, 700)]], size=38)
    c.append(b)
    c.append(footer())
    return svg_doc('\n'.join(c), glow_c=PRUGNA)

def c1s3():
    c = [logo(), slide_index(3)]
    c.append(kicker(238, 'la soluzione'))
    t, y = title(360, [[('Un piccolo mondo,', CREMA)], [('tutto vostro.', CORALLO)]], size=96)
    c.append(t)
    b, y = body(y+30, ['Voi due come protagonisti, in pixel art.',
                       'Le vostre foto. Le vostre parole. I vostri posti.',
                       'Un gioco vero, che esiste in una sola copia.'], size=37)
    c.append(b)
    c.append(image_frame(f'{IMG}/room-800.webp', MX, y+44, W-2*MX, 500, rotate=1.1))
    c.append(sprite(f'{IMG}/cuore.webp', MX+40, y+44-40, 84))
    c.append(footer())
    return svg_doc('\n'.join(c))

def c1s4():
    c = [logo(), slide_index(4)]
    c.append(kicker(238, 'come funziona'))
    t, y = title(360, [[('Semplice come', CREMA)], [('un ricordo.', CORALLO)]], size=96)
    c.append(t)
    y += 80
    c.append(step_row(y, 1, 'Ci raccontate la vostra storia', 'foto, date, dettagli: bastano cinque minuti')); y += 175
    c.append(step_row(y, 2, 'La trasformiamo in un gioco', 'con gli sprite di voi due, disegnati apposta')); y += 175
    c.append(step_row(y, 3, 'Ricevete link e QR da regalare', 'si gioca dal telefono, senza installare nulla')); y += 175
    b, y = body(y+20, [[('Pronto in ', SOFT, 400), ('2–5 giorni', CREMA, 700), ('.', SOFT, 400)]], size=38)
    c.append(b)
    c.append(footer())
    return svg_doc('\n'.join(c), glow_c=PRUGNA)

def c1s5():
    c = [logo(), slide_index(5)]
    c.append(kicker(238, 'perché è diverso'))
    t, y = title(360, [[('Unico.', CORALLO)], [('Come voi due.', CREMA)]], size=100)
    c.append(t)
    y += 76
    c.append(check_row(y, 'Esiste in una sola copia al mondo', 'nessun altro avrà mai il vostro gioco')); y += 168
    c.append(check_row(y, 'I protagonisti siete voi', 'sprite disegnati sulle vostre foto')); y += 168
    c.append(check_row(y, 'Sorprese nascoste da scoprire', 'ricordi e messaggi dentro gli oggetti')); y += 168
    c.append(check_row(y, 'Si rigioca per sempre', 'e ogni volta emoziona come la prima'))
    c.append(footer())
    return svg_doc('\n'.join(c))

def c1s6():
    cid = 'full6'
    uri = datauri(f'{IMG}/pop-finestra.webp')
    c = [f"""
  <clipPath id="{cid}"><rect width="{W}" height="{H}"/></clipPath>
  <image href="{uri}" x="0" y="-60" width="{W}" height="{H+120}" preserveAspectRatio="xMidYMid slice"
    clip-path="url(#{cid})"/>
  <rect width="{W}" height="{H}" fill="url(#ovgrad)"/>
"""]
    c.append(logo())
    c.append(slide_index(6))
    t, y = title(H-420, [[('Il momento in cui capisce', CREMA)],
                          [('che quei due pixel', CREMA)],
                          [('siete voi.', CORALLO)]], size=76, x=W/2, anchor='middle', lh=92)
    c.append(t)
    b, y = body(y+26, ['Questo è il regalo. Tutto il resto è tecnica.'],
                size=37, x=W/2, anchor='middle')
    c.append(b)
    c.append(footer())
    return svg_doc_full('\n'.join(c), overlay_defs())

def c1s7():
    c = [slide_index(7)]
    c.append(heart(W/2-72, 300, 9))
    c.append(f'<text x="{W/2}" y="530" text-anchor="middle" font-family="{PIXEL}" '
             f'font-size="30" fill="{CORALLO}">sempre</text>')
    c.append(f'<text x="{W/2}" y="630" text-anchor="middle" font-family="{BALOO}" '
             f'font-weight="800" font-size="104" fill="{CREMA}">Addue</text>')
    b, y = body(720, ['Un posto a due. Per sempre.'], size=44, x=W/2, anchor='middle',
                fill=PESCA, weight=700)
    c.append(b)
    c.append(pill(W/2, 820, 'Prova la demo gratis', size=44))
    b2, _ = body(970, [[('Link in bio  ·  L’Avventura a ', SOFT, 400), ('19,50 €', CREMA, 700)]],
                 size=36, x=W/2, anchor='middle')
    c.append(b2)
    c.append(footer())
    return svg_doc('\n'.join(c), glow_x=W/2, glow_y=420)

# ══════════════════════════════════════════════════════════════
# CAROSELLO 2 — Cosa realizziamo
# ══════════════════════════════════════════════════════════════
def occasione(idx, kick, tit_lines, body_lines, img, rotate=1.4, sprite_img=None, tsize=94):
    c = [logo(), slide_index(idx)]
    c.append(kicker(238, kick))
    t, y = title(352, tit_lines, size=tsize)
    c.append(t)
    b, y = body(y+28, body_lines, size=37)
    c.append(b)
    c.append(image_frame(img, MX, y+42, W-2*MX, H-(y+42)-46, rotate=rotate))
    if sprite_img:
        c.append(sprite(sprite_img, W-MX-180, H-330, 160))
    return svg_doc('\n'.join(c))

def c2s1():
    c = [logo(), slide_index(1)]
    c.append(kicker(238, 'dentro le avventure'))
    t, y = title(352, [[('Cosa costruiamo,', CREMA)], [('davvero.', CORALLO)]], size=96)
    c.append(t)
    b, y = body(y+26, ['Niente mockup finti: ogni scena che vedi',
                       'viene da un gioco SempreAddue giocabile.'], size=37)
    c.append(b)
    c.append(phone(f'{IMG}/village-800.webp', W/2, y+66+430, w=400, rotate=-2))
    return svg_doc('\n'.join(c))

def c2s2():
    return occasione(2, 'per un anniversario',
        [[('La vostra stanza,', CREMA)], [('ricostruita.', CORALLO)]],
        ['Il divano dei film, il giradischi, la finestra',
         'sui fuochi: ogni dettaglio è un vostro ricordo.'],
        f'{IMG}/room-800.webp', rotate=-1.2)

def c2s3():
    return occasione(3, 'per un compleanno',
        [[('Una festa che è', CREMA)], [('un mondo intero.', CORALLO)]],
        ['Come il Villaggio Incantato: si esplora, si parla',
         'con i personaggi, si scoprono gli auguri nascosti.'],
        f'{IMG}/village-800.webp', rotate=1.2)

def c2s4():
    return occasione(4, 'per la proposta',
        [[('La lettera che apre', CREMA)], [('la domanda.', CORALLO)]],
        ['Nascosta nella scrivania: la Richiesta Ufficiale',
         'di Matrimonio. Il sì più nerd della vostra vita.'],
        f'{IMG}/pop-scrivania.webp', rotate=-1.3)

def c2s5():
    return occasione(5, 'i vostri ricordi',
        [[('Le vostre foto,', CREMA)], [('dentro il gioco.', CORALLO)]],
        ['Fotografie vere incastonate nelle sorprese:',
         'si sbloccano una a una, giocando.'],
        f'{IMG}/pop-vinile.webp', rotate=1.3)

def c2s6():
    return occasione(6, 'il finale',
        [[('E un finale che', CREMA)], [('non si dimentica.', CORALLO)]],
        ['Dialoghi scritti per voi, messaggi che solo voi',
         'due capite, e un ultimo momento tutto vostro.'],
        f'{IMG}/pop-finestra.webp', rotate=-1.1)

def c2s7():
    c = [slide_index(7)]
    c.append(sprite(f'{IMG}/ballo.webp', W/2-105, 250, 210))
    t, y = title(700, [[('Quale storia', CREMA)], [('costruiamo per voi?', CORALLO)]],
                 size=88, x=W/2, anchor='middle')
    c.append(t)
    b, y = body(y+26, ['Anniversario, compleanno, proposta —',
                       'o un’occasione che esiste solo per voi due.'],
                size=37, x=W/2, anchor='middle')
    c.append(b)
    c.append(pill(W/2, y+40, 'Gioca la demo · link in bio', size=42))
    b2, _ = body(y+40+150, [[('19,50 € tutto incluso · sprite di voi due compresi', SOFT, 400)]],
                 size=33, x=W/2, anchor='middle')
    c.append(b2)
    c.append(footer())
    return svg_doc('\n'.join(c), glow_x=W/2, glow_y=380)

# ══════════════════════════════════════════════════════════════
# CAROSELLO 3 — Founder Promo
# ══════════════════════════════════════════════════════════════
def c3s1():
    c = [logo(), slide_index(1)]
    c.append(kicker(300, 'solo per i primi', x=W/2, anchor='middle'))
    c.append(f'<text x="{W/2}" y="640" text-anchor="middle" font-family="{BALOO}" '
             f'font-weight="800" font-size="330" fill="{CORALLO}">\u221250%</text>')
    t, y = title(780, [[('per i founder di SempreAddue', CREMA)]], size=54, x=W/2, anchor='middle')
    c.append(t)
    b, y = body(y+30, ['Sul totale dell’ordine. Extra compresi.',
                       'Fino al 6 ottobre 2026.'], size=40, x=W/2, anchor='middle')
    c.append(b)
    c.append(sprite(f'{IMG}/cuore.webp', W/2-52, y+50, 104))
    c.append(footer())
    return svg_doc('\n'.join(c), glow_x=W/2, glow_y=560, glow_c=CORALLO)

def c3s2():
    c = [logo(), slide_index(2)]
    c.append(kicker(238, 'cosa vuol dire founder'))
    t, y = title(360, [[('Chi ci crede per primo,', CREMA)], [('paga la metà.', CORALLO)]], size=88)
    c.append(t)
    b, y = body(y+34, ['SempreAddue è appena nato. I primi ordini',
                       'ci aiutano a crescere — e chi li fa merita',
                       'un trattamento da founder, non da cliente.'], size=39)
    c.append(b)
    c.append(image_frame(f'{SC}/still-2.png', MX, y+50, W-2*MX, H-(y+50)-46, rotate=1.2))
    return svg_doc('\n'.join(c))

def c3s3():
    c = [logo(), slide_index(3)]
    c.append(kicker(238, 'facciamo i conti'))
    t, y = title(360, [[('L’avventura completa,', CREMA)], [('a metà prezzo.', CORALLO)]], size=86)
    c.append(t)
    y += 140
    c.append(f'<text x="{W/2}" y="{y}" text-anchor="middle" font-family="{BALOO}" font-weight="800" '
             f'font-size="88" fill="{SOFT}" text-decoration="line-through" opacity="0.55">19,50 €</text>')
    c.append(f'<text x="{W/2}" y="{y+230}" text-anchor="middle" font-family="{BALOO}" font-weight="800" '
             f'font-size="210" fill="{CORALLO}">9,75 €</text>')
    y += 330
    b, y = body(y, ['con il codice founder, sul totale dell’ordine —',
                    'anche foto, personaggi extra e biglietto QR.'], size=38, x=W/2, anchor='middle')
    c.append(b)
    c.append(footer())
    return svg_doc('\n'.join(c), glow_x=W/2, glow_y=700, glow_c=CORALLO)

def c3s4():
    c = [logo(), slide_index(4)]
    c.append(kicker(238, 'cosa include'))
    t, y = title(360, [[('Tutto incluso.', CREMA)], [('Sul serio.', CORALLO)]], size=100)
    c.append(t)
    y += 76
    c.append(check_row(y, 'Sprite di voi due', 'disegnati sulle vostre foto, compresi nel prezzo')); y += 168
    c.append(check_row(y, '3 sorprese personalizzate', 'con i vostri testi, nascoste nella scena')); y += 168
    c.append(check_row(y, 'Finale su misura', 'dedica, auguri o proposta di matrimonio')); y += 168
    c.append(check_row(y, 'Link privato + QR code', 'pronto da regalare, si gioca subito'))
    c.append(footer())
    return svg_doc('\n'.join(c))

def c3s5():
    c = [logo(), slide_index(5)]
    c.append(kicker(238, 'come avere il codice'))
    t, y = title(360, [[('Trenta secondi,', CREMA)], [('letteralmente.', CORALLO)]], size=96)
    c.append(t)
    y += 80
    c.append(step_row(y, 1, 'Apri il sito dal link in bio', 'sempreaddue.netlify.app')); y += 175
    c.append(step_row(y, 2, 'Lascia la tua email nel riquadro', 'compare da solo: zero spam, promesso')); y += 175
    c.append(step_row(y, 3, 'Ricevi il codice e ordina', 'lo inserisci nel riepilogo: −50% applicato'))
    c.append(footer())
    return svg_doc('\n'.join(c), glow_c=PRUGNA)

def c3s6():
    c = [logo(), slide_index(6)]
    c.append(kicker(300, 'senza trucchi', x=W/2, anchor='middle'))
    t, y = title(430, [[('Fino al', CREMA)], [('6 ottobre 2026.', CORALLO)], [('Poi sparisce.', CREMA)]],
                 size=100, x=W/2, anchor='middle')
    c.append(t)
    b, y = body(y+40, ['Non è una data inventata per farti fretta:',
                       'è la fine del periodo founder. Dopo quel giorno',
                       'il −50% non torna più, per nessuno.'], size=39, x=W/2, anchor='middle')
    c.append(b)
    c.append(sprite(f'{IMG}/cuore.webp', W/2-45, y+60, 90))
    c.append(footer())
    return svg_doc('\n'.join(c), glow_x=W/2, glow_y=500)

def c3s7():
    c = [slide_index(7)]
    c.append(heart(W/2-64, 260, 8))
    t, y = title(560, [[('Diventa', CREMA)], [('founder.', CORALLO)]], size=140,
                 x=W/2, anchor='middle')
    c.append(t)
    b, y = body(y+24, ['La vostra storia, a metà prezzo,',
                       'nella prima generazione di avventure.'], size=40, x=W/2, anchor='middle')
    c.append(b)
    c.append(pill(W/2, y+44, 'Richiedi il codice · link in bio', size=44))
    b2, _ = body(y+44+156, [[('−50% sul totale · fino al 6 ottobre 2026', PESCA, 700)]],
                 size=35, x=W/2, anchor='middle')
    c.append(b2)
    c.append(footer())
    return svg_doc('\n'.join(c), glow_x=W/2, glow_y=440, glow_c=CORALLO)

# ══════════════════════════════════════════════════════════════
# PROFILO 1080x1080
# ══════════════════════════════════════════════════════════════
def profile():
    S = 1080
    inner = f"""
  <rect width="{S}" height="{S}" fill="url(#bggrad)"/>
  <ellipse cx="{S/2}" cy="{S/2-40}" rx="500" ry="440" fill="{ROSA}" opacity="0.14"/>
  <ellipse cx="{S/2}" cy="{S-140}" rx="480" ry="300" fill="{CORALLO}" opacity="0.08"/>
  {stars(11, 30, 0, S)}
  {heart(S/2 - 8*33, S/2 - 8*33 - 40, 33)}
  <text x="{S/2}" y="{S-190}" text-anchor="middle" font-family="{PIXEL}"
    font-size="34" fill="{CORALLO}">sempre</text>
  <text x="{S/2}" y="{S-105}" text-anchor="middle" font-family="{BALOO}"
    font-weight="800" font-size="92" fill="{CREMA}">Addue</text>
"""
    doc = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{S}" height="{S}" viewBox="0 0 {S} {S}">
<defs>
  <linearGradient id="bggrad" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#181019"/><stop offset="0.55" stop-color="{NOTTE}"/>
    <stop offset="1" stop-color="{NOTTE2}"/>
  </linearGradient>
  <style>{font_css()}</style>
</defs>
{inner}
</svg>"""
    return doc

# ══════════════════════════════════════════════════════════════
if __name__ == '__main__':
    slides = {
        'carousel-01': [c1s1, c1s2, c1s3, c1s4, c1s5, c1s6, c1s7],
        'carousel-02': [c2s1, c2s2, c2s3, c2s4, c2s5, c2s6, c2s7],
        'carousel-03': [c3s1, c3s2, c3s3, c3s4, c3s5, c3s6, c3s7],
    }
    for folder, fns in slides.items():
        for i, fn in enumerate(fns, 1):
            write(f'{OUT}/{folder}/slide-{i:02d}.svg', fn())
    write(f'{OUT}/profile/profilo.svg', profile())
    print('fatto')
