# Projekt: TheLook E-commerce Analytics

Projekt portfolio pod ofertę **Data Analyst w Allegro (zespół Advertising Analytics, Allegro Ads)**.
Cel: pokazać biznesowe podejście do danych — od analizy ruchu i zachowań kupujących do konkretnych rekomendacji z oszacowanym wpływem.

## Jak ze mną pracować (tryb nauki)

- Uczę się w trakcie projektu. Prowadź mnie **krok po kroku**, jeden etap naraz.
- Przy każdym kroku wyjaśnij najpierw **dlaczego** to robimy, potem **jak**.
- Daj mi samemu uruchamiać zapytania i kod; nie rób wszystkiego za mnie bez pytania.
- Nowe pojęcia (np. funkcje okna, CTE, kohorty) tłumacz krótko na przykładzie z tych danych.
- Odpowiadaj po polsku. Kod, nazwy plików i kolumn po angielsku.

## Wymagania z oferty, które projekt ma pokazać

- Analiza ruchu, zachowań kupujących i efektywności → rekomendacje biznesowe
- Stack: GCP / BigQuery, SQL, Python, Airflow, Looker Studio, Git
- Mile widziane: Agentic AI / ML do automatyzacji analityki

## Dane

- `bigquery-public-data.thelook_ecommerce` — syntetyczny sklep odzieżowy.
- Tabele: `users`, `orders`, `order_items`, `products`, `events`, `inventory_items`, `distribution_centers`.
- Źródło ruchu: `users.traffic_source` oraz `events.traffic_source`.
- **Brak kosztów reklam** — ROAS/CPA liczymy tylko na jawnie opisanych założeniach (np. przyjęty CPC per kanał) w symulatorze.
- Dostęp: BigQuery sandbox (bez karty). Zawsze sprawdzaj szacowany rozmiar zapytania, unikaj `SELECT *`.

## Pytanie biznesowe

> Z których źródeł ruchu przychodzą najbardziej wartościowi klienci, gdzie lejek traci kupujących i w co warto inwestować?

## Mapa projektu

0. Setup i poznanie danych ✅
1. **Pytania biznesowe i definicje KPI** ← obecny etap (CVR, AOV, LTV, retencja, zwroty; ROAS/CPA tylko na założeniach)
2. Analizy SQL: lejek (events), źródła ruchu, LTV wg kanału pozyskania, kohorty, zwroty
3. Python: połączenie z BigQuery przez API (`google-cloud-bigquery`), analiza w notebooku
4. Pipeline: automatyczne odświeżanie (Airflow lub GitHub Actions), warstwy raw → staging → marts
5. Aplikacja w Streamlit, opublikowana z linkiem (+ dashboard w Looker Studio)
6. Memo dla stakeholdera (3 rekomendacje z oszacowanym wpływem, założenia, ograniczenia) + agent AI (pytanie po polsku → SQL → wynik + rekomendacja; tylko SELECT, limit kosztu, pokazywany SQL)

## Środowisko

- Projekt GCP: `thelook-analytics-512312` (BigQuery sandbox, konsola w języku polskim)
- Zapytania wykonywane w BigQuery Studio na pełnych nazwach tabel `bigquery-public-data.thelook_ecommerce.*`
- **Python ✅ (działa od 2026-10-22):** SQL uruchamiany z Pythona przez `google-cloud-bigquery`, wyniki do pandas
  - Wirtualne środowisko `.venv` (Windows: `.venv\Scripts\activate`), biblioteki w `requirements.txt`
  - Logowanie: Google Cloud CLI + `gcloud auth application-default login` (bez kluczy w kodzie); domyślny projekt ustawiony przez `gcloud config set project`
  - Po instalacji gcloud trzeba było zrestartować VS Code, żeby terminal widział komendę
  - Skrypty w formacie komórek `# %%` (rozszerzenia Python + Jupyter w VS Code), uruchamiane komórka po komórce
