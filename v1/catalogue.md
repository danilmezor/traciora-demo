# Demo seed v1: catalogue, parc and mix

Drafted 2026-11-13 and brought to the ledger in the reconcile pass of the same day: where a number here is a ledger row, `ledger.json` holds it and `checks/check_files.py` fails on a difference. Files beside this one: `catalogue.json` (10 categories, 70 jobs), `parc.json` (78 models EN, 78 RU), `mix.json` (mix, curves, proposed ledger rows), `checks/check_catalogue.py` with its output `checks/catalogue_check.txt`. English prices are before sales tax; Russian prices, list and company-account, hold the VAT from 2025-01-01 for every customer, an account billed on terms included: the price is what is paid, nothing is added on top, and the amount before VAT is the price / 1.05 (ledger `tax.ru_price_basis`). The rows at the end were proposals; the ledger's decision on each is in its `mixrow.*` rows.

## How a price is built

| | English | Russian |
|---|---|---|
| Posted labour hour, before and after the last rise (P: the first Monday on or after T-150 days) | 125.00 -> 135.00 USD | 1 760 -> 1 900 RUB |
| Company-account hour | 112.50 -> 121.50 USD | 1 580 -> 1 700 RUB |
| Earlier rises of the posted hour (company-account hour) | none in the 24 months | 1 500 (1 350) from T-24 months; 1 620 (1 460) from the first open day on or after T-18 months; 1 760 (1 580) from the first full open day on or after T-335 days |
| Parts, fluids, tyres, fees and sublet before T | 3 % lower for each year back | 12 % lower for each year back |
| Labour of a job | hours x the hour, or a menu price (oil service, rotation, alignment, inspections) | нормо-часы x the hour, or a fixed price (шиномонтаж, сход-развал, диагностика) |
| Parts | gross margin 60 / 56 / 48 % by tier, tyres 22 %, batteries 40 %; weighted 51.1 % | markup 50 / 40 / 30 % by tier, tyres 15 %, batteries 25 %; weighted margin 30.2 % |
| Tiers sold (economy / standard / premium) | 25 / 55 / 20 % | 40 / 42 / 18 % |
| Shop supplies | 5 % of hourly labour, at most 35 USD | 3 % of hourly work, at most 500 RUB |
| Tax | sales tax on parts, labour, fees and shop supplies, added to the bill: 9.25 % at `main` and `east` (Chattanooga), 9.75 % at `west` (Nashville) (ledger `tax.rate.main`, `.east`, `.west`) | VAT 5 % inside every price on bills dated from 2025-01-01, none before; nothing is added; an account's счёт and УПД show the amount before VAT, the VAT and the total as separate figures (ledger `tax.ru_price_basis`) |
| Rounding | list prices to the cent; a company-account price is the list price x 0.9 to the cent | list prices to 10 RUB; a company-account price is the list price x 0.9 with kopecks kept, not rounded to 10 RUB again (ledger `price.company_rounding`) |
| Vehicle class (car / suv / truck / van) | hours x 1 / 1.15 / 1.25 / 1.3 on heavy jobs; parts x 1 / 1.15 / 1.3 / 1.3 | hours x 1 / 1.15 / 1.3 / 1.3; parts x 1 / 1.35 / 1.7 / 1.3 |

A rise moves labour only: the hour and every menu labour price (8 % at P in the English configuration, 7.95 % in the Russian). Parts follow cost and drift by the year. `catalogue.json` carries the history: `price_history` holds the hour by date, the drift and the rule, and every job's `labour_price.history` holds its labour price in each period, so a job's price on any date of the history can be computed.

## Categories and the mix

Share of orders counts an order under its lead job; revenue is at list price.

| Category | Jobs | EN orders | EN revenue | RU orders | RU revenue |
|---|---:|---:|---:|---:|---:|
| Maintenance / Техническое обслуживание | 10 | 34.4 % | 18.4 % | 27.9 % | 25.9 % |
| Brakes / Тормозная система | 8 | 13.1 % | 22.6 % | 8.6 % | 12.6 % |
| Tires & alignment / Шиномонтаж и сход-развал | 9 | 9.1 % | 8.6 % | 15.7 % | 7.9 % |
| Diagnostics / Диагностика | 4 | 14.8 % | 5.2 % | 11.6 % | 2.5 % |
| Suspension & steering / Ходовая часть и рулевое управление | 9 | 6.9 % | 15.3 % | 12.8 % | 18.1 % |
| Air conditioning / Кондиционер | 6 | 5.1 % | 5.5 % | 3.4 % | 3.9 % |
| Battery & electrical / АКБ и электрооборудование | 5 | 6.7 % | 6.0 % | 5.6 % | 7.9 % |
| Engine & cooling / Двигатель и система охлаждения | 11 | 6.1 % | 11.5 % | 8.3 % | 11.6 % |
| Transmission & driveline / Трансмиссия и привод | 6 | 2.5 % | 6.5 % | 4.8 % | 9.2 % |
| Inspections / Осмотры и проверки | 2 | 1.4 % | 0.4 % | 1.2 % | 0.3 % |

