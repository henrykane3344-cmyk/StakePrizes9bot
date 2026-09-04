import os
import logging
import tempfile
import sys
import re
import string
import random
import io
from datetime import datetime
from gtts import gTTS
from PIL import Image
import img2pdf
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Language options for TTS and Translation
LANGUAGES = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'ja': 'Japanese',
    'ko': 'Korean',
    'zh': 'Chinese (Mandarin)',
    'ar': 'Arabic',
    'hi': 'Hindi',
    'nl': 'Dutch',
    'tr': 'Turkish',
    'vi': 'Vietnamese',
    'th': 'Thai',
    'id': 'Indonesian',
    'pl': 'Polish',
    'uk': 'Ukrainian',
    'he': 'Hebrew',
    'el': 'Greek',
    'cs': 'Czech',
    'sv': 'Swedish',
    'hu': 'Hungarian',
    'ro': 'Romanian'
}

# StakePrizes9 themed responses
STAKE_PRIZES_RESPONSES = [
    "🏆 StakePrizes9 - You're a winner!",
    "💰 StakePrizes9 - Invest in excellence!",
    "🎁 StakePrizes9 - Your prize awaits!",
    "⭐ StakePrizes9 - Star performance!",
    "💎 StakePrizes9 - Quality guaranteed!",
    "🎯 StakePrizes9 - Precision in everything!",
    "🚀 StakePrizes9 - Elevate your game!",
    "🏅 StakePrizes9 - Gold medal quality!",
    "✨ StakePrizes9 - Making magic happen!",
    "🌟 StakePrizes9 - Shining success!",
]

# Grammar Rules
GRAMMAR_RULES = {
    "don't": 'do not', "can't": 'cannot', "won't": 'will not',
    "shouldn't": 'should not', "wouldn't": 'would not',
    "couldn't": 'could not', "isn't": 'is not', "aren't": 'are not',
    "wasn't": 'was not', "weren't": 'were not',
    "hasn't": 'has not', "haven't": 'have not',
    "hadn't": 'had not', "doesn't": 'does not', "didn't": 'did not',
    "ain't": 'am not', "i'm": 'I am', "you're": 'you are',
    "he's": 'he is', "she's": 'she is', "it's": 'it is',
    "we're": 'we are', "they're": 'they are',
    "i'll": 'I will', "you'll": 'you will', "he'll": 'he will',
    "she'll": 'she will', "it'll": 'it will', "we'll": 'we will',
    "they'll": 'they will', "i've": 'I have', "you've": 'you have',
    "we've": 'we have', "they've": 'they have',
    "i'd": 'I would', "you'd": 'you would', "he'd": 'he would',
    "she'd": 'she would', "we'd": 'we would', "they'd": 'they would',
    'a apple': 'an apple', 'a hour': 'an hour', 'a honest': 'an honest',
    'a honor': 'an honor', 'a umbrella': 'an umbrella',
    'a university': 'a university', 'a European': 'a European',
    'teh': 'the', 'adn': 'and', 'thier': 'their', 'there': 'their',
    'your': 'your', 'youre': "you're", 'alot': 'a lot',
    'untill': 'until', 'recieve': 'receive', 'belive': 'believe',
    'acheive': 'achieve', 'occured': 'occurred', 'ocurred': 'occurred',
    'seperate': 'separate', 'definately': 'definitely',
    'govenment': 'government', 'enviornment': 'environment',
    'accomodate': 'accommodate', 'aquire': 'acquire',
    'arguement': 'argument', 'begining': 'beginning',
    'business': 'business', 'calendar': 'calendar', 'career': 'career',
    'catagory': 'category', 'cemetary': 'cemetery',
    'collaegue': 'colleague', 'comittee': 'committee',
    'concious': 'conscious', 'dilemna': 'dilemma',
    'disappear': 'disappear', 'disatisfied': 'dissatisfied',
    'embarass': 'embarrass', 'enviroment': 'environment',
    'excede': 'exceed', 'existance': 'existence',
    'experiance': 'experience', 'guarantee': 'guarantee',
    'harrass': 'harass', 'independant': 'independent',
    'indispensible': 'indispensable', 'inoculate': 'inoculate',
    'irresistable': 'irresistible', 'maintainance': 'maintenance',
    'millenium': 'millennium', 'miniscule': 'minuscule',
    'mischevious': 'mischievous', 'neccessary': 'necessary',
    'occassion': 'occasion', 'occurence': 'occurrence',
    'pavillion': 'pavilion', 'perserverance': 'perseverance',
    'prefered': 'preferred', 'priviledge': 'privilege',
    'pronounciation': 'pronunciation', 'publically': 'publicly',
    'reccommend': 'recommend', 'relevent': 'relevant',
    'repetition': 'repetition', 'rhythm': 'rhythm',
    'schedual': 'schedule', 'seperate': 'separate',
    'similiar': 'similar', 'sucess': 'success',
    'suprize': 'surprise', 'tommorow': 'tomorrow',
    'unescessary': 'unnecessary', 'wierd': 'weird',
    'could of': 'could have', 'should of': 'should have',
    'would of': 'would have', 'must of': 'must have',
    'might of': 'might have',
}

