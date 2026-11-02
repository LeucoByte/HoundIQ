# GBGB scraper data

## 1. Data Source
The **Greyhound Board of Great Britain (GBGB)** is the regulatory body responsible for licensed greyhound racing in Great Britain.

HoundIQ retrieves historical racing information from the GBGB website's API:

`https://api.gbgb.org.uk/api`

The scraper uses three endpoints:

| Dataset | Endpoint | Purpose |
|---|---|---|
| Races | `GET /results?page={page}&itemsPerPage=100` | Retrieves paginated race-result records across GBGB. |
| Details | `GET /results/meeting/{meetingId}?meeting={meetingId}` | Retrieves the races and participant information belonging to a meeting. |
| Winners | `GET /results/dog/{dogId}?page={page}&itemsPerPage=100&race_type=race` | Retrieves the historical race records associated with an individual greyhound. |

### Extraction process
1. Retrieve all available records from `/results`.
2. Collect the unique `meetingId` and `dogId` values.
3. Retrieve the details of each meeting.
4. Retrieve the paginated racing history of each identified greyhound.

The endpoint descriptions above reflect the current scraper implementation, not a formally guaranteed API contract.

## 2. Dataset Overview
The three datasets provide different views of the same racing activity.

| Dataset | Structure | Represents |
|---|---|---|
| `Details` | Meeting → Races → Traps | A complete meeting, its races and the trap entries associated with each race. |
| `Races` | Flat collection of records | Individual greyhound race-result records retrieved through the global results endpoint. |
| `Winners` | Greyhound → Items | The historical race records associated with an individual greyhound. |

**Naming note:** `Winners` is the original scraper directory name. It does not contain exclusively winning records: it contains the racing history of each greyhound, including wins, second places and other finishing positions.

## 3. Data Structures and Field Definitions

### 3.1. Details
The `Details` dataset represents a meeting and its nested racing information:

`Meeting → Races → Traps`

#### Meeting

| Field | Description | Example |
|---|---|---|
| `meetingDate` | Date on which the meeting takes place. | `04/10/2026` |
| `meetingId` | GBGB identifier of the meeting. | `453183` |
| `trackName` | Name of the racecourse hosting the meeting. | `Yarmouth` |
| `races` | Collection of races belonging to the meeting. | Array of race objects |

#### Race

| Field | Description | Example |
|---|---|---|
| `raceTime` | Scheduled time associated with the race. | `11:01:00` |
| `raceDate` | Date associated with the race. | `04/10/2026` |
| `raceId` | GBGB identifier of the race. | `1248432` |
| `raceTitle` | Advertised race title, when available. | `null` |
| `raceNumber` | Race number within the meeting. | `"1"` |
| `raceType` | Race format, such as Flat or Hurdles. | `Flat` |
| `raceHandicap` | Indicates whether the race is a handicap race. | `false` |
| `raceClass` | Classification or grade assigned to the race. | `A6` |
| `raceDistance` | Distance of the race, apparently expressed in metres. | `462.0` |
| `racePrizes` | Prize information associated with the race. | `1st £115 \| Others £50 Race Total £315` |
| `raceGoing` | Going allowance associated with the track conditions, expressed as a signed value relative to normal. The examples suggest hundredths of a second. | `"0"` |
| `raceForecast` | Forecast result and associated displayed return. The exact betting/dividend convention should be confirmed against the source. | `(6-4) £20.58` |
| `raceTricast` | Tricast result and associated displayed return. The exact betting/dividend convention should be confirmed against the source. | `(6-4-1) £0.00` |
| `traps` | Collection of trap entries for the race. Each entry contains a trap number and, when available, greyhound and result information. | Array of trap objects |

#### Trap / Race Participation

Each entry in `traps` represents a starting trap in the race. It may contain only the trap number, without greyhound details, as observed in the example.