| | English | Russian |
|---|---|---|
| Priced jobs per order, mean | 2.62 | 2.37 |
| Orders with 1 / 2 / 3 / 4 / 5+ jobs | 20 % / 32 % / 26 % / 14 % / 8 % | 26 % / 35 % / 24 % / 11 % / 5 % |
| Orders on which work is recommended | 65 % | 60 % |
| Recommended jobs on such an order; share sold (ledger `sold.company`) | 3.1; 53.73 % | 3.1; 53.34 % |
| Recommended jobs sold per order | 1.08 | 1.00 |
| Declined work per order, at list | 217.15 USD | 4 518 RUB |
| Free courtesy inspection, share of orders | 80 % | 70 % |

## The twenty most common jobs

Hours and price for vehicle class car, standard parts, today's list: English before sales tax, Russian as paid, VAT inside. Share = orders that carry the job.

| Job, as written on the order (EN / RU) | EN hours | EN price, USD | EN share | RU н/ч | RU price, RUB | RU share |
|---|---:|---:|---:|---:|---:|---:|
| Full synthetic oil & filter change / Замена масла в двигателе и масляного фильтра | 0.5 | 90.95 | 31.9 % | 0.7 | 6 700 | 24.4 % |
| Replace engine air filter / Замена воздушного фильтра двигателя | 0.2 | 53.14 | 12.5 % | 0.2 | 1 530 | 17.0 % |
| Replace cabin air filter / Замена салонного фильтра | 0.3 | 64.36 | 10.5 % | 0.3 | 1 660 | 15.0 % |
| Tire rotation / Перестановка колёс по схеме (4 шт.) | 0.3 | 25.00 | 23.4 % | 0.4 | 760 | 0.5 % |
| Four-wheel alignment / Регулировка углов установки колёс (сход-развал), две оси | 1.0 | 119.95 | 9.7 % | 1.0 | 3 000 | 10.4 % |
| Check engine light - scan, test & diagnose (1 hr) / Компьютерная диагностика двигателя: считывание и анализ ошибок | 1.0 | 135.00 | 11.4 % | 0.5 | 1 200 | 8.3 % |
| Steering & suspension inspection - noise / vibration / Диагностика ходовой части | 0.5 | 49.95 | 4.3 % | 0.4 | 800 | 12.9 % |
| Replace front brake pads & rotors / Замена передних тормозных дисков и колодок | 1.8 | 493.00 | 9.6 % | 1.8 | 12 520 | 5.1 % |
| Battery, starting & charging system test / Проверка АКБ и системы зарядки нагрузочной вилкой | 0.1 | 0.00 | 9.2 % | 0.2 | 300 | 3.8 % |
| Brake system inspection / Диагностика тормозной системы | 0.5 | 49.95 | 7.1 % | 0.4 | 700 | 4.8 % |
| Brake fluid flush / Замена тормозной жидкости с прокачкой системы | 1.0 | 151.00 | 6.9 % | 1.0 | 2 480 | 4.2 % |
| Replace front sway bar links (pair) / Замена стоек стабилизатора передних (2 шт.) | 0.8 | 194.36 | 3.2 % | 0.8 | 3 700 | 7.4 % |
| Replace wiper blades (pair) / Замена щёток стеклоочистителя | 0.1 | 47.73 | 7.0 % | 0.1 | 2 570 | 2.5 % |
| Fleet PM service A - cargo van (oil & filter, chassis lube, 50-point inspection) / ТО коммерческого автомобиля: замена масла и фильтров, смазка, осмотр по чек-листу | 1.5 | 270.59 | 5.4 % | 1.5 | 9 710 | 4.1 % |
| Replace spark plugs / Замена свечей зажигания (4 шт.) | 1.0 | 222.28 | 4.1 % | 0.6 | 4 060 | 5.1 % |
| Scheduled maintenance service (30K / 60K / 90K) - inspect, adjust, lubricate / Техническое обслуживание по регламенту: контрольно-осмотровые и смазочные работы | 1.8 | 243.00 | 4.2 % | 1.5 | 2 850 | 4.4 % |
| Replace battery, clean terminals / Замена аккумуляторной батареи | 0.3 | 239.95 | 5.2 % | 0.2 | 8 760 | 3.3 % |
| Replace rear brake pads & rotors / Замена задних тормозных дисков и колодок | 1.8 | 470.27 | 6.6 % | 1.8 | 11 260 | 1.6 % |
| Electrical system diagnosis / Поиск неисправности электрооборудования | 1.5 | 202.50 | 3.9 % | 1.5 | 2 850 | 3.6 % |
| Seasonal tire changeover - dismount, mount & balance 4 / Сезонная замена шин: шиномонтаж 4 колёс с балансировкой | 1.0 | 100.00 | 0.1 % | 1.2 | 3 000 | 7.3 % |