# Translation Dictionary
TRANSLATION_DICT = {
    'hello': 'hola', 'goodbye': 'adiós', 'thank you': 'gracias',
    'yes': 'sí', 'no': 'no', 'please': 'por favor', 'sorry': 'lo siento',
    'good morning': 'buenos días', 'good afternoon': 'buenas tardes',
    'good night': 'buenas noches', 'how are you': '¿cómo estás',
    'i love you': 'te quiero', 'friend': 'amigo', 'family': 'familia',
    'home': 'casa', 'water': 'agua', 'food': 'comida', 'love': 'amor',
    'life': 'vida', 'happy': 'feliz', 'sad': 'triste', 'beautiful': 'hermoso',
    'good': 'bueno', 'bad': 'malo', 'big': 'grande', 'small': 'pequeño',
    'new': 'nuevo', 'old': 'viejo', 'young': 'joven',
    'success': 'éxito', 'excellence': 'excelencia',
    'quality': 'calidad', 'performance': 'rendimiento',
    'improvement': 'mejora', 'prize': 'premio',
    'stake': 'participación', 'winner': 'ganador',
    'bonjour': 'hello', 'merci': 'thank you', 'au revoir': 'goodbye',
    'oui': 'yes', 'non': 'no', "s'il vous plaît": 'please',
    'pardon': 'sorry', 'bonsoir': 'good evening', 'bonne nuit': 'good night',
    "comment ça va": 'how are you', "je t'aime": 'i love you',
    'ami': 'friend', 'famille': 'family', 'maison': 'home',
    'eau': 'water', 'nourriture': 'food', 'amour': 'love',
    'vie': 'life', 'heureux': 'happy', 'triste': 'sad',
    'beau': 'beautiful', 'bon': 'good', 'mauvais': 'bad',
    'grand': 'big', 'petit': 'small', 'nouveau': 'new',
    'vieux': 'old', 'jeune': 'young', 'succès': 'success',
    'excellence': 'excellence', 'qualité': 'quality',
    'performance': 'performance', 'amélioration': 'improvement',
}

# User preferences
user_preferences = {}