| Field | Description | Example |
|---|---|---|
| `trapNumber` | Starting trap allocated to the greyhound. | `"6"` |
| `trapHandicap` | Handicap allotment associated with the trap entry. `null` when no value is recorded. | `null` |
| `dogId` | GBGB identifier of the participating greyhound. | `652291` |
| `dogName` | Greyhound's registered name. | `Good Anna` |
| `dogSire` | Greyhound's sire (father). | `Ballyhimikin Jet` |
| `dogDam` | Greyhound's dam (mother). | `Epic Majesty` |
| `dogOrigin` | Origin information for the greyhound, apparently represented by a country code. | `Ir` |
| `dogBorn` | Greyhound's birth information, represented as month and year. | `Aug-2023` |
| `dogColour` | Greyhound's coat-colour code. | `bkw` |
| `dogSex` | Greyhound's sex code. Observed values include `b` (bitch) and `d` (dog). | `b` |
| `dogSeason` | Date associated with the bitch's season or reproductive history. Its exact API semantics should be verified. | `14.Au.25` |
| `trainerName` | Name of the greyhound's trainer. | `C R Morris` |
| `ownerName` | Name or names of the greyhound's owner(s). Multiple owners may appear in the same string. | `Mrs L Rackstraw` |
| `SP` | Starting Price: the recorded fractional betting price. A suffix such as `F` indicates favourite. | `11/8F` |
| `resultPosition` | Official finishing position of the greyhound. | `1` |
| `resultMarketPos` | Position of the greyhound in the betting market. In the example, `1` corresponds to the favourite. | `5` |
| `resultMarketCnt` | Additional market-related numeric field. Its exact meaning has not yet been established. | `1` |
| `resultPriceNumerator` | Numerator of the fractional price recorded for the greyhound. | `11` |
| `resultPriceDenominator` | Denominator of the fractional price recorded for the greyhound. | `8` |
| `resultBtnDistance` | Distance by which the greyhound finished behind the winner. Recorded as a fraction or mixed number; winners may have an empty value. | `1 1/2` |
| `resultSectionalTime` | Sectional time recorded for the greyhound. The precise timing point should be confirmed. | `05.39` |
| `resultComment` | Descriptive race comment about the greyhound's performance, position or incidents during the race. | `W,ALd,Crd4` |
| `resultRunTime` | Recorded running time for the greyhound. | `28.63` |
| `resultDogWeight` | Greyhound's recorded race weight. The unit and precise weighing convention should be confirmed. | `25.8` |
| `resultAdjustedTime` | Running time adjusted for the race's going allowance, according to the observed examples. | `28.63` |

### 3.2. Races
The `Races` endpoint returns a flat collection of individual greyhound race-result records.

Each record combines information about the meeting, race and participating greyhound. It is therefore not a complete race object containing all its participants.

| Field | Description | Example |
|---|---|---|
| `resultPosition` | Greyhound's official finishing position. | `1` |
| `trapNumber` | Starting trap allocated to the greyhound. | `"4"` |
| `raceTime` | Scheduled time associated with the race. | `15:38:00` |
| `raceDate` | Date associated with the race. | `02/11/2026` |
| `raceId` | GBGB identifier of the race. | `1255588` |
| `raceNumber` | Race number within the meeting. | `"5"` |
| `raceClass` | Race classification or grade. | `A7` |
| `raceDistance` | Race distance, apparently expressed in metres. | `480.0` |
| `meetingId` | Identifier of the meeting to which the race belongs. | `454567` |
| `trackName` | Name of the racecourse. | `Monmore` |
| `dogId` | GBGB identifier of the participating greyhound. | `657804` |
| `dogName` | Greyhound's registered name. | `Swift Jolly` |
| `dogSire` | Greyhound's sire (father). | `Droopys Got It` |
| `dogDam` | Greyhound's dam (mother). | `Swift Bach` |
| `trainerName` | Name of the greyhound's trainer, when available. | `P I Cowdrill` |
| `ownerName` | Name or names of the greyhound's owner(s), when available. | `Mrs S J James,mr L C G Preece` |

### 3.3. Winners
The `Winners` endpoint retrieves the historical race records associated with one greyhound.

#### Top-level fields

| Field | Description | Example |
|---|---|---|
| `dogId` | GBGB identifier of the greyhound whose history is being retrieved. | `51937` |
| `totalRaces` | Number of records collected by the scraper. It is calculated locally as `len(dog_races)`, not copied from the API's metadata. | `8` |
| `items` | Collection of historical race records associated with the greyhound. | Array of race objects |

#### Historical race records (`items`)