- Konwencje w kodzie Pythona:
  - funkcja `run_query()`: najpierw dry run (szacowany koszt w MB), potem wykonanie z `maximum_bytes_billed` (bezpiecznik 1 GB)
  - parametry zapytań (`@cutoff` + `ScalarQueryParameter`) zamiast wklejania wartości do SQL f-stringiem
  - BigQuery robi ciężkie agregacje, pandas dokańcza drobne obliczenia na małym wyniku

## Etap 0 — zakończony ✅

Zrobione:
- [x] Projekt GCP i BigQuery sandbox
- [x] Przejrzenie schematów i podglądu tabel
- [x] Pierwsze zapytania: liczba wierszy, statusy zamówień i zakres dat, rozkład `traffic_source`
- [ ] Repo GitHub `thelook-ecommerce-analytics` z README zawierającym pytanie biznesowe (do zrobienia)

Skala danych (stan na 2026-10-21): 100 000 users, 125 470 orders, 181 995 order_items, 29 120 products, 2 428 223 events.
Średnio ok. 1,25 zamówienia na użytkownika i ok. 1,45 produktu na zamówienie.

Wnioski:
- **Statusy zamówień:** Shipped ~30%, Complete ~25%, Processing ~20%, Cancelled ~15%, Returned ~10%.
  Przyjęta definicja: **przychód = Complete + Shipped**. Cancelled i Returned wyłączone z przychodu netto; anulowania i zwroty to osobne KPI.
  15% anulowań i 10% zwrotów to wysoki poziom — potencjalny temat rekomendacji w memo.
- **Okres danych:** od 2019-01 do bieżącego dnia — zbiór jest dopisywany codziennie.
  Dlatego stosujemy **datę odcięcia `2026-10-01`** (tylko pełne miesiące, odtwarzalne wyniki).
- **Ograniczenia danych (syntetyczne):** zamówienia w statusie Processing istnieją już od 2019 r., buyer rate ~51% jest nierealnie wysoki jak na e-commerce.
- **Źródła ruchu:** Search 69,9%, Organic 15,0%, Facebook 6,1%, Email 5,0%, Display 4,0% użytkowników — silna koncentracja na jednym kanale (ryzyko biznesowe).
  `users.traffic_source` = kanał pozyskania (pierwszy kontakt); `events.traffic_source` = źródło każdej sesji. Rozróżniamy te dwa pojęcia.

## Etap 1 — w toku

Definicje KPI (do zapisania w `docs/kpi.md`):
- Przychód = suma `order_items.sale_price` dla statusów Complete i Shipped
- Buyer rate = % użytkowników z ≥1 zamówieniem liczonym do przychodu
- AOV = przychód / liczba zamówień
- Revenue per user = przychód / liczba użytkowników pozyskanych z kanału
- Cancel rate / Return rate = % zamówień anulowanych / zwróconych
- Data odcięcia: `2026-10-01`

Wartość klienta wg kanału pozyskania (dane do 2026-10-01):

| Kanał | Users | Buyers | Buyer rate | Orders | Revenue | AOV | Revenue/user |
|---|---|---|---|---|---|---|---|
| Search | 67 656 | 34 781 | 51,4% | 44 879 | 3 874 649 | 86,34 | 57,27 |
| Organic | 14 499 | 7 440 | 51,3% | 9 659 | 826 793 | 85,60 | 57,02 |
| Facebook | 5 934 | 3 081 | 51,9% | 4 011 | 351 927 | 87,74 | 59,31 |
| Email | 4 888 | 2 542 | 52,0% | 3 294 | 283 860 | 86,17 | 58,07 |
| Display | 3 886 | 1 998 | 51,4% | 2 624 | 234 312 | 89,30 | 60,30 |

Wnioski:
- Kanały są **prawie identyczne**: rozrzut buyer rate 0,7 pp, AOV ok. 4%, revenue per user ok. 6%.
- Największy kanał (Search) nie ma najwyższej wartości klienta; najwyżej Display, ale różnice mogą być szumem.
- Wniosek biznesowy: jeśli wartość klienta nie różni się między kanałami, o alokacji budżetu decyduje **koszt pozyskania (CPA)**, nie jakość ruchu.
- Kanał jest w danych syntetycznych prawdopodobnie przypisywany losowo, więc historię biznesową budujemy na wymiarach, które się różnią.

