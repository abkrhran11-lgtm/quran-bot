import os
import time
import random
import threading
import requests
import telebot
from telebot import types
import schedule
from datetime import datetime, timedelta

# ================= الإعدادات =================
BOT_TOKEN = "8755170973:AAFGhhDJt_rjufga7QCIF7pOA4KofQfsuKk"
ADMIN_ID = 0  # ضع معرف حسابك الرقمي هنا (اختياري)
WHATSAPP_NUMBER = "249118626801"
DEFAULT_CHANNEL = "@YourChannelUsername"  # معرف قناتك
STATE_FILE = "quran_page.txt"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# عداد التسبيح التفاعلي المؤقت للمستخدمين
USER_TASBEEH = {}

# حماية المجموعات
GROUP_PROTECTION = {
    "lock_links": True,
    "lock_forward": True
}

# ================= المكتبة الصوتية الشاملة =================
AUDIO_LIBRARY = {
    "🎙 الشيخ د. محمد سيد حاج (مدارج السالكين)": "https://server11.mp3quran.net/download/hajj/001.mp3",
    "🎙 الشيخ محمود الحسنات (موعظة خاشعة)": "https://server16.mp3quran.net/download/hasanat/001.mp3",
    "🎙 الشيخ محمد المجتبى (خواطر إيمانية)": "https://server11.mp3quran.net/download/hajj/002.mp3",
    "📖 القارئ نورين محمد صديق (تلاوة سودانية)": "https://server10.mp3quran.net/download/nourin/001.mp3",
    "📖 القارئ الزين محمد أحمد (المصحف المرتل)": "https://server9.mp3quran.net/download/alzain/001.mp3",
    "📖 القارئ الفاتح محمد زبير (رواية الدوري)": "https://server10.mp3quran.net/download/fateh/001.mp3"
}

# ================= مكتبة الكتب الإسلامية =================
ISLAMIC_BOOKS = {
    "📘 حصن المسلم من أذكار الكتاب والسنة": "https://www.alukah.net/books/files/book_1113/bookfile/hisn_almuslim.pdf",
    "📗 متن الأربعين النووية": "https://www.alukah.net/books/files/book_1549/bookfile/arbaeen_nawawiya.pdf",
    "📙 رياض الصالحين للإمام النووي": "https://www.alukah.net/books/files/book_4102/bookfile/riyad_al-saliheen.pdf",
    "📕 الرحيق المختوم في السيرة النبوية": "https://www.alukah.net/books/files/book_4875/bookfile/raheeq_makhtoum.pdf"
}

# ================= بنك الأسئلة والمسابقات =================
ISLAMIC_QUIZZES = [
    {
        "q": "⭐ ما هي أعظم آية في كتاب الله تعالى؟",
        "options": ["آية الدين", "آية الكرسي", "آخر آية في البقرة", "أول آية في الكهف"],
        "ans": 1
    },
    {
        "q": "⭐ من هو الصحابي الملقب بـ أمين هذه الأمة؟",
        "options": ["أبو عبيدة بن الجراح", "خالد بن الوليد", "عمر بن الخطاب", "علي بن أبي طالب"],
        "ans": 0
    },
    {
        "q": "⭐ سورة في القرآن تسمى المنجية من عذاب القبر؟",
        "options": ["سورة يس", "سورة الواقعة", "سورة الملك", "سورة الدخان"],
        "ans": 2
    },
    {
        "q": "⭐ كم عدد السجدات في القرآن الكريم؟",
        "options": ["11 سجدة", "14 سجدة", "15 سجدة", "12 سجدة"],
        "ans": 2
    }
]

