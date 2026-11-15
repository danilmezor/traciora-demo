# -*- coding: utf-8 -*-
"""English conversations 9 to 27: two per advisor (slots 5, 6, 7, 16, 17, 22, 23, 24) and three for rule R13."""
from srclib import *

CFG = "en"


def fl(word, said_on, day, **kw):
    return dict(word=word, said_on=said_on, day=day, **kw)


def cust(name, note, first_time=False, phone=None):
    row = {"name": name, "invented": True, "first_time": first_time, "note": note}
    if phone:
        row["phone"] = phone
    return row


GREET = "Hi! I'm the assistant for Brennan Auto Care. "
SAID = "Your request is with the team now, and somebody will get back to you as soon as possible."


def f09():
    f = File(CFG, 9, "people", "p05-telegram-out-the-door",
             "The lead advisor at the flagship on Telegram: is the truck done, and why is the number bigger",
             "Slot 5 in writing: a first reply after 13 minutes, typed slowly with the typos left in, the out-the-door number and the pick-up time in one line, 'call me, easier' when a question takes more than a line. He writes his own text over two drafts and sends the third as it was. He does not resolve; Chatwoot does, a week later.")
    f.cast = {"customer": cust("Darryl Poteet", "a regular of the East Main shop; 2011 Chevrolet Silverado 1500; an alternator replaced that day")}
    f.staff(5)
    d = f.day(wk("Thu", 18))
    f.day(wk("Thu", 18, plus=7), "Chatwoot resolves the chat after 7 silent days")
    f.p("766", "alternator replaced, class truck, standard parts, list (766.37)", job="alternator", cls="truck")
    f.p("$766.37", "the same, to the cent", job="alternator", cls="truck")
    otd = f.p("$852.01", "the same with shop supplies and sales tax: out the door", job="alternator", cls="truck", supplies=True, tax=True)
    f.num_("852", "the customer's rounding of the out-the-door figure")
    f.scenario = {"who_writes": "A regular, from a job site, about a truck left that morning.", "vehicle": "2011 Chevrolet Silverado 1500",
                  "what_happens": "He asks if the truck is done. Travis gives the state, the out-the-door figure and the time. The figure is higher than the one he heard on the phone; Travis says why in a line and offers the phone. He comes at 4.",
                  "facts": {"main_line": "(423) 555-0142 (phones.md)", "public_pages_used": []}}
    f.floating = []
    c = tg(f, "c1", "main", 2114, "Darryl Poteet", avatar=pic("car", "a red Chevrolet Silverado parked at a boat ramp", matches="2011 Chevrolet Silverado 1500"),
           opened_note="in the full seed this is a later session of his one Telegram conversation; here it stands alone")
    c.c(d + " 14:02:10", "hey travis is the silverado done")
    c.d("14:02:55", "d1", "Hi Darryl. I don't have the status of the Silverado in front of me. I'll check with the shop and message you right back.")
    c.s(5, "14:15:30", "almost. alternator is in and chargin good, there road testing it now. $852.01 out the door, ready at 4")
    c.c("14:17:05", "852?? you told me 766 on the phone")
    c.d("14:17:50", "d2", "Darryl, the $766.37 was the alternator job before shop supplies and sales tax. With those it comes to $852.01. I'm sorry that wasn't clear on the phone.")
    c.s(5, "14:24:10", "766 was before tax and shop supplies. same job nothing added. call me if its easier 423 555 0142")
    c.c("14:26:40", "nah im good. see you at 4")
    c.d("14:27:20", "d3", "Sounds good, Darryl. See you at 4:00.")
    c.s(5, "14:31:00", "Sounds good, Darryl. See you at 4:00.", use="d3")
    c.auto()
    c.reads_extra = {"operator_credit": "slot 5: first answer {first} minutes (his ledger row is 14), three replies, two drafts discarded and one sent as it was, nothing resolved"}
    f.truth = {"reason": "is my car ready, has the part come", "handled": "slot 5; the assistant drafts", "outcome": "ready at 4:00; 852.01 out the door; resolved by 7 silent days",
               "facts": ["the alternator job is 766.37 at list for a truck; with shop supplies and tax 852.01", "the customer had heard the figure before tax on the phone", "slot 5 did not resolve the chat"], "questions": []}
    f.why = ["'chargin good, there road testing it now': slow thumbs, typos left in, and still the two things a customer needs: the total and the time.",
             "The second draft explains the bill better than he does; he writes his own and offers the phone.", "The third draft is one he can use, and he does."]
    f.new_facts = ["Darryl Poteet, 2011 Chevrolet Silverado 1500, alternator replaced on the Thursday of week T-18 at main: 766.37 at list, 852.01 with shop supplies and tax; he was given the pre-tax figure on the phone that morning.",
                   "The contact's picture: a red Chevrolet Silverado at a boat ramp."]
    return f


def f10():
    f = File(CFG, 10, "people", "p05-web-puddle-photo",
             "A photo instead of words: a puddle under the car, the assistant, and the lead advisor's comparison",
             "A symptom on the web chat. The customer opens with a picture; the assistant reads it, says what it cannot tell, names the test and its price, and hands over. Slot 5 takes it after 15 minutes: one long lower-case line with a time, a warning, a comparison and the price. The assistant's closing draft goes out as it was. He labels and resolves this one.")
    f.cast = {"customer": cust("Kim Ledford", "2012 Ford Escape; first visit", first_time=True, phone="(423) 555-0274")}
    f.staff(5)
    d = f.day(wk("Mon", 8))
    f.p("$67.50", "cooling system pressure test (0.5 h at the posted hour)", job="cooling_pressure_test")
    f.scenario = {"who_writes": "A first-time customer, at lunch, standing in her garage.", "vehicle": "2012 Ford Escape",
                  "what_happens": "A photo of a green puddle, then 'is this bad'. The assistant names the likely fluid without diagnosing, asks the car and the gauge, prices the test, takes her name, number and shop, hands over. Travis offers 2:00 the same day.",
                  "facts": {"public_pages_used": ["price list: cooling system pressure test", "hours and locations"], "booked": "%s 14:00 at main" % d, "main_line": "(423) 555-0142"}}
    f.floating = [fl("today", d, d)]
    c = web(f, "c1", "main", 318, 10)
    c.c(d + " 12:31:05", "", files=[{"kind": "image", "file": "IMG_2087.jpg", "pool": "puddle-under-car", "shows": "a green puddle on a garage floor under the front bumper of a car"}])
    c.c("12:31:20", "is this bad")
    c.a("12:31:45", GREET + "Thanks for the photo. A green puddle under the front of a car is usually coolant, though I can't diagnose it from a picture. If the temperature gauge climbs or a warning light comes on, stop driving. What kind of car is it, and has the gauge moved?")
    c.c("12:32:30", "2012 ford escape. gauge is normal so far")
    c.a("12:32:55", "Good. The way to find a leak like that is a cooling system pressure test, which is $67.50. The technician shows you where it's coming from before any repair is priced. Would you like me to ask the shop to get you in?")
    c.c("12:33:20", "yes today if they can")
    c.a("12:33:44", "I can't book a time myself, but I'll pass it on. What's your name and the best number to reach you, and which shop: East Main Street or Bonny Oaks Drive?")
    c.c("12:34:15", "Kim Ledford 423-555-0274 east main")
    c.a("12:34:40", "Thank you, Kim. " + SAID)
    c.h("12:34:41", "scheduling", "Kim Ledford", "(423) 555-0274", "east main",
        "2012 Ford Escape. She sent a photo of a green puddle under the front of the car and asked if it is bad; the temperature gauge is normal so far. I named the cooling system pressure test, $67.50, and no repair. She would like to come today, East Main Street.",
        "main", "%s 17:30, the day's close" % d)
    c.s(5, "12:50:10", "Kim this is Travis at east main. bring it on by today, I can get it on the lift at 2. dont top it off with water and dont drive it far, a cooling system is like a pressure cooker, it only works sealed up. test is $67.50. call me if its easier 423 555 0142")
    c.c("12:52:30", "ok be there at 2. thanks")
    c.d("12:53:10", "d1", "You're welcome, Kim. See you at 2:00 at 2106 East Main Street.")
    c.s(5, "12:58:40", "You're welcome, Kim. See you at 2:00 at 2106 East Main Street.", use="d1")
    c.label(5, "12:59:10", "booking")
    c.res(5, "12:59:30")
    c.reads_extra = {"operator_credit": "the chat's first answer is nobody's; slot 5: his first line {first} minutes after the hand-off, two replies, one draft sent as it was, one resolved"}
    f.truth = {"reason": "a symptom", "handled": "assistant first, handed over (scheduling), slot 5", "outcome": "pressure test booked the same day, 14:00, at main; resolved by slot 5",
               "facts": ["the customer opened with a photo; the assistant said what it showed and that it could not diagnose", "the only price named is the pressure test, 67.50", "slot 5 replied {first} working minutes after the hand-off"], "questions": []}
    f.why = ["The assistant reads a photo, and stops at 'usually coolant'.", "Travis explains with a kitchen: 'like a pressure cooker, it only works sealed up'.",
             "His reply is slower than the junior's and nobody would mind: it has a time in it."]
    f.new_facts = ["Kim Ledford, (423) 555-0274 (tier B of phones.md), 2012 Ford Escape; a cooling system pressure test at main on the Monday of week T-8 at 14:00.", "The photo IMG_2087.jpg (picture pool 'puddle-under-car')."]
    return f