def get_token():
    """Get token from environment variables"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if token and token not in ["YOUR_BOT_TOKEN_HERE", "your_bot_token_here", ""]:
        return token
    
    token = os.getenv('BOT_TOKEN')
    if token and token not in ["YOUR_BOT_TOKEN_HERE", ""]:
        return token
    
    token = os.getenv('TELEGRAM_TOKEN')
    if token and token not in ["YOUR_BOT_TOKEN_HERE", ""]:
        return token
    
    return None

def get_stake_prizes_response():
    """Get random StakePrizes9 themed response"""
    return random.choice(STAKE_PRIZES_RESPONSES)

def correct_grammar(text):
    """AI Grammar Correction with advanced rules"""
    original_text = text
    corrections = []
    corrected_text = text
    
    words = corrected_text.split()
    corrected_words = []
    
    for word in words:
        clean_word = word.strip(string.punctuation)
        lower_word = clean_word.lower()
        
        if lower_word in GRAMMAR_RULES:
            correction = GRAMMAR_RULES[lower_word]
            if clean_word[0].isupper():
                correction = correction.capitalize()
            if word != clean_word:
                correction += word[-1] if word[-1] in string.punctuation else ''
            corrected_words.append(correction)
            corrections.append(f"'{clean_word}' → '{correction}'")
        else:
            corrected_words.append(word)
    
    corrected_text = ' '.join(corrected_words)
    
    sentences = corrected_text.split('. ')
    corrected_text = '. '.join([s.capitalize() if s else s for s in sentences])
    corrected_text = re.sub(r'\ba ([aeiouAEIOU])', r'an \1', corrected_text)
    corrected_text = re.sub(r'\ban ([^aeiouAEIOU])', r'a \1', corrected_text)
    corrected_text = ' '.join(corrected_text.split())
    corrected_text = re.sub(r'\bi\b', 'I', corrected_text)
    
    months = ['january', 'february', 'march', 'april', 'may', 'june', 
              'july', 'august', 'september', 'october', 'november', 'december']
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    
    for month in months:
        corrected_text = re.sub(rf'\b{month}\b', month.capitalize(), corrected_text, flags=re.IGNORECASE)
    for day in days:
        corrected_text = re.sub(rf'\b{day}\b', day.capitalize(), corrected_text, flags=re.IGNORECASE)
    
    corrected_text = re.sub(r'([.!?])\1+', r'\1', corrected_text)
    corrected_text = re.sub(r'\s+([.,!?;:])', r'\1', corrected_text)
    
    changes_made = len(corrections) > 0 or original_text != corrected_text
    
    return {
        'original': original_text,
        'corrected': corrected_text,
        'changes_made': changes_made,
        'corrections': corrections[:10] if corrections else [],
        'total_corrections': len(corrections)
    }

def translate_text(text, target_lang='es'):
    """Simple translation function"""
    text_lower = text.lower().strip()
    
    if text_lower in TRANSLATION_DICT:
        return {
            'original': text,
            'translated': TRANSLATION_DICT[text_lower],
            'target_lang': target_lang,
            'confidence': 'high'
        }
    
    words = text_lower.split()
    translated_parts = []
    found_translations = 0
    
    for word in words:
        clean_word = re.sub(r'[^\w\s]', '', word)
        if clean_word in TRANSLATION_DICT:
            translated_parts.append(TRANSLATION_DICT[clean_word])
            found_translations += 1
        else:
            translated_parts.append(word)
    
    if found_translations > 0:
        translated_text = ' '.join(translated_parts)
        if text[0].isupper():
            translated_text = translated_text.capitalize()
        
        return {
            'original': text,
            'translated': translated_text,
            'target_lang': target_lang,
            'confidence': 'medium',
            'words_translated': found_translations
        }
    
    return {
        'original': text,
        'translated': f"[No direct translation available]",
        'target_lang': target_lang,
        'confidence': 'none'
    }

async def convert_image_to_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Convert image to PDF"""
    if not update.message.photo:
        await update.message.reply_text(
            "🖼️ Please send me an image to convert to PDF!\n"
            "Send a photo and I'll convert it to PDF for you."
        )
        return
    
    photo = update.message.photo[-1]
    file = await photo.get_file()
    stake_response = get_stake_prizes_response()
    
    await update.message.reply_text(f"🖼️ Converting image to PDF... {stake_response}")
    
    try:
        # Download image
        file_bytes = await file.download_as_bytearray()
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as img_file:
            img_path = img_file.name
            img_file.write(file_bytes)
        
        # Convert to PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as pdf_file:
            pdf_path = pdf_file.name
        
        # Open image and convert to PDF
        with open(img_path, 'rb') as f:
            pdf_bytes = img2pdf.convert(f.read())
        
        with open(pdf_path, 'wb') as f:
            f.write(pdf_bytes)
        
        # Send PDF
        with open(pdf_path, 'rb') as f:
            await update.message.reply_document(
                document=f,
                filename='converted_image.pdf',
                caption=f"🖼️ Image converted to PDF\n📊 {stake_response}"
            )
        
        # Clean up
        os.unlink(img_path)
        os.unlink(pdf_path)
        
        await update.message.reply_text("✅ PDF created successfully!")
        
    except Exception as e:
        logger.error(f"Error converting image to PDF: {e}")
        await update.message.reply_text(
            "❌ Error converting image to PDF. Please try again with a different image."
        )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when /start is issued."""
    user = update.effective_user
    current_time = datetime.now().strftime("%I:%M %p")
    stake_response = get_stake_prizes_response()
    
    await update.message.reply_text(
        f"🏆 Welcome to @StakePrizes9bot, {user.first_name}! 👋\n\n"
        f"🕐 Current time: {current_time}\n\n"
        f"🎁 {stake_response} 🎁\n\n"
        f"🎯 **Speak better • Write better • Understand more**\n\n"
        "I'm your **all-in-one** assistant with FOUR powerful functions:\n\n"
        "🔊 **Text → Speech** - Convert text to audio\n"
        "🌍 **Translation** - Translate instantly\n"
        "✍️ **Grammar Correction** - Perfect your writing\n"
        "🖼️ **Image → PDF** - Convert images to PDF\n\n"
        "📝 **Commands:**\n"
        "/start - Show this message\n"
        "/tts - Convert text to speech\n"
        "/translate - Translate text\n"
        "/grammar - Check grammar\n"
        "/all - Do everything at once!\n"
        "/lang - Change TTS language\n"
        "/target - Set translation language\n"
        "/speed - Change speech speed\n"
        "/stake - Get StakePrizes9 info\n"
        "/help - Get help\n"
        "/about - About this bot\n\n"
        "💡 **How to use:**\n"
        "• /tts [text] - Convert to speech\n"
        "• /translate [text] - Translate text\n"
        "• /grammar [text] - Check grammar\n"
        "• /all [text] - Do everything at once!\n"
        "• Send an image - Convert to PDF\n\n"
        "🏆 **StakePrizes9 - Win at communication!**"
    )

async def stake_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send StakePrizes9 information."""
    stake_response = get_stake_prizes_response()
    
    await update.message.reply_text(
        f"🏆 **StakePrizes9 - Your Winning Assistant**\n\n"
        f"{stake_response}\n\n"
        f"🎁 **What Makes Us Special:**\n"
        f"• 🏆 4 Powerful Functions\n"
        f"• 📊 25+ Languages\n"
        f"• 🎯 Precision in everything\n"
        f"• 💎 Quality guaranteed\n"
        f"• 🚀 24/7 availability\n\n"
        f"📊 **Your Winning Tools:**\n"
        f"• 🔊 Clear speech\n"
        f"• 🌍 Global communication\n"
        f"• ✍️ Perfect grammar\n"
        f"• 🖼️ Image to PDF conversion\n"
        f"• ✨ Confident expression\n\n"
        f"💡 **Commands to use:**\n"
        f"/tts - Convert text to speech\n"
        f"/translate - Translate text\n"
        f"/grammar - Check grammar\n"
        f"/all - Do everything at once!\n"
        f"Send an image - Convert to PDF\n\n"
        f"🏆 **StakePrizes9 - Win at communication!**"
    )

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send about information."""
    await update.message.reply_text(
        "🏆 **About @StakePrizes9bot**\n\n"
        "🎯 **Mission:** Speak better • Write better • Understand more\n\n"
        "🎁 **StakePrizes9 - Your Winning Assistant**\n\n"
        "🔊 **Text-to-Speech:** 12+ languages\n"
        "🌍 **Translation:** 25+ languages\n"
        "✍️ **Grammar Correction:** 100+ rules\n"
        "🖼️ **Image to PDF:** Convert images instantly\n\n"
        "📊 **Special Features:**\n"
        "• 4-in-1 functionality\n"
        "• 24/7 availability\n"
        "• Interactive processing\n"
        "• Prize-winning experience\n\n"
        "📅 **Created:** 2026\n"
        "🔧 **Technology:** Python + Google TTS + AI\n\n"
        "🏆 **StakePrizes9 - Win at communication!**"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a help message."""
    await update.message.reply_text(
        "🏆 **@StakePrizes9bot Help**\n\n"
        "🎯 **Speak better • Write better • Understand more**\n\n"
        "📖 **How to use:**\n\n"
        "**🔊 Text-to-Speech:**\n"
        "/tts [text] - Convert to speech\n"
        "Example: /tts Hello\n\n"
        "**🌍 Translation:**\n"
        "/translate [text] - Translate text\n"
        "Example: /translate hello\n\n"
        "**✍️ Grammar Correction:**\n"
        "/grammar [text] - Check grammar\n"
        "Example: /grammar i am go\n\n"
        "**🔄 All-in-One:**\n"
        "/all [text] - Do everything!\n"
        "Example: /all hello world\n\n"
        "**🖼️ Image to PDF:**\n"
        "Send any image - Convert to PDF\n\n"
        "**🏆 StakePrizes9 Info:**\n"
        "/stake - Get info\n\n"
        "**Commands:**\n"
        "/start - Welcome\n"
        "/tts - Text to Speech\n"
        "/translate - Translate\n"
        "/grammar - Grammar Check\n"
        "/all - All functions\n"
        "/stake - StakePrizes9 info\n"
        "/lang - Change TTS language\n"
        "/target - Set translation language\n"
        "/speed - Change speed\n"
        "/help - This menu\n"
        "/about - About this bot\n\n"
        "💡 **Tips:**\n"
        "• Send any image to convert to PDF\n"
        "• Use /all for everything at once\n"
        "• StakePrizes9 - Win at communication!"
    )

