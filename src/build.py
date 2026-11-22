"""Build a self-contained index.html (no Claude runtime) from the artifact page + words.json.

Saving: the browser always; optionally a username/password account (Firebase Auth + Firestore)
when src/firebase-config.json exists.

Usage (from the repository root):  python src/build.py
Writes index.html in the repository root. Set RAMZOR_OUT=<folder>/ to build somewhere else (e.g. a preview).
"""
import json, os, re, tempfile

ROOT = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/") + "/"   # this folder (src/)
REPO = os.path.dirname(ROOT.rstrip("/")) + "/"
src = open(os.environ.get("RAMZOR_SRC", ROOT + "ramzor-milim.html"), encoding="utf-8").read()
words = json.load(open(ROOT + "words.json", encoding="utf-8"))
cfg_path = ROOT + "firebase-config.json"
WEB3FORMS_KEY = "d0177881-4491-482a-bbd6-4b688f41f151"   # access key from web3forms.com (sent to the owner's Gmail)
firebase_config = json.load(open(cfg_path, encoding="utf-8")) if os.path.exists(cfg_path) else None

head_part, rest = src.split('<div class="app"', 1)
body_html, script = rest.split("<script>", 1)
body_html = '<div class="app"' + body_html
script = script.rsplit("</script>", 1)[0]

# --- head ---
head_part = head_part.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', "")
extra_css = """<style>
:root { color-scheme: light; padding-top: env(safe-area-inset-top, 0px); padding-bottom: env(safe-area-inset-bottom, 0px); }
body { margin: 0; } img { max-width: 100%; } [hidden] { display: none !important; }
.site-counts { display: inline-flex; gap: 12px; justify-content: center; flex-wrap: wrap; font-weight: 600; color: var(--ink); font-variant-numeric: tabular-nums; }
.backup { display: flex; gap: 8px; justify-content: center; flex-wrap: wrap; margin-top: 4px; }
.backup button { border: 1px solid var(--line); background: var(--surface); border-radius: 10px; padding: 6px 12px; font-weight: 600; font-size: .82rem; }
.acct { margin-inline-start: auto; border: 1px solid var(--line); background: var(--surface); border-radius: 99px; padding: 5px 12px; font-weight: 600; font-size: .85rem; display: inline-flex; align-items: center; gap: 6px; max-width: 50%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.acct i { width: 8px; height: 8px; border-radius: 50%; background: var(--new); flex: none; }
.acct[data-in="true"] i { background: var(--green); }
dialog { border: 1px solid var(--line); border-radius: 16px; background: var(--surface); color: var(--ink); width: min(92vw, 380px); padding: 20px; }
dialog::backdrop { background: rgb(0 0 0 / .45); }
dialog h2 { margin: 0 0 6px; font-family: var(--display); font-size: 1.4rem; }
dialog form, dialog .pane { display: grid; gap: 8px; }
dialog label { font-size: .85rem; font-weight: 700; color: var(--muted); }
dialog input { width: 100%; border: 1px solid var(--line); border-radius: 10px; padding: 9px 12px; background: var(--bg); }
dialog .note { margin: 0; color: var(--muted); font-size: .85rem; }
dialog .err { margin: 0; color: var(--red); font-size: .88rem; font-weight: 600; min-height: 1.2em; }
dialog .btns { display: flex; gap: 8px; flex-wrap: wrap; }
dialog .btns button { flex: 1 1 140px; }
dialog h2:focus { outline: none; }
dialog .nick { border-top: 1px solid var(--line); padding-top: 10px; margin-top: 4px; }
dialog .nick-row { display: flex; gap: 8px; }
dialog .nick-row input { flex: 1; min-width: 0; }
dialog .nick-row button { flex: none; }
dialog .forgot { justify-self: start; font-size: .85rem; }
dialog .nick-out { border-top: 0; padding-top: 0; margin-top: 0; border-bottom: 1px solid var(--line); padding-bottom: 6px; display: grid; gap: 6px; }
dialog .merge { border-top: 1px solid var(--line); padding-top: 10px; margin-top: 4px; display: grid; gap: 8px; }
dialog .merge > .link { justify-self: start; font-size: .9rem; }
dialog #mergeBox { display: grid; gap: 8px; }
dialog #mergeBox[hidden] { display: none; }
dialog #mergeForm { display: grid; gap: 6px; }
dialog .nick-ok { color: var(--green); font-weight: 600; min-height: 1.2em; }
dialog .secondary { border: 1.5px solid var(--accent); background: transparent; color: var(--accent); border-radius: 12px; padding: 9px 16px; font-weight: 700; }
dialog .google { border: 1px solid var(--line); background: var(--bg); border-radius: 12px; padding: 10px 16px; font-weight: 700; display: flex; align-items: center; justify-content: center; gap: 10px; width: 100%; }
dialog .google svg { width: 18px; height: 18px; flex: none; }
dialog .or { display: flex; align-items: center; gap: 10px; color: var(--muted); font-size: .82rem; margin-block: 4px; }
dialog .or::before, dialog .or::after { content: ""; flex: 1; border-top: 1px solid var(--line); }

dialog .primary:disabled, dialog .secondary:disabled { opacity: .5; cursor: default; }
.fb-link { font-size: .85rem; }
.gh-link { font-size: .8rem; color: var(--muted); justify-self: center; }
.gh-link:hover { color: var(--accent); }
.fb-top span { background: var(--green-soft); color: var(--green); font-size: .75rem; }
/* phone: login + suggestions share the top row; how it works becomes its ? circle so the suggestions button keeps its words */
@media (max-width: 560px) {
  .title-row:has(.acct:not([hidden])) { flex-wrap: nowrap; gap: 6px; }
  .title-row:has(.acct:not([hidden])) h1 { white-space: nowrap; }
  .title-row:has(.acct:not([hidden])) .how-link:not(.fb-top) { font-size: 0; gap: 0; padding: 4px; }
  .title-row:has(.acct:not([hidden])) .how-link.fb-top { font-size: .78rem; gap: 4px; padding: 4px 8px 4px 5px; white-space: nowrap; flex: none; }
  .title-row .fb-top span { width: 18px; height: 18px; }
  .title-row .acct { max-width: 110px; min-width: 0; }
}
@media (max-width: 400px) {
  .title-row:has(.acct:not([hidden])) { gap: 4px; }
  .title-row:has(.acct:not([hidden])) h1 { font-size: 1.15rem; }
  .title-row:has(.acct:not([hidden])) .lights { transform: scale(.85); }
  .title-row:has(.acct:not([hidden])) .how-link.fb-top { font-size: .72rem; padding: 3px 6px 3px 4px; }
  .title-row .acct { max-width: 96px; padding-inline: 8px; font-size: .78rem; }
}
.note-meta button.admin-note { color: var(--red); }
#admDlg { width: min(94vw, 560px); }
dialog .adm-list { list-style: none; margin: 0; padding: 0; display: grid; gap: 6px; max-height: 45vh; overflow: auto; }
dialog .adm-list li { border: 1px solid var(--line); border-radius: 10px; padding: 8px 10px; display: grid; gap: 4px; background: var(--bg); }
dialog .adm-list .adm-top { display: flex; justify-content: space-between; gap: 8px; font-size: .8rem; color: var(--muted); }
dialog .adm-list .adm-text { white-space: pre-wrap; overflow-wrap: anywhere; font-size: .92rem; }
dialog .adm-list button, dialog .adm-danger { color: var(--red); }
dialog .adm-list button { border: 0; background: none; padding: 4px 2px; font-weight: 600; text-decoration: underline; text-underline-offset: 3px; }
dialog .adm-status { font-weight: 700; margin: 0; }
dialog .adm-notify { border: 1px solid var(--line); border-radius: 10px; padding: 8px 12px; margin: 0; display: grid; gap: 6px; }
dialog .adm-notify legend { font-weight: 700; padding: 0 4px; }
dialog .adm-notify label { display: flex; align-items: center; gap: 8px; font-weight: 400; margin: 0; cursor: pointer; }
dialog .adm-notify input { width: 18px; height: 18px; flex: none; margin: 0; accent-color: var(--accent); }
dialog .adm-tabs { display: flex; gap: 6px; flex-wrap: wrap; }
dialog .adm-tabs button { border: 1px solid var(--line); background: var(--bg); border-radius: 99px; padding: 5px 12px; font-weight: 600; font-size: .85rem; color: var(--ink); }
dialog .adm-tabs button[aria-pressed="true"] { border-color: var(--accent); background: var(--accent); color: var(--accent-ink); }
dialog .adm-list li.adm-user { cursor: pointer; }
dialog .adm-list .adm-user-row { display: flex; justify-content: space-between; gap: 8px; align-items: center; }
dialog .adm-list .adm-user-row button { color: var(--accent); }
.adm-footer { font-size: .85rem; color: var(--red); }
dialog .adm-status[data-banned="true"] { color: var(--red); }
dialog .adm-uid { font-family: monospace; font-size: .78rem; color: var(--muted); overflow-wrap: anywhere; margin: 0; }
.note-meta button.report-note { color: var(--muted); }
dialog .rep-quote { margin: 0; padding: 8px 12px; border-inline-start: 3px solid var(--line); background: var(--bg); border-radius: 8px; font-size: .9rem; white-space: pre-wrap; overflow-wrap: anywhere; max-height: 7.5em; overflow: auto; }
dialog textarea { width: 100%; box-sizing: border-box; min-height: 120px; resize: vertical; border: 1px solid var(--line); border-radius: 10px; padding: 9px 12px; background: var(--bg); line-height: 1.5; }
dialog .fb-kind { display: flex; gap: 8px; }
dialog .fb-kind label { flex: 1; display: flex; align-items: center; justify-content: center; gap: 6px; border: 1px solid var(--line); border-radius: 10px; padding: 8px; cursor: pointer; color: var(--ink); font-size: .9rem; }
dialog .fb-kind input { width: auto; margin: 0; accent-color: var(--accent); }
dialog .fb-kind label:has(input:checked) { border-color: var(--accent); background: color-mix(in srgb, var(--accent) 10%, transparent); }
</style>
"""
head = (
    '<!doctype html>\n<html lang="he" dir="rtl">\n<head>\n<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
    '<meta name="apple-mobile-web-app-capable" content="yes">\n'
    '<meta name="mobile-web-app-capable" content="yes">\n'
    '<meta name="apple-mobile-web-app-title" content="רמזור מילים">\n'
    '<meta name="theme-color" content="#f3f5f8">\n'
    + head_part + extra_css + "</head>\n<body>\n"
)

# --- account button in the unit row (on phones the page script moves it up next to "how it works") ---
body_html = body_html.replace(
    '>↺ איפוס</button>\n    </div>',
    '>↺ איפוס</button>\n'
    '      <button type="button" class="acct" id="acctBtn" data-in="false" hidden><i></i><span id="acctLabel">התחברות</span></button>\n'
    '    </div>')

# --- "suggestions / report" button in the top row, after "how it works" (on phones the login button joins that row); opens the same window as the footer link ---
if firebase_config:
    _how = 'איך זה עובד</button>\n'
    assert body_html.count(_how) == 1
    body_html = body_html.replace(_how, _how + '        <button type="button" class="how-link fb-top" id="fbTop"><span aria-hidden="true">💡</span>הצעות ודיווח</button>\n', 1)

# --- footer: browser saving + backup/restore ---
body_html = re.sub(
    r'<span class="sync" id="sync".*?</span></span>',
    '<span class="site-counts" id="siteCounts" hidden></span>\n'
    '<span class="sync" id="sync"><i></i><span id="syncText">ההתקדמות נשמרת בדפדפן הזה</span></span>\n'
    + ('<button type="button" class="link adm-footer" id="admFooter" hidden>⚙️ ניהול האתר</button>\n' if firebase_config else "")
    + ('<button type="button" class="link fb-link" id="fbOpen">הצעות לשיפור / דיווח על בעיה</button>\n' if firebase_config else "")
    + '<a class="gh-link" href="https://github.com/ramzor-milim/ramzor-milim.github.io" target="_blank" rel="noopener">קוד פתוח ב-GitHub</a>\n'
    + ("" if firebase_config else  # accounts replace backup files
    '    <div class="backup">\n'
    '      <button type="button" id="exportBtn">שמירת גיבוי לקובץ</button>\n'
    '      <button type="button" id="importBtn">שחזור מגיבוי</button>\n'
    '      <input type="file" id="importFile" accept=".json,application/json" hidden>\n'
    '    </div>\n'
    '    <span id="backupMsg" role="status"></span>'),
    body_html, flags=re.S)

