import json, os
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/"
c = json.load(open(D + "cast.json", encoding="utf-8"))
ONE = {
 "1": "founder; rarely on site, reads the morning brief on his phone",
 "2": "his daughter; runs the money and the growth, bought the third shop, set the product up",
 "3": "payments, fleet bills, payroll hours; caught the missing money checking the tills against payments",
 "4": "**the senior operator**: plans both home shops, hands out tasks, decides notes and discounts",
 "5": "the steady lead: honest seller, slow in chat, took the timing-belt complaint",
 "6": "**the junior operator**: good and getting better, call score 58 to 72; objections are her weak spot",
 "7": "the newcomer: eager, punctual, promises before he checks; two wrong prices",
 "8": "foreman: hands out the work, takes the 'look at this car again' tasks",
 "9": "parts for both home shops; wants the bought shop on the home supplier",
 "10": "the all-star diagnostician nobody can replace; his two weeks of leave cost the flagship 18 % of its billed hours",
 "11": "high revenue, hard to work with: fast, late, comebacks, declines meetings",
 "12": "the steady mechanic who teaches the apprentice and covers swaps",
 "13": "electrician: methodical, slow, few comebacks",
 "14": "the apprentice: 65 % of the norm, forgets to clock out one day in six",
 "15": "always late, three shifts in ten; well liked, never misses a day",
 "16": "the all-star advisor the east shop depends on; her week off is not covered",
 "17": "works in her shadow; on her days off his numbers are the shop's",
 "18": "lead technician; why east has the fewest comebacks",
 "19": "solid, cheerful, slow on Mondays",
 "20": "did not show up two days ago; a second job in the evenings",
 "21": "floats between the two home shops; took the no-show's shift",
 "22": "came with the purchase; defensive, late rosters, half the owners' tasks overdue",
 "23": "the weakest desk: call score 39, the most missed calls, two unapproved discounts",
 "24": "the bright spot: hired after the purchase, call score 66 to 74 in six months",
 "25": "old-timer; trusts the manager, teaches the part-timer",
 "26": "does the day's work and no more; clocked in twice from 600 m away",
 "27": "the shop's brake man and the source of the brake comebacks",
 "28": "part-time student; learns from the old-timer",
 "29": "fourth advisor at the flagship: Saturdays and cover days (en), the full two-on, two-off rota (ru)",
 "F1": "fired five months ago: unapproved cash discounts; voids and a short till (en), parts written off with no sale and work done past the order (ru)",
 "F2": "fired four months ago: late four shifts in ten, five absences",
 "F3": "resigned seven months ago for a dealership; why the newcomer was hired",
 "F4": "seasonal helper; contract ended",
}
def tenure(p, k):
    x = p[k]
    if "seasons_calendar" in x: return "seasonal"
    s = "%g" % x["start_months_before_t"]
    if "at_shop_since_months_before_t" in x: s += " (at the shop %g)" % x["at_shop_since_months_before_t"]
    if "end_months_before_t" in x: s += " to %g" % x["end_months_before_t"]
    return s
rows = ["| Slot | Site | Role, English / Russian | Rank | Ext. | English name, age | Russian name, age | Months before T: en / ru | In one line |", "|---|---|---|---|---|---|---|---|---|"]
for p in c["people"]:
    r = c["roles"][p["role_key"]]
    site = p["site"] + ("" if not p.get("also_sites") else " + " + " + ".join(p["also_sites"]))
    rows.append("| %s | %s | %s / %s | %s | %s | %s, %d | %s, %d | %s / %s | %s |" % (
        p["slot"], site, r["en"], r["ru"], p["rank"] or "none", p["extension"] or "", p["en"]["full_name"], p["en"]["age"],
        p["ru"]["full_name"], p["ru"]["age"], tenure(p, "en"), tenure(p, "ru"), ONE[p["slot"]]))