def f11():
    f = File(CFG, 11, "people", "p06-telegram-found-work",
             "The junior operator on Telegram: found work, two photos, a yes and a no",
             "Slot 6 in writing: four minutes to a first reply, complete sentences, the urgent thing first with its price, the other offered without pressure, a pick-up time, at most one exclamation mark a message. She builds on two drafts and sends the third as it was; she labels and resolves.")
    f.cast = {"customer": cust("Shonda Ellis", "a customer of the East Main shop; 2015 Kia Sorento, in for an oil change")}
    f.staff(6)
    d = f.day(wk("Tue", 11))
    f.p("$260.31", "rear brake pads, class suv, standard parts", job="rear_brake_pads", cls="suv")
    f.p("$67.94", "cabin air filter, class suv", job="cabin_air_filter", cls="suv")
    f.num_("3 mm", "what the rear pads measured; new pads are about 10 mm")
    f.scenario = {"who_writes": "A customer whose car is in for an oil change, from her desk.", "vehicle": "2015 Kia Sorento",
                  "what_happens": "She asks for news. Maya has two findings with photos: rear pads at 3 mm, and a cabin filter full of leaves. The customer takes the brakes and keeps the filter for herself.",
                  "facts": {"approved": "rear brake pads, 260.31", "declined": "cabin air filter, 67.94", "public_pages_used": []}}
    f.floating = [fl("today", d, d)]
    c = tg(f, "c1", "main", 2291, "Shonda E.", opened_note="in the full seed this is a later session of her one Telegram conversation; here it stands alone")
    c.c(d + " 11:05:10", "hey Maya its Shonda. any news on the sorento?")
    c.d("11:05:55", "d1", "Hi Shonda! I don't have the status of the Sorento in front of me. I'll check with the technician and message you right back.")
    c.s(6, "11:09:20", "Hi Shonda, good timing. The oil change is done and the inspection found two things, photos below. The rear brake pads are down to 3 mm, and that one I wouldn't put off: $260.31, about an hour. The cabin air filter is full of leaves, $67.94, and that can wait if you'd rather. Want us to go ahead with either one today?",
        files=[{"kind": "image", "file": "sorento_rear_pad.jpg", "pool": "worn-pad", "shows": "a rear brake pad held next to a new one, a thin strip of friction material left"},
               {"kind": "image", "file": "sorento_cabin_filter.jpg", "pool": "dirty-cabin-filter", "shows": "a cabin air filter grey with dust, dry leaves in the pleats"}], edit="d1")
    c.c("11:12:40", "do the brakes. ill do the filter myself lol")
    c.d("11:13:25", "d2", "Sounds good, Shonda. We'll do the rear brake pads today, $260.31, and leave the cabin filter. We'll message you when it's ready.")
    c.s(6, "11:14:50", "Sounds good, Shonda. We'll do the rear pads today, $260.31, and leave the cabin filter to you. It'll be ready by 1:30, and I'll message you here when it's done!", edit="d2")
    c.label(6, "11:15:10", "approval")
    c.s(6, "13:24:30", "The Sorento is ready whenever you are, Shonda. We're here until 5:30.")
    c.c("13:30:15", "omw")
    c.d("13:30:55", "d3", "See you soon, Shonda!")
    c.s(6, "13:31:40", "See you soon, Shonda!", use="d3")
    c.res(6, "13:32:00")
    c.reads_extra = {"operator_credit": "slot 6: first answer {first} minutes (her ledger row is 4), four replies, two drafts edited and one sent as it was, one resolved"}
    f.truth = {"reason": "found work: approve or decline", "handled": "slot 6; the assistant drafts", "outcome": "rear brake pads approved (260.31), cabin air filter declined; resolved by slot 6",
               "facts": ["two findings, each with a photo", "approved: rear brake pads; declined: the cabin air filter", "ready by 1:30, as said"], "questions": []}
    f.why = ["The first draft has nothing in it, because the assistant cannot see the car; Maya keeps the greeting and writes the rest.",
             "Urgent thing first, with its reason and its price; the second thing offered, not pushed.", "She tells the customer when, and then does it."]
    f.new_facts = ["Shonda Ellis (Telegram name 'Shonda E.'), 2015 Kia Sorento, at main on the Tuesday of week T-11: oil change; rear brake pads approved, 260.31; cabin air filter declined, 67.94.",
                   "The photos sorento_rear_pad.jpg and sorento_cabin_filter.jpg (picture pools 'worn-pad', 'dirty-cabin-filter').", "The contact has no picture."]
    return f


def f12():
    f = File(CFG, 12, "people", "p06-web-moved-booking",
             "A booking moved, and a price doubt the junior operator steps over",
             "Slot 6's weak spot in writing, as in her calls: a time first and a clean summary, and when the customer says another shop is cheaper she soothes ('I totally understand') and does not answer. The draft she wrote over had the answer. The booking holds anyway; she sends the closing draft as it was, labels, resolves.")
    f.cast = {"customer": cust("Andre Tate", "a customer of the East Main shop with an alignment booked for the Monday", phone="(423) 555-0318")}
    f.staff(6)
    d = f.day(wk("Fri", 5))
    f.day(wk("Mon", 4), "the booking he moves")
    f.day(wk("Thu", 4), "the new day")
    f.p("$119.95", "four-wheel alignment, menu price", job="wheel_alignment")
    f.num_("120", "the customer's rounding of 119.95")
    f.num_("89", "what another shop is said to charge; the customer's claim")
    f.scenario = {"who_writes": "A customer with an appointment he cannot keep.", "what_happens": "He asks to move Monday's alignment. The assistant cannot see appointments and hands over. Maya moves it and offers two times; he takes Thursday at 8:00 and asks whether the price is really 120 when another shop charges 89. She reassures him and confirms the time.",
                  "facts": {"moved_to": "the Thursday of week T-4, 08:00, at main", "public_pages_used": ["price list: four-wheel alignment"]}}
    f.floating = [fl("monday", d, "the Monday of week T-4"), fl("wednesday", d, "the Wednesday of week T-4"), fl("Thursday at 8:00", d, "the Thursday of week T-4"), fl("Friday at 10:30", d, "the Friday of week T-4")]
    c = web(f, "c1", "main", 455, 12)
    c.c(d + " 08:50:10", "hi i have an appointment monday for an alignment and i need to move it")
    c.a("08:50:33", GREET + "I can't see or change appointments from here, but I'll pass this to the service desk so they can move it. What's your name, the best number for you, and which shop is the appointment at?")
    c.c("08:51:15", "Andre Tate. 423 555 0318. east main")
    c.c("08:51:30", "any day after wednesday works")
    c.a("08:51:54", "Thank you, Andre. " + SAID)
    c.h("08:51:55", "scheduling", "Andre Tate", "(423) 555-0318", "east main",
        "Andre Tate has an alignment booked at East Main on Monday and needs to move it; any day after Wednesday works. I can't see the appointment, so I changed nothing.",
        "main", "%s 17:30, the day's close" % d)
    c.s(6, "08:55:40", "Good morning Andre, this is Maya at East Main. I've moved your alignment off Monday. I can do Thursday at 8:00 or Friday at 10:30, and it takes about an hour either way. Which one would you like?")
    c.c("08:58:20", "thursday at 8. also is it really 120 for an alignment? place by my work said 89")
    c.d("08:59:00", "d1", "Thursday at 8:00 it is, Andre. Our four-wheel alignment is $119.95: all four wheels are measured and adjusted. I can't speak for another shop's price, but I'm glad to tell you what ours covers.")
    c.s(6, "09:01:10", "I totally understand, Andre, nobody likes paying more than they have to. You're all set for Thursday at 8:00 at East Main, and we'll take good care of it!")
    c.c("09:03:30", "ok")
    c.d("09:04:10", "d2", "See you Thursday at 8:00, Andre: 2106 East Main Street.")
    c.s(6, "09:05:00", "See you Thursday at 8:00, Andre: 2106 East Main Street.", use="d2")
    c.label(6, "09:05:20", "booking")
    c.res(6, "09:05:40")
    c.reads_extra = {"operator_credit": "the chat's first answer is nobody's; slot 6: her first line {first} minutes after the hand-off, three replies, one draft discarded and one sent as it was, one resolved"}
    f.truth = {"reason": "moving or cancelling a booking", "handled": "assistant first, handed over (scheduling), slot 6", "outcome": "alignment moved from Monday to Thursday 08:00; resolved by slot 6",
               "facts": ["the booking was moved by slot 6 four minutes after the hand-off", "the customer voiced a price doubt (120 against 89 elsewhere) and it was not answered: she reassured and confirmed the time",
                         "the alignment is 119.95"], "questions": []}
    f.why = ["'I totally understand' is where an answer should be; her call scores show the same thing (story S4, objection).", "The discarded draft is the better reply, and the outcome row is the evidence.",
             "Everything else is her at her best: four minutes, two times, the address in the last line."]
    f.new_facts = ["Andre Tate, (423) 555-0318 (tier B), an alignment at main moved from the Monday to the Thursday of week T-4, 08:00."]
    return f


def f13():
    f = File(CFG, 13, "people", "p07-telegram-first-of-two",
             "The newcomer on Telegram: two questions in one message, and he answers the first",
             "Slot 7 in writing: polite, short, an exclamation mark, and of two questions the first. He sends what he is given: three drafts go out untouched, and the one time he types for himself he drops half the question, so the customer has to ask again. He resolves.")
    f.cast = {"customer": cust("Brianna Cagle", "2016 Nissan Altima; first visit", first_time=True)}
    f.staff(7, s7={"weeks_in_the_job": 3})
    d = f.day(wk("Thu", 12))
    f.day(wk("Fri", 12), "'tomorrow'")
    f.p("$90.95", "full synthetic oil and filter change, class car", job="oil_service")
    f.scenario = {"who_writes": "Somebody new, writing between other things.", "vehicle": "2016 Nissan Altima",
                  "what_happens": "Price and whether to book: the draft answers both and Caleb sends it. Then 'tomorrow morning, and can I wait there': he types 'Yes ma'am, tomorrow at 8:30 works!' and the second half has to be asked again; the next draft answers it and he sends it.",
                  "facts": {"booked": "the Friday of week T-12, 08:30, at main", "oil_change_hours": "0.5 (catalogue): 'about half an hour'", "public_pages_used": []}}
    f.floating = [fl("tomorrow morning", d, "the Friday of week T-12"), fl("tomorrow at 8:30", d, "the Friday of week T-12")]
    c = tg(f, "c1", "main", 2407, "Brianna C.")
    c.c(d + " 09:40:10", "Hi! How much is an oil change for a 2016 altima and do i need an appointment")
    c.d("09:40:55", "d1", "Hi! A full synthetic oil and filter change on a 2016 Altima is $90.95. It's best to book a time so the car isn't waiting. Which day works for you?")
    c.s(7, "09:48:30", "Hi! A full synthetic oil and filter change on a 2016 Altima is $90.95. It's best to book a time so the car isn't waiting. Which day works for you?", use="d1")
    c.c("09:51:05", "tomorrow morning? and can i wait there while yall do it or should i get a ride")
    c.d("09:51:50", "d2", "Tomorrow morning works; I'll confirm the exact time. An oil change takes about half an hour, so you're welcome to wait here.")
    c.s(7, "09:55:10", "Yes ma'am, tomorrow at 8:30 works!")
    c.c("09:57:40", "ok and can i wait there?")
    c.d("09:58:25", "d3", "Yes, you're welcome to wait. An oil change takes about half an hour.")
    c.s(7, "10:03:00", "Yes, you're welcome to wait. An oil change takes about half an hour.", use="d3")
    c.c("10:04:10", "great see you then")
    c.d("10:04:50", "d4", "See you tomorrow at 8:30!")
    c.s(7, "10:09:20", "See you tomorrow at 8:30!", use="d4")
    c.res(7, "10:09:50")
    c.reads_extra = {"operator_credit": "slot 7: first answer {first} minutes (his ledger row is 9), four replies, three drafts sent as they were and one discarded, one resolved"}
    f.truth = {"reason": "what a job costs", "handled": "slot 7; the assistant drafts", "outcome": "oil change booked for the next morning, 08:30; resolved by slot 7",
               "facts": ["the price given is 90.95", "of two questions in one message slot 7 answered the first; the second was asked again and answered by a draft sent as it was", "no name or number was asked for"], "questions": []}
    f.why = ["The draft he discarded answered both questions; his own line answered one.", "Three of four drafts go out untouched: the share his ledger row gives him.",
             "He never asks who she is; on a messenger the name comes with the chat."]
    f.new_facts = ["Brianna Cagle (Telegram name 'Brianna C.'), 2016 Nissan Altima, an oil change at main on the Friday of week T-12 at 08:30.", "The contact has no picture."]
    return f


