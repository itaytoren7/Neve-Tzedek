# Draws the three business-plan charts as SVG files in ../assets, straight from the model.
# Run:  python3 make_charts.py
# Change an assumption in financial_model.py / analysis.py, re-run, and the charts follow.
import os
from analysis import scenarios, sensitivity

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'assets')
os.makedirs(OUT, exist_ok=True)

FONT = "'Assistant','Arial Hebrew','Noto Sans Hebrew',Arial,sans-serif"
INK, QUIET, GRID, AXIS = '#1b221e', '#5b6660', '#e3e6e1', '#9aa39d'
ACCENT, MUTED = '#2d6d61', '#b9bfb8'
GOOD, BAD = '#7fbf93', '#e0a09a'


def esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def text(x, y, s, size=13, anchor='end', weight=400, fill=INK, rtl=True):
    # anchor is physical: 'end' = the text ends (right edge) at x, 'start' = it begins (left edge) at x.
    # In an rtl run SVG flips start/end, so translate the physical anchor to the logical one.
    a = {'end': 'start', 'start': 'end'}.get(anchor, anchor) if rtl else anchor
    d = ' direction="rtl"' if rtl else ''
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{a}"{d}>{esc(s)}</text>')


def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'font-family="{FONT}" role="img" aria-label="{esc(title)}">\n'
            f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n' + '\n'.join(body) + '\n</svg>\n')


def chart_alternatives():
    sc = scenarios()
    rows = [('C', 'ג. שימור + תוספת (עצמי)'), ('E', 'ה. עסקת קומבינציה'), ('B0', 'ב׳. להמשיך כמו שזה'),
            ('A', 'א. מכירה היום'), ('B', 'ב. שיפוץ שימור בלבד'), ('D', 'ד. מלון בוטיק')]
    data = [(k, lbl, sc['low'][k] / 1e6, sc['base'][k] / 1e6, sc['high'][k] / 1e6) for k, lbl in rows]
    W, y0, step = 860, 130, 48
    H = y0 + step * len(data) + 20
    X = lambda v: 60 + (v + 15) * 11.5
    sale, best = next(d for d in data if d[0] == 'A'), data[0]
    b = [text(W - 20, 32, 'פיתוח עצמי מוסיף על מכירה היום — והוא גם החלופה עם הטווח הרחב ביותר', 17, weight=700),
         text(W - 20, 56, f'בסיס: {best[3]:.1f} מ׳ ₪ מול {sale[3]:.1f} מ׳ ₪ במכירה היום · פער של {best[3] - sale[3]:.1f} מ׳ ₪', 13, fill=QUIET),
         text(W - 20, 76, 'ערך נוכחי נקי לבעלים בהיוון 7% ל-10 שנים, מיליוני ₪ · נקודה = תרחיש בסיס, קו = פסימי עד אופטימי', 12, fill=QUIET)]
    for v in range(-10, 36, 5):
        b.append(f'<line x1="{X(v):.1f}" x2="{X(v):.1f}" y1="{y0 - 22}" y2="{H - 26}" stroke="{GRID}"/>')
        b.append(text(X(v), H - 8, f'{v}', 11, anchor='middle', fill=QUIET, rtl=False))
    b.append(f'<line x1="{X(0):.1f}" x2="{X(0):.1f}" y1="{y0 - 22}" y2="{H - 26}" stroke="{AXIS}"/>')
    b.append(f'<line x1="{X(sale[3]):.1f}" x2="{X(sale[3]):.1f}" y1="{y0 - 30}" y2="{H - 26}" stroke="{QUIET}" stroke-dasharray="4 4"/>')
    b.append(text(X(sale[3]) + 4, y0 - 34, f'מכירה היום: {sale[3]:.1f}', 11, anchor='start', fill=QUIET))
    for i, (k, lbl, lo, base, hi) in enumerate(data):
        y = y0 + i * step
        c = ACCENT if k == 'C' else MUTED
        b.append(text(W - 20, y + 4, lbl, 13.5, weight=700 if k == 'C' else 400))
        b.append(f'<line x1="{X(lo):.1f}" x2="{X(hi):.1f}" y1="{y}" y2="{y}" stroke="{c}" stroke-width="3" stroke-linecap="round"/>')
        b.append(f'<circle cx="{X(base):.1f}" cy="{y}" r="7" fill="{c}"/>')
        b.append(text(X(base), y - 12, f'{base:.1f}', 13, anchor='middle', weight=700, rtl=False))
        b.append(text(X(lo) - 8, y + 4, f'{lo:.1f}', 11.5, anchor='end', fill=QUIET, rtl=False))
        b.append(text(X(hi) + 8, y + 4, f'{hi:.1f}', 11.5, anchor='start', fill=QUIET, rtl=False))
    return svg(W, H, b, 'השוואת חלופות — ערך נוכחי לבעלים')