# ================= الأذكار =================
ADHIKAR = {
    "sabah": (
        "🌅 <b>أذكار الصباح:</b>\n\n"
        "• «أَصْبَحْنَا وَأَصْبَحَ المُلْكُ لِلَّهِ، وَالحَمْدُ لِلَّهِ لاَ إِلَهَ إِلاَّ اللَّهُ وَحْدَهُ لاَ شَرِيكَ لَهُ».\n"
        "• «اللّهُـمَّ بِكَ أَصْـبَحْنا وَبِكَ أَمْسَـينا، وَبِكَ نَحْـيا وَبِكَ نَمُـوتُ وَإِلَـيْكَ النُّـشُور».\n"
        "• «يَا حَيُّ يَا قَيُّومُ بِرَحْمَتِكَ أَسْتَغِيثُ، أَصْلِحْ لِي شَأْنِي كُلَّهُ، وَلَا تَكِلْنِي إِلَى نَفْسِي طَرْفَةَ عَيْنٍ»."
    ),
    "masaa": (
        "🌃 <b>أذكار المساء:</b>\n\n"
        "• «أَمْسَيْنَا وَأَمْسَى المُلْكُ لِلَّهِ، وَالحَمْدُ لِلَّهِ لاَ إِلَهَ إِلاَّ اللَّهُ».\n"
        "• «اللّهُـمَّ ما أَمسى بي مِنْ نِعْمَةٍ أَو بِأَحَدٍ مِنْ خَلْقِكَ، فَمِنْكَ وَحْدَكَ لاَ شَرِيكَ لَكَ».\n"
        "• «أَعُوذُ بِكَلِمَاتِ اللَّهِ التَّامَّاتِ مِنْ شَرِّ مَا خَلَقَ» (3 مرات)."
    ),
    "sleep": (
        "🛌 <b>أذكار النوم:</b>\n\n"
        "• «بِاسْمِكَ رَبِّي وَضَعْتُ جَنْبِي وَبِكَ أَرْفَعُهُ».\n"
        "• قراءة آية الكرسي والمعوذتين.\n"
        "• «اللَّهُمَّ قِنِي عَذَابَكَ يَوْمَ تَبْعَثُ عِبَادَكَ»."
    )
}

HADITHS = [
    "قال رسول الله ﷺ: «خَيْرُكُمْ مَنْ تَعَلَّمَ القُرْآنَ وَعَلَّمَهُ». [رواه البخاري]",
    "قال رسول الله ﷺ: «مَنْ سَلَكَ طَرِيقًا يَلْتَمِسُ فِيهِ عِلْمًا، سَهَّلَ اللهُ لَهُ بِهِ طَرِيقًا إِلَى الْجَنَّةِ». [رواه مسلم]",
    "قال رسول الله ﷺ: «كَلِمَتَانِ خَفِيفَتَانِ عَلَى اللِّسَانِ، ثَقِيلَتَانِ فِي المِيزَانِ: سُبْحَانَ اللَّهِ وَبِحَمْدِهِ، سُبْحَانَ اللَّهِ العَظِيمِ». [متفق عليه]",
    "قال رسول الله ﷺ: «إِنَّمَا الأَعْمَالُ بِالنِّيَّاتِ، وَإِنَّمَا لِكُلِّ امْرِئٍ مَا نَوَى». [متفق عليه]",
    "قال رسول الله ﷺ: «مَنْ صَلَّى عَلَيَّ صَلَاةً صَلَّى اللَّهُ عَلَيْهِ بِهَا عَشْرًا». [رواه مسلم]"
]

# ================= أدوات القرآن =================
def get_current_page():
    if not os.path.exists(STATE_FILE):
        return 1
    with open(STATE_FILE, "r") as f:
        try:
            return int(f.read().strip())
        except Exception:
            return 1

def save_current_page(page_num):
    with open(STATE_FILE, "w") as f:
        f.write(str(page_num))

def fetch_random_ayah():
    try:
        ayah_num = random.randint(1, 6236)
        res = requests.get(f"https://api.alquran.cloud/v1/ayah/{ayah_num}/ar.alafasy", timeout=8)
        data = res.json()
        if data["code"] == 200:
            text = data["data"]["text"]
            surah = data["data"]["surah"]["name"]
            num = data["data"]["numberInSurah"]
            return f"﴿ {text} ﴾\n\n📖 سورة {surah} - الآية {num}"
    except Exception:
        pass
    return "﴿ إِنَّ هَذَا الْقُرْآنَ يَهْدِي لِلَّتِي هِيَ أَقْوَمُ ﴾ [الإسراء: 9]"

