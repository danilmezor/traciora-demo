# Assembled sample: 60 background conversations (English)

Built by `checks/check_conv_bank_en.py` from the bank in this folder with random seed 20261113. Slots are filled with sample values the check script draws (names invented, phones in the 555 range, cars from `parc.json`, prices from `catalogue.json` and the public pages); a real build takes them from the generator's scenario. Drafts and notes are shown in italics; only plain lines reach the customer.

### 1. complaint · web chat · `complaint.web.3` · handed over · slot 24 Jasmine Bolden (Charlotte Pike)

- **customer:** nobody called me back
- **customer:** just being honest
- **assistant:** Good morning! I'm the assistant for Brennan Auto Care. Thank you for telling us, and I'm sorry. I'll pass this on now so a person at the shop can sort it out. What's the best number for the desk to reach you?
- **customer:** Jamal (615)555-9369
- **assistant:** Got it, Jamal. It's with the shop now; somebody will get back to you as soon as possible.
- *hand-over (escalation), the bot's private note: Complaint, in the customer's words: 'nobody called me back'. I said sorry and passed it on; I promised nothing.*
- *draft, discarded: You're welcome! Somebody from the shop will be in touch.*
- **Jasmine (24):** Hi Jamal, Jasmine here at the Charlotte Pike shop. Thank you for your patience. I'm sorry, Jamal. To confirm: 2023 Kia Soul, worked on Friday. Can you bring it by tomorrow at 7:30?
- **customer:** ok thank you
- — handed over

### 2. booking · web chat · `booking.web.1` · handed over · slot 7 Caleb Sutton (East Main) · after hours

- **customer:** is it first come first serve or do i need an appt for spark plugs
- **assistant:** Hi there! I'm the Brennan Auto Care assistant. The shops open at 7:30 tomorrow, and in the meantime I'm happy to help. Booking is handled by the service desk, not by me. I'll pass it on so they can set it up with you. Could I get your name and a phone number for the desk? And which shop works better: East Main Street or Bonny Oaks Drive?
- **customer:** 423-555-8891 thats my cell
- **customer:** east main by my work
- **assistant:** Thank you. Your question is with the team now, and somebody will get back to you as soon as possible.
- *hand-over (scheduling), the bot's private note: Booking request in the customer's words: 'is it first come first serve or do i need an appt for spark plugs'. I said the desk confirms the time.*
- **customer:** ok perfect thanks
- *draft, discarded: You're welcome, Courtney. Have a good night!*
- **Caleb (7):** Hi Courtney, Caleb at East Main. Yes ma'am, I can help with that! Should be able to do tomorrow, how about 10:30?
- **customer:** 10:30 👍
- *draft, sent edited: Thank you, Courtney. Tomorrow at 10:30 works. See you then!*
- **Caleb (7):** Thank you, Courtney! Tomorrow at 10:30 works, see you then!
- (label_added booking)
- (resolved)
- — handed over

### 3. symptom · Telegram · `symptom.tg.3` · person · slot 24 Jasmine Bolden (Charlotte Pike)

- **customer:**  [voice message: voice-1, 0:27]
- *draft, discarded: Thanks for the voice message, Brent. Could you type the main points so I get it right?*
- **Jasmine (24):** To confirm: 2024 Ford Transit 150, pedal feels spongy. I can take it Wednesday at 11:15 or Thursday at 1:00. The brake fluid flush is $151.00.
- **customer:** lets do Wednesday
- *draft, sent edited: Thank you, Brent. See you Wednesday at 11:15 at 6399 Charlotte Pike.*
- **Jasmine (24):** You're booked, Brent: Wednesday at 11:15, brake fluid flush on the Transit 150.
- — person

### 4. booking · Telegram · `booking.tg.5` · silent · slot 22 Dale Hutchins (Charlotte Pike)

- **customer:** Dale yall got room this week?
- *draft, discarded: Hi Marcus. Would a morning or an afternoon suit you better? I'll confirm the exact time.*
- **Dale (22):** drop it off, we'll get to it
- — silent

### 5. price · Telegram · `price.tg.1` · person · slot 16 Angie Holloway (Bonny Oaks) · unclear u06, after one

- **customer:** how much for a new transmission
- *draft, sent as is: What's it doing that makes you think it needs one?*
- **Angie (16):** What's it doing that makes you think it needs one?
- **customer:** its fine, just hasnt had the fluid changed ever
- *draft, sent edited: Thanks for asking, Earl. Our listed price for automatic transmission fluid drain & fill is $191.98 before tax; the exact figure for the Wrangler comes on the estimate.*
- **Angie (16):** Earl, I'd want to see it first so I don't quote you the wrong thing: the transmission fluid service is $202.55, and I'll send you photos before you spend a dime more. Tuesday at 10:30 or Friday at 1:00? / Angie
- **customer:** ok lets do it
- *draft, sent as is: Thanks, Earl. What day were you thinking? I'll check what we have and confirm a time.*
- **Angie (16):** Thanks, Earl. What day were you thinking? I'll check what we have and confirm a time.
- **Angie (16):** Let's get it in, Earl. I have Tuesday at 10:30 or Friday at 1:00. / Angie
- **customer:** the later one, i work mornings
- *draft, discarded: You're all set for Friday at 1:00, Earl.*
- **Angie (16):** Got you down, Earl: Friday at 1:00. Bring any paperwork from last time and I'll go over it with you. / Angie
- (label_added price)
- (resolved)
- — person

### 6. booking · Telegram · `booking.tg.1` · person · slot 7 Caleb Sutton (East Main)

