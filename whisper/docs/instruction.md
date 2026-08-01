### Mini-instrukcja parametrów Whispera – jak to działa i jak wpływa na system?

* **`vad_filter` (Filtrowanie dźwięków tła - Voice Activity Detection)**
* *Domyślnie:* `true`
* *Opis:* Inteligentnie wycina z pliku audio ciszę, stuki, szumy maszyn i wdechy *zanim* przekaże dźwięk do sieci neuronowej.
* *Wpływ:* Zapobiega tzw. **halucynacjom AI** (gdy w pliku jest cisza lub szum tła magazynu, zwykły Whisper potrafi generować losowe słowa lub zapętlać kropki). Zostaw włączone na produkcję.


* **`beam_size` (Dokładność przeszukiwania drzewa decyzji)**
* *Domyślnie:* `5` (Zakres: `1` do `10`)
* *Opis:* Określa, ile równoległych ścieżek tekstu model analizuje podczas dekodowania słowa.
* *Wpływ:* Ustawienie `beam_size=1` wyłącza zaawansowane wyszukiwanie i sprawia, że Whisper działa **maksymalnie szybko**, ale może popełniać drobne błędy w trudnych słowach. Wartość `5` to idealny złoty środek między senioralną precyzją a prędkością.


* **`temperature` (Kreatywność vs Stabilność)**
* *Domyślnie:* `0.0`
* *Opis:* Kontroluje losowość generowanego tekstu.
* *Wpływ:* W systemach ERP/WMS chcemy **bezwzględnej powtarzalności**. Ustawienie `0.0` gwarantuje, że za każdym razem, gdy pracownik powie to samo słowo, system zinterpretuje je identycznie.


* **`word_timestamps` (Precyzja czasowa słów)**
* *Domyślnie:* `false`
* *Opis:* Rozbija całe zdanie na pojedyncze słowa i przypisuje im dokładny czas (co do milisekundy), w którym zostały wypowiedziane.
* *Wpływ:* Zwiększa rozmiar odpowiedzi JSON. Przydatne, jeśli we Flutterze chciałbyś robić napisy podświetlające się dokładnie w rytm mowy lektora.



### 3. Jak to przetestować przez cURL?

Teraz możesz przekazać parametry prosto w adresie URL. Spróbujmy wymusić pełną dokładność słów (`word_timestamps=true`) oraz maksymalną prędkość przetwarzania (`beam_size=1`):

```cmd
curl -X POST "http://localhost:8001/api/transcribe?beam_size=1&word_timestamps=true" -F "file=@C:\Users\Neo\Desktop\WWW\csof\csof_backend_v2\platform\services\ai-piper-tts\test\raport_prezesa.wav"
