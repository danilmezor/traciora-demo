from kbb import *

RU_PB = ['Same playbook for the same rank; examples from the Russian stories and channels. The product pins the playbooks folder at administrator in both configurations.']

page('playbooks/README.md', 'Playbooks', 'A', 2,
 'Index of the rank playbooks; states plainly that only the administrator can open them.',
 f"""*{S(2,'full')} · {D('@golive+2w')}*

One page per rank: what a person at that rank uses Traciora for here, what they can ask it, and what it will not do for them.

- [Technicians](technician.md)
- [Service advisors](advisor.md)
- [Lead advisors and the office](lead-and-office.md)
- [Managers](manager.md)
- [Owner and administrator](owner.md)

This folder is visible to the administrator only. That is how the product ships it. What each rank needs to read day to day is therefore repeated where they can see it: for technicians in [Shop floor](../shop-floor/README.md), for the counter in [How we do things](../how-to/README.md).
""",
 serves=['visibility:administrator', 'operate:overview'],
 facts=['Five playbooks: technician (worker rank), advisor (junior), lead and office (middle), manager (senior), owner (administrator).',
        'The folder is pinned at administrator by the product\'s import; staff-facing copies of what matters live in shop-floor/ and how-to/.'],
 created=(2, '@golive+2w'),
 ru=RU_PB)

page('playbooks/technician.md', 'Playbook: technicians', 'A', 2,
 'Worker rank: what a technician does in Traciora and what the assistant will and will not answer.',
 f"""*For {S(10)}, {S(11)}, {S(12)}, {S(13)}, {S(14)}, {S(15)}, {S(18)}, {S(19)}, {S(20)}, {S(21)}, {S(25)}, {S(26)}, {S(27)}, {S(28)}.*

## What you have

Home, Shifts, Ask, Calendar and the bell.

- **Home:** today's shift, the clock-in button, anything waiting for you (a forgotten clock-out, an answer to a request).
- **Shifts:** your week, two weeks ahead. Ask for a change on the shift itself, with a reason.
- **Ask:** the assistant. For you it knows your own schedule and what is written in Shop floor.
- **Calendar:** your own. Meetings you are invited to; say yes or no.

## Ask it

- "When do I work next week?"
- "Who is on with me Saturday?"
- "I forgot to clock out yesterday, what do I do?"
- "Can I move my Thursday shift?" It will open the request for you: a change of date, with who takes the shift. It cannot approve it.
- "What do I check before a car leaves?"

## It will not

- Show you anyone else's hours, punches or lateness.
- Show you prices, customers, orders or the board. That is the counter's.
- Tell you pay or time-off balances. See {S(3)}.
- Approve anything.

## House rules

Clock in at the shop. A reason on every request. If the app is wrong about you, tell your foreman the same day.
""",
 serves=['S14', 'visibility:administrator'],
 facts=['Worker rank screens: Home, Shifts, Ask, Calendar, Inbox bell (design 1.4).',
        'Workers have no data tools, board or knowledge screen; the assistant reads the worker-visible folders for them.',
        'Listed for the fourteen technicians by slot.',
        'The assistant can open a shift request and cannot approve it.'],
 created=(2, '@golive+2w'),
 rev=[(2, '@newcomers', 'the list of technicians at the head gained the apprentice, who started the week before; message: "Hunter is on the list."')],
 ru=RU_PB)

