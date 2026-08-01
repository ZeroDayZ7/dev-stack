# Dokumentacja Parametrów Piper TTS (CSOF)

### 1. `speed` (Skala długości dźwięku)

* **Wartość domyślna:** `1.0`
* **Zakres:** `0.1` do `3.0` (Sugerowany: `0.80` – `1.20`)
* **Jak działa:** Kontroluje tempo mówienia lektora. **Mniejsza wartość = szybsza mowa**, większa wartość = wolniejsza mowa.
* **Wpływ na system:** `speed: 0.85` skraca czas trwania pliku audio o 15%, co idealnie sprawdza się w dynamicznych komunikatach magazynowych (WMS), gdzie pracownik musi szybko dostać informację.

### 2. `sentence_silence` (Pauzy między zdaniami)

* **Wartość domyślna:** `0.2` (sekundy)
* **Zakres:** `0.0` do `5.0`
* **Jak działa:** Określa długość wymuszonej ciszy po każdej kropce, średniku czy wykrzykniku.
* **Wpływ na system:** Zwiększenie do `0.5` – `0.7` eliminuje efekt "zlewania się" zdań przy długich raportach (np. podsumowania reklamacji AI). Daje lektorowi naturalny oddech między wątkami z różnych modułów.

### 3. `noise_scale` (Modulacja intonacji)

* **Wartość domyślna:** `0.667`
* **Zakres:** `0.0` do `2.0`
* **Jak działa:** Kontroluje poziom zmienności energii głosu (ekspresję).
* **Wpływ na system:** Im mniejsza wartość (np. `0.3`), tym głos staje się bardziej monotonny, surowy i "robotyczny" – dobre do suchych alertów systemowych. Wyższa wartość dodaje lektorowi więcej ludzkiej, żywiołowej intonacji.

### 4. `noise_w` (Płynność głosek)

* **Wartość domyślna:** `0.8`
* **Zakres:** `0.0` do `2.0`
* **Jak działa:** Kontroluje szerokość szumu fonemów (czas trwania pojedynczych głosek i przejść między nimi).
* **Wpływ na system:** Odpowiada za płynność wymowy. Zbyt niska wartość sprawi, że słowa będą poszatkowane; optymalne wartości (`0.7` – `0.9`) zapewniają czyste i naturalne łączenie polskich zgłosek (np. "sz", "cz", "dź").

### 5. `speaker_id` (Wybór lektora)

* **Wartość domyślna:** `null`
* **Zakres:** Liczby całkowite od `0` w górę
* **Jak działa:** Wskazuje numer indeksu głosu (działa wyłącznie w modelach typu *multi-speaker*, które zawierają w sobie kilka różnych głosów).
* **Wpływ na system:** Pozwala jedną opcją zmienić głos np. z kobiecego na męski bez konieczności ładowania nowego pliku modelu `.onnx` do pamięci RAM.

---

### Ściągawka: Gotowe profile ustawień

* **Profil "Magazyn / WMS" (Szybki, konkretny):**
```json
{ "speed": 0.82, "sentence_silence": 0.15, "noise_scale": 0.4 }

```


* **Profil "Raport Zarządu / CRM" (Prestiżowy, naturalny):**
```json
{ "speed": 0.92, "sentence_silence": 0.65, "noise_scale": 0.75 }

```