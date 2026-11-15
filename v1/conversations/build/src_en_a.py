# -*- coding: utf-8 -*-
"""English story conversations 1 to 8 (stories S7, S1, S6, S13)."""
from srclib import *

CFG = "en"
RACHEL = {"ref": "named_customers.json en.S7", "name": "Rachel Dunlap", "first_time": True, "phone": "(423) 555-0131"}
RACHEL_NOTE = "One website visitor: the browser of the first chat, remembered for 30 days (ledger conv.web_visitor_memory_days). The contact holds no name and no phone; both are in the hand-off notes and on the cards."


def fl(word, said_on, day, **kw):
    return dict(word=word, said_on=said_on, day=day, **kw)


def f01():
    f = File(CFG, 1, "S7", "web-after-hours",
             "Website chat on a Sunday night: a noise, one question, the assistant hands over, the junior operator next morning",
             "The assistant answers first on the web chat, from public pages only. The customer is unclear (R13): she asks what it costs to fix a noise she hears mostly in the morning. The assistant asks once, braking or turning, and that settles it. It cannot book, so it takes a name and a number and hands over as a scheduling request. The junior operator picks it up six minutes after opening.")
    f.cast = {"customer": RACHEL}
    f.staff(6)
    ev = f.day(wd(6, -14, plus=-1), "the chat, 21:10: the evening before day A")
    a = f.day(wd(6, -14), "day A: slot 6 takes the hand-over, books the visit, rings to confirm")
    v = f.day(wd(6, -13), "the visit, 09:00: slot 6's next working day after A")
    f.p("$49.95", "brake inspection, menu price", job="brake_inspection")
    f.scenario = {
        "who_writes": "A first-time customer, on her phone, after the shops have closed.",
        "vehicle": "2014 Honda CR-V EX AWD, 121,400 miles",
        "wants": "She thinks she wants a price to fix a noise. What she needs is a brake inspection, soon.",
        "what_happens": "One clarifying question, a photo of the dash, the public price of an inspection, a request for Tuesday morning. The assistant cannot book: it asks for her name, number and shop, hands over, and says somebody will get back to her. Monday at 7:36 Maya books Tuesday 9:00 and says she will call to confirm (the call is in the calls set, unscored).",
        "facts": {"hours_weekday": "7:30 to 17:30", "address_main": "2106 East Main Street",
                  "public_pages_used": ["hours and locations", "price list: brake inspection", "brake questions: a grinding sound with a warning light"],
                  "booked": "%s 09:00 at main; ERP appointment, source web chat" % v,
                  "anchors": "rule R6: day A is slot 6's 14th working day before T; the chat is the evening before it and the visit her next working day. The first chat is under 30 days before T, inside the web chat's memory of a visitor (ledger s7.booking_day, s7.thread, conv.web_visitor_memory_days)."},
        "unclear": {"kind": "vague: a noise, mostly in the morning, and a price asked for it", "loops": 1, "resolved": True,
                    "how": "The assistant asks once whether she hears it when she presses the brake or when she turns the wheel; she says when she brakes, a scraping, and sends a photo of the warning light. It never names a repair or a repair price."}}
    f.floating = [fl("tomorrow", ev, a), fl("tuesday morning", ev, v), fl("tonight", ev, ev), fl("tomorrow, Tuesday", a, v),
                  fl("Tuesday at 9:00", a, v), fl("later today", a, a)]
    c = web(f, "c1", "main", 1, 1)
    c.c(ev + " 21:10:12", "hi how much to fix a noise my car is making")
    c.c("21:10:25", "its mostly in the morning")
    c.a("21:10:49", "Hi! I'm the assistant for Brennan Auto Care. The shops are closed right now and open at 7:30 tomorrow, but I can help in the meantime. A price depends on where the noise comes from, so one question first: do you hear it when you press the brake, or when you turn the steering wheel? And what kind of car is it?")
    c.c("21:11:40", "when i brake. like a scraping")
    c.c("21:11:53", "idk if it matters but theres a light on now too")
    c.c("21:12:10", "", files=[{"kind": "image", "file": "IMG_4412.jpg", "pool": "dash-red-brake-lamp", "shows": "instrument cluster at night, the red BRAKE lamp lit"}])
    c.a("21:12:41", "Thank you for the photo: that's the red BRAKE warning light. I can't diagnose a car over chat, but a scraping sound when you press the brake, together with that light, should be looked at soon, and I wouldn't put many miles on it until then. The first step is a brake inspection, which is $49.95. The technician shows you what they find before any repair is priced. Would you like me to ask the shop to get you in?")
    c.c("21:13:30", "yes please. can i bring it tuesday morning before work? its a 2014 crv")
    c.a("21:13:55", "I can't book a time myself, but I'll pass your request to the service desk and they'll confirm it with you. What's your name and the best number to reach you? And which shop works better: East Main Street or Bonny Oaks Drive?")
    c.c("21:14:37", "Rachel Dunlap 423 555 0131")
    c.c("21:14:46", "main st")
    c.a("21:15:19", "Thank you, Rachel. Your request is with the team now, and somebody will get back to you as soon as possible. Anything else I can help with tonight?")
    c.h("21:15:20", "scheduling", "Rachel Dunlap", "(423) 555-0131", "main st",
        "2014 Honda CR-V. Scraping sound when she presses the brake, mostly in the morning; the red BRAKE light is on (photo in the chat). She first asked what it costs to fix a noise; I asked once whether it was when braking or when turning, and she said braking. Wants a brake inspection on Tuesday morning before work, East Main Street.",
        "main", "%s 17:30, the next open day's close" % a)
    c.c("21:15:58", "no thats it thx")
    c.d("21:16:33", "d1", "You're welcome, Rachel. Have a good night!")
    c.s(6, a + " 07:36:40", "Good morning Rachel, this is Maya at Brennan Auto Care on East Main. I have you down for tomorrow, Tuesday, at 9:00 for a brake inspection on the CR-V. It's $49.95, takes about half an hour, and we'll show you what we find before anything else is done. If you need it earlier for work I can also do 7:30. I'll give you a quick call later today to confirm!")
    c.c("08:12:10", "9 works!! thank you")
    c.d("08:12:55", "d2", "You're welcome, Rachel. See you Tuesday at 9:00 at 2106 East Main Street.")
    c.s(6, "08:14:05", "You're welcome, Rachel. See you Tuesday at 9:00 at 2106 East Main Street.", use="d2")
    c.label(6, "08:14:30", "booking")
    c.res(6, "08:14:50")
    c.out("13:40", "calls", "Maya's confirming call, outbound, transcribed, not judged (calls design, story call 8); the hour is the calls set's to state")
    c.out(v + " 09:00", "erp", "appointment kept; repair order opened by slot 6")
    c.state_extra = {"contact_note": RACHEL_NOTE}
    c.reads_extra = {"operator_credit": "the chat's first answer is nobody's (the assistant wrote it); slot 6 has two replies and one resolution"}
    f.truth = {"reason": "a symptom", "handled": "assistant first, handed over (scheduling), slot 6", "outcome": "brake inspection booked for the next day, 09:00, at main",
               "facts": ["first written at 21:10 on the evening before day A, outside opening hours", "one clarifying question, asked by the assistant",
                         "the assistant named only the inspection price, 49.95, and no repair", "handed over with her name and number; the contact itself holds neither",
                         "slot 6's first line {first} working minutes after opening", "resolved by slot 6, label booking"],
               "questions": ["S7.1"]}
    f.why = ["The assistant never books, never quotes a repair, never promises a time: 'as soon as possible' is the product's own sentence.",
             "One question is enough here: it offers two readings, and her answer comes with a photo. The hand-off note says what was asked and how she answered.",
             "Maya's two lines are her sheet: complete, a time offered before anything else, one exclamation mark, and the second is the draft sent as it was."]
    f.new_facts = ["The photo IMG_4412.jpg (picture pool 'dash-red-brake-lamp').", "The confirming call is shown at 13:40; calls/en decides its hour."]
    return f


