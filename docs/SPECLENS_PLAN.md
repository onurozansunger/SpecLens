# SpecLens geliştirme planı

29 Ekim 2026. Hedef: Apple M4 Pro / 48 GB birleşik bellekte, ücretli API veya bulut GPU gerektirmeyen, teknik belgelerden kanıtlı özellik çıkarımı ve karşılaştırma yapan bir sistem.

## 29 Ekim oturumu: mevcut durum

Demo korpusu 10 PDF / 195 sayfa / 257 parça içeriyor. Ayrı test korpusu 4 yeni ürün ailesi, 101 sayfa ve 132 parça ekliyor. V3 çıkarım hattı, model/kaynak revizyonları ve değerlendirme kodu test çalıştırılmadan donduruldu. Geliştirme setinde 28/30, aile ayrımlı testte 40/48 istem bütün otomatik alan/değer/kaynak kontrollerini geçti. Bunlar insan doğruluğu ölçümü değildir; 48 istem 24 Türkçe/İngilizce soru çiftidir. İnsan incelemesi bekleniyor. 61 CPU testi geçti; gerçek MLX inference ve temiz CPU ortamı doğrulandı. Demo temel modeli kullanıyor; sentetik LoRA adapteri kullanılmıyor. Güncel sonuçlar [EXPERIMENTS.md](EXPERIMENTS.md), hata ayrımı [FAILURE_ANALYSIS.md](FAILURE_ANALYSIS.md), tekrar çalıştırma [REPRODUCING.md](REPRODUCING.md).

Aşağıdaki geniş kapsam ve eğitim bölümleri ilk yol haritasıdır; tamamlanmış özellik listesi değildir. Mevcut sürümün sınırları README'de belirtilmiştir.

## Ürün kapsamı

İlk sürüm İngilizce, metin katmanı bulunan teknik PDF'leri okur; Türkçe ve İngilizce soruları yanıtlar. Sonuçlar belge, fiziksel PDF sayfası ve alıntı içerir. HTML/Markdown kaynakları doğrulama ve veri hazırlama için kullanılır; PDF deneyinde modele ayrıca temiz kaynak metni verilmez.

İlk görevler: besleme aralığı, I/O gerilimi, çalışma sıcaklığı, bellek, haberleşme protokolü, ürün varyantı ve bu alanlara dayalı karşılaştırmalar. Bir özelliğin belgede bulunmaması, özelliğin desteklenmediği anlamına gelmez. Uygulanan çıkarım durumları `stated`, `not_stated`, `conflicting` olarak ayrılır; desteklenmeme bilgisi ayrıca alan değeri ve alıntıyla ifade edilir. Özellik desteği ile kullanıcının sayısal koşulunu karşılamak ayrıca değerlendirilir.

Örnek: "UNO R4 Minima ve Nano ESP32'nin VIN aralıklarını karşılaştır. Hangisinin belgelenmiş aralığı 24 V'u içeriyor? I/O gerilimini ayrı göster."

Taranmış PDF, grafik yorumlama, devre şeması anlama ve serbest otonom agent ilk sürümün kapsamı dışındadır. İngilizce belgelerde Türkçe soru desteği, Türkçe OCR doğruluğu iddiası değildir.

## Model seçimi

| Rol | Seçim | Gerekçe |
|---|---|---|
| Ana LLM | `mlx-community/Qwen3-4B-Instruct-2507-4bit` | 4B, non-thinking, Apache-2.0; doğrudan MLX biçimi; ağırlık dosyası yaklaşık 2.26 GB |
| Quantization kontrolü | Aynı modelin `8bit` sürümü | Yaklaşık 4.27 GB; yalnızca 4-bit kaynaklı kalite kaybını ölçmek için, ilk kurulumda indirilmez |
| Embedding | `intfloat/multilingual-e5-small` | MIT; 384 boyut; Türkçe dahil çok dilli retrieval; yaklaşık 471 MB safetensors |
| Lexical baseline | BM25 | Sayılar, SKU ve protokol adları için denetlenebilir temel yöntem |
| PDF çıkarımı | `pdfplumber` ve `pypdfium2`, CPU | Sayfa ve sözcük koordinatlarını koruyan, küçük başlangıç yolu |
| Zor tablolar | Docling, ayrı ortam/süreç; önce CPU, sonra MPS karşılaştırması | Ana akışı bozmadan tablo kalitesini iyileştirmek için ikinci aşama |

