import os
import time
import random
import threading
import requests
import telebot
import schedule
from datetime import datetime, timedelta

# ================= الإعدادات =================
BOT_TOKEN = "8755170973:AAFGhhDJt_rjufga7QCIF7pOA4KofQfsuKk"
CHANNEL_ID = "@YourChannelUsername"  # معرف قناتك أو مجموعتك
STATE_FILE = "quran_page.txt"

bot = telebot.TeleBot(BOT_TOKEN)

# قائمة أحاديث نبوية صحيحة
HADITHS = [
    "قال رسول الله ﷺ: «خَيْرُكُمْ مَنْ تَعَلَّمَ القُرْآنَ وَعَلَّمَهُ». [رواه البخاري]",
    "قال رسول الله ﷺ: «مَنْ سَلَكَ طَرِيقًا يَلْتَمِسُ فِيهِ عِلْمًا، سَهَّلَ اللهُ لَهُ بِهِ طَرِيقًا إِلَى الْجَنَّةِ». [رواه مسلم]",
    "قال رسول الله ﷺ: «كَلِمَتَانِ خَفِيفَتَانِ عَلَى اللِّسَانِ، ثَقِيلَتَانِ فِي المِيزَانِ: سُبْحَانَ اللَّهِ وَبِحَمْدِهِ، سُبْحَانَ اللَّهِ العَظِيمِ». [متفق عليه]",
    "قال رسول الله ﷺ: «إِنَّمَا الأَعْمَالُ بِالنِّيَّاتِ، وَإِنَّمَا لِكُلِّ امْرِئٍ مَا نَوَى». [متفق عليه]",
    "قال رسول الله ﷺ: «اتَّقِ اللَّهَ حَيْثُمَا كُنْتَ، وَأَتْبِعِ السَّيِّئَةَ الحَسَنَةَ تَمْحُهَا، وَخَالِقِ النَّاسَ بِخُلُقٍ حَسَنٍ». [رواه الترمذي]",
    "قال رسول الله ﷺ: «مَنْ صَلَّى عَلَيَّ صَلَاةً صَلَّى اللَّهُ عَلَيْهِ بِهَا عَشْرًا». [رواه مسلم]"
]

# ================= أدوات جلب القرآن =================
def get_current_page():
    if not os.path.exists(STATE_FILE):
        return 1
    with open(STATE_FILE, "r") as f:
        try:
            return int(f.read().strip())
        except ValueError:
            return 1

def save_current_page(page_num):
    with open(STATE_FILE, "w") as f:
        f.write(str(page_num))

def fetch_random_ayah():
    """جلب آية عشوائية بالتشكيل من API القرآن"""
    try:
        ayah_num = random.randint(1, 6236)
        res = requests.get(f"https://api.alquran.cloud/v1/ayah/{ayah_num}/ar.alafasy", timeout=10)
        data = res.json()
        if data["code"] == 200:
            text = data["data"]["text"]
            surah = data["data"]["surah"]["name"]
            num_in_surah = data["data"]["numberInSurah"]
            return f"﴿ {text} ﴾\n\nسورة {surah} - الآية {num_in_surah}"
    except Exception:
        pass
    return "﴿ إِنَّ هَذَا الْقُرْآنَ يَهْدِي لِلَّتِي هِيَ أَقْوَمُ ﴾ [الإسراء: 9]"

# ================= النشر التلقائي اليومي =================
def daily_post():
    page = get_current_page()
    page_str = str(page).zfill(3)
    
    # رابط الصفحة من مصحف المدينة المنورة
    image_url = f"https://everyayah.com/data/quranpngs/{page_str}.png"
    hadith = random.choice(HADITHS)
    ayah = fetch_random_ayah()
    
    caption = (
        f"📖 <b>ورد اليوم: صفحة رقم ({page})</b>\n\n"
        f"✨ <b>آية مختارة:</b>\n{ayah}\n\n"
        f"🌿 <b>حديث شريف:</b>\n{hadith}\n\n"
        f"🤲 <i>اللهم اجعل القرآن الكريم ربيع قلوبنا وجلاء همومنا.</i>"
    )
    
    try:
        bot.send_photo(chat_id=CHANNEL_ID, photo=image_url, caption=caption, parse_mode="HTML")
        print(f"تم النشر التلقائي: صفحة {page}")
        next_page = page + 1 if page < 604 else 1
        save_current_page(next_page)
    except Exception as e:
        print(f"خطأ أثناء النشر: {e}")

# ================= فحص صلاحيات المشرفين =================
def is_admin(chat_id, user_id):
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ['creator', 'administrator']
    except Exception:
        return False

