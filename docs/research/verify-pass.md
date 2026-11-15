# Verify pass: legal, tax and benchmark facts of seed v1 (2026-11-13/14)

Status words: **verified** (page read, sentence on it), **corrected** (page read, the seed says something else), **open** (not settled; what was tried). "Snippet only" marks a search-result summary, never presented as read. Pages were read through a fetch tool that returns excerpts and quotes; where the tool split a long sentence, the parts are joined with "…". Web queries named no person, company, project or seed address. Not legal advice: a lawyer reads the clause before any page is shown as legal guidance.


## 1. Russia: VAT in retail prices, documents, return, advances

| Fact | Status | Source (version) | Sentence |
|---|---|---|---|
| Sales to the public at retail prices: VAT is inside the price; not shown separately on price tags | verified | НК РФ ст. 168 п. 6, https://legalacts.ru/kodeks/NK-RF-chast-2/razdel-viii/glava-21/statja-168/ (НК ч. 2 ред. от 04.08.2026) | «соответствующая сумма налога включается в указанные цены (тарифы)»; «на ярлыках товаров и ценниках, выставляемых продавцами, сумма налога не выделяется» (the tax is included in those prices; it is not shown separately on labels and price tags) |
| Retail for cash: the cash receipt replaces the invoice | verified | same, п. 7 | requirements of п. 3 and 4 «считаются выполненными, если продавец выдал покупателю кассовый чек или иной документ установленной формы» (are met if the seller gave the buyer a cash receipt or another document of the set form) |
| The cash receipt carries the VAT rate (incl. 5 % and 7 %) | verified | ФНС news, 2024-11-19 (archived), https://www.nalog.gov.ru/rn03/news/activities_fts/15418336/ | required receipt data «к числу которых также относится налоговая ставка по налогу на добавленную стоимость»; draft order adds «новых ставок НДС 5% и 7 %» (receipt data include the VAT rate; new rates 5 % and 7 %) |
| Advance receipt with a "payment method" attribute (предоплата / аванс) | open | ст. 4.7 of 54-ФЗ: legalacts URL 404; consultant.ru (cons_doc_LAW_42359) seen as snippet only: the law lists «признак расчета»; the "payment method" attribute (tag 1214) comes from ФНС formats and letter АБ-4-20/4418@ of 2021-04-02 (snippet only) | — |
| Invoice to a legal entity within 5 calendar days of shipment or of payment received | verified | НК ст. 168 п. 3 (same page) | счета-фактуры выставляются «не позднее пяти календарных дней» from shipment or receipt of payment (paraphrase by the fetch tool; the five days quoted) |
| A company on the simplified system paying VAT issues invoices, incl. on advances; keeps a sales book; files a VAT return | verified | ФНС page "НДС при УСН", updated 2026-08-05, https://www.nalog.gov.ru/rn05/taxation/taxes/nds_usn/ | «при получении авансов выставляются соответствующие счета-фактуры не позднее 5 календарных дней»; «возникает обязанность вести книгу продаж и представить налоговую декларацию по НДС» |
| Invoice form: updated forms and filling rules (ПП № 1137 as amended by ПП № 26 of 2026-01-23) in force from 2026-04-01; ФНС had recommended them from 2026-01-01 | verified on a secondary page | Главная книга news, 2026-03-19, https://glavkniga.ru/news/20631 | «С 1 апреля официально вступит в силу новая форма счета-фактуры»; the resolution «вступит в силу с 01.04.2026»; forms «учитывают поправки в НК, которые уже работают с 01.01.2026» |
| Electronic format 5.03 of invoice and УПД (ФНС order ЕД-7-26/970@ as amended by ЕД-7-26/1032@) the only format from 2025-04-01; УПД is a ФНС-recommended combined form, not a Tax Code form | open (snippet only) | search summaries of buhexpert8, saby, spmag | — |
| VAT tax period is the quarter | verified | НК ст. 163, https://legalacts.ru/kodeks/NK-RF-chast-2/razdel-viii/glava-21/statja-163/ | налоговый период «устанавливается как квартал» (the tax period is set as the quarter) |
| Return due by the 25th of the month after the quarter | verified | НК ст. 174 п. 5, https://legalacts.ru/kodeks/NK-RF-chast-2/razdel-viii/glava-21/statja-174/ (ред. от 04.08.2026) | «обязаны представить в налоговые органы по месту своего учета соответствующую налоговую декларацию» … «в срок не позднее 25-го числа месяца, следующего за истекшим налоговым периодом». The electronic-only clause of the same sentence was not in the excerpt. |
| VAT on an advance at the rate 5/105 under the 5 % regime | verified | ФНС page above; НК ст. 164 п. 4 (legalacts, ред. от 04.08.2026) | «применив расчетную ставку в размере 5/105% или 7/107% (при применении специальной ставки НДС)»; ст. 164 п. 4: the rate applies «при получении оплаты, частичной оплаты в счет предстоящих поставок товаров», as a percentage of a base «принятой за 100 и увеличенной на соответствующий размер налоговой ставки» |