page('playbooks/advisor.md', 'Playbook: service advisors', 'A', 2,
 'Junior rank: what an advisor uses Traciora for, with the call scorecard as the centre.',
 f"""*For {S(6)}, {S(7)}, {S(29)}, {S(17)}, {S(23)}, {S(24)}; and {S(8)} and {S(9)}, who hold the same rank.*

## What you have

Everything a technician has, plus: the board, Conversations, Calls, the knowledge base, and questions about the shop's data.

## The phone

Every call from a new caller is scored on eight things: [Taking a call](../how-to/taking-a-call.md). After each one you get your strongest moment and one thing to try next. One thing, not eight.

- Read the "try next" before your next shift, not at the end of the month.
- Offering a time and asking for the booking are worth the most. A friendly call that ends on the price scores badly, and should.
- Three things fail a call whatever else you did: a wrong promise, a dropped customer, a call back you did not make.
- A bad line or a garbled transcript can cost you a point you earned. If a score looks wrong, tell {S(4)}; do not argue with the screen.

## The To call back list

Claim, call within the hour, three tries: [Missed calls](../how-to/missed-calls-and-call-backs.md).

## Conversations

Web chat is answered by the assistant from the public pages and handed to you when the customer wants a time. Telegram is drafted for you. You send; you are responsible for what is sent.

## Ask it

- "What do we charge for front pads and rotors on a 2015 Camry?" It reads the price list.
- "Tell me everything about this customer." It joins the chat, the call and the visit by the phone number.
- "What did she decline last time?"
- "Which of my tasks are due this week?"
- "What is our rule on discounts?"

## It will not

- Give you a customer's phone or address in a list. You see them one customer at a time.
- Show you colleagues' call scores, pay or till counts.
- Change a knowledge page. You can ask it to draft a correction; a lead advisor proposes it.

## Notes

When the assistant gets something about how you work wrong, tell it. It keeps a note for you. If the whole team should do it, propose it as a team note and {S(4)} decides. Facts about a customer or a price are not notes. They belong on a page.
""",
 serves=['S4', 'S3', 'S7', 'visibility:administrator'],
 facts=['Junior rank adds board, conversations, calls, knowledge and data tools (design 1.4).',
        'The scorecard: eight checks, strongest moment and one "try next" per call; offered time and asked-for-booking weigh most; three automatic fails; recognition damage can cost a point (calls design: truth beside verdict).',
        'The To call back list: claim, one hour, three tries.',
        'Web chat sends, Telegram drafts.',
        'Limits: no bulk customer contact data (ERP access by rank), no colleagues\' scores, pay or till counts; cannot change a page (propose rung is middle).',
        'Notes: personal notes are about how the assistant works with the person; team notes are decided by slot 4; customer and price facts belong on pages (review resolution for S4).',
        'Slots 8 and 9 hold junior rank.'],
 created=(2, '@golive+2w'),
 rev=[(2, 'T-4mo', 'section "The phone" rewritten when the scorecard came in; message: "Eight checks."'),
      (2, '@newcomers', 'the list of advisors at the head gained the newcomer on his first day; message: "Caleb is on the list."')],
 ru=RU_PB)

page('playbooks/lead-and-office.md', 'Playbook: lead advisors and the office', 'A', 2,
 'Middle rank: what the lead advisors and the office manager can do beyond an advisor.',
 f"""*For {S(5)}, {S(16)} and {S(3)}.*

## What you have beyond an advisor

- A year of history instead of six months.
- Customers' contact details in lists, when you need them for statements or call backs.
- Conversation numbers for the period and by person.
- **You can propose a change to a knowledge page.** {S(4)}, {S(22)}, {S(1)} or {S(2)} decides it.
- {S(3)} also reads pay and the till counts, because the books need them.

## What we expect of a lead

- You are the price check. A newcomer's estimate does not go out unread.
- You are the page check. When a price or a rule changes, the service pages you keep are right within five working days. If you find a wrong page, propose the fix that day and say why in the proposal.
- You take the hard call and hand it up with a card when it needs money to fix.
- You do not approve discounts over 10 %. You ask.

## Ask it

- "Which service pages still show the old labour rate?"
- "Draft a correction to the timing belt page." It shows you the exact change on a card. You confirm; it goes to the deciders.
- "Which estimates have been waiting more than a day?"
- "Whose calls should a new advisor listen to?" It will say that scores across colleagues are a manager's view, and it is right.

## It will not

- Publish a page change for you, or approve your own proposal.
- Show you colleagues' call scores.
- Decide a team note.
""",
 serves=['S12', 'operate:propose', 'visibility:administrator'],
 facts=['Middle rank: history window 365 days against 180 for junior; customer contact details in lists; conversation statistics by period and operator; can propose knowledge changes (product defaults).',
        'Slot 3 reads pay and till counts (design 7.2: the ERP rule opens them from middle).',
        'Lead duties: price check, page check within five working days, hard calls handed up with a card, no approval of discounts over 10 %.',
        'Example: "Draft a correction to the timing belt page" is what slot 5 did at T-8 days (S12).',
        'Colleagues\' call scores are a senior view.'],
 created=(2, '@golive+2w'),
 ru=RU_PB)