def f02():
    f = File(CFG, 2, "S7", "web-approval-and-thanks",
             "The day of the visit: she approves the brakes and declines the shock absorbers in the website chat; her thanks the next morning",
             "A returning website visitor is the same contact, and the assistant remembers her name and number. It cannot see or change a repair order, so an approval is a hand-over, kind escalation. The junior operator confirms in four minutes with the price, the total and the pick-up time. The thanks next day reopens the chat she owns: the assistant drafts, she edits and resolves.")
    f.cast = {"customer": dict(RACHEL, first_time=False)}
    f.staff(6)
    f.cast["named_in_a_line"] = [{"slot": 12, "name": "Luis Herrera", "role": "the mechanic on her car"}]
    v = f.day(wd(6, -13), "the visit: slot 6's next working day after day A")
    th = f.day(wd(6, -13, plus=1), "the day after the visit")
    pads = f.p("$493.00", "front brake pads and rotors, class car, standard parts", job="front_pads_rotors")
    f.p("$606.45", "the bill with tax: inspection 49.95 + pads and rotors 493.00 + shop supplies 12.15, plus sales tax", amount=606.45, source={"ledger": "s7.bill.with_tax"})
    f.scenario = {
        "who_writes": "The same customer, from work, after reading the estimate the shop e-mailed her.",
        "vehicle": "2014 Honda CR-V EX AWD",
        "wants": "To say yes to the front brakes and no to the rear shock absorbers.",
        "what_happens": "The inspection found worn front pads and rotors and a seeping rear shock absorber. She writes her decision in a new website visit; the assistant hands it over; Maya confirms the work, the total and the time. She pays by card that afternoon. Next morning she writes her thanks; the chat reopens, Maya sends the edited draft and resolves.",
        "facts": {"found": "front pads at the wear indicator, front rotors scored; right rear shock absorber seeping", "approved": "front brake pads and rotors",
                  "declined_and_deferred": "rear shock absorbers, pair: 339.28 at list (ledger s7.bill.declined_rear_shocks); a reminder is raised",
                  "paid": "606.45 by card (ledger s7.bill)", "public_pages_used": []}}
    f.floating = [fl("today", v, v), fl("this afternoon", v, v)]
    c = web(f, "c1", "main", 1, 2)
    c.out(v + " 09:00", "erp", "the visit: repair order opened by slot 6; inspection by slot 12")
    c.out("10:05", "erp", "the estimate is e-mailed to her from the shop system: front pads and rotors 493.00; rear shock absorbers, pair, 339.28")
    c.c("10:21:15", "hi its Rachel Dunlap, yall have my crv today. got the estimate in my email")
    c.c("10:21:40", "go ahead with the front brakes. not the shocks right now, thats a lot at once")
    c.a("10:22:04", "Hi Rachel! I can't see or change repair orders from here, so I'll pass this to the service desk at East Main right away: yes to the front brakes, no to the rear shock absorbers for now. Is (423) 555-0131 still the best number for you?")
    c.c("10:22:35", "yes")
    c.a("10:22:58", "Thank you. It's with the team now, and somebody will get back to you as soon as possible.")
    c.h("10:22:59", "escalation", "Rachel Dunlap", "(423) 555-0131", "East Main",
        "Rachel Dunlap, 2014 Honda CR-V, at East Main today. She has read the estimate and says: go ahead with the front brakes; not the rear shock absorbers for now, it is a lot at once. I can't see the repair order, so I confirmed nothing.",
        "main", "%s 17:30, the day's close" % v)
    c.s(6, "10:26:20", "Hi Rachel, it's Maya! Got it: we're doing the front pads and rotors today, $493.00, and I've marked the rear shocks as declined for now. That one is seeping, not leaking, so it's fine to wait a few weeks, and I'll put a reminder on your file. With the inspection your total comes to $606.45 with tax. Luis will have it ready by 3:00, and we're here until 5:30.")
    c.c("10:31:02", "perfect thank you!")
    c.d("10:31:40", "d1", "You're welcome, Rachel! We'll see you this afternoon.")
    c.s(6, "10:32:30", "You're welcome, Rachel! We'll see you this afternoon.", use="d1")
    c.label(6, "10:32:50", "approval")
    c.res(6, "10:33:05")
    c.out("15:10", "erp", "repair order closed: front pads and rotors fitted; rear shock absorbers declined, deferred, reminder raised; paid by card, 606.45")
    c.c(th + " 08:47:20", "brakes feel so much better. thank you Maya!!")
    c.d("08:48:00", "d2", "You're welcome, Rachel! We're glad the brakes feel right. Thank you for coming in.")
    c.s(6, "08:50:40", "So glad to hear it, Rachel! Thank you for coming in. I'll check in with you in a few weeks about that rear shock.", edit="d2")
    c.res(6, "08:51:00")
    c.state_extra = {"contact_note": RACHEL_NOTE}
    c.reads_extra = {"operator_credit": "the chat's first answer is nobody's; slot 6 has three replies, two resolutions of one chat (Stats counts distinct chats: one), one draft sent as it was and one edited"}
    f.truth = {"reason": "found work: approve or decline", "handled": "assistant first, handed over (escalation), slot 6",
               "outcome": "front pads and rotors approved and paid, 606.45 with tax; rear shock absorbers declined and deferred",
               "facts": ["approved: front brake pads and rotors, 493.00", "declined: rear shock absorbers (a pair), deferred with a reminder", "paid by card: 606.45 with sales tax",
                         "a thank-you from her the next morning; the chat is resolved by slot 6", "the same website contact as the first chat"],
               "questions": ["S7.1", "S7.2"]}
    f.why = ["The assistant repeats her decision back in plain words and confirms nothing it cannot see.",
             "Maya answers what was asked and then what she will be asked next: the total and the time, and why the shock absorber can wait.",
             "The thanks is a new session of a resolved chat: reopened, drafted for, sent edited, resolved again."]
    f.new_facts = ["The estimate reached her by e-mail from the shop system at about 10:05 on the day of the visit (rdunlap@inbox.example).",
                   "The car was ready by 3:00; the order was closed and paid at about 15:10.", "The seeping shock absorber is the right rear one."]
    return f