# --- account dialog ---
body_html += """
<dialog id="localTip" dir="rtl" lang="he">
  <div class="pane">
    <h2 tabindex="-1" autofocus>האסוציאציה נשמרה ✓</h2>
    <p class="note">כרגע, בלי משתמש, האסוציאציות שלך נשמרות רק בדפדפן הזה. אם תחליפו מכשיר או תנקו את הדפדפן, הן ילכו לאיבוד.</p>
    <p class="note">עם משתמש (בחינם) הן נשמרות בכל המכשירים, ואפשר גם לשתף אותן עם אחרים ולראות אסוציאציות של אחרים. מה שכבר כתבתם יעבור למשתמש אוטומטית.</p>
    <div class="btns"><button type="button" class="primary" id="localTipSignup">הירשמו בחינם</button><button type="button" id="localTipOk">הבנתי</button></div>
    <p class="note tip-login">כבר יש לך משתמש? <button type="button" class="link" id="localTipLogin">להתחברות</button></p>
  </div>
</dialog>"""
body_html += """
<dialog id="acctDlg" dir="rtl" lang="he">
  <div class="pane" id="acctOut">
    <h2 tabindex="-1" autofocus>משתמש</h2>
    <p class="note">עם משתמש, הצבעים והאסוציאציות נשמרים ונטענים בכל מכשיר שמתחברים ממנו.</p>
    <div class="nick nick-out">
      <label for="nickNew">כינוי (לא חובה)</label>
      <p class="note">כך יופיע השם שלך ליד אסוציאציות שתשתפו, במקום השם האמיתי. אפשר גם להוסיף או לשנות אחר כך.</p>
      <input id="nickNew" maxlength="20" autocomplete="nickname" spellcheck="false">
      <p class="err" id="nickNewErr" role="alert"></p>
    </div>
    <button type="button" class="google" id="googleBtn"><svg viewBox="0 0 48 48" aria-hidden="true"><path fill="#FFC107" d="M43.6 20.5H42V20H24v8h11.3C33.7 32.7 29.2 36 24 36c-6.6 0-12-5.4-12-12s5.4-12 12-12c3.1 0 5.8 1.2 7.9 3.1l5.7-5.7C34 6.1 29.3 4 24 4 12.9 4 4 12.9 4 24s8.9 20 20 20 20-8.9 20-20c0-1.3-.1-2.4-.4-3.5z"/><path fill="#FF3D00" d="m6.3 14.7 6.6 4.8C14.7 15.1 19 12 24 12c3.1 0 5.8 1.2 7.9 3.1l5.7-5.7C34 6.1 29.3 4 24 4 16.3 4 9.7 8.3 6.3 14.7z"/><path fill="#4CAF50" d="M24 44c5.2 0 9.9-2 13.4-5.2l-6.2-5.2C29.2 35.1 26.7 36 24 36c-5.2 0-9.6-3.3-11.3-8l-6.5 5C9.5 39.6 16.2 44 24 44z"/><path fill="#1976D2" d="M43.6 20.5H42V20H24v8h11.3c-.8 2.2-2.2 4.2-4.1 5.6l6.2 5.2C37 39.2 44 34 44 24c0-1.3-.1-2.4-.4-3.5z"/></svg>כניסה עם Google</button>
    <p class="err" id="googleErr" role="alert"></p>
    <div class="or">או עם אימייל וסיסמה</div>
    <form id="acctForm" novalidate>
      <label for="acctUser">אימייל</label>
      <p class="note">נרשמתם בעבר עם שם משתמש? אפשר להקליד אותו כאן וללחוץ "כניסה".</p>
      <input id="acctUser" name="username" autocomplete="username" autocapitalize="none" spellcheck="false" maxlength="100">
      <label for="acctPass">סיסמה (לפחות 6 תווים)</label>
      <input id="acctPass" name="password" type="password" autocomplete="current-password">
      <p class="err" id="acctErr" role="alert"></p>
      <div class="btns">
        <button type="submit" class="primary" id="loginBtn" value="login">כניסה</button>
        <button type="submit" class="secondary" id="signupBtn" value="signup">יצירת משתמש חדש</button>
      </div>
      <button type="button" class="link forgot" id="forgotBtn">שכחתי סיסמה</button>
      <p class="note" id="forgotMsg" role="status"></p>
    </form>
  </div>
  <div class="pane" id="acctIn" hidden>
    <h2 tabindex="-1" autofocus>משתמש</h2>
    <p>מחובר/ת בתור <b id="acctName"></b></p>
    <p class="note">ההתקדמות נשמרת במשתמש ומסונכרנת בין המכשירים.</p>
    <form id="nickForm" class="nick" novalidate>
      <label for="nickInput">כינוי (לא חובה)</label>
      <p class="note">כך יופיע השם שלך ליד אסוציאציות ששיתפת. אם משאירים ריק, יופיע <b id="nickDefault"></b>.</p>
      <div class="nick-row"><input id="nickInput" maxlength="20" autocomplete="nickname" spellcheck="false"><button type="submit" class="primary" id="nickSave">שמירה</button></div>
      <p class="err" id="nickErr" role="alert"></p>
      <p class="note nick-ok" id="nickMsg" role="status"></p>
    </form>
    <form id="emailForm" class="nick" novalidate hidden>
      <label for="emailInput">אימייל לשחזור סיסמה (לא חובה)</label>
      <p class="note">אם תוסיפו אימייל, תוכלו לשחזר את הסיסמה אם תשכחו אותה. נשלח אליו קישור לאישור. אחרי האישור נכנסים עם האימייל במקום שם המשתמש (הסיסמה וההתקדמות נשארות).</p>
      <div class="nick-row"><input id="emailInput" type="email" maxlength="100" autocomplete="email" spellcheck="false" autocapitalize="none"><button type="submit" class="primary" id="emailSave">שליחה</button></div>
      <p class="err" id="emailErr" role="alert"></p>
      <p class="note nick-ok" id="emailMsg" role="status"></p>
    </form>
    <div class="merge">
      <button type="button" class="link" id="mergeOpen">יש לך עוד משתמש באתר? איחוד משתמשים</button>
      <div id="mergeBox" hidden>
        <p class="note">נרשמת פעמיים (למשל פעם עם Google ופעם עם אימייל או שם משתמש)? אפשר לאחד: ההתקדמות משני המשתמשים תעבור למשתמש הזה, והמשתמש השני יימחק. מילה שסומנה אחרת בשניהם תקבל את הסימון החדש יותר.</p>
        <button type="button" class="google" id="linkGoogle"><svg viewBox="0 0 48 48" aria-hidden="true"><path fill="#FFC107" d="M43.6 20.5H42V20H24v8h11.3C33.7 32.7 29.2 36 24 36c-6.6 0-12-5.4-12-12s5.4-12 12-12c3.1 0 5.8 1.2 7.9 3.1l5.7-5.7C34 6.1 29.3 4 24 4 12.9 4 4 12.9 4 24s8.9 20 20 20 20-8.9 20-20c0-1.3-.1-2.4-.4-3.5z"/><path fill="#FF3D00" d="m6.3 14.7 6.6 4.8C14.7 15.1 19 12 24 12c3.1 0 5.8 1.2 7.9 3.1l5.7-5.7C34 6.1 29.3 4 24 4 16.3 4 9.7 8.3 6.3 14.7z"/><path fill="#4CAF50" d="M24 44c5.2 0 9.9-2 13.4-5.2l-6.2-5.2C29.2 35.1 26.7 36 24 36c-5.2 0-9.6-3.3-11.3-8l-6.5 5C9.5 39.6 16.2 44 24 44z"/><path fill="#1976D2" d="M43.6 20.5H42V20H24v8h11.3c-.8 2.2-2.2 4.2-4.1 5.6l6.2 5.2C37 39.2 44 34 44 24c0-1.3-.1-2.4-.4-3.5z"/></svg>איחוד עם חשבון Google</button>
        <form id="mergeForm" novalidate>
          <label for="mergeUser" id="mergeUserLbl">או: האימייל / שם המשתמש של המשתמש השני</label>
          <input id="mergeUser" autocomplete="off" autocapitalize="none" spellcheck="false" maxlength="100">
          <label for="mergePass">הסיסמה שלו</label>
          <div class="nick-row"><input id="mergePass" type="password" autocomplete="off"><button type="submit" class="primary" id="mergeSave">איחוד</button></div>
        </form>
        <p class="err" id="mergeErr" role="alert"></p>
        <p class="note nick-ok" id="mergeMsg" role="status"></p>
      </div>
    </div>
    <div class="merge" id="admEntry" hidden><button type="button" class="link" id="admOpenList">⚙️ ניהול האתר</button></div>
    <div class="btns"><button type="button" class="secondary" id="logoutBtn">יציאה מהמשתמש</button></div>
  </div>
  <button type="button" class="link" id="acctClose">סגירה</button>
</dialog>
"""

body_html += """
<dialog id="fbDlg" dir="rtl" lang="he">
  <div class="pane" id="fbOut">
    <h2 tabindex="-1" autofocus>הצעות ובעיות</h2>
    <p class="note">כדי לשלוח הצעה לשיפור או לדווח על בעיה צריך להיות מחוברים למשתמש (בחינם).</p>
    <div class="btns"><button type="button" class="primary" id="fbLogin">להתחברות / הרשמה</button></div>
  </div>
  <form class="pane" id="fbForm" novalidate hidden>
    <h2 tabindex="-1" autofocus>הצעות ובעיות</h2>
    <p class="note">משהו לא עובד? יש לך רעיון שישפר את האתר? כתבו כאן וזה יגיע ישירות אליי.</p>
    <div class="fb-kind" role="radiogroup">
      <label><input type="radio" name="fbKind" value="הצעה לשיפור" checked>💡 הצעה לשיפור</label>
      <label><input type="radio" name="fbKind" value="דיווח על בעיה">🐞 דיווח על בעיה</label>
    </div>
    <label for="fbText" id="fbTextLbl">מה ההצעה?</label>
    <textarea id="fbText" maxlength="3000"></textarea>
    <p class="err" id="fbErr" role="alert"></p>
    <p class="note nick-ok" id="fbMsg" role="status"></p>
    <div class="btns"><button type="submit" class="primary" id="fbSend">שליחה</button></div>
  </form>
  <button type="button" class="link" id="fbClose">סגירה</button>
</dialog>
"""

body_html += """
<dialog id="repDlg" dir="rtl" lang="he">
  <form class="pane" id="repForm" novalidate>
    <h2 tabindex="-1" autofocus>דיווח על אסוציאציה</h2>
    <p class="rep-quote" id="repQuote"></p>
    <div class="fb-kind" role="radiogroup">
      <label><input type="radio" name="repKind" value="ספאם" checked>ספאם</label>
      <label><input type="radio" name="repKind" value="תוכן פוגעני">פוגעני</label>
      <label><input type="radio" name="repKind" value="אחר">אחר</label>
    </div>
    <label for="repText">פרטים נוספים (לא חובה)</label>
    <textarea id="repText" maxlength="1000" style="min-height:70px"></textarea>
    <p class="note">הדיווח יגיע אליי לבדיקה, והאסוציאציה תוסתר אצלך מיד.</p>
    <p class="err" id="repErr" role="alert"></p>
    <p class="note nick-ok" id="repMsg" role="status"></p>
    <div class="btns"><button type="submit" class="primary" id="repSend">שליחת דיווח</button></div>
  </form>
  <button type="button" class="link" id="repClose">סגירה</button>
</dialog>
"""