def f14():
    f = File(CFG, 14, "people", "p07-web-sends-what-he-is-given",
             "The newcomer takes a hand-over: 'should', and a draft that sends the customer back to him",
             "A booking on the web chat. The assistant gives the public price, cannot book, hands over. Slot 7 answers in nine minutes with a time, an exclamation mark and two 'should's. Asked whether the price is the total, the assistant drafts that the advisor can give the exact figure, and the advisor sends that sentence as it was.")
    f.cast = {"customer": cust("Jerome Pruitt", "2017 Toyota Camry; first visit", first_time=True, phone="(423) 555-0391")}
    f.staff(7, s7={"weeks_in_the_job": 11})
    d = f.day(wk("Tue", 3))
    f.day(wk("Wed", 3), "'tomorrow'")
    f.p("$151.00", "brake fluid flush, class car", job="brake_fluid_exchange")
    f.num_("151", "the customer's way of writing 151.00")
    f.scenario = {"who_writes": "A first-time customer who knows which service he wants.", "vehicle": "2017 Toyota Camry",
                  "what_happens": "Price from the list, a hand-over, 'tomorrow at 10:00'. His one question about the total gets a sentence that answers nothing; he lets it go.",
                  "facts": {"booked": "the Wednesday of week T-3, 10:00, at main", "the_exact_total": "151.00 + 6.75 shop supplies, 172.34 with tax; nobody tells him", "public_pages_used": ["price list: brake fluid flush"]}}
    f.floating = [fl("tomorrow", d, "the Wednesday of week T-3"), fl("tomorrow at 10:00", d, "the Wednesday of week T-3")]
    c = web(f, "c1", "main", 512, 14)
    c.c(d + " 15:12:05", "need a brake fluid flush. do yall do those and how much")
    c.a("15:12:28", GREET + "Yes, we do. A brake fluid flush is $151.00 before shop supplies and tax. Would you like me to ask the shop to set up a time?")
    c.c("15:13:00", "yeah tomorrow if possible. 2017 camry")
    c.a("15:13:24", "I can't book a time myself, but I'll pass it on. What's your name and the best number to reach you, and which shop works better: East Main Street or Bonny Oaks Drive?")
    c.c("15:13:55", "Jerome Pruitt 4235550391. east main")
    c.a("15:14:18", "Thank you, Jerome. " + SAID)
    c.h("15:14:19", "scheduling", "Jerome Pruitt", "(423) 555-0391", "east main",
        "Jerome Pruitt, 2017 Toyota Camry. He wants a brake fluid flush tomorrow if possible, East Main Street. I gave the price-list figure, $151.00 before shop supplies and tax.",
        "main", "%s 17:30, the day's close" % d)
    c.s(7, "15:23:40", "Hi Jerome, Caleb at East Main. Yes sir, we can get you in tomorrow at 10:00! Should take about an hour so you should be out by lunch")
    c.c("15:25:10", "cool. is 151 the total or is there more on top")
    c.d("15:25:50", "d1", "Good question, Jerome. $151.00 is the price of the flush. Shop supplies and sales tax are added on the bill, so the total will be a little higher; the advisor can give you the exact figure.")
    c.s(7, "15:31:20", "Good question, Jerome. $151.00 is the price of the flush. Shop supplies and sales tax are added on the bill, so the total will be a little higher; the advisor can give you the exact figure.", use="d1")
    c.c("15:33:05", "ok. see you at 10")
    c.d("15:33:45", "d2", "See you tomorrow at 10:00, Jerome: 2106 East Main Street.")
    c.s(7, "15:38:30", "See you tomorrow at 10:00, Jerome: 2106 East Main Street.", use="d2")
    c.res(7, "15:39:00")
    c.reads_extra = {"operator_credit": "the chat's first answer is nobody's; slot 7: his first line {first} minutes after the hand-off, three replies, two drafts sent as they were, one resolved"}
    f.truth = {"reason": "to book or ask for a slot", "handled": "assistant first, handed over (scheduling), slot 7", "outcome": "brake fluid flush booked for the next day, 10:00; resolved by slot 7",
               "facts": ["the price given is 151.00 before shop supplies and tax", "asked for the total, slot 7 sent the assistant's draft unchanged, which says the advisor can give the exact figure; nobody gave it"], "questions": []}
    f.why = ["'Should take about an hour so you should be out by lunch.'", "A draft is written for a person to finish. Sent as it was, by the advisor, it tells the customer to ask the advisor.",
             "No label: he labels about half his chats."]
    f.new_facts = ["Jerome Pruitt, (423) 555-0391 (tier B), 2017 Toyota Camry, a brake fluid flush at main on the Wednesday of week T-3 at 10:00."]
    return f


def f15():
    f = File(CFG, 15, "people", "p16-telegram-brake-squeal",
             "A complaint to the all-star: brakes that squeal a week after the job",
             "Slot 16 in writing: the customer's name twice, 'if it were my car', two times to choose from, a summary, her name at the end. She raises the chat to High herself, books a free check under the warranty, and after it tells the customer what was wrong in plain words, including that it was the shop's doing. Two drafts edited, one written over; labelled and resolved.")
    f.cast = {"customer": cust("Gloria Simmons", "a regular of the Bonny Oaks shop; 2014 Toyota Highlander; front brakes done the week before")}
    f.staff(16)
    d = f.day(wk("Wed", 15))
    f.scenario = {"who_writes": "A regular who does not like to complain.", "vehicle": "2014 Toyota Highlander",
                  "what_happens": "The brakes fitted last week squeal at every stop. Angie thanks her for saying so, offers today at 1:00 or tomorrow at 7:30, no charge. In the afternoon the customer asks what it was: an anti-rattle clip not seated on one side.",
                  "facts": {"warranty": "24 months or 24,000 miles on parts and labour (ledger s12.warranty)", "found": "an anti-rattle clip not fully seated; both sides reseated, road tested", "public_pages_used": []}}
    f.floating = [fl("last week", d, "the week T-16"), fl("today at 1:00", d, d), fl("tomorrow at 7:30", d, "the Thursday of week T-15")]
    c = tg(f, "c1", "east", 1422, "Gloria Simmons", avatar=pic("view", "sunrise over a lake with fog on the water"))
    c.c(d + " 08:05:20", "Angie I hate to complain but the brakes yall put on last week are squealing every time I stop")
    c.c("08:05:50", "it wasnt doing that before")
    c.d("08:06:30", "d1", "Good morning, Gloria. I'm sorry about the noise. New brake pads sometimes squeal while they bed in, but it should be checked. We'd like to look at it. Which day works for you?")
    c.s(16, "08:11:10", "Good morning, Gloria, and please don't apologize, I'm glad you told me. That's not how I want you leaving here. New pads can squeal until they seat, but if it were my car I'd want it looked at, not guessed at. Bring the Highlander by today at 1:00 or tomorrow at 7:30 and we'll pull the wheels while you wait. No charge, Gloria: it's under our warranty.\nAngie", edit="d1")
    c.prio(16, "08:11:40", "high")
    c.c("08:14:30", "today at 1 is fine. thank you")
    c.d("08:15:10", "d2", "Thank you, Gloria. Today at 1:00 works. See you then.")
    c.s(16, "08:17:00", "You're all set, Gloria: today at 1:00, here at Bonny Oaks, a brake noise check on the Highlander, no charge. I'll walk out to the car with you myself.\nAngie", edit="d2")
    c.label(16, "08:17:20", "complaint")
    c.c("14:20:15", "all quiet now 🙌 what was it")
    c.d("14:20:55", "d3", "I'm glad it's quiet now, Gloria! I don't have the technician's notes in front of me; I'll find out what it was and let you know.")
    c.s(16, "14:25:30", "So glad, Gloria! The pads were fine. One of the little anti-rattle clips wasn't seated all the way, and that's on us. They reseated both sides and road tested it. Any noise at all, you message me.\nAngie")
    c.res(16, "14:26:00")
    c.reads_extra = {"operator_credit": "slot 16: first answer {first} minutes (her ledger row is 6), three replies, two drafts edited and one discarded, a base priority of High set by her, one resolved"}
    f.truth = {"reason": "complaint, comeback, the bill", "handled": "slot 16; the assistant drafts", "outcome": "checked the same day at no charge; an anti-rattle clip reseated; resolved by slot 16",
               "facts": ["a brake noise a week after a brake job at east", "slot 16 set the priority to High and booked a free check the same day", "the cause was a clip not seated at the first job; she said so"], "questions": []}
    f.why = ["She does not defend the job and does not blame the pads: she books the look.", "'That's on us' is in writing.", "The draft that could not know the answer is the one she wrote over."]
    f.new_facts = ["Gloria Simmons, 2014 Toyota Highlander: front brakes at east in week T-16; a no-charge brake noise check on the Wednesday of week T-15 at 13:00 (an anti-rattle clip reseated): a warranty order pointing at the first one.",
                   "The contact's picture: sunrise over a lake."]
    return f