def f03():
    f = File(CFG, 3, "S7", "web-return-draft-waiting",
             "She comes back for the shock absorbers: the assistant prices and hands over, the junior operator takes the chat; at T her answer is unread and a draft waits",
             "The live-demo chat. A returning visitor asks to book the deferred work. The assistant answers from the public price list, cannot book, hands over; from Maya's first line the chat is hers and the assistant only drafts. Thirty minutes before T the customer writes again: the chat is open, owned by slot 6, unread, with one draft in the box that is honest about what the assistant cannot see. Editing it (two free times, the total with tax) and sending it is the demo.")
    f.cast = {"customer": dict(RACHEL, first_time=False)}
    f.staff(6)
    r = f.day(wd(6, -1), "the return chat, 15:40; slot 6 replies at 16:05")
    t = f.day(T(), "she writes again 30 minutes before T")
    f.day(wk("Mon", -1), "'mon'")
    f.day(wk("Tue", -1), "'tues'")
    f.day(wk("Wed", -1), "'wed'")
    f.day(wk("Thu", -1), "'thurs'; the stocktake day: every shop closes at 12:00")
    f.p("$339.28", "rear shock absorbers, pair, class car, standard parts, today's list", job="rear_shocks_pair")
    f.scenario = {
        "who_writes": "The same customer, from the same phone, 17 days after her visit.",
        "vehicle": "2014 Honda CR-V EX AWD",
        "wants": "To book the rear shock absorbers she declined, and to know the total.",
        "what_happens": "Thursday 15:40 she asks the price and for a day next week. The assistant gives the price-list figure and hands over. Maya replies at 16:05 with two times. She does not answer that day. Friday at 10:00 she writes that neither time works and asks for Wednesday or Thursday early, and for the total with tax. The assistant drafts; nobody has opened it at T.",
        "facts": {"declined_at_the_visit": "rear shock absorbers, pair", "with_supplies": 347.38, "with_tax": 379.51,
                  "expected_reply": "two free times at main in the next seven days and the price: 339.28 plus shop supplies, 379.51 with tax (card S07, question S7.3)",
                  "public_pages_used": ["price list: rear shock absorbers"],
                  "note": "The Thursday she asks about is the stocktake day (S13): the shop closes at noon, so only its morning is free."}}
    f.floating = [fl("next week", r, "the week W+1"), fl("Monday at 9:00", r, "the Monday of week W+1 (T+3d)"), fl("Tuesday at 1:00", r, "the Tuesday of week W+1 (T+4d)"),
                  fl("mon and tues", t, "T+3d and T+4d"), fl("wed or thurs", t, "T+5d or T+6d"), fl("Wednesday or Thursday", t, "T+5d or T+6d")]
    c = web(f, "c1", "main", 1, 3)
    c.c(r + " 15:40:05", "hi again its Rachel Dunlap with the CRV. im ready to do those rear shocks")
    c.c("15:40:22", "what was the price again and can i get in next week")
    c.a("15:40:47", "Hi Rachel, welcome back! On our price list, replacing the rear shock absorbers as a pair is $339.28 for a car like the CR-V, before shop supplies and tax; the service desk has your exact estimate. I can't book a time myself, so I'll pass this to East Main and they'll confirm a day with you. Is (423) 555-0131 still the right number?")
    c.c("15:41:20", "yep same number")
    c.a("15:41:44", "Thank you. Your request is with the team now, and somebody will get back to you as soon as possible.")
    c.h("15:41:45", "scheduling", "Rachel Dunlap", "(423) 555-0131", "East Main",
        "Rachel Dunlap, 2014 Honda CR-V, East Main. She wants to book the rear shock absorbers she put off at her last visit, some time next week. I gave her the price-list figure for the pair, $339.28 before shop supplies and tax, and no time.",
        "main", "%s 17:30, the day's close" % r)
    c.s(6, "16:05:10", "Hi Rachel, it's Maya, good to hear from you! Yes, let's get those rear shocks done. I can take the CR-V Monday at 9:00 or Tuesday at 1:00, and it's about an hour and a half either way. Which works better for you?",
        late="story: the card's 16:05 (ledger s7.thread.taken_by_6)")
    c.c(t + " 10:00:12", "morning Maya, sorry just now seeing this. mon and tues dont work, im out of town for work")
    c.c("10:00:41", "anything wed or thurs, early? and whats my total with tax")
    c.d("10:01:20", "d1", "Good morning, Rachel! No problem at all. The rear shock absorbers as a pair are $339.28 before shop supplies and tax. I'll confirm your exact total and an early time on Wednesday or Thursday and message you right back.")
    c.state_extra = {"contact_note": RACHEL_NOTE,
                     "live_demo": "a web chat owned by slot 6, so the waiting draft can be edited and sent in a live demo (ledger conv.live_demo, conv.open_at_t)"}
    c.reads_extra = {"operator_credit": "the chat's first answer is nobody's; slot 6: one reply 23 minutes after the hand-off, nothing resolved; the second hand-over card was taken by her at 16:05"}
    f.truth = {"reason": "to book or ask for a slot", "handled": "assistant first, handed over (scheduling), slot 6; then drafts",
               "outcome": "open at T, owned by slot 6, unread, one unsent draft",
               "facts": ["she asked on slot 6's last working day before T to book the rear shock absorbers she had declined",
                         "the assistant gave the list price, 339.28 before shop supplies and tax, and handed over",
                         "slot 6 offered Monday 9:00 or Tuesday 1:00; she cannot come either day and asks for Wednesday or Thursday early and for the total with tax",
                         "the right answer offers two free times and the price: 339.28 plus supplies, 379.51 with tax", "nothing is sent without slot 6"],
               "questions": ["S7.1", "S7.2", "S7.3"]}
    f.why = ["The draft says what the assistant knows (the list price) and promises only to find out the rest; the junior's edit is the two times and the total.",
             "Maya's 16:05 line has no price in it: the time comes first, and the price had just been given.",
             "At T this is one of the two chats that wait on the shop, and both are web chats."]
    f.new_facts = ["Maya offered the Monday of week W+1 at 9:00 and the Tuesday at 1:00; the customer is out of town on both days.",
                   "A shock-absorber job is spoken of as 'about an hour and a half' (catalogue: 1.2 billed hours)."]
    return f