Seed impact. Ledger `s7.bill` and `s8.paid_with_tax` (5 % added on top of the list price for a private customer) contradict ст. 168 п. 6. This confirms the controller's PENDING decision (Russian list prices are what the private customer pays, VAT inside). KB pages `customers/prices-for-common-services.md` and `policies/documents-and-vat.md` («без НДС» for private customers) change with it. `accounts/company-account-terms.md` and `policies/documents-and-vat.md` (invoice or УПД to a company account) stand: invoice within five days, on shipment and on advances. `office/month-end-close.md` (quarterly return, sales book) stands; the page can say "by the 25th of the month after the quarter".

## 2. Russia: simplified system and VAT thresholds

| Fact | Status | Source | Sentence |
|---|---|---|---|
| Simplified-system companies are VAT payers from 2025-01-01 | verified | ФНС page "НДС при УСН" (2026-08-05) | «С 01.01.2025 все организации и индивидуальные предприниматели, применяющие УСН, являются налогоплательщиками НДС.» (From 2025-01-01 all companies and sole traders on the simplified system are VAT payers.) |
| Before 2025-01-01 they were not VAT payers (except imports and agent cases) | verified by implication only | same sentence; the old text of НК ст. 346.11 п. 2 and the amending law (176-ФЗ of 2024-07-12) were not read | — |
| 2025: exempt with 2024 income up to 60 mln; 5 % with 2024 income up to 250 mln | verified | same ФНС page | «с 01.01.2025 при сумме доходов за 2024 год до 60 млн руб. (включительно)»; 5 %: «сумма доходов за 2024 не превысила в совокупности 250 миллионов рублей» |
| 2025: 7 % up to 450 mln | verified (base figure) | НК ст. 164 п. 8, https://legalacts.ru/kodeks/NK-RF-chast-2/razdel-viii/glava-21/statja-164/ | 5 %: «не превысила в совокупности 250 миллионов рублей»; 7 %: «не превысила в совокупности 450 миллионов рублей»; indexed «в порядке, предусмотренном пунктом 2 статьи 346.12» |
| 2026: exempt below 20 mln (2025 income and during 2026); 5 % from 20 to 272.5 mln; 7 % from 272.5 to 490.5 mln; deflator 1.090 | verified | ФНС leaflet «Налоговая реформа для УСН с 01.01.2026», PDF dated 2025-12-26, https://data.nalog.ru/files/media/usn_01012026.pdf | «5% … при доходе в 2026 — от 20 до 272.5 млн ₽»; «7% … при доходе в 2026 — от 272.5 до 490,5 млн ₽»; «Освобождение от НДС: доход менее 20 млн ₽ за 2025 год и в течение 2026 года»; «на 2026 год коэффициент-дефлятор = 1,090»; «Плательщики УСН являются налогоплательщиками НДС» |
| Exemption threshold path: 20 mln for 2025–2028, 15 mln for 2029, 10 mln from 2030 | verified | НК ст. 145 п. 1 (legalacts, ред. от 04.08.2026) | «20 миллионов рублей за 2025 - 2028 годы, 15 миллионов рублей за 2029 год»; «10 миллионов рублей за 2030 год и последующие годы» |
| General VAT rate 22 % from 2026 (20 % before) | verified | ФНС leaflet above | «22%, 10% (до 2026: 20% и 10%)» |

Seed impact. `tax.rate` ru 5 and its note "5 % up to 272.5 million" are right for 2026; the note should name both years (250 mln in 2025, 272.5 mln in 2026) and the exemption (60 mln in 2025, 20 mln in 2026). `tax.ru_vat_from` 2025-01-01 is right; its class can become measured. Company income `volume.revenue_year.company` 121.76 mln RUB is inside the 5 % band in 2026. For 2025 the company needs 2024 income above 60 mln: in 2024 only main and east traded (west was bought 14 months before T), at lower prices; the controller should confirm the seeded 2024 income of main and east tops 60 mln, or the 2025 bills carry no VAT.

