# Annotation review worksheet

Status: **not human-reviewed**. This worksheet covers 39 base tasks: 15 development and 24 held-out, each with an English/Turkish pair. It was generated from the sealed labels, not filled in by a human.

For each task, inspect the original physical PDF page, verify units and scope, and look for alternate supporting pages. For absence cases, inspect the entire document. Review passing predictions as well as failures. Record reviewer, date, decision and proposed corrections in a separate versioned file; do not modify the sealed v1 labels.

Reference patterns below are scoring criteria, not prose answers. Source attribution: Arduino documentation contributors, CC BY-SA 4.0; see [THIRD_PARTY.md](../THIRD_PARTY.md).

## uno-vin (development)

English: What is the recommended VIN input voltage range?

Türkçe: Önerilen VIN giriş gerilimi aralığı nedir?

- [ ] Human source/label review complete
- Reviewer / date / decision: pending

**uno-r4-minima · vin_voltage · stated**

Value patterns: `(?<!\d)6\b`, `\b24\s*V(?:DC)?\b`

Accepted reference group 1: [uno-r4-minima PDF, physical page 2](https://docs.arduino.cc/resources/datasheets/ABX00080-datasheet.pdf#page=2).

PDF SHA-256: `49f5fda615856efe43b880ed6196376191896f686216c10fcbc05a5f15c19fe3`

> Recommended input voltage (VIN) is 6-24 V

Accepted reference group 1: [uno-r4-minima PDF, physical page 6](https://docs.arduino.cc/resources/datasheets/ABX00080-datasheet.pdf#page=6).

PDF SHA-256: `49f5fda615856efe43b880ed6196376191896f686216c10fcbc05a5f15c19fe3`

> V IN Input voltage from VIN pad / DC Jack 6 7.0 24 V

Accepted reference group 1: [uno-r4-minima PDF, physical page 5](https://docs.arduino.cc/resources/datasheets/ABX00080-datasheet.pdf#page=5).

PDF SHA-256: `49f5fda615856efe43b880ed6196376191896f686216c10fcbc05a5f15c19fe3`

> supports input voltages from 6-24 V

Review notes / alternate evidence: pending.

## nano-vin (development)

English: What is the recommended VIN voltage range?

Türkçe: Önerilen VIN gerilim aralığı nedir?

- [ ] Human source/label review complete
- Reviewer / date / decision: pending

**nano-esp32 · vin_voltage · stated**

Value patterns: `(?<!\d)6\b`, `\b21\s*V\b`

Accepted reference group 1: [nano-esp32 PDF, physical page 13](https://docs.arduino.cc/resources/datasheets/ABX00083-datasheet.pdf#page=13).

PDF SHA-256: `ef9c75c0c97387f5429dee5a416bee4f9fad0f79b95da9e0dae18a5716b624ac`

> The recommended input voltage range is 6-21 V.

Accepted reference group 1: [nano-esp32 PDF, physical page 2](https://docs.arduino.cc/resources/datasheets/ABX00083-datasheet.pdf#page=2).

PDF SHA-256: `ef9c75c0c97387f5429dee5a416bee4f9fad0f79b95da9e0dae18a5716b624ac`

> VIN range is 6-21 V

Accepted reference group 1: [nano-esp32 PDF, physical page 5](https://docs.arduino.cc/resources/datasheets/ABX00083-datasheet.pdf#page=5).

PDF SHA-256: `ef9c75c0c97387f5429dee5a416bee4f9fad0f79b95da9e0dae18a5716b624ac`

> V IN Input voltage from VIN pad 6 7.0 21 V

Review notes / alternate evidence: pending.

## nano-gpio (development)

English: What voltage do the digital and analog pins use?

Türkçe: Dijital ve analog pinlerin gerilimi kaç volt?

- [ ] Human source/label review complete
- Reviewer / date / decision: pending

**nano-esp32 · gpio_voltage · stated**

Value patterns: `\b3[.,]3\s*V\b`

Accepted reference group 1: [nano-esp32 PDF, physical page 13](https://docs.arduino.cc/resources/datasheets/ABX00083-datasheet.pdf#page=13).

PDF SHA-256: `ef9c75c0c97387f5429dee5a416bee4f9fad0f79b95da9e0dae18a5716b624ac`

> All digital & analog pins on the Nano ESP32 are 3.3 V.

Review notes / alternate evidence: pending.

## uno-wifi-sram (development)

English: How much SRAM does the main RA4M1 MCU have?

Türkçe: Ana RA4M1 mikrodenetleyicisinde ne kadar SRAM var?

- [ ] Human source/label review complete
- Reviewer / date / decision: pending

**uno-r4-wifi · sram_capacity · stated**

Value patterns: `\b32\s*(?-i:kB|KB)\b`

Accepted reference group 1: [uno-r4-wifi PDF, physical page 2](https://docs.arduino.cc/resources/datasheets/ABX00087-datasheet.pdf#page=2).

PDF SHA-256: `4c59ecec0a9a9f5d0029b8e11cdda23e917ce9262fe6ecddb1933182ff84f6bd`

> 32 kB SRAM

Accepted reference group 1: [uno-r4-wifi PDF, physical page 9](https://docs.arduino.cc/resources/datasheets/ABX00087-datasheet.pdf#page=9).

PDF SHA-256: `4c59ecec0a9a9f5d0029b8e11cdda23e917ce9262fe6ecddb1933182ff84f6bd`

> 256 kB flash / 32 kB SRAM / 8 kB data flash (EEPROM)

Accepted reference group 1: [uno-r4-wifi PDF, physical page 1](https://docs.arduino.cc/resources/datasheets/ABX00087-datasheet.pdf#page=1).

PDF SHA-256: `4c59ecec0a9a9f5d0029b8e11cdda23e917ce9262fe6ecddb1933182ff84f6bd`

> 32 kB SRAM

Review notes / alternate evidence: pending.

## ble-flash (development)

English: How much flash memory does the NINA B306 processor have?

Türkçe: NINA B306 işlemcisinin flash belleği ne kadar?

- [ ] Human source/label review complete
- Reviewer / date / decision: pending

**nano-33-ble-rev2 · flash_capacity · stated**

Value patterns: `\b1\s*(?-i:MB)\b`

Accepted reference group 1: [nano-33-ble-rev2 PDF, physical page 3](https://docs.arduino.cc/resources/datasheets/ABX00071-datasheet.pdf#page=3).

PDF SHA-256: `611a01f53e5a6f71ba1cb2a45a08a58c119c3d7e457c979ae26b37dfe89a55dd`

> 1 MB Flash + 256 kB RAM

Review notes / alternate evidence: pending.

## sense-humidity (development)

English: Which sensor measures relative humidity?

Türkçe: Bağıl nemi hangi sensör ölçüyor?

- [ ] Human source/label review complete
- Reviewer / date / decision: pending

**nano-33-ble-sense-rev2 · humidity_sensor · stated**

Value patterns: `\bHS3003\b`

Accepted reference group 1: [nano-33-ble-sense-rev2 PDF, physical page 4](https://docs.arduino.cc/resources/datasheets/ABX00069-datasheet.pdf#page=4).

PDF SHA-256: `2d5fa00cdfad050ee7f1586f662dbeb33d1cc5a640ede4964c7f710580fb5715`

> HS3003 Temperature & humidity sensor

Accepted reference group 1: [nano-33-ble-sense-rev2 PDF, physical page 10](https://docs.arduino.cc/resources/datasheets/ABX00069-datasheet.pdf#page=10).

PDF SHA-256: `2d5fa00cdfad050ee7f1586f662dbeb33d1cc5a640ede4964c7f710580fb5715`

> HS3003 (U8) Relative Humidity and Temperature Sensor

Accepted reference group 1: [nano-33-ble-sense-rev2 PDF, physical page 10](https://docs.arduino.cc/resources/datasheets/ABX00069-datasheet.pdf#page=10).

PDF SHA-256: `2d5fa00cdfad050ee7f1586f662dbeb33d1cc5a640ede4964c7f710580fb5715`

> The HS3003 (U8) is a MEMS sensors, designed to provide accurate readings of relative humidity and temperature in a small package.

Review notes / alternate evidence: pending.

## rp2040-sram (development)

English: How much on-chip SRAM does the RP2040 have?

Türkçe: RP2040 işlemcisinde ne kadar dahili SRAM var?

- [ ] Human source/label review complete
- Reviewer / date / decision: pending

**nano-rp2040-connect · sram_capacity · stated**

Value patterns: `\b264\s*(?-i:kB|KB)\b`

Accepted reference group 1: [nano-rp2040-connect PDF, physical page 2](https://docs.arduino.cc/resources/datasheets/ABX00053-datasheet.pdf#page=2).

PDF SHA-256: `b75b720d7e1ecf50221aedf472f208ae85257ab04213d3a248905f29dc95d46d`

> 264 kB on-chip SRAM

Review notes / alternate evidence: pending.

## mkr-clock (development)

English: What is the maximum SAMD21 processor clock frequency?

Türkçe: SAMD21 işlemcisinin en yüksek saat frekansı kaç?

- [ ] Human source/label review complete
- Reviewer / date / decision: pending

**mkr-wifi-1010 · clock_frequency · stated**

Value patterns: `\b48\s*MHz\b`

Accepted reference group 1: [mkr-wifi-1010 PDF, physical page 2](https://docs.arduino.cc/resources/datasheets/ABX00023-datasheet.pdf#page=2).

PDF SHA-256: `dfc94af6ecb1a3696cda5c282f579ea844d456a1bece6e73e37d0e12963c4949`

> Arm® Cortex®-M0+ at up to 48 MHz

Accepted reference group 1: [mkr-wifi-1010 PDF, physical page 7](https://docs.arduino.cc/resources/datasheets/ABX00023-datasheet.pdf#page=7).

PDF SHA-256: `dfc94af6ecb1a3696cda5c282f579ea844d456a1bece6e73e37d0e12963c4949`

> Arm® Cortex®-M0+ running at up to 48 MHz

Review notes / alternate evidence: pending.

## mega-pins (development)

English: How many digital I/O pins are listed for the board?

Türkçe: Kart için kaç dijital I/O pini listeleniyor?

- [ ] Human source/label review complete
- Reviewer / date / decision: pending

**mega-2560 · digital_io_count · stated**

Value patterns: `\b54\b`

Accepted reference group 1: [mega-2560 PDF, physical page 2](https://docs.arduino.cc/resources/datasheets/A000067-datasheet.pdf#page=2).

PDF SHA-256: `b5c7a45b0934043ac52364d9c2da42935238b687fbd75cb9c2098564a8ba5cf4`

> 54 Digital

Accepted reference group 1: [mega-2560 PDF, physical page 1](https://docs.arduino.cc/resources/datasheets/A000067-datasheet.pdf#page=1).

PDF SHA-256: `b5c7a45b0934043ac52364d9c2da42935238b687fbd75cb9c2098564a8ba5cf4`

> 54 digital input/output pins

Review notes / alternate evidence: pending.

## portenta-flash (development)

English: What is the external QSPI flash memory capacity?

Türkçe: Harici QSPI flash bellek kapasitesi nedir?

- [ ] Human source/label review complete
- Reviewer / date / decision: pending

**portenta-c33 · flash_capacity · stated**

Value patterns: `\b16\s*(?-i:MB)\b`

Accepted reference group 1: [portenta-c33 PDF, physical page 5](https://docs.arduino.cc/resources/datasheets/ABX00074-datasheet.pdf#page=5).

PDF SHA-256: `852496c4d28c71e2cb5c66fcb094a5785e2b1a9d56714de7e52b58cbc53d5fb5`

> 16 MB QSPI Flash memory (MX25L12833F)

Review notes / alternate evidence: pending.

## opta-supply (development)

English: What is the nominal supply voltage range, excluding the permissible range?

Türkçe: İzin verilen tolerans aralığından ayrı olarak nominal besleme gerilimi aralığı nedir?

- [ ] Human source/label review complete
- Reviewer / date / decision: pending

**opta · nominal_supply · stated**

Value patterns: `\b12\b`, `\b24\s*V(?:DC)?\b`

Accepted reference group 1: [opta PDF, physical page 8](https://docs.arduino.cc/resources/datasheets/AFX00001-AFX00002-AFX00003-datasheet.pdf#page=8).

PDF SHA-256: `fd47c8f48498d7b0c713b2880c0aabf5b4cda20ecb3d75dabc12c32ca1cfc13d`

> Supply voltage 12 - 24 V

Review notes / alternate evidence: pending.

## opta-variant (development)

English: Which Opta SKU provides Wi-Fi connectivity?

Türkçe: Hangi Opta SKU kodu Wi-Fi bağlantısı sunuyor?

- [ ] Human source/label review complete
- Reviewer / date / decision: pending

**opta · wifi_sku · stated**

Value patterns: `\bAFX00002\b`

Accepted reference group 1: [opta PDF, physical page 4](https://docs.arduino.cc/resources/datasheets/AFX00001-AFX00002-AFX00003-datasheet.pdf#page=4).

PDF SHA-256: `fd47c8f48498d7b0c713b2880c0aabf5b4cda20ecb3d75dabc12c32ca1cfc13d`

> SKU AFX00003 AFX00001 AFX00002

Accepted reference group 1: [opta PDF, physical page 13](https://docs.arduino.cc/resources/datasheets/AFX00001-AFX00002-AFX00003-datasheet.pdf#page=13).

PDF SHA-256: `fd47c8f48498d7b0c713b2880c0aabf5b4cda20ecb3d75dabc12c32ca1cfc13d`

> Wi-Fi® and Bluetooth® Low Energy (AFX00002 Only)

Accepted reference group 1: [opta PDF, physical page 5](https://docs.arduino.cc/resources/datasheets/AFX00001-AFX00002-AFX00003-datasheet.pdf#page=5).

PDF SHA-256: `fd47c8f48498d7b0c713b2880c0aabf5b4cda20ecb3d75dabc12c32ca1cfc13d`

> Wi-Fi® 2.4 GHz and Bluetooth® LE 4.2 supported by firmware, 5.1 supported by hardware (AFX00002)

Accepted reference group 2: [opta PDF, physical page 4](https://docs.arduino.cc/resources/datasheets/AFX00001-AFX00002-AFX00003-datasheet.pdf#page=4).

PDF SHA-256: `fd47c8f48498d7b0c713b2880c0aabf5b4cda20ecb3d75dabc12c32ca1cfc13d`

> Wi-Fi® N/A N/A 802.11 b/g/n

Accepted reference group 2: [opta PDF, physical page 13](https://docs.arduino.cc/resources/datasheets/AFX00001-AFX00002-AFX00003-datasheet.pdf#page=13).

PDF SHA-256: `fd47c8f48498d7b0c713b2880c0aabf5b4cda20ecb3d75dabc12c32ca1cfc13d`

> Wi-Fi® and Bluetooth® Low Energy (AFX00002 Only)

Accepted reference group 2: [opta PDF, physical page 5](https://docs.arduino.cc/resources/datasheets/AFX00001-AFX00002-AFX00003-datasheet.pdf#page=5).

PDF SHA-256: `fd47c8f48498d7b0c713b2880c0aabf5b4cda20ecb3d75dabc12c32ca1cfc13d`

> Wi-Fi® 2.4 GHz and Bluetooth® LE 4.2 supported by firmware, 5.1 supported by hardware (AFX00002)

Review notes / alternate evidence: pending.

## opta-temperature (development)

English: What is the recommended operating temperature range?

Türkçe: Önerilen çalışma sıcaklığı aralığı nedir?

- [ ] Human source/label review complete
- Reviewer / date / decision: pending

**opta · operating_temperature · stated**

Value patterns: `-20`, `\b50\s*°?\s*C\b`

Accepted reference group 1: [opta PDF, physical page 8](https://docs.arduino.cc/resources/datasheets/AFX00001-AFX00002-AFX00003-datasheet.pdf#page=8).

PDF SHA-256: `fd47c8f48498d7b0c713b2880c0aabf5b4cda20ecb3d75dabc12c32ca1cfc13d`

> Temperature Operating Range -20...50 °C

Review notes / alternate evidence: pending.

## nano-temperature-review (development)

English: Report both upper temperature limits: the recommended ambient table and the EUT compliance statement. Preserve their different scopes.

Türkçe: Önerilen ortam sıcaklığı tablosu ile EUT uygunluk ifadesindeki iki üst sıcaklık sınırını da ayrı kapsamlarıyla bildir.

- [ ] Human source/label review complete
- Reviewer / date / decision: pending

**nano-esp32 · ambient_temperature · stated**

Value patterns: `\b105\s*°?\s*C\b`

Accepted reference group 1: [nano-esp32 PDF, physical page 5](https://docs.arduino.cc/resources/datasheets/ABX00083-datasheet.pdf#page=5).

PDF SHA-256: `ef9c75c0c97387f5429dee5a416bee4f9fad0f79b95da9e0dae18a5716b624ac`

> T ambient Ambient Temperature -40 25 105 °C

**nano-esp32 · eut_temperature · stated**

Value patterns: `\b85\s*°?\s*C\b`

Accepted reference group 1: [nano-esp32 PDF, physical page 21](https://docs.arduino.cc/resources/datasheets/ABX00083-datasheet.pdf#page=21).

PDF SHA-256: `ef9c75c0c97387f5429dee5a416bee4f9fad0f79b95da9e0dae18a5716b624ac`

> The operating temperature of the EUT can’t exceed 85°C

Review notes / alternate evidence: pending.

## opta-price (development)

English: What is the retail price in Turkish lira stated in this datasheet?

Türkçe: Bu datasheet'te Türk lirası cinsinden belirtilen perakende satış fiyatı nedir?

- [ ] Human source/label review complete
- Reviewer / date / decision: pending

**opta · retail_price · not_stated**

Expected value: null; no citations.

Review notes / alternate evidence: pending.

## test-due-sram (test)

English: How much total SRAM does the SAM3X8E have, before dividing it into banks?

Türkçe: Bankalara ayırmadan önce SAM3X8E toplam SRAM kapasitesi nedir?

- [ ] Human source/label review complete
- Reviewer / date / decision: pending

**due · sram_capacity · stated**

Value patterns: `\b96\s*(?-i:KB|kB)\b`

Accepted reference group 1: [due PDF, physical page 6](https://docs.arduino.cc/resources/datasheets/A000062-datasheet.pdf#page=6).

PDF SHA-256: `8adecb95208f6571fb25d8ba1254f66dd735ac255977007c5ff6cde346685391`

> 96 KB SRAM

Review notes / alternate evidence: pending.

## test-due-flash (test)

English: What is the SAM3X8E flash memory capacity?

Türkçe: SAM3X8E flash bellek kapasitesi nedir?

- [ ] Human source/label review complete
- Reviewer / date / decision: pending

**due · flash_capacity · stated**

Value patterns: `\b512\s*(?-i:KB|kB)\b`

Accepted reference group 1: [due PDF, physical page 6](https://docs.arduino.cc/resources/datasheets/A000062-datasheet.pdf#page=6).

PDF SHA-256: `8adecb95208f6571fb25d8ba1254f66dd735ac255977007c5ff6cde346685391`

> Flash Memory 512 KB

Accepted reference group 1: [due PDF, physical page 6](https://docs.arduino.cc/resources/datasheets/A000062-datasheet.pdf#page=6).

PDF SHA-256: `8adecb95208f6571fb25d8ba1254f66dd735ac255977007c5ff6cde346685391`

> SAM3X 512 KB Flash

Review notes / alternate evidence: pending.

## test-due-vin-table (test)

English: In the Recommended Operating Conditions table, what are the minimum and maximum VIN input voltages? Exclude the typical value.

Türkçe: Recommended Operating Conditions tablosundaki minimum ve maksimum VIN giriş gerilimi nedir? Tipik değeri hariç tut.

- [ ] Human source/label review complete
- Reviewer / date / decision: pending

**due · vin_voltage · stated**

Value patterns: `(?<!\d)6(?:[.,]0)?\b`, `\b16\s*V\b`

Accepted reference group 1: [due PDF, physical page 7](https://docs.arduino.cc/resources/datasheets/A000062-datasheet.pdf#page=7).

PDF SHA-256: `8adecb95208f6571fb25d8ba1254f66dd735ac255977007c5ff6cde346685391`

> V IN Input voltage from VIN pad 6.0 7.0 16 V

Review notes / alternate evidence: pending.

## test-due-digital (test)

English: How many digital input pins are listed for the board?

Türkçe: Kart için kaç dijital giriş pini listeleniyor?

- [ ] Human source/label review complete
- Reviewer / date / decision: pending

**due · digital_io_count · stated**

Value patterns: `\b54\b`

Accepted reference group 1: [due PDF, physical page 7](https://docs.arduino.cc/resources/datasheets/A000062-datasheet.pdf#page=7).

PDF SHA-256: `8adecb95208f6571fb25d8ba1254f66dd735ac255977007c5ff6cde346685391`

> 54x digital inputs

Accepted reference group 1: [due PDF, physical page 1](https://docs.arduino.cc/resources/datasheets/A000062-datasheet.pdf#page=1).

PDF SHA-256: `8adecb95208f6571fb25d8ba1254f66dd735ac255977007c5ff6cde346685391`

> 54x digital input/output

Accepted reference group 1: [due PDF, physical page 6](https://docs.arduino.cc/resources/datasheets/A000062-datasheet.pdf#page=6).

PDF SHA-256: `8adecb95208f6571fb25d8ba1254f66dd735ac255977007c5ff6cde346685391`

> Digital Inputs not 5 V compatible (x54)

Review notes / alternate evidence: pending.

## test-giga-sram (test)

English: What is the on-chip SRAM capacity of the STM32H747, excluding external SDRAM?

Türkçe: Harici SDRAM hariç STM32H747 dahili SRAM kapasitesi nedir?

- [ ] Human source/label review complete
- Reviewer / date / decision: pending

**giga-r1-wifi · sram_capacity · stated**

Value patterns: `\b1\s*(?-i:MB)\b`

Accepted reference group 1: [giga-r1-wifi PDF, physical page 11](https://docs.arduino.cc/resources/datasheets/ABX00063-datasheet.pdf#page=11).

PDF SHA-256: `58c107bd49b3d2efe33d4044c913a6cc4cb7df352c1b0de9dc5136133e146a6c`

> 1 MB SRAM on the STM32H747

Accepted reference group 1: [giga-r1-wifi PDF, physical page 2](https://docs.arduino.cc/resources/datasheets/ABX00063-datasheet.pdf#page=2).

PDF SHA-256: `58c107bd49b3d2efe33d4044c913a6cc4cb7df352c1b0de9dc5136133e146a6c`

> STM32H747XI 2 MB Flash 1 MB RAM

Review notes / alternate evidence: pending.

## test-giga-external-flash (test)

English: What is the external NOR flash memory capacity, excluding the MCU internal flash?

Türkçe: MCU dahili flash hariç harici NOR flash bellek kapasitesi nedir?

- [ ] Human source/label review complete
- Reviewer / date / decision: pending

**giga-r1-wifi · flash_capacity · stated**

Value patterns: `\b16\s*(?-i:MB)\b`

Accepted reference group 1: [giga-r1-wifi PDF, physical page 2](https://docs.arduino.cc/resources/datasheets/ABX00063-datasheet.pdf#page=2).

PDF SHA-256: `58c107bd49b3d2efe33d4044c913a6cc4cb7df352c1b0de9dc5136133e146a6c`

> 16 MB NOR Flash

Accepted reference group 1: [giga-r1-wifi PDF, physical page 11](https://docs.arduino.cc/resources/datasheets/ABX00063-datasheet.pdf#page=11).

PDF SHA-256: `58c107bd49b3d2efe33d4044c913a6cc4cb7df352c1b0de9dc5136133e146a6c`

> 16 MB of NOR Flash

Review notes / alternate evidence: pending.

## test-giga-m7-clock (test)

English: What is the maximum clock frequency of the Cortex-M7 core only?

Türkçe: Yalnızca Cortex-M7 çekirdeğinin maksimum saat frekansı nedir?

- [ ] Human source/label review complete
- Reviewer / date / decision: pending

**giga-r1-wifi · clock_frequency · stated**

Value patterns: `\b480\s*MHz\b`

Accepted reference group 1: [giga-r1-wifi PDF, physical page 2](https://docs.arduino.cc/resources/datasheets/ABX00063-datasheet.pdf#page=2).

PDF SHA-256: `58c107bd49b3d2efe33d4044c913a6cc4cb7df352c1b0de9dc5136133e146a6c`

> Cortex®-M7 core with double-precision FPU and L1 cache up to 480 MHz

Accepted reference group 1: [giga-r1-wifi PDF, physical page 10](https://docs.arduino.cc/resources/datasheets/ABX00063-datasheet.pdf#page=10).

PDF SHA-256: `58c107bd49b3d2efe33d4044c913a6cc4cb7df352c1b0de9dc5136133e146a6c`

> Cortex®-M7 running at 480 MHz

Review notes / alternate evidence: pending.

## test-giga-vin-table (test)

English: What minimum-to-maximum VIN range is stated in the Recommended Operating Conditions table?

Türkçe: Recommended Operating Conditions tablosunda belirtilen minimum-maksimum VIN aralığı nedir?

- [ ] Human source/label review complete
- Reviewer / date / decision: pending

**giga-r1-wifi · vin_voltage · stated**

Value patterns: `(?<!\d)6\b`, `\b32\s*V\b`

Accepted reference group 1: [giga-r1-wifi PDF, physical page 7](https://docs.arduino.cc/resources/datasheets/ABX00063-datasheet.pdf#page=7).

PDF SHA-256: `58c107bd49b3d2efe33d4044c913a6cc4cb7df352c1b0de9dc5136133e146a6c`

> V IN Input voltage from VIN pad 6 7.0 32 V

Review notes / alternate evidence: pending.

## test-nicla-sram (test)

English: How much internal SRAM is available in the nRF52832?

Türkçe: nRF52832 içinde ne kadar dahili SRAM var?

- [ ] Human source/label review complete
- Reviewer / date / decision: pending

**nicla-sense-me · sram_capacity · stated**

Value patterns: `\b64\s*(?-i:KB|kB)\b`

Accepted reference group 1: [nicla-sense-me PDF, physical page 4](https://docs.arduino.cc/resources/datasheets/ABX00050-datasheet.pdf#page=4).

PDF SHA-256: `d5ec525dee59ef58eee5cea1ab54c119d232ad5bff69b3b9d1fb9ecb0d5e0299`

> Internal SRAM Memory 64 KB

Accepted reference group 1: [nicla-sense-me PDF, physical page 11](https://docs.arduino.cc/resources/datasheets/ABX00050-datasheet.pdf#page=11).

PDF SHA-256: `d5ec525dee59ef58eee5cea1ab54c119d232ad5bff69b3b9d1fb9ecb0d5e0299`

> 64 KB SRAM is available to the user.

Review notes / alternate evidence: pending.

## test-nicla-internal-flash (test)

English: What is the internal flash memory capacity of the nRF52832, excluding external flash?

Türkçe: Harici flash hariç nRF52832 dahili flash bellek kapasitesi nedir?

- [ ] Human source/label review complete
- Reviewer / date / decision: pending

**nicla-sense-me · flash_capacity · stated**

Value patterns: `\b512\s*(?-i:KB|kB)\b`

Accepted reference group 1: [nicla-sense-me PDF, physical page 4](https://docs.arduino.cc/resources/datasheets/ABX00050-datasheet.pdf#page=4).

PDF SHA-256: `d5ec525dee59ef58eee5cea1ab54c119d232ad5bff69b3b9d1fb9ecb0d5e0299`

> Internal Flash Memory 512 KB

Accepted reference group 1: [nicla-sense-me PDF, physical page 11](https://docs.arduino.cc/resources/datasheets/ABX00050-datasheet.pdf#page=11).

PDF SHA-256: `d5ec525dee59ef58eee5cea1ab54c119d232ad5bff69b3b9d1fb9ecb0d5e0299`

> nRF52832 internal 512 KB FLASH

Review notes / alternate evidence: pending.

## test-nicla-humidity (test)

English: Which environmental sensor measures humidity?

Türkçe: Nemi ölçen çevresel sensörün modeli nedir?

- [ ] Human source/label review complete
- Reviewer / date / decision: pending

**nicla-sense-me · humidity_sensor · stated**

Value patterns: `\bBME688\b`

Accepted reference group 1: [nicla-sense-me PDF, physical page 5](https://docs.arduino.cc/resources/datasheets/ABX00050-datasheet.pdf#page=5).

PDF SHA-256: `d5ec525dee59ef58eee5cea1ab54c119d232ad5bff69b3b9d1fb9ecb0d5e0299`

> Model Bosch® BME688

Accepted reference group 1: [nicla-sense-me PDF, physical page 11](https://docs.arduino.cc/resources/datasheets/ABX00050-datasheet.pdf#page=11).

PDF SHA-256: `d5ec525dee59ef58eee5cea1ab54c119d232ad5bff69b3b9d1fb9ecb0d5e0299`

> via the Bosch® BME688 sensor (U6).

Accepted reference group 2: [nicla-sense-me PDF, physical page 5](https://docs.arduino.cc/resources/datasheets/ABX00050-datasheet.pdf#page=5).

PDF SHA-256: `d5ec525dee59ef58eee5cea1ab54c119d232ad5bff69b3b9d1fb9ecb0d5e0299`

> Humidity: 0-100%

Accepted reference group 2: [nicla-sense-me PDF, physical page 11](https://docs.arduino.cc/resources/datasheets/ABX00050-datasheet.pdf#page=11).

PDF SHA-256: `d5ec525dee59ef58eee5cea1ab54c119d232ad5bff69b3b9d1fb9ecb0d5e0299`

> This provides capabilities for pressure, humidity, temperature

Review notes / alternate evidence: pending.

## test-nicla-vin-table (test)

English: What is the minimum-to-maximum VIN input range? Do not use the logic-level voltage.

Türkçe: Minimum-maksimum VIN giriş aralığı nedir? Mantık seviyesi gerilimini kullanma.

- [ ] Human source/label review complete
- Reviewer / date / decision: pending

**nicla-sense-me · vin_voltage · stated**

Value patterns: `\b3[.,]5\b`, `\b5[.,]5\s*V\b`

Accepted reference group 1: [nicla-sense-me PDF, physical page 7](https://docs.arduino.cc/resources/datasheets/ABX00050-datasheet.pdf#page=7).

PDF SHA-256: `d5ec525dee59ef58eee5cea1ab54c119d232ad5bff69b3b9d1fb9ecb0d5e0299`

> V IN Input voltage from VIN pad 3.5 5.0 5.5 V

Review notes / alternate evidence: pending.

## test-edge-sram (test)

English: How much RAM is listed for the Nina B306 module?

Türkçe: Nina B306 modülü için ne kadar RAM listeleniyor?

- [ ] Human source/label review complete
- Reviewer / date / decision: pending

**edge-control · sram_capacity · stated**

Value patterns: `\b256\s*(?-i:KB|kB)\b`

Accepted reference group 1: [edge-control PDF, physical page 2](https://docs.arduino.cc/resources/datasheets/AKX00034-datasheet.pdf#page=2).

PDF SHA-256: `1d8e9005b61de220de786029c52a796c99cab59baf6df5cccf38579411f908b5`

> 1 MB Flash + 256 KB RAM

Review notes / alternate evidence: pending.

## test-edge-storage-flash (test)

English: What is the additional external flash memory capacity for data storage?

Türkçe: Veri depolama için ek harici flash bellek kapasitesi nedir?

- [ ] Human source/label review complete
- Reviewer / date / decision: pending

**edge-control · flash_capacity · stated**

Value patterns: `\b2\s*(?-i:MB)\b`

Accepted reference group 1: [edge-control PDF, physical page 15](https://docs.arduino.cc/resources/datasheets/AKX00034-datasheet.pdf#page=15).

PDF SHA-256: `1d8e9005b61de220de786029c52a796c99cab59baf6df5cccf38579411f908b5`

> additional 2MB flash memory for data storage

Accepted reference group 1: [edge-control PDF, physical page 2](https://docs.arduino.cc/resources/datasheets/AKX00034-datasheet.pdf#page=2).

PDF SHA-256: `1d8e9005b61de220de786029c52a796c99cab59baf6df5cccf38579411f908b5`

> Memory 2MB onboard QSPI

Review notes / alternate evidence: pending.

## test-edge-clock (test)

English: What is the maximum clock frequency of the main processor?

Türkçe: Ana işlemcinin maksimum saat frekansı nedir?

- [ ] Human source/label review complete
- Reviewer / date / decision: pending

**edge-control · clock_frequency · stated**

Value patterns: `\b64\s*MHz\b`

Accepted reference group 1: [edge-control PDF, physical page 11](https://docs.arduino.cc/resources/datasheets/AKX00034-datasheet.pdf#page=11).

PDF SHA-256: `1d8e9005b61de220de786029c52a796c99cab59baf6df5cccf38579411f908b5`

> The Main Processor is a Cortex M4F running at up to 64MHz.

Accepted reference group 1: [edge-control PDF, physical page 2](https://docs.arduino.cc/resources/datasheets/AKX00034-datasheet.pdf#page=2).

PDF SHA-256: `1d8e9005b61de220de786029c52a796c99cab59baf6df5cccf38579411f908b5`

> 64 MHz Arm® Cortex®-M4F (with FPU)

Review notes / alternate evidence: pending.

## test-edge-recommended-temperature (test)

English: What is the recommended operating temperature range, excluding absolute maximum ratings?

Türkçe: Mutlak maksimum değerler hariç önerilen çalışma sıcaklığı aralığı nedir?

- [ ] Human source/label review complete
- Reviewer / date / decision: pending

**edge-control · operating_temperature · stated**

Value patterns: `-15`, `\b60\s*°?\s*C\b`

Accepted reference group 1: [edge-control PDF, physical page 8](https://docs.arduino.cc/resources/datasheets/AKX00034-datasheet.pdf#page=8).

PDF SHA-256: `1d8e9005b61de220de786029c52a796c99cab59baf6df5cccf38579411f908b5`

> T Conservative thermal limits -15 20 60 °C

Review notes / alternate evidence: pending.

## test-due-missing-price (test)

English: What retail price in Turkish lira is stated in this datasheet?

Türkçe: Bu datasheet içinde Türk lirası cinsinden hangi perakende satış fiyatı belirtiliyor?

- [ ] Human source/label review complete
- Reviewer / date / decision: pending

**due · retail_price · not_stated**

Expected value: null; no citations.

Review notes / alternate evidence: pending.

## test-giga-r1-wifi-missing-price (test)

English: What retail price in Turkish lira is stated in this datasheet?

Türkçe: Bu datasheet içinde Türk lirası cinsinden hangi perakende satış fiyatı belirtiliyor?

- [ ] Human source/label review complete
- Reviewer / date / decision: pending

**giga-r1-wifi · retail_price · not_stated**

Expected value: null; no citations.

Review notes / alternate evidence: pending.

## test-nicla-sense-me-missing-price (test)

English: What retail price in Turkish lira is stated in this datasheet?

Türkçe: Bu datasheet içinde Türk lirası cinsinden hangi perakende satış fiyatı belirtiliyor?

- [ ] Human source/label review complete
- Reviewer / date / decision: pending

**nicla-sense-me · retail_price · not_stated**

Expected value: null; no citations.

Review notes / alternate evidence: pending.

## test-edge-control-missing-price (test)

English: What retail price in Turkish lira is stated in this datasheet?

Türkçe: Bu datasheet içinde Türk lirası cinsinden hangi perakende satış fiyatı belirtiliyor?

- [ ] Human source/label review complete
- Reviewer / date / decision: pending

**edge-control · retail_price · not_stated**

Expected value: null; no citations.

Review notes / alternate evidence: pending.

## test-due-memory-pair (test)

English: Give the SAM3X8E SRAM and flash capacities separately.

Türkçe: SAM3X8E SRAM ve flash kapasitelerini ayrı ayrı ver.

- [ ] Human source/label review complete
- Reviewer / date / decision: pending

**due · sram_capacity · stated**

Value patterns: `\b96\s*(?-i:KB|kB)\b`

Accepted reference group 1: [due PDF, physical page 6](https://docs.arduino.cc/resources/datasheets/A000062-datasheet.pdf#page=6).

PDF SHA-256: `8adecb95208f6571fb25d8ba1254f66dd735ac255977007c5ff6cde346685391`

> 96 KB SRAM

**due · flash_capacity · stated**

Value patterns: `\b512\s*(?-i:KB|kB)\b`

Accepted reference group 1: [due PDF, physical page 6](https://docs.arduino.cc/resources/datasheets/A000062-datasheet.pdf#page=6).

PDF SHA-256: `8adecb95208f6571fb25d8ba1254f66dd735ac255977007c5ff6cde346685391`

> Flash Memory 512 KB

Accepted reference group 1: [due PDF, physical page 6](https://docs.arduino.cc/resources/datasheets/A000062-datasheet.pdf#page=6).

PDF SHA-256: `8adecb95208f6571fb25d8ba1254f66dd735ac255977007c5ff6cde346685391`

> SAM3X 512 KB Flash

Review notes / alternate evidence: pending.

## test-nicla-memory-pair (test)

English: Give the nRF52832 internal SRAM and internal flash capacities separately.

Türkçe: nRF52832 dahili SRAM ve dahili flash kapasitelerini ayrı ayrı ver.

- [ ] Human source/label review complete
- Reviewer / date / decision: pending

**nicla-sense-me · sram_capacity · stated**

Value patterns: `\b64\s*(?-i:KB|kB)\b`

Accepted reference group 1: [nicla-sense-me PDF, physical page 4](https://docs.arduino.cc/resources/datasheets/ABX00050-datasheet.pdf#page=4).

PDF SHA-256: `d5ec525dee59ef58eee5cea1ab54c119d232ad5bff69b3b9d1fb9ecb0d5e0299`

> Internal SRAM Memory 64 KB

Accepted reference group 1: [nicla-sense-me PDF, physical page 11](https://docs.arduino.cc/resources/datasheets/ABX00050-datasheet.pdf#page=11).

PDF SHA-256: `d5ec525dee59ef58eee5cea1ab54c119d232ad5bff69b3b9d1fb9ecb0d5e0299`

> 64 KB SRAM is available to the user.

**nicla-sense-me · flash_capacity · stated**

Value patterns: `\b512\s*(?-i:KB|kB)\b`

Accepted reference group 1: [nicla-sense-me PDF, physical page 4](https://docs.arduino.cc/resources/datasheets/ABX00050-datasheet.pdf#page=4).

PDF SHA-256: `d5ec525dee59ef58eee5cea1ab54c119d232ad5bff69b3b9d1fb9ecb0d5e0299`

> Internal Flash Memory 512 KB

Accepted reference group 1: [nicla-sense-me PDF, physical page 11](https://docs.arduino.cc/resources/datasheets/ABX00050-datasheet.pdf#page=11).

PDF SHA-256: `d5ec525dee59ef58eee5cea1ab54c119d232ad5bff69b3b9d1fb9ecb0d5e0299`

> nRF52832 internal 512 KB FLASH

Review notes / alternate evidence: pending.

## test-compare-sram (test)

English: Compare the main processor SRAM capacity in the two selected boards. Give one value per document.

Türkçe: Seçilen iki kartın ana işlemci SRAM kapasitesini karşılaştır. Her belge için ayrı değer ver.

- [ ] Human source/label review complete
- Reviewer / date / decision: pending

**due · sram_capacity · stated**

Value patterns: `\b96\s*(?-i:KB|kB)\b`

Accepted reference group 1: [due PDF, physical page 6](https://docs.arduino.cc/resources/datasheets/A000062-datasheet.pdf#page=6).

PDF SHA-256: `8adecb95208f6571fb25d8ba1254f66dd735ac255977007c5ff6cde346685391`

> 96 KB SRAM

**nicla-sense-me · sram_capacity · stated**

Value patterns: `\b64\s*(?-i:KB|kB)\b`

Accepted reference group 1: [nicla-sense-me PDF, physical page 4](https://docs.arduino.cc/resources/datasheets/ABX00050-datasheet.pdf#page=4).

PDF SHA-256: `d5ec525dee59ef58eee5cea1ab54c119d232ad5bff69b3b9d1fb9ecb0d5e0299`

> Internal SRAM Memory 64 KB

Accepted reference group 1: [nicla-sense-me PDF, physical page 11](https://docs.arduino.cc/resources/datasheets/ABX00050-datasheet.pdf#page=11).

PDF SHA-256: `d5ec525dee59ef58eee5cea1ab54c119d232ad5bff69b3b9d1fb9ecb0d5e0299`

> 64 KB SRAM is available to the user.

Review notes / alternate evidence: pending.

## test-compare-vin (test)

English: Compare the minimum-to-maximum VIN ranges in the Recommended Operating Conditions tables. Give one range per document.

Türkçe: Recommended Operating Conditions tablolarındaki minimum-maksimum VIN aralıklarını karşılaştır. Her belge için ayrı aralık ver.

- [ ] Human source/label review complete
- Reviewer / date / decision: pending

**giga-r1-wifi · vin_voltage · stated**

Value patterns: `(?<!\d)6\b`, `\b32\s*V\b`

Accepted reference group 1: [giga-r1-wifi PDF, physical page 7](https://docs.arduino.cc/resources/datasheets/ABX00063-datasheet.pdf#page=7).

PDF SHA-256: `58c107bd49b3d2efe33d4044c913a6cc4cb7df352c1b0de9dc5136133e146a6c`

> V IN Input voltage from VIN pad 6 7.0 32 V

**nicla-sense-me · vin_voltage · stated**

Value patterns: `\b3[.,]5\b`, `\b5[.,]5\s*V\b`

Accepted reference group 1: [nicla-sense-me PDF, physical page 7](https://docs.arduino.cc/resources/datasheets/ABX00050-datasheet.pdf#page=7).

PDF SHA-256: `d5ec525dee59ef58eee5cea1ab54c119d232ad5bff69b3b9d1fb9ecb0d5e0299`

> V IN Input voltage from VIN pad 3.5 5.0 5.5 V

Review notes / alternate evidence: pending.
