<div dir="rtl">

<p align="center"><img src="assets/brand/logo.png" alt="סמל הפרויקט שבזי 58 · אחד העם 1" width="220"></p>

# שבזי 58 · אחד העם 1 — נווה צדק

הדמיה תלת-ממדית, תכנית עסקית ומודל פיננסי לנכס לשימור בגוש 7422, חלקות 47–48 (473 מ״ר), בפינת שבזי, אחד העם, תחכמוני ורבי יהודה חסיד.

| מה | קובץ |
| --- | --- |
| הדמיה תלת-ממדית (מצב קיים, חלופת שימור + תוספת, מעטפת זכויות, פנים משוער) | [`index.html`](index.html) |
| התכנית העסקית כדף אינטרנט | [`bizplan.html`](bizplan.html) |
| התכנית העסקית כקובץ טקסט (נקרא ישירות בגיטהאב) | [`BUSINESS_PLAN.md`](BUSINESS_PLAN.md) |
| המודל הפיננסי (Python) | [`model/`](model/) |
| דפי הזכויות של העירייה | [`data/zchuyot/`](data/zchuyot/) |
| נתוני GIS של העירייה (חלקות, מבנים, רחובות, שימור, עצים) | [`data/gis/`](data/gis/) |

## איך פותחים

**במחשב:** לחיצה כפולה על `index.html` או `bizplan.html`. הכל מקומי (Three.js בתיקייה `vendor/`), ורק הגופנים נטענים מהאינטרנט. בלי אינטרנט הדפים עובדים עם גופן מערכת.

**ב-VS Code:** File → Open Folder על התיקייה הזו. כדי לצפות בדפים מתוך VS Code אפשר להתקין את התוסף Live Server, ללחוץ קליק ימני על `index.html` ולבחור "Open with Live Server".

## העלאה לגיטהאב ושיתוף

בטרמינל של VS Code (Terminal → New Terminal), מתוך התיקייה:

```bash
git init
git add .
git commit -m "Neve Tzedek — 3D model, business plan, financial model"
git branch -M main
git remote add origin https://github.com/<USER>/<REPO>.git
git push -u origin main
```

את `<USER>/<REPO>` מחליפים בשם המשתמש ובשם הריפו שיצרתם ב-github.com (New repository, בלי README).

**קישור לשיתוף (GitHub Pages):** בריפו → Settings → Pages → Source: Deploy from a branch → Branch: `main`, תיקייה `/ (root)` → Save. אחרי דקה-שתיים ההדמיה תהיה זמינה בכתובת `https://<USER>.github.io/<REPO>/`, והתכנית העסקית בכתובת `https://<USER>.github.io/<REPO>/bizplan.html`.

> **שימו לב:** ריפו ציבורי (Public) — כל אחד באינטרנט יכול לראות אותו, כולל דפי הזכויות והמספרים. אם זה מיועד רק לשותפים, צרו ריפו פרטי (Private) והזמינו אותם ב-Settings → Collaborators. GitHub Pages בריפו פרטי דורש מנוי בתשלום; בלי מנוי, השותפים יורידו את הריפו ויפתחו את הקבצים אצלם.

## המודל הפיננסי

```bash
cd model
python3 financial_model.py   # ערך נוכחי לכל חלופה בתרחיש הבסיס
python3 analysis.py          # שלושה תרחישים + רגישות, כותב results.json
python3 make_charts.py       # מצייר מחדש את שלושת הגרפים ב-assets/
```

כל ההנחות נמצאות במילון `BASE` בראש `financial_model.py` (דמי שכירות, מחירי דירות, עלויות בנייה, היטל השבחה, ריבית ועוד). התרחיש הפסימי והאופטימי מוגדרים ב-`analysis.py`. משנים הנחה, מריצים את שלושת הפקודות, ומעדכנים את המספרים בטקסט של `BUSINESS_PLAN.md` בהתאם.

**ההנחה החלשה ביותר היום:** דמי השכירות הנוכחיים (`rent_now` = 170 ₪ למ״ר לחודש) הם הערכה. כדאי להחליף אותם בסכום האמיתי מחוזי השכירות.

אחרי עריכה של `BUSINESS_PLAN.md`, הדף `bizplan.html` נבנה מחדש כך:

```bash
pip install markdown
python3 tools/build_bizplan.py
```

## מבנה התיקייה

```
index.html            ההדמיה התלת-ממדית
bizplan.html          התכנית העסקית (נבנית מ-BUSINESS_PLAN.md)
BUSINESS_PLAN.md      התכנית העסקית
assets/               גרפים (SVG) — נוצרים ב-model/make_charts.py
model/                המודל הפיננסי
data/gis/             נתוני GIS גולמיים (JSON)
data/gis.js           אותם נתונים בפורמט שההדמיה טוענת (tools/build_gis.py)
data/zchuyot/         דפי הזכויות של חלקות 47 ו-48
vendor/               Three.js r128 (רישיון MIT)
tools/                סקריפטים לבנייה מחדש של הדפים והנתונים
```

## מקורות והסתייגויות

- דפי הזכויות של עיריית תל אביב-יפו לחלקות 47 ו-48, גוש 7422 (הופקו ב-27/09/2026).
- שכבות ה-GIS של העירייה ([IView2](https://gisn.tel-aviv.gov.il/arcgis/rest/services/IView2/MapServer)): חלקות, מבנים וגבהים, מבנים לשימור, צירי רחוב, כתובות, עצים — נשלפו ב-29/09/2026.
- חזיתות המבנה לפי Google Street View (2011, 2015, 2018). מיקום העצים והפריסה הפנימית משוערים.
- נתוני שוק ומקורות נוספים מפורטים בסוף [`BUSINESS_PLAN.md`](BUSINESS_PLAN.md).

ההדמיה עקרונית ואינה מבוססת על מפת מדידה. התכנית אינה ייעוץ משפטי, שמאי, תכנוני או מיסויי; הזכויות נקבעות סופית רק בהיתר בנייה מול הוועדה המקומית.

</div>
