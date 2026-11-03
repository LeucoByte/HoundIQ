MEETING_ID = 991001
RACE_ID = 992001
SECOND_RACE_ID = 992002
DOG_ID = 993001


RACE_RECORDS = [
    {
        "meetingId": MEETING_ID,
        "raceId": RACE_ID,
        "dogId": DOG_ID,
        "raceDate": "04/10/2026",
        "trackName": "Yarmouth",
        "raceTime": "11:01:00",
        "raceNumber": "1",
        "raceClass": "A6",
        "raceDistance": 462.0,
        "raceType": "Flat",
        "raceHandicap": False,
        "raceGoing": "0",
        "raceWinTime": "28.50",
        "dogName": "Good Anna",
        "dogSire": "Ballyhimikin Jet",
        "dogDam": "Epic Majesty",
        "dogOrigin": "Ir",
        "trainerName": "C R Morris",
        "trapNumber": "6",
        "resultPosition": 1,
    }
]


MEETING_DETAILS = [
    {
        "meetingId": MEETING_ID,
        "meetingDate": "04/10/2026",
        "trackName": "Yarmouth",
        "races": [
            {
                "raceId": RACE_ID,
                "raceTime": "11:01:00",
                "raceNumber": "1",
                "raceClass": "A6",
                "raceDistance": 462.0,
                "raceType": "Flat",
                "raceHandicap": False,
                "raceGoing": "0",
                "raceWinTime": "28.50",
                "traps": [
                    {
                        "trapNumber": "6",
                        "dogId": DOG_ID,
                        "dogName": "Good Anna",
                        "dogBorn": "Aug-2023",
                        "dogSex": "b",
                        "dogSire": "Ballyhimikin Jet",
                        "dogDam": "Epic Majesty",
                        "dogOrigin": "Ir",
                        "trainerName": "C R Morris",
                        "resultPosition": 1,
                        "resultBtnDistance": "",
                        "resultRunTime": "28.63",
                        "resultAdjustedTime": "28.63",
                        "resultSectionalTime": "05.39",
                        "resultComment": "",
                        "resultDogWeight": "25.8",
                        "SP": "11/8F",
                    },
                    {
                        "trapNumber": "2"
                    },
                ],
            }
        ],
    }
]


DOG_HISTORIES = [
    {
        "dogId": DOG_ID,
        "totalRaces": 2,
        "items": [
            {
                "raceId": RACE_ID,
                "meetingId": MEETING_ID,
                "raceDate": "04/10/2026",
                "trackName": "Yarmouth",
                "raceTime": "11:01:00",
                "raceNumber": "1",
                "raceClass": "A6",
                "raceDistance": 462.0,
                "raceType": "Flat",
                "raceHandicap": False,
                "raceGoing": "0",
                "raceWinTime": "28.50",
                "trapNumber": "6",
                "resultPosition": 1,
                "resultRunTime": "28.63",
                "resultAdjustedTime": "28.63",
            },
            {
                "raceId": SECOND_RACE_ID,
                "meetingId": MEETING_ID,
                "raceDate": "04/10/2026",
                "trackName": "Yarmouth",
                "raceTime": "11:15:00",
                "raceNumber": "2",
                "raceClass": "A5",
                "raceDistance": 462.0,
                "raceType": "Flat",
                "raceHandicap": False,
                "raceGoing": "0",
                "raceWinTime": "28.40",
                "trapNumber": "3",
                "resultPosition": 2,
                "resultRunTime": "28.70",
                "resultAdjustedTime": "28.70",
            },
        ],
    }
]