def f16():
    f = File(CFG, 16, "people", "p16-web-pre-purchase",
             "After hours: a used car to be checked before it is bought",
             "The web chat at 19:42. The assistant gives the public price, takes the name, number and shop, hands over. Slot 16 answers six minutes after opening: the name twice, 'if it were my money', what the inspection is, two times; then the summary with the address and what to bring.")
    f.cast = {"customer": cust("Tasha Reed", "first visit; she is buying a 2015 Honda Pilot from a lot", first_time=True, phone="(423) 555-0407")}
    f.staff(16)
    d = f.day(wk("Mon", 7))
    n = f.day(wk("Mon", 7, plus=1), "the next morning")
    f.day(wk("Wed", 7), "the inspection")
    f.p("$149.95", "pre-purchase inspection with road test and written report, menu price", job="pre_purchase_inspection")
    f.scenario = {"who_writes": "Somebody about to buy a used car, in the evening.", "vehicle": "a 2015 Honda Pilot she does not own yet",
                  "what_happens": "Price from the list after hours, a hand-over, and the next morning two times on the day the seller allows.",
                  "facts": {"booked": "the Wednesday of week T-7, 13:00, at east", "inspection_hours": "1.5 (catalogue): 'about an hour and a half'", "public_pages_used": ["price list: pre-purchase inspection", "hours and locations"]}}
    f.floating = [fl("tomorrow", d, n), fl("wednesday", d, "the Wednesday of week T-7"), fl("Wednesday at 9:00", n, "the Wednesday of week T-7"), fl("Wednesday at 1:00", n, "the Wednesday of week T-7")]
    c = web(f, "c1", "east", 590, 16)
    c.c(d + " 19:42:10", "hey do you check out used cars before someone buys them")
    c.a("19:42:34", GREET + "Yes: a pre-purchase inspection with a road test and a written report is $149.95. The shops are closed now and open at 7:30 tomorrow. Would you like me to ask the shop to set one up?")
    c.c("19:43:20", "yes its at a lot, 2015 honda pilot. guy says i can take it for a couple hours wednesday")
    c.a("19:43:45", "I can't book a time myself, but I'll pass it on. What's your name and the best number for you, and which shop is closer: East Main Street or Bonny Oaks Drive?")
    c.c("19:44:20", "bonny oaks. Tasha Reed 423 555 0407")
    c.a("19:44:44", "Thank you, Tasha. " + SAID)
    c.h("19:44:45", "scheduling", "Tasha Reed", "(423) 555-0407", "bonny oaks",
        "Tasha Reed is buying a 2015 Honda Pilot from a lot and wants a pre-purchase inspection; the seller lets her take the car for a couple of hours on Wednesday. I gave the price, $149.95. Bonny Oaks Drive.",
        "east", "%s 17:30, the next open day's close" % n)
    c.s(16, n + " 07:35:50", "Good morning, Tasha, this is Angie at Bonny Oaks. Good for you for having it checked before you sign anything, Tasha; if it were my money I'd do the same. The inspection is $149.95 and takes about an hour and a half: a road test, up on the lift, and a written report you can take back to the seller. I can do Wednesday at 9:00 or Wednesday at 1:00. Which is easier with the lot?\nAngie")
    c.c("07:52:10", "1 is better")
    c.d("07:52:50", "d1", "Thank you, Tasha. Wednesday at 1:00 works. See you then at 6340 Bonny Oaks Drive.")
    c.s(16, "07:56:00", "You're set, Tasha: Wednesday at 1:00, pre-purchase inspection on the 2015 Pilot, here at 6340 Bonny Oaks Drive. Ask the lot for the keys and any service records they have, and I'll go over the report with you before you leave.\nAngie", edit="d1")
    c.label(16, "07:56:20", "booking")
    c.res(16, "07:56:40")
    c.reads_extra = {"operator_credit": "the chat's first answer is nobody's; slot 16: her first line {first} working minutes after opening, two replies, one draft edited, one resolved"}
    f.truth = {"reason": "what a job costs", "handled": "assistant first, handed over (scheduling), slot 16", "outcome": "pre-purchase inspection booked, Wednesday 13:00, at east; resolved by slot 16",
               "facts": ["asked after closing; the assistant answered in 24 seconds with the public price, 149.95", "slot 16 replied {first} working minutes after the shop opened"], "questions": []}
    f.why = ["A question asked at 19:42 has its price at 19:42 and its time at 7:35.", "Angie's message is longer than anyone else's and none of it is filler.", "The summary carries the address; she is the advisor who never forgets it."]
    f.new_facts = ["Tasha Reed, (423) 555-0407 (tier B): a pre-purchase inspection of a 2015 Honda Pilot at east on the Wednesday of week T-7 at 13:00."]
    return f


def f17():
    f = File(CFG, 17, "people", "p17-telegram-not-today",
             "The second advisor at Bonny Oaks, alone at the counter: the price before the need, and the first 'not today' accepted",
             "Slot 17 in writing, on one of the lead advisor's days off: 'gotcha', the price before what the part does, 'just holler' at the first no. The draft he wrote over asked for the booking. A second question waits an hour, and then he edits the draft into an answer of his own. He does not resolve.")
    f.cast = {"customer": cust("Dwight Hensley", "a customer of the Bonny Oaks shop; 2013 Ford F-150; front sway bar links recommended at yesterday's oil change")}
    f.staff(17)
    d = f.day(wk("Fri", 12), "a Friday on which slot 16 is off (ledger s5.days_off_so_far)")
    f.day(wk("Fri", 12, plus=7), "Chatwoot resolves the chat after 7 silent days")
    f.p("$220.26", "front sway bar links, pair, class truck", job="sway_bar_links", cls="truck")
    f.scenario = {"who_writes": "A customer reading yesterday's inspection sheet.", "vehicle": "2013 Ford F-150",
                  "what_happens": "'What's that clunk thing': the price first, then what it is. 'Not today': accepted. Then: is it safe to pull the boat? An hour later, yes.",
                  "facts": {"recommended": "front sway bar links, pair", "sold": "no", "public_pages_used": []}}
    f.floating = [fl("not today", d, d), fl("saturday", d, "the Saturday of week T-12"), fl("before Saturday", d, "the Saturday of week T-12")]
    c = tg(f, "c1", "east", 1533, "Dwight Hensley", avatar=pic("car", "a blue Ford F-150 hitched to a boat trailer", matches="2013 Ford F-150"))
    c.c(d + " 10:15:05", "Josh whats that clunk thing yall wrote on my paper. is it gonna fall apart")
    c.d("10:15:50", "d1", "Hi Dwight. I don't have your inspection sheet in front of me. I'll look it up and message you right back.")
    c.s(17, "10:27:40", "Hey Dwight! Thats the front sway bar links, $220.26 for the pair. They keep the truck from leaning in the turns. Wont fall apart but its gonna keep clunking")
    c.c("10:30:10", "ok not today")
    c.d("10:30:50", "d2", "No problem, Dwight. They aren't urgent, but the clunk won't go away on its own. Would you like us to do them with your next oil change?")
    c.s(17, "10:38:00", "Gotcha, no worries! Just holler when youre ready")
    c.c("10:41:30", "is it safe to pull my boat with it like that")
    c.d("10:42:15", "d3", "Good question, Dwight. Worn sway bar links mostly affect how the truck leans and how it sounds. I'll confirm whether towing is a concern for yours.")
    c.c("11:02:40", "taking it to the lake saturday is why im asking")
    c.d("11:03:25", "d4", "Understood, Dwight. Worn sway bar links mostly affect how the truck leans and how it sounds. I'll confirm before Saturday whether towing is a concern for yours.")
    c.s(17, "11:39:20", "Yeah youre fine to pull the boat, links mostly affect the lean and the noise. Just take the ramp easy", edit="d4",
        late="a second question can wait an hour: the lead advisor is off and the counter is his alone")
    c.auto()
    c.reads_extra = {"operator_credit": "slot 17: first answer {first} minutes (his ledger row is 11), three replies, two drafts discarded, one replaced before he looked and one edited, nothing resolved"}
    f.truth = {"reason": "found work: approve or decline", "handled": "slot 17; the assistant drafts", "outcome": "the recommended sway bar links are not sold; resolved by 7 silent days",
               "facts": ["the price was named before the reason for the work", "the customer said 'not today' once and slot 17 accepted it", "the discarded draft proposed doing the work with the next oil change",
                         "a later question waited 58 minutes"], "questions": ["S5.1"]}
    f.why = ["Price, then need, then 'just holler': the three habits of his call sheet, typed.", "The draft he threw away is what the lead advisor would have sent.", "This is one of the days story S5 counts: the shop sells less when she is off."]
    f.new_facts = ["Dwight Hensley, 2013 Ford F-150: front sway bar links (220.26) recommended at east at an oil change on the Thursday of week T-12 and declined the next day.", "The contact's picture: a blue F-150 with a boat trailer."]
    return f