- **customer:** hey Caleb can i bring the subaru impreza by tomorrow for a brake check
- *draft, sent as is: Hi Tasha! We'd be glad to take care of the Impreza. Which day works best for you? I'll confirm a time.*
- **Caleb (7):** Hi Tasha! We'd be glad to take care of the Impreza. Which day works best for you? I'll confirm a time.
- **Caleb (7):** Yes ma'am, we can get you in tomorrow at 11:15!
- **customer:** tomorrow 11:15 is good
- *draft, sent as is: Thank you, Tasha. Tomorrow at 11:15 works. See you then!*
- **Caleb (7):** Thank you, Tasha. Tomorrow at 11:15 works. See you then!
- (label_added booking)
- (resolved)
- — person

### 7. booking · web chat · `booking.web.5` · handed over · slot 17 Josh Tipton (Bonny Oaks) · after hours

- **customer:** do yall have anything this week
- **customer:** whenever yall have room
- **assistant:** Hello, this is Brennan Auto Care's assistant. We're closed for the night and open again at 7:30 tomorrow; I can answer what I can until then. I can't book a time myself, but I'll pass your request to the service desk and they'll confirm it with you. What's your name and the best number to reach you?
- **customer:** 4235554359. do yall have a shuttle
- **assistant:** East Main and Bonny Oaks run a free shuttle for customers within 5 miles of the shop, morning and afternoon. Charlotte Pike doesn't run one. Got it, thanks. The team has your message now, and somebody will get back to you as soon as possible.
- *hand-over (scheduling), the bot's private note: Wants a time: 'do yall have anything this week'. I booked nothing.*
- **Josh (17):** Hey Rhonda! Josh here at Bonny Oaks, saw your message. Come by Friday around 8:00, we'll get you taken care of
- **customer:** ill take 8:00
- *draft, sent as is: Thank you, Rhonda. See you Friday at 8:00 at 6340 Bonny Oaks Drive.*
- **Josh (17):** Thank you, Rhonda. See you Friday at 8:00 at 6340 Bonny Oaks Drive.
- — handed over

### 8. found_work · Telegram · `found_work.tg.1` · person · slot 17 Josh Tipton (Bonny Oaks) · unclear u05, after one

- **Josh (17):** $777.57 for the radiator. Up to you [estimate-pdf]
- **customer:** go ahead with the stuff
- *draft, sent as is: Happy to. Which items should we go ahead with?*
- **Josh (17):** Happy to. Which items should we go ahead with?
- **customer:** the first one only
- *draft, discarded: Got it, Lamar: yes to the radiator, no to the rest for now. I'll note the rest on your record.*
- **Josh (17):** Bet, doing it now
- (label_added approval)
- — person

### 9. spam · web chat · `spam.web.5` · alone · after hours

- **customer:** hello
- **assistant:** Hi! I'm the assistant for Brennan Auto Care. The shops are closed right now and open at 7:30 tomorrow, but I can help in the meantime. How can I help you today?
- — alone

### 10. booking · Telegram · `booking.tg.7` · person · slot 6 Maya Torres (East Main)

- **customer:** can i get in this week for a battery
- **customer:** mornings are better for me
- *draft, sent edited: Hi Derrick. Would a morning or an afternoon suit you better? I'll confirm the exact time.*
- **Maya (6):** I can do Wednesday at 7:30 or Tuesday at 2:15, and it takes half an hour either way. Which one works better for you?
- **customer:** how much for that btw
- *draft, sent as is: Hi Derrick! For a typical car, replacement runs $198.28 to $334.95 before tax, depending on the parts. We'd give you the exact figure for the Corolla after a look.*
- **Maya (6):** Hi Derrick! For a typical car, replacement runs $198.28 to $334.95 before tax, depending on the parts. We'd give you the exact figure for the Corolla after a look.
- **customer:** whatever you have this week
- *draft, discarded: Thanks, Derrick. What day were you thinking? I'll check what we have and confirm a time.*
- **Maya (6):** Absolutely, let me get that set up for you! I have Wednesday at 7:30, or if mornings are easier, Tuesday at 2:15.
- **customer:** the first one
- *draft, sent as is: You're all set for Wednesday at 7:30, Derrick.*
- **Maya (6):** You're all set for Wednesday at 7:30, Derrick.
- — person

### 11. moving · web chat · `moving.web.1` · handed over · unclear u15, never · after hours

- **customer:** need to move my appt and add the brakes
- **assistant:** Hi there! I'm the Brennan Auto Care assistant. The shops open at 7:30 Monday, and in the meantime I'm happy to help. Sure. Do you want a new day, or to keep the day and add brakes?
- **customer:** the appointment
- **assistant:** Let me know which change you'd like and the desk will set it.
- — ended unclear: the customer stopped answering

### 12. booking · web chat · `booking.web.7` · silent · slot 6 Maya Torres (East Main)

- **customer:** I need to make an appointment for oil and filter. Is next week around noon available? If not, what is?
- **assistant:** Hi! I'm the assistant for Brennan Auto Care. I'm not able to book appointments, but I can send your request to an advisor, who will confirm a time with you. Who should they ask for, and what's the best number?
- **customer:** 423 555 8321 (Hank)
- **assistant:** Thanks, Hank. I've passed it to the service desk, and somebody will get back to you as soon as possible.
- *hand-over (scheduling), the bot's private note: 'I need to make an appointment for oil and filter. Is next week around noon available? If...'. Asks to come in; I can't book, so nothing is set.*
- *draft, discarded: Thank you, Hank. Take care.*
- **Maya (6):** Good morning Hank, this is Maya at Brennan Auto Care on East Main. I got your message from last night. The soonest I have is tomorrow at 1:00. It takes half an hour, and our shuttle can run you home if you need it.
- — silent

### 13. hours · web chat · `hours.web.1` · alone

- **customer:** hours?
- **assistant:** Hello! I'm the Brennan Auto Care assistant. We're open 7:30 a.m. to 5:30 p.m., Monday to Friday, at all three shops. Charlotte Pike in Nashville keeps the same hours on Central time.
- — alone