## 3. Russia: car repair rules (ПП № 780) and consumer law

Second source for ПП № 780: КонсультантПлюс, edition «ред. от 27.10.2025» (amended by ПП № 1670 of 2025-10-27, per government.ru/publication.pravo.gov.ru search results; which points it changed was not read), https://www.consultant.ru/document/cons_doc_LAW_506689/3409fcd416ac8943d31abf977818ecdd873f3c5d/ . base.garant.ru served corrupted text.

| Fact | Status | Sentence (consultant.ru) |
|---|---|---|
| Заказ-наряд named only among sample documents the shop shows | verified (2 sources) | п. 4: «образцы договоров на оказание услуг (далее - договоры), заказов-нарядов» |
| Written contract with dates and term | verified (2 sources) | п. 9: «Договор заключается в письменной форме и должен содержать следующие сведения:» … «дата заключения договора, сроки его исполнения» |
| Warranty only if set | verified (2 sources) | п. 9: «гарантийные сроки на результаты оказания услуг, если они установлены;» |
| Customer-supplied parts listed in the contract | verified | п. 9: «перечень запасных частей и материалов, предоставленных потребителем,» «с указанием информации об обязательном подтверждении их соответствия» |
| Check-in act with the contract; one copy each to the customer | verified (2 sources) | п. 12: «исполнитель обязан одновременно с договором составить приемо-сдаточный акт»; «Потребителю выдается по одному экземпляру договора и приемо-сдаточного акта.» |
| Unfit customer parts: warn, stop; may terminate if not replaced | verified (2 sources) | п. 14: «обнаружения непригодности или недоброкачественности запасных частей и материалов, полученных от потребителя»; п. 15: «в разумный срок не заменит непригодные или недоброкачественные запасные части и материалы» |
| Rules in force 2025-09-01 to 2031-09-01 | verified (search result quoting the act; first pass read п. 4) | «Правила … действуют до 1 сентября 2031 г.» |
| Defect in work: removed in a reasonable term set by the consumer | verified | ЗоЗПП ст. 30, https://legalacts.ru/doc/ZZPP/glava-iii/statja-30/ (ред. от 28.12.2025, с изм. от 27.10.2026): «Недостатки работы (услуги) должны быть устранены исполнителем в разумный срок, назначенный потребителем.» |
| Ten days to satisfy price-reduction, cost-of-repair, refund and loss claims | verified (first pass; not re-read) | ЗоЗПП ст. 31 п. 1 |
| Refusal at any time paying actual expenses | verified (first pass; not re-read) | ЗоЗПП ст. 32 |

The rules state no term for answering a written claim; the ten days are the law's term for satisfying the listed demands (ст. 31). KB pages already say this.

The four "corrected" items in TO-VERIFY.md (body-work warranty on two pages, cast biographies, rack subcontractor) are seed-internal consistency fixes, not facts on any web page; there is nothing to second-source.

## 4. Russia: labour facts (staff handbook, payroll, safety)

ТК РФ on legalacts.ru, «ред. от 25.05.2026».