def f04():
    f = File(CFG, 4, "S1", "web-fleet-quote-waited",
             "The fading account's new fleet contact asks for a quote in the website chat; two days to a person's first reply",
             "A hand-over that nobody takes. The assistant will not price fleet work, takes a number and hands over at 10:14 on Tuesday. The lead advisor reads it at 16:02 and passes it on in a private note; the newcomer answers 'on it' in another note. A note answers nobody: the customer's follow-up on Wednesday gets a draft that sits. Thursday at 10:41 the newcomer sends that draft as it was, promises 'today', answers one of her two questions, and the quote arrives at 16:47. The assistant's last draft answers the question he skipped, and he sends it untouched.")
    f.cast = {"customer": {"ref": "accounts.json en.A6 contacts[1]", "name": "Erin Castillo", "company": "Sourwood Catering Co.",
                           "role": "Operations Coordinator, the fleet contact since P", "phone": "(423) 555-0106", "first_time": False},
              "named_in_a_line": [{"name": "Marianne Tolliver", "ref": "accounts.json en.A6 contacts[2]", "role": "owner; signs off the spending"}]}
    f.staff(5, 7, s7={"weeks_in_the_job": 10})
    d0 = f.day(wk("Tue", 4), "the quote request (card S01; ledger s1.dates.a6_chat_waited_two_days)")
    d1 = f.day(wk("Tue", 4, plus=1), "her follow-up; a draft, no reply")
    d2 = f.day(wk("Tue", 4, plus=2), "the first reply by a person, the quote")
    d3 = f.day(wk("Tue", 4, plus=3), "she takes it to the owner")
    f.day(wk("Tue", 4, plus=10), "Chatwoot resolves the chat after 7 silent days")
    f.p("$640.91", "front brake pads and rotors, class van, standard parts, list (in the PDF)", job="front_pads_rotors", cls="van")
    f.p("$304.45", "battery replaced, class van, list (in the PDF)", job="battery_replace", cls="van")
    f.num_("net 30", "the account's payment terms in days (accounts.json, ledger acct.A6.terms_days)")
    f.scenario = {
        "who_writes": "The contact who took the vans over from the man who used to ring the lead advisor directly. She types at a desk, in full sentences, and is comparing shops.",
        "vehicles": ["SC-4, 2019 Ram ProMaster 2500, BRC-4958", "SC-9, 2017 Chevrolet Express 3500 cutaway, BRC-6984"],
        "wants": "An itemized quote on two vehicles before she schedules anything, in time for the owner's sign-off on Friday morning.",
        "what_happens": "Tuesday 10:12 she asks. Travis leaves a note for Caleb at 16:02. Wednesday she follows up. Thursday 10:41 Caleb sends the waiting draft; the quote goes out at 16:47, list prices. Friday she takes it to the owner. Nothing is booked; Chatwoot resolves the chat a week later.",
        "facts": {"price_class": "list: medium accounts are not on the company-account rate (catalogue.json company_account_terms)", "terms": "net 30 (accounts.json)",
                  "first_person_reply_after": "two days: Tuesday 10:14 to Thursday 10:41", "saturday": "main is open Saturday 08:00 to 13:00 (ledger site.open_days)",
                  "public_pages_used": ["hours and locations"],
                  "note": "This is the chat of card S01's wrinkle, 'a chat that waited two days'. Call 22 (the quote promised and sent two days late) is another event, on the Tuesday of week T-9; this chat does not mention it."}}
    f.floating = [fl("Friday morning", d0, d3), fl("yesterday", d1, d0), fl("today", d2, d2), fl("tomorrow morning", d2, d3), fl("a Saturday", d2, "any Saturday"),
                  fl("this morning", d3, d3), fl("Saturdays", d3, "any Saturday")]
    c = web(f, "c1", "main", 207, 4)
    c.c(d0 + " 10:12:20", "Hello, this is Erin Castillo with Sourwood Catering. We have an account with your East Main shop.")
    c.c("10:13:05", "I need an itemized quote on two of our vehicles before I schedule anything. SC-4 (the 2019 ProMaster): front brakes, pads and rotors. SC-9 (the 2017 box truck): a new battery. Parts and labor separate, please. Our owner signs off on these Friday morning.")
    c.a("10:13:31", "Hello Erin, I'm the assistant for Brennan Auto Care. I can't prepare a quote for specific fleet vehicles from here, and I don't want to give you list prices that may not match your account. I'll pass your request to the service advisors at East Main so they can send an itemized quote. What's the best phone number for you?")
    c.c("10:14:02", "(423) 555-0106")
    c.a("10:14:25", "Thank you, Erin. Your request is with the team now, and somebody will get back to you as soon as possible.")
    c.h("10:14:26", "escalation", "Erin Castillo", "(423) 555-0106", "East Main",
        "Erin Castillo, Sourwood Catering (company account, East Main). She asks for an itemized quote, parts and labor separate, before scheduling: SC-4, 2019 ProMaster, front brake pads and rotors; SC-9, 2017 box truck, a new battery. Their owner signs off on Friday morning. I gave no prices.",
        "main", "%s 17:30, the day's close" % d0)
    c.n(5, "16:02:40", "@Caleb Sutton can u work up a quote for sourwood on these 2. list price, there not on the fleet rate. im slammed at the counter", mentions=[7])
    c.n(7, "16:09:15", "Yes sir, on it!")
    c.c(d1 + " 10:22:15", "Good morning. Following up on the quote I asked for yesterday.")
    c.d("10:22:55", "d1", "Good morning, Erin. I'm sorry for the wait. Your request for an itemized quote on SC-4 and SC-9 is with our service advisors, and you'll have it from us. If you can send the plate or VIN for each, the quote will be exact.")
    c.s(7, d2 + " 10:41:20", "Good morning, Erin. I'm sorry for the wait. Your request for an itemized quote on SC-4 and SC-9 is with our service advisors, and you'll have it from us. If you can send the plate or VIN for each, the quote will be exact.",
        use="d1", late="story: the two days of card S01 (ledger s1.a6.quote_chat_waited_days)")
    c.s(7, "10:42:00", "Working on it now, should have it over to you today!")
    c.c("10:50:10", "Plates are BRC-4958 and BRC-6984. Thank you. I do need it today: Marianne signs off tomorrow morning.")
    c.c("10:50:35", "Two questions while I have you: are we still on net 30, and can SC-9 come in on a Saturday? It's on the road every weekday.")
    c.d("10:51:15", "d2", "Thanks, Erin, that's what we needed. I'll confirm the terms and a Saturday drop-off and answer both with the quote today.")
    c.s(7, "10:58:00", "Yes still net 30!")
    c.label(7, "10:58:30", "fleet")
    c.s(7, "16:47:05", "Hi Erin, here's the quote for both! Let me know when you'd like to bring them in",
        files=[{"kind": "file", "file": "Sourwood_quote_SC4_SC9.pdf", "pool": "estimate-pdf",
                "shows": "a two-vehicle estimate at list prices: SC-4 front brake pads and rotors $640.91; SC-9 battery $304.45; shop supplies and tax on their own lines"}])
    c.c(d3 + " 08:05:30", "Received, thank you. I'll take it to Marianne this morning and let you know.")
    c.d("08:06:10", "d3", "You're welcome, Erin. And to your second question: yes, East Main is open Saturdays from 8:00 to 1:00, so SC-9 can come in on a Saturday.")
    c.s(7, "08:19:40", "You're welcome, Erin. And to your second question: yes, East Main is open Saturdays from 8:00 to 1:00, so SC-9 can come in on a Saturday.", use="d3")
    c.auto()
    c.reads_extra = {"operator_credit": "the chat's first answer is nobody's; slot 7: his first line two days after the hand-off, four replies, two drafts sent as they were and one discarded, nothing resolved; slot 5: a note and no reply"}
    f.truth = {"reason": "company account: weekly bookings, quotes, documents", "handled": "assistant first, handed over (escalation); slot 5's note; slot 7",
               "outcome": "quote sent two days after it was asked for; nothing booked; resolved by 7 silent days",
               "facts": ["asked on the Tuesday of week T-4 at 10:12; handed over at 10:14", "the first line by a person came on Thursday at 10:41: two days",
                         "slot 5 read it the same afternoon and passed it to slot 7 in a private note", "the quote, at list prices, went out on Thursday at 16:47",
                         "of her two questions slot 7 answered one; the other was answered by the assistant's draft, sent as it was", "no visit followed"],
               "questions": ["S1.3"]}
    f.why = ["Erin stays in full sentences and her lines get shorter: an introduction, 'Following up', 'I do need it today', 'Received, thank you.' Nobody is rude.",
             "Travis writes to a colleague, not to the customer, slowly and with the typos left in.",
             "Caleb: 'should', an exclamation mark on a late answer, the first of two questions, and two drafts sent untouched, the second of which does his job for him.",
             "For S1 an agent finds here: the hand-off instant, the two notes, the first human line two days later."]
    f.new_facts = ["The quote is for SC-4 (front brake pads and rotors, 640.91 at list) and SC-9 (battery, 304.45 at list); it was asked for the owner's sign-off on the Friday of week T-4.",
                   "ERP: the estimate made from this chat is proposed as one of A6's five slow estimates (ledger s1.a6), expired; no order followed.",
                   "The file Sourwood_quote_SC4_SC9.pdf (picture pool 'estimate-pdf').",
                   "Call 22's vehicles were not read (calls/en is another agent's): the units here are chosen to differ from the old sample's SC-6, SC-8 and SC-10."]
    return f