### 14. status · Telegram · `status.tg.1` · person · slot 29 Brenda Pickett (East Main) · unclear u13, after two

- **customer:** ready? and how much do i owe
- *draft, sent as is: Which car is this about?*
- **Brenda (29):** Which car is this about?
- **customer:** the car
- *draft, discarded: Which car is this about?*
- **Brenda (29):** I see more than one car on your name. Is it the town & country or the other one? / - Brenda
- **customer:** oh we have two in there. the town & country
- *draft, discarded: Hi Jessica! I don't have the status in front of me; I'll check with the technician and let you know.*
- **Brenda (29):** It is all finished, ma'am. You can pick it up any time before 5:30 p.m. / - Brenda
- **customer:** see you then
- *draft, discarded: You're welcome, Jessica!*
- **Brenda (29):** You are welcome, Jessica. Have a good weekend. / - Brenda
- (resolved)
- — person

### 15. symptom · Telegram · `symptom.tg.8` · person · slot 6 Maya Torres (East Main)

- **customer:** ac is blowing hot again
- *draft, sent as is: Hi Felicia. I'm sorry to hear that. That should be checked soon. Would you like to bring the Elantra in?*
- **Maya (6):** Hi Felicia. I'm sorry to hear that. That should be checked soon. Would you like to bring the Elantra in?
- **customer:** mornings are better
- *draft, discarded: Hi Felicia! We'd be glad to take care of the Elantra. Which day works best for you? I'll confirm a time.*
- **Maya (6):** I have you penciled in for Wednesday at 8:00. If you need it earlier I can also do 1:00. Just let me know!
- **customer:** i can do 1:00
- *draft, sent edited: Thank you, Felicia. Friday at 1:00 works. See you then!*
- **Maya (6):** You're all set for Friday at 1:00 for the A/C performance check on the Elantra. See you then!
- — person

### 16. symptom · web chat · `symptom.web.2` · alone

- **customer:** grinding noise when i stop
- **customer:** idk if its serious
- **assistant:** Hi there, this is Brennan Auto Care's assistant. A squeal on the first few stops on a damp morning is usually surface rust and clears itself. If it stays, or it grinds, a brake inspection is $49.95.
- **customer:** ok thanks, ill call them
- **assistant:** Sounds good. Have a good one!
- — alone

### 17. fleet · web chat · `fleet.web.3` · handed over · slot 24 Jasmine Bolden (Charlotte Pike)

- **customer:** Our office needs the invoice for ND-03 for the statement.
- **assistant:** Hi! I'm the assistant for Brennan Auto Care. Company vehicles are handled by the advisors, who keep each vehicle's history under your company name. I'll send this to them. Who should they ask for, and what's the best number?
- **customer:** Linda Qualls. 6155558953. call after lunch if you can
- **assistant:** Thank you, Linda. Your request is with the team now, and somebody will get back to you as soon as possible.
- *hand-over (escalation), the bot's private note: Company vehicle: 'Our office needs the invoice for ND-03 for the statement.'. I gave no account prices.*
- *draft, discarded: You're welcome! Somebody from the shop will be in touch.*
- **Jasmine (24):** Good morning, Linda, this is Jasmine at Charlotte Pike. To confirm: Linda Qualls, (615) 555-8953, 2019 Ford Transit-250 Cargo Van. I'll send the statement copy to your office email by end of day.
- — handed over

### 18. booking · web chat · `booking.web.8` · handed over · slot 23 Chad Binkley (Charlotte Pike)

- **customer:** any chance today? acting funny
- **assistant:** Hello! I'm the Brennan Auto Care assistant. I'm not able to book appointments, but I can send your request to an advisor, who will confirm a time with you. What's your name and the best number to reach you?
- **customer:** 615.555.2286 ask for Tyrone
- **assistant:** Thank you, Tyrone. Your request is with the team now, and somebody will get back to you as soon as possible.
- *hand-over (scheduling), the bot's private note: 'any chance today? acting funny'. Asks to come in; I can't book, so nothing is set.*
- **customer:** thanks yall
- *draft, discarded: Thank you, Tyrone. Take care.*
- **Chad (23):** chad at charlotte pike. bring it in Wednesday morning
- **customer:** hmm ok let me see and get back to you
- *draft, discarded: Sounds good, Tyrone. We're here when you're ready.*
- **Chad (23):** aight
- — handed over

### 19. status · web chat · `status.web.4` · handed over · slot 16 Angie Holloway (Bonny Oaks) · unclear u13, after two

- **customer:** ready? and how much do i owe
- **assistant:** Hi there, this is Brennan Auto Care's assistant. Which car is this about?
- **customer:** the car
- **assistant:** I see more than one car on your name. Is it the 21 explorer or the other one?
- **customer:** the 21 explorer. not the truck
- **assistant:** Got it, the 21 explorer. Thanks. I don't have access to the shop's system, so I can't tell you where your car is. The service desk can, and I'll send them your question. Could I get your name and a phone number for the desk?
- **customer:** Dustin Whitlow / (423)555-0556
- **assistant:** Got it, Dustin. It's with the shop now; somebody will get back to you as soon as possible.
- *hand-over (escalation), the bot's private note: 'ready? and how much do i owe'. Status question; I gave no date and no total.*
- *draft, discarded: You're welcome, Dustin. Have a good night!*
- **Angie (16):** Good afternoon, Dustin, it's Angie at Brennan's Bonny Oaks shop. Let's sort this out, Dustin. All done, Dustin! The check engine diagnosis went fine, and the total is $154.86. See you before 5:30 p.m.? / Angie
- **customer:** great ill grab it after work
- — handed over

### 20. status · Telegram · `status.tg.6` · person · slot 7 Caleb Sutton (East Main)

