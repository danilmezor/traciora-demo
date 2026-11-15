# Fictional phone numbers and e-mail addresses (seed v1, draft)

Goal: no number or address the seed generates can reach a real subscriber. Researched 2026-11-13. "Read" means the page was opened (through a fetch tool that summarises, so clause wording is to be re-read on the primary page before approval). "Not verified" means general knowledge or a search snippet. "Proposal" is this file's design, not a fact.

## 1. United States (Tennessee)

### What the numbering plan says

| Fact | Status | Source |
|---|---|---|
| 555-0100 to 555-0199 "will remain reserved for entertainment/advertising" as "fictitious, non-working numbers" | read | NANPA, 555 line numbers: https://nanpa.com/numbering/555-line-numbers |
| "All 555 line numbers have been returned to the inventory of NANPA resources." Still in use: 555-1212 (directory assistance) and 555-4334 (national use, assigned). | read | same page |
| The industry committee (INC) decided this in May 2016, the FCC approved in September 2016, the 555 assignment guidelines (ATIS-0300048) were sunset; reference document ATIS-0300115. "The future of a 555 resource will be determined if a need for the resource is identified and agreed to by INC." | read | same page |
| Wikipedia words it differently: other 555 numbers "can now be assigned by telephone companies". NANPA's own page says they are back in inventory with no assignment process. The NANPA page is the authority. | read, sources disagree | https://en.wikipedia.org/wiki/555_(North_American_Numbering_Plan) |
| The 555 exchange is not reserved in toll-free area codes (800, 888 and so on). | read | same Wikipedia page |
| Chattanooga is area code 423. Its overlay 729 went into service on 2025-09-05 and its exchanges are given out only when 423 is exhausted. | read (search summary of NANPA planning letters PL-619, PL-629 and the Tennessee commission's docket) | https://nanpa.com/sites/default/files/planning_letters/PL-629.pdf |
| Nashville is 615 with overlay 629. Neighbours a Chattanooga shop really sees: 706 and 762 (north-west Georgia), 256 and 938 (north Alabama), 865 (Knoxville), 931 (middle Tennessee). | not verified | general knowledge, `demo-seed-research/addresses.md` |
| Exchanges 958 and 959 are plant test codes and N11 cannot be an exchange. | not verified | general knowledge; not used below |
| Whether a carrier routes a call to an unassigned 555 number, and whether the product's phone validation accepts 555 numbers. | not verified | to be tested by the seeder's implementer |

### Scheme (proposal)

Two tiers, both in the 555 exchange, so every number is recognisably fictional to an American and none is assigned to anyone.

| Tier | Numbers | Per area code | Guarantee | Used for |
|---|---|---:|---|---|
| A | NPA-555-0100 to NPA-555-0199 | 100 | reserved for fiction by NANPA | the shops' own lines; every person, company and vendor a story names; anything that appears in sales material |
| B | NPA-555-0200 to NPA-555-9999, without 1212 and 4334 | 9,798 | unassigned today (returned to inventory in 2016), not reserved | background customers and callers |

Never used: 555-0000 to 555-0099, 555-1212, 555-4334, any toll-free area code.

Capacity of tier B and the proposed mix of area codes by shop (the mix is class X, designed):

| Area code | Tier B numbers | Share at `main` and `east` | Share at `west` |
|---|---:|---:|---:|
| 423 | 9,798 | 70 % | 3 % |
| 706 | 9,798 | 12 % | |
| 762 | 9,798 | 3 % | |
| 256 | 9,798 | 3 % | |
| 865 | 9,798 | 3 % | 2 % |
| 931 | 9,798 | 3 % | 8 % |
| 615 | 9,798 | 3 % | 62 % |
| 629 | 9,798 | | 15 % |
| 270 (Kentucky) | 9,798 | | 3 % |
| 901 | 9,798 | | 2 % |
| other real area codes (people who moved and kept their number), at most 200 tier-B numbers per code | | 3 % | 5 % |
| Total | 97,980 and more | | |

The ceiling is 423: at a 70 % share the two home shops can hold 13,997 distinct numbers. If the full-density seed needs more, lower the 423 share (706 can honestly carry more: a quarter of Chattanooga's metro area lives in Georgia) rather than leave the 555 exchange. Area code 729 is not used: it has almost no subscribers yet.

Formats: stored as E.164, `+14235550142`; shown as `(423) 555-0142`.

The shops' own numbers (tier A):

| Site | Public line | Rings |
|---|---|---|
| `main` | (423) 555-0142 | group 100, then 101, 102, 103, 105 |
| `east` | (423) 555-0167 | group 200, then 201, 202 |
| `west` | (615) 555-0119 | group 300, then 302, 303, 301 (304 was the fired advisor's desk and is retired) |
| head office | no public line; 401 and 402 forward to mobiles | |

Tier A numbers already given to named companies and people are in `accounts.json`, `vendors.json` and `named_customers.json`; the seeder must not draw them again.

## 2. Russia (Ульяновск, Казань)

### What the numbering plan says

| Fact | Status | Source |
|---|---|---|
| The plan in force is приказ Минцифры России от 31.01.2022 № 75 (ред. от 17.06.2025), in force since 2022-09-01; it replaced приказ Минкомсвязи № 205 of 2017. | read | https://legalacts.ru/doc/prikaz-mintsifry-rossii-ot-31012022-n-75-ob-utverzhdenii/ |
| The plan has no range for fiction, film or testing. | read (nothing of the kind in № 75 or in № 205) | same; https://legalacts.ru/doc/prikaz-minkomsvjazi-rossii-ot-25042017-n-205-ob-utverzhdenii/ |
| DEF codes in the plan's reserve (приложение № 7, пункт 6): 907, 935, 943, 944, 945, 946, 947, 948, 972, 973, 974, 975, 976. Thirteen codes. | read | № 75 |
| DEF codes given to mobile networks (приложение № 8): 900 to 906, 908 to 934, 936 to 939, 949 to 953, 958 to 969, 977 to 996, 999; mobile radio 955, 956, 957, 997; satellite 954; ЭРА-ГЛОНАСС 941, 942. So 907 and 935 sit between working codes and are in none of these lists. | read | № 75 |
| 907 and 935 were also in the reserve list of the 2017 plan, so they have been unused through two editions. | read | № 205, приложение 6 |
| A zone number's first digit "не должен быть равен «0» и «1»" (пункт 13); numbers in a geographic zone begin with 2 to 7 and 9, and with 2 to 9 after stage I (пункт 67). So a city number that begins with 0 or 1 cannot exist. | read | № 75 |
| Казань has seven-digit numbers (since 2005-09-17), code 843. | read | https://ru.wikipedia.org/wiki/Телефонный_план_нумерации_России |
| Ульяновск: code 8422 with six-digit numbers. | not verified | general knowledge, `addresses.md` |
| The registry of allocated ranges (the files DEF-9xx.csv and ABC-8xx.csv on opendata.digital.gov.ru) was not read: the site's certificate chains to a root this Mac does not trust, and the download was not forced. So "no operator holds a number in 907 or 935" rests on the plan, not on the registry. | not verified | to be checked once by the controller |
| A reserve code can be opened by a later order (949 and 959 were reserve in 2017 and are mobile now). | read | compare № 205 with № 75 |

### Scheme (proposal)

| Kind | Numbers | Capacity | Why it cannot be real | How it reads |
|---|---|---:|---|---|
| Mobile | +7 907 XXX-XX-XX, then +7 935 XXX-XX-XX | 10,000,000 each | the whole code is in the plan's reserve; no operator can hold a number in it without a new order of the ministry | like any mobile number; nobody knows the list of codes by heart |
| City number, Ульяновск | +7 (8422) 1X-XX-XX; overflow 0X-XX-XX | 100,000 + 100,000 | the plan forbids 0 and 1 as the first digit | slightly unusual to a local eye, as 555 is to an American |
| City number, Казань | +7 (843) 1XX-XX-XX; overflow 0XX-XX-XX | 1,000,000 + 1,000,000 | same | same |

Rules:
- Private customers get a mobile only, as in real shop data. City numbers go to the shops, company accounts, vendors and small businesses, beside a mobile for each contact.
- Story-named people use 907; background numbers draw from 907 and 935 alike. A check before every build: 907 and 935 still appear in the reserve list of the current plan.
- No patterns a person would choose (no 907 000-00-01): numbers are drawn at random inside the code.
- Formats: stored as E.164, `+79072143658`; shown as `+7 907 214-36-58`, city numbers as `+7 (8422) 10-40-40` and `+7 (843) 100-40-30`.
- The city numbers are structurally impossible, so a strict validator may refuse them; the mobiles pass any format check. Whether the product's validation accepts both is to be tested by the seeder's implementer.

The shops' own numbers:

| Site | Public line | Rings |
|---|---|---|
| `main` | +7 (8422) 10-40-40 | group 100, then 101, 102, 103, 105 |
| `east` | +7 (8422) 10-40-41 | group 200, then 201, 202 |
| `west` | +7 (843) 100-40-30 | group 300, then 302, 303, 301 (304 was the fired advisor's desk and is retired) |
| head office | no public line; 401 and 402 forward to mobiles | |

## 3. E-mail addresses

`.example` is a top-level domain reserved for documentation (RFC 2606, RFC 6761; not re-read in this pass), so no address under it can be delivered.

| Who | Pattern | Example |
|---|---|---|
| Staff, English | first initial + surname @brennanautocare.example | mtorres@brennanautocare.example |
| Staff, Russian | first initial + surname in Latin letters @ermak-service.example | akhasanova@ermak-service.example |
| Shop mailboxes | main@, east@, west@, accounting@ on the same domains | west@brennanautocare.example |
| Company accounts and vendors | a short Latin form of the company name + .example | dispatch@nickajackdelivery.example |
| Private customers, English | name@inbox.example or name@postmail.example | rdunlap@inbox.example |
| Private customers, Russian | name@pochta.example or name@yapochta.example | o.timofeeva@pochta.example |

Usernames are in `cast.json`. No real mail provider's domain appears anywhere in the seed.
