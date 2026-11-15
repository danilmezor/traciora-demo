# Sample conversations: how to read them

**The source is `../en/` and `../ru/`.** The ten files here are byte-for-byte copies of five story conversations per language, kept so the bar can be read in one sitting; `../../checks/check_conversations.py` fails when a copy differs. A change is made in `../en/` or `../ru/` (through `../build/`) and copied here by `../build/readme.py`, never the other way round. The full sets, with their tables and the facts they add, are in `../en/README.md` and `../ru/README.md`. Design: `../DESIGN.md`.

Four situations, each written twice from nothing: once as people in Tennessee type to a shop, once as people in Ульяновск and Казань do. Sample 4 was one file with two chats; it is now two files, one per conversation, as section 6 counts them.

| Sample | Is file | Channel, mode | Who (slot) | When | State at T | Shows |
|---|---|---|---|---|---|---|
| `en-1-web-after-hours`, `ru-1-web-after-hours` | 01 | web chat, assistant sends | Maya Torres / Алина Хасанова (6) | 21:10 on the evening before S7's day A, picked up on day A (slot 6's 14th working day before T; RU her 10th) | resolved | S7's first chat; an unclear customer and the one question card S07 gives the assistant (R13); a scheduling hand-over |
| `en-2-fleet-quote-waited`, `ru-2-fleet-quote-waited` | 04 | web chat: the assistant sends and hands over, then drafts | Travis and Caleb / Дмитрий and Никита (5, 7); RU also one line by Алина (6) | the Tuesday of week T-4 (card S01); RU after closing, so the two days fall on the shift of slots 5 and 7 | resolved by 7 silent days | S1: the quote request that waited two days for a person; a note that answers nobody; a draft that does the advisor's job |
| `en-3-west-nine-days`, `ru-3-west-nine-days` | 06 | web chat: the assistant sends and hands over, then drafts once the chat is owned | Chad, Jasmine, Dale / Вячеслав, Камила, Ринат Фаридович (23, 24, 22) | 7, 5, 3 and 1 days before T (card S06) | open, Urgent, draft waiting: a reply can be sent here in a live demo | S6: four messages, three late answers, a private note |
| `en-4a-stocktake-web`, `ru-4a-stocktake-web` | 07 | web chat, assistant sends | nobody | the Monday of week W0 (card S13) | pending, the assistant's | S13: the assistant alone |
| `en-4b-stocktake-messenger`, `ru-4b-stocktake-messenger` | 08 | Telegram / VK, drafts | Angie Holloway / Светлана Демидова (16) | slot 16's last working day before T | resolved | S13: a draft edited and sent, twice |

What changed against the first samples, and why (the cards win):

- Sample 1: one clarifying question instead of two.
- Sample 2: rewritten. It was one messenger thread nine weeks before T with call 22 inside it; it is the website chat of week T-4, and call 22 is another event.
- Sample 3: the message days are the card's 7, 5, 3 and 1. The first date he was given is therefore outside the chat (when the part was ordered), which is also what call 15 says. In the Russian file the days follow the rota: the first message comes after closing and the owner answers on his own shift.
- Sample 4: the web question is on the card's day; the Russian regular's car is a Volkswagen Polo, because the Kia Rio 2017 of the first sample is another Marina's car in `named_customers.json`.

Prices and hours are from `catalogue.json` and the ledger; the public pages the assistant quotes are another part of the seed. Customers in sample 4 are invented; the others are the named ones.

## Reading order inside a file

