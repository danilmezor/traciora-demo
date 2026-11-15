# Shop addresses research (partial: no candidate passed every test)

Status: Overpass API timed out or stalled for most of the run, so the neighbour checks needed to clear an address could not be finished. No address below is cleared. Nothing was geocoded for Ulyanovsk, Kazan or Nashville.

## Checked, all rejected (Chattanooga)
Geocoder = Nominatim search, generic client name. Neighbours = Overpass tags within 150-200 m.

| Address | lat, lon | Nominatim | Finding | Verdict |
|---|---|---|---|---|
| 1503 Dodds Avenue, Chattanooga, TN 37404 (Ridgedale) | 35.02178, -85.27031 | way 761106015, building=commercial, house number match | web search: AT&T service centre at this address | rejected: well-known named business |
| 2106 East Main Street, Chattanooga, TN 37404 | 35.02475, -85.27694 | way 761115875, building | ex-convenience store for sale (C-2); OSM neighbours include a tyre shop (shop=car_repair) and an industrial-supply shop | rejected: automotive business adjacent |
| 6025 East Brainerd Road, Chattanooga, TN 37421 | 35.01748, -85.20453 | way 51792702, building=commercial | multi-tenant strip (restaurants, nails, furniture, tobacco), a car wash across the road | rejected: named tenants, car wash near |
| 4140 Jersey Pike, Chattanooga, TN 37421 | 35.06257, -85.19484 | way 302175452, building=commercial | dealerships tagged within 200 m (VW, Mazda) | rejected: automotive neighbours |
| 344 Dodds Avenue, 37404 | 35.03101, -85.26331 | not geocoded | beside a school and funeral home | rejected: not a repair corridor |
| 707 South Germantown Road, 37412 | 35.01202, -85.25354 | way 209373346, building=yes | city is East Ridge, not Chattanooga; use unchecked | not used |

## Time zones (from tz database facts)
- Chattanooga: America/New_York (Eastern, east of the Tennessee split).
- Nashville: America/Chicago (Central).
- Ulyanovsk: Europe/Ulyanovsk, fixed UTC+4, no DST (IANA europe file, zone covers RU-ULY; verified by web search).
- Kazan: Europe/Moscow, UTC+3 (from tz knowledge; not searched).

## Phone facts (not web-verified except where noted)
- Chattanooga 423; Nashville 615 and 629. US fiction range: 555-0100 to 555-0199 (NANP reserved).
- Ulyanovsk +7 8422 (city code 8422 national, 422 after +7); Kazan +7 843. Mobile numbers +7 9xx.
- Russia has no reserved fictional range that I know of; not verified. Proposal only: fictional landlines as +7 8422 000-xxxx and +7 843 000-xxxx, which no real exchange uses.

## Method notes
- Overpass: simple union queries (shop, amenity, craft, office within r metres) work when the server answers; regex key filters time out. Use curl for transport, Python urllib fails TLS on this Mac.
- OSM coverage of commercial buildings with house numbers is sparse in Chattanooga; expect to hand-pick from a map or listing site and then geocode.

## Second try

Rule used: the number itself must not be an automotive or widely known named business; neighbours do not matter. Geocoder: Nominatim search (jsonv2, addressdetails, countrycodes), curl, generic client name, 1 request per second, no Overpass. Time zones confirmed by timeapi.io coordinate lookup. Web search tool is weak on Russian address directories, so "nothing found at the number" means no automotive or named business surfaced, not that 2GIS was read.

### Chosen addresses

| Site | Address (as locals write it) | lat, lon | Nominatim object | Time zone | At that number (web) | District |
|---|---|---|---|---|---|---|
| Chattanooga main | 2106 East Main Street, Chattanooga, TN 37404 | 35.0247317, -85.2769473 | way 761115875, building=yes | America/New_York | Hamilton County assessor card (parcel 156B G 002) and LoopNet record, 2017 for-sale listing; no business listed, no automotive | Ridgedale / Highland Park |
| Chattanooga east | 4140 Jersey Pike, Chattanooga, TN 37421 | 35.0625706, -85.1948441 | way 302175452, building=commercial | America/New_York | no listing at this number (4120 is an office building on the same pike); no automotive business found | East Brainerd |
| Nashville west | 6399 Charlotte Pike, Nashville, TN 37209 | 36.1441360, -86.8729220 | place=house on way 19483391 (address interpolation on the road, not a building polygon) | America/Chicago | Showcase lists a freestanding commercial property for sale at 6399; no business named | Whitebridge / West Nashville |
| Nashville west spare | 6301 Charlotte Pike, Nashville, TN 37209 | 36.1454086, -86.8714321 | place=house, same way (interpolated) | America/Chicago | no listing found; 6300 block has restaurants | West Nashville |
| Ulyanovsk main | 432045, г. Ульяновск, Московское шоссе, 40 (Moskovskoye shosse 40) | 54.3029561, 48.2861459 | way 347278103, building=yes, house number 40 | Europe/Ulyanovsk | no organisation found at 40 | Засвияжский район |
| Ulyanovsk main spare | 432045, г. Ульяновск, Московское шоссе, 30 | 54.3003086, 48.2844581 | way 336344003, building=yes | Europe/Ulyanovsk | not searched | Засвияжский район |
| Ulyanovsk east | 432059, г. Ульяновск, 10-й Инженерный проезд, 30 (10-y Inzhenerny proyezd 30) | 54.3672744, 48.5889458 | way 751865374, building=yes | Europe/Ulyanovsk | no organisation found at 30 | Заволжский район (Новый Город) |
| Ulyanovsk east spare | 433430, г. Ульяновск, 46-й Инженерный проезд, 10 | 54.3663925, 48.6913168 | way 380200216, building=industrial | Europe/Ulyanovsk | no organisation found at 10; ZIP 433430 as Nominatim gives it | Заволжский район |
| Kazan west | 420054, г. Казань, улица Техническая, 30 (Tekhnicheskaya ulitsa 30) | 55.7280123, 49.1345304 | way 737112644, building=yes | Europe/Moscow | no organisation found at 30; an auto service further down the street (neighbour, fine) | Борисково, Приволжский район (industrial belt) |
| Kazan west spare | 420054, г. Казань, улица Техническая, 23 | 55.7435921, 49.1295812 | way 96415206, building=yes | Europe/Moscow | only a registered office at 23А | Воскресенское |