- **customer:** can it be done by before work
- **customer:** its under Kayla
- *draft, replaced unseen: Thanks for checking in, Kayla. Let me find out where the F-150 is and get back to you.*
- *draft, sent as is: Hi Kayla. I don't have the status of the F-150 in front of me. I'll check with the shop and message you right back.*
- **Caleb (7):** Hi Kayla. I don't have the status of the F-150 in front of me. I'll check with the shop and message you right back.
- **Caleb (7):** Not yet but should be done by 1:00!
- **customer:** ok. thank you
- — person

### 21. price · web chat · `price.web.8` · alone

- **customer:** Hi, I was wondering what you charge for tire sensors. It's a ford focus. Thank you!
- **assistant:** Good morning! I'm the assistant for Brennan Auto Care. Our replacing one sensor is $128.86 before tax, for a car or small crossover. Would you like me to ask the shop to set up a time?
- **customer:** hm the other place said 80
- **assistant:** I don't know what the other shop includes, so I can't compare. Ours is the price on the list, and every repair comes with our written warranty.
- **customer:** hm ok
- — alone

### 22. price · web chat · `price.web.2` · alone

- **customer:** how much yall charge for trans fluid changes on a 17 prius
- **assistant:** Good morning! I'm the assistant for Brennan Auto Care. Automatic transmission fluid drain & fill is $191.98 on our price list, before tax. That's for a car or small crossover.
- **customer:** and thats everything? no extra fees
- **assistant:** Not quite: tax of 9.25 % goes on top, and repairs billed by the hour add shop supplies up to $35.00. The service desk can tell you your exact total.
- **customer:** okay
- — alone

### 23. status · Telegram · `status.tg.4` · person · slot 23 Chad Binkley (Charlotte Pike)

- **customer:** any news on the part
- *draft, discarded: Hi Amber. I don't have the status of the Versa in front of me. I'll check with the shop and message you right back.*
- **Chad (23):** part still not in
- **customer:** ?
- (priority high)
- *draft, sent edited: Hi Amber! I don't have the status in front of me; I'll check with the technician and let you know.*
- **Chad (23):** not in yet. should be early next week
- — person

### 24. fleet · Telegram · `fleet.tg.3` · person · slot 24 Jasmine Bolden (Charlotte Pike)

- **customer:** Status on Car 4?
- *draft, sent as is: Thanks for checking in, Rob. Let me find out where the Elantra is and get back to you.*
- **Jasmine (24):** Thanks for checking in, Rob. Let me find out where the Elantra is and get back to you.
- **Jasmine (24):** The part is due early next week. What I can do is call you the moment it arrives and give you a firm time then.
- **customer:** ok great
- **Jasmine (24):** Hi Rob! Your car is ready. Invoice attached: $664.92.
- — person

### 25. price · web chat · `price.web.1` · alone · unclear u10, after one

- **customer:** how much is an alignment it shakes on the interstate
- **assistant:** Hi! I'm the assistant for Brennan Auto Care. Does it pull to one side, or does it shake?
- **customer:** it pulls right too
- **assistant:** Thanks. A shake at speed is usually balance; a pull is alignment. Sure. On our price list, balance four wheels is $60.00 before shop supplies and tax, for a car like yours. The service desk has the exact figure for your Cruze.
- **customer:** appreciate it
- — alone

### 26. symptom · web chat · `symptom.web.5` · alone

- **customer:** ac not cold anymore
- **assistant:** Hello! I'm the Brennan Auto Care assistant. The first step is the A/C performance check, $49.95. It tells whether the system is just low or something has failed.
- **customer:** and a recharge is how much
- **assistant:** If it needs a recharge, the price depends on the refrigerant your car takes: $207.40 for most older cars, $278.80 for most newer ones. The label under the hood says which. A system that was empty has a leak, and the shop tells you so before you pay.
- **customer:** ok good to know
- — alone

### 27. booking · web chat · `booking.web.4` · handed over · slot 29 Brenda Pickett (East Main)

- **customer:** saturday appt possible?
- **assistant:** Hi there, this is Brennan Auto Care's assistant. On Saturday it's East Main only, 8:00 a.m. to 1:00 p.m. The other two shops open again on Monday. I can ask an advisor to contact you about it. Would that help?
- **customer:** yes main st works
- **assistant:** Who should they ask for, and what's the best number?
- **customer:** Lamar D 423 555 7562 main st
- **assistant:** Thanks, Lamar. I've passed it to the service desk, and somebody will get back to you as soon as possible.
- *hand-over (scheduling), the bot's private note: Booking request in the customer's words: 'saturday appt possible?'. I said the desk confirms the time.*
- *draft, discarded: You're welcome! Somebody from the shop will be in touch.*
- **Brenda (29):** Good morning, sir. This is Brenda at the East Main shop. I can help you with that. Let me read you what I have: Monday at 7:30, or Thursday at 1:00. / - Brenda
- **customer:** earlier one
- *draft, sent as is: Thank you, Lamar. See you Monday at 7:30 at 2106 East Main St.*
- **Brenda (29):** Thank you, Lamar. See you Monday at 7:30 at 2106 East Main St.
- — handed over

### 28. price · web chat · `price.web.7` · handed over · slot 7 Caleb Sutton (East Main)

- **customer:** got this quote from another place is this fair [photo: estimate-other-shop]
- **assistant:** Hi there, this is Brennan Auto Care's assistant. Thank you. I'm not able to compare an estimate from another shop, and I won't guess at a price for your car. An advisor can look at it with you; who should they ask for, and what's the best number?
- **customer:** (423)555-2370 its Bonnie
- **assistant:** Thanks, Bonnie. I've passed it to the service desk, and somebody will get back to you as soon as possible.
- *hand-over (escalation), the bot's private note: Price question: 'got this quote from another place is this fair'. I named the public figure or the first step and said the desk has the exact price.*
- *draft, discarded: You're welcome, Bonnie. Have a good night!*
- **Caleb (7):** Hey Bonnie, Caleb here at East Main. Yes ma'am, got your message! Yes ma'am, the steering and suspension inspection should be $49.95!
- **customer:** about the same then
- — handed over