LLM başlangıç tercihi Qwen3-4B'dir. Qwen3.5-4B için MLX desteği bulunsa da GatedDeltaNet LoRA geri yayılımında uzun adım süresi bildiren açık bir hata kaydı vardır. Bu rapor bütün kurulumların başarısız olduğunu göstermez; ilk sürümün eğitim riskini azaltmak için daha basit Qwen3 mimarisi seçilmiştir.

Model kartının uzun bağlam desteğine rağmen başlangıç inference giriş bütçesi 4,096 token, çıktı bütçesi tek belge için 512, çoklu belge için 1,024 token olarak uygulanır. Gerektiğinde ölçerek 8,192 token'a çıkılır. 256K bağlam hedeflenmez. Türkçe görev başarısı model kartından varsayılmaz; test edilir.

Embedding girdileri E5 tokenizer'ıyla ölçülür, en fazla 512 token olur. `query: ` ve `passage: ` önekleri her dilde kullanılır. Metin birimleri yaklaşık 250–380 E5 token, tablolar başlıkları tekrarlanan satır grupları şeklinde tutulur. Sessiz truncation raporlanır. Embedding L2 normalize edilir; küçük korpusta NumPy ile tam arama yapılır.

## Apple Metal çalışma düzeni

- Donanım doğrulandı: Apple M4 Pro, arm64, 48 GiB birleşik bellek, macOS 27.2. Kontrol sırasında yaklaşık 294 GiB kullanılabilir disk ve sıfır swap görüldü; bunlar anlık ölçümlerdir.
- Python 3.12.12 zaten `uv` üzerinden kurulu. Sistemdeki varsayılan Python 3.14 ve Conda ortamları değiştirilmez.
- LLM inference ve adapter eğitimi **MLX / Metal** üzerinde native macOS sürecinde çalışır. MLX ile PyTorch `mps` aynı backend değildir.
- Belge çıkarımı CPU'dadır. Embedding PyTorch MPS ile denenir; küçük sorgularda CPU daha uygunsa ölçüme göre CPU seçilebilir.
- Uygulama/veri ortamı ve LLM ortamı ayrı lockfile kullanır. Docling gerekirse üçüncü, isteğe bağlı ortam olur. CUDA, bitsandbytes, FlashAttention ve Linux CUDA paketleri bu yola dahil edilmez.
- Linux Docker konteynerinin Metal'e erişeceği varsayılmaz. Yerel GPU süreci macOS'ta kalır. Docker ileride yalnızca CPU testi veya API paketlemesi için kullanılabilir; Docker Model Runner farklı bir mekanizmadır ve bu sürümün bağımlılığı değildir.
- Aynı anda tek ağır GPU işi: belge ön işleme/embedding, LLM inference ve eğitim sırayla. Birden fazla model yükleyen Uvicorn worker açılmaz.
- PyTorch'ta MPS'ye taşınan tensörler float32/uygun float16 olur; float64 CPU'da tutulur. MPS fallback sessizce açılmaz; gerekiyorsa ilgili aşama açıkça CPU'ya alınır ve kaydedilir.
- High Power Mode yoğun yüklerde soğutma/performance kapasitesine yardımcı olabilir. Bellek ve operator uyumluluğunu değiştirmez. Çalışma güç adaptörüne bağlıyken ve normal termal korumalar açıkken yapılır.
- İlk süreç hedefi inference için 12 GiB, eğitim için 24 GiB altında tepe bellektir. Bunlar ölçülmüş tüketimler değil, başlangıç bütçeleridir. Bellek basıncı/swap artarsa sıra: bağlamı azalt, batch'i azalt, eğitim katmanlarını azalt, checkpointing kullan. İşletim sisteminin bellek korumaları kaldırılmaz.

## Veriler

Ana kaynak Arduino'nun `arduino/docs-content` deposundaki CC BY-SA 4.0 belgeleridir. Belgelerin üçüncü taraf bağlantıları otomatik olarak aynı lisansa sahip sayılmaz. Yayımlanacak belge/alıntı kayıtlarında kaynak, yazar/kurum, lisans, revizyon ve değişiklik bilgisi korunur; kod lisansı ile veri lisansı ayrı tutulur.

Pilot, kaynağı doğrulanmış şu 10 datasheet ile başlar:

1. UNO R4 Minima — ABX00080.
2. UNO R4 WiFi — ABX00087.
3. Nano ESP32 — ABX00083.
4. Nano 33 BLE Rev2 — ABX00071.
5. Nano 33 BLE Sense Rev2 — ABX00069.
6. Nano RP2040 Connect — ABX00053.
7. MKR WiFi 1010 — ABX00023.
8. Mega 2560 Rev3 — A000067.
9. Portenta C33 — ABX00074.
10. Opta collective datasheet — AFX00001 / AFX00002 / AFX00003.

