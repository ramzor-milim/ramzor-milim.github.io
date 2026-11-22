# רמזור מילים

אתר לתרגול אוצר מילים לפסיכומטרי (אנגלית ועברית) בשיטת רמזור: כל מילה מסומנת בירוק (יודעת), כתום (לא בטוחה) או אדום (לא יודעת), ומתרגלים רק את מה שצריך.

**לאתר:** https://ramzor-milim.github.io/

## מה יש באתר
- תרגול לפי יחידות, רשימת מילים עם חיפוש, מעקב התקדמות ויעדים
- אסוציאציות לכל מילה, עם אפשרות לשתף אותן עם משתמשים אחרים (לייקים, מועדפים, הסתרה ודיווח)
- משתמש בחינם (Google או אימייל) לסנכרון בין מכשירים, דרך Firebase

## איך זה בנוי
הכול בקובץ אחד, `index.html`, בלי שלב בנייה. הנתונים נשמרים בדפדפן, ולמשתמשים רשומים גם ב-Firebase (Authentication + Firestore).

הגדרות ה-Firebase ומפתח הטופס (Web3Forms) שמופיעים בקוד ציבוריים מעצם הגדרתם. ההגנה על הנתונים נעשית בכללי האבטחה של Firestore בצד השרת.

## רישיון
הקוד מופץ ברישיון MIT (ראו `LICENSE`).
רשימת המילים והפירושים לקוחים ממילוני העברית והאנגלית של קורס "הפסיכומטרי של המדינה" בקמפוס IL, והזכויות עליהם שמורות לבעליהם. הרישיון אינו חל עליהם.

---

**Ramzor Milim** is a free traffic-light vocabulary trainer for the Israeli psychometric exam (English and Hebrew). It is a single static `index.html` that uses Firebase for optional accounts and shared associations. The code is MIT-licensed. The word lists come from the Campus IL "הפסיכומטרי של המדינה" course dictionaries and are not covered by this license.
