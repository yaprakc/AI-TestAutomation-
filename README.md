# AI-TestAutomation-
## BU PROJENİN AMACI ÜRETKEN YAPAY ZEKA KULLANARAK OTOMATİK YAZILIM TESTLERİ OLUŞTURMAK VE ÇALIŞTIRMAK.

### Genel Bakış
Dinamik Fonksiyon Testi uygulaması, Python fonksiyonları için birim, entegrasyon ve performans testlerini; java için birim ve entegrasyon  testlerini otomatik olarak oluşturup çalıştıran bir GUI tabanlı araçtır. OpenAI'nin Gemini modelini kullanarak kodu analiz eder, programlama dilini tespit eder ve standartlaştırılmış komutlarla uygun test senaryoları üretir. Bu uygulama, kodu manuel olarak test yazmadan hızlı bir şekilde test etmek isteyen geliştiriciler için oldukça faydalıdır.


### Özellikler
Otomatik Test Üretimi: Verilen fonksiyon koduna göre birim, entegrasyon ve performans testlerini AI kullanarak oluşturur.

Çoklu Dil Desteği: Sağlanan kodun Python veya Java olup olmadığını algılar ve buna göre testler oluşturur.

Performans Testi: Python için timeit kullanarak performans testi seçeneği içerir.

Ayrıntılı Test Sonuçları: Test sonuçlarını hata, başarısızlık ve başarı için renk kodlarıyla gösterir.

İlerleme Çubuğu ve GUI Arayüzü: Test oluşturma ve çalıştırma durumu için bir ilerleme çubuğu içeren interaktif bir arayüz.


### Teknoloji Yığını

Python: Ana programlama dili

Tkinter: Kullanıcı etkileşimi için GUI framework

Google Gemini API: Test senaryolarını oluşturmak için kullanılan model

JUnit 4: Java birim testleri için kullanılan framework

unittest: Python birim testleri için kullanılan framework

### Kurulum
1-Rehberliği klonlayın:

```
git clone https://github.com/yaprakc/AI-TestAutomation-.git
```

```
cd AI-TestAutomation-
```

2-Gerekli Python kütüphanelerini yükleyin:

```
pip install google-generativeai
```

3-Java'nın sisteminizde yüklü olduğundan emin olun.

4-JUnit 4 ve Hamcrest Core JAR dosyalarını indirin ve yollarını script'e ekleyin.

5-API Anahtarı Konfigürasyonu: GOOGLE_API_KEY değişkenini kendi Google Gemini API anahtarınızla güncelleyin.

6-JAR Dosya Yolları: junit_jar_path ve hamcrest_jar_path değişkenlerine junit-4.12.jar ve hamcrest-core-1.3.jar dosyalarının yollarını girin.

### Projenin Çalışması
![image](https://github.com/user-attachments/assets/840d463b-6dfe-4f6f-9fec-1b735322d93a) İlk olarak bir fonksiyon girilir.

![image](https://github.com/user-attachments/assets/a1ec23c6-1e16-48fd-aa91-01ec28609e6e) Fonksiyon için birim, entegrasyon ve performans testleri oluşturulur. Burada bir tane örneği verilmiştir.

![image](https://github.com/user-attachments/assets/ca8637ef-6c8f-4028-8911-d26be0421c77) Tüm testlerin çalıştırılıp sonuçlarının başarılı ve başarısız olduğu ekranda yazdırılır.


### Lisans
Bu proje MIT Lisansı ile lisanslanmıştır.