1. `scenario`: who writes, about what, what happens, and the facts the words rest on. `unclear` is there only when the customer is (sample 1). `facts.prices` gives every amount with the catalogue row it comes from.
2. `days`: every day as an anchor of rule R6 with the date it falls on for the nominal T; `floating_days`: every weekday word of the text with its day.
3. `conversations[].timeline`: everything in order. `message` is what the customer sees. `note` is staff only. `draft` is what the assistant put in the reply box, and its `outcome` says what became of it: sent as it was, sent after editing (`became` points at the message), discarded for the person's own words, or replaced before anyone looked. `handoff` is the assistant passing the chat to a person: the tool's arguments, the note it leaves, the card on the board. `activity` is a small line of the thread, stored as a fact; those marked `derived` are the ones the product writes by itself. `outside` is a call or an order in another store, there so the thread makes sense.
4. `state_at_t`: what the Conversations screen shows on the day of the demo.
5. `reads_back`: what the product must compute from it: who answered first and after how many working minutes, each wait, the outcome rows, and whom the Stats screen credits.
6. `truth`, `why`, `new_facts`: the facts an answer may rest on, what to look at, what the file invented.

Times are `day` and `at`, on the clock named in `clock`. In a live demo a reply is sent in the web chat only; the messenger threads here are history.

Three things that are not mistakes:

- The assistant's lines are tidy and alike. It is one writer, and the product strips its formatting.
- On a drafts channel the customer sees nothing of the assistant; the first thing they read is a person's line.
- A draft that says "I don't have the status in front of me" is what an assistant without access to the shop system can honestly write. Whether an advisor uses it is the point.

## For an American reader: three things to check

1. **Thumbs, not sentences.** "idk if it matters but theres a light on now too", "nah mornings dont work", "Friday at 1 👍", a photo instead of the name of the light. Is the lower case and the missing apostrophe where a person on a phone leaves it, and does the fleet coordinator, who types at a desk, stay in full sentences?
2. **Each advisor is one person.** Maya: complete, a time before a price, one exclamation mark. Travis: slow, typos left in ("there not on the fleet rate"). Caleb: "should", "Yes sir", an exclamation mark on a late answer, one answer for two questions. Chad: "its not here yet. supplier says monday". Dale: "handled". Angie: the customer's name twice, "if it were my car", two times to choose from, signed. Could you tell them apart with the names removed?
3. **Shop sense.** A $49.95 brake inspection before any repair is priced; a red BRAKE lamp with scraping; list price for an account that is not on the fleet rate; net 30; a reman angle gear that no Nashville warehouse stocks; a rental running while the car waits. Does anything ring false for an independent shop in 2026? One thing is the product's and not the market's: the messenger is Telegram.

## Русскому читателю: на что смотреть

1. **Это мессенджер, а не письмо.** «машина шумит, сколько стоит посмотреть», «по моему нет» без дефиса, «??» через сорок минут, «Ольга 89073786035», голосовое на сорок секунд вместо текста, «не, с утра не могу». Так ли пишут с телефона в 2026 году, и не слишком ли аккуратно? А логист из офиса пишет полными фразами, с госномерами: похоже ли это на человека, у которого «в пятницу утром директор согласует расходы»?
2. **Каждый приёмщик — один и тот же человек.** Алина: грамотно, полно, сначала время, потом цена. Дмитрий: наспех, в заметке, с опечаткой («договрных»), «я на выдаче зашиваюсь». Никита: «да-да, сделаю», «должен отправить», из двух вопросов ответ на первый. Вячеслав: «не пришло. поставщик перенёс на понедельник», «должны привезти». Ринат Фаридович: «принял». Светлана: по имени дважды, «я бы на своей машине», два времени на выбор и итог. Узнаете ли вы их без подписей?
3. **Сервис и место.** Диагностика тормозов за 700 ₽ до любых цен на ремонт; «муж говорит подшипник»; насос ЭГУР на Peugeot 308 под заказ и поставщик, который «трек-номер не даёт»; отсрочка 30 дней по договору; «В будни он на линии»; два через два, из-за которого вопрос висит между сменами; Московское шоссе, Новый город, Техническая; «закажем через Пашу Мещерякова в Ульяновске». Так ли говорят на приёмке в Поволжье? И отдельно ассистент: «Сам записать я не могу», «Заказ-наряды я не вижу», «с вами свяжутся в ближайшее время». Читается ли это как вежливая машина, а не как переводной текст?