| Field | Description | Example |
|---|---|---|
| `SP` | Starting Price recorded for the greyhound. | `7/4F` |
| `resultPosition` | Greyhound's finishing position. | `3` |
| `resultBtnDistance` | Distance by which the greyhound finished behind the winner. | `3/4` |
| `resultSectionalTime` | Recorded sectional time. | `04.28` |
| `resultComment` | Descriptive comment about the greyhound's performance. | `Crd 1/4` |
| `resultRunTime` | Recorded running time of the greyhound. | `29.53` |
| `resultDogWeight` | Recorded race weight of the greyhound. | `29.1` |
| `winnerOr2ndName` | Name of the winner or runner-up associated with the record. The observed examples suggest it identifies the other greyhound occupying one of the first two positions. | `Chart Topper` |
| `winnerOr2ndId` | GBGB identifier of the greyhound referenced by `winnerOr2ndName`. | `334258` |
| `resultAdjustedTime` | Running time adjusted for the going allowance, according to the observed examples. | `29.43` |
| `trapNumber` | Starting trap allocated to the greyhound. | `"3"` |
| `raceTime` | Scheduled time associated with the race. | `14:29:00` |
| `raceDate` | Date associated with the race. | `24/05/2026` |
| `raceId` | GBGB identifier of the race. | `1218783` |
| `raceType` | Type of race, such as Flat or Hurdles. | `Flat` |
| `raceClass` | Race classification or grade. | `A1` |
| `raceDistance` | Race distance, apparently expressed in metres. | `500.0` |
| `raceGoing` | Signed going allowance relative to normal. Observed values suggest hundredths of a second. | `-10` |
| `raceWinTime` | Winning running time recorded for the race. | `29.20` |
| `meetingId` | Identifier of the meeting. | `447505` |
| `trackName` | Name of the racecourse. | `Sheffield` |

## 4. Data Interpretation and Observations

### 4.1. Running Times and Going Allowances
GBGB Rule 151 states that allowances for track-going conditions are expressed mathematically as plus or minus from normal.

The supplied examples show a consistent relationship between `raceGoing`, `resultRunTime` and `resultAdjustedTime`:

| `resultRunTime` | `raceGoing` | `resultAdjustedTime` |
|---:|---:|---:|
| `28.43` | `-30` | `28.13` |
| `29.53` | `-10` | `29.43` |
| `29.00` | `20` | `29.20` |

These examples are consistent with:

`resultAdjustedTime = resultRunTime + (raceGoing / 100)`

This interpretation should be verified against additional records before being treated as a universal rule.

`raceWinTime` represents the winning time associated with the race, whereas `resultRunTime` and `resultAdjustedTime` describe the greyhound's own performance.

### 4.2. Missing and Optional Values
The examples demonstrate that fields do not always contain values.

Three distinct cases must be preserved:
- A field can be absent from an object.
- A field can explicitly contain `null`.
- A field can contain an empty string (`""`).

These cases are not necessarily equivalent.

For example, a trap entry may contain only `trapNumber`, while a participating greyhound's entry contains additional identity and result information.

Some fields are also conditional. For example, `winnerOr2ndId` and `winnerOr2ndName` are not present in every historical race record.

### 4.3. Record Counts
The `totalRaces` field in the `Winners` files is calculated by the scraper using the number of records successfully collected.

It should not be interpreted as an independently verified total supplied by GBGB. If an API request fails during pagination, the collected history may be incomplete.

### 4.4. Structure Comparison
A comparison of the observed field structures from September and November 2026 found no structural differences in the three datasets.

This confirms that the observed field structures remained consistent during that comparison, but does not establish that every historical record was retrieved completely or that every field has an invariant meaning.

## 5. Official References
- [GBGB – About Us](https://www.gbgb.org.uk/about/about-us/)
- [GBGB Rule 33 – Greyhound registration and markings](https://rules.gbgb.org.uk/section-4-greyhounds/rule-33-greyhound-registration-and-markings/)
- [GBGB Rule 57 – Reporting of season details](https://rules.gbgb.org.uk/section-4-greyhounds/rule-57-reporting-of-season-details-spaying-whelping-litter/)
- [GBGB Rule 64 – Categories and types of Race](https://rules.gbgb.org.uk/section-5-organisation-of-races-and-trials/rule-64-categories-and-types-of-race/)
- [GBGB Rule 108 – Racecard](https://rules.gbgb.org.uk/section-7-trials-meetings-and-race-meetings/rule-108-racecard/)
- [GBGB Rule 138 – Timing, Timekeeper](https://rules.gbgb.org.uk/section-7-trials-meetings-and-race-meetings/rule-138-timing-timekeeper/)
- [GBGB Rule 139 – Beaten distance, Calculated Time](https://rules.gbgb.org.uk/section-7-trials-meetings-and-race-meetings/rule-139-beaten-distance-calculated-time/)
- [GBGB Rule 140 – Order of Finish, Result](https://rules.gbgb.org.uk/section-7-trials-meetings-and-race-meetings/rule-140-order-of-finish-result-definitions/)
- [GBGB Rule 151 – Records of Trials and Races, Going Allowances](https://rules.gbgb.org.uk/section-7-trials-meetings-and-race-meetings/rule-151-records-of-trials-and-races-going-allowances/)