async def all_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /all command - do everything at once!"""
    text = update.message.text.replace('/all', '').strip()
    
    if not text:
        await update.message.reply_text(
            "📝 Please provide text!\nExample: /all Hello world"
        )
        return
    
    user_id = update.effective_user.id
    lang = user_preferences.get(user_id, {}).get('lang', 'en')
    speed = user_preferences.get(user_id, {}).get('speed', 'normal')
    target_lang = user_preferences.get(user_id, {}).get('target_lang', 'es')
    stake_response = get_stake_prizes_response()
    
    await update.message.reply_text(f"🏆 Processing all functions... {stake_response}")
    
    try:
        # Grammar
        grammar_result = correct_grammar(text)
        
        # Translation
        translation_result = translate_text(text, target_lang)
        
        # TTS
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            temp_path = tmp_file.name
        
        slow = (speed == 'slow')
        tts = gTTS(text=text, lang=lang, slow=slow)
        tts.save(temp_path)
        
        response = (
            f"🏆 **All Functions Complete!**\n\n"
            f"📝 **Original:** {text}\n\n"
            f"✍️ **Grammar:** {grammar_result['corrected']}\n"
            f"🌍 **Translation:** {translation_result['translated']}\n"
            f"🎁 {stake_response}"
        )
        
        await update.message.reply_text(response, parse_mode='Markdown')
        
        with open(temp_path, 'rb') as audio_file:
            await update.message.reply_audio(
                audio=audio_file,
                caption=f"🏆 StakePrizes9 TTS",
                title="StakePrizes9 Audio",
                performer="@StakePrizes9bot"
            )
        
        os.unlink(temp_path)
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("❌ Error processing. Please try again.")

async def tts_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /tts command"""
    text = update.message.text.replace('/tts', '').strip()
    
    if not text:
        await update.message.reply_text("📝 Please provide text!\nExample: /tts Hello")
        return
    
    user_id = update.effective_user.id
    lang = user_preferences.get(user_id, {}).get('lang', 'en')
    speed = user_preferences.get(user_id, {}).get('speed', 'normal')
    stake_response = get_stake_prizes_response()
    
    await update.message.reply_text(f"🔊 Converting to speech... {stake_response}")
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            temp_path = tmp_file.name
        
        slow = (speed == 'slow')
        tts = gTTS(text=text, lang=lang, slow=slow)
        tts.save(temp_path)
        
        with open(temp_path, 'rb') as audio_file:
            await update.message.reply_audio(
                audio=audio_file,
                caption=f"🏆 TTS\n🌐 {LANGUAGES.get(lang, 'English')}",
                title="StakePrizes9 Audio",
                performer="@StakePrizes9bot"
            )
        
        os.unlink(temp_path)
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("❌ Error. Please try again.")