| Fact | Status | Sentence |
|---|---|---|
| Pay at least every half month, within 15 days of the period's end | verified | ст. 136: «Заработная плата выплачивается не реже чем каждые полмесяца.»; «не позднее 15 календарных дней со дня окончания периода, за который она начислена» |
| 28 calendar days of annual leave | verified | ст. 115: «Ежегодный основной оплачиваемый отпуск предоставляется работникам продолжительностью 28 календарных дней.» |
| One part of split leave at least 14 days | verified | ст. 125: «При этом хотя бы одна из частей этого отпуска должна быть не менее 14 календарных дней.» |
| Leave schedule "drawn up in December" | corrected (wording) | ст. 123: approved «не позднее чем за две недели до наступления календарного года» (no later than two weeks before the calendar year). Say "approved by mid-December at the latest". |
| Holiday or day-off work: at least double, or single pay plus an unpaid day off at the employee's wish | verified | ст. 153: «Работа в выходной или нерабочий праздничный день оплачивается не менее чем в двойном размере»; «В этом случае работа … оплачивается в одинарном размере» «а день отдыха оплате не подлежит». The day off is the employee's choice. |
| Прогул = absence over four hours in a row; ground for dismissal | verified | ст. 81 ч. 1 п. 6 «а»: «прогула, то есть отсутствия на рабочем месте без уважительных причин в течение всего рабочего дня (смены)» … «а также в случае отсутствия на рабочем месте без уважительных причин более четырех часов подряд» |
| Two weeks' written notice by the employee | verified | ст. 80: «предупредив об этом работодателя в письменной форме» «не позднее чем за две недели, если иной срок не установлен» |
| "The order замечание then выговор" | corrected | ст. 192 lists «замечание; выговор; увольнение по соответствующим основаниям» and requires that «тяжесть совершенного проступка» be weighed; it sets no order. A company ladder may use this order, but not as a legal rule. |
| Repeated safety briefing at least every 6 months; every 3 months in the first year for first-time workers on hazardous work | verified | ПП № 2464 of 2021-12-24, ред. от 30.06.2026, https://legalacts.ru/doc/postanovlenie-pravitelstva-rf-ot-24122021-n-2464-o-porjadke/ , Правила п. 14: «Повторный инструктаж по охране труда проводится не реже одного раза в 6 месяцев.» «Для работников, впервые начавших трудовую деятельность, допущенных к выполнению работ повышенной опасности,» «повторный инструктаж … не реже одного раза в 3 месяца в течение первого года работы.» The rules now run «до 1 сентября 2032 г.» (extended by ПП № 805 of 2026-06-30, in force 2026-08-31, read on kontur-extern.ru). |

## 5. Russia: traffic rules

| Fact | Status | Source | Sentence |
|---|---|---|---|
| Tread depth, tyres without wear indicators, M1/N1/O1/O2: 1.6 mm | verified, citation corrected | ПДД (ПП № 1090, ред. от 28.08.2026), Перечень неисправностей п. 5.4, https://www.consultant.ru/document/cons_doc_LAW_2709/ec034e2d80085428905b10189ee7d0d08173e8c7/ | «для транспортных средств категорий M1, N1, O1, O2 - 1,6 мм;» (the point bars residual depth of no more than that value). Applies to any tyre, not only summer ones. |
| Winter tyres on snow or ice: 4 mm and less is a fault | verified, citation corrected | same, п. 5.5 | «Остаточная глубина рисунка протектора зимних шин … составляет 4 мм и менее.» |
| Winter tyres mandatory December–February on M1 and N1 | verified | same, п. 5.2 | «На транспортном средстве категорий M1 и N1 не установлены зимние шины в зимний период (декабрь, январь, февраль).» |
| Driving-school car must have dual pedals (clutch except automatics, brake), an instructor's mirror and the "Учебное транспортное средство" sign | verified | Основные положения по допуску, п. 5, https://www.consultant.ru/document/cons_doc_LAW_2709/6d8c7fbd95f0b2f282a790182c6d28e791f15e51/ | «Механическое транспортное средство, используемое для обучения вождению, должно быть оборудовано дополнительными педалями» «привода сцепления (кроме транспортных средств с автоматической трансмиссией) и тормоза,» «зеркалом заднего вида для обучающего и опознавательным знаком "Учебное транспортное средство"» |

The first pass cited the 2015 edition (п. 5.1). The list was replaced from 2023-09-01 (ПП № 837 of 2023-05-27, per garant.ru search result); the values are unchanged, the points are now 5.4 and 5.5, and the law's boundary is "4 mm and less" / "1.6 mm and less", so a tyre at exactly 4 mm (winter, on snow) or 1.6 mm fails. KB `services/tires/seasonal-changeover-and-storage.md` says «меньше 4 мм … меньше 1,6 мм на летней»: see changes file.

## 6. Russia: messengers (state on 2026-11-13)