# ================= النشر اليومي بالقناة =================
def daily_post():
    page = get_current_page()
    page_str = str(page).zfill(3)
    image_url = f"https://everyayah.com/data/quranpngs/{page_str}.png"
    hadith = random.choice(HADITHS)
    ayah = fetch_random_ayah()

    caption = (
        f"👑 <b>ورد اليوم المبارك | الصفحة ({page})</b> 👑\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"{ayah}\n\n"
        f"💎 <b>حديث اليوم:</b>\n{hadith}\n\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🤲 <i>اللهم اجعل القرآن ربيع قلوبنا وشفيعنا يوم نلقاك.</i>"
    )
    try:
        bot.send_photo(chat_id=DEFAULT_CHANNEL, photo=image_url, caption=caption)
        next_page = page + 1 if page < 604 else 1
        save_current_page(next_page)
    except Exception as e:
        print(f"Error daily: {e}")

# ================= القوائم التفاعلية =================
def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    b1 = types.InlineKeyboardButton("📖 المصحف الشريف", callback_data="m_quran")
    b2 = types.InlineKeyboardButton("🎙 صوتيات ومحاضرات سودانية", callback_data="m_audio")
    b3 = types.InlineKeyboardButton("📿 السُّبحة الإلكترونية", callback_data="m_tasbeeh")
    b4 = types.InlineKeyboardButton("📜 حصن المسلم والأذكار", callback_data="m_adhkar")
    b5 = types.InlineKeyboardButton("📚 مكتبة الكتب الإسلامية", callback_data="m_books")
    b6 = types.InlineKeyboardButton("🎲 مسابقة واختبار إسلامي", callback_data="m_quiz")
    b7 = types.InlineKeyboardButton("✨ آية وحديث فوري", callback_data="m_ayah_hadith")
    b8 = types.InlineKeyboardButton("⚙️ لوحة تحكم النشر", callback_data="m_admin_panel")
    
    # زر الواتساب للمطور بنمط مميز
    b_whatsapp = types.InlineKeyboardButton(
        "💬 تواصل مع المطور (WhatsApp)",
        url=f"https://wa.me/{WHATSAPP_NUMBER}?text=%D8%A7%D9%84%D8%B3%D9%84%D8%A7%D9%85%20%D8%B9%D9%84%D9%8A%D9%83%D9%85%D8%8C%20%D8%A3%D8%B1%D8%BA%D8%A8%20%D9%81%D9%8A%20%D8%AA%D9%81%D8%B9%D9%8A%D9%84%20%D8%A7%D9%84%D8%A8%D9%88%D8%AA%20%D8%A7%D9%84%D8%A5%D8%B3%D9%84%D8%A7%D9%85%D9%8A"
    )

    markup.add(b1, b2)
    markup.add(b3, b4)
    markup.add(b5, b6)
    markup.add(b7)
    markup.add(b8)
    markup.add(b_whatsapp)
    return markup

# ================= البداية /start =================
@bot.message_handler(commands=['start'])
def send_start(message):
    if message.chat.type == 'private':
        text = (
            f"👑 <b>مرحباً بك يا {message.from_user.first_name} في البوت الإسلامي الملكي</b> 👑\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🌟 <b>خدمات البوت المتاحة بين يديك:</b>\n\n"
            f"🔹 صفحات المصحف الشريف كاملة بجودة فائقة\n"
            f"🔹 تلاوات ومحاضرات أعلام الدعوة في السودان والعالم\n"
            f"🔹 سُبحة إلكترونية تفاعلية حية\n"
            f"🔹 أذكار الصباح والمساء والنوم\n"
            f"🔹 مكتبة كتب بصيغة PDF قابلة للتحميل\n"
            f"🔹 مسابقات واختبارات دينية فورية\n"
            f"🔹 حماية وتأمين المجموعات من الروابط والإعلانات\n\n"
            f"👇 <i>اضغط على الخيارات أدناه للتنقل بحرية:</i>"
        )
        bot.send_message(message.chat.id, text, reply_markup=main_menu())
    else:
        bot.reply_to(message, "🌟 البوت مفعل في المجموعة! اكتب <b>الاوامر</b> لعرض أدوات الإشراف.")