Query pattern: https://nominatim.openstreetmap.org/search?q=<number>+Charlotte+Pike,+Nashville&format=jsonv2&addressdetails=1&countrycodes=us ; Russian: q=Ульяновск,+Московское+шоссе,+40 (and Казань,+улица+Техническая,+30; Ульяновск,+Инженерный+проезд,+30) with countrycodes=ru, accept-language=ru.

### Not verified
- Nashville: OSM has almost no building polygons on Charlotte, Nolensville and Murfreesboro Pikes; every hit was an interpolated house number on the road (or a named amenity). 6399 is therefore a house-number object, not a building. Dickerson Pike numbers also interpolate.
- Ulyanovsk and Kazan: no 2GIS or Yandex card was read; absence of a business was inferred from search results only. Ulyanovsk "Инженерный проезд" is numbered (8-й, 10-й, 42-й, 46-й); the east pick is on 10-й.
- ZIPs for Ulyanovsk and Kazan are Nominatim's postcode values.

## Second Chattanooga shop, third try

Street chosen: Bonny Oaks Drive (staff say "the Bonny Oaks shop"). Geocoder: Nominatim search (jsonv2, addressdetails, countrycodes=us), curl, generic client name, 1 request per second, no Overpass. Distances are great-circle from 2106 East Main Street (35.0247317, -85.2769473).

| | Candidate 1 (best) | Candidate 2 |
|---|---|---|
| Address | 6340 Bonny Oaks Drive, Chattanooga, TN 37416 | 5513 Bonny Oaks Drive, Chattanooga, TN 37416 |
| lat, lon | 35.0743712, -85.1718599 | 35.0739872, -85.1825860 |
| Nominatim object | way 143263710, place=house (interpolated house number on the road, not a building polygon) | same way 143263710, place=house (interpolated) |
| Query URL | https://nominatim.openstreetmap.org/search?q=6340+Bonny+Oaks+Drive,+Chattanooga&format=jsonv2&addressdetails=1&countrycodes=us | https://nominatim.openstreetmap.org/search?q=5513+Bonny+Oaks+Drive,+Chattanooga&format=jsonv2&addressdetails=1&countrycodes=us |
| Distance to 2106 East Main | 11.0 km | 10.2 km |
| Time zone | America/New_York | America/New_York |
| Staff short name | the Bonny Oaks shop | the Bonny Oaks shop |

### What the web searches returned
- 6340: two searches of the exact string. Only hit is the broker listing (Crexi sale and lease pages, LoopNet 38327325): a 14,440 sq ft one-story flex building, 1.10 acres, zoned I-H, showroom and four drive-in doors, at a traffic light, listed for sale and lease, no tenant named. No business directory (D&B, NAICS list, MapQuest) lists any company at that number. Fits a repair shop.
- 5513: three searches. Nothing at that number in any directory or listing; assessor and Redfin pages only show other numbers.
- Neighbours on the road: a general auto repair shop at 6413, a restaurant, a lender and a homebuilder, a lot for sale at 6391, the flex building at 6340.

### Not verified
- Neither number is a building polygon; both are interpolated, so "a real building at that number" is inferred from the broker listing only for 6340.
- 5513: nothing confirms it is commercial or even a parcel; the Hamilton County assessor card was not read (site returned an error to search).
- 6340 is a live sale listing; the occupant history was not checked. A business could have been there before and be missing from the indexed directories.
- Searches are a general web search, not direct directory queries.
- Rejected: 1801 Gunbarrel Road (mapped building, but inside a shopping centre, beside a fast-food restaurant).