| Fact | Status | Source | Sentence or note |
|---|---|---|---|
| Calls in WhatsApp and Telegram restricted by Роскомнадзор, August 2025 | verified (secondary) | ru.wikipedia «Частичная блокировка Telegram и WhatsApp в России», revision 2026-10-12 (cites Meduza, AP, Guardian of 2025-08-13/14); Men Today 2026-10-20 | «В августе 2025 года ведомство заблокировало голосовые звонки в обоих мессенджерах для борьбы с мошенничеством.» |
| Regional outages from 2025-10-20; РКН admitted «частично ограничил» on 2025-10-22 | verified (secondary) | ru.wikipedia, same revision | the article's own dates for the spread conflict (21 vs 22 October) |
| РКН warned of a possible full WhatsApp block, December 2025 | verified (secondary) | Men Today, 2026-10-20 | «в декабре предупредила о возможности полной блокировки WhatsApp*» |
| whatsapp.com and web.whatsapp.com removed from the national domain system, 2026-02-11/12 | not re-read this pass | ru-shop.md (albato blog, 2026-07-06, read in the earlier pass) | contested: a Business FM report of 2026-03-02 that messages and calls worked again without VPN (snippet only) |
| WhatsApp's owner is designated extremist and banned in Russia | verified (secondary) | Men Today, 2026-10-20 | Meta «признана в РФ экстремистской организацией и запрещена» |
| Telegram slowed from 2026-02-10 by РКН; "final decision" on blocking reported 2026-02-26; full block "in the first days of April" per RBC sources | verified as reported (secondary) | ru.wikipedia (cites RBC); RBC headlines of 2026-02-10 (snippet only) | **Contested / unconfirmed:** no page read confirms that a full Telegram block happened in April 2026 or later; Men Today (2026-10-20) mentions only the February slowdown. |
| Audiences, August 2026 (Mediascope): Telegram 33.8 mln daily, WhatsApp 22.6 mln | snippet only | search summary of Men Today | the read excerpt confirms Mediascope as a source and that Mediascope hid messenger statistics in early October 2026 |
| MAX: national messenger by Federal law № 156-ФЗ of 2025-06-24; platform named by распоряжение № 1880-р of 2025-07-12; mandatory pre-install from 2025-09-01 (распоряжение № 2240-р of 2025-08-19); use of its functions voluntary (Минцифры letter ММ-П10-82860 of 2025-08-27) | snippet only (consultant.ru, garant.ru, government.ru results) | — | none of these pages was opened |
| MAX removed from the App Store in early June 2026 | verified (secondary) | Men Today, 2026-10-20 | «в начале июня 2026 года из App Store удалили отечественный мессенджер «Макс»» |

KB `how-to/chats-and-messages.md`: the status changes month to month and is contested; state no block as fact beyond the call restrictions (2025-08) and the February 2026 slowing of Telegram.

## 7. Road distances

Routing source: OSRM demo server on OpenStreetMap data, https://router.project-osrm.org/route/v1/driving/ , queried 2026-11-14 07:13 UTC, fastest car route.

| Pair | Status | Result | Route |
|---|---|---|---|
| Ульяновск centre (54.3142, 48.4035) to Казань centre (55.7887, 49.1221) | corrected | 225.7 km, 3 h 31 min | Р-241 for 179 km, М-7 14 km, Горьковское шоссе |
| The ledger's two Russian shop coordinates (main to west) | corrected | 223.1 km, 3 h 29 min | same corridor |
| Chattanooga centre (35.0456, -85.3097) to Nashville centre (36.1627, -86.7816) | verified | 133.6 mi (214.9 km), 2 h 34 min | I-24 for 203 km |
| The ledger's two English shop coordinates (main to west) | verified | 140.8 mi, 2 h 41 min | I-24 |

`geo.distance` ru 240 is too long by OSRM (225.7); earlier figures 243 (travel site) and 250.9 (coach route register, between bus stations) were longer still. Proposed: about 225 km by the Р-241. `geo.distance` en 135 matches city to city (133.6); shop to shop is 140.8.

## 8. Tennessee sales tax