# ================= معالجة الأوامر العربية =================
@bot.message_handler(func=lambda msg: True)
def handle_arabic_commands(message):
    text = message.text.strip() if message.text else ""
    chat_id = message.chat.id
    
    # --- قائمة المساعدة والترحيب ---
    if text in ["اوامر", "الاوامر", "مساعدة", "/start"]:
        help_msg = (
            "📖 <b>مرحباً بك! أوامر البوت المتاحة:</b>\n\n"
            "🔹 <b>اية</b> : إرسال آية عشوائية بالتشكيل\n"
            "🔹 <b>حديث</b> : إرسال حديث نبوي شريف\n"
            "🔹 <b>صفحة [رقم]</b> : لعرض صفحة مصحف (مثال: <code>صفحة 20</code>)\n\n"
            "🛡 <b>أوامر إدارة المجموعات (بالرد على الشخص):</b>\n"
            "🔸 <b>حظر</b> : طرد وحظر العضو من المجموعة\n"
            "🔸 <b>الغاء الحظر</b> : فك الحظر عن العضو\n"
            "🔸 <b>كتم</b> أو <b>اسكات</b> : منع العضو من الكتابة\n"
            "🔸 <b>رفع ادمن</b> : ترقية العضو لمشرف\n"
            "🔸 <b>تنزيل ادمن</b> : سحب الإشراف من العضو"
        )
        bot.reply_to(message, help_msg, parse_mode="HTML")
        return

    # --- آية عشوائية ---
    if text == "اية":
        ayah_text = fetch_random_ayah()
        bot.reply_to(message, f"✨ <b>آية كريمة:</b>\n\n{ayah_text}", parse_mode="HTML")
        return

    # --- حديث عشوائي ---
    if text == "حديث":
        bot.reply_to(message, f"🌿 <b>حديث شريف:</b>\n\n{random.choice(HADITHS)}", parse_mode="HTML")
        return

    # --- طلب صفحة معينة ---
    if text.startswith("صفحة "):
        parts = text.split()
        if len(parts) == 2 and parts[1].isdigit():
            p_num = int(parts[1])
            if 1 <= p_num <= 604:
                p_str = str(p_num).zfill(3)
                img = f"https://everyayah.com/data/quranpngs/{p_str}.png"
                bot.send_photo(chat_id, photo=img, caption=f"📖 المصحف الشريف - صفحة رقم ({p_num})")
            else:
                bot.reply_to(message, "⚠️ رقم الصفحة يجب أن يكون بين 1 و 604.")
        return

    # ================= أوامر الإدارة (للمشرفين بالرد على رسالة) =================
    admin_commands = ["حظر", "الغاء الحظر", "كتم", "اسكات", "رفع ادمن", "ترقية", "تنزيل ادمن"]
    if text in admin_commands:
        if message.chat.type not in ['group', 'supergroup']:
            bot.reply_to(message, "⚠️ هذه الأوامر تعمل داخل المجموعات فقط.")
            return

        # التأكد أن من يكتب الأمر مشرف
        if not is_admin(chat_id, message.from_user.id):
            bot.reply_to(message, "⛔ هذا الأمر مخصص لمشرفي المجموعة فقط.")
            return

        # التأكد من الرد على رسالة
        if not message.reply_to_message:
            bot.reply_to(message, f"⚠️ يجب الرد على رسالة العضو وكتابة <b>{text}</b>.", parse_mode="HTML")
            return

        target_user = message.reply_to_message.from_user

        # أمر الحظر
        if text == "حظر":
            try:
                bot.ban_chat_member(chat_id, target_user.id)
                bot.reply_to(message, f"🚫 تم حظر العضو: <b>{target_user.first_name}</b> بنجاح.", parse_mode="HTML")
            except Exception:
                bot.reply_to(message, "⚠️ تعذر الحظر، تأكد أن البوت يملك صلاحيات المشرف كاملة.")

        # أمر فك الحظر
        elif text == "الغاء الحظر":
            try:
                bot.unban_chat_member(chat_id, target_user.id, only_if_banned=True)
                bot.reply_to(message, f"✅ تم إلغاء حظر العضو: <b>{target_user.first_name}</b>.", parse_mode="HTML")
            except Exception:
                bot.reply_to(message, "⚠️ تعذر فك الحظر.")

        # أمر الكتم
        elif text in ["كتم", "اسكات"]:
            try:
                bot.restrict_chat_member(
                    chat_id=chat_id,
                    user_id=target_user.id,
                    until_date=datetime.now() + timedelta(hours=1),
                    can_send_messages=False
                )
                bot.reply_to(message, f"🔇 تم كتم العضو: <b>{target_user.first_name}</b> لمدة ساعة.", parse_mode="HTML")
            except Exception:
                bot.reply_to(message, "⚠️ تعذر كتم العضو.")

        # رفع مشرف
        elif text in ["رفع ادمن", "ترقية"]:
            try:
                bot.promote_chat_member(
                    chat_id=chat_id,
                    user_id=target_user.id,
                    can_change_info=True,
                    can_post_messages=True,
                    can_edit_messages=True,
                    can_delete_messages=True,
                    can_invite_users=True,
                    can_restrict_members=True,
                    can_pin_messages=True,
                    can_promote_members=False
                )
                bot.reply_to(message, f"⭐ تمت ترقية <b>{target_user.first_name}</b> إلى مشرف في المجموعة.", parse_mode="HTML")
            except Exception:
                bot.reply_to(message, "⚠️ تعذر الترقية، تأكد أن البوت يملك صلاحية إضافة مشرفين.")

        # تنزيل مشرف
        elif text == "تنزيل ادمن":
            try:
                bot.promote_chat_member(
                    chat_id=chat_id,
                    user_id=target_user.id,
                    can_change_info=False,
                    can_post_messages=False,
                    can_edit_messages=False,
                    can_delete_messages=False,
                    can_invite_users=False,
                    can_restrict_members=False,
                    can_pin_messages=False,
                    can_promote_members=False
                )
                bot.reply_to(message, f"🔻 تم تجريد <b>{target_user.first_name}</b> من رتبة الإشراف.", parse_mode="HTML")
            except Exception:
                bot.reply_to(message, "⚠️ تعذر تنزيل المشرف.")

# ================= تشغيل الجدولة التلقائية =================
def run_scheduler():
    # توقيت النشر التلقائي كل يوم (الساعة 06:00 صباحاً)
    schedule.every().day.at("06:00").do(daily_post)
    while True:
        schedule.run_pending()
        time.sleep(30)

threading.Thread(target=run_scheduler, daemon=True).start()

print("✅ تم تشغيل البوت بنجاح ومستعد لاستقبال الأوامر العربية...")
bot.infinity_polling()