Story jobs outside the twenty: timing belt with kit and pump 720.00 USD (3.2 h; 688.00 at the hour before the rise) and 16 000 RUB (15 552 at the hour before the rise); rear shock absorbers, pair, 339.28 USD and 11 720 RUB; seasonal tyre storage 3 000 RUB a season; pre-purchase inspection 149.95 USD and 3 000 RUB; fleet PM for a van 270.59 USD and 9 710 RUB. The S6 pad is a fictional brand on purpose (Calder ValueStop / BREMHOF), 39.00 USD and 1 250 RUB a set.

## Seasonal, weekday and hour curves

Index of orders per open day, yearly mean 1.

| | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| EN all orders | 0.98 | 0.96 | 0.98 | 1.00 | 1.04 | 1.05 | 1.04 | 1.02 | 0.97 | 0.97 | 1.00 | 0.98 |
| EN air conditioning | 0.15 | 0.15 | 0.45 | 0.84 | 1.89 | 2.48 | 2.48 | 2.09 | 0.90 | 0.30 | 0.10 | 0.10 |
| EN battery jobs | 1.45 | 1.10 | 0.80 | 0.70 | 0.70 | 0.85 | 0.95 | 0.90 | 0.75 | 1.00 | 1.50 | 1.30 |
| RU all orders | 0.67 | 0.87 | 0.89 | 1.35 | 1.24 | 0.99 | 0.95 | 0.92 | 0.89 | 1.29 | 1.08 | 0.85 |
| RU tyres and alignment | 0.24 | 0.28 | 0.33 | 2.94 | 1.85 | 0.40 | 0.37 | 0.35 | 0.35 | 2.92 | 1.65 | 0.28 |
| RU air conditioning | 0.05 | 0.05 | 0.20 | 0.89 | 2.58 | 2.88 | 2.58 | 1.69 | 0.60 | 0.20 | 0.10 | 0.10 |
| RU battery jobs | 1.50 | 1.25 | 0.95 | 0.75 | 0.65 | 0.65 | 0.65 | 0.70 | 0.85 | 1.10 | 1.40 | 1.55 |

- Russian tyre windows: 13 April to 10 May and 13 October to 9 November, seasonal tyre jobs at 6.0 times their yearly mean, a shoulder week either side at 0.5. Inside a window the shops open 1.64 times their mean daily orders.
- English seasons against the mean: winter -2.4 %, spring +0.7 %, summer +3.5 %, autumn -1.9 %.
- Weekday, EN: Mon 1.12, Tue 1.02, Wed 0.96, Thu 0.94, Fri 0.96; Saturday morning at main 0.30 of a weekday. RU: Mon 0.98, Tue 1.05, Wed 1.02, Thu 1.00, Fri 1.03, Sat 1.10, Sun 0.82.
- Arrivals by hour, EN: 07:30 16 %, 08:00 24 %, 09:00 13 %, 10:00 9 %, 11:00 7 %, 12:00 6 %, 13:00 7 %, 14:00 7 %, 15:00 6 %, 16:00 4 %, 17:00 1 %. RU: 09:00 15 %, 10:00 12 %, 11:00 10 %, 12:00 9 %, 13:00 8 %, 14:00 8 %, 15:00 8 %, 16:00 8 %, 17:00 9 %, 18:00 9 %, 19:00 4 %.

## The check

| Ledger row | EN computed | EN target | RU computed | RU target |
|---|---:|---:|---:|---:|
| Billed hours per order | 2.48 (-0.9 %) | 2.5 | 2.21 (+0.3 %) | 2.2 |
| Labour per order | 286.73 (-0.1 %) | 286.9 | 4 238 (+1.4 %) | 4 180 |
| Parts and other per order | 236.33 (+0.6 %) | 235 | 7 855 (+0.7 %) | 7 800 |
| Average order | 523.06 (+0.2 %) | 521.9 | 12 093 (+0.9 %) | 11 980 |
| Average order at main / east / west, at each shop's sold share | 512.8 / 566.6 / 490.8 | 511.6 / 565.4 / 489.6 | 11 883 / 12 939 / 11 515 | 11 770 / 12 826 / 11 402 |
| Effective labour rate | 85.7 % | 85 % | not used | |
| Age of a drawn car, mean | 12.8 years | 12.8 | 13.6 years, 69 % over ten | over 15; 69 % |