| Fact | Status | Source | Sentence |
|---|---|---|---|
| State rate 7 %; local rate 1.50 % to 2.75 %, a multiple of .25 | verified | TN Dept. of Revenue, Sales and Use Tax Manual, August 2026, https://www.tn.gov/content/dam/tn/revenue/documents/tax_manuals/august-2026/sales-use-tax-manual.pdf | "The local option sales and use tax rates vary from 1.50% to 2.75%. The local option tax rate may not exceed 2.75% and must be a multiple of .25." |
| Chattanooga (and Hamilton County) local rate 2.25 % since 2004-07-01: combined 9.25 % | verified | Department's rate table (Streamlined file) TNR2026Q4AUG21.csv linked from https://www.tn.gov/revenue/taxes/sales-and-use-tax/local-sales-tax.html | rows `47,0,065,0.0225,…,20040701,29991231` (Hamilton) and `47,1,14000,0.0225,…,20040701,29991231` (Chattanooga) |
| Nashville/Davidson: local 2.25 % plus a 0.5 % transit surcharge from 2025-02-01: combined 9.75 % | **corrected** | rate map page, https://www.tn.gov/revenue/taxes/sales-and-use-tax/local-sales-tax/local-sales-tax-rates-map.html ; same CSV | "There is an 0.5% local option transit surcharge in Davidson County beginning February 1, 2025. This effectively increases the local sales and food tax rates to 2.75%." CSV: `47,1,52006,0.0225,…` and transit rows `47,79,9195x,0.005,…,20250201,29991231` |
| Repair labour on motor vehicles is taxable, parts and labour | verified | Manual, ch. "Repair of Tangible Personal Property", footnotes: Tenn. Code Ann. § 67-6-205(c)(4); Tenn. Comp. R. & Regs. 1320-05-01-.54 | "Tennessee law imposes sales tax on any repair of any tangible personal property or computer software that is performed in the state."; "All charges for repair services and repairs of any kind of tangible personal property, such as automobiles, including all parts and/or labor, are subject to the sales tax." |
| Local tax only on the first $1,600 of a single article; state single-article tax 2.75 % on $1,600 to $3,200 | verified | Manual, ch. 9 (footnote: Tenn. Code Ann. § 67-6-702(d)) | "The local option tax is applied only to the first $1,600 of the purchase price of any single article of tangible personal property sold."; "The state single article tax rate of 2.75% is applied to the amount of the sales price of a single article of tangible personal property between $1,600 and $3,200." |
| The cap does not apply to taxable services | verified | Manual, ch. 9 | "The single article limitation does not apply to sales of taxable services, amusements, custom computer software, and warranty or maintenance contracts. These sales are subject to the full local option tax." |
| Whether a part sold on a repair order is its own "single article" | open | the Manual does not say it for repair invoices; "Independent units sold in sets … are not considered to be single articles" | Needs a ruling or a Department letter; the seed avoids it with `tax.max_single_part` 1600. |

Seed impact. `tax.rate` en 9.25 "in both cities" holds for Chattanooga (main, east) only; west (Nashville) is 9.75 % for every order dated on or after 2025-02-01, which is the whole of west's history (bought 14 months before T). `location.tax_rate` of west, every west total, and story numbers on west bills change. The ledger note "2026 secondary table (Stripe, read); the state's own table to be read" is settled by the Department's own table.

## 9. US figures marked unverified

| Ledger row / claim | Status | What was tried |
|---|---|---|
| 0.7 technicians per bay, 1 advisor per 3 bays (PartsTech 2025) | open (snippet only) | Search summary repeats it; PartsTech page https://partstech.com/?p=6058 opened: no such figure. The full report is behind a form. No ledger row uses it directly (`site.bays.*` is designed). |
| `calls.inbound_per_order` en note "about 27 calls a day at a shop of 13 cars (OktoRocket 2025, snippet)" | open (snippet only) | Only a secondary article (briefglance) citing "over 800 inbound calls a month … answers only 89%" was found in search; not opened; the vendor report itself was not found. The row is designed, so nothing breaks. |
| `site.open_days` en note "about a quarter of shops open Saturday" | open | Not re-tried this pass (budget); earlier pass found only a forum summary (27 %, unverified). The row is designed. |
| Appointment no-show 10–15 % (vendor-sponsored article, read earlier) | not a ledger row; not re-tried | — |
| `conv.fictional_ids` (Telegram ids above 2^52, unissued VK range) | open | not attempted |
| `geo.address.main/east/west` (candidate street addresses) | open | not attempted: checking them means putting the seed's addresses into web services; OSRM routed between their coordinates without error |

## 10. Time zones

| Fact | Status | Source | Text |
|---|---|---|---|
| Europe/Ulyanovsk is UTC+4 since 2016-03-27 02:00 | verified | IANA tz, file `europe` at https://raw.githubusercontent.com/eggert/tz/main/europe (latest release in NEWS: 2026f, 2026-10-27) | `3:00 - %z 2016 Mar 27 2:00s` then `4:00 - %z` (no end); zone1970.tab: `RU +5420+04824 Europe/Ulyanovsk MSK+01 - Ulyanovsk`; comment cites publication.pravo.gov.ru/Document/View/0001201603090051 |
| Kazan (Tatarstan) is in Europe/Moscow, UTC+3 | verified | same file | "Europe/Moscow covers... 16 RU-TA Tatarstan, Republic of"; Moscow zone last line `3:00 - MSK` (since 2014-10-26) |