Przedziały ufności 95% dla revenue per user (skrypt `01_channel_value.py`, uruchomiony 2026-10-22):

| Kanał | Users | Revenue/user | 95% CI |
|---|---|---|---|
| Display | 3 898 | 58,24 | 55,04–61,45 |
| Search | 68 082 | 57,74 | 56,97–58,51 |
| Facebook | 5 750 | 56,65 | 54,16–59,15 |
| Email | 4 793 | 56,55 | 53,72–59,37 |
| Organic | 14 202 | 56,45 | 54,82–58,08 |

- **Wszystkie przedziały zachodzą na siebie → brak dowodu na różnicę wartości klienta między kanałami.** Potwierdza wniosek: budżet optymalizujemy po CPA.
- Szerokość przedziału zależy od liczebności: Search ±0,8 (68 tys. users), Display ±3,2 (3,9 tys.). Wysoka średnia Display to najpewniej efekt małej próby.
- Nakładanie się CI to test ostrożny; możliwe rozszerzenie: test t Welcha dla par kanałów.

**Odkrycie: historia danych zmienia się z dnia na dzień.** Przy tej samej dacie odcięcia (`2026-10-01`) liczba użytkowników Search wzrosła z 67 656 (2026-10-21) do 68 082 (2026-10-22), a revenue per user Display spadł z 60,30 do 58,24.
Zbiór nie jest tylko dopisywany — generator najpewniej dodaje rekordy z datami wstecz lub zmienia statusy starych zamówień.
Wniosek: **data odcięcia nie wystarcza do odtwarzalności → potrzebny snapshot** (zamrożona kopia tabel we własnym zbiorze BigQuery). Liczby w tabelach powyżej pochodzą z różnych dni i nie są w pełni porównywalne.
Uwaga: w trybie sandbox tabele we własnych zbiorach domyślnie wygasają po 60 dniach — snapshot musi dać się odtworzyć skryptem.

Poznane techniki SQL: funkcja okna `SUM(COUNT(*)) OVER ()`, CTE (`WITH`), `LEFT JOIN` zachowujący użytkowników bez zakupów, `COUNT(DISTINCT ...)`.

## Zmiana kierunku (2026-10-22)

Projekt skupia się teraz na **EDA**, a potem na **dashboardach pokazujących, że dane są pobierane na bieżąco**.
Snapshot odłożony: codzienne zmiany w danych to zaleta dla dashboardu „na żywo”. W EDA zawsze zapisujemy, na jaki moment są dane (`checked_at`, `MAX(created_at)`).

### Część A – EDA

| Krok | Zakres | Pytanie biznesowe | Plik |
|---|---|---|---|
| A1 ✅ | Jakość danych: braki, duplikaty, zakresy dat, świeżość | Czy możemy ufać danym? | `02_eda_data_quality.ipynb` |
| A2 ✅ | Klienci: wiek, płeć, kraje, kanał pozyskania | Kim są klienci? | `04_eda_customers.ipynb` |
| A3 ✅ | Produkty: kategorie, marki, ceny, marża (`cost` vs `retail_price`) | Na czym zarabiamy? | `05_eda_products.ipynb` |
| A4 ✅ | Zamówienia w czasie: trendy miesięczne, sezonowość, statusy | Czy biznes rośnie? | `06_eda_orders_time.ipynb` |
| A5 ✅ | Anulowania i zwroty wg kategorii, marki, kraju | Gdzie tracimy pieniądze? | `07_eda_cancellations_returns.ipynb` |
| A6 ✅ | Zachowanie na stronie: sesje, typy zdarzeń, ścieżka do zakupu (`events`) | Gdzie odpadają kupujący? | `08_eda_events_funnel.ipynb` |

