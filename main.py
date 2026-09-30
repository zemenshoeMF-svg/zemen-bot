BOT_TOKEN = os.environ["BOT_TOKEN"]

# ==================== LOCAL ASSETS ====================
# Put images in the repo at assets/<name>.jpg (or .jpeg / .png).
# Missing files are fine: the bot automatically falls back to text.
BASE_DIR = Path(__file__).resolve().parent
ASSET_DIR = BASE_DIR / "assets"
ASSET_NAMES = ("welcome", "catalog", "rubber", "custom", "services", "location", "qr")


def find_asset(name: str):
    for ext in (".jpg", ".jpeg", ".png"):
        path = ASSET_DIR / f"{name}{ext}"
        if path.is_file():
            return path
    return None


ASSETS = {name: find_asset(name) for name in ASSET_NAMES}
logger.info("Assets found: %s", [n for n, p in ASSETS.items() if p] or "none (text-only mode)")


async def send_photo_or_text(message, asset_name, caption, reply_markup=None):
    """Send a local photo with caption; on ANY problem send the same text + buttons."""
    path = find_asset(asset_name)
    if path and len(caption) <= 1024:  # Telegram caption limit
        try:
            with open(path, "rb") as f:
                return await message.reply_photo(
                    photo=f,
                    caption=caption,
                    parse_mode="HTML",
                    reply_markup=reply_markup,
                )
        except Exception:
            logger.exception("Failed to send photo '%s', falling back to text", asset_name)
    return await message.reply_text(
        caption,
        parse_mode="HTML",
        reply_markup=reply_markup,
    )


async def ack(update: Update):
    if update.callback_query:
        await update.callback_query.answer()


# --- USER SESSIONS (temporary memory) ---
user_languages = {}  # {user_id: 'am' or 'en'}
user_states = {}

MAPS_URL = "https://maps.app.goo.gl/y1VoGfmMfwen1vLa8"
WHATSAPP_URL = "https://wa.me/251911719676"
BACK_MAIN = [InlineKeyboardButton("◀️ Main Menu / ዋና ገጽ", callback_data="main_menu")]


# ==================== /start ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ack(update)
    message = update.effective_message
    if update.effective_user:
        user_languages.setdefault(update.effective_user.id, "am")

    keyboard = [
        [
            InlineKeyboardButton("🇪🇹 አማርኛ (Amharic)", callback_data="lang_am"),
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
        ],
        [InlineKeyboardButton("👟 የራበር ሶል ካታሎግ | Catalog", callback_data="menu_catalog")],
        [InlineKeyboardButton("📝 እንደ ደንበኛ ይመዝገቡ | Register Client", callback_data="register_client")],
        [InlineKeyboardButton("📦 ትዕዛዝ ይስጡ | Place Bulk Order", callback_data="place_order")],
        [InlineKeyboardButton("🛡️ የውል ምስጢራዊነት (NDA) | Confidentiality", callback_data="menu_services")],
        [InlineKeyboardButton("📍 የፋብሪካ አድራሻ | Location & QR", callback_data="menu_location")],
        [InlineKeyboardButton("📢 የቴሌግራም ቻናል ይቀላቀሉ | Join Channel", callback_data="join_channel")],
        [InlineKeyboardButton("📞 የሽያጭ ክፍል | Contact B2B", callback_data="menu_contact")],
    ]
    caption = (
        "🇪🇹 <b>እንኳን ወደ ዘመን ጫማ ማኑፋክቸሪንግ ኃ.የተ.የግ.ማ በደህና መጡ!</b>\n"
        "<i>\"ጽኑ ሶል፣ ትልቅ እርምጃ!\"</i>\n\n"
        "የወንዶች የጫማ ሶል አምራች | በቻይናውያን ባለሙያዎች የሚመራ | ለጫማ ፋብሪካዎች ብጁ የራበር ሶል እና የራበር ሞልድ ሥራ | አዲስ አበባ\n\n"
        "-------------------------------\n"
        "🇬🇧 <b>Welcome to Zemen Shoe Manufacturing PLC</b>\n"
        "<b>STRONGER SOLES. GREATER STEPS.</b>\n"
        "<i>B2B Men's Shoe Soles Manufacturer | Chinese Expert-Led | "
        "Custom Rubber &amp; Rubber Molds | Addis Ababa</i>\n\n"
        "👇 <i>ቋንቋ ይምረጡ ወይም ከታች ያሉትን አማራጮች ይጠቀሙ / Select an option below:</i>"
    )
    await send_photo_or_text(message, "welcome", caption, InlineKeyboardMarkup(keyboard))


