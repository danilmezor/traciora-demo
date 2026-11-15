# Sample calls: how to read them

Eight calls, four situations, each written twice from nothing: once as Tennessee shop talk, once as Russian shop talk. They set the bar for the story calls and the phrase banks. Design: `../DESIGN.md`.

| File | Who (slot) | Day | Score | The two checks that carry it |
|---|---|---|---:|---|
| `en-1-junior-early`, `ru-1-junior-early` | Maya Torres / Алина Хасанова (6) | a working day of hers in P1 | 40.0 | no time offered, no booking asked |
| `en-2-junior-now`, `ru-2-junior-now` | the same | a working day of hers in P6 | 71.9 | the booking taken; a doubt stepped over |
| `en-3-weak-desk`, `ru-3-weak-desk` | Chad Binkley / Вячеслав Крюков (23) | `west`'s 4th full open day before T | 25.0, with `wrong_promise` | added work not taken; the last doubt unanswered |
| `en-4-good-call-damaged`, `ru-4-good-call-damaged` | Angie Holloway / Светлана Демидова (16) | the Wednesday of week T-2 (RU: her first working day on or after it) | 83.3 on the stored lines, 100 on the speech | the booking taken; the second time she offered, lost to noise |

The people, companies, cars, plates, phones and prices are the seed's. Staff are the cast's (`cast.json`). Samples 3 are story S6's call 15: the customer, his car and the part it waits for are `named_customers.json` `S6_waiting_nine_days` (Curtis Vaughn, 2012 Volvo XC60, the angle gear; Айрат Гизатуллин, Peugeot 308 2011, насос электрогидроусилителя руля). Samples 4 are account A2 of `accounts.json` (Millsaps Heating & Plumbing, unit M-112; «Тёплый контур», Т-17). The callers of samples 1 and 2 are invented. Every price is `catalogue.json`'s for the car's class on the call's day, said the way a person says it; each file's `scenario.facts` gives the exact figure. Each `call.day` is an anchor of rule R6 with the date it falls on for the nominal T; phone numbers follow `phones.md`.

## Reading order inside a file

1. `scenario`: who calls, about which car and job, what happens.
2. `script`: what was said. This is the speech, with its hesitations and restarts. Judge the language here.
3. `recognition.applied`: each thing the recognition did to the script, by rule (R1 to R12 in the design) and turn.
4. `transcript.segments`: what the product stores and shows. No timing, as in the product; the clock is `at_s` on the script.
5. `judge_answer`, then `verdict`: the judge's answer with its quotes, and the stored verdict that the product's own `judge.verdict` made of it. Every quote sits word for word on the line it names.
6. `why`: one line per check. `truth` holds what the speech earns; it differs from the verdict only in sample 4, and that difference is the point of sample 4.

Samples 1 and 2 are one person six months apart on the same kind of call. Sample 3 is scored only because the customer asks for new work; a plain "is it ready" call gets no score from the rubric. In sample 4 the coaching line tells the advisor to say what she in fact said.

## For an American reader: three things to check

1. **The small words.** "Y'all", dropped g's, "yes sir" from a man who is giving nothing away, "tag" for a plate, "'preciate you", "what would that run me". Are they where someone from Chattanooga or Nashville puts them, and no thicker than that?
2. **Turns, not paragraphs.** Does each line answer the one before it? Look for half answers ("Front, I think?"), restarts ("I was — I was kinda hopin'"), a doubt that hangs ("Four-fifteen."). Nobody should speak a finished sentence where a person would trail off.
3. **Shop sense.** Would an advisor price it this way: pads alone against pads and rotors, "out the door", a hub assembly after a road test, "write it up", a PO on a fleet job? Do the money and the hours fit a Tennessee independent in 2026?

## Русскому читателю: на что смотреть

1. **Это телефон, а не письмо.** «Девушка, подскажите», «ну, сто восемнадцать где-то», «не, ну нормально, в принципе», «ездить-то надо, куда деваться». Стоят ли частицы, обрывы и переспросы там, где их ставит живой человек? Нет ли фразы, которую вслух никто не скажет?
2. **Язык приёмки.** «Рейка под заказ», «отдельный наряд открывать», «корзина, диск, выжимной», «масло с допуском», «своё масло привезу», «принимаю сама», «путёвка», «три на договоре». Так ли говорит мастер-приёмщик в Ульяновске и в Казани, и не слишком ли гладко для него?
3. **Место, люди и ошибки распознавания.** «На Инженерном», «на Верхнюю Террасу», Гульнара, Рамиль, Айрат, цены 2026 года: узнаётся ли Поволжье без нажима? И отдельно в `transcript`: «моховик» вместо маховика, «Peugeot» латиницей у клиента и «Пежо» у приёмщика, «Савина» вместо Сафиной, «30 900 92», «358, не». Похоже ли это на то, что на самом деле выдаёт расшифровка звонка?