def f05():
    f = File(CFG, 5, "S1", "telegram-weekly-vans",
             "The healthy account: the dispatcher's Monday list, every week, in one Telegram conversation",
             "One messenger conversation for life: every week the dispatcher's message reopens it, the assistant drafts, the east shop's lead advisor edits and sends, and resolves. Four sessions are written: the first after go-live, found work approved with a photo and a purchase-order number, a van swapped, and this week's, which at T is confirmed and waits on the customer. It is the named open messenger chat: its last public line is the shop's and no draft sits in its box.")
    f.cast = {"customer": {"ref": "accounts.json en.A2 contacts[0]", "name": "Tina Ragsdale", "company": "Millsaps Heating & Plumbing", "role": "Dispatcher (books the weekly slot)",
                           "phone": "(423) 555-0121", "first_time": False},
              "named_in_a_line": [{"name": "Hal Millsaps", "ref": "accounts.json en.A2 contacts[1]", "role": "President"},
                                  {"name": "Darnell", "role": "the account's driver of M-112 (calls design, story call 25)", "invented": True}]}
    f.staff(16)
    s1 = f.day(wk("Thu", 23), "session 1: the first list sent here, for the Monday after")
    f.day(wk("Mon", 22), "'Monday the 8th'")
    s2 = f.day(wk("Mon", 15), "session 2: a Monday slot; found work on M-112")
    s3 = f.day(wk("Thu", 6), "session 3: a van swapped")
    f.day(wk("Mon", 5), "'Monday' of session 3")
    f.day(wk("Mon", 4), "'Monday the 12th'")
    s4 = f.day(wd(16, -1), "session 4: this week's list, for the Monday of week W+1")
    f.day(wk("Mon", -1), "'Monday the 16th'")
    struts = f.p("$985.03", "front strut assemblies, pair, class van, company-account price", job="front_struts_pair", cls="van", klass="company")
    align = f.p("$134.95", "four-wheel alignment, class van, company-account price", job="wheel_alignment", cls="van", klass="company")
    f.p("$1,119.98", "the two together, before tax", amount=round(struts + align, 2), source={"sum_of_said": ["$985.03", "$134.95"]})
    f.num_("3 mm", "the pad thickness under which she asks for a decision; a shop habit, not a catalogue row")
    f.num_("600 miles", "how far M-108 is past its service in session 3; invented")
    f.scenario = {
        "who_writes": "The dispatcher of the account with the most visits. She has sent the Monday list by phone for years; since go-live she sends it here.",
        "vehicles": "five vans every Monday at 07:30 from the fleet of 25 (accounts.json en.A2): the units named in each session",
        "wants": "The Monday slot confirmed; found work decided the same day.",
        "what_happens": "Session 1: the first list in the messenger. Session 2: on a Monday the front struts of M-112 are found leaking; Angie sends a photo and the fleet price, the president says go ahead and gives a purchase-order number. Session 3: one van is swapped and the missed one is put on a later Monday. Session 4, the day before T: next Monday's five are confirmed and Angie asks one question that is still unanswered.",
        "facts": {"weekly_slot": "Monday 07:30, five vans (ledger acct.A2.weekly_slot)", "price_class": "company-account rate (A1 and A2; ledger price.hour.company)",
                  "sessions_written": 4, "sessions_in_the_seed": "one a week since G; the others are built from these four with the fleet's units and the same two voices",
                  "ties": "M-112 is the van whose front struts were done 'back in the summer' in story call 25; its driver is Darnell there too",
                  "public_pages_used": []}}
    f.floating = [fl("Monday the 8th", s1, "the Monday of week T-22"), fl("Monday", s1, "the Monday of week T-22"), fl("today", s2, s2), fl("next Monday", s2, "the Monday of week T-14"),
                  fl("Monday", s3, "the Monday of week T-5"), fl("all week", s3, "the week T-5"), fl("Monday the 12th", s3, "the Monday of week T-4"), fl("Thursday", s3, "the Thursday of week T-5"),
                  fl("Monday the 16th", s4, "the Monday of week W+1 (T+3d)"), fl("Monday", s4, "the Monday of week W+1 (T+3d)")]
    c = tg(f, "c1", "east", 1310, "Tina Ragsdale", avatar=pic("pet", "a golden retriever looking out of a truck window"),
           opened_note="the conversation was created by the first session; every later session reopens it")
    # session 1
    c.c(s1 + " 14:05:10", "Hi Angie, it's Tina at Millsaps. Hal says we can send the Monday list here now instead of calling?")
    c.c("14:06:02", "For Monday the 8th: M-103, M-107, M-110, M-114 and M-121. Service on all five. 110's driver says it pulls to the right")
    c.d("14:06:45", "d1", "Hi Tina! Yes, the Monday list can come here. For Monday the 8th at 7:30 we have M-103, M-107, M-110, M-114 and M-121 for service, and we'll look at the pull to the right on M-110.")
    c.s(16, "14:11:20", "Hi Tina! Yes ma'am, this is the place, and it's me on this end. I have all five down for Monday the 8th at 7:30: M-103, M-107, M-110, M-114 and M-121, service on each, and we'll put M-110 on the alignment rack for that pull. Same as always, Tina: I'll message you here as each one is ready, and anything past the service I run by you first.\nAngie", edit="d1")
    c.c("14:13:40", "Perfect 👍")
    c.d("14:14:20", "d2", "Thank you, Tina. See you Monday!")
    c.s(16, "14:15:05", "Thank you, Tina. See you Monday!", use="d2")
    c.label(16, "14:15:20", "fleet")
    c.res(16, "14:15:40")
    # session 2
    c.c(s2 + " 10:40:15", "Morning Angie. How are we looking on today's five? Hal wants 112 back by 3 if we can")
    c.d("10:41:00", "d3", "Good morning, Tina. I don't have the status of today's vans in front of me. I'll check on all five, and on M-112 for 3:00, and message you right back.")
    c.s(16, "10:46:30", "Good morning, Tina! Four of the five are on schedule and will be ready by noon. M-112 is the one I was about to write you about, Tina: both front struts are leaking, and the right one is wet all the way down. If it were my van I wouldn't send it back out loaded like that. Photo below. At your fleet rate the pair is $985.03 installed, and it needs an alignment after, $134.95. I can still have it back to you by 3:00 if I get a yes by 11:30, or we can put it on next Monday's list. Which would Hal rather?\nAngie",
        files=[{"kind": "image", "file": "M112_front_strut.jpg", "pool": "worn-part-strut", "shows": "a front strut wet with oil down to the spring seat, a gloved finger pointing at the seal"}], edit="d3")
    c.c("10:52:10", "Ugh. Let me ask Hal")
    c.d("10:52:50", "d4", "Of course, Tina. We'll hold M-112 until we hear from you.")
    c.c("11:08:05", "Hal says go ahead, struts and alignment, today. PO 4398A")
    c.d("11:08:45", "d5", "Thank you, Tina. We'll go ahead with the front struts and the alignment on M-112 today under PO 4398A and have it ready by 3:00.")
    c.s(16, "11:12:05", "Thank you, Tina, and thank Hal for the quick answer. So we're doing the front struts and the alignment on M-112 today, PO 4398A, $1,119.98 before tax. It'll be ready by 3:00 with the other four, and I'll message you when Darnell can come for it.\nAngie", edit="d5",
        late="nothing to answer until the customer came back with the decision: the product counts the wait from 'Let me ask Hal'")
    c.label(16, "11:12:30", "approval")
    c.c("11:14:10", "👍 thank you")
    c.d("11:14:50", "d6", "You're welcome, Tina!", clear=(16, "11:16:20"))
    c.res(16, "11:16:30")
    # session 3
    c.c(s3 + " 15:20:10", "Angie for Monday swap M-108 for M-115 please. 108 is stuck on the hospital job all week")
    c.c("15:20:40", "so its 104 106 111 115 119")
    c.d("15:21:25", "d7", "Got it, Tina: M-115 in place of M-108. Monday at 7:30: M-104, M-106, M-111, M-115 and M-119.")
    c.s(16, "15:26:10", "Got it, Tina: M-115 in place of M-108, so Monday at 7:30 it's M-104, M-106, M-111, M-115 and M-119. M-108 is about 600 miles past its service, so let's not let it slide much further, Tina. Want me to put it on the list for Monday the 12th?\nAngie", edit="d7")
    c.c("15:31:30", "yes do that")
    c.d("15:32:10", "d8", "Done, Tina. M-108 is down for Monday the 12th.")
    c.s(16, "15:34:20", "Done: M-108 is on the list for Monday the 12th, and I'll remind you the Thursday before.\nAngie", edit="d8")
    c.res(16, "15:34:40")
    # session 4
    c.c(s4 + " 13:10:20", "Hi Angie! Monday the 16th: M-102, M-109, M-113, M-116, M-122.")
    c.c("13:10:55", "113's driver says the heat is weak. kinda important this time of year lol")
    c.d("13:11:35", "d9", "Hi Tina! Got it for Monday the 16th at 7:30: M-102, M-109, M-113, M-116 and M-122, and we'll check the heater on M-113.")
    c.s(16, "13:16:40", "Hi Tina! All five are down for Monday the 16th at 7:30: M-102, M-109, M-113, M-116 and M-122. We'll check the heat on M-113 first thing; if it were my van I'd want the coolant level and the thermostat looked at before it gets any colder. One thing I need from you, Tina: M-122 is the F-250, and its rear brakes were getting low at the last service. If they measure under 3 mm on Monday, do you want us to go ahead, or call Hal first?\nAngie", edit="d9")
    c.state_extra = {"waits_on": "the customer: the last public line is the shop's question; a reply cannot be sent on Telegram in a live demo and none is owed (ledger conv.live_demo, conv.open_at_t)",
                     "sessions": [{"n": 1, "day": s1, "ended": "resolved by 16"}, {"n": 2, "day": s2, "ended": "resolved by 16"}, {"n": 3, "day": s3, "ended": "resolved by 16"},
                                  {"n": 4, "day": s4, "ended": "open at T, waiting on the customer"}]}
    c.reads_extra = {"operator_credit": "slot 16: the chat's first answer is hers (5.3 minutes, her ledger row is 6); in the four sessions seven replies, five drafts edited, one sent as it was, one cleared; three resolutions of one chat",
                     "new_dialogs": "Stats counts this chat once, in the week it was created: its later sessions are in no 'new dialogs' figure (design section 10, gap 3)"}
    f.truth = {"reason": "company account: weekly bookings, quotes, documents", "handled": "slot 16; the assistant drafts",
               "outcome": "open at T: next Monday's five vans confirmed, one question to the customer unanswered",
               "facts": ["A2 books five vans every Monday at 07:30 through this conversation", "found work on M-112 (front struts and an alignment, 1,119.98 before tax at the fleet rate) was approved the same morning with PO 4398A",
                         "M-108 missed a Monday and was put on a later one", "at T the list for the Monday of week W+1 is confirmed and the shop waits for an answer about M-122's rear brakes",
                         "nothing is overdue on the shop's side"],
               "questions": ["S1.1", "S5.1"]}
    f.why = ["Tina writes like a dispatcher: unit numbers, no greeting after the first week, 'Ugh. Let me ask Hal'.",
             "Angie's lines keep the draft's facts and add what is hers: the name twice, 'if it were my van', a choice, the summary, her name at the end.",
             "A draft the customer overtook is 'replaced before anyone acted' (d4); a thanks that needs no answer is cleared (d6).",
             "The healthy account beside the fading one: same channel mode, minutes instead of days."]
    f.new_facts = ["The Monday lists: week T-22: M-103, M-107, M-110, M-114, M-121; week T-15: five vans, M-112 among them; week T-5: M-104, M-106, M-111, M-115, M-119 (M-108 swapped out); week T-4: M-108 added; week W+1: M-102, M-109, M-113, M-116, M-122.",
                   "M-112's front struts and alignment were done on the Monday of week T-15 for 1,119.98 before tax under purchase order 4398A (the 'front struts back in the summer' of story call 25).",
                   "M-110 pulled to the right in week T-22; M-113's heater is weak in week W0; M-122's rear brakes were low at its last service.",
                   "The photo M112_front_strut.jpg (picture pool 'worn-part-strut').", "The contact's picture: a golden retriever looking out of a truck window."]
    return f


