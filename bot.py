import os
import time
import random
import threading
import requests
import telebot
from telebot import types
import schedule
from datetime import datetime, timedelta
from flask import Flask

# ================= خادم ويب خفيف لإرضاء منصة الاستضافة =================
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running 24/7 Live!"

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# ================= الإعدادات الأساسية =================
BOT_TOKEN = "8755170973:AAFGhhDJt_rjufga7QCIF7pOA4KofQfsuKk"
ADMIN_ID = 0  # ضع هنا الآيدي الرقمي لحسابك (اختياري)
WHATSAPP_NUMBER = "249118626501"
DEFAULT_CHANNEL = "@YourChannelUsername"  # معرف قناتك (مثال: @my_channel)
STATE_FILE = "quran_page.txt"

# ⏰ توقيت النشر التلقائي اليومي في القناة
POST_TIME = "06:30"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
USER_TASBEEH = {}

GROUP_PROTECTION = {
    "lock_links": True,
    "lock_forward": True
}

# ================= بنك القراء والمصاحف (أكثر من 20 قارئاً) =================
QURAN_RECITERS = {
    # قراء وشيوخ السودان
    "🇸🇩 القارئ نورين محمد صديق": "https://server10.mp3quran.net/nourin/",
    "🇸🇩 القارئ الزين محمد أحمد": "https://server9.mp3quran.net/alzain/",
    "🇸🇩 القارئ الفاتح محمد زبير (الدوري)": "https://server10.mp3quran.net/fateh/",
    "🇸🇩 القارئ محمد عثمان حاج علي": "https://www.tvquran.com/ar/scholar/213/profile/%D9%85%D8%AD%D9%85%D8%AF-%D8%B9%D8%AB%D9%85%D8%A7%D9%86-%D8%AD%D8%A7%D8%AC-%D8%B9%D9%84%D9%8A",
    "🇸🇩 القارئ جعفر محمود الفاتح": "https://www.tvquran.com/ar/scholar/214/profile/%D8%AC%D8%B9%D9%81%D8%B1-%D9%85%D8%AD%D9%85%D9%88%D8%AF",
    "🇸🇩 القارئ مصطفى عثمان الهاشمي": "https://surahquran.com/mp3/sudani.html",
    "🇸🇩 الشيخ د. محمد سيد حاج (المكتبة والدروس)": "https://ar.islamway.net/scholar/1107",
    "🇸🇩 الشيخ محمد المجتبى (مواعظ وخواطر)": "https://youtube.com/results?search_query=الشيخ+محمد+المجتبى",

    # كبار قراء العالم الإسلامي
    "📖 الشيخ محمود خليل الحصري": "https://server13.mp3quran.net/hussary/",
    "📖 الشيخ محمد صديق المنشاوي": "https://server10.mp3quran.net/minsh/",
    "📖 الشيخ عبد الباسط عبد الصمد": "https://server7.mp3quran.net/basit/",
    "📖 الشيخ مشاري بن راشد العفاسي": "https://server8.mp3quran.net/afs/",
    "📖 الشيخ أحمد بن علي العجمي": "https://server10.mp3quran.net/ajm/",
    "📖 الشيخ سعد بن سعيد الغامدي": "https://server7.mp3quran.net/s_gmd/",
    "📖 الشيخ ماهر بن حمد المعيقلي": "https://server12.mp3quran.net/maher/",
    "📖 الشيخ عبد الرحمن السديس": "https://server11.mp3quran.net/sds/",
    "📖 الشيخ سعود بن إبراهيم الشريم": "https://server7.mp3quran.net/shur/",
    "📖 الشيخ ياسر بن راشد الدوسري": "https://server11.mp3quran.net/yasser/",
    "📖 الشيخ ناصر بن علي القطامي": "https://server6.mp3quran.net/qtm/",
    "📖 الشيخ علي بن عبد الرحمن الحذيفي": "https://server9.mp3quran.net/hthfi/",
    "📖 الشيخ فارس عباد": "https://server8.mp3quran.net/frs_a/",
    "📖 الشيخ إدريس بن محمد أبكر": "https://server6.mp3quran.net/abkr/",
    "🎙️ الشيخ محمود الحسنات (الخطب والدروس)": "https://ar.islamway.net/scholar/4462"
}

