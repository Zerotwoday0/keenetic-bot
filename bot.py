import os
import hashlib
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN", "8526033732:AAH_vaPPPm0f3wtuatJhpff73xwDG6bV0SQ")
ROUTER = "https://3fd8196059599b47b0c11f7f.netcraze.io"
USER = "admin"
PASS = "a4lllvl966a1982xi"
I0 = "WifiMaster0/AccessPoint1"
I1 = "WifiMaster1/AccessPoint1"

session = requests.Session()

def md5(s):
    return hashlib.md5(s.encode()).hexdigest()

def sha256(s):
    return hashlib.sha256(s.encode()).hexdigest()

def auth():
    r1 = session.get(f"{ROUTER}/auth")
    if r1.status_code == 200:
        return True
    realm = r1.headers.get("X-NDM-Realm", "")
    challenge = r1.headers.get("X-NDM-Challenge", "")
    if not realm or not challenge:
        return False
    h = sha256(challenge + md5(f"{USER}:{realm}:{PASS}"))
    r2 = session.post(f"{ROUTER}/auth", json={"login": USER, "password": h})
    return r2.status_code == 200

def get_status():
    try:
        auth()
        r = session.get(f"{ROUTER}/rci/show/interface")
        if r.status_code != 200:
            return None
        data = r.json()
        iface = data.get(I0, {})
        return iface.get("state") == "up" or iface.get("up") == True
    except:
        return None

def set_enabled(on: bool):
    try:
        auth()
        r = session.post(f"{ROUTER}/rci/", json={
            "interface": {
                I0: {"up": on},
                I1: {"up": on}
            }
        })
        return r.status_code in [200, 204]
    except:
        return False

def make_keyboard(status):
    if status is True:
        btn = InlineKeyboardButton("❌ Выключить гостевую сеть", callback_data="off")
    elif status is False:
        btn = InlineKeyboardButton("✅ Включить гостевую сеть", callback_data="on")
    else:
        btn = InlineKeyboardButton("🔄 Обновить статус", callback_data="refresh")
    refresh = InlineKeyboardButton("🔄 Обновить", callback_data="refresh")
    return InlineKeyboardMarkup([[btn], [refresh]])

def status_text(status):
    if status is True:
        return "📶 Гостевая сеть: *ВКЛЮЧЕНА* ✅"
    elif status is False:
        return "📶 Гостевая сеть: *ВЫКЛЮЧЕНА* ❌"
    else:
        return "📶 Гостевая сеть: *НЕИЗВЕСТНО* ❓"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status = get_status()
    await update.message.reply_text(
        f"🏠 *Keenetic Extra KN-1714*\n\n{status_text(status)}",
        parse_mode="Markdown",
        reply_markup=make_keyboard(status)
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "on":
        await query.edit_message_text("⏳ Включаю гостевую сеть...", parse_mode="Markdown")
        set_enabled(True)
        import time; time.sleep(2)
        status = get_status()
    elif query.data == "off":
        await query.edit_message_text("⏳ Выключаю гостевую сеть...", parse_mode="Markdown")
        set_enabled(False)
        import time; time.sleep(2)
        status = get_status()
    else:
        status = get_status()

    await query.edit_message_text(
        f"🏠 *Keenetic Extra KN-1714*\n\n{status_text(status)}",
        parse_mode="Markdown",
        reply_markup=make_keyboard(status)
    )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    print("Bot started!")
    app.run_polling()

if __name__ == "__main__":
    main()