def f18():
    f = File(CFG, 18, "people", "p17-web-own-tires",
             "Tires bought online: the assistant passes the question on, and the second advisor answers half of it now and half an hour later",
             "A question the public pages do not settle: the assistant gives the listed price, says what it cannot confirm and hands over as a question, not a booking. Slot 17 answers in 11 minutes ('gotcha', 'we'll get you taken care of'), names the Saturday rule of his own shop, books Friday, and the second question waits 57 minutes for a draft he then sends as it was. He labels it and does not resolve.")
    f.cast = {"customer": cust("Hector Ortega", "first visit; he has four tires he bought online", first_time=True, phone="(423) 555-0452")}
    f.staff(17)
    d = f.day(wk("Thu", 20))
    f.day(wk("Fri", 20), "the booking")
    f.day(wk("Thu", 20, plus=7), "Chatwoot resolves the chat after 7 silent days")
    f.p("$100.00", "dismount, mount and balance four tires, class car, menu price", job="seasonal_tyre_change")
    f.p("$100", "the same, as he writes it", job="seasonal_tyre_change")
    f.num_("$3.50", "tire disposal, each (catalogue.json new_tyres_fitted, the fee's name)")
    f.scenario = {"who_writes": "Somebody with four tires in his trunk.", "what_happens": "Do you mount tires bought elsewhere, how much, Saturday, and what about the old ones. The Bonny Oaks shop is closed on Saturdays; he comes Friday at 2.",
                  "facts": {"booked": "the Friday of week T-20, 14:00, at east", "hours": "east: Monday to Friday; main: also Saturday 8:00 to 1:00 (ledger site.open_days)", "public_pages_used": ["price list: tires", "hours and locations"]}}
    f.floating = [fl("saturday", d, "the Saturday of week T-20"), fl("Saturday", d, "any Saturday"), fl("Saturdays", d, "any Saturday"), fl("Friday at 2", d, "the Friday of week T-20"), fl("friday at 2", d, "the Friday of week T-20"),
                  fl("Friday at 2:00", d, "the Friday of week T-20"), fl("Monday to Friday", d, "every weekday")]
    c = web(f, "c1", "east", 644, 18)
    c.c(d + " 13:02:10", "do yall put on tires if i bought them online")
    c.a("13:02:33", GREET + "Our price list has mounting and balancing four tires at $100.00 for a car. I can't confirm from here how the shop handles tires bought elsewhere, so I'll pass your question to an advisor. What's your name and the best number for you, and which shop: East Main Street or Bonny Oaks Drive?")
    c.c("13:03:15", "Hector Ortega 423 555 0452 bonny oaks")
    c.a("13:03:39", "Thank you, Hector. Your question is with the team now, and somebody will get back to you as soon as possible.")
    c.h("13:03:40", "escalation", "Hector Ortega", "(423) 555-0452", "bonny oaks",
        "Hector Ortega asks whether the shop mounts tires he bought online. I gave the price-list figure for mounting and balancing four, $100.00, and said I could not confirm how tires bought elsewhere are handled. Bonny Oaks Drive.",
        "east", "%s 17:30, the day's close" % d)
    c.s(17, "13:15:10", "Hey Hector, Josh at Bonny Oaks. Gotcha, yeah we mount tires you bring in, $100 for all four mounted and balanced. We'll get you taken care of, when you wanna come by?")
    c.c("13:18:40", "saturday?")
    c.c("13:18:55", "and do yall charge to get rid of the old ones")
    c.d("13:19:35", "d1", "The Bonny Oaks shop is open Monday to Friday, 7:30 to 5:30, so Saturday won't work there; East Main is open Saturday from 8:00 to 1:00. For the old tires there is a disposal fee; I'll confirm the amount.")
    c.s(17, "13:27:05", "Were closed Saturdays out here, East Main does 8 to 1 though. I can do Friday at 2 here")
    c.label(17, "13:27:30", "tires")
    c.c("13:29:30", "friday at 2 works. what about the old tires")
    c.d("13:30:10", "d2", "Friday at 2:00 works. For the old tires, disposal is $3.50 a tire.")
    c.s(17, "14:26:40", "Friday at 2:00 works. For the old tires, disposal is $3.50 a tire.", use="d2", late="a second question can wait an hour")
    c.auto()
    c.reads_extra = {"operator_credit": "the chat's first answer is nobody's; slot 17: his first line {first} minutes after the hand-off, three replies, one draft discarded and one sent as it was, nothing resolved"}
    f.truth = {"reason": "what a job costs", "handled": "assistant first, handed over (escalation), slot 17", "outcome": "mounting booked for Friday 14:00 at east; resolved by 7 silent days",
               "facts": ["the assistant gave the listed price, 100.00, and passed on what it could not confirm", "the question about old tires was asked twice and answered 57 minutes after the second asking: 3.50 a tire"], "questions": []}
    f.why = ["The hand-over is kind escalation: a question, not a booking. Its card is High and due the same day.", "'We'll get you taken care of' comes before any time is offered.",
             "The wait of 57 minutes is the hour his voice note names."]
    f.new_facts = ["Hector Ortega, (423) 555-0452 (tier B): four customer-supplied tires mounted and balanced at east on the Friday of week T-20 at 14:00, 100.00 plus disposal at 3.50 a tire.",
                   "The shop mounts tires a customer brings (said by slot 17; the public pages do not say)."]
    return f


def f19():
    f = File(CFG, 19, "people", "p22-telegram-bring-it-by",
             "The Nashville manager and a man he has known for years",
             "Slot 22 in writing, at his warmest: half an hour to a first reply, five words and a question about the customer's mother. No time, no price, no name taken; 'will do'. Both drafts written over. Nobody resolves it.")
    f.cast = {"customer": cust("Buddy Carver", "a regular of the Charlotte Pike shop since before the purchase; he brings his mother's Buick")}
    f.staff(22)
    d = f.day(wk("Tue", 16))
    f.day(wk("Tue", 16, plus=7), "Chatwoot resolves the chat after 7 silent days")
    f.scenario = {"who_writes": "A regular who writes to Dale by name.", "vehicle": "his mother's Buick (model not said)",
                  "what_happens": "A whine when the wheel is turned, again. 'bring it by. hows your mama doing'. He will be there after lunch. 'will do'.",
                  "facts": {"public_pages_used": [], "note": "nothing is written anywhere: no appointment, no time; the visit is a walk-in"}}
    f.floating = []
    c = tg(f, "c1", "west", 3105, "Buddy Carver")
    c.c(d + " 07:48:10", "Dale its Buddy Carver. mamas buick is making that whine again when she turns the wheel. can i run it by")
    c.d("07:48:55", "d1", "Good morning, Buddy. Yes, bring it by and we'll take a look. A whine when turning the wheel should be checked soon. Would this morning or this afternoon suit you?")
    c.s(22, "08:20:30", "bring it by. hows your mama doing")
    c.c("08:24:10", "shes good, ornery as ever. be there after lunch")
    c.d("08:24:50", "d2", "Glad to hear it, Buddy. See you after lunch.")
    c.s(22, "08:51:15", "will do")
    c.auto()
    c.reads_extra = {"operator_credit": "slot 22: first answer {first} minutes (his ledger row is 35), two replies, two drafts discarded, nothing resolved"}
    f.truth = {"reason": "a symptom", "handled": "slot 22; the assistant drafts", "outcome": "a walk-in after lunch, no time agreed; resolved by 7 silent days",
               "facts": ["slot 22 offered no time and no price and took no note of the car", "both drafts were discarded"], "questions": []}
    f.why = ["This is what the regulars like about him, and it is real.", "Set it beside file 20: the same man, a stranger, the next day, eight words.", "The draft asked 'this morning or this afternoon'; he did not."]
    f.new_facts = ["Buddy Carver, a regular of west, brings his mother's Buick (a whine when turning, a repeat) as a walk-in on the Tuesday of week T-16.", "The contact has no picture."]
    return f


def f20():
    f = File(CFG, 20, "people", "p22-web-shop-supplies",
             "A line on the bill nobody explained: the manager answers the next day, and the other advisor finishes the answer",
             "A question about a bill on the web chat: the assistant explains the charge in general, cannot see the bill, hands over. The chat turns Urgent and stays so overnight. Slot 22 answers the next morning in eight words. The customer's reply gets a draft he does not touch; slot 24 edits it and sends it nine minutes later, with the figure, and resolves.")
    f.cast = {"customer": cust("Sharon Whitfield", "a customer of the Charlotte Pike shop; a water pump replaced the day before", phone="(615) 555-0236")}
    f.staff(22, 24)
    d = f.day(wk("Wed", 9))
    n = f.day(wk("Wed", 9, plus=1), "the next day")
    f.psup("$17.55", "shop supplies on a water pump job: 5 % of its hourly labour, 351.00", "water_pump")
    f.num_("5 percent", "the shop-supplies rate (ledger price.supplies.rate)")
    f.num_("5%", "the same")
    f.num_("$35.00", "the cap per order (ledger price.supplies.cap)")
    f.scenario = {"who_writes": "A customer reading yesterday's bill.", "what_happens": "'Shop supplies $17.55. Nobody mentioned it. What is that?' The answer comes the next morning: 'its on every ticket. 5 percent of labor'. She says she would have liked to be told. Jasmine tells her, properly.",
                  "facts": {"rule": "5 % of hourly-priced labour on the order, at most 35.00 (catalogue.json shop_supplies)", "public_pages_used": ["price list: shop supplies"]}}
    f.floating = [fl("yesterday", d, "the Tuesday of week T-9")]
    c = web(f, "c1", "west", 702, 20)
    c.c(d + " 11:20:10", "I picked up my car from your Nashville shop yesterday and there's a 'shop supplies' charge of $17.55 on the bill. Nobody mentioned it. What is that?")
    c.a("11:20:35", "Hello. I'm the assistant for Brennan Auto Care. I can't see your bill from here. In general, shop supplies is a small charge on repairs billed by the hour; it covers things like cleaners, rags and hardware. For your own bill I'll pass the question to the Charlotte Pike shop. What's your name and the best number to reach you?")
    c.c("11:21:20", "Sharon Whitfield, 615-555-0236")
    c.a("11:21:44", "Thank you, Ms. Whitfield. Your question is with the team now, and somebody will get back to you as soon as possible.")
    c.h("11:21:45", "escalation", "Sharon Whitfield", "(615) 555-0236", "Nashville",
        "Sharon Whitfield picked up her car at the Charlotte Pike shop yesterday. Her bill has a 'shop supplies' charge of $17.55 that nobody mentioned, and she asks what it is. I can't see the bill; I explained the charge in general terms only.",
        "west", "%s 17:30, the day's close" % d)
    c.s(22, n + " 08:10:20", "its on every ticket. 5 percent of labor", late="he answers the next day (ledger conv.slowest_tenth)")
    c.c("08:31:00", "It would have been nice to be told. Thank you.")
    c.d("08:31:40", "d1", "You're right, Ms. Whitfield, and I'm sorry it wasn't explained at pick-up. Shop supplies is 5% of the hourly labor on a repair, never more than $35.00, and it is listed on every estimate.")
    c.s(24, "08:40:10", "Ms. Whitfield, this is Jasmine at Charlotte Pike. You're right, and I'm sorry it wasn't explained at pick-up. Shop supplies is 5% of the hourly labor on a repair, never more than $35.00. On yours it was $17.55, on the water pump labor. It should be shown to you on the estimate before any work starts. If anything else on the bill isn't clear, message me here.", edit="d1")
    c.label(24, "08:40:30", "complaint")
    c.res(24, "08:40:50")
    c.reads_extra = {"operator_credit": "the chat's first answer is nobody's; slot 22: his first line {first} working minutes after the hand-off, the next morning; slot 24: one reply in his chat, one draft edited, one resolved"}
    f.truth = {"reason": "complaint, comeback, the bill", "handled": "assistant first, handed over (escalation), slot 22, then slot 24", "outcome": "explained the next day; resolved by slot 24",
               "facts": ["shop supplies is 5 % of hourly labour, at most 35.00 an order; on her bill 17.55", "the hand-over waited from 11:21 to the next morning", "slot 22 owns the chat; slot 24 wrote the reply that explained it"], "questions": []}
    f.why = ["Eight words, no name, no apology, and factually right.", "The draft was ready 40 seconds after her line; the owner of the chat left it; the other advisor used it.", "The owner of a chat and the person who helped the customer are not always the same row in Stats."]
    f.new_facts = ["Sharon Whitfield, (615) 555-0236 (tier B): a water pump replaced at west, picked up on the Tuesday of week T-9; the bill carries shop supplies of 17.55."]
    return f