### 29. complaint · web chat · `complaint.web.5` · handed over · slot 17 Josh Tipton (Bonny Oaks) · after hours

- **customer:** theres a handprint on my headliner
- **assistant:** Hello, this is Brennan Auto Care's assistant. We're closed for the night and open again at 7:30 tomorrow; I can answer what I can until then. I'm sorry to hear that. If the car needs to come back, the shop looks at it first and it costs you nothing to have it looked at. I'll pass this on now. What's the best number for the desk to reach you?
- **customer:** felicia burchett 423-555-3173 either shop is fine
- **assistant:** Thank you, Felicia. Your request is with the team now, and somebody will get back to you as soon as possible.
- *hand-over (escalation), the bot's private note: 'theres a handprint on my headliner'. Unhappy after a visit. I can't see the order or the bill; I quoted only the public pages.*
- *draft, discarded: Thank you, Felicia. Take care.*
- **Josh (17):** Whats up Felicia, Josh at Bonny Oaks. Got you. Thats not good, sorry. Can you swing by tomorrow?
- **customer:** thanks!
- — handed over

### 30. hours · web chat · `hours.web.4` · alone · after hours

- **customer:** saturday hours?
- **assistant:** Hi! I'm the assistant for Brennan Auto Care. The shops are closed right now and open at 7:30 Monday, but I can help in the meantime. On Saturday it's East Main only, 8:00 a.m. to 1:00 p.m. The other two shops open again on Monday.
- — alone

### 31. price · web chat · `price.web.4` · abandoned

- **customer:** my husband says it needs new shocks what would that cost me roughly i dont need exact just ballpark
- **assistant:** Good morning! I'm the assistant for Brennan Auto Care. That one depends on the car, so I won't guess. The shop starts with the steering and suspension inspection at $49.95, then gives you a written estimate with each job priced separately.
- **customer:** so you cant tell me a price at all?
- — abandoned

### 32. price · web chat · `price.web.3` · handed over · slot 7 Caleb Sutton (East Main)

- **customer:** Good afternoon. I would like a price on a new alternator for my grand caravan, please. I am on a fixed income and like to know ahead of time.
- **assistant:** Hello! I'm the Brennan Auto Care assistant. A price for that depends on what your car needs, so we look first. The first step is the battery, starting and charging test, which is free, and the technician shows you what they find before any repair is priced.
- **customer:** ok yeah can yall look at it this week
- **assistant:** Booking is handled by the service desk, not by me. I'll pass it on so they can set it up with you. Could I get your name and a phone number for the desk? Is that for one of the Chattanooga shops or for Charlotte Pike in Nashville?
- **customer:** (423)555-3724
- **assistant:** Thank you. It's with the service desk now, and somebody will get back to you as soon as possible.
- *hand-over (scheduling), the bot's private note: Asks a price, in the customer's words: 'Good afternoon. I would like a price on a new alternator for my grand caravan, please. I...'. I gave only what the public price page states and no price for this car.*
- *draft, discarded: You're welcome! Somebody from the shop will be in touch.*
- **Caleb (7):** Hi Hank, this is Caleb! Sorry for the wait, I'm on it now! I think we have 7:30 open Thursday, does that work?
- **customer:** Thursday at 7:30 please
- *draft, sent as is: You're all set for Thursday at 7:30, Hank.*
- **Caleb (7):** You're all set for Thursday at 7:30, Hank.
- (label_added price)
- — handed over

### 33. price · web chat · `price.web.6` · handed over · slot 23 Chad Binkley (Charlotte Pike) · after hours

- **customer:** can someone price rear pads on a grand caravan for me
- **assistant:** Hi there! I'm the Brennan Auto Care assistant. The shops open at 7:30 Monday, and in the meantime I'm happy to help. A price for a repair comes after the car is looked at, not before. You'd get it in writing and approve it job by job. Would you like me to ask the shop to get you in?
- **customer:** yes please have someone reach out
- **assistant:** Could I get your name and a phone number for the desk?
- **customer:** Derrick Gentry (615)555-4395
- **assistant:** Got it, Derrick. It's with the shop now; somebody will get back to you as soon as possible.
- *hand-over (escalation), the bot's private note: 'can someone price rear pads on a grand caravan for me'. I quoted nothing beyond the public pages; wants a person to price it.*
- *draft, discarded: You're welcome, Derrick. Have a good night!*
- **Chad (23):** hey this is chad. around $260.31
- **customer:** does that include tax and everything
- *draft, discarded: Good question, Derrick. That's the price of the job; shop supplies and sales tax are added on the bill, so the total will be a little higher.*
- **Chad (23):** thats with labor
- **customer:** ok ill get back to you
- — handed over

### 34. status · Telegram · `status.tg.1` · person · slot 17 Josh Tipton (Bonny Oaks) · unclear u04, after two

- **customer:** so is it good now
- *draft, sent as is: Which part are you asking about?*
- **Josh (17):** Which part are you asking about?
- **customer:** the problem
- *draft, discarded: Which part are you asking about?*
- **Josh (17):** There were two things on the order, the A/C and the noise. Which one are you asking about?
- **customer:** the ac. thats what i need for the trip
- *draft, discarded: Hi Kayla. I don't have the status of the ES 330 in front of me. I'll check with the shop and message you right back.*
- **Josh (17):** Its done, come grab it whenever
- **customer:** omw
- (resolved)
- — person

### 35. booking · web chat · `booking.web.3` · handed over · slot 17 Josh Tipton (Bonny Oaks) · after hours