**Część A (EDA) zakończona** — następny etap: część B (widoki w BigQuery + dashboard).

Każdy krok kończy się 2–3 wnioskami, które trafią na dashboard.

Analizy EDA są teraz w notatnikach `.ipynb` (zamiast skryptów `# %%`); dane wczytuje `read_bq()` z `bq_utils.py` (jak `pd.read_csv` z `usecols`/`dtype`, opcjonalnie `sample_pct`). Kolumn z danymi osobowymi nie pobieramy. `events` wczytujemy jako 10% próbkę (`TABLESAMPLE`) — wyniki z niej to szacunki.

#### A1 – wnioski (2026-10-29)

1. **Braki w datach są strukturalne, nie są błędami.** Puste `shipped_at` / `delivered_at` / `returned_at` odpowiadają dokładnie statusom (np. 90% braków `returned_at` = ~10% zwrotów). `inventory.sold_at` puste w 63% = towar niesprzedany (temat do A3).
   46,5% zdarzeń w `events` nie ma `user_id` (sesje niezalogowanych) → **lejek liczymy po `session_id`**.
2. **`order_items.created_at` jest niewiarygodne:** 30,4% wysłanych pozycji ma `shipped_at < created_at` (w `orders`: 0%), a `order_items`, `events` i `inventory` mają rekordy do 3 dni w przyszłości.
   → **Reguła: analizy w czasie opieramy na `orders.created_at`** (pozycje łączymy z zamówieniem po `order_id`).
3. **Dane czyste, ale wyraźnie syntetyczne:** brak duplikatów kluczy, cen ≤ 0 i sprzedaży poniżej kosztu; statusy idealnie spójne z datami; marża ~51% zarówno Men, jak i Women (koszt prawdopodobnie jako stały % ceny — sprawdzić w A3).
   Historia się zmienia: 124 452 zamówienia (2026-10-29) vs 125 470 (2026-10-21), mimo braku filtra.

Pułapka pandas: `(newest - now).dt.days` zaokrągla w dół, więc różnica −8 h daje `-1`. Porównanie z `NaT` zawsze daje False → odsetki liczymy wśród wierszy z niepustą datą.

#### A2 – wnioski (dane na 2026-10-29 08:21 UTC)

1. **Płeć to pierwszy wymiar z realną różnicą wartości:** revenue per user M 63,18 vs F 55,85 (+13%), po ~50 tys. users w grupie (nie szum).
   Buyer rate równy (~52,8%) → różnica w całości z AOV (92,08 vs 81,27). Pokrywa się z różnicą średniej ceny produktów Men 63,2 vs Women 55,9 (+13%, A1)
   → **hipoteza: przyczyną jest asortyment (ceny), nie zachowanie klientów — do sprawdzenia w A3.**
2. **Wiek, kraj i kanał nie różnicują wartości klienta.** Rozrzut revenue/user: kanał 3,5%, wiek 6,7%, kraj (top 10) 12,3% — ale duże kraje (Chiny, USA, Brazylia) mają ~59,5, a wyższe Japonia (64,69) i Niemcy (61,97) to efekt małej próby (2–4 tys. users).
   Skład wieku i płci jest identyczny we wszystkich kanałach (kanał przypisany losowo). Wiek rozłożony równomiernie 12–70 (syntetyczne).
3. **Baza klientów nie rośnie:** stałe ~1 040 nowych users miesięcznie od 2019 r. Koncentracja rynku: Chiny 33,7%, USA 22,8%, Brazylia 14,6% (razem 71%).

Technika z A2: funkcja `segment_kpi(df, by)` (KPI dla dowolnego wymiaru), kontrola poprawności złączenia (liczba wierszy i suma przychodu przed/po), miara rozrzutu max/min revenue per user do porównania wymiarów.
Ostrzeżenia przy wczytywaniu (`google-cloud-bigquery-storage` już dodany do `requirements.txt`): brak quota project (`gcloud auth application-default set-quota-project thelook-analytics-512312`) i brak `google-cloud-bigquery-storage` (wolniejsze pobieranie) — niegroźne.