def f21():
    f = File(CFG, 21, "people", "p23-telegram-anytime",
             "The weak desk on a booking: 'come by monday', 'anytime'",
             "Slot 23 in writing on an ordinary day: 44 minutes to a first reply, four words, a day and no time. Asked what time, he answers at five to five: 'anytime'. Both drafts written over; nothing labelled, nothing resolved.")
    f.cast = {"customer": cust("Terrence Boyd", "2010 Honda Accord; he has been to the Charlotte Pike shop before")}
    f.staff(23)
    d = f.day(wk("Mon", 13))
    f.day(wk("Mon", 13, plus=7), "Chatwoot resolves the chat after 7 silent days")
    f.scenario = {"who_writes": "A customer who wants an oil change on a Saturday.", "vehicle": "2010 Honda Accord",
                  "what_happens": "The shop is closed on Saturdays. 'come by monday.' 'what time' waits seven hours for 'anytime'. Whether he came is the ERP's to say.",
                  "facts": {"hours": "west: Monday to Friday, 7:30 to 5:30 (ledger site.open_days)", "public_pages_used": []}}
    f.floating = [fl("saturday", d, "the Saturday of week T-13"), fl("saturdays", d, "any Saturday"), fl("monday", d, "the Monday of week T-12"), fl("Monday", d, "the Monday of week T-12"), fl("Monday to Friday", d, "every weekday")]
    c = tg(f, "c1", "west", 3218, "T Boyd", avatar=pic("pet", "a brown pit bull lying on a porch"))
    c.c(d + " 09:05:15", "yall got time for an oil change saturday")
    c.d("09:06:00", "d1", "Hi! The Charlotte Pike shop is open Monday to Friday, 7:30 to 5:30, so Saturday isn't available. We could do an oil change any weekday. Which day works for you?")
    c.s(23, "09:49:40", "closed saturdays. come by monday")
    c.c("09:55:10", "what time")
    c.d("09:55:50", "d2", "Would Monday morning or afternoon suit you better? I'll confirm a time.")
    c.c("13:12:05", "?")
    c.d("13:12:50", "d3", "Sorry for the wait. Would Monday morning or afternoon suit you better? I'll confirm a time.")
    c.s(23, "16:58:30", "anytime", late="his replies come at the end of the day (cast.json; ledger conv.slowest_tenth)")
    c.auto()
    c.reads_extra = {"operator_credit": "slot 23: first answer {first} minutes (his ledger row is 40), two replies, two drafts discarded and one replaced before he looked, nothing resolved"}
    f.truth = {"reason": "to book or ask for a slot", "handled": "slot 23; the assistant drafts", "outcome": "no time agreed; resolved by 7 silent days",
               "facts": ["no time was offered; asked for one, and asked again with a question mark, slot 23 answered 'anytime' seven hours later", "no draft was used"], "questions": []}
    f.why = ["Nothing here is rude or wrong, and nothing is booked.", "Each draft ended with a question that would have fixed a time.", "Set it beside file 24: the same desk, the same kind of request, the other advisor."]
    f.new_facts = ["Terrence Boyd (Telegram name 'T Boyd'), 2010 Honda Accord, asked west for a Saturday oil change on the Monday of week T-13; no appointment was made.", "The contact's picture: a brown pit bull on a porch."]
    return f


def f22():
    f = File(CFG, 22, "people", "p23-web-found-on-the-invoice",
             "Work recommended on the invoice and never said aloud: the customer asks the website",
             "Slot 23 writes up what he is asked for and mentions the rest at pick-up, or not at all. A customer finds 'rear brake pads 3mm, recommend replace' on her invoice at home. The assistant says what 3 mm means in general and hands over. His reply comes at 17:02: 'yeah theyre low. bring it back whenever'. Asked the price, he gives it the next morning, with no time and no step.")
    f.cast = {"customer": cust("Monica Reyes", "a customer of the Charlotte Pike shop; 2016 Hyundai Tucson, picked up the day before", phone="(615) 555-0289")}
    f.staff(23)
    d = f.day(wk("Thu", 5))
    n = f.day(wk("Thu", 5, plus=1), "the next day")
    f.day(wk("Thu", 5, plus=8), "Chatwoot resolves the chat after 7 silent days")
    f.p("$225.77", "rear brake pads, class car, standard parts", job="rear_brake_pads")
    f.p("225.77", "the same, as he writes it", job="rear_brake_pads")
    f.num_("3mm", "the measurement on her invoice")
    f.num_("3 mm", "the same")
    f.scenario = {"who_writes": "A customer who read her invoice at home.", "vehicle": "2016 Hyundai Tucson",
                  "what_happens": "Is it safe? The assistant: 3 mm is close to the end; here is a person. The person, at closing time: bring it back whenever. How much and how long? The next morning: the price and 'about an hour'.",
                  "facts": {"recommended": "rear brake pads; written on the invoice, not said at pick-up", "sold": "no", "public_pages_used": ["brake questions: pad thickness"]}}
    f.floating = [fl("yesterday", d, "the Wednesday of week T-5")]
    c = web(f, "c1", "west", 760, 22)
    c.c(d + " 12:10:20", "Picked up my Tucson at Charlotte Pike yesterday and the invoice says 'rear brake pads 3mm, recommend replace'. Nobody said anything when I paid. Is it safe to drive?")
    c.a("12:10:45", "Hello. I'm the assistant for Brennan Auto Care. I can't see your invoice or diagnose a car over chat, but brake pads at 3 mm are close to the end of their life, so it's worth replacing them soon rather than waiting for a noise. I'll pass your question to the Charlotte Pike shop so an advisor can go over it with you. What's your name and the best number to reach you?")
    c.c("12:11:30", "Monica Reyes 615 555 0289")
    c.a("12:11:54", "Thank you, Monica. Your question is with the team now, and somebody will get back to you as soon as possible.")
    c.h("12:11:55", "escalation", "Monica Reyes", "(615) 555-0289", "Charlotte Pike",
        "Monica Reyes picked up her Hyundai Tucson at the Charlotte Pike shop yesterday. The invoice says 'rear brake pads 3mm, recommend replace'; nobody told her at pick-up, and she asks if it is safe to drive. I said pads at 3 mm are near the end and should be replaced soon; I can't see the invoice.",
        "west", "%s 17:30, the day's close" % d)
    c.s(23, "17:02:10", "yeah theyre low. bring it back whenever", late="his replies come at the end of the day (cast.json; ledger conv.slowest_tenth)")
    c.c("17:20:05", "How much, and how long does it take?")
    c.d("17:20:45", "d1", "Replacing the rear brake pads on a car like yours is $225.77 before shop supplies and tax and takes about an hour. Would you like to book a time?")
    c.s(23, n + " 08:20:30", "225.77 plus tax. about an hour")
    c.auto()
    c.reads_extra = {"operator_credit": "the chat's first answer is nobody's; slot 23: his first line {first} working minutes after the hand-off, two replies, one draft discarded, nothing resolved"}
    f.truth = {"reason": "found work: approve or decline", "handled": "assistant first, handed over (escalation), slot 23", "outcome": "the recommended rear pads are not sold; resolved by 7 silent days",
               "facts": ["the recommendation was on the invoice and was not said at pick-up", "slot 23 answered at 17:02 with no price and no time", "the price, 225.77, came the next morning; no time was offered"], "questions": []}
    f.why = ["'bring it back whenever' is a recommendation mentioned when it is too late, in writing.", "The draft ended with 'Would you like to book a time?'; his line ends with 'about an hour'.", "This is how a shop sells four recommendations in ten."]
    f.new_facts = ["Monica Reyes, (615) 555-0289 (tier B), 2016 Hyundai Tucson, at west on the Wednesday of week T-5: rear brake pads at 3 mm recommended on the invoice (225.77), not sold."]
    return f