PDF URL'leri üretici sayfasından doğrulanır; HTTP cevabı, PDF magic bytes ve SHA-256 kontrol edilir. İndirilen PDF ile GitHub Markdown revizyonunun aynı olduğu varsayılmaz: iki artifact ayrı hash/snapshot taşır. Pilot PDF gelmezse Markdown alternatif deneyi olarak etiketlenir; PDF başarısı diye sunulmaz.

İkinci kaynak Raspberry Pi'nin CC BY-SA 4.0 kapsamındaki dokümantasyon alt dizinidir. Pico, kamera ve Compute Module özellik belgeleri, farklı kaynak düzenlerini ölçmek için eklenir. Harici datasheet PDF'lerinin lisansı ayrıca kontrol edilir. Kendi render ettiğimiz PDF varsa `derived_pdf` olarak işaretlenir; üreticinin özgün PDF'i sayılmaz.

Hazır DocVQA/DocLayNet gibi genel veri setleri başlangıç eğitim seti değildir: ilk hedefimiz ürün özellikleri, varyant koşulları ve kanıt doğruluğudur. İleride layout/OCR deneyleri ayrı benchmark olarak eklenebilir.

### Veri büyüklüğü ve ayrım

- Pilot: 10 belge, 15 temel görevin Türkçe/İngilizce eşleri olan 30 istem. Kaynak alıntıları programatik olarak kontrol edildi; insan incelemesi bekleniyor. Bunlar geliştirme örnekleridir; nihai test değildir.
- V1 hedefi: 40–60 belge, en az 24 bağımsız ürün ailesi grubu. Envanter bu çeşitliliği sağlamazsa aile sayısı/split yeniden tasarlanır; belge sayısı bağımsız örnek sayısı gibi sunulmaz.
- Hedef grup ayrımı: 14 train / 5 validation / 5 test ailesi. Aynı ürünün varyantları, eski/yeni revizyonları, çevirileri, PDF ve Markdown sürümleri aynı grupta kalır. Ortak tablolarda geçen birden fazla ürün, split grafiğiyle birlikte gruplandırılır veya bu tablolar eğitim korpusundan çıkarılır.
- Eğitim: önce yaklaşık 300–400 elle doğrulanmış görev/alan kaydı; yalnızca train ailelerinden yerel paraphrase ve kontrollü dönüşümle en fazla 1,200–1,600 örnek. Sentetik örnekler ayrıca işaretlenir. LLM'nin kendi yanıtı doğrulanmadan gold etiket olmaz.
- Validation: hedef 60 temel görev, Türkçe/İngilizce eşleriyle 120 istem.
- Test: hedef 100 temel görev, Türkçe/İngilizce eşleriyle 200 istem. Dil çiftleri bağımsız örnek sayılmaz; istatistikler görev/aile gruplarıyla hesaplanır. Az sayıda aile sonucu genelleme sınırı olarak belirtilir.
- Test aileleri adapter eğitimine, sentetik veri üretimine, prompt/model/threshold seçimine girmez. Değerlendirme anında test belgesinin retrieval indeksinde bulunması, belgeye dayalı görev tanımının parçasıdır; test etiketleri veya hazırlanmış yanıtlar indekse girmez.
- Ön eğitimde açık belgelerin görülmüş olma ihtimali nedeniyle corpus-free baseline ve ayrı, açıkça sentetik karşı-olgusal sayısal testler tutulur. Bu, ön eğitim verisinin temiz olduğunu kanıtlamaz.

Her görev: kimlik, aile, dil, soru, beklenen alan/değer/birim/koşul, cevaplanabilirlik, belge hash'i, sayfa, alıntı ve reviewer durumu içerir.

## Mimari

PDF → sayfa/sözcük/tablo çıkarımı → kaynak kimlikli parçalar → BM25 + E5 → aday kanıtlar → LLM yapılandırılmış alan çıkarımı → Pydantic doğrulaması → birim/aralık karşılaştırma araçları → kaynaklı yanıt.

Sayısal karşılaştırma LLM tarafından tahmin edilmez; doğrulanmış alanlar üzerinden Python/Pint/Decimal ile yapılır. Birim, tolerans, min/typ/max, çalışma/saklama sıcaklığı, VIN/I/O gerilimi ve varyant koşulları birbirine karıştırılmaz.

Her citation için belge/hash/sayfa/alıntı eşleşmesi kontrol edilir. Alıntının mevcut olması, iddiayı desteklediğinin tek başına kanıtı değildir; destek doğruluğu ayrıca gold görevlerle değerlendirilir. Destek bulunamazsa yanıt eksik bilgi olarak kalır.