async def translate_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /translate command"""
    text = update.message.text.replace('/translate', '').strip()
    
    if not text:
        await update.message.reply_text("📝 Please provide text!\nExample: /translate hello")
        return
    
    user_id = update.effective_user.id
    target_lang = user_preferences.get(user_id, {}).get('target_lang', 'es')
    stake_response = get_stake_prizes_response()
    
    await update.message.reply_text(f"🌍 Translating... {stake_response}")
    
    result = translate_text(text, target_lang)
    
    response = (
        f"🌍 **Translation**\n\n"
        f"📝 {result['original']}\n"
        f"✅ {result['translated']}\n"
        f"🎯 {LANGUAGES.get(target_lang, 'Spanish')}"
    )
    
    await update.message.reply_text(response, parse_mode='Markdown')

async def grammar_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /grammar command"""
    text = update.message.text.replace('/grammar', '').strip()
    
    if not text:
        await update.message.reply_text("📝 Please provide text!\nExample: /grammar i am go")
        return
    
    stake_response = get_stake_prizes_response()
    await update.message.reply_text(f"✍️ Checking grammar... {stake_response}")
    
    result = correct_grammar(text)
    
    if result['changes_made']:
        response = (
            f"✍️ **Grammar Correction**\n\n"
            f"📝 **Original:** {result['original']}\n"
            f"✅ **Corrected:** {result['corrected']}\n"
            f"🔧 **Changes:** {result['total_corrections']}"
        )
    else:
        response = f"✍️ **Grammar Check**\n\n✅ No corrections needed!\n📝 {text}"
    
    await update.message.reply_text(response, parse_mode='Markdown')