#### A3 – wnioski (dane na 2026-10-29 08:39 UTC)

1. **Hipoteza z A2 potwierdzona: różnica AOV M vs F to asortyment, nie zachowanie.** Pozycji w zamówieniu tyle samo (F 1,45 vs M 1,46), różni się średnia cena pozycji (F 55,99 vs M 63,27).
   Kobiety kupują w 100% z działu Women, mężczyźni w 100% z Men → **płeć i dział są nierozdzielne (confounding)**.
   Źródło głównie **efekt struktury** (mix): u M garnitury (Suits & Sport Coats, śr. 127) to 11,4% przychodu, kurtki i jeansy po ~14% (u F ~9%). Efekt ceny w tych samych kategoriach niejednoznaczny (Shorts M +23%, Swim M −25%).
2. **Marża różni się systematycznie między kategoriami** — każda ma własny przedział ~10 pp. (np. Blazers & Jackets 57–67%, Socks 35–45%). Wysoka: Blazers & Jackets 62%, Accessories / Skirts / Suits & Sport Coats / Socks & Hosiery ~60%; niska: Clothing Sets 38%, Suits (Women) / Socks ~40%, Leggings 40%.
   **Ranking po przychodzie ≠ ranking po zysku** (Jeans: 2. w przychodzie, marża 46,5%; Suits & Sport Coats: 4., marża 59,8%) → **budżet reklamowy optymalizować pod zysk brutto (ROAS na marży / POAS), nie przychód** — kandydat na rekomendację w memo.
3. **Sprzedaż rozproszona:** 13 z 26 kategorii = 80% przychodu (lider Outerwear & Coats 12,2%, Jeans 11,7%); 2 756 marek, największa (Calvin Klein) 1,9%, top 10 = 13,4% (długi ogon reklamodawców).
   Brak rabatów (`sale_price` = `retail_price` w 100%); artefakt: produkty po 0,02.

Przychód w A3 (5 952 870) = A2 → definicja przychodu spójna między notatnikami.
Technika z A3: `validate="many_to_one"` w `merge` (bezpiecznik przed zdublowaniem), Pareto (`cumsum` udziałów), dekompozycja AOV = pozycje/zamówienie × średnia cena pozycji, rozróżnienie efektu ceny i efektu struktury (`pivot_table` + udziały kategorii).
Notatniki generowane z pełnym kodem i testowane na sztucznych danych przed oddaniem; użytkownik uruchamia i zapisuje, wyniki odczytywane z pliku `.ipynb`.
**Poprawki w istniejącym notatniku: edytować komórki w miejscu (zachować `id` komórek)**, nie generować pliku od nowa — inaczej diff w Gicie pokazuje „Metadata changed” w każdej komórce.

#### A4 – wnioski (dane na 2026-10-29, pełne miesiące 2019-01 – 2026-09)

1. **Wzrost wykładniczy i przyspieszający:** przychód YTD 2026 **+72% r/r** (2023–2025 ~45% rocznie); wrzesień 2026 265 tys. vs 119 tys. rok wcześniej. AOV stały (~85–88) → wzrost = **liczba zamówień, nie wartość koszyka**. Nowe rejestracje stałe (~1 040/mies.) → wzrostu nie tłumaczy pozyskanie.
2. **Wzrost napędza kumulująca się baza:** udział powracających w przychodzie 3% (2019) → 20% (2022) → 46% (2026). Mediana od rejestracji do 1. zakupu **394 dni** (średnia 591) → rośnie pula zarejestrowanych, którzy jeszcze nie kupili.
   → **Największe aktywo to baza zarejestrowanych: aktywacja i powroty (retargeting, CRM)** — kandydat na rekomendację w memo. Ograniczenie: >1 rok do 1. zakupu to raczej cecha generatora.