def f23():
    f = File(CFG, 23, "people", "p24-telegram-estimate-attached",
             "The bright spot at Charlotte Pike: findings by number, the estimate attached, a total to the cent",
             "Slot 24 in writing: six minutes to a first reply, the findings as a numbered list with the estimate as a file, 'what I can do is' and a deadline for the answer, then the approved work and the total with shop supplies and tax. Two drafts edited, one sent as it was; labelled and resolved.")
    f.cast = {"customer": cust("Latoya Greene", "a customer of the Charlotte Pike shop; 2014 Chevrolet Equinox, in for a check engine light")}
    f.staff(24)
    d = f.day(wk("Fri", 10))
    f.p("$153.86", "ignition coil, one cylinder, class car", job="ignition_coil")
    f.p("$222.28", "spark plugs, four, class car", job="spark_plugs")
    f.p("$135.00", "check engine light diagnosis, one hour", job="check_engine_diag")
    f.psum("$576.86", "coil, plugs and diagnosis with shop supplies and sales tax", [("ignition_coil", "car"), ("spark_plugs", "car"), ("check_engine_diag", "car")])
    f.num_("96,000 miles", "the car's mileage; invented")
    f.scenario = {"who_writes": "A customer whose car is in for a diagnosis, from work.", "vehicle": "2014 Chevrolet Equinox",
                  "what_happens": "Any update? The diagnosis is done: a failed coil on cylinder 2 and worn original plugs. Both by 4:30 if she says yes by 2:00. She says both and asks the total.",
                  "facts": {"approved": "ignition coil and spark plugs", "public_pages_used": []}}
    f.floating = [fl("this morning", d, d), fl("today", d, d)]
    c = tg(f, "c1", "west", 3340, "Latoya Greene", avatar=pic("car", "a gray Chevrolet Equinox on the top deck of a parking garage", matches="2014 Chevrolet Equinox"))
    c.c(d + " 13:02:10", "Hi Jasmine, any update on my Equinox?")
    c.d("13:02:55", "d1", "Hi Latoya! I don't have the status of the Equinox in front of me. I'll check with the technician and message you right back.")
    c.s(24, "13:08:30", "Hi Latoya! Yes, the diagnosis is done. Estimate attached.\n1. The ignition coil on cylinder 2 has failed: that's the misfire and the light. $153.86.\n2. The spark plugs are the originals at 96,000 miles and worn: $222.28 for all four.\n3. The diagnosis you approved this morning: $135.00.\nWhat I can do is have both done today by 4:30 if I hear from you by 2:00. Would you like both, or the coil only?",
        files=[{"kind": "file", "file": "Estimate_Equinox_Greene.pdf", "pool": "estimate-pdf", "shows": "a one-page estimate: diagnosis, ignition coil, spark plugs, shop supplies, tax"}], edit="d1")
    c.c("13:15:40", "both. total?")
    c.d("13:16:20", "d2", "Thank you, Latoya. Both it is. I'll confirm the total with shop supplies and tax.")
    c.s(24, "13:19:10", "Thank you, Latoya. Both approved: coil and plugs. The total with the diagnosis, shop supplies and tax is $576.86. Ready by 4:30, and I'll message you here.", edit="d2")
    c.label(24, "13:19:30", "approval")
    c.s(24, "16:22:40", "The Equinox is ready, Latoya. The light is off and it idles smooth. We're here until 5:30.")
    c.c("16:35:10", "on my way")
    c.d("16:35:50", "d3", "See you soon, Latoya.")
    c.s(24, "16:37:00", "See you soon, Latoya.", use="d3")
    c.res(24, "16:37:20")
    c.reads_extra = {"operator_credit": "slot 24: first answer {first} minutes (her ledger row is 7), four replies, two drafts edited and one sent as it was, one resolved"}
    f.truth = {"reason": "found work: approve or decline", "handled": "slot 24; the assistant drafts", "outcome": "coil and plugs approved; 576.86 with shop supplies and tax; resolved by slot 24",
               "facts": ["the findings came as a numbered list with the estimate attached", "both jobs approved in seven minutes", "ready before the time she gave"], "questions": []}
    f.why = ["A list, a file, a deadline and a choice: the customer answers in two words.", "'What I can do is' where another desk would say it can't be done today.", "Same shop as files 21 and 22."]
    f.new_facts = ["Latoya Greene, 2014 Chevrolet Equinox, 96,000 miles, at west on the Friday of week T-10: check engine diagnosis 135.00, ignition coil 153.86, spark plugs 222.28; 576.86 with shop supplies (16.88) and tax.",
                   "The file Estimate_Equinox_Greene.pdf (picture pool 'estimate-pdf').", "The contact's picture: a gray Chevrolet Equinox in a parking garage."]
    return f


def f24():
    f = File(CFG, 24, "people", "p24-web-same-day",
             "A dead battery at 7:41: the assistant passes it on, and the advisor finds two times in a full morning",
             "A same-day request on the web chat. The assistant says what is free and what it cannot do, and hands over. Slot 24 answers in under seven minutes: she repeats name, number and car, says the morning is full and what she can do, prices the battery if it is needed. The closing draft goes out as it was; labelled and resolved.")
    f.cast = {"customer": cust("Deion Marshall", "2017 Kia Soul; first visit", first_time=True, phone="(615) 555-0347")}
    f.staff(24)
    d = f.day(wk("Tue", 17))
    f.p("$239.95", "battery replaced, class car, menu labour and a standard battery", job="battery_replace")
    f.num_("free", "battery, starting and charging system test: 0.00 in the catalogue")
    f.scenario = {"who_writes": "Somebody whose car needed a jump this morning.", "vehicle": "2017 Kia Soul",
                  "what_happens": "Can you get me in today? The test is free; the morning is full; 11:30 or 2:15. He takes 11:30.",
                  "facts": {"booked": "%s 11:30 at west" % d, "public_pages_used": ["price list: battery test"]}}
    f.floating = [fl("this morning", d, d), fl("today", d, d), fl("11:30 today", d, d)]
    c = web(f, "c1", "west", 811, 24)
    c.c(d + " 07:41:10", "my battery died this morning had to get a jump. can you guys get me in today?? charlotte pike")
    c.a("07:41:33", "Good morning! I'm the assistant for Brennan Auto Care. I can't book a time myself, but I'll pass this to the Charlotte Pike shop right away. A battery, starting and charging system test is free, and if the car needs a battery the advisor will price one for it. What's your name, the best number for you, and what are you driving?")
    c.c("07:42:15", "Deion Marshall 615 555 0347. 2017 kia soul")
    c.a("07:42:39", "Thank you, Deion. " + SAID)
    c.h("07:42:40", "scheduling", "Deion Marshall", "(615) 555-0347", "charlotte pike",
        "Deion Marshall, 2017 Kia Soul. The battery died this morning and the car needed a jump; he asks to be seen today at Charlotte Pike. I told him the battery and charging test is free and named no battery price.",
        "west", "%s 17:30, the day's close" % d)
    c.s(24, "07:49:20", "Good morning, Deion, this is Jasmine at Charlotte Pike. To confirm: Deion Marshall, (615) 555-0347, 2017 Kia Soul. The morning is full, so what I can do is 11:30 or 2:15 today. The battery and charging test is free and takes about ten minutes; if it does need a battery, it's $239.95 installed. Which time works?")
    c.c("07:51:05", "11:30")
    c.d("07:51:45", "d1", "Thank you, Deion. 11:30 today works. See you at 6399 Charlotte Pike.")
    c.s(24, "07:53:10", "Thank you, Deion. 11:30 today works. See you at 6399 Charlotte Pike.", use="d1")
    c.label(24, "07:53:30", "booking")
    c.res(24, "07:53:50")
    c.reads_extra = {"operator_credit": "the chat's first answer is nobody's; slot 24: her first line {first} minutes after the hand-off, two replies, one draft sent as it was, one resolved"}
    f.truth = {"reason": "to book or ask for a slot", "handled": "assistant first, handed over (scheduling), slot 24", "outcome": "battery test booked the same day, 11:30, at west; resolved by slot 24",
               "facts": ["written 11 minutes after opening; answered by the assistant in 23 seconds and by slot 24 in 6.7 minutes", "the test is free; a battery, if needed, 239.95"], "questions": []}
    f.why = ["She reads back the three things a booking needs before she offers anything.", "'The morning is full, so what I can do is': a no that the customer hears as a yes.", "The draft has the address; she had nothing to add."]
    f.new_facts = ["Deion Marshall, (615) 555-0347 (tier B), 2017 Kia Soul: a battery and charging test at west on the Tuesday of week T-17 at 11:30."]
    return f


def f25():
    f = File(CFG, 25, "R13", "web-one-question",
             "Unclear, then clear after one question: 'the thing where you hook it up to the computer'",
             "Rule R13 on the web chat. The customer names a tool, not a need. The assistant asks one plain question (what is the car doing?) and the answer settles it: a check engine light. It prices the diagnosis, hands over, and its note says what was asked. The advisor's own question (steady or flashing) is need discovery, not a second loop.")
    f.cast = {"customer": cust("Kenny Dillard", "2013 Dodge Charger; first visit", first_time=True, phone="(615) 555-0412")}
    f.staff(24)
    d = f.day(wk("Wed", 13), "the Wednesday of week T-13 (DESIGN.md section 6, row 25)")
    f.day(wk("Thu", 13), "'tomorrow, Thursday'")
    f.p("$135.00", "check engine light: scan, test and diagnose, one hour", job="check_engine_diag")
    f.num_("730", "7:30, as the customer types it")
    f.scenario = {"who_writes": "Somebody who knows there is a machine and not what it is called.", "vehicle": "2013 Dodge Charger",
                  "what_happens": "One clarifying question; then price, hand-over, and the advisor's two times.",
                  "facts": {"booked": "the Thursday of week T-13, 07:30, at west", "public_pages_used": ["price list: check engine light diagnosis"]},
                  "unclear": {"kind": "vague: names a tool ('hook it up to the computer') instead of what is wrong", "loops": 1, "resolved": True,
                              "how": "The assistant asks whether a warning light is on or the car is doing something it should not; he says the check engine light came on yesterday."}}
    f.floating = [fl("yesterday", d, "the Tuesday of week T-13"), fl("tomorrow", d, "the Thursday of week T-13"), fl("tomorrow at 7:30", d, "the Thursday of week T-13"), fl("tomorrow, Thursday", d, "the Thursday of week T-13")]
    c = web(f, "c1", "west", 835, 25)
    c.c(d + " 16:05:10", "do yall do the thing where you hook it up to the computer")
    c.a("16:05:34", GREET + "We do have diagnostic equipment. So I point you to the right service: is a warning light on, or is the car doing something it shouldn't?")
    c.c("16:06:20", "check engine light came on yesterday. 2013 charger")
    c.a("16:06:45", "Thanks, that's clear. For a check engine light the service is a scan, test and diagnosis: $135.00 for up to an hour, and the technician tells you what they found before any repair is priced. Would you like me to ask the shop to get you in?")
    c.c("16:07:15", "yes the nashville one. tomorrow")
    c.a("16:07:39", "I can't book a time myself, but I'll pass it to the Charlotte Pike shop. What's your name and the best number for you?")
    c.c("16:08:05", "Kenny Dillard 6155550412")
    c.a("16:08:28", "Thank you, Kenny. " + SAID)
    c.h("16:08:29", "scheduling", "Kenny Dillard", "(615) 555-0412", "the nashville one",
        "Kenny Dillard, 2013 Dodge Charger. He first asked whether we 'hook it up to the computer'; I asked once what the car was doing: the check engine light came on yesterday. I named the diagnosis, $135.00. He wants to come tomorrow, the Nashville shop.",
        "west", "%s 17:30, the day's close" % d)
    c.s(24, "16:14:50", "Hi Kenny, this is Jasmine at Charlotte Pike. To confirm: 2013 Dodge Charger, check engine light on since yesterday. I can take it tomorrow at 7:30 or at 1:00. The diagnosis is $135.00 and takes about an hour. Is the light steady or flashing? If it's flashing, please don't drive it far.")
    c.c("16:17:30", "steady. 730")
    c.d("16:18:10", "d1", "Thank you, Kenny. Tomorrow at 7:30 works. See you at 6399 Charlotte Pike.")
    c.s(24, "16:19:40", "You're booked, Kenny: tomorrow, Thursday, at 7:30, check engine diagnosis on the Charger, 6399 Charlotte Pike. A steady light is fine to drive in on.", edit="d1")
    c.label(24, "16:20:00", "booking")
    c.res(24, "16:20:20")
    c.reads_extra = {"operator_credit": "the chat's first answer is nobody's; slot 24: her first line {first} minutes after the hand-off, two replies, one draft edited, one resolved"}
    f.truth = {"reason": "a symptom", "handled": "assistant first, handed over (scheduling), slot 24", "outcome": "check engine diagnosis booked for the next day, 07:30, at west; resolved by slot 24",
               "facts": ["unclear first message; clear after one question by the assistant", "the hand-off note carries his own words and says what was asked", "the price named is the diagnosis, 135.00"], "questions": []}
    f.why = ["The assistant does not guess a job from 'the computer': it asks what the car is doing.", "The note lets the advisor skip the question the assistant already asked.", "Jasmine's 'steady or flashing' is the question a judge would count for need discovery."]
    f.new_facts = ["Kenny Dillard, (615) 555-0412 (tier B), 2013 Dodge Charger: a check engine diagnosis at west on the Thursday of week T-13 at 07:30."]
    return f