page('playbooks/manager.md', 'Playbook: managers', 'A', 2,
 'Senior rank: planning shifts, deciding notes and page changes, seeing colleagues\' phone performance.',
 f"""*For {S(4)} and {S(22)}. {S(1)} holds this rank too and uses the morning brief.*

## What you have beyond a lead

- **The schedule is yours to plan and publish.** Requests come to your Inbox.
- **Team notes:** you approve or decline them. Give the reason; the person who proposed it reads it.
- **Knowledge pages:** you can change them and you decide other people's proposals.
- **Calls:** you see every advisor's scores, not only your own.
- The whole history, not a year.
- Pay and till counts.

## Every day

- "Needs you" on Home is the list. Shift requests, punch corrections, proposals waiting, cards handed to you. Empty it.
- Tomorrow's gaps in cover arrive at 4:30. Fill them before you go home.
- The To call back list is not yours to work. It is yours to look at.

## Every week

- Publish the following week by Thursday noon.
- Decide every proposal within five working days. A proposal that sits says the page does not matter.
- Read the calls of whoever scored lowest, and of whoever improved most. Tell both.

## Ask it

- "When do we miss the most calls?"
- "Who can cover the Bonny Oaks desk the week {S(16)} is off?"
- "Was that discount inside our rules?"
- "What is waiting for me to decide?"
- "Which shifts next week have nobody?"

## It will not

- Publish a schedule or decide a request without you pressing the button.
- Tell you what one shop's manager may not see of another's: you see your own shops' people in full and the company's numbers.
- Open the console. That is {S(2)}'s.

## Declining well

When you decline a note because it is already written down, name the page. "The page 'Booking a visit' already says this; propose the wording there" teaches. "Duplicate" does not.
""",
 serves=['S4', 'S5', 'S12', 'S14', 'operate:find-waiting', 'visibility:administrator'],
 facts=['Senior rank: plans and publishes shifts; decides team notes and knowledge proposals; sees colleagues\' phone performance; whole history; pay and till counts (design 1.4, 2.6).',
        'Daily: "Needs you"; the cover-gaps report at 16:30 (S10: slot 4\'s scheduled task). Weekly: publish by Thursday noon; decide proposals within five working days; read calls.',
        'The decline example quotes slot 4\'s reason for slot 6\'s note (S4).',
        'Slot 1 holds senior rank and uses the morning brief.'],
 created=(2, '@golive+2w'),
 rev=[(2, '@note_declined', 'added the section "Declining well" after the first declined team note; message: "Name the page."')],
 ru=RU_PB)

page('playbooks/owner.md', 'Playbook: owner and administrator', 'A', 2,
 'Administrator: the managing owner\'s own notes on running the product.',
 f"""*For me. And for whoever does this job when I am on holiday.*

## What only the administrator has

The console: people and ranks, job roles, feature switches, the connected shop system, scheduled jobs, alerts, usage. And the knowledge base's ranks: who may propose, who may publish, who sees which folder.

## How the knowledge base is ranked here

| Folder | Seen from |
|---|---|
| customers, shop-floor, services, and the price list | Everyone, and the website assistant |
| the rest of prices, and policies, accounts, how-to, parts, shops, team | Advisors and up |
| accounts/credit, office | Lead advisors, the office and up |
| management | Managers and up |
| management/owners, playbooks | Me |

Anything in the first row can be quoted to a customer by the website assistant. Before you move a page there, read it as a customer would.

Propose from lead advisor. Publish from manager. I left those where they shipped.

## My reports

- Monday 8:00: company accounts this week.
- Friday 4:00: discounts over 10 %.
- Monday 9:00: Charlotte Pike against plan.
- Daily 6:00 p.m.: missed calls today.

If one fails it says so in my Inbox. Run it again from there; do not wait for next week.

## When someone leaves

End their sign-in the same day. Take them off [Who is who](../team/who-is-who.md). Their name stays on what they did; that is correct.

## When a price changes

[How prices change](../prices/how-prices-change.md). The price list first. Then the service pages, which is the step I skipped once.
""",
 serves=['S10', 'S12', 'visibility:administrator', 'challenge:fact-in-table'],
 facts=['Administrator: the console (people, ranks, job roles, switches, sources, jobs, alerts, usage) and the knowledge ranks.',
        'Visibility table of the whole base by folder (the rank design of this seed): customers, shop-floor, services and the price list at worker rank (also the website assistant); the other staff folders and the rest of prices at junior; accounts/credit and office at middle; management at senior; management/owners and playbooks at administrator.',
        'Rungs left at product defaults: propose from middle, publish from senior.',
        'Slot 2\'s scheduled tasks (design S10 as corrected in 7.2: the monthly report became weekly): accounts Monday 8:00; discounts Friday 16:00; Charlotte Pike against plan weekly, Monday 9:00; missed calls daily 18:00 (ledger s10.tasks).',
        'Leavers: sign-in ended the same day, removed from the directory, their name stays in history (S2, S14).'],
 new=['The owner\'s weekly report on the Nashville shop is called "Charlotte Pike against plan" on the page; ledger s10.tasks holds it as "west against plan", Monday 09:00 home time. The scheduled-task definition carries the page\'s name.'],
 created=(2, '@golive+2w'),
 rev=[(2, '@belt_proposal', 'added the section "When a price changes"; message: "After the timing belt."')],
 ru=RU_PB)
