import os
import json
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests

import os

TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

if not TOKEN or not OPENROUTER_API_KEY:
    print("Environment variables not set!")
    exit(1)

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
    
    marka_isimleri = {
        "modern bir kahve dükkanı": ["Kahve Lab", "Bean & Brew", "Demli", "Mola Cafe", "Kahveci"],
        "teknoloji startup şirketi": ["TechFlow", "DataPeak", "Cloudix", "Innovate", "ByteSoft"],
        "online giyim markası": ["ModaVibe", "StreetStyle", "Trendix", "StyleUp", "UrbanWear"],
        "spor salonu/fitness merkezi": ["PowerFit", "FitZone", "IronGym", "ActiveLife", "ShapeUp"],
        "kuaför ve güzellik salonu": ["Luxe Beauty", "Güzelle", "StyleSalon", "PrimeCut", "BeautyBox"],
        "mobilya ve dekorasyon mağazası": ["Evim", "MobiTrend", "DekorPlus", "ModernHome", "LuxeLiving"],
        "pet shop/evcil hayvan dükkanı": ["PawHouse", "PetZone", "HappyPaws", "VetPet", "PawMart"],
        "online eğitim platformu": ["BilgiMax", "EğitimHub", "LearnPro", "SkillUp", "AkademiPlus"],
        "diş kliniği/sağlık merkezi": ["DentalCare", "SağlıkPlus", "MediZone", "GülüşKlinik", "HealthPro"],
        "butik giyim mağazası": ["ChicStyle", "EliteWear", "ModaButik", "TrendHouse", "LuxeLook"],
        "vegan/vejetaryen restoran": ["YeşilTabak", "VeganHouse", "BitkiKe", "GreenBite", "VegLife"],
        "kreatif ajans": ["PixelArt", "CreativeHub", "DesignMax", "ArtFlow", "IdeaBox"],
        "cryptocurrency/fintech şirketi": ["CoinFlow", "CryptoPay", "FinTechPro", "BlockChain", "Digimoney"],
        "yoga stüdyosu": ["ZenFlow", "YogaZone", "Harmoni", "DengeStudio", "ZenithYoga"],
        "çocuk eğitim merkezi": ["KidsAcademy", "MiniMinds", "ÇocukDünyası", "GelecekKüçük", "EğitimYıldız"]
    }
    
    marka_ismi = random.choice(marka_isimleri.get(sektor, ["Marka"]))
    
    return sektor, tur, marka_ismi

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
    sektor, tur, marka_ismi = generate_task()
    current_task[user_id] = {"sektor": sektor, "tur": tur, "marka": marka_ismi}

    detay_brief = {
        "logo tasarımı": f"Marka adı: {marka_ismi}. Sektör: {sektor}. Hedef kitle: 25-45 yaş arası profesyoneller. Tasarım stili: modern, minimal. Renk tercihi: sıcak tonlar (turuncu, krem). Kullanım alanları: website, sosyal medya, kartvizit.",
        "marka kimliği": f"Marka: {marka_ismi}. Sektör: {sektor}. Tüm marka kimliği packeti (logo, renk paleti, tipografi, kartvizit, antetli). Hedef kitle: genç-orta yaş. Marka kişiliği: güvenilir, profesyonel.",
        "poster tasarımı": f"Marka: {marka_ismi}. Sektör: {sektor}. Etkinlik: yaz indirimi/kampanya. Tarih: önümüzdeki hafta. Mekan: mağaza/online. Hedef kitle: mevcut müşteriler. İletilmek istenen: %30 indirim mesajı.",
        "sosyal medya içeriği": f"Marka: {marka_ismi}. Platform: Instagram. İçerik türü: ürün tanıtım postu. Kampanya: yeni sezon/koleksiyon. Hedef kitle: 18-35 yaş. Stil: dinamik, renkli.",
        "reels/video kapağı": f"Marka: {marka_ismi}. Video içeriği: ürün tanıtım/reklam. Marka renkleri kullanılmalı. Metin: marka adı + slogan. Stil: dikkat çekici, modern.",
        "menü tasarımı": f"Restoran: {marka_ismi}. Sektör: {sektor}. Yemek türü: kahvaltı/kahve & içecek. Fiyat aralığı: orta segment. Özel: vegan seçenekler, ev yapımı tatlılar.",
        "web sitesi mockup": f"Marka: {marka_ismi}. Sektör: {sektor}. Site türü: e-ticaret. Ana sayfa: hero banner, ürün kategorileri, öne çıkan ürünler, hakkımızda. Renk: marka renkleri.",
        "ambalaj tasarımı": f"Marka: {marka_ismi}. Ürün türü: kahve çekirdeği/paket. Ambalaj malzemesi: kağıt. Marka elementleri: logo, renkler. Boyut: 250g paket.",
        "etiket tasarımı": f"Marka: {marka_ismi}. Ürün: doğal içecek/meyve suyu. İçerik: doğal, katkısız. Barcode gerekli. Marka elementleri: logo, slogan.",
        "sosyal medya reklam": f"Marka: {marka_ismi}. Reklam hedefi: satış/artış. Hedef kitle: ilgi alanına göre. Bütçe: 1000 TL. Süre: 1 hafta. Format: 1080x1080.",
        "katalog tasarımı": f"Marka: {marka_ismi}. Ürün sayısı: 20-30 ürün. Kategoriler: 4-5 kategori. Sayfa: 12-16 sayfa. Stil: modern, temiz.",
        "davetiye kartı": f"Etkinlik: {marka_ismi} açılış/kuruluş yıldönümü. Tarih: önümüzdeki ay. Mekan: otel/etkinlik salonu. Konuk sayısı: 100-150 kişi. Stil: şık, profesyonel."
    }
    
    detaylar = detay_brief.get(tur, f"Marka: {marka_ismi}. Sektör: {sektor}. Detayları sen ekle.")
    
    ai_prompt = f"""Sen bir gerçek müşterisin ve grafik tasarımcıdan tasarım istiyorsun. Aşağıdaki bilgileri kullanarak kısa, doğal ve profesyonel bir brief yaz:

{detaylar}

Sadece tek bir mesaj olarak yaz. Hiç ek açıklama yapma. Türkçe yaz."""
    
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
    marka = task["marka"]

    if update.message.photo:
        await update.message.reply_text("⏳ Tasarımınızı inceliyorum...")
        
        ai_prompt = f"""Sen {marka} markası için tasarım yaptıran bir müşterisin. Tasarımcı {sektor} sektörü için {tur} tasarımını gönderdi. 
        
Tasarımı değerlendir:
- Brief'e uygun mu?
- Renkler ve stil markaya uygun mu?
- Profesyonel görünüyor mu?

Ya onay ver (beğendim, güzel, onaylıyorum) ya da düzeltme iste (renk değişikliği, font değişikliği, daha modernize et vb).
Kısa ve doğal yanıt ver. Türkçe yaz."""
        
        response = get_ai_response(ai_prompt)
        await update.message.reply_text(response)

        if "onay" in response.lower() or "güzel" in response.lower() or "beğendim" in response.lower() or "onaylıyorum" in response.lower():
            await update.message.reply_text(
                "✅ Teşekkürler! Yeni bir proje için /basla yazabilirsin."
            )
            del current_task[user_id]
    else:
        await update.message.reply_text(
            f"📝 {marka} için {tur} tasarımınızı bekliyorum. "
            "Lütfen tasarım dosyasını/görseli gönderin."
        )

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("basla", start))
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))

print("Bot calisiyor...")
app.run_polling()