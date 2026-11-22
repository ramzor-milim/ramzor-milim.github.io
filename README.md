# רמזור מילים

אתר לתרגול אוצר מילים לפסיכומטרי (אנגלית ועברית) בשיטת רמזור: כל מילה מסומנת בירוק (יודעת), כתום (לא בטוחה) או אדום (לא יודעת), ומתרגלים רק את מה שצריך.

**לאתר:** https://ramzor-milim.github.io/

## מה יש באתר
- תרגול לפי יחידות, רשימת מילים עם חיפוש, מעקב התקדמות ויעדים
- אסוציאציות לכל מילה, עם אפשרות לשתף אותן עם משתמשים אחרים (לייקים, מועדפים, הסתרה ודיווח)
- משתמש בחינם (Google או אימייל) לסנכרון בין מכשירים, דרך Firebase

## איך זה בנוי
האתר עצמו הוא קובץ אחד, `index.html`, שנבנה מקבצי המקור שבתיקייה `src/`:

| קובץ | מה הוא |
|---|---|
| `src/ramzor-milim.html` | קוד המקור של האפליקציה (ממשק, תרגול, רשימות) |
| `src/build.py` | סקריפט הבנייה: מוסיף חשבונות, אסוציאציות משותפות, דיווחים וניהול, ומטמיע את רשימת המילים |
| `src/words.json` | רשימת המילים והפירושים |
| `src/firebase-config.json` | הגדרות ה-Firebase הציבוריות (בלעדיהן האתר עובד בלי חשבונות) |
| `firestore.rules` | כללי האבטחה של Firestore, כפי שהם מפורסמים |

בנייה (Python 3, בלי חבילות נוספות), מתיקיית השורש של הפרויקט:

```
python src/build.py
```

הנתונים נשמרים בדפדפן, ולמשתמשים רשומים גם ב-Firebase (Authentication + Firestore).
הגדרות ה-Firebase ומפתח הטופס (Web3Forms) שמופיעים בקוד ציבוריים מעצם הגדרתם. ההגנה על הנתונים נעשית בכללי האבטחה של Firestore בצד השרת (`firestore.rules`).

## רישיון
הקוד מופץ ברישיון MIT (ראו `LICENSE`).
רשימת המילים והפירושים לקוחים ממילוני העברית והאנגלית של קורס "הפסיכומטרי של המדינה" בקמפוס IL, והזכויות עליהם שמורות לבעליהם. הרישיון אינו חל עליהם (כולל `src/words.json`).

---

**Ramzor Milim** is a free traffic-light vocabulary trainer for the Israeli psychometric exam (English and Hebrew). The site is a single static `index.html` built from `src/` with `python src/build.py` (Python 3, no dependencies); it uses Firebase for optional accounts and shared associations, protected by `firestore.rules`. The code is MIT-licensed. The word lists come from the Campus IL "הפסיכומטרי של המדינה" course dictionaries and are not covered by this license.