3. **Sezonowość słaba; „spadek lutego” to efekt kalendarza:** surowo luty −10,3%, na przychodzie dziennym −3,4%. Wzorzec ±7%: słabsze lato (lipiec −6,6%, sierpień −4,9%), lepsze październik (+4,4%) i grudzień (+3,1%). Brak efektu dnia tygodnia (po 14,3%).
   Statusy stabilne w czasie (~15% Cancelled, ~10% Returned), także w ostatnich miesiącach → brak efektu cenzurowania; generator nadaje status niezależnie od wieku zamówienia.

Techniki z A4: `groupby().cumcount()` jako `ROW_NUMBER() OVER (PARTITION BY ...)` (nowy vs powracający), porównanie YTD (te same miesiące każdego roku), trend = scentrowana średnia ruchoma 2×12, indeks sezonowy = wartość / trend (nie / średnia roku — przy wzroście zawyża koniec roku: grudzień wychodził 1,41), **korekta kalendarza (przychód na dzień, `PeriodIndex.days_in_month`)**. Przy wykładniczym wzroście MA lekko zawyża trend → indeksy przesunięte o ok. −1 pp.

#### A5 – wnioski (dane na 2026-10-29, wszystkie zamówienia)

1. **Tracimy prawie co czwartą złotówkę:** Cancelled + Returned = 2,67 mln (24,8% wartości zamówień). Z każdych 100 zł rozstrzygniętych zamówień (bez Processing) sklep zatrzymuje **69 zł**.
   → **ROAS na złożonych zamówieniach zawyża realny zwrot o ~45% (1 / 0,69): „ROAS 4,0” ≈ 2,8** — kandydat na rekomendację w memo (oceniać kampanie na przychodzie po stratach).
2. **Anulowania kosztują więcej niż zwroty:** 1,63 mln (61% strat) vs 1,04 mln. Anulowanie jest przed wysyłką → łatwiej zapobiec (płatność, dostawa, dostępność) — kandydat do memo.
3. **Żaden wymiar nie różnicuje strat (szum):** return rate kategorie 9,0–11,3%, kraje 9,6–10,7%, płeć / kanał / dział ~10%. Po Bonferronim nie przechodzi nic (max |z| 2,76 — anulowania Suits — przy progu 3,10 dla 26 kategorii). Każda kategoria traci ~30–31% zysku brutto; ranking po stratach bez zmian (korelacja 0,999) → wnioski z A3 o marży aktualne.
   Status pozycji = status zamówienia w 100% (reguła z A1 potwierdzona). Ograniczenie: status w danych syntetycznych wygląda na losowy.

Techniki z A5: analiza na dwóch poziomach (zamówienie — wymiary klienta; pozycja — wymiary produktu), `rate_table()` z z-score i 95% CI, wykres przedziałów ufności (dot + error bar), **wielokrotne porównania i poprawka Bonferroniego** (`statistics.NormalDist().inv_cdf(1 - 0.05 / (2k))` — bez scipy; progi: 2 grupy 2,24, 10 → 2,81, 20 → 3,02, 26 → 3,10), zależność obserwacji na poziomie pozycji (zawyża z), korelacja Spearmana jako Pearson na rangach.

#### A6 – wnioski (dane na 2026-10-29, zdarzenia do 2026-09-30: 662 088 sesji, 2,31 mln zdarzeń)

1. **Lejek zdeterminowany przez logowanie:** 74,8% sesji anonimowych, **0% zakupów** (4 stałe ścieżki: `department > product`, `product`, `product > cart > cancel`, `department > product > cart`); zalogowane kupują w 99,8%. Konwersja sesji 25,2% (realnie 2–3%). Lejek ogółem: produkt 100% → koszyk 62,4% → zakup 40,3% koszyków; połowa anonimowych koszyków kończy się `cancel`.
2. **Źródło sesji i przeglądarka nie różnicują konwersji** (24,9–25,6%).
3. **Atrybucja niemożliwa bez wspólnego słownika kanałów:** `users.traffic_source` = Search, Organic, Facebook, Email, Display; `events.traffic_source` = Adwords, Email, Facebook, Organic, YouTube (wspólne 3). Źródło sesji z zakupem niezależne od kanału pozyskania (Email → Email 44,7% vs 45,1% losowo). Anonimowe sesje stałe ~5,3 tys./mies., zalogowane rosną wykładniczo → konwersja sesji 41% → 57% w ostatnim roku (efekt wzrostu bazy z A4).
   → Wartość na rozmowę: rozróżnienie first / last touch i problem niespójnej taksonomii kanałów.