body_html += """
<dialog id="banDlg" dir="rtl" lang="he">
  <div class="pane">
    <h2 tabindex="-1" autofocus>המשתמש נחסם</h2>
    <p class="note">המשתמש הזה נחסם בגלל הפרה של כללי האתר (למשל ספאם או תוכן פוגעני), ולכן אי אפשר להתחבר אליו.</p>
    <p class="note">אפשר להמשיך לתרגל באתר בלי משתמש. ההתקדמות תישמר בדפדפן הזה.</p>
    <div class="btns"><button type="button" class="primary" id="banOk">הבנתי</button></div>
  </div>
</dialog>
<dialog id="admDlg" dir="rtl" lang="he">
  <div class="pane" id="admBody"></div>
  <p class="err" id="admErr" role="alert"></p>
  <button type="button" class="link" id="admClose">סגירה</button>
</dialog>
"""

# --- script: replace the Claude account-sync block ---
start = script.index("/* ---------- Saving")
end = script.index("/* ---------- Start")
local_save = r'''/* ---------- Saving: this browser, plus an optional username/password account ---------- */
const FIREBASE_CONFIG = __FIREBASE_CONFIG__;
const FB_VERSION = "10.12.2";
let fb = null, account = null, unsubs = [];
const wTimers = {}, wBusy = {}, wDirty = {};
const LANGS = ["en", "he"];
function setSync(t) { $("syncText").textContent = t; }
function localSyncText() { setSync(account ? `ההתקדמות נשמרת במשתמש ${account.name}` : "ההתקדמות נשמרת בדפדפן הזה"); }
function save(lang) { lsSet(LS_STATE, state); if (account) (lang ? [lang] : LANGS).forEach(queueWrite); }
/* cloud saves are batched: at most one write per language every 10s (Firestore free plan counts writes), plus a flush when the page is hidden/closed or on sign-out */
function queueWrite(lang) { if (!wTimers[lang]) wTimers[lang] = setTimeout(() => writeLang(lang), 10000); }
function flushWrites() { return Promise.all(LANGS.filter((l) => wTimers[l]).map((l) => { clearTimeout(wTimers[l]); return writeLang(l); })); }
document.addEventListener("visibilitychange", () => { if (document.visibilityState === "hidden") flushWrites(); });
addEventListener("pagehide", () => { flushWrites(); });
async function writeLang(lang) {
  wTimers[lang] = null;
  if (!account) return;
  if (wBusy[lang]) { wDirty[lang] = true; return; }
  wBusy[lang] = true;
  try {
    await fb.setDoc(fb.doc(fb.db, "users", account.uid, "progress", lang), { p: state.p[lang], c: state.c[lang], l: (state.l || {})[lang] || {}, g: ui.goals || null, pl: typeof planOut === "function" ? planOut((ui.plans || {})[lang]) : null, nick: account.nick || "", sn: myNotes[lang] || {}, t: Date.now() });
    localSyncText();
  } catch (e) { setSync("השמירה במשתמש לא הצליחה כרגע. ההתקדמות שמורה בדפדפן ותישלח שוב בשינוי הבא."); }
  wBusy[lang] = false;
  if (wDirty[lang]) { wDirty[lang] = false; writeLang(lang); }
}
let mergeBusy = false;
const writeBusy = (l) => mergeBusy || wTimers[l] || wBusy[l] || wDirty[l];
const isEditing = () => !!document.activeElement && /^(TEXTAREA|INPUT)$/.test(document.activeElement.tagName) && !document.activeElement.closest("dialog");
function refreshAfterData() {
  for (const k in cache) delete cache[k];
  if (!DICT) return;
  if (ui.view === "practice") { const keep = pos; buildQueue(); pos = Math.min(keep, queue.length); }
  render();
}

/* usernames become Firebase sign-in addresses; Hebrew names are hex-encoded */
function userEmail(name) {
  const n = name.trim().toLowerCase();
  const local = /^[a-z0-9._-]+$/.test(n) ? n : "x-" + [...new TextEncoder().encode(n)].map((b) => b.toString(16).padStart(2, "0")).join("");
  return local.length > 64 ? null : local + "@ramzor-milim.app";
}
function userName(email) {
  const local = (email || "").split("@")[0];
  if (local.startsWith("x-")) {
    try { return new TextDecoder().decode(new Uint8Array(local.slice(2).match(/../g).map((h) => parseInt(h, 16)))); } catch (e) {}
  }
  return local;
}
const AUTH_ERRORS = {
  "auth/email-already-in-use": "שם המשתמש הזה כבר תפוס. אפשר לבחור שם אחר, או ללחוץ \"כניסה\" אם זה המשתמש שלך.",
  "auth/invalid-credential": "שם המשתמש או הסיסמה לא נכונים.",
  "auth/invalid-login-credentials": "שם המשתמש או הסיסמה לא נכונים.",
  "auth/wrong-password": "שם המשתמש או הסיסמה לא נכונים.",
  "auth/user-not-found": "אין משתמש בשם הזה. אפשר ליצור אותו עם \"יצירת משתמש חדש\".",
  "auth/weak-password": "הסיסמה צריכה להיות לפחות 6 תווים.",
  "auth/missing-password": "צריך להקליד סיסמה.",
  "auth/too-many-requests": "היו יותר מדי ניסיונות. נסו שוב בעוד כמה דקות.",
  "auth/network-request-failed": "אין חיבור לאינטרנט. בדקו את החיבור ונסו שוב.",
  "auth/invalid-email": "שם המשתמש יכול להכיל אותיות, מספרים, נקודה, מקף וקו תחתון."
};

async function loadFirebase() {
  if (fb) return fb;
  const base = `https://www.gstatic.com/firebasejs/${FB_VERSION}/`;
  const [appM, authM, fsM] = await Promise.all([import(base + "firebase-app.js"), import(base + "firebase-auth.js"), import(base + "firebase-firestore.js")]);
  const app = appM.initializeApp(FIREBASE_CONFIG);
  fb = {
    mods: { app: appM, auth: authM, fs: fsM },
    auth: authM.getAuth(app), db: fsM.getFirestore(app),
    signIn: authM.signInWithEmailAndPassword, signUp: authM.createUserWithEmailAndPassword,
    signOut: authM.signOut, onAuth: authM.onAuthStateChanged,
    resetPass: authM.sendPasswordResetEmail, verifyNewEmail: authM.verifyBeforeUpdateEmail,
    googlePopup: () => authM.signInWithPopup(fb.auth, new authM.GoogleAuthProvider()),
    doc: fsM.doc, getDoc: fsM.getDoc, setDoc: fsM.setDoc, onSnapshot: fsM.onSnapshot,
    collection: fsM.collection, getDocs: fsM.getDocs, query: fsM.query, orderBy: fsM.orderBy, limit: fsM.limit, deleteDoc: fsM.deleteDoc,
    updateDoc: fsM.updateDoc, arrayUnion: fsM.arrayUnion, arrayRemove: fsM.arrayRemove, count: fsM.getCountFromServer,
    collectionGroup: fsM.collectionGroup, where: fsM.where
  };
  return fb;
}
const uniqList = (x, y) => { const o = (x || []).slice(); (y || []).forEach((v) => { if (!o.some((q) => JSON.stringify(q) === JSON.stringify(v))) o.push(v); }); return o; };
/* one word from two sources: the newer colour wins (st = when it was set); with no times, `a` (the preferred side) wins
   when both have a colour; associations, stars and hidden lists are combined */
function mergeEntry(a, b) {
  if (!a) return { ...b }; if (!b) return { ...a };
  const out = { ...b, ...a }, ta = a.st || 0, tb = b.st || 0;
  const src = ta !== tb ? (ta > tb ? a : b) : (a.s ? a : b);
  if (src.s) out.s = src.s; else delete out.s;
  if (src.st) out.st = src.st; else delete out.st;
  for (const k of ["a", "f", "h", "pa"]) { const v = uniqList(a[k], b[k]); if (v.length) out[k] = v; else delete out[k]; }
  return out;
}
function mergeP(pa, pb) { const p = { ...pb }; for (const [w, v] of Object.entries(pa || {})) p[w] = mergeEntry(v, (pb || {})[w]); return p; }
/* opts.add: `remote` is a second account (daily counts add up) rather than this browser's copy of the same account;
   opts.mineFirst: with no times, this side's colours win */
function mergeLang(lang, remote, opts = {}) {
  if (typeof applyRemoteGoals === "function") applyRemoteGoals(lang, remote);
  if (state.l && remote.l) {   // daily log: same account → keep the higher count; two accounts → add them up
    const L = (state.l[lang] = state.l[lang] || {});
    const join = (x, y) => opts.add ? (x || 0) + (y || 0) : Math.max(x || 0, y || 0);
    for (const [day, r] of Object.entries(remote.l)) {
      const d = (L[day] = L[day] || { n: 0, up: 0, nw: 0, t: {} });
      for (const f of ["n", "up", "nw"]) d[f] = join(d[f], r[f]);
      d.t = d.t || {};
      for (const [k, v] of Object.entries(r.t || {})) d.t[k] = join(d.t[k], v);
      if (r.w) d.w = Object.assign({}, r.w, d.w || {});
    }
  }
  state.p[lang] = opts.mineFirst ? mergeP(state.p[lang], remote.p) : mergeP(remote.p, state.p[lang]);
  const seen = new Set(remote.c.map((x) => x.w));
  state.c[lang] = remote.c.concat(state.c[lang].filter((x) => !seen.has(x.w)));
}
function renderAccount() {
  $("acctBtn").hidden = !FIREBASE_CONFIG;
  $("acctBtn").dataset.in = String(!!account);
  $("acctLabel").textContent = account ? (account.nick || account.name.split("@")[0]) : "התחברות";
  $("acctOut").hidden = !!account;
  $("acctIn").hidden = !account;
  if ($("admEntry")) $("admEntry").hidden = !isAdminNow();
  if ($("admFooter")) $("admFooter").hidden = !isAdminNow();
  if ($("fbOut")) { $("fbOut").hidden = !!account; $("fbForm").hidden = !account; }
  if (account) {
    $("acctName").textContent = account.name;
    $("nickDefault").textContent = account.baseShare;
    if (document.activeElement !== $("nickInput")) $("nickInput").value = account.nick || "";
    $("emailForm").hidden = !account.canAddEmail;
    $("linkGoogle").hidden = !!account.google;
    $("mergeUserLbl").textContent = account.google ? "האימייל / שם המשתמש של המשתמש השני" : "או: האימייל / שם המשתמש של המשתמש השני";
  }
}
async function startAccounts() {
  renderAccount();
  if (!FIREBASE_CONFIG) return;
  try { await loadFirebase(); } catch (e) { $("acctBtn").hidden = true; return; }
  loadCounts();
  fb.onAuth(fb.auth, async (u) => {
    unsubs.forEach((f) => f()); unsubs = [];
    if (!u) { account = null; renderAccount(); localSyncText(); return; }
    try { if ((await fb.getDoc(fb.doc(fb.db, "bans", u.uid))).exists()) { await fb.signOut(fb.auth); for (const d of document.querySelectorAll("dialog[open]")) d.close(); $("banDlg").showModal(); return; } } catch (e) {}
    const viaPassword = (u.email || "").endsWith("@ramzor-milim.app");
    const viaGoogle = (u.providerData || []).some((p) => p.providerId === "google.com");
    const viaEmail = !viaPassword && !viaGoogle;   // signed up with a real email + password (can reset it)
    account = { uid: u.uid, name: viaPassword ? userName(u.email) : viaEmail ? (u.email || "משתמש") : (u.displayName || u.email || "משתמש Google"), canAddEmail: viaPassword, google: viaGoogle };
    account.baseShare = (viaPassword ? account.name : viaEmail ? "" : (u.displayName || "").split(" ")[0]) || "משתמש";   // never show an email address publicly
    account.nick = ""; setShareName(); myNotes = { en: {}, he: {} };
    renderAccount(); setSync("מסנכרן עם המשתמש…");
    {
      const memRef = fb.doc(fb.db, "members", u.uid);
      const kind = viaPassword ? "שם משתמש" : viaGoogle ? "Google" : "אימייל", login = viaPassword ? userName(u.email) : (u.email || "");
      fb.getDoc(memRef).then((s) => {   // first sign-in of a new account: no members doc yet and the account was created in the last day
        if (!s.exists() && Date.now() - Date.parse((u.metadata && u.metadata.creationTime) || 0) < 864e5)
          notifyOwner("signup", { _subject: `רמזור מילים: משתמש חדש נרשם (${login || "ללא שם"})`, "התחברות": login, "סוג": kind, "שם": u.displayName || pendingNick || "", "ניהול המשתמש": adminLink(u.uid), "זמן": new Date().toLocaleString("he-IL") });
      }).catch(() => {}).then(() => fb.setDoc(memRef, { t: Date.now() })).then(loadCounts).catch(() => {});
    }
    fb.setDoc(fb.doc(fb.db, "profiles", u.uid), { login: (viaPassword ? userName(u.email) : (u.email || "")).slice(0, 120), kind: viaPassword ? "username" : viaGoogle ? "google" : "email", name: (u.displayName || "").slice(0, 80), t: Date.now() }).catch(() => {});
    try {
      for (const lang of LANGS) {
        const snap = await fb.getDoc(fb.doc(fb.db, "users", u.uid, "progress", lang));
        if (snap.exists()) { mergeLang(lang, normLang(snap.data())); takeNick(snap.data()); takeMyNotes(lang, snap.data()); }
      }
      if (pendingNick) { account.nick = pendingNick; setShareName(); pendingNick = ""; $("nickNew").value = ""; renderAccount(); }
      lsSet(LS_STATE, state);
      await migrateLocalAssoc();
      refreshAfterData();
      await Promise.all(LANGS.map(writeLang));
      for (const lang of LANGS) {
        unsubs.push(fb.onSnapshot(fb.doc(fb.db, "users", u.uid, "progress", lang), (snap) => {
          if (snap.metadata.hasPendingWrites || !snap.exists() || writeBusy(lang) || isEditing()) return;
          takeNick(snap.data()); takeMyNotes(lang, snap.data());
          const r = normLang(snap.data());
          if (typeof applyRemoteGoals === "function") applyRemoteGoals(lang, r);
          if (JSON.stringify({ p: r.p, c: r.c, l: r.l || {} }) === JSON.stringify({ p: state.p[lang], c: state.c[lang], l: (state.l || {})[lang] || {} })) return;
          state.p[lang] = r.p; state.c[lang] = r.c; if (state.l) state.l[lang] = r.l || {}; lsSet(LS_STATE, state);
          if (ui.lang === lang) { if (ui.view === "practice") { for (const k in cache) delete cache[k]; renderHeader(); } else refreshAfterData(); }
        }, () => {}));
      }
      localSyncText();
      if (isAdminNow()) { refreshAfterData(); const q = new URLSearchParams(location.search).get("admin"); if (q) { history.replaceState(history.state, "", location.pathname); adminOpen(q, ""); } }
    } catch (e) { setSync("לא הצלחנו לטעון את ההתקדמות מהמשתמש. בדקו את החיבור ורעננו את הדף."); }
  });
}

/* tip after every association saved without an account */
function showLocalTip() {
  if (account) return;
  setTimeout(() => { const d = $("localTip"); if (d && !d.open && !account) d.showModal(); }, 250);
}
{
  const d = $("localTip");
  $("localTipOk").addEventListener("click", () => d.close());
  const toAcct = () => { d.close(); const a = $("acctBtn"); if (a && !a.hidden) a.click(); };
  $("localTipSignup").addEventListener("click", toAcct);
  $("localTipLogin").addEventListener("click", toAcct);
  d.addEventListener("click", (e) => { if (e.target !== d) return; const r = d.getBoundingClientRect(); if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) d.close(); });
  addEventListener("popstate", () => { if (d.open) d.close(); });
}
/* account window: a tap outside it closes it (press and release both outside, so dragging out of a field doesn't) */
{
  const dlg = $("acctDlg");
  const outside = (e) => { if (e.target !== dlg) return false; const r = dlg.getBoundingClientRect(); return e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom; };
  let downOutside = false;
  dlg.addEventListener("pointerdown", (e) => { downOutside = outside(e); });
  dlg.addEventListener("click", (e) => { if (downOutside && outside(e)) dlg.close(); downOutside = false; });
  dlg.addEventListener("close", () => Nav.close("acct"));   // however it closes, drop its "back" step
}
/* suggestions / bug reports: signed-in users only, emailed to the site owner via FormSubmit */
const WEB3FORMS_KEY = "__WEB3FORMS_KEY__";   // Web3Forms access key: messages go to the owner's email, which never appears in this page
{
  const dlg = $("fbDlg");
  const sync = () => {
    $("fbOut").hidden = !!account; $("fbForm").hidden = !account;
    const bug = (document.querySelector('input[name="fbKind"]:checked') || {}).value === "דיווח על בעיה";
    $("fbTextLbl").textContent = bug ? "מה קרה? (מה עשיתם, מה ציפיתם שיקרה ומה קרה בפועל)" : "מה ההצעה?";
  };
  $("fbOpen").addEventListener("click", () => { $("fbErr").textContent = ""; $("fbMsg").textContent = ""; sync(); dlg.showModal(); Nav.open("fb"); });
  $("fbClose").addEventListener("click", () => dlg.close());
  if ($("fbTop")) $("fbTop").addEventListener("click", () => $("fbOpen").click());
  $("fbLogin").addEventListener("click", () => { dlg.close(); setTimeout(() => $("acctBtn").click(), 50); });
  dlg.addEventListener("change", sync);
  const outside = (e) => { if (e.target !== dlg) return false; const r = dlg.getBoundingClientRect(); return e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom; };
  let downOutside = false;
  dlg.addEventListener("pointerdown", (e) => { downOutside = outside(e); });
  dlg.addEventListener("click", (e) => { if (downOutside && outside(e)) dlg.close(); downOutside = false; });
  dlg.addEventListener("close", () => Nav.close("fb"));
  addEventListener("popstate", (e) => { if (dlg.open && (e.state || {}).layer !== "fb") dlg.close(); });
  $("fbForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const err = $("fbErr"), msg = $("fbMsg"), btn = $("fbSend"), text = $("fbText").value.trim();
    err.textContent = ""; msg.textContent = "";
    if (!account) { sync(); return; }
    if (text.length < 3) { err.textContent = "כתבו כמה מילים לפני השליחה."; return; }
    const last = +lsGet("ramzor-fb-last", 0) || 0;
    if (Date.now() - last < 30000) { err.textContent = "רק שלחת הודעה. אפשר לשלוח שוב בעוד חצי דקה."; return; }
    const kind = (document.querySelector('input[name="fbKind"]:checked') || {}).value || "הודעה";
    const u = fb.auth.currentUser || {};
    const realMail = u.email && !u.email.endsWith("@ramzor-milim.app") ? u.email : "";
    const body = {
      _subject: `רמזור מילים: ${kind} מ${account.nick || account.name.split("@")[0]}`,
      _template: "table", _captcha: "false",
      "סוג": kind, "הודעה": text,
      "משתמש": account.name, "כינוי": account.nick || "-", "אימייל": realMail || "-", "uid": account.uid,
      "מסך": `${ui.lang === "he" ? "עברית" : "אנגלית"} / ${ui.view}`,
      "מכשיר": navigator.userAgent, "גודל מסך": `${innerWidth}x${innerHeight}`, "זמן": new Date().toLocaleString("he-IL")
    };
    if (realMail) body._replyto = realMail;
    btn.disabled = true; btn.textContent = "שולח…";
    try {
      await sendOwnerMail(body);
      lsSet("ramzor-fb-last", Date.now());
      $("fbText").value = "";
      msg.textContent = "נשלח, תודה! 🙏";
    } catch (ex) { err.textContent = "השליחה לא הצליחה. בדקו את החיבור ונסו שוב."; }
    btn.disabled = false; btn.textContent = "שליחה";
  });
}
/* report another user's association (spam / offensive): signed-in only, emailed like feedback, and hidden for the reporter */
async function sendOwnerMail(body) {
  const { _subject, _replyto, _template, _captcha, ...fields } = body;
  const payload = Object.assign({ access_key: WEB3FORMS_KEY, subject: _subject, from_name: "רמזור מילים" }, _replyto ? { replyto: _replyto } : {}, fields);
  const r = await fetch("https://api.web3forms.com/submit", { method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json" }, body: JSON.stringify(payload) });
  const d = await r.json().catch(() => ({}));
  if (!r.ok || String(d.success) === "false") throw new Error(d.message || r.status);
}
/* owner email alerts, switched on/off by the admin in the dashboard (settings/notify: public read, admin write) */
let notifyCfg = null;
async function getNotify() {
  try { const s = await fb.getDoc(fb.doc(fb.db, "settings", "notify")); notifyCfg = s.exists() ? s.data() : {}; } catch (e) { notifyCfg = notifyCfg || {}; }
  return notifyCfg;
}
const adminLink = (uid) => location.origin + location.pathname + "?admin=" + encodeURIComponent(uid);
async function notifyOwner(kind, body) {
  try { if (isAdminNow()) return; const c = await getNotify(); if (c[kind]) await sendOwnerMail(body); } catch (e) {}
}
function notifyNote(lang, w, n) {
  notifyOwner("notes", { _subject: `רמזור מילים: אסוציאציה חדשה ל־${w}`, "מילה": w, "שפה": lang === "he" ? "עברית" : "אנגלית", "מאת": n.name || "אנונימי", "אסוציאציה": n.text || "", "תמונה": n.img ? "כן" : "לא", "ניהול המשתמש": adminLink(account.uid), "זמן": new Date().toLocaleString("he-IL") });
}
{
  const dlg = $("repDlg");
  let cur = null;   // { w, lang, n }
  document.addEventListener("click", (e) => {
    const t = e.target.closest && e.target.closest(".report-note");
    if (!t) return;
    const box = t.closest(".assoc"); if (!box) return;
    const w = box.dataset.w, lang = ui.lang;
    const n = (notesCache[ck(w, lang)] || []).find((x) => x.id === t.dataset.note);
    if (!n) return;
    if (!account) { $("acctBtn").click(); return; }
    cur = { w, lang, n };
    $("repQuote").textContent = n.text || "(תמונה)";
    $("repText").value = ""; $("repErr").textContent = ""; $("repMsg").textContent = "";
    $("repSend").disabled = false; $("repSend").hidden = false;
    dlg.showModal(); Nav.open("rep");
  });
  $("repClose").addEventListener("click", () => dlg.close());
  const outside = (e) => { if (e.target !== dlg) return false; const r = dlg.getBoundingClientRect(); return e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom; };
  let downOutside = false;
  dlg.addEventListener("pointerdown", (e) => { downOutside = outside(e); });
  dlg.addEventListener("click", (e) => { if (downOutside && outside(e)) dlg.close(); downOutside = false; });
  dlg.addEventListener("close", () => Nav.close("rep"));
  addEventListener("popstate", (e) => { if (dlg.open && (e.state || {}).layer !== "rep") dlg.close(); });
  $("repForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!cur || !account) return;
    const { w, lang, n } = cur, err = $("repErr"), btn = $("repSend");
    err.textContent = "";
    const done = lsGet("ramzor-reported") || [];
    const hideIt = () => { setHidden(w, favKey(n), true); refreshAssoc(w); };
    if (done.includes(n.id)) { hideIt(); $("repMsg").textContent = "כבר דיווחת על האסוציאציה הזו. היא מוסתרת אצלך."; btn.hidden = true; return; }
    const kind = (document.querySelector('input[name="repKind"]:checked') || {}).value || "דיווח";
    btn.disabled = true; btn.textContent = "שולח…";
    try {
      await sendOwnerMail({
        _subject: `רמזור מילים: דיווח על אסוציאציה (${kind}) במילה ${w}`,
        "סוג": kind, "מילה": w, "שפה": lang === "he" ? "עברית" : "אנגלית",
        "האסוציאציה": n.text || "-", "תמונה": n.img || "-", "שם הכותב": n.name || "אנונימי", "uid של הכותב": n.uid || "-", "ניהול הכותב (לפתוח כשמחוברים)": n.uid ? "https://ramzor-milim.github.io/?admin=" + n.uid : "-",
        "נתיב ב-Firestore": `shared/${lang}/words/${noteKey(w)}/notes/${n.id}`,
        "פרטים מהמדווח": $("repText").value.trim() || "-",
        "מדווח": account.name, "uid של המדווח": account.uid, "זמן": new Date().toLocaleString("he-IL")
      });
      done.push(n.id); lsSet("ramzor-reported", done.slice(-300));
      hideIt();
      $("repMsg").textContent = "תודה! הדיווח נשלח והאסוציאציה הוסתרה אצלך.";
      btn.hidden = true;
    } catch (ex) { err.textContent = "השליחה לא הצליחה. בדקו את החיבור ונסו שוב."; }
    btn.disabled = false; btn.textContent = "שליחת דיווח";
  });
}
/* admin (site owner only; Firestore rules enforce it): see all associations of a user, delete them, ban / unban */
const ADMIN_UID = "0Nr9yU1s9PbYWfDvRRYHWjMF1H42";
function isAdminNow() { return !!account && account.uid === ADMIN_UID; }
let admUser = null, admNotes = null, admBan = null, admBans = null, admMembers = null, admAll = null, admProf = {}, admTab = "users";
const admDate = (t) => t ? new Date(t).toLocaleDateString("he-IL") : "";
const admKind = { username: "שם משתמש", google: "Google", email: "אימייל" };
const admLogin = (uid) => { const p = admProf[uid]; return p && p.login ? `${esc(p.login)} · ${admKind[p.kind] || ""}` : "פרטי כניסה יופיעו אחרי הכניסה הבאה של המשתמש"; };
async function adminLoadNotes(uid) {
  let docs;
  try { docs = (await fb.getDocs(fb.query(fb.collectionGroup(fb.db, "notes"), fb.where("uid", "==", uid)))).docs; }
  catch (e) { docs = (await fb.getDocs(fb.collectionGroup(fb.db, "notes"))).docs.filter((d) => d.data().uid === uid); }   // no index yet: scan
  return docs.map((d) => { const wr = d.ref.parent.parent; return { ...d.data(), id: d.id, ref: d.ref, w: decodeURIComponent(wr.id), lang: wr.parent.parent.id }; })
    .sort((a, b) => (b.t || 0) - (a.t || 0));
}
function adminRender() {
  const body = $("admBody");
  if (!admUser) {
    const loading = admMembers === null || admAll === null || admBans === null;
    const banned = new Set((admBans || []).map((x) => x.id));
    const byUser = {};
    for (const n of admAll || []) (byUser[n.uid] = byUser[n.uid] || []).push(n);
    const nameOf = (uid) => { const named = (byUser[uid] || []).find((n) => n.name); const ban = (admBans || []).find((x) => x.id === uid); const pr = admProf[uid]; return uid === ADMIN_UID ? "את (מנהלת)" : named ? named.name : pr && pr.name ? pr.name : ban && ban.name ? ban.name : "ללא שם"; };
    const users = (admMembers || []).slice().sort((a, b) => (byUser[b.id] || []).length - (byUser[a.id] || []).length || (b.t || 0) - (a.t || 0));
    const tab = (k, label) => `<button type="button" data-adm-tab="${k}" aria-pressed="${admTab === k}">${label}</button>`;
    let list = "";
    if (loading) list = `<p class="note">טוען…</p>`;
    else if (admTab === "users") list = users.length ? `<ul class="adm-list">${users.map((m) => { const c = (byUser[m.id] || []).length; return `<li class="adm-user" data-adm-open="${esc(m.id)}"><span class="adm-user-row"><b>${esc(nameOf(m.id))}${banned.has(m.id) ? " 🚫" : ""}</b><button type="button" class="link" data-adm-open="${esc(m.id)}">${c ? c + " אסוציאציות" : "אין אסוציאציות"} ←</button></span><span class="adm-text" style="font-size:.85rem">${admLogin(m.id)}</span><span class="adm-top"><span>נכנס/ה לאחרונה: ${admDate(m.t)}</span><span class="adm-uid">${esc(m.id.slice(0, 8))}…</span></span></li>`; }).join("")}</ul>` : `<p class="note">אין משתמשים רשומים.</p>`;
    else if (admTab === "notes") list = admAll.length ? `<ul class="adm-list">${admAll.slice(0, 200).map((n, i) => `<li><span class="adm-top"><span>${esc(n.w)} · ${n.lang === "he" ? "עברית" : "אנגלית"} · ${esc(n.name || "אנונימי")}</span><span>${admDate(n.t)}</span></span><span class="adm-text">${esc(n.text || "")}${n.img ? " 🖼️" : ""}</span><span class="note-actions"><button type="button" class="link" data-adm-open="${esc(n.uid)}" style="color:var(--accent)">המשתמש</button><button type="button" data-adm-fdel="${i}">מחיקה</button></span></li>`).join("")}</ul>` : `<p class="note">עוד לא פורסמו אסוציאציות.</p>`;
    else list = admBans.length
        ? `<ul class="adm-list">${admBans.map((x) => `<li><span class="adm-top"><b>${esc(x.name || "ללא שם")}</b><span>${admDate(x.t)}</span></span>${x.reason ? `<span class="adm-text">${esc(x.reason)}</span>` : ""}<span class="note-actions"><button type="button" class="link" data-adm-open="${esc(x.id)}" style="color:var(--accent)">פתיחה</button><button type="button" data-adm-unban="${esc(x.id)}">ביטול חסימה</button></span></li>`).join("")}</ul>`
        : `<p class="note">אין משתמשים חסומים.</p>`;
    body.innerHTML = `<h2 tabindex="-1" autofocus>ניהול האתר</h2>
      <fieldset class="adm-notify"><legend>התראות במייל</legend>${notifyCfg === null ? `<span class="note">טוען…</span>` : `
        <label><input type="checkbox" data-adm-notify="signup"${notifyCfg.signup ? " checked" : ""}>להודיע לי על כל משתמש חדש שנרשם</label>
        <label><input type="checkbox" data-adm-notify="notes"${notifyCfg.notes ? " checked" : ""}>להודיע לי על כל אסוציאציה חדשה שפורסמה</label>`}</fieldset>
      <div class="adm-tabs">${tab("users", `משתמשים${admMembers ? ` (${admMembers.length})` : ""}`)}${tab("notes", `אסוציאציות אחרונות${admAll ? ` (${admAll.length})` : ""}`)}${tab("bans", `חסומים${admBans ? ` (${admBans.length})` : ""}`)}</div>
      ${list}
      <p class="note">מוצגות רק אסוציאציות שפורסמו לכולם (כולל אנונימיות). אסוציאציות שמשתמשים הסתירו מכולם נשמרות אצלם בלבד ולא מופיעות כאן.</p>`;
    return;
  }
  const u = admUser, me = u.uid === ADMIN_UID;
  const name = u.name || (admNotes && admNotes[0] && admNotes[0].name) || (admProf[u.uid] && admProf[u.uid].name) || "משתמש";
  body.innerHTML = `<h2 tabindex="-1" autofocus>ניהול: ${esc(name)}</h2>
    <p class="note" style="margin:0">${admLogin(u.uid)}</p>
    <p class="adm-uid">uid: ${esc(u.uid)}</p>
    <p class="adm-status" data-banned="${!!admBan}">${admBan ? `🚫 חסום מאז ${admDate(admBan.t)}${admBan.reason ? ` · ${esc(admBan.reason)}` : ""}` : "✓ לא חסום"}</p>
    <h3 style="margin:6px 0 0;font-size:1rem">אסוציאציות שפרסם${admNotes ? ` (${admNotes.length})` : ""}</h3>
    ${admNotes === null ? `<p class="note">טוען…</p>` : admNotes.length
      ? `<ul class="adm-list">${admNotes.map((n, i) => `<li><span class="adm-top"><span>${esc(n.w)} · ${n.lang === "he" ? "עברית" : "אנגלית"} · ${esc(n.name || "אנונימי")}</span><span>${admDate(n.t)}</span></span><span class="adm-text">${esc(n.text || "")}${n.img ? " 🖼️" : ""}</span><span class="note-actions"><button type="button" data-adm-del="${i}">מחיקה</button></span></li>`).join("")}</ul>
        <div class="btns"><button type="button" class="secondary adm-danger" id="admDelAll">מחיקת כל ${admNotes.length} האסוציאציות</button></div>`
      : `<p class="note">אין אסוציאציות מפורסמות.</p>`}
    ${me ? "" : admBan
      ? `<div class="btns"><button type="button" class="secondary" id="admUnban">ביטול החסימה</button></div>`
      : `<label for="admReason">סיבת החסימה (רק את רואה אותה)</label><input id="admReason" maxlength="200" placeholder="למשל: ספאם, קללות">
         <div class="btns"><button type="button" class="primary" id="admBan" style="background:var(--red)">חסימת המשתמש</button><button type="button" class="secondary" id="admBanDel">חסימה + מחיקת כל האסוציאציות</button></div>`}
    <button type="button" class="link" id="admToList" style="justify-self:start">← חזרה לניהול האתר</button>`;
}
async function adminOpen(uid, name) {
  if (!isAdminNow()) return;
  admUser = uid ? { uid, name } : null; admNotes = null; admBan = null; admBans = null; admMembers = null; admAll = null;
  $("admErr").textContent = "";
  const d = $("admDlg"); adminRender(); if (!d.open) { d.showModal(); Nav.open("adm"); }
  try {
    if (!uid) {
      const [mem, all, bans, prof] = await Promise.all([fb.getDocs(fb.collection(fb.db, "members")), fb.getDocs(fb.collectionGroup(fb.db, "notes")), fb.getDocs(fb.collection(fb.db, "bans")), fb.getDocs(fb.collection(fb.db, "profiles")).catch(() => null)]);
      admProf = {}; if (prof) prof.docs.forEach((x) => { admProf[x.id] = x.data(); });
      admMembers = mem.docs.map((x) => ({ id: x.id, ...x.data() }));
      admAll = all.docs.map((d) => { const wr = d.ref.parent.parent; return { ...d.data(), id: d.id, ref: d.ref, w: decodeURIComponent(wr.id), lang: wr.parent.parent.id }; }).sort((a, b) => (b.t || 0) - (a.t || 0));
      admBans = bans.docs.map((x) => ({ id: x.id, ...x.data() })).sort((a, b) => (b.t || 0) - (a.t || 0));
      await getNotify();
    } else {
      const [notes, ban, prof] = await Promise.all([adminLoadNotes(uid), fb.getDoc(fb.doc(fb.db, "bans", uid)), fb.getDoc(fb.doc(fb.db, "profiles", uid)).catch(() => null)]);
      if (prof && prof.exists()) admProf[uid] = prof.data();
      admNotes = notes; admBan = ban.exists() ? ban.data() : null;
    }
  } catch (e) { $("admErr").textContent = "הטעינה לא הצליחה (" + (e.code || e.message) + ")."; admNotes = admNotes || []; admBans = admBans || []; admMembers = admMembers || []; admAll = admAll || []; }
  adminRender();
}
async function adminDelete(n) {
  await fb.deleteDoc(n.ref);
  fb.deleteDoc(fb.doc(fb.db, "noteIndex", n.id)).catch(() => {});
  const k = ck(n.w, n.lang);
  if (notesCache[k]) { notesCache[k] = notesCache[k].filter((x) => x.id !== n.id); afterNotes(n.w, n.lang); }
}
async function adminBan(withDelete) {
  const u = admUser, reason = ($("admReason") || {}).value || "";
  const name = u.name || (admNotes && admNotes[0] && admNotes[0].name) || "";
  if (withDelete && admNotes) for (const n of admNotes.slice()) await adminDelete(n);
  await fb.setDoc(fb.doc(fb.db, "bans", u.uid), { t: Date.now(), name: name.slice(0, 60), reason: reason.trim().slice(0, 200) });
}
{
  const dlg = $("admDlg");
  $("admClose").addEventListener("click", () => dlg.close());
  $("banOk").addEventListener("click", () => $("banDlg").close());
  dlg.addEventListener("close", () => Nav.close("adm"));
  dlg.addEventListener("change", async (e) => {
    const cb = e.target.closest && e.target.closest("input[data-adm-notify]");
    if (!cb || !isAdminNow()) return;
    const next = { signup: !!(notifyCfg || {}).signup, notes: !!(notifyCfg || {}).notes, [cb.dataset.admNotify]: cb.checked };
    $("admErr").textContent = ""; cb.disabled = true;
    try { await fb.setDoc(fb.doc(fb.db, "settings", "notify"), next); notifyCfg = next; }
    catch (ex) { cb.checked = !cb.checked; $("admErr").textContent = "השמירה לא הצליחה (" + (ex.code || ex.message) + ")."; }
    cb.disabled = false;
  });
  addEventListener("popstate", (e) => { if (dlg.open && (e.state || {}).layer !== "adm") dlg.close(); });
  document.addEventListener("click", async (e) => {
    const row = e.target.closest && !e.target.closest("button") && e.target.closest("li.adm-user");
    if (row && isAdminNow()) { adminOpen(row.dataset.admOpen, ""); return; }
    const t = e.target.closest && e.target.closest("button");
    if (!t) return;
    if (t.classList.contains("admin-note")) { adminOpen(t.dataset.uid, t.dataset.name); return; }
    if (t.id === "admOpenList") { $("acctDlg").close(); setTimeout(() => adminOpen(null), 50); return; }
    if (t.id === "admFooter") { adminOpen(null); return; }
    if (!dlg.contains(t) || !isAdminNow()) return;
    const err = $("admErr"); err.textContent = "";
    const run = async (f, ask) => {
      if (ask && !confirm(ask)) return;
      t.disabled = true;
      try { await f(); } catch (ex) { err.textContent = "הפעולה לא הצליחה (" + (ex.code || ex.message) + ")."; }
      t.disabled = false;
    };
    if (t.id === "admToList") return adminOpen(null);
    if (t.dataset.admTab) { admTab = t.dataset.admTab; adminRender(); return; }
    if (t.dataset.admFdel !== undefined) { const n = admAll[+t.dataset.admFdel]; return run(async () => { await adminDelete(n); admAll = admAll.filter((x) => x !== n); adminRender(); }, "למחוק את האסוציאציה הזו?"); }
    if (t.dataset.admOpen) return adminOpen(t.dataset.admOpen, "");
    if (t.dataset.admUnban) return run(async () => { await fb.deleteDoc(fb.doc(fb.db, "bans", t.dataset.admUnban)); admBans = admBans.filter((x) => x.id !== t.dataset.admUnban); adminRender(); }, "לבטל את החסימה?");
    if (t.dataset.admDel !== undefined) { const n = admNotes[+t.dataset.admDel]; return run(async () => { await adminDelete(n); admNotes = admNotes.filter((x) => x !== n); adminRender(); }, "למחוק את האסוציאציה הזו?"); }
    if (t.id === "admDelAll") return run(async () => { for (const n of admNotes.slice()) await adminDelete(n); admNotes = []; adminRender(); }, `למחוק את כל ${admNotes.length} האסוציאציות של המשתמש? אי אפשר לבטל.`);
    if (t.id === "admBan") return run(async () => { await adminBan(false); adminOpen(admUser.uid, admUser.name); }, "לחסום את המשתמש? הוא לא יוכל להתחבר או לפרסם.");
    if (t.id === "admBanDel") return run(async () => { await adminBan(true); adminOpen(admUser.uid, admUser.name); }, "לחסום את המשתמש ולמחוק את כל האסוציאציות שלו? את המחיקה אי אפשר לבטל.");
    if (t.id === "admUnban") return run(async () => { await fb.deleteDoc(fb.doc(fb.db, "bans", admUser.uid)); adminOpen(admUser.uid, admUser.name); }, "לבטל את החסימה?");
  });
}
/* nickname: optional public name for shared associations, stored with the progress docs */
let pendingNick = "";
function nickProblem(nick) {
  if (nick && nick.length < 2) return "הכינוי צריך להיות לפחות 2 תווים.";
  if (/[<>@]/.test(nick)) return "הכינוי לא יכול להכיל את התווים < > @.";
  return "";
}
function takePendingNick() {
  const nick = $("nickNew").value.trim().replace(/\s+/g, " "), bad = nickProblem(nick);
  $("nickNewErr").textContent = bad;
  if (bad) return false;
  pendingNick = nick;
  return true;
}
/* where this account's shared associations are ({lang: {noteId: word}}), kept in the progress docs,
   so a nickname change can rename all of them at once */
let myNotes = { en: {}, he: {} };
function rememberNote(lang, id, w) { if (!account || !lang || !w || (myNotes[lang] || {})[id] === w) return; (myNotes[lang] = myNotes[lang] || {})[id] = w; queueWrite(lang); }
function forgetNote(lang, id) { if (!account || !lang || !(myNotes[lang] || {})[id]) return; delete myNotes[lang][id]; queueWrite(lang); }
function takeMyNotes(lang, data) {
  if (!data || !data.sn || typeof data.sn !== "object") return;
  myNotes[lang] = Object.assign({}, myNotes[lang] || {}, data.sn);
}
async function renameNote(lang, w, id) {
  try {
    const ref = fb.doc(notesCol(lang, w), id), snap = await fb.getDoc(ref);
    if (!snap.exists()) { forgetNote(lang, id); return; }
    const d = snap.data();
    if (d.uid !== account.uid || !d.name || d.name === account.shareName) return;   // anonymous ones stay anonymous
    await fb.updateDoc(ref, { name: account.shareName });
    const c = (notesCache[ck(w, lang)] || []).find((n) => n.id === id); if (c) c.name = account.shareName;
  } catch (e) {}
}
function setShareName() { if (account) account.shareName = (account.nick || account.baseShare).slice(0, 40); }
function takeNick(data) {
  if (!account || !data || typeof data.nick !== "string" || data.nick === (account.nick || "")) return;
  account.nick = data.nick.slice(0, 20); setShareName(); renderAccount();
}
function fixMyNoteNames(lang, w) {
  if (!account) return [];
  (notesCache[ck(w, lang)] || []).forEach((n) => { if (n.uid === account.uid) rememberNote(lang, n.id, w); });
  const mine = (notesCache[ck(w, lang)] || []).filter((n) => n.uid === account.uid && n.name && n.name !== account.shareName);
  return mine.map((n) => { n.name = account.shareName; return fb.updateDoc(fb.doc(notesCol(lang, w), n.id), { name: n.name }).catch(() => {}); });
}
document.addEventListener("submit", async (e) => {
  if (e.target.id !== "nickForm") return;
  e.preventDefault();
  if (!account) return;
  const nick = $("nickInput").value.trim().replace(/\s+/g, " "), err = $("nickErr"), msg = $("nickMsg");
  err.textContent = ""; msg.textContent = "";
  const bad = nickProblem(nick); if (bad) { err.textContent = bad; return; }
  $("nickSave").disabled = true;
  const prev = account.nick || "";
  account.nick = nick; setShareName();   // set first, so a background progress save can't write back the old one
  try {
    await loadFirebase();
    await Promise.all(LANGS.map((lang) => fb.setDoc(fb.doc(fb.db, "users", account.uid, "progress", lang), { nick }, { merge: true })));
    renderAccount();
    const fixes = Object.keys(notesCache).flatMap((k) => { const i = k.indexOf("|"); return fixMyNoteNames(k.slice(0, i), k.slice(i + 1)); });
    LANGS.forEach((lang) => Object.entries(myNotes[lang] || {}).forEach(([id, w]) => fixes.push(renameNote(lang, w, id))));
    await Promise.all(fixes);
    if (DICT) render();
    msg.textContent = nick ? `נשמר. האסוציאציות שלך יופיעו בשם "${nick}".` : `הכינוי נמחק. האסוציאציות שלך יופיעו בשם "${account.baseShare}".`;
  } catch (ex) {
    account.nick = prev; setShareName(); renderAccount();
    err.textContent = "השמירה לא הצליחה. בדקו את החיבור לאינטרנט ונסו שוב.";
  }
  $("nickSave").disabled = false;
});

document.addEventListener("click", async (e) => {
  const id = e.target.closest("button") && e.target.closest("button").id;
  if (id === "acctBtn") { $("acctErr").textContent = ""; $("googleErr").textContent = ""; $("nickErr").textContent = ""; $("nickMsg").textContent = ""; $("nickNewErr").textContent = ""; $("forgotMsg").textContent = ""; $("emailErr").textContent = ""; $("emailMsg").textContent = ""; $("mergeErr").textContent = ""; $("mergeMsg").textContent = ""; $("mergeBox").hidden = true; $("acctDlg").showModal(); Nav.open("acct"); }
  if (id === "acctClose") $("acctDlg").close();
  if (id === "googleBtn") {
    const gErr = $("googleErr"); gErr.textContent = "";
    if (!takePendingNick()) return;
    const btn = $("googleBtn"); btn.disabled = true;
    try { await loadFirebase(); await fb.googlePopup(); $("acctDlg").close(); }
    catch (ex) {
      const code = ex && ex.code;
      const homeScreen = window.navigator.standalone === true || matchMedia("(display-mode: standalone)").matches;
      if (code === "auth/popup-closed-by-user" || code === "auth/cancelled-popup-request") gErr.textContent = "";
      else if (code === "auth/popup-blocked" || homeScreen) gErr.textContent = homeScreen
        ? "באפליקציה שעל מסך הבית אייפון לא תמיד מאפשר כניסה עם Google. אפשר להשתמש כאן בשם משתמש וסיסמה, או לפתוח את האתר בספארי."
        : "הדפדפן חסם את חלון הכניסה. אפשרו חלונות קופצים לאתר הזה ונסו שוב.";
      else if (code === "auth/account-exists-with-different-credential") gErr.textContent = "כבר יש משתמש עם האימייל הזה, עם סיסמה. היכנסו עם האימייל והסיסמה, ואז אפשר לחבר את Google בחלון המשתמש (\"איחוד משתמשים\").";
      else if (code === "auth/unauthorized-domain" || code === "auth/operation-not-allowed") gErr.textContent = "הכניסה עם Google עדיין לא הופעלה באתר הזה.";
      else gErr.textContent = AUTH_ERRORS[code] || "הכניסה עם Google לא הצליחה. נסו שוב.";
      pendingNick = "";
    }
    btn.disabled = false;
  }
  if (id === "logoutBtn") { await flushWrites().catch(() => {}); await fb.signOut(fb.auth); $("acctDlg").close(); }
});
document.addEventListener("submit", async (e) => {
  if (e.target.id !== "acctForm") return;
  e.preventDefault();
  const mode = e.submitter && e.submitter.value === "signup" ? "signup" : "login";
  const name = $("acctUser").value.trim(), pass = $("acctPass").value;
  const err = $("acctErr");
  const isMail = name.includes("@");
  if (isMail && !EMAIL_RE.test(name)) { err.textContent = "האימייל לא נראה תקין. בדקו שהקלדתם אותו נכון."; return; }
  if (mode === "signup" && !isMail) { err.textContent = "להרשמה צריך אימייל. מי שכבר יש לו שם משתמש יכול להיכנס איתו בכפתור \"כניסה\"."; return; }
  if (!isMail && name.length < 2) { err.textContent = "שם המשתמש צריך להיות לפחות 2 תווים."; return; }
  if (!isMail && /\s/.test(name)) { err.textContent = "שם המשתמש לא יכול להכיל רווחים."; return; }
  const email = isMail ? name.toLowerCase() : userEmail(name);
  if (!email) { err.textContent = "שם המשתמש ארוך מדי."; return; }
  if (pass.length < 6) { err.textContent = "הסיסמה צריכה להיות לפחות 6 תווים."; return; }
  err.textContent = "";
  if (!takePendingNick()) return;   // checked last, so it's only held when a sign-in is really sent
  $("loginBtn").disabled = $("signupBtn").disabled = true;
  try {
    await loadFirebase();
    if (mode === "signup") await fb.signUp(fb.auth, email, pass); else await fb.signIn(fb.auth, email, pass);
    $("acctPass").value = "";
    $("acctDlg").close();
  } catch (ex) {
    const code = ex && ex.code;
    err.textContent = isMail && code === "auth/email-already-in-use" ? "כבר יש משתמש עם האימייל הזה. אם נרשמתם עם Google, היכנסו בכפתור של Google למעלה. אחרת לחצו \"כניסה\" (או \"שכחתי סיסמה\")."
      : isMail && /invalid-(login-)?credential|wrong-password/.test(code || "") ? "האימייל או הסיסמה לא נכונים. אם נרשמתם עם Google, היכנסו בכפתור של Google למעלה. אם שכחתם את הסיסמה, לחצו \"שכחתי סיסמה\"."
      : isMail && code === "auth/user-not-found" ? "אין משתמש עם האימייל הזה. אפשר ליצור אותו עם \"יצירת משתמש חדש\"."
      : isMail && code === "auth/invalid-email" ? "האימייל לא נראה תקין. בדקו שהקלדתם אותו נכון."
      : AUTH_ERRORS[code] || "משהו השתבש. נסו שוב בעוד רגע.";
    pendingNick = "";
  }
  $("loginBtn").disabled = $("signupBtn").disabled = false;
});


/* ---------- merging a second account of the same person into this one ----------
   The other account is signed in on a separate, memory-only Firebase instance, so this one stays signed in.
   Its progress is combined into this account, its shared associations move here, then it is deleted. */
let fb2 = null;
function otherAuth() {
  if (fb2) return fb2;
  const m = fb.mods, app2 = m.app.initializeApp(FIREBASE_CONFIG, "merge");
  fb2 = { auth: m.auth.initializeAuth(app2, { persistence: m.auth.inMemoryPersistence }), db: m.fs.getFirestore(app2) };
  return fb2;
}
async function absorbAccount(u2) {
  const me = fb.auth.currentUser, db2 = fb2.db;
  if (!me || !account || u2.uid === me.uid) return false;
  await flushWrites().catch(() => {});
  mergeBusy = true;
  try {
    for (const lang of LANGS) {
      const [s2, s1] = await Promise.all([fb.getDoc(fb.doc(db2, "users", u2.uid, "progress", lang)), fb.getDoc(fb.doc(fb.db, "users", me.uid, "progress", lang))]);
      if (!s2.exists()) continue;
      const d2 = s2.data(), t1 = s1.exists() ? s1.data().t || 0 : 0;
      mergeLang(lang, normLang(d2), { add: true, mineFirst: t1 >= (d2.t || 0) });   // with no times, the account used more recently wins
      for (const [id, w] of Object.entries(d2.sn || {})) {   // its shared associations become this account's
        try {
          const ref = fb.doc(db2, "shared", lang, "words", noteKey(w), "notes", id), snap = await fb.getDoc(ref);
          if (!snap.exists() || snap.data().uid !== u2.uid) continue;
          await fb.updateDoc(ref, { uid: me.uid, name: snap.data().name ? account.shareName : "" });
          await fb.deleteDoc(fb.doc(db2, "noteIndex", id)).catch(() => {});
          await fb.setDoc(fb.doc(fb.db, "noteIndex", id), { uid: me.uid, t: Date.now() }).catch(() => {});
          rememberNote(lang, id, w);
        } catch (e) {}
      }
    }
    for (const k in notesCache) delete notesCache[k];
    lsSet(LS_STATE, state);
  } finally { mergeBusy = false; }
  refreshAfterData();
  await Promise.all(LANGS.map(writeLang));
  await Promise.all(LANGS.map((l) => fb.deleteDoc(fb.doc(db2, "users", u2.uid, "progress", l)).catch(() => {})));
  await fb.deleteDoc(fb.doc(db2, "members", u2.uid)).catch(() => {});
  await fb.mods.auth.deleteUser(u2).catch(() => fb.mods.auth.signOut(fb2.auth));
  loadCounts();
  return true;
}
const MERGE_DONE = "האיחוד הושלם ✓ ההתקדמות משני המשתמשים נמצאת עכשיו כאן, והמשתמש השני נמחק.";
document.addEventListener("click", async (e) => {
  const b = e.target.closest("button"); if (!b) return;
  if (b.id === "mergeOpen") { $("mergeBox").hidden = !$("mergeBox").hidden; return; }
  if (b.id !== "linkGoogle" || !account) return;
  const err = $("mergeErr"), msg = $("mergeMsg"), A = fb.mods.auth;
  err.textContent = ""; msg.textContent = ""; b.disabled = true;
  try {
    try {
      await A.linkWithPopup(fb.auth.currentUser, new A.GoogleAuthProvider());
      msg.textContent = "חשבון Google חובר ✓ מעכשיו אפשר להיכנס למשתמש הזה גם עם Google.";
    } catch (ex) {
      if (ex.code !== "auth/credential-already-in-use" && ex.code !== "auth/email-already-in-use") throw ex;
      const cred = A.GoogleAuthProvider.credentialFromError(ex); if (!cred) throw ex;
      msg.textContent = "מאחד את המשתמשים…";
      const uc = await A.signInWithCredential(otherAuth().auth, cred);
      await absorbAccount(uc.user);
      let linked = true; await A.linkWithCredential(fb.auth.currentUser, cred).catch(() => { linked = false; });
      msg.textContent = MERGE_DONE + (linked ? " מעכשיו אפשר להיכנס למשתמש הזה גם עם Google." : "");
    }
    await fb.auth.currentUser.reload().catch(() => {});
    account.google = (fb.auth.currentUser.providerData || []).some((p) => p.providerId === "google.com");
    renderAccount();
  } catch (ex) {
    msg.textContent = "";
    const code = ex && ex.code;
    if (code !== "auth/popup-closed-by-user" && code !== "auth/cancelled-popup-request")
      err.textContent = code === "auth/popup-blocked" ? "הדפדפן חסם את חלון Google. אפשרו חלונות קופצים לאתר הזה ונסו שוב."
        : code === "auth/requires-recent-login" ? "מטעמי אבטחה צריך להתחבר מחדש: צאו מהמשתמש, היכנסו שוב ונסו שוב."
        : AUTH_ERRORS[code] || "האיחוד לא הצליח. נסו שוב בעוד רגע.";
  }
  b.disabled = false;
});
document.addEventListener("submit", async (e) => {
  if (e.target.id !== "mergeForm") return;
  e.preventDefault();
  const err = $("mergeErr"), msg = $("mergeMsg");
  err.textContent = ""; msg.textContent = "";
  if (!account) return;
  const name = $("mergeUser").value.trim(), pass = $("mergePass").value;
  const email = name.includes("@") ? name.toLowerCase() : userEmail(name);
  if (!name || !email) { err.textContent = "הקלידו את האימייל או שם המשתמש של המשתמש השני."; return; }
  if (!pass) { err.textContent = "צריך להקליד את הסיסמה של המשתמש השני."; return; }
  $("mergeSave").disabled = true; msg.textContent = "מאחד את המשתמשים…";
  try {
    const uc = await fb.mods.auth.signInWithEmailAndPassword(otherAuth().auth, email, pass);
    if (uc.user.uid === fb.auth.currentUser.uid) { msg.textContent = ""; err.textContent = "זה המשתמש שכבר מחובר עכשיו. הקלידו את הפרטים של המשתמש השני."; }
    else { await absorbAccount(uc.user); msg.textContent = MERGE_DONE; $("mergeUser").value = ""; $("mergePass").value = ""; }
  } catch (ex) {
    msg.textContent = "";
    const code = ex && ex.code;
    err.textContent = /invalid-(login-)?credential|wrong-password|user-not-found/.test(code || "") ? "האימייל / שם המשתמש או הסיסמה של המשתמש השני לא נכונים."
      : AUTH_ERRORS[code] || "האיחוד לא הצליח. נסו שוב בעוד רגע.";
  }
  $("mergeSave").disabled = false;
});

/* forgot password (email accounts only) and adding an email to a username account */
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
document.addEventListener("click", async (e) => {
  if (!e.target.closest("#forgotBtn")) return;
  const v = $("acctUser").value.trim(), msg = $("forgotMsg");
  $("acctErr").textContent = "";
  if (!v) { msg.textContent = "הקלידו למעלה את האימייל שאיתו נרשמתם, ולחצו שוב על \"שכחתי סיסמה\"."; return; }
  if (!v.includes("@")) { msg.textContent = "שחזור סיסמה אפשרי רק למי שנרשם עם אימייל. עם שם משתמש אין דרך לשחזר. אפשר לפתוח משתמש חדש, עדיף עם Google או אימייל."; return; }
  if (!EMAIL_RE.test(v)) { msg.textContent = "האימייל לא נראה תקין. בדקו שהקלדתם אותו נכון."; return; }
  const btn = $("forgotBtn"); btn.disabled = true; msg.textContent = "שולח…";
  try {
    await loadFirebase(); fb.auth.languageCode = "he";
    await fb.resetPass(fb.auth, v.toLowerCase());
    msg.textContent = `אם יש משתמש עם האימייל ${v}, שלחנו אליו קישור לבחירת סיסמה חדשה. כדאי לבדוק גם בתיקיית הספאם.`;
  } catch (ex) {
    const code = ex && ex.code;
    msg.textContent = code === "auth/user-not-found" ? "אין משתמש עם האימייל הזה." : code === "auth/invalid-email" ? "האימייל לא נראה תקין." : AUTH_ERRORS[code] || "השליחה לא הצליחה. נסו שוב בעוד רגע.";
  }
  btn.disabled = false;
});
document.addEventListener("submit", async (e) => {
  if (e.target.id !== "emailForm") return;
  e.preventDefault();
  const v = $("emailInput").value.trim().toLowerCase(), err = $("emailErr"), msg = $("emailMsg");
  err.textContent = ""; msg.textContent = "";
  if (!account || !account.canAddEmail) return;
  if (!EMAIL_RE.test(v)) { err.textContent = "האימייל לא נראה תקין. בדקו שהקלדתם אותו נכון."; return; }
  $("emailSave").disabled = true;
  try {
    fb.auth.languageCode = "he";
    if (!account.nick) {   // keep today's public name once sign-in switches to the email
      const nick = account.name.slice(0, 20);
      await Promise.all(LANGS.map((lang) => fb.setDoc(fb.doc(fb.db, "users", account.uid, "progress", lang), { nick }, { merge: true })));
      account.nick = nick; setShareName(); renderAccount();
    }
    await fb.verifyNewEmail(fb.auth.currentUser, v);
    msg.textContent = `שלחנו קישור אישור ל-${v} (כדאי לבדוק גם בספאם). אחרי שתלחצו עליו, תיכנסו עם האימייל הזה במקום שם המשתמש ${account.name}, עם אותה סיסמה.`;
    $("emailInput").value = "";
  } catch (ex) {
    const code = ex && ex.code;
    err.textContent = code === "auth/requires-recent-login" ? "מטעמי אבטחה צריך להתחבר מחדש: צאו מהמשתמש, היכנסו שוב ונסו שוב."
      : code === "auth/email-already-in-use" ? "האימייל הזה כבר שייך למשתמש אחר."
      : code === "auth/invalid-email" || code === "auth/invalid-new-email" ? "האימייל לא נראה תקין."
      : AUTH_ERRORS[code] || "השליחה לא הצליחה. נסו שוב בעוד רגע.";
  }
  $("emailSave").disabled = false;
});

/* shared associations: a comment-style list per word; signed-in users' notes are visible to everyone */
const notesCache = {}, notesLoading = {};
const noteKey = (w) => encodeURIComponent(w).replace(/\./g, "%2E");
const notesCol = (lang, w) => fb.collection(fb.db, "shared", lang, "words", noteKey(w), "notes");
const ck = (w, lang = ui.lang) => lang + "|" + w;
const localAdd = Assoc.add, localRemove = Assoc.remove;
function newNote(text, img) {
  const n = { uid: account.uid, text: String(text || "").trim().slice(0, 500), name: account.shareName.slice(0, 40), t: Date.now() };
  if (img) n.img = img;
  return n;
}
const privItem = (x) => (typeof x === "string" ? { text: x } : { text: String(x.text || ""), img: x.img || "" });
async function fetchNotes(lang, w) {
  const k = ck(w, lang);
  try {
    await loadFirebase();
    const snap = await fb.getDocs(fb.query(notesCol(lang, w), fb.orderBy("t", "desc"), fb.limit(60)));
    notesCache[k] = snap.docs.map((d) => ({ id: d.id, ...d.data() }));
    fixMyNoteNames(lang, w);
  } catch (e) { notesCache[k] = []; }
}
function afterNotes(w, lang) {
  if (lang !== ui.lang || !DICT) return;
  if (typeof modalWord !== "undefined" && modalWord === w) refreshAssoc(w);
  if (ui.view === "practice") {
    const cur = queue[pos];
    if (!cur || cur.w !== w) return;
    if (revealed) refreshAssoc(w); else if (hasMine(w)) renderPractice();
  } else refreshAssoc(w);
}
if (FIREBASE_CONFIG) {
  Assoc.mine = (w) => {
    if (!account) return localMine(w);
    const shared = (notesCache[ck(w)] || []).filter((n) => n.uid === account.uid).map((n) => {
      const anon = !n.name;
      return {
        id: n.id, text: n.text, img: n.img || "", vis: anon ? "anon" : "named", likeCount: (n.likes || []).length,
        badge: anon ? "גלוי לכולם, בלי שם" : `גלוי לכולם בשם ${n.name}`,
        actions: [anon ? { key: "named", label: "להציג את שמי" } : { key: "anon", label: "להפוך לאנונימי" }, { key: "hide", label: "להסתיר מכולם" }]
      };
    });
    const priv = (entry(w).pa || []).map((x, i) => ({
      id: "p" + i, ...privItem(x), vis: "private", badge: "מוסתר מכולם", actions: [{ key: "share", label: "לשתף" }]
    }));
    return shared.concat(priv);
  };
  Assoc.act = async (w, id, act) => {
    if (!account) return false;
    const k = ck(w), col = () => notesCol(ui.lang, w);
    try {
      await loadFirebase();
      if (act === "share") {
        const list = (entry(w).pa || []).slice();
        const [item] = list.splice(Number(id.slice(1)), 1);
        if (item === undefined) return false;
        const p = privItem(item);
        const ref = fb.doc(col()); const n = newNote(p.text, p.img);
        await fb.setDoc(ref, n);
        indexNote(ref.id, ui.lang, w); notifyNote(ui.lang, w, n);
        (notesCache[k] = notesCache[k] || []).unshift({ id: ref.id, ...n });
        setEntry(w, { pa: list });
        return true;
      }
      const old = (notesCache[k] || []).find((n) => n.id === id && n.uid === account.uid);
      if (!old) return false;
      if (act === "hide") {
        await fb.deleteDoc(fb.doc(col(), id));
        unindexNote(id, ui.lang);
        notesCache[k] = notesCache[k].filter((n) => n.id !== id);
        setEntry(w, { pa: (entry(w).pa || []).concat(old.img ? [{ text: old.text, img: old.img }] : [old.text]) });
        return true;
      }
      if (act === "anon" || act === "named") {
        const name = act === "anon" ? "" : account.shareName.slice(0, 40);
        await fb.updateDoc(fb.doc(col(), id), { name });
        old.name = name;
        return true;
      }
    } catch (e) {}
    return false;
  };
  Assoc.others = (w) => (notesCache[ck(w)] || []).filter((n) => !account || n.uid !== account.uid)
    .map((n) => ({ ...n, likeCount: (n.likes || []).length, liked: !!account && (n.likes || []).includes(account.uid) }));
  Assoc.like = async (w, id) => {
    if (!account) return "signin";
    const k = ck(w), n = (notesCache[k] || []).find((x) => x.id === id);
    if (!n || n.uid === account.uid) return false;
    const liked = (n.likes || []).includes(account.uid);
    try {
      await loadFirebase();
      await fb.updateDoc(fb.doc(notesCol(ui.lang, w), id), { likes: liked ? fb.arrayRemove(account.uid) : fb.arrayUnion(account.uid) });
      n.likes = liked ? (n.likes || []).filter((u) => u !== account.uid) : (n.likes || []).concat(account.uid);
      return true;
    } catch (e) { return false; }
  };
  Assoc.note = () => account
    ? `אסוציאציה חדשה גלויה לכולם בשם ${esc(account.shareName)}. לכל אסוציאציה אפשר לבחור להפוך לאנונימית או להסתיר מכולם.`
    : `בלי משתמש, האסוציאציות שלך נשמרות רק בדפדפן הזה. <button type="button" class="link signup-link">הירשמו בחינם</button> כדי לשמור אותן בכל המכשירים ולשתף עם אחרים.`;
  Assoc.canImage = () => !!account;
  Assoc.othersLocked = () => !account;
  if (typeof Stats !== "undefined") Stats.enabled = () => !!account;   // progress tracking for signed-in users only
  Assoc.add = async (w, text, img) => {
    if (!account) { if (!text) return false; const ok = await localAdd(w, text); if (ok) showLocalTip(); return ok; }
    try {
      await loadFirebase();
      const ref = fb.doc(notesCol(ui.lang, w));
      const n = newNote(text, img);
      await fb.setDoc(ref, n);
      indexNote(ref.id, ui.lang, w); notifyNote(ui.lang, w, n);
      (notesCache[ck(w)] = notesCache[ck(w)] || []).unshift({ id: ref.id, ...n });
      return true;
    } catch (e) { return false; }
  };
  Assoc.remove = async (w, id) => {
    if (!account) return localRemove(w, id);
    if (id.startsWith("p")) {
      const list = (entry(w).pa || []).slice(); list.splice(Number(id.slice(1)), 1);
      setEntry(w, { pa: list });
      return true;
    }
    try {
      await fb.deleteDoc(fb.doc(notesCol(ui.lang, w), id));
      unindexNote(id, ui.lang);
      notesCache[ck(w)] = (notesCache[ck(w)] || []).filter((n) => n.id !== id);
      return true;
    } catch (e) { return false; }
  };
  Assoc.prefetch = (w) => {
    if (!account) return;   // other users' associations are for signed-in users
    const lang = ui.lang, k = ck(w, lang);
    if (notesCache[k] || notesLoading[k]) return;
    notesLoading[k] = true;
    fetchNotes(lang, w).then(() => { notesLoading[k] = false; afterNotes(w, lang); });
  };
}
/* public counters: one tiny doc per member and per posted association */
const indexNote = (id, lang, w) => { rememberNote(lang, id, w); return fb.setDoc(fb.doc(fb.db, "noteIndex", id), { uid: account.uid, t: Date.now() }).catch(() => {}); };
const unindexNote = (id, lang) => { forgetNote(lang, id); return fb.deleteDoc(fb.doc(fb.db, "noteIndex", id)).catch(() => {}); };
async function loadCounts() {
  try {
    await loadFirebase();
    const [m, n] = await Promise.all([fb.count(fb.collection(fb.db, "members")), fb.count(fb.collection(fb.db, "noteIndex"))]);
    const users = m.data().count, notes = n.data().count, el = $("siteCounts");
    if (!users && !notes) return;
    el.innerHTML = `<span>👥 ${users.toLocaleString("he-IL")} ${users === 1 ? "משתמש רשום" : "משתמשים רשומים"}</span><span>💬 ${notes.toLocaleString("he-IL")} ${notes === 1 ? "אסוציאציה פורסמה" : "אסוציאציות פורסמו"}</span>`;
    el.hidden = false;
  } catch (e) {}
}

/* after sign-in, associations written on this device move into the shared list */
async function migrateLocalAssoc() {
  for (const lang of LANGS) {
    let changed = false;
    for (const [w, e] of Object.entries(state.p[lang])) {
      if (!e || !Array.isArray(e.a) || !e.a.length) continue;
      try {
        for (const text of e.a) {
          if (!String(text).trim()) continue;
          const ref = fb.doc(notesCol(lang, w));
          const n = newNote(text);
          await fb.setDoc(ref, n);
          indexNote(ref.id, lang, w);
          if (notesCache[ck(w, lang)]) notesCache[ck(w, lang)].unshift({ id: ref.id, ...n });
        }
      } catch (err) { break; }
      const rest = { ...e }; delete rest.a;
      if (Object.keys(rest).length) state.p[lang][w] = rest; else delete state.p[lang][w];
      changed = true;
    }
    if (changed) { lsSet(LS_STATE, state); queueWrite(lang); }
  }
}

/* backup file */
function backupMsg(t) { const el = $("backupMsg"); el.textContent = t; clearTimeout(backupMsg.t); backupMsg.t = setTimeout(() => (el.textContent = ""), 6000); }
document.addEventListener("click", (e) => {
  if (e.target.id === "exportBtn") {
    const blob = new Blob([JSON.stringify({ app: "ramzor-milim", v: 2, saved: new Date().toISOString(), state })], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "ramzor-milim-backup-" + new Date().toISOString().slice(0, 10) + ".json";
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
    backupMsg("הגיבוי נשמר. אפשר לפתוח אותו במכשיר אחר עם \"שחזור מגיבוי\".");
  }
  if (e.target.id === "importBtn") $("importFile").click();
});
document.addEventListener("change", (e) => {
  if (e.target.id !== "importFile" || !e.target.files[0]) return;
  const reader = new FileReader();
  reader.onload = () => {
    try {
      const d = JSON.parse(reader.result);
      if (!d || d.app !== "ramzor-milim" || !d.state) throw new Error("bad");
      state = normalize(d.state);
      save();
      resetView();
      backupMsg("ההתקדמות שוחזרה מהגיבוי.");
    } catch (err) { backupMsg("הקובץ הזה אינו גיבוי של רמזור מילים."); }
    e.target.value = "";
  };
  reader.readAsText(e.target.files[0]);
});

'''
local_save = local_save.replace("__WEB3FORMS_KEY__", WEB3FORMS_KEY)
local_save = local_save.replace("__FIREBASE_CONFIG__", json.dumps(firebase_config) if firebase_config else "null")
script = script[:start] + local_save + script[end:]