# ================= مكتبة الكتب الإسلامية والروايات =================
ISLAMIC_BOOKS = {
    # مؤلفات أدهم شرقاوي
    "📗 أدهم شرقاوي: رسائل من القرآن": "https://www.noor-book.com/كتاب-رسائل-من-القرآن-pdf",
    "📗 أدهم شرقاوي: ليطمئن قلبي": "https://www.noor-book.com/كتاب-ليطمئن-قلبي-pdf",
    "📗 أدهم شرقاوي: إلى المنكسرة قلوبهم": "https://www.noor-book.com/كتاب-الي-المنكسره-قلوبهم-pdf",
    "📗 أدهم شرقاوي: السلام عليك يا صاحبي": "https://www.noor-book.com/كتاب-السلام-عليك-يا-صاحبي-pdf",
    "📗 أدهم شرقاوي: حديث الصباح": "https://www.noor-book.com/كتاب-حديث-الصباح-pdf",

    # مؤلفات د. حنان لاشين
    "📙 د. حنان لاشين: إيكادولي": "https://www.noor-book.com/كتاب-إيكادولي-pdf",
    "📙 د. حنان لاشين: أوبال": "https://www.noor-book.com/كتاب-أوبال-pdf",
    "📙 د. حنان لاشين: أمانوس": "https://www.noor-book.com/كتاب-أمانوس-pdf",
    "📙 د. حنان لاشين: كويكول": "https://www.noor-book.com/كتاب-كويكول-pdf",
    "📙 د. حنان لاشين: سقطت بين يدي مجالد": "https://www.noor-book.com/كتاب-سقطت-بين-يدي-مجالد-pdf",

    # كتب التراث والسنة النبوية
    "📘 صحيح البخاري كاملاً": "https://waqfeya.net/book.php?bid=701",
    "📘 حصن المسلم من أذكار السنة": "https://www.alukah.net/books/files/book_1113/bookfile/hisn_almuslim.pdf",
    "📘 الأربعين النووية مع الشرح": "https://www.alukah.net/books/files/book_1549/bookfile/arbaeen_nawawiya.pdf",
    "📘 رياض الصالحين للإمام النووي": "https://www.alukah.net/books/files/book_4102/bookfile/riyad_al-saliheen.pdf"
}

DAILY_DUAS = [
    "اللهم إنا نسألك من الخير كله عاجله وآجله، ما علمنا منه وما لم نعلم.",
    "اللهم اجعل القرآن العظيم ربيع قلوبنا، ونور صدورنا، وجلاء أحزاننا، وذهاب همومنا.",
    "اللهم إنا نعوذ بك من زوال نعمتك، وتحول عافيتك، وفجاءة نقمتك، وجميع سخطك.",
    "يا حي يا قيوم برحمتك نستغيث، أصلح لنا شأننا كله ولا تكلنا إلى أنفسنا طرفة عين.",
    "اللهم احفظ بلادنا وسائر بلاد المسلمين، واجعلها دار أمن وإيمان وسلام وسخاء ورخاء."
]

HADITHS = [
    "قال رسول الله ﷺ: «خَيْرُكُمْ مَنْ تَعَلَّمَ القُرْآنَ وَعَلَّمَهُ». [رواه البخاري]",
    "قال رسول الله ﷺ: «مَنْ سَلَكَ طَرِيقًا يَلْتَمِسُ فِيهِ عِلْمًا، سَهَّلَ اللهُ لَهُ بِهِ طَرِيقًا إِلَى الْجَنَّةِ». [رواه مسلم]",
    "قال رسول الله ﷺ: «كَلِمَتَانِ خَفِيفَتَانِ عَلَى اللِّسَانِ، ثَقِيلَتَانِ فِي المِيزَانِ: سُبْحَانَ اللَّهِ وَبِحَمْدِهِ، سُبْحَانَ اللَّهِ العَظِيمِ». [متفق عليه]",
    "قال رسول الله ﷺ: «إِنَّمَا الأَعْمَالُ بِالنِّيَّاتِ، وَإِنَّمَا لِكُلِّ امْرِئٍ مَا نَوَى». [متفق عليه]",
    "قال رسول الله ﷺ: «مَنْ صَلَّى عَلَيَّ صَلَاةً صَلَّى اللَّهُ عَلَيْهِ بِهَا عَشْرًا». [رواه مسلم]"
]