Techniki z A6: agregacja w BigQuery zamiast wczytywania 2,4 mln wierszy (wyniki do pandas: dziesiątki wierszy), `LOGICAL_OR` (flagi na poziomie sesji), `COUNTIF`, `GROUP BY ROLLUP` (wiersz sumy), `STRING_AGG(... ORDER BY sequence_number)` (ścieżki), `HAVING`, parametr `@cutoff` jako `TIMESTAMP`, test niezależności „obserwowane vs oczekiwane przy losowości”. Koszt zapytań: 140–180 MB każde.

### Wykresy

- `viz_style.py` — wspólny styl matplotlib: `apply_style()`, `legend_outside(ax)` (legenda poza wykresem, prawy górny róg), `COLORS`, `MONTHS_PL`. Import: `from viz_style import apply_style, legend_outside, COLORS, MONTHS_PL`. Po zmianie pliku: restart kernela.
- Paleta dopasowana do szablonu dashboardu użytkownika (zielony akcent, grafitowa typografia, białe karty, pastelowy gradient w tle strony): `series_1` zielony `#1a9a50`, `series_2` grafit `#3a3f47`, tło `#ffffff`. Para sprawdzona: kontrast 3,6:1 / 10,6:1 na białym, OKLab ΔE 28,5 (≥ 25 przy każdym typie daltonizmu). Jaśniejszy zielony z szablonu (`#22b35e`) ma tylko 2,7:1 — za mało.
- Preferencje użytkownika: legenda poza obszarem wykresu (prawy górny róg); **jeden kolor, gdy znaczenie niesie oś** (np. odchylenie +/− od trendu — bez legendy i bez drugiego koloru); etykiety tylko selektywnie (ostatni punkt, max/min); oś słupków od 0.
- Gradient i zaokrąglone karty z szablonu → warstwa dashboardu (Looker Studio / Streamlit), nie matplotlib.

### Praca z Gitem

- Każdy krok na osobnej gałęzi (np. `eda-a4-orders-time`), na koniec Pull Request na GitHubie i merge do `main`.

### Część B – Dashboard na żywych danych

- **Looker Studio** podłączone bezpośrednio do BigQuery (darmowe, wymienione w ofercie, link do CV).
- W BigQuery **widoki (views)** — liczą się na aktualnych danych przy każdym otwarciu dashboardu.
- Kafelek **„Dane na: …”** z `MAX(created_at)` jako dowód aktualności.
- Opcjonalnie później: aplikacja Streamlit robiąca to samo z Pythona.

### Struktura kodu

- `bq_utils.py` — wspólne ustawienia (`PROJECT_ID`, `DATASET`, `MAX_BYTES`), `client` i `run_query()`; każdy skrypt importuje: `from bq_utils import client, run_query, DATASET`.
- `client.get_table()` — darmowe metadane tabeli (liczba wierszy, rozmiar, schemat).
- f-string dopuszczalny dla nazw tabel/kolumn z metadanych; parametry `@...` tylko dla wartości.

### Automatyczny monitoring świeżości danych

- `03_freshness_log.py` — sprawdza `COUNT(*)`, `MIN/MAX(created_at)` w tabelach źródłowych i dopisuje wynik (`checked_at`, `lag_minutes`) do `thelook-analytics-512312.monitoring.data_freshness`.
  - Zbiór `monitoring` w lokalizacji **US** (jak dane publiczne — umożliwia łączenie w jednym zapytaniu).
  - Zapis przez load job `load_table_from_dataframe` z `WRITE_APPEND` (dopisuje, nie nadpisuje).