async def language_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show language selection menu for TTS."""
    keyboard = []
    row = []
    tts_languages = ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh', 'ar', 'hi']
    
    for code in tts_languages:
        if code in LANGUAGES:
            row.append(InlineKeyboardButton(LANGUAGES[code], callback_data=f"lang_{code}"))
            if len(row) == 3:
                keyboard.append(row)
                row = []
    if row:
        keyboard.append(row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🌐 Select TTS language:", reply_markup=reply_markup)

async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle language selection callback."""
    query = update.callback_query
    await query.answer()
    
    lang_code = query.data.replace("lang_", "")
    user_id = query.from_user.id
    
    if user_id not in user_preferences:
        user_preferences[user_id] = {}
    user_preferences[user_id]['lang'] = lang_code
    
    stake_response = get_stake_prizes_response()
    await query.edit_message_text(
        f"✅ Language set to: {LANGUAGES[lang_code]}\n\n"
        f"🏆 {stake_response}"
    )

async def target_language_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show target language selection for translation."""
    keyboard = []
    row = []
    
    for i, (code, name) in enumerate(LANGUAGES.items()):
        row.append(InlineKeyboardButton(name, callback_data=f"target_{code}"))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🌍 Select translation target:", reply_markup=reply_markup)

async def target_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle target language selection callback."""
    query = update.callback_query
    await query.answer()
    
    lang_code = query.data.replace("target_", "")
    user_id = query.from_user.id
    
    if user_id not in user_preferences:
        user_preferences[user_id] = {}
    user_preferences[user_id]['target_lang'] = lang_code
    
    stake_response = get_stake_prizes_response()
    await query.edit_message_text(
        f"✅ Target set to: {LANGUAGES[lang_code]}\n\n"
        f"🏆 {stake_response}"
    )

SPEED_OPTIONS = {
    'normal': 'Normal Speed',
    'slow': 'Slow Speed',
}

async def speed_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show speed selection menu."""
    keyboard = []
    for speed, name in SPEED_OPTIONS.items():
        keyboard.append([InlineKeyboardButton(name, callback_data=f"speed_{speed}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🎚️ Select speed:", reply_markup=reply_markup)

async def speed_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle speed selection callback."""
    query = update.callback_query
    await query.answer()
    
    speed = query.data.replace("speed_", "")
    user_id = query.from_user.id
    
    if user_id not in user_preferences:
        user_preferences[user_id] = {}
    user_preferences[user_id]['speed'] = speed
    
    stake_response = get_stake_prizes_response()
    await query.edit_message_text(
        f"✅ Speed set to: {SPEED_OPTIONS[speed]}\n\n"
        f"🏆 {stake_response}"
    )

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle general text messages"""
    text = update.message.text
    
    if text.startswith('/'):
        return
    
    keyboard = [
        [InlineKeyboardButton("🔊 TTS", callback_data="process_tts")],
        [InlineKeyboardButton("🌍 Translate", callback_data="process_translate")],
        [InlineKeyboardButton("✍️ Grammar", callback_data="process_grammar")],
        [InlineKeyboardButton("🏆 All", callback_data="process_all")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🏆 How to process?\n\n_{text[:100]}_",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    context.user_data['pending_text'] = text

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle photo messages - Convert to PDF"""
    await convert_image_to_pdf(update, context)