ISLAMIC_QUIZZES = [
    {"q": "⭐ ما هي أعظم آية في كتاب الله تعالى؟", "options": ["آية الدين", "آية الكرسي", "آخر آية في البقرة", "أول آية في الكهف"], "ans": 1},
    {"q": "⭐ من هو الصحابي الملقب بـ أمين هذه الأمة؟", "options": ["أبو عبيدة بن الجراح", "خالد بن الوليد", "عمر بن الخطاب", "علي بن أبي طالب"], "ans": 0},
    {"q": "⭐ ما هي السورة المنجية من عذاب القبر؟", "options": ["سورة يس", "سورة الواقعة", "سورة الملك", "سورة الدخان"], "ans": 2},
    {"q": "⭐ كم عدد أجزاء القرآن الكريم؟", "options": ["30 جزءاً", "60 جزءاً", "25 جزءاً", "40 جزءاً"], "ans": 0}
]

# ================= أدوات إدارة المصحف والنشر =================
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

def send_daily_post():
    page = get_current_page()
    page_str = str(page).zfill(3)
    image_url = f"https://everyayah.com/data/quranpngs/{page_str}.png"
    hadith = random.choice(HADITHS)
    ayah = fetch_random_ayah()
    dua = random.choice(DAILY_DUAS)

    caption = (
        f"👑 <b>ورد اليوم المبارك | الصفحة ({page}) من المصحف</b> 👑\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"{ayah}\n\n"
        f"💎 <b>حديث شريف:</b>\n{hadith}\n\n"
        f"🤲 <b>دعاء اليوم:</b>\n{dua}\n\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🌸 <i>تقبل الله منا ومنكم صالح الأعمال.</i>"
    )
    try:
        bot.send_photo(chat_id=DEFAULT_CHANNEL, photo=image_url, caption=caption)
        print(f"[{datetime.now()}] تم نشر الورد اليومي بنجاح.")
        next_page = page + 1 if page < 604 else 1
        save_current_page(next_page)
    except Exception as e:
        print(f"Daily post error: {e}")

# ================= القائمة التفاعلية =================
def build_main_menu():
    markup = types.InlineKeyboardMarkup(row_width=3)
    b_quran = types.InlineKeyboardButton("📖 المصحف كاملاً", callback_data="sec_quran")
    b_reciters = types.InlineKeyboardButton("🎙️ قراء السودان والعالم", callback_data="sec_reciters")
    b_quiz = types.InlineKeyboardButton("🧐 اختبر حفظك", callback_data="sec_quiz")
    
    b_tasbeeh = types.InlineKeyboardButton("📿 سُبحة ذكية", callback_data="sec_tasbeeh")
    b_adhkar = types.InlineKeyboardButton("🌙 الأذكار اليومية", callback_data="sec_adhkar")
    b_books = types.InlineKeyboardButton("📚 المكتبة الشاملة", callback_data="sec_books")
    
    b_ruqyah = types.InlineKeyboardButton("🛡️ الرقية الشرعية", callback_data="sec_ruqyah")
    b_hadith = types.InlineKeyboardButton("📜 آية وحديث فوري", callback_data="sec_instant")
    b_admin = types.InlineKeyboardButton("⚙️ لوحة النشر", callback_data="sec_admin")
    
    b_whatsapp = types.InlineKeyboardButton(
        "💬 تواصل مع المطور (WhatsApp)",
        url=f"https://wa.me/{WHATSAPP_NUMBER}?text=%D8%A7%D9%84%D8%B3%D9%84%D8%A7%D9%85%20%D8%B9%D9%84%D9%8A%D9%83%D9%85%D8%8C%20%D8%A3%D8%B1%D8%BA%D8%A8%20%D9%81%D9%8A%20%D8%AA%D9%81%D8%B9%D9%8A%D9%84%20%D8%A7%D9%84%D8%A8%D9%88%D8%AA"
    )

    markup.add(b_quran, b_reciters, b_quiz)
    markup.add(b_tasbeeh, b_adhkar, b_books)
    markup.add(b_ruqyah, b_hadith, b_admin)
    markup.add(b_whatsapp)
    return markup