Every row is inside 2 % except one gap left open on purpose: the Russian mean age (see open points). The targets are ledger rows; the realisation factor (0.9585 and 0.9594) uses the ledger's company-account share of sales (5.53 % and 5.55 %) and comeback share (2.64 % and 2.55 %).

## Ledger rows proposed

Class: M measured, D derived, X designed. Basis and check for each row are in `mix.json`, `ledger_rows_proposed`.

| Row | English | Russian | Class |
|---|---|---|---|
| job mix: share of orders by category of the lead job | see the categories table | see the categories table | X |
| job mix: share of revenue by category | see the categories table | see the categories table | D |
| jobs per order, priced | mean 2.62 | mean 2.37 | D |
| orders that carry recommended work | 65.0 % | 60.0 % | X |
| recommended jobs on such an order | 3.09 | 3.14 | D |
| seasonal curve by month, all orders (index of orders per open day) | see the table above | see the table above | D |
| seasonal curve: air conditioning | see the table above | see the table above | X |
| seasonal curve: battery jobs | see the table above | see the table above | X |
| seasonal tyre windows | none (the three seasonal tyre jobs together are under 0.2 % of orders) | 13 April to 10 May and 13 October to 9 November at 6.0 times the yearly mean, a shoulder week either side at 0.5, 0.053 otherwise | X |
| seasonal tyre jobs as a share of orders | 0.2 % | 10.2 % | X |
| weekday curve | see above | see above | X |
| hour-of-day curve of arrivals | see above | see above | X |
| parts tier mix (economy / standard / premium) | 25 / 55 / 20 % | 40 / 42 / 18 % | X |
| parts gross margin, tier-weighted | 51.1 % | 30.2 % | M / X |
| labour rate before the rise | 125.00 USD | 1 760 RUB before the last rise; 1 500 and 1 620 before the two earlier ones | D |
| company-account labour rate | 121.50 USD (112.50 before) | 1 700 RUB (1 580 before the last rise; 1 350 and 1 460 earlier) | X |
| shop supplies | 5 % of hourly labour, at most 35 USD an order | 3 % of hourly work, at most 500 RUB an order | X |
| discounts and coupons, share of sales | 1.0 % | 1.0 % | X |
| menu pricing: labour at list over billed hours x posted hour | 0.894 | 1.054 | D |
| parts sent back to the supplier | 6 % (ledger) | 4 % | X |
| vehicle classes of customers' cars (car / suv / truck / van) | 52.6 % / 19.9 % / 21.5 % / 5.9 % | 60.9 % / 27.6 % / 4.1 % / 7.4 % | D |
| age of customers' cars | mean 12.8 years | mean 13.6 years, 69.0 % older than ten | M / X |

## Points raised with the controller, and how each was settled

1. **S8 against the 8 % rise.** 640 -> 720 USD is +12.5 %. With labour up 8 % the job goes 688 -> 720; with the whole price up 8 %, 667 -> 720. Settled as (A): the stale page carries the old hour and today's parts, so the newcomer quoted 688 (ledger `s8.price_quoted`); the 640 is gone.
2. **S8's bill of 742 USD** is read as 720 + 21.60 shop supplies before sales tax (810.20 with tax). The Russian amounts are 16 000 now, 15 552 quoted and 1 800 off (ledger `s8.*`); the first draft's 14 200 is gone.
3. **Russian car age.** The design asks for over fifteen years (the whole parc); cars seen at independent services average 12.7 (Fit Service). With 69 % older than ten, the cars drawn here average 13.6. Over 15 is out of reach with the models such a shop sees: 28 % of them did not exist fifteen years ago, and the mean tops out at 14.7 with implausible weights. Proposed: accept 13.6.
4. **Ledger readings taken.** The posted hour (135 USD, 1 900 RUB) is today's, after the rise. The ledger's 'parts' bucket holds everything that is not labour: parts, fluids, tyres, fees, shop supplies, sublet. The Russian labour target is 2.2 x 1 900 = 4 180.
5. **Tyre window against S11.** Six times the mean for four weeks with seasonal tyre jobs at 10.2 % of orders gives 1.64 times the usual daily orders; S11 says calls rise 40 %.
6. **Part numbers.** Of 361 part options, 14 carry a number seen on retailer listings in this pass, 49 a number recalled from memory and not re-checked, 224 a styled number, 66 none (sold by description), 8 the fictional S6 brand. The legend is in `catalogue.json`. None was read in a brand's own catalogue.