def f06():
    f = File(CFG, 6, "S6", "web-west-nine-days",
             "Nashville: the car that has waited nine days; its owner writes for the fourth time",
             "A web chat: the assistant answers first, cannot read the shop system and hands the question over; from the advisor's first line the chat is his and the assistant only drafts. The weak desk in writing: replies at closing time, a handful of words, a new date each time and no reason. Every draft is discarded. A private note by the other advisor says what is really going on, and the manager's answer to it is one word. At T the fourth message is unanswered, the chat is Urgent by its wait, and a usable draft sits in the box.")
    f.cast = {"customer": {"ref": "named_customers.json en.S6_waiting_nine_days", "name": "Curtis Vaughn", "first_time": False, "phone": "(615) 555-0115"},
              "named_in_a_note": [{"slot": 9, "name": "Marcus Gaines"}, {"vendor": "V2", "name": "Harpeth Valley Parts Supply"}]}
    f.staff(23, 24, 22)
    car = f.day(cal(-9, "the car enters waiting_parts; a full open day"), "the car is dropped off")
    o8 = f.day(cal(-8, "the day after the car came in"), "the part is ordered and he is told Friday; 'last Thursday'")
    m1 = f.day(cal(-7), "message 1")
    m2 = f.day(cal(-5), "message 2 (a Sunday for the nominal T: the shop is closed)")
    c15 = f.day(od("west", -4), "call 15, and the reply to message 2")
    m3 = f.day(cal(-3), "message 3; the other advisor's note")
    d2 = f.day(cal(-2), "the manager's note; the reply to message 3; the day promised in call 15")
    m4 = f.day(cal(-1), "message 4; the missed call and call 16 (west's last full open day before T)")
    f.day(T(), "'Tomorrow is 9 days'")
    f.num_("day 6", "calendar days since the car came in, on the day of message 3")
    f.num_("9 days", "calendar days in waiting_parts at T (ledger s6.waiting_at_t)")
    f.scenario = {
        "who_writes": "A customer whose car has stood at the Charlotte Pike shop since %s, waiting for a part." % car,
        "vehicle": "2012 Volvo XC60 T6 AWD, BRC-7896",
        "waiting_for": "a remanufactured angle gear, ordered from the supplier the shop kept after the purchase, promised twice and moved twice",
        "what_happens": "He writes 7, 5, 3 and 1 days before T and phones on %s and %s (calls design, story calls 15 and 16). Chad answers three times, late, with a date or with nothing. Jasmine asks the manager in a note to order through the home shops' parts manager or tell the customer the truth. The manager writes 'handled'. Nothing changes." % (c15, m4),
        "facts": {"car_in": car,
                  "dates_given": ["Friday, %s (when the part was ordered, %s; outside the chat)" % (m1, o8), "Monday, %s (written, %s)" % (c15, m1),
                                  "the part Tuesday and the car Wednesday, %s (on the phone and in the chat, %s; nothing behind it)" % (d2, c15)],
                  "each_message_waits_over_hours": 4, "at_t": "day 9; the part has no confirmed arrival",
                  "public_pages_used": [],
                  "note": "The assistant cannot read the shop system, so each draft says it has no status and promises only to find out. It never names a date."}}
    f.floating = [fl("today", m1, m1), fl("monday", m1, c15), fl("Monday", m2, c15), fl("first thing Monday", m2, c15), fl("tomorrow", c15, m3), fl("wednesday", c15, d2),
                  fl("today", m3, m3), fl("Friday, then Monday, then Wednesday", m3, "%s, %s, %s" % (m1, c15, d2)), fl("early next week", m3, "T+3d to T+4d"),
                  fl("Tomorrow", m4, "T"), fl("tomorrow morning", m4, "T"), fl("last Thursday", m4, o8)]
    c = web(f, "c1", "west", 733, 6)
    c.c(m1 + " 10:14:20", "Morning. Curtis Vaughn, you have my Volvo XC60. I was told the part would be in today. Any word?")
    c.a("10:14:44", "Good morning, Mr. Vaughn. I'm the assistant for Brennan Auto Care. I can't see the shop's repair orders from here, so I don't have the status of your part. I'll pass your question to the service desk at the Charlotte Pike shop so they can answer you. What's the best number to reach you?")
    c.c("10:15:30", "615 555 0115")
    c.a("10:15:52", "Thank you. Your question is with the team now, and somebody will get back to you as soon as possible.")
    c.h("10:15:53", "escalation", "Curtis Vaughn", "(615) 555-0115", "Charlotte Pike",
        "2012 Volvo XC60, at the Charlotte Pike shop waiting for a part. He was told the part would be in today and asks whether it is. I can't see the repair order, so I gave no status and no date.",
        "west", "%s 17:30, the day's close" % m1)
    c.s(23, "16:52:10", "its not here yet. supplier says monday", late="story: card S06, each message waits over four hours")
    c.c(m2 + " 13:20:15", "Is Monday for sure? I'm paying for a rental by the day.")
    c.d("13:21:00", "d1", "Mr. Vaughn, I'm sorry, I don't have a confirmed arrival for the part in front of me. I'll check with the supplier first thing Monday and message you before noon.")
    c.out(c15 + " 15:40", "calls", "he phones; Chad says the part comes tomorrow and the car is ready Wednesday (calls design, story call 15: wrong_promise, score 25.0)")
    c.s(23, "17:21:30", "like i said on the phone. part tomorrow, car wednesday", late="story: card S06, each message waits over four hours")
    c.c(m3 + " 13:05:15", "Chad said on the phone the part comes in today. Did it?")
    c.c("13:05:40", "This is day 6 with no car.")
    c.d("13:06:25", "d2", "Mr. Vaughn, I'm sorry. You were given dates that did not hold, and that is on us. I don't want to give you another one I can't stand behind. Let me find out exactly where the part is and call you today.")
    c.n(24, "16:05:30", "@Dale Hutchins Mr. Vaughn (XC60, angle gear) has written three times now and called. Harpeth Valley has moved the reman unit twice and today they told me \"early next week\", no tracking number. Chad gave him Friday, then Monday, then Wednesday. Can we order it through Marcus in Chattanooga instead, or at least tell him the truth? He said on the phone he's thinking about towing it out.", mentions=[22])
    c.n(22, d2 + " 08:40:10", "handled")
    c.s(23, "08:55:20", "not in yet. will call u when it is", late="story: card S06, each message waits over four hours")
    c.out(m4 + " 09:20", "calls", "he phones, nobody answers: a missed call, later got_through; the hour is the calls set's to state")
    c.out("14:10", "calls", "he gets through (calls design, story call 16: existing job, no score; repeat_caller, complaint; his question about 'the other thing' is not asked about); the hour is the calls set's to state")
    c.c("16:48:05", "This is the fourth time I'm writing. Tomorrow is 9 days. Is the part on a truck or not? I need a straight answer.")
    c.c("16:48:20", "I've been paying for a rental since last Thursday.")
    c.d("16:49:05", "d3", "Mr. Vaughn, you're right to be frustrated, and I'm sorry. Three dates we gave you did not hold. I don't have a confirmed arrival for the part, and I won't give you a fourth guess. Our shop manager will call you tomorrow morning with exactly where the part is.")
    c.state_extra = {"live_demo": "a web chat, so the waiting draft can be edited and sent in a live demo (ledger conv.live_demo, conv.open_at_t)",
                     "shown_why": "the wait: 42 working minutes on the last open day and the two hours of T's morning at the shop"}
    c.reads_extra = {"operator_credit": "the chat's first answer is nobody's (the assistant wrote it); slot 23: his first line {first} working minutes after the hand-off, three replies, two drafts discarded, nothing resolved; slots 24 and 22 wrote notes only, which count nowhere"}
    f.truth = {"reason": "is my car ready, has the part come", "handled": "assistant first, handed over (escalation), slot 23; notes by 24 and 22",
               "outcome": "open at T, owned by slot 23, urgent by its wait, unread, one unsent draft",
               "facts": ["four messages, 7, 5, 3 and 1 days before T, each waiting over four hours for a person's reply; the fourth unanswered at T",
                         "slot 23 wrote 'supplier says monday', then 'part tomorrow, car wednesday', then 'will call u when it is'",
                         "the Wednesday promise repeats call 15's and had nothing behind it; the car is still waiting at T",
                         "slot 24 told the manager in a note that the supplier has moved the part twice and now says early next week, and proposed ordering through the home shops; slot 22 answered 'handled'",
                         "he has paid for a rental since the day after the car came in"],
               "questions": ["S6.5", "S6.2"]}
    f.why = ["Chad's three replies are twenty-five words together and none of them says why.",
             "The customer goes from 'Morning.' to counting days and money; he never swears in writing.",
             "The note is the only place the supplier is named, and it sits two lines above 'handled'.",
             "The drafts get better as the customer gets angrier, and the outcome rows say nobody used one."]
    f.new_facts = ["The first date, Friday, was given to him when the part was ordered, on the day after the car came in, outside the chat and outside any hand-written call (call 15: 'Fella told me Friday').",
                   "ERP: the purchase order for the angle gear was promised for 7 days before T, then for west's 4th full open day before T; on the day of message 3 the supplier said 'early next week' with no tracking number.",
                   "Chad repeated call 15's promise in writing at 17:21 on the day of the call.",
                   "He has a rental car since 8 days before T.",
                   "The missed call (09:20) and call 16 (14:10) are shown at assumed hours; message 4 is written after call 16."]
    return f