V1'de kontrollü pipeline baseline vardır. Daha sonra `search`, `read_page`, `convert_unit`, `compare_range` gibi izinli araçlardan seçim yapan, en fazla dört adımlı agent varyantı aynı görevlerle karşılaştırılır. Serbest Python veya shell çalıştırılmaz. Belgeler komut değil veri olarak işlenir. Kaynak içindeki prompt injection örnekleri ayrı regresyon testlerine girer.

Depolama: JSON/JSONL metadata ve kanıt/deney kayıtları, NumPy embedding dosyaları. SQLite henüz gerekli olmadı. İlk korpus için ayrı vector database veya Kubernetes gerekmez. API FastAPI; yerel arayüz kaynak PDF sayfası ve sonuçları birlikte gösterir. Varsayılan erişim localhost'tur.

## Adapter eğitimi

Amaç teknik özellik ezberletmek değil, verilen kanıttan doğru şemaya çıkarım yapmak ve eksik bilgi davranışını öğretmektir. Retrieval ve extraction hataları ayrıştırılmadan eğitim başlatılmaz.

Başlangıç konfigürasyonu: quantized 4-bit base üzerinde MLX LoRA; microbatch 1, gradient accumulation 4, sequence 1,024 token ile pilot / 2,048 token ile ilk çalışma; son 8 katman, rank 8, learning rate 1e-5. Kesin CLI/config anahtarları kurulan sürümden doğrulanır. Gerekirse gradient checkpointing etkinleştirilir. Bu değerler başlangıç deneyi olup optimal oldukları iddia edilmez.

İlk çalışma 20 optimizer adımıyla kayıp, süre, gradient ve bellek testi; ardından 100 adımlık kısa deney. Uzun çalışma ancak ölçülen token/step süresiyle tahmin edildikten sonra, en fazla 60–90 dakikalık checkpoint'li oturumlar halinde yürür. İlk bütçe iki adapter konfigürasyonu; umut veren ayar için daha sonra ek seed. High Power Mode'a dayanarak süre tahmini yapılmaz.

`mask_prompt` kullanılır; kurulan MLX sürümünün hangi assistant mesajına loss uyguladığı doğrulanır. Araç yörüngeleri için gerekiyorsa her karar ayrı eğitim kaydı yapılır. Validation task başarısı checkpoint seçiminde, loss ise teşhiste kullanılır. Nihai test yalnızca yapı dondurulunca çalışır.

## Değerlendirme ve kabul

Karşılaştırmalar: BM25 / E5 / hybrid retrieval; aynı kanıtlarla temel 4-bit model / adapter; gerektiğinde aynı temel modelin 8-bit kontrolü; pipeline / sınırlı agent. Bir karşılaştırmada değişen bileşenler açıkça kaydedilir.

Ölçümler: gold kanıt Recall@5/10, normalize alan doğruluğu, birim/aralık doğruluğu, citation support precision ve completeness, görev başarısı, answerable coverage, unsupported-answer oranı, cevapsız/çelişkili soruların davranışı, TR/EN dil farkı. Sadece JSON geçerli olmasını doğruluk saymayız; sadece reddederek yüksek güvenlik metriği alınmasına izin vermemek için coverage raporlanır.

Başlangıç geliştirme hedefleri: şema geçerliliği ≥%98, destekli citation precision ≥%95, answerable görev başarısı ≥%80 ve cevapsız sorularda uydurma oranı ≤%5. Bunlar ölçülmüş sonuç veya üretim garantisi değildir. Pilot sonrası uygulanabilir hedefler validation üzerinde belirlenip testten önce dondurulur. Başarısızlık dil ve görev türüne göre gösterilir.

Gecikme: cold/warm ayrı, giriş/çıktı tokenları sabit, en az 30 istek; TTFT, toplam süre, token/s, p50/p95, süreç RSS, MLX tepe allocation ve sistem swap. MLX asenkron hesaplamada `mx.eval`/synchronization, MPS ölçümünde `torch.mps.synchronize` kullanılır. Sequential ölçüm concurrent SLA sayılmaz.

CPU unit testleri kaynak/şema/birim/split sınırlarını kontrol eder. Metal testleri yalnızca Mac'te gerçek modelle çalışır; CPU CI sonucu Metal doğrulaması yerine geçmez. Günlük geliştirme için test seti tekrar tekrar kullanılmaz.

## Aşamalar