- **customer:** can i drop it off tonight and yall look at it tomorrow
- **assistant:** Hi! I'm the assistant for Brennan Auto Care. The shops are closed right now and open at 7:30 Monday, but I can help in the meantime. Yes. Use the key drop by the office door; the envelope asks for your name, phone and what the car is doing, and the shop calls you once they've looked at it.
- **customer:** ok cool and someone will call me?
- **assistant:** Yes, the shop calls you once they've looked at it. I can also let the desk know it's coming: what's your name and the best number?
- **customer:** My name is Terrence Hollis and my number is (423)555-5207.
- **assistant:** Got it, thanks. The team has your message now, and somebody will get back to you as soon as possible.
- *hand-over (scheduling), the bot's private note: Wants a time: 'can i drop it off tonight and yall look at it tomorrow'. I booked nothing.*
- *draft, discarded: Thank you, Terrence. Take care.*
- **Josh (17):** Hey Terrence, this is Josh with Brennan out on Bonny Oaks. We can help with that. Sounds good, we'll check it out first thing
- **customer:** thanks a bunch
- — handed over

### 36. booking · web chat · `booking.web.6` · handed over · slot 7 Caleb Sutton (East Main)

- **customer:** hi this is Jessica Varner, 4235554384. need a tune up on my 09 camry tuesday
- **assistant:** Hi! I'm the assistant for Brennan Auto Care. I can't book a time myself, but I'll pass your request to the service desk and they'll confirm it with you. Thank you. It's with the service desk now, and somebody will get back to you as soon as possible.
- *hand-over (scheduling), the bot's private note: 'hi this is Jessica Varner, 4235554384. need a tune up on my 09 camry tuesday'. Asks to come in; I can't book, so nothing is set.*
- **Caleb (7):** Hi Jessica! This is Caleb at Brennan, no problem at all! Yes ma'am, Monday at 7:30 works!
- **customer:** 7:30
- *draft, sent as is: You're all set for Monday at 7:30, Jessica.*
- **Caleb (7):** You're all set for Monday at 7:30, Jessica.
- (label_added booking)
- — handed over

### 37. status · Telegram · `status.tg.3` · person · slot 7 Caleb Sutton (East Main)

- **Caleb (7):** It's ready to go! We're here till 5:30 p.m.!
- **customer:** be there after work
- **customer:** just checking
- — person

### 38. hours · web chat · `hours.web.2` · alone

- **customer:** address for the main st shop?
- **customer:** asking for my mom
- **assistant:** Good morning! I'm the assistant for Brennan Auto Care. Charlotte Pike is at 6399 Charlotte Pike. The phone there is (615) 555-0119.
- **customer:** thanks a bunch
- — alone

### 39. fleet · web chat · `fleet.web.1` · handed over · slot 17 Josh Tipton (Bonny Oaks)

- **customer:** we have a few work trucks, can we get an account
- **assistant:** Hello! I'm the Brennan Auto Care assistant. A business with five or more vehicles can apply for an account and pay on a monthly statement. To set one up, our page says to call Greg Whitaker, the service manager, at (423) 555-0142.
- **customer:** ok can someone call me instead
- **assistant:** What's the best number for the desk to reach you?
- **customer:** its Dennis Fitch. (423)555-7021
- **assistant:** Thanks, Dennis. I've passed it to the service desk, and somebody will get back to you as soon as possible.
- *hand-over (escalation), the bot's private note: 'we have a few work trucks, can we get an account'. Company account question; passed to the advisors.*
- *draft, discarded: You're welcome, Dennis. Have a good night!*
- **Josh (17):** Hey Dennis, Josh at Bonny Oaks. Gotcha, we'll get you taken care of. Hang on, asking the tech
- — handed over

### 40. hours · Telegram · `hours.tg.3` · person · slot 16 Angie Holloway (Bonny Oaks)

- **customer:** ok to leave it in the drop box tonight?
- *draft, sent edited: Of course, Carla. Use the key drop by the office door after hours; the envelope asks for your name, number and what the car is doing.*
- **Angie (16):** After hours the key drop is by the office door, Carla. Fill out the envelope and I'll call you first thing. / Angie
- **customer:** perfect
- — person

### 41. found_work · Telegram · `found_work.tg.2` · person · slot 6 Maya Torres (East Main)

- **Maya (6):** Hi Bonnie! While it was up, Dustin found the front tires are at 3/32 and worn on the inside edge. It's $779.91 and takes an hour. Would you like us to take care of it today? [estimate-pdf]
- **customer:** total?
- *draft, sent edited: Thank you, Bonnie. I'll confirm the total with shop supplies and tax.*
- **Maya (6):** Perfect. Your new total is $852.05 with tax, ready by 5:00.
- **customer:** ok go ahead
- *draft, sent as is: Thank you for the quick answer, Bonnie. We'll get started on the new tires.*
- **Maya (6):** Thank you for the quick answer, Bonnie. We'll get started on the new tires.
- — person

### 42. price · web chat · `price.web.5` · alone

- **customer:** hi there!! do yall do front breaks and how much 😊
- **assistant:** Hi! I'm the assistant for Brennan Auto Care. For a typical car, front pads and discs runs from $428.00 to $523.76 before tax. Where yours falls depends on the parts it takes, so I can't give you one number from here.
- **customer:** ok so somewhere in there
- **assistant:** That's the honest range. The exact figure for your Versa comes from an advisor.
- **customer:** you guys are the best
- — alone

### 43. hours · web chat · `hours.web.6` · alone

- **customer:** can i pay with a check
- **assistant:** Hi there, this is Brennan Auto Care's assistant. Credit, debit or cash. There's no discount for cash; the price is the price.
- **customer:** sounds good
- — alone

### 44. complaint · Telegram · `complaint.tg.4` · person · slot 17 Josh Tipton (Bonny Oaks)