- Harmonogram: **GitHub Actions** (`.github/workflows/freshness.yml`), codziennie 05:17 UTC + ręczne uruchomienie (`workflow_dispatch`). Pełni rolę lekkiego orkiestratora (odpowiednik Airflow z oferty).
- Logowanie w GitHub Actions: konto usługi GCP z rolami BigQuery Job User + BigQuery Data Editor; klucz JSON tylko jako sekret `GCP_SA_KEY` — **nigdy w repozytorium**.
- Uwaga sandbox: tabele we własnych zbiorach wygasają domyślnie po 60 dniach.

Status (2026-10-22): **działa ✅** — repo na GitHubie, konto usługi `github-freshness`, sekret `GCP_SA_KEY`, pierwsze ręczne uruchomienie zakończone sukcesem (ok. 47 s). Od teraz uruchamia się codziennie o 05:17 UTC.
- Wersja Pythona w workflow = wersja lokalna (3.15; w razie braku na runnerze → 3.14).
- Akcje podbite do wersji na Node 24: `actions/checkout@v6`, `actions/setup-python@v6`, `google-github-actions/auth@v3` (ostrzeżenie o wycofaniu Node 20).
- Klucz JSON wykluczony w `.gitignore` wzorcem `thelook-analytics-*.json`.

Jak runner loguje się do BigQuery (dla przypomnienia): akcja `auth` zapisuje klucz z sekretu do pliku tymczasowego i ustawia `GOOGLE_APPLICATION_CREDENTIALS` → biblioteka znajduje go przez Application Default Credentials (lokalnie zamiast tego używa logowania z `gcloud`, więc ten sam kod działa w obu miejscach) → podpisuje prośbę kluczem prywatnym i dostaje token dostępu ważny ok. 1 h → BigQuery sprawdza role konta w IAM (brak roli = 403).

**Do zrobienia później — logowanie bez klucza (Workload Identity Federation):**
- Problem: klucz JSON jest ważny bezterminowo; wyciek = dostęp do projektu do czasu ręcznego usunięcia klucza.
- Rozwiązanie: GitHub przy każdym uruchomieniu wystawia jednorazowy, podpisany token tożsamości (OIDC) dla konkretnego repozytorium; Google skonfigurowany, by mu ufać, wymienia go na krótkotrwały token. Żaden klucz nie jest przechowywany.
- Po wdrożeniu: usunąć sekret `GCP_SA_KEY` i klucz konta usługi w GCP; w `freshness.yml` zamienić `credentials_json` na `workload_identity_provider` + `service_account` w akcji `google-github-actions/auth`.
- Wartość na rozmowę: znajomość obu podejść i wiedza, dlaczego to drugie jest bezpieczniejsze.

## Następne kroki

1. Zamknąć A6: PR `eda-a6-events-funnel` → `main` (squash merge), `git branch -D`, `git fetch --prune`.
2. Część B: widoki w BigQuery (zbiór we własnym projekcie, lokalizacja US) na kluczowe KPI z EDA + dashboard w Looker Studio w stylu szablonu użytkownika (zielony akcent, białe karty) z kafelkiem „Dane na: …”.
   Kandydaci do memo z EDA: (a) budżet pod zysk brutto / POAS, nie przychód (A3); (b) aktywacja bazy zarejestrowanych — retargeting / CRM (A4); (c) ROAS po stratach: × 0,69 (A5); (d) anulowania > zwroty — zapobiegać przed wysyłką (A5); (e) wspólny słownik kanałów przed atrybucją (A6).
   (Lekcje z `01_channel_value`: `COALESCE(..., 0)` dla użytkowników bez zakupów; warunki filtrujące tabelę dołączaną w `ON`, nie w `WHERE`; przedziały ufności.)
3. `docs/kpi.md`, uzupełnienie README.
4. Potem: Streamlit (opcjonalnie), memo dla stakeholdera, agent AI (etap 6 z mapy projektu).