| Aşama | Çıktı | Geçiş koşulu |
|---|---|---|
| 0 — Yerel uyumluluk | İzole Python 3.12 ortamları, lockfile, MLX/MPS kontrolü, temel model smoke raporu | Native arm64; Metal'de gerçek üretim; kaydedilmiş bellek/süre |
| 1 — Veri ve kaynak | 10 PDF, hash manifesti, sayfa çıkarımı, 30 pilot görev | Sayfa ve alıntıların elle kontrolü; varyant/gerilim ayrımlarının görünmesi |
| 2 — Retrieval | BM25/E5/hybrid, kaynak kartları | Pilot recall ve hata analizi; bütçeye uyan gecikme |
| 3 — Kanıtlı extraction | JSON şeması, yerel model worker, doğrulanmış citations, sayısal araçlar | Hataların parser/retrieval/extraction olarak ayrılması |
| 4 — Benchmark | Aile bazlı ayrım, gold validation/test protokolü | Test sızıntısı kontrolleri; eğitim ve test verisinin ayrılması |
| 5 — LoRA | Adapter, temel modelle eş koşullu karşılaştırma, model kartı | Validation'da ölçülen fayda veya dürüst negatif sonuç |
| 6 — Araç seçimi | Sınırlı agent/pipeline karşılaştırması | Döngü/timeout/injection regresyonları; fayda varsa dahil et |
| 7 — Ürün ve paylaşım | PDF yanında kanıt, karşılaştırma tablosu, tek komut demo, 2 dakikalık video | Yerel kurulumun temiz ortamda tekrarı; raporların artifact hash'leri |
| 8 — Kullanıcı pilotu | 3–5 gönüllüyle görev süresi/doğruluk kaydı | Onaylı görev verisi; gözlenen fayda ile iddiaların eşleşmesi |

İlk çalışan baseline için yaklaşık 15–25 saat, güvenilir benchmark/adapter/ürün için ek 30–55 saat mühendislik ve etiketleme tahmini vardır. Donanım süreleri pilot ölçümünden sonra hesaplanır. İnsan etiketleme bütçesi model çalıştırmadan ayrıdır.

İlk oturumun 22.05 süre sınırı sona erdi. Kullanıcının yeni talebiyle kalite, bağımsız test ve yayın hazırlığı aşamasına geçildi; ilk oturum sınırı devam eden çalışmaya uygulanmaz.

## Maliyet ve disk

Zorunlu GPU/API/hosting ücreti hedefi 0. İlk kurulum paket/model/belge indirmek için internet ister; cache tamamlanınca normal inference ağsız test edilir. Elektrik ve mevcut internet kullanımı dışında ücretli servis bağımlılığı yoktur.

İlk model ve embedding ağırlıkları yaklaşık 2.74 GB; tokenizer/paket/cache eklenir. İki Python ortamı, veri, cache ve adapter için başlangıçta 15–25 GB disk bütçesi ayrılır. 8-bit model ayrıca yaklaşık 4.27 GB indirir ve yalnızca gerekirse alınır. Ham belgeler/ağırlıklar Git'e konmaz; kaynak manifesti ve indirme komutları tutulur.

## Birincil kaynaklar

- [Qwen3-4B-Instruct-2507 model kartı](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507)
- [MLX 4-bit dönüşüm](https://huggingface.co/mlx-community/Qwen3-4B-Instruct-2507-4bit)
- [MLX 8-bit dönüşüm](https://huggingface.co/mlx-community/Qwen3-4B-Instruct-2507-8bit)
- [MLX LoRA belgeleri](https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/LORA.md)
- [Qwen3.5 LoRA performans raporu](https://github.com/ml-explore/mlx-lm/issues/1956)
- [Multilingual E5 small](https://huggingface.co/intfloat/multilingual-e5-small)
- [Arduino belge lisansı](https://github.com/arduino/docs-content/blob/main/CONTRIBUTING.md)
- [Arduino Opta kaynak sayfası](https://docs.arduino.cc/hardware/opta/)
- [Raspberry Pi belge lisansı](https://github.com/raspberrypi/documentation/blob/master/README.md)
- [Docling MPS örneği](https://docling-project.github.io/docling/_generated/examples/run_with_accelerator/)
- [PyTorch MPS](https://docs.pytorch.org/docs/main/notes/mps.html)
- [Docker GPU erişimi](https://docs.docker.com/desktop/features/gpu/)
- [Apple güç modları](https://support.apple.com/en-us/101613)

Model revizyonları ve doğrulanan kaynak yolları `configs` altındaki manifestlerde sabitlendi. Ortam sürümleri `reports/environment.json`, bağımlılıklar iki `uv.lock` dosyasında kaydedildi.