# ================= معالجة الكول باك والأزرار =================
@bot.callback_query_handler(func=lambda call: True)
def process_callbacks(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id

    if call.data == "m_quran":
        markup = types.InlineKeyboardMarkup(row_width=3)
        pages = [1, 50, 100, 200, 300, 400, 500, 604]
        for p in pages:
            markup.add(types.InlineKeyboardButton(f"📄 صفحة {p}", callback_data=f"p_{p}"))
        bot.send_message(chat_id, "📖 اختر الصفحة أو اكتب في الرسائل: <code>صفحة 20</code>", reply_markup=markup)

    elif call.data.startswith("p_"):
        p = call.data.split("_")[1]
        p_str = str(p).zfill(3)
        img = f"https://everyayah.com/data/quranpngs/{p_str}.png"
        bot.send_photo(chat_id, photo=img, caption=f"📖 المصحف الشريف | صفحة ({p})")

    elif call.data == "m_audio":
        markup = types.InlineKeyboardMarkup(row_width=1)
        for name in AUDIO_LIBRARY.keys():
            markup.add(types.InlineKeyboardButton(name, callback_data=f"aud_{name[:18]}"))
        bot.send_message(chat_id, "🎙 اختر التلاوة أو المحاضرة للاستماع المباشر:", reply_markup=markup)

    elif call.data.startswith("aud_"):
        tag = call.data.replace("aud_", "")
        for full_name, link in AUDIO_LIBRARY.items():
            if full_name.startswith(tag):
                bot.send_audio(chat_id, audio=link, caption=f"✨ {full_name}")
                break

    elif call.data == "m_tasbeeh":
        USER_TASBEEH[user_id] = 0
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("📿 سُبحان الله (0)", callback_data="tsb_click"),
            types.InlineKeyboardButton("🔄 تصفير العداد", callback_data="tsb_reset")
        )
        bot.send_message(chat_id, "📿 <b>السُّبحة الإلكترونية الذكية:</b>\nاضغط على الزر للتسبيح:", reply_markup=markup)

    elif call.data == "tsb_click":
        count = USER_TASBEEH.get(user_id, 0) + 1
        USER_TASBEEH[user_id] = count
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton(f"📿 سُبحان الله ({count})", callback_data="tsb_click"),
            types.InlineKeyboardButton("🔄 تصفير العداد", callback_data="tsb_reset")
        )
        try:
            bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=markup)
        except Exception:
            pass

    elif call.data == "tsb_reset":
        USER_TASBEEH[user_id] = 0
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("📿 سُبحان الله (0)", callback_data="tsb_click"),
            types.InlineKeyboardButton("🔄 تصفير العداد", callback_data="tsb_reset")
        )
        bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id, "تم تصفير العداد.")

    elif call.data == "m_adhkar":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("🌅 أذكار الصباح", callback_data="adk_sabah"),
            types.InlineKeyboardButton("🌃 أذكار المساء", callback_data="adk_masaa"),
            types.InlineKeyboardButton("🛌 أذكار النوم", callback_data="adk_sleep")
        )
        bot.send_message(chat_id, "📜 <b>اختر من الأذكار النبوية:</b>", reply_markup=markup)

    elif call.data.startswith("adk_"):
        key = call.data.replace("adk_", "")
        bot.send_message(chat_id, ADHIKAR.get(key, ""))

    elif call.data == "m_books":
        markup = types.InlineKeyboardMarkup(row_width=1)
        for b_title, b_url in ISLAMIC_BOOKS.items():
            markup.add(types.InlineKeyboardButton(b_title, url=b_url))
        bot.send_message(chat_id, "📚 <b>مكتبة الكتب الإسلامية (تحميل وقراءة مباشرة PDF):</b>", reply_markup=markup)

    elif call.data == "m_quiz":
        q = random.choice(ISLAMIC_QUIZZES)
        bot.send_poll(chat_id, q["q"], q["options"], type='quiz', correct_option_id=q["ans"], is_anonymous=False)

    elif call.data == "m_ayah_hadith":
        bot.send_message(chat_id, f"{fetch_random_ayah()}\n\n💎 <b>حديث شريف:</b>\n{random.choice(HADITHS)}")

    elif call.data == "m_admin_panel":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("🚀 نشر ورد اليوم بالقناة فوراً", callback_data="act_pub_daily"),
            types.InlineKeyboardButton("📢 نشر آية عشوائية بالقناة", callback_data="act_pub_ayah"),
            types.InlineKeyboardButton("🌿 نشر حديث شريف بالقناة", callback_data="act_pub_hadith")
        )
        bot.send_message(chat_id, "⚙️ <b>لوحة التحكم السريعة للمشرفين:</b>", reply_markup=markup)

    elif call.data == "act_pub_daily":
        daily_post()
        bot.answer_callback_query(call.id, "✅ تم نشر الورد في القناة بنجاح.")

    elif call.data == "act_pub_ayah":
        bot.send_message(DEFAULT_CHANNEL, fetch_random_ayah())
        bot.answer_callback_query(call.id, "✅ تم نشر الآية في القناة.")

    elif call.data == "act_pub_hadith":
        bot.send_message(DEFAULT_CHANNEL, f"💎 <b>حديث اليوم:</b>\n\n{random.choice(HADITHS)}")
        bot.answer_callback_query(call.id, "✅ تم نشر الحديث في القناة.")

