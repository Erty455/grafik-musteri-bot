import os
import json
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests

TOKEN = "8587966861:AAGDACLbMkJtg3OHkVHfYP77WhLnIyoa_-g"
OPENROUTER_API_KEY = "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"

tasarim_turleri = [
    "logo tasarımı",
    "marka kimliği (renk paleti, font seçimi, kartvizit, antetli kağıt)",
    "poster tasarımı",
    "sosyal medya içeriği (Instagram post, story, kapak)",
    "reels/video kapağı tasarımı",
    "menü tasarımı",
    "web sitesi mockup tasarımı",
    "ambalaj tasarımı",
    "etiket tasarımı",
    "sosyal medya reklam tasarımı",
    "katalog tasarımı",
    "davetiye kartı tasarımı"
]

sektorler = [
    "modern bir kahve dükkanı",
    "teknoloji startup şirketi",
    "online giyim markası",
    "spor salonu/fitness merkezi",
    "kuaför ve güzellik salonu",
    "mobilya ve dekorasyon mağazası",
    "pet shop/evcil hayvan dükkanı",
    "online eğitim platformu",
    "diş kliniği/sağlık merkezi",
    "butik giyim mağazası",
    "vegan/vejetaryen restoran",
    "kreatif ajans",
    "cryptocurrency/fintech şirketi",
    "yoga stüdyosu",
    "çocuk eğitim merkezi"
]

brief_detaylari = {
    "logo tasarımı": "Şirketin adı, sloganı, hedef kitle, tercih ettiği renkler, kullanım alanları (web, basılı vs)",
    "marka kimliği": "Marka adı, sektör, hedef kitle, logo stili tercihi, marka hikayesi",
    "poster tasarımı": "Etkinlik/tanıtım konusu, tarih/saat, mekan, hedef kitle, iletilmek istenen mesaj",
    "sosyal medya içeriği": "Platform (Instagram, Facebook, LinkedIn), içerik türü, kampanya/konsept, hedef kitle",
    "reels/video kapağı": "Video içeriği, marka renkleri, metin ekleme isteği, stil tercihi",
    "menü tasarımı": "Restoranın tarzı, yemek kategorileri, fiyat aralığı, özel içecekler/tatlılar",
    "web sitesi mockup": "Site türü (e-ticaret, kurumsal, blog), ana sayfa içerikleri, renk tercihi",
    "ambalaj tasarımı": "Ürün türü, ambalaj malzemesi, marka elementleri, boyut",
    "etiket tasarımı": "Ürün türü, içerik bilgileri, barcode/QR kod, marka elementleri",
    "sosyal medya reklam": "Reklam hedefi, hedef kitle, bütçe, kampanya süresi",
    "katalog tasarımı": "Ürün sayısı, ürün kategorileri, sayfa sayısı, stil",
    "davetiye kartı": "Etkinlik türü, tarih/saat, mekan, konuk sayısı, stil"
}

current_task = {}
user_context = {}

def generate_task():
    sektor = random.choice(sektorler)
    tur = random.choice(tasarim_turleri)
    return sektor, tur

def get_ai_response(prompt):
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://telegram.me/grafik_musteri_bot",
                "X-Title": "Grafik Musteri Botu"
            },
            json={
                "model": "deepseek/deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 500
            },
            timeout=30
        )
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        return f"Bir hata oluştu: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    sektor, tur = generate_task()
    current_task[user_id] = {"sektor": sektor, "tur": tur}

    detaylar = brief_detaylari.get(tur, "Detayları sen belirle")
    
    ai_prompt = f"Sen bir grafik tasarımcıdan tasarım isteyen bir müşterisin. {sektor} için {tur} istiyorsun. Kısa ve doğal bir şekilde tasarım isteğini yaz. Detay olarak şunu belirt: {detaylar}. Türkçe yaz."
    
    mesaj = get_ai_response(ai_prompt)
    
    await update.message.reply_text(
        f"👋 Merhaba! {mesaj}\n\n"
        "📎 Tasarımı hazırlayıp gönder, ardından değerlendireceğim."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text

    if user_text in ["/basla", "/start", "/basla@ grafik_musteri_bot"]:
        await start(update, context)
        return

    if user_id not in current_task:
        await update.message.reply_text(
            "Merhaba! Yeni bir proje başlatmak için /başla yazabilirsin."
        )
        return

    task = current_task[user_id]
    sektor = task["sektor"]
    tur = task["tur"]

    if update.message.photo:
        await update.message.reply_text("⏳ Tasarımınızı inceliyorum...")
        
        ai_prompt = f"Sen bir grafik tasarım müşterisisin. {sektor} için {tur} için tasarım yaptın ve müşteri tasarımı gönderdi. Tasarımı değerlendir. Olumlu veya olumsuz geri bildirim ver. Kısa ve doğal bir şekilde yanıtla. Türkçe yaz."
        
        response = get_ai_response(ai_prompt)
        await update.message.reply_text(response)

        if "onay" in response.lower() or "güzel" in response.lower() or "beğendim" in response.lower():
            await update.message.reply_text(
                "✅ Teşekkürler! Yeni bir proje için /başla yazabilirsin."
            )
            del current_task[user_id]
    else:
        await update.message.reply_text(
            f"📝 {sektor} için {tur} tasarımınızı bekliyorum. "
            "Lütfen tasarım dosyasını/görseli gönderin."
        )

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("basla", start))
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))

print("Bot calisiyor...")
app.run_polling()