@bot.message_handler(commands=['start'])
def start_cmd(message):
    if message.chat.type == 'private':
        text = (
            f"👑 <b>مرحباً بك يا {message.from_user.first_name} في البوت الإسلامي الملكي</b> 👑\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"اختر الخدمة المطلوبة من القائمة أدناه:"
        )
        bot.send_message(message.chat.id, text, reply_markup=build_main_menu())
    else:
        bot.reply_to(message, "🌟 البوت مفعل بالمجموعة! اكتب <b>الاوامر</b> لعرض أدوات الإشراف.")

@bot.callback_query_handler(func=lambda call: True)
def on_menu_click(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    data = call.data

    if data == "sec_quran":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("🌐 المصحف الإلكتروني كاملاً", url="https://quran.ksu.edu.sa"),
            types.InlineKeyboardButton("📖 قراءة المصحف بجودة فائقة PDF", url="https://archive.org/details/Quran-Madina-High-Quality"),
            types.InlineKeyboardButton("🔙 رجوع", callback_data="sec_back")
        )
        bot.send_message(chat_id, "📖 <b>المصحف الشريف كاملاً:</b>\nتصفح القرآن أو اكتب في الشات <code>صفحة 20</code> لعرضها مباشرة.", reply_markup=markup)

    elif data == "sec_reciters":
        markup = types.InlineKeyboardMarkup(row_width=1)
        for r_name, r_url in QURAN_RECITERS.items():
            markup.add(types.InlineKeyboardButton(r_name, url=r_url))
        markup.add(types.InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="sec_back"))
        bot.send_message(chat_id, "🎙️ <b>مكتبة القراء والمصاحف:</b>", reply_markup=markup)

    elif data == "sec_books":
        markup = types.InlineKeyboardMarkup(row_width=1)
        for b_name, b_url in ISLAMIC_BOOKS.items():
            markup.add(types.InlineKeyboardButton(b_name, url=b_url))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="sec_back"))
        bot.send_message(chat_id, "📚 <b>مكتبة الكتب الإسلامية والروايات:</b>", reply_markup=markup)

    elif data == "sec_tasbeeh":
        USER_TASBEEH[user_id] = 0
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("📿 سُبحان الله وبحمده (0)", callback_data="tsb_add"),
            types.InlineKeyboardButton("🔄 تصفير العداد", callback_data="tsb_clear"),
            types.InlineKeyboardButton("🔙 رجوع", callback_data="sec_back")
        )
        bot.send_message(chat_id, "📿 <b>السُّبحة الإلكترونية:</b>", reply_markup=markup)

    elif data == "tsb_add":
        count = USER_TASBEEH.get(user_id, 0) + 1
        USER_TASBEEH[user_id] = count
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton(f"📿 سُبحان الله وبحمده ({count})", callback_data="tsb_add"),
            types.InlineKeyboardButton("🔄 تصفير العداد", callback_data="tsb_clear"),
            types.InlineKeyboardButton("🔙 رجوع", callback_data="sec_back")
        )
        try:
            bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=markup)
        except Exception:
            pass

    elif data == "tsb_clear":
        USER_TASBEEH[user_id] = 0
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("📿 سُبحان الله وبحمده (0)", callback_data="tsb_add"),
            types.InlineKeyboardButton("🔄 تصفير العداد", callback_data="tsb_clear"),
            types.InlineKeyboardButton("🔙 رجوع", callback_data="sec_back")
        )
        bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id, "تم تصفير العداد بنجاح.")

    elif data == "sec_adhkar":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("🌅 أذكار الصباح", callback_data="adk_morn"),
            types.InlineKeyboardButton("🌃 أذكار المساء", callback_data="adk_eve"),
            types.InlineKeyboardButton("🛌 أذكار النوم", callback_data="adk_slp"),
            types.InlineKeyboardButton("🔙 رجوع", callback_data="sec_back")
        )
        bot.send_message(chat_id, "🌙 <b>الأذكار اليومية:</b>", reply_markup=markup)

    elif data == "adk_morn":
        bot.send_message(chat_id, "🌅 <b>أذكار الصباح:</b>\n\n• «أَصْبَحْنَا وَأَصْبَحَ المُلْكُ لِلَّهِ، وَالحَمْدُ لِلَّهِ لاَ إِلَهَ إِلاَّ اللَّهُ وَحْدَهُ لاَ شَرِيكَ لَهُ».\n• «اللّهُـمَّ بِكَ أَصْـبَحْنا وَبِكَ أَمْسَـينا، وَبِكَ نَحْـيا وَبِكَ نَمُـوتُ وَإِلَـيْكَ النُّـشُور».")

    elif data == "adk_eve":
        bot.send_message(chat_id, "🌃 <b>أذكار المساء:</b>\n\n• «أَمْسَيْنَا وَأَمْسَى المُلْكُ لِلَّهِ، وَالحَمْدُ لِلَّهِ لاَ إِلَهَ إِلاَّ اللَّهُ».\n• «أَعُوذُ بِكَلِمَاتِ اللَّهِ التَّامَّاتِ مِنْ شَرِّ مَا خَلَقَ» (3 مرات).")

    elif data == "adk_slp":
        bot.send_message(chat_id, "🛌 <b>أذكار النوم:</b>\n\n• «بِاسْمِكَ رَبِّي وَضَعْتُ جَنْبِي وَبِكَ أَرْفَعُهُ».\n• قراءة آية الكرسي والمعوذتين.")

    elif data == "sec_ruqyah":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("🎧 الرقية الشرعية MP3", url="https://server11.mp3quran.net/download/hajj/001.mp3"),
            types.InlineKeyboardButton("📖 الرقية مكتوبة", url="https://kalemtayeb.com/safahat/item/3173"),
            types.InlineKeyboardButton("🔙 رجوع", callback_data="sec_back")
        )
        bot.send_message(chat_id, "🛡️ <b>الرقية الشرعية الشاملة:</b>", reply_markup=markup)

    elif data == "sec_quiz":
        q = random.choice(ISLAMIC_QUIZZES)
        bot.send_poll(chat_id, q["q"], q["options"], type='quiz', correct_option_id=q["ans"], is_anonymous=False)

    elif data == "sec_instant":
        bot.send_message(chat_id, f"{fetch_random_ayah()}\n\n💎 <b>حديث:</b>\n{random.choice(HADITHS)}\n\n🤲 <b>دعاء:</b>\n{random.choice(DAILY_DUAS)}")

    elif data == "sec_admin":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("🚀 إرسال ورد اليوم بالقناة الآن", callback_data="adm_publish_now"),
            types.InlineKeyboardButton("🔙 رجوع", callback_data="sec_back")
        )
        bot.send_message(chat_id, f"⚙️ <b>لوحة النشر:</b> موعد النشر التلقائي اليومي: <b>{POST_TIME}</b>", reply_markup=markup)

    elif data == "adm_publish_now":
        send_daily_post()
        bot.answer_callback_query(call.id, "✅ تم إرسال الورد للقناة بنجاح.")

    elif data == "sec_back":
        bot.send_message(chat_id, "👑 القائمة الرئيسية:", reply_markup=build_main_menu())