- **customer:** how many times do i have to bring it back
- (priority high)
- *draft, discarded: Good morning, Marcus. I'm sorry about that. We'd like to look at it. Which day works for you?*
- **Josh (17):** I'll have Angie text you
- **customer:** ok
- **Josh (17):** My bad, we'll get you taken care of. Come by whenever
- — person

### 45. booking · web chat · `booking.web.2` · declined

- **customer:** Hello, I would like to schedule a transmission flush for my 20 expedition. Mornings are best for me. Thank you.
- **assistant:** Good morning! I'm the assistant for Brennan Auto Care. I can't book a time myself, but I'll pass your request to the service desk and they'll confirm it with you. What's the best number for the desk to reach you?
- **customer:** ill have my husband call
- **assistant:** No problem. The number for East Main is (423) 555-0142.
- — declined

### 46. found_work · Telegram · `found_work.tg.1` · person · slot 7 Caleb Sutton (East Main) · unclear u20, never

- **Caleb (7):** We also found the outer tie rod on the driver side has play, I think it's $178.91! Do you want it done today? [estimate-pdf]
- **customer:** yeah leave it
- *draft, sent as is: Just to be sure: do you want it done, or left for now?*
- **Caleb (7):** Just to be sure: do you want it done, or left for now?
- **customer:** yes
- — ended unclear: the customer stopped answering

### 47. price · web chat · `price.web.4` · abandoned

- **customer:** how much for the timing belt and water pump
- **assistant:** Hello! I'm the Brennan Auto Care assistant. I can't price that repair without the car being looked at; it depends on what's worn and the parts it takes. What I can tell you is that the timing belt is free, and nothing else is done until you approve it.
- **customer:** hmm ok
- **assistant:** Want me to pass this to the service desk so they can set up a time?
- — abandoned

### 48. moving · Telegram · `moving.tg.2` · person · slot 6 Maya Torres (East Main)

- **customer:** gotta cancel sorry
- **customer:** sorry for the trouble
- *draft, sent edited: Thanks for the heads-up, Brittany. It's cancelled on our end once I've updated it; message us any time.*
- **Maya (6):** Got it, I've taken you off the schedule. Just let me know when works better.
- — person

### 49. symptom · web chat · `symptom.web.3` · abandoned

- **customer:** is this bad [photo: puddle-under-car]
- **assistant:** Hi! I'm the assistant for Brennan Auto Care. Thanks, the picture helps. I can't tell from a photo what's leaking, and I won't guess. If the temperature gauge goes high or the oil light comes on, stop the engine and call the shop or have it towed.
- — abandoned

### 50. status · Telegram · `status.tg.2` · person · slot 24 Jasmine Bolden (Charlotte Pike)

- **customer:** need it back by after lunch if at all possible, i have to get the kids
- *draft, sent edited: Thanks for checking in, Felicia. Let me find out where the Focus is and get back to you.*
- **Jasmine (24):** Not yet, Felicia. It's next on the lift, and I'll update you by 2:15.
- **customer:** ugh ok
- **Jasmine (24):** All done, Felicia. The full synthetic oil change is complete and road tested. We're open until 5:30 p.m.
- **customer:** omw
- — person

### 51. price · web chat · `price.web.8` · alone

- **customer:** ballpark on wheels aligned? f-150
- **customer:** its a f-150
- **assistant:** Hi there, this is Brennan Auto Care's assistant. Yes, we do. Four-wheel alignment is $119.95 before tax. Larger SUVs, pickups and vans can cost more.
- **customer:** the other shop does it for $79
- **assistant:** I can't speak for another shop's price. With every service here you also get a free courtesy inspection with photos, so you see what the car needs before you decide.
- **customer:** ill think about it
- — alone

### 52. booking · web chat · `booking.web.4` · handed over · slot 29 Brenda Pickett (East Main)

- **customer:** can i come saturday morning
- **assistant:** Good morning! I'm the assistant for Brennan Auto Care. East Main is open Saturday mornings, 8:00 a.m. to 1:00 p.m.; Bonny Oaks and Charlotte Pike are weekdays only. Want me to pass this to the service desk so they can set up a time?
- **customer:** east main is fine
- **assistant:** What's your name and the best number to reach you?
- **customer:** Cody, 4235554614, text is better
- **assistant:** Thank you, Cody. Your request is with the team now, and somebody will get back to you as soon as possible.
- *hand-over (scheduling), the bot's private note: Booking request in the customer's words: 'can i come saturday morning'. I said the desk confirms the time.*
- **customer:** ok thanks have a good night
- *draft, discarded: Thank you, Cody. Take care.*
- **Brenda (29):** Hello Cody, this is Brenda at East Main. Thank you for writing in, and I'm sorry to keep you waiting. I can take it Tuesday at 7:30, or Friday at 2:15. Which suits you better? / - Brenda
- **customer:** 7:30 works
- *draft, sent as is: Thank you, Cody. See you Tuesday at 7:30 at 2106 East Main St.*
- **Brenda (29):** Thank you, Cody. See you Tuesday at 7:30 at 2106 East Main St.
- — handed over

### 53. hours · web chat · `hours.web.7` · alone

- **customer:** open sunday?
- **assistant:** Hello! I'm the Brennan Auto Care assistant. We're closed that day. When a holiday falls on a weekend we close on the nearest weekday, and the key drop stays open.
- **customer:** appreciate yall
- — alone

### 54. status · web chat · `status.web.4` · handed over · slot 16 Angie Holloway (Bonny Oaks) · unclear u13, after one