# ==================== LANGUAGE TOGGLE ====================
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if query.data == "lang_am":
        user_languages[user_id] = "am"
        note = "✅ ቋንቋ ወደ አማርኛ ተቀይሯል። ከታች ካሉት አማራጮች ይምረጡ:"
    else:
        user_languages[user_id] = "en"
        note = "✅ Language switched to English. Choose an option below:"
    await query.message.reply_text(note)
    await start(update, context)


# ==================== CATALOG & PRODUCTS ====================
async def catalog_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ack(update)
    text = (
        "👟 <b>Zemen B2B Rubber Sole Catalog / የራበር ሶል ካታሎግ</b>\n\n"
        "1️⃣ <b>High-Volume Vulcanized Rubber Soles</b>\n"
        "• ለኢንዱስትሪ ደህንነት እና ለቀን ጫማዎች የሚሆን የራበር ሶል።\n\n"
        "2️⃣ <b>Custom Rubber Soles &amp; Custom Rubber Molds</b>\n"
        "• በራሳችሁ ብራንድ፣ ሎጎ እና ስታይል የሚሰራ ብጁ ሶል እና ሞልድ፤ በጥብቅ ምስጢራዊነት (NDA)።\n\n"
        "👇 <i>ምርቶቹን ለመመልከት ይጫኑ / Select below:</i>"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👞 Standard Rubber Soles", callback_data="prod_rubber")],
        [InlineKeyboardButton("🛠️ Custom Rubber Molds", callback_data="prod_custom")],
        BACK_MAIN,
    ])
    await send_photo_or_text(update.effective_message, "catalog", text, keyboard)


async def prod_rubber(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ack(update)
    text = (
        "👞 <b>High-Volume Vulcanized Rubber Outsoles</b>\n\n"
        "• <b>Material:</b> Vulcanized rubber compounds for shoe factories.\n"
        "• <b>Performance:</b> Abrasion resistance &amp; flex endurance.\n"
        "• <b>Safety:</b> Oil-resistant, anti-slip tread profiles available.\n\n"
        "🇪🇹 ለጫማ ፋብሪካዎች የምርት መስመር በብዛት የሚቀርብ አስተማማኝ የራበር ሶል።"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 Place Order / ትዕዛዝ ስጡ", callback_data="place_order")],
        [InlineKeyboardButton("◀️ Back / ተመለስ", callback_data="menu_catalog")],
    ])
    await send_photo_or_text(update.effective_message, "rubber", text, keyboard)


async def prod_custom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ack(update)
    text = (
        "🛠️ <b>Custom Rubber Soles &amp; Custom Rubber Molds</b>\n\n"
        "• <b>Own-brand / own-style production:</b> your factory logo, design and size runs.\n"
        "• <b>Custom molds:</b> made to your specifications for factory customers.\n\n"
        "<b>STRICT NDA &amp; CONFIDENTIALITY</b>\n"
        "Customer designs, molds, specifications, and product information are handled "
        "confidentially and are not disclosed to unauthorized third parties.\n\n"
        "🇪🇹 የእርስዎን ልዩ ንድፍ በቻይናውያን ባለሙያዎች መሪነት እናመርታለን።"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 Request Custom Mold / የሞልድ ትዕዛዝ", callback_data="place_order")],
        [InlineKeyboardButton("◀️ Back / ተመለስ", callback_data="menu_catalog")],
    ])
    await send_photo_or_text(update.effective_message, "custom", text, keyboard)


# ==================== CLIENT REGISTRATION ====================
async def register_client(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ack(update)
    user_states[update.effective_user.id] = "waiting_for_contact"
    contact_button = KeyboardButton(text="📱 ስልክ ቁጥሬን አጋራ / Share Contact", request_contact=True)
    reply_markup = ReplyKeyboardMarkup([[contact_button]], resize_keyboard=True, one_time_keyboard=True)
    await update.effective_message.reply_text(
        "📝 <b>እንደ ፋብሪካ/ደንበኛ ለመመዝገብ</b>\n\n"
        "እባክዎ ከታች ያለውን <b>'ስልክ ቁጥሬን አጋራ'</b> የሚለውን ቁልፍ በመጫን ስልክዎን ያጋሩ።\n\n"
        "<i>Please tap the button below to share your phone number and complete B2B client registration.</i>",
        parse_mode="HTML",
        reply_markup=reply_markup,
    )


async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user_states.get(user.id) == "waiting_for_contact":
        phone_number = update.message.contact.phone_number
        user_states[user.id] = "registered"
        await update.message.reply_text(
            "✅ <b>ምዝገባዎ ተጠናቋል! (Registration Successful)</b>\n\n"
            f"ስም: {user.full_name}\n"
            f"ስልክ: {phone_number}\n\n"
            "አሁን የራበር ሶል ትዕዛዝ መስጠት ወይም ከሽያጭ ክፍላችን ጋር መነጋገር ይችላሉ።",
            parse_mode="HTML",
            reply_markup=ReplyKeyboardRemove(),
        )


# ==================== ORDER INTAKE ====================
async def place_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ack(update)
    text = (
        "📦 <b>B2B Bulk Order &amp; Custom Inquiry / የትዕዛዝ ማመልከቻ</b>\n\n"
        "ትዕዛዝዎን ለመጀመር እባክዎ በስልክ ቁጥሮቻችን ያነጋግሩን ወይም በዋትስአፕ ይጻፉልን፡\n\n"
        "📞 <b>ስልክ:</b> +251 911 719 676 / +251 911 245 457\n"
        f"💬 <b>WhatsApp:</b> {WHATSAPP_URL}\n"
        "📧 <b>Email:</b> zemenshoemanufacturing@gmail.com"
    )
    # NOTE: Telegram rejects tel: links in inline buttons, so phones are shown as text.
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 Chat on WhatsApp", url=WHATSAPP_URL)],
        BACK_MAIN,
    ])
    await update.effective_message.reply_text(text, parse_mode="HTML", reply_markup=keyboard)