def is_admin(chat_id, user_id):
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ['creator', 'administrator']
    except Exception:
        return False

@bot.message_handler(func=lambda msg: True, content_types=['text', 'photo', 'video', 'document'])
def handle_messages_and_moderation(message):
    chat_id = message.chat.id
    text = message.text.strip() if message.text else ""

    if message.chat.type in ['group', 'supergroup']:
        if not is_admin(chat_id, message.from_user.id):
            if GROUP_PROTECTION["lock_links"] and ("http://" in text or "https://" in text or "t.me/" in text):
                try:
                    bot.delete_message(chat_id, message.message_id)
                    w = bot.send_message(chat_id, f"⚠️ الروابط ممنوعة بالمجموعة يا {message.from_user.first_name}.")
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

    if text in ["اوامر", "الاوامر", "مساعدة"]:
        help_text = (
            "👑 <b>أوامر البوت:</b>\n"
            "🔹 <b>اية</b> | <b>حديث</b> | <b>دعاء</b>\n"
            "🔹 <b>صفحة [رقم]</b> (مثال: <code>صفحة 20</code>)\n"
            "🔹 <b>سؤال</b> : اختبار ديني\n"
            "🔹 <b>المطور</b> : للتواصل عبر واتساب\n\n"
            "🛡 <b>أوامر الإشراف بالرد داخل المجموعة:</b>\n"
            "🔸 حظر | الغاء الحظر | كتم | رفع ادمن | تنزيل ادمن"
        )
        bot.reply_to(message, help_text)
        return

    if text == "اية":
        bot.reply_to(message, fetch_random_ayah())
        return

    if text == "حديث":
        bot.reply_to(message, f"💎 {random.choice(HADITHS)}")
        return

    if text == "دعاء":
        bot.reply_to(message, f"🤲 {random.choice(DAILY_DUAS)}")
        return

    if text == "سؤال":
        q = random.choice(ISLAMIC_QUIZZES)
        bot.send_poll(chat_id, q["q"], q["options"], type='quiz', correct_option_id=q["ans"])
        return

    if text == "المطور":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("💬 مراسلة المطور عبر WhatsApp", url=f"https://wa.me/{WHATSAPP_NUMBER}"))
        bot.reply_to(message, "👑 تواصل مباشرة مع المطور:", reply_markup=markup)
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

    admin_actions = ["حظر", "الغاء الحظر", "كتم", "اسكات", "رفع ادمن", "ترقية", "تنزيل ادمن"]
    if text in admin_actions and message.chat.type in ['group', 'supergroup']:
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
                bot.reply_to(message, f"🚫 تم حظر <b>{target.first_name}</b> بنجاح.")
            except Exception:
                bot.reply_to(message, "⚠️ تعذر الحظر.")

        elif text == "الغاء الحظر":
            try:
                bot.unban_chat_member(chat_id, target.id, only_if_banned=True)
                bot.reply_to(message, f"✅ تم فك الحظر عن <b>{target.first_name}</b>.")
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
                bot.promote_chat_member(chat_id, target.id, can_change_info=True, can_delete_messages=True, can_invite_users=True, can_pin_messages=True)
                bot.reply_to(message, f"⭐ تمت ترقية <b>{target.first_name}</b> إلى مشرف.")
            except Exception:
                bot.reply_to(message, "⚠️ تعذر الترقية.")

        elif text == "تنزيل ادمن":
            try:
                bot.promote_chat_member(chat_id, target.id, can_change_info=False, can_delete_messages=False, can_invite_users=False, can_pin_messages=False)
                bot.reply_to(message, f"🔻 تم سحب الإشراف من <b>{target.first_name}</b>.")
            except Exception:
                bot.reply_to(message, "⚠️ تعذر سحب الإشراف.")

@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_user(message):
    for member in message.new_chat_members:
        welcome_txt = f"👑 مرحباً بك يا <b>{member.first_name}</b> في مجموعتنا المباركة 🌸"
        bot.send_message(message.chat.id, welcome_txt)

def run_scheduler():
    schedule.every().day.at(POST_TIME).do(send_daily_post)
    while True:
        schedule.run_pending()
        time.sleep(30)

# ================= نقطة البداية وتشغيل الخيوط =================
if __name__ == "__main__":
    threading.Thread(target=run_web_server, daemon=True).start()
    threading.Thread(target=run_scheduler, daemon=True).start()
    print("✅ البوت الإسلامي وخادم الويب يعملان بنجاح...")
    bot.infinity_polling()