EN = """## Who is who (read this before a demo)

Brennan Auto Care is a family repair company, thirty years old: two shops in Chattanooga (East Main, the flagship, and Bonny Oaks) and a third on Charlotte Pike in Nashville, bought fourteen months ago and an hour behind on the clock. Most of the bad news comes from Nashville.

- **You drive the demo as two people.** Maya Torres is the junior: a service advisor at the flagship, eighteen months in, the fastest on chat and a little better on the phone every month. Greg Whitaker is the senior: he runs service for both Chattanooga shops, plans the shifts, hands out the tasks and approves discounts and team notes.
- **The owners.** Ray Brennan founded the company and now reads the morning brief on his phone. His daughter Claire runs the money, bought the Nashville shop and asks the data questions.
- **The people the stories lean on.** Angie Holloway at Bonny Oaks sells seven recommendations in ten; on her days off the shop sells five, and her week off is not covered. Brenda Pickett, part-time, is who the flagship calls when the desk is short. Kevin Lawson is the diagnostician nobody can replace. Dustin Swafford bills the most and is the hardest to schedule. Caleb Sutton, three months in, promised a price from an old page. Cody Gann is ten minutes late three mornings in ten and has never missed a day.
- **Nashville.** Dale Hutchins managed the shop before it was bought and hears every question as an accusation. Chad Binkley is the weakest desk in the company. Jasmine Bolden, hired after the purchase, shows it can be done. Derek Hooper's brake jobs come back. Brent Lassiter, fired five months ago, is the name under the discounts and the missing money.
- **Customers to know.** Nickajack Delivery is the anchor fleet and pays later every month. Cumberland Bend Electric has left. Sourwood Catering is fading.
"""
RU = """## Кто есть кто (прочитать перед показом)

«Ермак-Сервис» — семейная компания, которой тридцать лет: два сервиса в Ульяновске (главный — на Московском шоссе, второй — в Новом городе) и третий в Казани, на Технической. Казанский купили четырнадцать месяцев назад; там на час меньше, и оттуда приходит большая часть плохих новостей.

- **Показ ведётся от двух лиц.** Алина Хасанова — мастер-приёмщик на Московском шоссе, работает полтора года: быстрее всех отвечает в чате и с каждым месяцем увереннее говорит по телефону. Сергей Анатольевич Мельников — руководитель сервиса: на нём обе ульяновские площадки, график, задачи, скидки и заметки для команды.
- **Владельцы.** Основатель Николай Петрович Ермолаев в сервисе бывает редко и утреннюю сводку читает с телефона. Его дочь Екатерина Николаевна — директор: деньги, развитие, покупка казанского сервиса и вопросы к данным — её.
- **На ком держатся истории.** Светлана Демидова в Новом городе продаёт семь рекомендаций из десяти, без неё сервис продаёт пять, а её отпуск пока некем закрыть. Татьяна Геннадьевна Пахомова работает в одной смене с Алиной и подстраховывает её. Диагноста Андрея Шубина заменить некем. У Макса Рябова лучшая выработка и самый трудный характер в цехе. Никита Ведяшкин работает три месяца и уже пообещал клиенту цену со старой страницы. Женя Чугунов опаздывает три утра из десяти и ни разу не прогулял.
- **Казань.** Ринат Фаридович Галиев руководил сервисом ещё при прежнем владельце и любой вопрос из Ульяновска воспринимает как упрёк. У Славы Крюкова самая слабая приёмка в компании. Камила Шакирова пришла уже при новых владельцах и показывает, что можно работать иначе. У Виталия Сомова возвращаются машины после ремонта тормозов. Артур Назаров уволен пять месяцев назад: под его фамилией в учёте несогласованные скидки и недостача.
- **Клиенты, которых нужно знать.** «Симбирский гонец» — главный корпоративный клиент, платит с каждым месяцем позже. «Идель-Электромонтаж» ушёл. «Вкусный выезд» уходит.
"""
out = "# Cast of seed v1\n\nGenerated from `cast.json`; edit that file, not this one. Biographies and voice notes are in the JSON. Months are counted back from T, the day of generation. Each person's numbers are in `ledger.json` under the prefix `pNN`.\n\n" + "\n".join(rows) + "\n\n" + EN + "\n" + RU
open(D + "cast.md", "w", encoding="utf-8").write(out)
print(len(out))