def f26():
    f = File(CFG, 26, "R13", "telegram-two-questions",
             "Unclear, then clear after two questions: 'the car is doing that thing again'",
             "Rule R13 on a drafts channel. The clarifying question is the draft; the advisor sends it in her own words. The first answer ('the one from last time') does not settle it, because last time there were two things. She asks again by naming both, and the answer shows it is neither: the shake is now under braking. One draft edited after another; booked, labelled, resolved.")
    f.cast = {"customer": cust("Dot Kirby", "an older regular of the Bonny Oaks shop; 2012 Toyota Camry; tires balanced in March, a battery light in June")}
    f.staff(16)
    d = f.day(wk("Wed", 6), "the Wednesday of week T-6 (DESIGN.md section 6, row 26)")
    f.day(wk("Thu", 6), "'tomorrow, Thursday'")
    f.day(wk("Fri", 6), "'Friday at 7:30'")
    f.p("$49.95", "brake inspection, menu price", job="brake_inspection")
    f.scenario = {"who_writes": "A regular who expects Angie to know.", "vehicle": "2012 Toyota Camry",
                  "what_happens": "Two questions before the request is clear, then a brake inspection the next morning.",
                  "facts": {"history": "a shake at highway speed in March, cured by balancing the tires; a battery light in the mornings in June", "booked": "the Thursday of week T-6, 09:00, at east", "public_pages_used": []},
                  "unclear": {"kind": "the wrong thing named: 'that thing again' points at last time's tire balance, and it is the brakes", "loops": 2, "resolved": True,
                              "how": "Angie asks which thing; the answer is 'the one from last time'. She names the two things of last time and asks which is back: the shaking, but now when braking downhill. That is a different job, and she says so."}}
    f.floating = [fl("tomorrow at 9:00", d, "the Thursday of week T-6"), fl("tomorrow at 9", d, "the Thursday of week T-6"), fl("tomorrow, Thursday", d, "the Thursday of week T-6"), fl("Friday at 7:30", d, "the Friday of week T-6"),
                  fl("today", d, d), fl("in March", d, "March"), fl("in June", d, "June")]
    c = tg(f, "c1", "east", 1650, "Dot Kirby")
    c.c(d + " 10:02:15", "Angie its Dot. the car is doing that thing again")
    c.d("10:03:00", "d1", "Good morning, Dot! I'm sorry to hear that. Could you tell me a little more about what the car is doing?")
    c.s(16, "10:08:10", "Good morning, Dot! I'm sorry, that's no fun. Help me out, Dot: which thing is it doing again?\nAngie", edit="d1")
    c.c("10:11:40", "the one from last time")
    c.d("10:12:20", "d2", "Thank you, Dot. I don't have your last visit in front of me. Is it a noise, a warning light, or something you feel when you drive?")
    c.s(16, "10:15:30", "We had two things, Dot, so let me chase the right one: the shake in the steering wheel on the highway, that we balanced the tires for in March, or the battery light that came on in the mornings in June. Which one is back?\nAngie", edit="d2")
    c.c("10:19:05", "the shaking")
    c.c("10:19:30", "but now its when I put the brakes on coming down the mountain")
    c.d("10:20:10", "d3", "Thank you, Dot, that helps. A shake that comes when you brake, especially downhill, should be checked. A brake inspection is $49.95. Would you like to bring it in?")
    c.s(16, "10:24:00", "That tells me a lot, Dot. A shake when you brake coming downhill isn't the tires this time; it's most likely the front brake rotors, and if it were my car I wouldn't keep riding the mountain on them. A brake inspection is $49.95, and we'll show you what we find before anything is done. I can see you tomorrow at 9:00 or Friday at 7:30. Which is easier?\nAngie", edit="d3")
    c.c("10:27:15", "tomorrow at 9")
    c.d("10:27:55", "d4", "Thank you, Dot. Tomorrow at 9:00 works. See you then!")
    c.s(16, "10:29:40", "You're set, Dot: tomorrow, Thursday, at 9:00, brake inspection on the Camry, here at Bonny Oaks. Take it easy coming down today.\nAngie", edit="d4")
    c.label(16, "10:30:00", "booking")
    c.res(16, "10:30:20")
    c.reads_extra = {"operator_credit": "slot 16: first answer {first} minutes (her ledger row is 6), four replies, four drafts edited, one resolved"}
    f.truth = {"reason": "a symptom", "handled": "slot 16; the assistant drafts", "outcome": "brake inspection booked for the next day, 09:00, at east; resolved by slot 16",
               "facts": ["unclear first message; clear after two questions by slot 16", "what she named (the thing from last time) was not what the car needed: the shake is under braking", "the price named is the inspection, 49.95"], "questions": []}
    f.why = ["The assistant's second draft offers three readings without knowing the history; Angie offers the two that are true.", "A weaker desk would have booked a tire balance.",
             "She still does not name a repair price: 'most likely the rotors', then the inspection."]
    f.new_facts = ["Dot Kirby, 2012 Toyota Camry, a regular of east: tires balanced in March for a highway shake, a battery light in June; a brake inspection on the Thursday of week T-6 at 09:00.", "The contact has no picture."]
    return f


def f27():
    f = File(CFG, 27, "R13", "web-never-clear",
             "Unclear and never cleared: 'how much for the 60'",
             "Rule R13, the session that ends unclear. The assistant asks one plain question, then offers two readings from the price list, then offers a way out (a name and a number, or come back when he knows). It never guesses. The customer stops answering; with no number there is no hand-off, the chat stays the assistant's, and Chatwoot resolves it after seven silent days with no person on the event.")
    f.cast = {"customer": {"name": "Website visitor", "invented": True, "first_time": True}}
    f.cast["staff"] = []
    d = f.day(wk("Wed", 2), "the Wednesday of week T-2 (DESIGN.md section 6, row 27)")
    f.day(wk("Wed", 2, plus=7), "Chatwoot resolves the chat after 7 silent days")
    f.p("$60.00", "balance four wheels, menu price", job="wheel_balance")
    f.p("$243.00", "scheduled maintenance service (30K / 60K / 90K)", job="scheduled_maintenance")
    f.num_("60", "what the customer asks for; it could be the 60.00 wheel balance or the 60,000-mile service")
    f.num_("60,000-mile", "the 60K scheduled maintenance of the catalogue")
    f.scenario = {"who_writes": "Somebody passing on what a friend told him.", "what_happens": "Three customer lines, three answers, no result.",
                  "facts": {"public_pages_used": ["price list: tires and alignment", "price list: maintenance"]},
                  "unclear": {"kind": "two readings of one word: 'the 60' is a price or a mileage", "loops": 2, "resolved": False,
                              "how": "The assistant asks what he means; he repeats himself. It offers the two things on the price list that fit; he does not know. It asks for the friend's word or a number to pass on, and he does not answer."}}
    f.floating = []
    c = web(f, "c1", "main", 902, 27)
    c.c(d + " 12:40:05", "how much for the 60")
    c.a("12:40:29", GREET + "Happy to help. What do you mean by \"the 60\", and what kind of car is it?")
    c.c("12:41:10", "the 60 thing. my buddy said yall do it")
    c.a("12:41:35", "Thanks. So I give you the right price, which of these is it: balancing four wheels, which is $60.00, or the 60,000-mile scheduled maintenance service, which is $243.00? If it's something else, tell me what the car needs or what it's doing.")
    c.c("12:42:30", "idk he just said the 60")
    c.a("12:42:54", "No problem. If you can find out from him which service it was, or tell me what the car is doing, I can give you a price. Or leave your name and a number and I'll ask an advisor to call you.")
    c.auto()
    c.state_extra = {"resolved_how": "by Chatwoot after 7 silent days; no person, no hand-off, no card"}
    c.reads_extra = {"operator_credit": "nobody: the assistant is not an operator"}
    f.truth = {"reason": "what a job costs", "handled": "the assistant alone", "outcome": "ended unclear; resolved by 7 silent days",
               "facts": ["the request was never made clear", "the assistant asked, offered two readings from the price list (60.00 and 243.00) and did not guess", "no name or number was left, so no hand-over was made"], "questions": []}
    f.why = ["Both readings are real rows of the price list: a wheel balance is 60.00 and there is a 60,000-mile service.", "The assistant stays on the question and names no job as his.", "This is one of the three sessions in a hundred that end unclear."]
    f.new_facts = []
    return f


FILES = [f09, f10, f11, f12, f13, f14, f15, f16, f17, f18, f19, f20, f21, f22, f23, f24, f25, f26, f27]