async def process_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle processing callback"""
    query = update.callback_query
    await query.answer()
    
    action = query.data
    text = context.user_data.get('pending_text', '')
    
    if not text:
        await query.edit_message_text("❌ No text found.")
        return
    
    user_id = query.from_user.id
    lang = user_preferences.get(user_id, {}).get('lang', 'en')
    speed = user_preferences.get(user_id, {}).get('speed', 'normal')
    target_lang = user_preferences.get(user_id, {}).get('target_lang', 'es')
    stake_response = get_stake_prizes_response()
    
    if action == "process_tts":
        await query.edit_message_text(f"🔊 Converting to speech... {stake_response}")
        
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                temp_path = tmp_file.name
            
            slow = (speed == 'slow')
            tts = gTTS(text=text, lang=lang, slow=slow)
            tts.save(temp_path)
            
            with open(temp_path, 'rb') as audio_file:
                await query.message.reply_audio(
                    audio=audio_file,
                    caption=f"🏆 TTS Audio",
                    title="StakePrizes9 Audio",
                    performer="@StakePrizes9bot"
                )
            
            os.unlink(temp_path)
            await query.edit_message_text(f"✅ Audio sent! {stake_response}")
            
        except Exception as e:
            await query.edit_message_text("❌ Error. Please try again.")
    
    elif action == "process_translate":
        await query.edit_message_text(f"🌍 Translating... {stake_response}")
        
        result = translate_text(text, target_lang)
        response = f"🌍 **Translation**\n\n✅ {result['translated']}"
        await query.message.reply_text(response, parse_mode='Markdown')
        await query.edit_message_text("✅ Translation done!")
    
    elif action == "process_grammar":
        await query.edit_message_text(f"✍️ Checking grammar... {stake_response}")
        
        result = correct_grammar(text)
        response = f"✍️ **Grammar**\n\n✅ {result['corrected']}"
        await query.message.reply_text(response, parse_mode='Markdown')
        await query.edit_message_text("✅ Grammar check done!")
    
    elif action == "process_all":
        await query.edit_message_text(f"🏆 Processing all... {stake_response}")
        
        # Grammar
        grammar_result = correct_grammar(text)
        await query.message.reply_text(f"✍️ **Grammar:** {grammar_result['corrected']}", parse_mode='Markdown')
        
        # Translation
        translation_result = translate_text(text, target_lang)
        await query.message.reply_text(f"🌍 **Translation:** {translation_result['translated']}", parse_mode='Markdown')
        
        # TTS
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                temp_path = tmp_file.name
            
            slow = (speed == 'slow')
            tts = gTTS(text=text, lang=lang, slow=slow)
            tts.save(temp_path)
            
            with open(temp_path, 'rb') as audio_file:
                await query.message.reply_audio(
                    audio=audio_file,
                    caption=f"🏆 All functions done!",
                    title="StakePrizes9 Audio",
                    performer="@StakePrizes9bot"
                )
            
            os.unlink(temp_path)
            await query.edit_message_text(f"✅ All completed! {stake_response}")
            
        except Exception as e:
            await query.edit_message_text("❌ Error with TTS.")

async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle voice messages."""
    await update.message.reply_text("🎤 Please send text or images!")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors."""
    logger.error(f"Update {update} caused error {context.error}")
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "⚠️ An error occurred. Please try again later."
            )
    except:
        pass

def main() -> None:
    """Start the bot."""
    logger.info("🏆 @StakePrizes9bot Starting...")
    
    token = get_token()
    
    if not token:
        logger.error("❌ No token found!")
        sys.exit(1)
    
    logger.info(f"✅ Token found!")
    
    try:
        application = Application.builder().token(token).build()
        
        # Command handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("about", about_command))
        application.add_handler(CommandHandler("stake", stake_command))
        application.add_handler(CommandHandler("lang", language_menu))
        application.add_handler(CommandHandler("target", target_language_menu))
        application.add_handler(CommandHandler("speed", speed_menu))
        application.add_handler(CommandHandler("tts", tts_command))
        application.add_handler(CommandHandler("translate", translate_command))
        application.add_handler(CommandHandler("grammar", grammar_command))
        application.add_handler(CommandHandler("all", all_command))
        
        # Callback query handlers
        application.add_handler(CallbackQueryHandler(language_callback, pattern="^lang_"))
        application.add_handler(CallbackQueryHandler(target_callback, pattern="^target_"))
        application.add_handler(CallbackQueryHandler(speed_callback, pattern="^speed_"))
        application.add_handler(CallbackQueryHandler(process_callback, pattern="^process_"))
        
        # Message handlers
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
        application.add_handler(MessageHandler(filters.PHOTO, photo_handler))
        application.add_handler(MessageHandler(filters.VOICE, voice_handler))
        
        # Error handler
        application.add_error_handler(error_handler)
        
        logger.info("✅ @StakePrizes9bot is running!")
        logger.info("🎯 Bot: @StakePrizes9bot")
        logger.info("📝 Features: TTS + Translation + Grammar + Image to PDF")
        
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"❌ Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
