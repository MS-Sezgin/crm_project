CRM Capstone - Excel + Google surumu

KURULUM
    pip install -r requirements.txt

CALISTIRMA
    python main.py        -> .py (kod ile olusturulmus) surum
    python main.py --ui   -> ui/ klasorundeki .ui dosyalarini yukleyen surum

VERI
    data/Users.xlsx          Giris bilgileri (kullanici adi, sifre, yetki)
    data/Applications.xlsx   Applications sayfasi
    data/Interviews.xlsx     Interviews sayfasi
    data/Mentor.xlsx         Mentor Interview sayfasi
    data/VIT1.xlsx           VIT1 listesi (ORNEK dosya, gercek dosyanizla degistirin)
    data/VIT2.xlsx           VIT2 listesi (ORNEK dosya, gercek dosyanizla degistirin)

GOOGLE KURULUMU (bir kez)
    1. console.cloud.google.com: proje olustur, "Google Calendar API" ve "Gmail API" etkinlestir.
    2. OAuth ekrani: uygulama adini gir, kendi Gmail adresini "Test users" listesine ekle.
    3. Credentials > Create credentials > OAuth client ID > Desktop app. JSON'u indir.
    4. Dosyayi credentials/credentials.json olarak proje klasorune koy.
    5. Admin ekraninda Event Record'a bas. Tarayicida giris yap, izin ver.
       credentials/token.json olusur, bir daha giris istenmez.
    credentials/ klasorunu GitHub'a yukleme (.gitignore bunu engeller).

DRIVE SENKRONIZASYONU
    Program her acilista Drive klasorundeki dosyalara bakar (ID: 1MZkG-X0zkXa9AKKgzR5f3NTihKoOP4Gd).
    Degisen dosyalar data/ klasorune indirilir. Degismeyenler indirilmez.
    Drive'a ulasilamazsa son yerel kopyalar kullanilir. Durum alt cubukta gosterilir.
    Google Cloud'da "Google Drive API" da etkinlestirilmeli.
    Ilk kullanimda eski token.json silinmeli (Drive izni icin yeniden giris gerekir).
    VIT1/VIT2 Drive klasorunde yoksa yerel ornek dosyalar kullanilir.
    Excel dosyasi acikken indirme yapilamaz; dosyayi kapatip programi yeniden acin.

TEST
    python test_navigation.py
    (Gecici veri kullanir ve Google cagrilarini sahte fonksiyonlarla degistirir.)

KLASOR YAPISI
    main.py              Ana pencere ve sayfa gecisleri
    data_store.py        Excel okuma, arama, filtreleme ve giris kontrolu
    google_services.py   Google Calendar okuma ve Gmail gonderimi
    styles.py            Ortak stil sablonu ve sayfa renk temalari
    pages/               Her pencerenin .py surumu
    ui/                  Qt Designer .ui dosyalari
    test_navigation.py   Navigasyon, veri ve Google testi

FILTRELER (Applications sayfasi, Filter kutusu)
    Duplicate Records      Ayni isim ve e-posta birden fazla kayitta varsa
    Previous VIT Check     Kisi Applications, VIT1, VIT2 dosyalarindan en az ikisinde varsa
    Different Record       Kisi VIT1 ve VIT2'den sadece birinde varsa
    Application Filter     Ayni isim birden fazla kayitta varsa bir kez gosterilir
    Eslestirme: isim + e-posta. Kolon adlari anahtar kelimeyle bulunur.