# ================= فحص إشراف المجموعة =================
def is_admin(chat_id, user_id):
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ['creator', 'administrator']
    except Exception:
        return False

# ================= معالجة الرسائل والأوامر =================
@bot.message_handler(func=lambda msg: True, content_types=['text', 'photo', 'video', 'document'])
def handle_messages(message):
    chat_id = message.chat.id
    text = message.text.strip() if message.text else ""

    # حماية المجموعات التلقائية
    if message.chat.type in ['group', 'supergroup']:
        if not is_admin(chat_id, message.from_user.id):
            if GROUP_PROTECTION["lock_links"] and ("http://" in text or "https://" in text or "t.me/" in text):
                try:
                    bot.delete_message(chat_id, message.message_id)
                    w = bot.send_message(chat_id, f"⚠️ عذراً يا {message.from_user.first_name}، نشر الروابط محظور بالمجموعة.")
                    time.sleep(3)
                    bot.delete_message(chat_id, w.message_id)
                    return
                except Exception:
                    pass

            if GROUP_PROTECTION["lock_forward"] and message.forward_date:
                try:
                    bot.delete_message(chat_id, message.message_id)
                    return
                except Exception:
                    pass

    # قائمة الأوامر المباشرة
    if text in ["اوامر", "الاوامر", "مساعدة"]:
        help_text = (
            "👑 <b>دليل الأوامر الشامل:</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🔹 <b>اية</b> : إرسال آية كريمة بالتشكيل\n"
            "🔹 <b>حديث</b> : إرسال حديث نبوي صحيح\n"
            "🔹 <b>صفحة [رقم]</b> : عرض أي صفحة مصحف (مثال: <code>صفحة 45</code>)\n"
            "🔹 <b>سؤال</b> : طرح سؤال ديني بالخيارات\n"
            "🔹 <b>اذكار</b> : عرض قائمة الأذكار\n"
            "🔹 <b>المطور</b> : للتواصل المباشر مع مطور البوت\n\n"
            "🛡 <b>أوامر المشرفين (بالرد على الشخص في المجموعة):</b>\n"
            "🔸 <b>حظر</b> : طرد وحظر نهائي\n"
            "🔸 <b>الغاء الحظر</b> : فك الحظر\n"
            "🔸 <b>كتم</b> أو <b>اسكات</b> : منع من الكتابة\n"
            "🔸 <b>رفع ادمن</b> : ترقية المشرف\n"
            "🔸 <b>تنزيل ادمن</b> : سحب رتبة المشرف"
        )
        bot.reply_to(message, help_text)
        return

    if text == "اية":
        bot.reply_to(message, fetch_random_ayah())
        return

    if text == "حديث":
        bot.reply_to(message, f"💎 <b>حديث شريف:</b>\n\n{random.choice(HADITHS)}")
        return

    if text == "المطور":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("💬 مراسلة المطور عبر WhatsApp", url=f"https://wa.me/{WHATSAPP_NUMBER}"))
        bot.reply_to(message, "👑 للتواصل مع مطور البوت والاتفاق:", reply_markup=markup)
        return

    if text.startswith("صفحة "):
        parts = text.split()
        if len(parts) == 2 and parts[1].isdigit():
            p_num = int(parts[1])
            if 1 <= p_num <= 604:
                p_str = str(p_num).zfill(3)
                img = f"https://everyayah.com/data/quranpngs/{p_str}.png"
                bot.send_photo(chat_id, photo=img, caption=f"📖 المصحف الشريف | صفحة ({p_num})")
            else:
                bot.reply_to(message, "⚠️ رقم الصفحة يجب أن يكون بين 1 و 604.")
        return

    # أوامر الإشراف بالرد على رسالة
    admin_cmds = ["حظر", "الغاء الحظر", "كتم", "اسكات", "رفع ادمن", "ترقية", "تنزيل ادمن"]
    if text in admin_cmds and message.chat.type in ['group', 'supergroup']:
        if not is_admin(chat_id, message.from_user.id):
            bot.reply_to(message, "⛔ هذا الأمر مخصص لمشرفي المجموعة فقط.")
            return

        if not message.reply_to_message:
            bot.reply_to(message, f"⚠️ قم بالرد على رسالة العضو واكتب <b>{text}</b>.")
            return

        target = message.reply_to_message.from_user

        if text == "حظر":
            try:
                bot.ban_chat_member(chat_id, target.id)
                bot.reply_to(message, f"🚫 تم حظر العضو: <b>{target.first_name}</b> بنجاح.")
            except Exception:
                bot.reply_to(message, "⚠️ تعذر الحظر، تأكد من صلاحيات البوت الإدارية.")

        elif text == "الغاء الحظر":
            try:
                bot.unban_chat_member(chat_id, target.id, only_if_banned=True)
                bot.reply_to(message, f"✅ تم فك الحظر عن: <b>{target.first_name}</b>.")
            except Exception:
                bot.reply_to(message, "⚠️ تعذر فك الحظر.")

        elif text in ["كتم", "اسكات"]:
            try:
                bot.restrict_chat_member(chat_id, target.id, until_date=datetime.now() + timedelta(hours=1), can_send_messages=False)
                bot.reply_to(message, f"🔇 تم كتم <b>{target.first_name}</b> لمدة ساعة.")
            except Exception:
                bot.reply_to(message, "⚠️ تعذر كتم العضو.")

        elif text in ["رفع ادمن", "ترقية"]:
            try:
                bot.promote_chat_member(
                    chat_id, target.id,
                    can_change_info=True, can_delete_messages=True,
                    can_invite_users=True, can_restrict_members=True,
                    can_pin_messages=True
                )
                bot.reply_to(message, f"⭐ تمت ترقية <b>{target.first_name}</b> إلى مشرف في المجموعة.")
            except Exception:
                bot.reply_to(message, "⚠️ تعذر الترقية.")

        elif text == "تنزيل ادمن":
            try:
                bot.promote_chat_member(
                    chat_id, target.id,
                    can_change_info=False, can_delete_messages=False,
                    can_invite_users=False, can_restrict_members=False,
                    can_pin_messages=False
                )
                bot.reply_to(message, f"🔻 تم تنزيل <b>{target.first_name}</b> من رتبة الإشراف.")
            except Exception:
                bot.reply_to(message, "⚠️ تعذر سحب الإشراف.")

# ================= ترحيب تلقائي فخم للأعضاء =================
@bot.message_handler(content_types=['new_chat_members'])
def welcome_user(message):
    for member in message.new_chat_members:
        welcome_text = (
            f"👑 <b>أهلاً وسهلاً بك يا {member.first_name} في مجموعتنا المباركة</b> 👑\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🌸 نتمنى لك قضاء وقت مفيد ونافع معنا.\n"
            f"🌿 صلِّ على الحبيب المصطفى ﷺ."
        )
        bot.send_message(message.chat.id, welcome_text)

# ================= جدولة النشر التلقائي =================
def run_scheduler():
    # نشر الورد اليومي صباحاً
    schedule.every().day.at("06:00").do(daily_post)
    while True:
        schedule.run_pending()
        time.sleep(30)

threading.Thread(target=run_scheduler, daemon=True).start()

print("✅ البوت الإسلامي الملكي المتكامل يعمل الآن بكل ميزاته...")
bot.infinity_polling()