# ==================== CONFIDENTIALITY & SERVICES ====================
async def services_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ack(update)
    text = (
        "🛡️ <b>STRICT NDA &amp; CONFIDENTIALITY</b>\n\n"
        "Customer designs, molds, specifications, and product information are handled "
        "confidentially and are not disclosed to unauthorized third parties.\n\n"
        "• <b>Chinese Expert-Led:</b> production guided by experienced rubber technology experts.\n"
        "• <b>Own-brand / own-style production</b> for factory customers.\n\n"
        "🇪🇹 የእርስዎ ንድፍ፣ ሞልድ እና የምርት መረጃ በምስጢር ይያዛል፤ ያለ ፈቃድ ለሶስተኛ ወገን አይሰጥም።"
    )
    keyboard = InlineKeyboardMarkup([BACK_MAIN])
    await send_photo_or_text(update.effective_message, "services", text, keyboard)


# ==================== LOCATION & QR ====================
async def location_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ack(update)
    message = update.effective_message
    text = (
        "📍 <b>Factory Location &amp; Google Maps</b>\n\n"
        "<b>Zemen Shoe Manufacturing PLC</b>\n"
        "Addis Ababa, Ethiopia (Beyond Shewa Market / Abebeche Building Area)\n\n"
        "🗺️ <i>Tap the button below for direct map navigation.</i>"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🗺️ Open Google Maps", url=MAPS_URL)],
        [InlineKeyboardButton("⭐ Google Review", url="https://search.google.com/local/writereview?placeid=ChIJ4XGOQieFSxYR5d0RqiYShLI")],
        BACK_MAIN,
    ])
    # QR image is optional: only sent if the file exists.
    if find_asset("qr"):
        await send_photo_or_text(message, "qr", "📷 <b>Zemen Official Location QR Code</b>")
    await send_photo_or_text(message, "location", text, keyboard)


# ==================== CHANNEL & CONTACT ====================
async def join_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ack(update)
    text = "📢 <b>የዘመን ጫማ ማኑፋክቸሪንግ ኦፊሴላዊ ቻናል ይቀላቀሉ!</b>\n\nዕለታዊ የምርት ዝመናዎችን እና አዳዲስ የሶል ዲዛይኖችን ይከታተሉ።"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Join Telegram Channel", url="https://t.me/ZemenShoes_Bot")],
        BACK_MAIN,
    ])
    await update.effective_message.reply_text(text, parse_mode="HTML", reply_markup=keyboard)


async def contact_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ack(update)
    text = (
        "📞 <b>Contact Zemen B2B Sales &amp; Engineering</b>\n\n"
        "• <b>Phones:</b> +251 911 719 676 / +251 911 245 457\n"
        f"• <b>WhatsApp:</b> {WHATSAPP_URL}\n"
        "• <b>Email:</b> zemenshoemanufacturing@gmail.com\n"
        "• <b>Location:</b> Addis Ababa (Beyond Shewa Market)"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 WhatsApp", url=WHATSAPP_URL)],
        [InlineKeyboardButton("🗺️ Google Maps", url=MAPS_URL)],
        BACK_MAIN,
    ])
    await update.effective_message.reply_text(text, parse_mode="HTML", reply_markup=keyboard)


# ==================== GLOBAL ERROR HANDLER ====================
async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Unhandled Telegram error", exc_info=context.error)


# ==================== MAIN ====================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("catalog", catalog_menu))
    app.add_handler(CommandHandler("rubber", prod_rubber))
    app.add_handler(CommandHandler("custom", prod_custom))
    app.add_handler(CommandHandler("services", services_menu))
    app.add_handler(CommandHandler("location", location_menu))
    app.add_handler(CommandHandler("contact", contact_menu))

    # Inline keyboard callbac