fetch_start = script.index('fetch("words.json")')
fetch_end = script.index("initCloud();") + len("initCloud();")
script = script[:fetch_start] + "DICT = { en: WORDS.en, he: WORDS.he };\nbuildQueue(); render();\nstartAccounts();" + script[fetch_end:]
script = script.replace('renderHeader(); setSync("local");', "renderHeader();")
_st_old = '  if (!cur.s || cur.s === "n") delete cur.s;\n  if (Object.keys(cur).length) state.p[lang][w] = cur;'
assert script.count(_st_old) == 1
script = script.replace(_st_old, '  if ("s" in patch && (patch.s || "n") !== (entry(w, lang).s || "n")) cur.st = Date.now();   // when the colour was set, so merges keep the newer one\n' + _st_old)
_rep_old = '`<button type="button" class="hide-note" data-key="${esc(favKey(n))}">הסתרה</button>`'
assert script.count(_rep_old) == 1
script = script.replace(_rep_old, '`${FIREBASE_CONFIG && n.uid && isAdminNow() ? `<button type="button" class="admin-note" data-uid="${esc(n.uid)}" data-name="${esc(n.name || "")}">ניהול</button>` : ""}${FIREBASE_CONFIG && n.id ? `<button type="button" class="report-note" data-note="${esc(n.id)}">דיווח</button>` : ""}<button type="button" class="hide-note" data-key="${esc(favKey(n))}">הסתרה</button>`')
# resetView clears the words cache so restored/merged custom words show up
script = script.replace("function resetView() { listShown = PAGE;", "function resetView() { for (const k in cache) delete cache[k]; listShown = PAGE;")
script = "const WORDS = " + json.dumps({"en": words["en"], "he": words["he"]}, ensure_ascii=False, separators=(",", ":")) + ";\n" + script

out_dir = os.environ.get("RAMZOR_OUT", REPO)
os.makedirs(out_dir, exist_ok=True)
html = head + body_html + "<script>\n" + script + "</script>\n</body>\n</html>\n"
open(out_dir + "index.html", "w", encoding="utf-8").write(html)
check_js = os.path.join(tempfile.gettempdir(), "ramzor_check.js")   # syntax check: node --check <this file>
open(check_js, "w", encoding="utf-8").write(script)
print("wrote", out_dir + "index.html", "| accounts:", "ON" if firebase_config else "off (no firebase-config.json yet)")
print("window.claude refs:", html.count("window.claude"))
