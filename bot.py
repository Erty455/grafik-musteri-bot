import os
import json
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests

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
                "model": "mistralai/mistral-7b-instruct",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 400
            },
            timeout=90
        )
        result = response.json()
        if 'choices' in result and len(result['choices']) > 0:
            return result['choices'][0]['message']['content']
        elif 'error' in result:
            return f"Hata: {result['error'].get('message', 'Bilinmeyen hata')}"
        else:
            return "Bir hata oluştu, tekrar deneyin."
    except requests.exceptions.Timeout:
        return "Timeout. Tekrar deneyin."
    except Exception as e:
        return f"Hata: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    sektor, tur, marka_ismi = generate_task()
    current_task[user_id] = {"sektor": sektor, "tur": tur, "marka": marka_ismi}

    detay_brief = {
        "logo tasarımı": f"Şirket: {marka_ismi}, {sektor} sektöründe faaliyet gösteriyor. Logo için: şirket adı, minimalist ve modern bir logo istiyoruz. Renk: turuncu-beyaz tonları. Kullanım: website, sosyal medya profil fotoğrafı, kartvizit. Hedef kitle: 25-40 yaş arası şehirli profesyoneller.",
        "marka kimliği": f"Marka: {marka_ismi}, {sektor} alanında hizmet veriyor. Tüm marka kimliği packeti istiyoruz: logo, renk paleti (3 ana renk + 2 aksan renk), tipografi (header + body font), kartvizit, antetli kağıt, zarflar. Marka kişiliği: güvenilir, modern, profesyonel. Hedef: 25-45 yaş.",
        "poster tasarımı": f"Kampanya: {marka_ismi} yaz sezonu indirimi. Tarih: 15-30 Haziran. Mekan: tüm şubeler ve online. İndirim: %40. Hedef kitle: mevcut müşterilerimiz ve potansiyel yeni müşteriler. Poster boyutu: A3. Tasarımda: logo, indirim oranı, tarih bilgisi yer alsın.",
        "sosyal medya içeriği": f"Marka: {marka_ismi}. Platform: Instagram. Yeni ürünümüzü tanıtan 1080x1080 boyutunda bir post hazırlayın. Ürün: [ürün adı]. Fiyat: [fiyat]. Hafta sonu kampanyası. Hedef: 18-35 yaş, şehirli, aktif sosyal medya kullanıcıları.",
        "reels/video kapağı": f"Marka: {marka_ismi}. Video: 15-30 saniyelik ürün tanıtım videosu için kapak tasarımı. Boyut: 1080x1920 (dikey). Logo sol üst köşede, marka adı ortada. Renk: marka renkleri ağırlıklı. Stil: dikkat çekici, genç.",
        "menü tasarımı": f"Restoran: {marka_ismi}. Tür: kahve & kahvaltı dükkanı. Menü: kahve içecekler (10 çeşit), kahvaltı tabağı (5 çeşit), tatlılar (4 çeşit), sandwich/sandwich (6 çeşit). Fiyat aralığı: 35-120 TL. Tasarım: temiz, okunaklı, modern.",
        "web sitesi mockup": f"Marka: {marka_ismi}, {sektor}. E-ticaret sitesi ana sayfa mockup istiyoruz. Bölümler: üst menü (logo, kategoriler, sepet), hero banner (buyuk görsel + slogan), kategoriler (4 ana kategori), öne çıkan ürünler (8 ürün), footer. Renk: marka renkleri.",
        "ambalaj tasarımı": f"Marka: {marka_ismi}. Ürün: organik kahve çekirdeği. Ambalaj: 250g valfli kahve paketi. Tasarımda: logo, ürün adı, içerik bilgileri, barcode, kahve çekirdeği illüstrasyonu. Renk: kahverengi-tonları, modern.",
        "etiket tasarımı": f"Marka: {marka_ismi}. Urun: dogal elma sirkesi (500ml sise). Etiket: logo, urun adi, icerik (elma sirkesi), son kullanma tarihi, barcode, Organik ibaresi. Stil: dogal, temiz, beyaz-yesil tonlari.",
        "sosyal medya reklam": f"Marka: {marka_ismi}, {sektor}. Instagram reklamı: 1080x1080 boyutunda. Amaç: yeni müşteri kazanımı. Hedef: [ilgi alanı], 25-45 yaş, şehirli. Bütçe: günlük 500 TL. Süre: 7 gün. Hafta sonu özel %25 indirim.",
        "katalog tasarımı": f"Marka: {marka_ismi}. Ürünler: mobilya koleksiyonu. 16 sayfalık katalog: kapak, 4 kategori (koltuk, masa, sandalye, aksesuar), her kategoride 3-4 ürün, son sayfa iletişim. Stil: modern, minimal, beyaz zemin.",
        "davetiye kartı": f"Etkinlik: {marka_ismi} 5. kuruluş yıldönümü partisi. Tarih: 20 Haziran Cuma, saat 19:00. Yer: [mekan adresi]. Konuk: 150 kişi. Kartvizit boyutunda, katlı. Stil: şık, altın detaylı, modern."
    }
    
    detaylar = detay_brief.get(tur, f"Marka: {marka_ismi}, {sektor} sektöründe. {tur} için detaylı tasarım briefi istiyorum.")
    
    ai_prompt = f"""Sen bir gerçek müşterisin. {marka_ismi} için {tur} tasarımı yaptırmak istiyorsun.

Aşağıdaki bilgileri kullanarak kısa ama DETAYLI bir brief yaz. Sanki gerçek bir müşteri gibi konuş:

{detaylar}

Kurallar:
- Marka adı ve sektör MUTLAKA belirtilmeli
- Ne istediğin NET olmalı (boyut, format, renk tercihi, hedef kitle)
- Örnek bir cümle: "Merhaba, [marka adı] için [ne istediğini] tasarımını yaptırmak istiyorum. [detaylar]. [tarih/talimat]"
- Kesinlikle fazla detay ekleme ama temel bilgileri ver
- Sadece brief yaz, başka bir şey yazma
- Türkçe yaz"""
    
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
        
        ai_prompt = f"""Sen {marka} markasının sahibisin. {sektor} sektöründe faaliyet gösteriyorsun. Tasarımcıya {tur} tasarımı için brief verdin ve tasarımcı çalışmayı gönderdi.

Şimdi tasarımı değerlendir:
1. Brief'e uygun mu? (boyut, format, renk, içerik)
2. Marka kimliğine uygun mu?
3. Profesyonel ve kullanışlı mı?

Mümkünse ONAY VER (onaylıyorum, güzel, beğendim, tamam). 
Eğer düzeltme istersen tek bir şey iste (örn: "renkleri biraz daha canlı olsun" veya "logo daha büyük olsun").
Kısa ve doğal yanıt ver. Türkçe yaz."""
        
        response = get_ai_response(ai_prompt)
        await update.message.reply_text(response)

        if "onay" in response.lower() or "güzel" in response.lower() or "beğendim" in response.lower() or "onaylıyorum" in response.lower():
            await update.message.reply_text(
                "✅ Teşekkürler! Yeni bir proje için /basla yazabilirsin."
            )
            del current_task[user_id]
    detay_istek_kelimeleri = ["detay", "daha", "fazla", "bilgi", "ayrintı", "ne istediğimi", "daha açık"]
    
    if any(kelime in user_text.lower() for kelime in detay_istek_kelimeleri):
        detay_ai_prompt = f"""Sen bir gerçek müşterisin. {marka} için {tur} tasarımı için once brief verdin ama tasarımcı daha fazla detay istedi.

Asagidaki bilgileri DETAYLI sekilde yaz (boyut, renk, hedef kitle, stil, kullanım alanı, özel istekler dahil):

Marka: {marka}
Sektor: {sektor}
Tasarim: {tur}

Örnek detay:
- Boyut/format: ...
- Renk tercihi: ...
- Hedef kitle: ...
- Stil: ...
- İçerik: ...
- Kullanım alanı: ...

Kısa ama FULL DETAYLI yaz. Türkçe yaz."""

        detay_mesaj = get_ai_response(detay_ai_prompt)
        await update.message.reply_text(
            f"📋 Detaylar:\n{detay_mesaj}\n\nTasarımı hazırlayıp gönderebilirsiniz."
        )
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