- **customer:** is it ready and whats the total
- **assistant:** Hi! I'm the assistant for Brennan Auto Care. Which car is this about?
- **customer:** just the express 2500, the other one is next week
- **assistant:** Thank you, the express 2500 then. I can't see the shop's repair orders from here, so I don't have the status of your car. I'll pass your question to the service desk so they can answer you. Who should they ask for, and what's the best number?
- **customer:** 423-555-6177 thats my cell
- **assistant:** Thank you. I've sent your request to the service desk; somebody will get back to you as soon as possible.
- *hand-over (escalation), the bot's private note: Asks about a car at the shop: 'is it ready and whats the total'. I can't see the repair order, so I gave no status and no time.*
- *draft, discarded: You're welcome! Somebody from the shop will be in touch.*
- **Angie (16):** Hi Kayla, this is Angie on Bonny Oaks. I read your message, Kayla, and I can help. Good afternoon, Kayla! The Express 2500 is ready. Your total is $54.57, and we're here until 5:30 p.m. / Angie
- **customer:** omw
- — handed over

### 55. status · web chat · `status.web.6` · abandoned · after hours

- **customer:** any update on the sonata
- **assistant:** Hello, this is Brennan Auto Care's assistant. We're closed for the night and open again at 7:30 tomorrow; I can answer what I can until then. I'm not able to look up repair orders. I'll get your question to an advisor at the shop, who can check on the Sonata. What's your name and the best number to reach you?
- — abandoned

### 56. hours · web chat · `hours.web.8` · alone

- **customer:** do yall service hybrids
- **customer:** just wondering
- **assistant:** Hi there, this is Brennan Auto Care's assistant. For hybrids we do the ordinary service, oil, brakes, tires, suspension and the small battery, and that's at East Main only. We don't repair the high-voltage battery, the inverter or the drive motor.
- **customer:** ok good to know
- — alone

### 57. price · web chat · `price.web.3` · handed over · slot 7 Caleb Sutton (East Main)

- **customer:** Requesting a price for struts on a chevrolet malibu. Parts and labor separate if possible.
- **assistant:** Hello! I'm the Brennan Auto Care assistant. That one depends on the car, so I won't guess. The shop starts with the steering and suspension inspection at $49.95, then gives you a written estimate with each job priced separately.
- **customer:** how soon can they look at it
- **assistant:** I'm not able to book appointments, but I can send your request to an advisor, who will confirm a time with you. What's the best number for the desk to reach you? Which shop is easier for you: East Main, Bonny Oaks, or Charlotte Pike in Nashville?
- **customer:** lamar hollis. 706.555.9678. call after lunch if you can
- **customer:** downtown one i guess
- **assistant:** Got it, Lamar. It's with the shop now; somebody will get back to you as soon as possible.
- *hand-over (scheduling), the bot's private note: 'Requesting a price for struts on a chevrolet malibu. Parts and labor separate if possible.'. I quoted nothing beyond the public pages; wants a person to price it.*
- **customer:** many thanks
- *draft, discarded: You're welcome, Lamar. Have a good night!*
- **Caleb (7):** Hi Lamar, Caleb at East Main. Yes sir, I can help with that! I think we have 9:00 open Friday, does that work?
- **customer:** 9:00 is perfect thank you
- *draft, sent as is: Thank you, Lamar. Friday at 9:00 works. See you then!*
- **Caleb (7):** Thank you, Lamar. Friday at 9:00 works. See you then!
- (label_added price)
- — handed over

### 58. price · web chat · `price.web.1` · alone · after hours

- **customer:** hey quick question whats a brake fluid flush run on a corolla and do i need an appointment
- **assistant:** Hi! I'm the assistant for Brennan Auto Care. The shops are closed right now and open at 7:30 tomorrow, but I can help in the meantime. Our brake fluid flush is $151.00 before tax, for a car or small crossover. Would you like me to ask the shop to set up a time?
- — alone

### 59. price · web chat · `price.web.5` · alone

- **customer:** whats yalls price on a battery i got a quote somewhere else and want to compare
- **assistant:** Good morning! I'm the assistant for Brennan Auto Care. It ranges from $198.28 to $334.95 for replacement, depending on the brand and grade. An advisor can price yours exactly. Our listed prices are for cars and small crossovers; a truck like yours can come out higher. An advisor can give you the figure for it.
- **customer:** dang ok. thanks
- **customer:** ok thank you sir
- — alone

### 60. found_work · web chat · `found_work.web.4` · handed over · slot 6 Maya Torres (East Main)

- **customer:** what is this charge for [photo: invoice-line-circled]
- **customer:** just saw the text
- **assistant:** Hi there, this is Brennan Auto Care's assistant. Thanks for the photo. I can't see your estimate in the shop's system, so I'll ask an advisor to go over that line with you. What's the best number to reach you?
- **customer:** My name is Scotty Hensley and my number is 4235555514.
- **assistant:** Got it, Scotty. It's with the shop now; somebody will get back to you as soon as possible.
- *hand-over (escalation), the bot's private note: Answer to the estimate, in the customer's words: 'what is this charge for'. I changed nothing and approved nothing.*
- *draft, discarded: Thank you, Scotty. Take care.*
- **Maya (6):** Hi Scotty, this is Maya with Brennan Auto Care. I saw your request come in and wanted to get right back to you. Good news and bad news, Scotty. The alternator is done, but the alternator is putting out low voltage. I'd do it soon: $597.82. Should I go ahead?
- **customer:** can i do half now and half next time
- *draft, sent as is: I'll put the total together for you, Scotty, with tax and shop supplies, and send it right over.*
- **Maya (6):** I'll put the total together for you, Scotty, with tax and shop supplies, and send it right over.
- **Maya (6):** Great, thank you! Terry is starting on it now.
- — handed over

## Duplicate messages

326 public messages; 6 are exact repeats of an earlier one (1.8%); 11 messages share their text with another (3.4%).

- 3 x `omw`
- 2 x `ready? and how much do i owe`
- 2 x `the car`
- 2 x `ok good to know`
- 2 x `thanks a bunch`