def f07():
    f = File(CFG, 7, "S13", "web-stocktake-question",
             "The stocktake afternoon, asked on the website: the assistant answers alone",
             "Web chat, assistant sends: two customer lines, two answers from the dated hours, no person. The chat stays the assistant's: pending at T, in All with the Agent mark, owed nothing.")
    f.cast = {"customer": {"name": "Website visitor", "invented": True, "first_time": True}}
    f.cast["staff"] = []
    q = f.day(wk("Mon", 0), "the customer's question (card S13: the Monday of week W0 when it is before T)")
    st = f.day(wk("Thu", -1), "the stocktake: every shop closes at 12:00")
    f.scenario = {
        "who_writes": "Somebody who wants an oil change on a particular afternoon.",
        "what_happens": "He asks whether the shop is open on the afternoon of the stocktake day. The assistant says no, why, and what is open; offers a hand-over for a morning time; does not push when it is declined.",
        "facts": {"stocktake": "the Thursday of week W+1: every shop closes at 12:00 (card S13; ledger site.stocktake). Nominal: Thursday 2026-11-19.",
                  "hours_weekday": "7:30 to 17:30", "public_pages_used": ["hours and locations, with the dated closure"]}}
    f.floating = [fl("thursday the 19th", q, st), fl("Thursday the 19th", q, st), fl("friday", q, "not fixed: he may mean either Friday, and the assistant does not guess"),
                  fl("Fridays", q, "any Friday")]
    c = web(f, "c1", "main", 412, 7)
    c.c(q + " 12:47:10", "are yall open thursday the 19th in the afternoon? need an oil change")
    c.a("12:47:31", "Hi! On Thursday the 19th all three Brennan Auto Care shops close at noon for our twice-a-year inventory count, so there's no afternoon service that day. That morning we're open from 7:30, and every other weekday it's the usual 7:30 to 5:30. Would you like me to ask the shop to set up a morning time for you?")
    c.c("12:48:40", "nah mornings dont work. ill just come friday. thx")
    c.a("12:49:02", "Sounds good. Fridays are regular hours, 7:30 to 5:30. Have a good one!")
    c.state_extra = {"shown_as": "in All with the Agent mark; not in the Queue: nobody is owed an answer",
                     "later": "Chatwoot resolves it after 7 silent days, three days after T: not in the data"}
    c.reads_extra = {"operator_credit": "nobody: the assistant is not an operator"}
    f.truth = {"reason": "hours, address, do you work on this", "handled": "the assistant alone", "outcome": "answered; pending at T, the assistant's",
               "facts": ["no: every shop closes at 12:00 that day for the stocktake", "the morning is open from 7:30", "a hand-over for a morning time was offered and declined"],
               "questions": ["S13.1", "S13.3"]}
    f.why = ["It is as short as these really are.", "The assistant offers a hand-over for a morning time and does not push when it is declined.",
             "The answer to 'are we open that afternoon' is here in the assistant's words and in file 08 in a person's."]
    f.new_facts = []
    f.extra = {"disagrees_with": "DESIGN.md section 6 puts this chat on the 2nd full open day before T; card S13 puts it on the Monday of week W0 when that day is before T. The card is followed. The card's footprint says 'resolved'; the ledger (conv.open_at_t) and the design name it as pending at T, and it is pending here: under seven silent days have passed."}
    return f