def chart_sensitivity():
    base, rows = sensitivity()
    base /= 1e6
    W, y0, step = 860, 110, 44
    H = y0 + step * len(rows) + 10
    X = lambda v: 60 + (v - 15) * 50
    b = [text(W - 20, 32, 'מחיר הדירות והיקף התוספת קובעים את ערך הפיתוח יותר מכל השאר', 17, weight=700),
         text(W - 20, 56, 'ערך נוכחי של חלופה ג׳ במיליוני ₪, כשמשנים הנחה אחת בכל פעם', 12.5, fill=QUIET),
         text(W - 20, 76, 'אדום = הנחה פסימית · ירוק = הנחה אופטימית', 12, fill=QUIET)]
    b.append(f'<line x1="{X(base):.1f}" x2="{X(base):.1f}" y1="{y0 - 22}" y2="{H - 8}" stroke="{QUIET}" stroke-dasharray="4 4"/>')
    b.append(text(X(base), y0 - 28, f'בסיס {base:.1f}', 11.5, anchor='middle', fill=QUIET))
    for i, r in enumerate(rows):
        y = y0 + i * step
        lo, hi = r['lo'] / 1e6, r['hi'] / 1e6
        b.append(text(W - 20, y, r['label'], 13.5))
        b.append(text(W - 20, y + 16, r['detail'], 11, fill=QUIET))
        b.append(f'<rect x="{X(lo):.1f}" y="{y - 9}" width="{X(base) - X(lo):.1f}" height="18" fill="{BAD}"/>')
        b.append(f'<rect x="{X(base):.1f}" y="{y - 9}" width="{X(hi) - X(base):.1f}" height="18" fill="{GOOD}"/>')
        b.append(text(X(lo) - 6, y + 4, f'{lo:.1f}', 11.5, anchor='end', fill=QUIET, rtl=False))
        b.append(text(X(hi) + 6, y + 4, f'{hi:.1f}', 11.5, anchor='start', fill=QUIET, rtl=False))
    return svg(W, H, b, 'רגישות חלופה ג׳')


def chart_roadmap():
    phases = [('הכנה', '10/2026–03/2027', ['הסכם שותפים, חוזים', 'סקרים ושמאי', 'פגישה במחלקת השימור', 'כ-0.5 מ׳ ₪'], True),
              ('תכנון ותיק תיעוד', '04/2027–03/2028', ['אדריכל שימור', 'תכנון מוקדם', 'תיאום עם העירייה'], False),
              ('היתר בנייה', '04/2028–03/2029', ['בקשה וּוועדה', 'שומת היטל השבחה', 'מימון ומכירות מוקדמות'], False),
              ('ביצוע ואכלוס', '04/2029–06/2031', ['פינוי שוכרים', 'שימור ובנייה', 'מסירה והשכרת המסחר'], False)]
    gates = [('שער 1: כל השותפים', 'מסכימים להמשיך'), ('שער 2: היקף תוספת', 'ממשיכים אם מעל 330 מ״ר'), ('שער 3: היתר + ליווי', 'ו-40% מכירות מוקדמות')]
    W, H, BW, gap, y0, BH = 860, 330, 172, 44, 80, 138
    bx = lambda i: W - 20 - BW - i * (BW + gap)
    mid = y0 + BH / 2
    b = [text(W - 20, 32, 'מההחלטה ועד אכלוס: כארבע וחצי שנים, עם שלושה שערי החלטה', 17, weight=700),
         text(W - 20, 56, 'חלופה ג׳ או ה׳, בהנחה שמתחילים ב-10/2026 ושהשוכרים לא מעכבים', 12, fill=QUIET)]
    for i, (name, dates, lines, main) in enumerate(phases):
        x = bx(i)
        b.append(f'<rect x="{x}" y="{y0}" width="{BW}" height="{BH}" rx="9" fill="{"#e3efeb" if main else "#ffffff"}" '
                 f'stroke="{ACCENT if main else AXIS}" stroke-width="{2 if main else 1.2}"/>')
        b.append(text(x + BW - 12, y0 + 26, name, 14, weight=700))
        b.append(text(x + BW - 12, y0 + 45, dates, 11.5, fill=QUIET, rtl=False))
        for j, ln in enumerate(lines):
            b.append(text(x + BW - 12, y0 + 72 + j * 17, ln, 12, fill=QUIET if ln.startswith('כ-') else INK))
    for i, (g1, g2) in enumerate(gates):
        gx = bx(i) - gap / 2
        b.append(f'<line x1="{bx(i)}" x2="{bx(i + 1) + BW}" y1="{mid}" y2="{mid}" stroke="{AXIS}" stroke-width="1.2"/>')
        b.append(f'<polygon points="{gx - 12},{mid} {gx},{mid - 12} {gx + 12},{mid} {gx},{mid + 12}" fill="#f1f3ef" stroke="{AXIS}" stroke-width="1.2"/>')
        b.append(f'<line x1="{gx}" x2="{gx}" y1="{mid + 13}" y2="{y0 + BH + 22}" stroke="{AXIS}" stroke-dasharray="3 3"/>')
        b.append(text(gx, y0 + BH + 40, g1, 12, anchor='middle', weight=700))
        b.append(text(gx, y0 + BH + 57, g2, 11.5, anchor='middle', fill=QUIET))
    b.append(text(W - 20, H - 14, 'בכל שער אפשר לעצור ולמכור — והנכס שווה יותר ככל שהתכנון מתקדם', 12, fill=QUIET))
    return svg(W, H, b, 'לוח זמנים משוער')


if __name__ == '__main__':
    for name, fn in (('alternatives.svg', chart_alternatives), ('sensitivity.svg', chart_sensitivity), ('roadmap.svg', chart_roadmap)):
        open(os.path.join(OUT, name), 'w', encoding='utf-8').write(fn())
        print('wrote assets/' + name)