def f08():
    f = File(CFG, 8, "S13", "telegram-stocktake-regular",
             "The stocktake afternoon, asked on Telegram: the assistant drafts and the advisor edits and sends",
             "A drafts-only channel: the draft is correct and plain; the east shop's lead advisor keeps its facts and rewrites it in her own voice, twice. Both outcomes are sent_edited.")
    f.cast = {"customer": {"name": "Patsy Greer", "invented": True, "first_time": False,
                           "note": "a regular of the Bonny Oaks shop; 2013 Buick Enclave; rear brakes were recommended at her last visit"}}
    f.staff(16)
    q = f.day(wd(16, -1), "slot 16's last working day before T")
    st = f.day(wk("Thu", -1), "the stocktake: every shop closes at 12:00")
    fr = f.day(wk("Fri", -1), "the day after the stocktake; her appointment")
    f.scenario = {
        "who_writes": "A regular who writes to Angie by name.",
        "vehicle": "2013 Buick Enclave",
        "what_happens": "She asks to drop the car off on the stocktake afternoon. Angie turns the draft's 'closed' into two times to choose from, and her second message is the summary.",
        "facts": {"stocktake": "the Thursday of week W+1: every shop closes at 12:00 (card S13; ledger site.stocktake)", "hours_weekday": "7:30 to 17:30",
                  "booked": "the Friday of week W+1, 13:00 at east; ERP appointment, source messenger", "public_pages_used": ["hours and locations, with the dated closure"]}}
    f.floating = [fl("the 19th", q, st), fl("Thursday the 19th", q, st), fl("Thursday at 7:30", q, st), fl("Friday the 20th", q, fr), fl("Friday at 1", q, fr)]
    c = tg(f, "c1", "east", 805, "Patsy Greer", avatar=pic("car", "a white Buick Enclave in a driveway under a carport", matches="2013 Buick Enclave"),
           opened_note="in the full seed this is a later session of her one Telegram conversation; here it stands alone")
    c.c(q + " 09:12:10", "Morning Angie! Can I drop the Buick off the 19th after lunch for those back brakes")
    c.d("09:12:55", "d1", "Good morning! On Thursday the 19th all our shops close at noon for inventory, so we can't take the car in that afternoon. That morning we're open from 7:30, and the rest of the week is regular hours, 7:30 to 5:30. Would a morning drop-off work for you?")
    c.s(16, "09:17:30", "Good morning, Patsy! Thursday the 19th we close at noon for inventory, so the afternoon's out. If it were my car I wouldn't put those rear brakes off much longer anyway. I can take the Buick Thursday at 7:30 and have it back to you by 11, or Friday the 20th at 1:00. Which is easier for you, Patsy?\nAngie", edit="d1")
    c.c("09:25:05", "Friday at 1 👍")
    c.d("09:25:50", "d2", "Thank you, Patsy. Friday the 20th at 1:00 works. See you then!")
    c.s(16, "09:27:40", "You're all set, Patsy: Friday the 20th at 1:00, rear brakes on the Enclave, here at Bonny Oaks. I'll message you when it's ready, should be by 4.\nAngie", edit="d2")
    c.label(16, "09:28:00", "booking")
    c.res(16, "09:28:20")
    c.reads_extra = {"operator_credit": "slot 16: first answer {first} minutes (her ledger row is 6), two replies, two drafts edited, one resolved"}
    f.truth = {"reason": "to book or ask for a slot", "handled": "slot 16; the assistant drafts", "outcome": "booked for the day after the stocktake, 13:00, at east; resolved by slot 16",
               "facts": ["the shop closes at 12:00 on the stocktake day, so the afternoon she asked for is not possible", "slot 16 offered that morning at 7:30 or the next day at 1:00",
                         "she chose the next day at 1:00"],
               "questions": ["S13.1"]}
    f.why = ["The draft and what Angie sent say the same facts. Hers has the customer's name twice, 'if it were my car', two times to choose from, and her name at the end.",
             "Her second message is the summary: day, time, work, car, shop."]
    f.new_facts = ["Patsy Greer, a regular of the Bonny Oaks shop, 2013 Buick Enclave, rear brakes recommended at her last visit; an appointment on the Friday of week W+1 at 13:00.",
                   "Both times Angie offers lie inside the week she has asked off (S5); her shifts on those two days are published and the request is undecided, so she is still on the roster.",
                   "The contact's picture: a white Buick Enclave under a carport."]
    return f


FILES = [f01, f02, f03, f04, f05, f06, f07, f08]
