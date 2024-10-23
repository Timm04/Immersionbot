import os

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
guild_id = os.getenv("SERVER_ID")
TOKEN = os.getenv("TOKEN")
ALLOWED_CHANNELS = [796876740445208606] # Channel IDs where certain features like logging are allowed

_DB_NAME = 'prod.db'
_JP_DB = "dbs/japanese.db"
_GOAL_DB = "dbs/goals.db"
_IMMERSION_CODES = "jsons/immersion_codes.json"
_MULTIPLIERS = "jsons/multipliers.json"

ACHIEVEMENTS = {
    "VN": [1, 50_000, 100_000, 500_000, 1_000_000, 2_000_000, 4_000_000, 10_000_000, float('inf')],
    "ANIME": [1, 12, 25, 100, 200, 500, 800, 1500, float('inf')],
    "READING": [1, 50_000, 100_000, 500_000, 1_000_000, 2_000_000, 4_000_000, 10_000_000, float('inf')],
    "BOOK": [1, 100, 250, 1000, 2500, 5000, 10_000, 20_000, float('inf')],
    "MANGA": [1, 250, 1250, 5000, 10_000, 25_000, 50_000, 100_000, float('inf')],
    "LISTENING": [1, 250, 500, 2000, 5000, 10_000, 25_000, 50_000, float('inf')],
    "READTIME": [1, 250, 500, 2000, 5000, 10_000, 25_000, 50_000, float('inf')],
}

PT_ACHIEVEMENTS = [1, 100, 300, 1000, 2000, 10_000, 25_000, 100_000, float('inf')]

ACHIEVEMENT_RANKS = ['Beginner', 'Initiate', 'Apprentice', 'Hobbyist', 'Enthusiast', 'Aficionado', 'Sage', 'Master']
ACHIEVEMENT_EMOJIS = [':new_moon:', ':new_moon_with_face:', ':waning_crescent_moon:', ':last_quarter_moon:', ':waning_gibbous_moon:', ':full_moon:', ':full_moon_with_face:', ':sun_with_face:']
ACHIEVEMENT_IDS = [1120790734476423270, 1120790825702527037, 1120790890038952066, 1120790964970213436, 1120791040463470702, 1120791104518901912, 1120791193366823112, 1120791256818266112]

EMOJI_TABLE = {
    # 'Yay': 658999234787278848,
    # 'NanaYes': 837211260155854849,
    # 'NanaYay': 837211306293067797,
    "990": 921933172432863283,
    "CatBlush": 933089264030339083,
    "CatTup": 948511239401799681,
    "ChikaTup": 918620369919828000,
    "ChubbyGero": 831348462305673286,
    "ChubbyGeroSwag": 929124878047641690,
    "CoolCat": 783741575582580758,
    "InuPero": 963127794194350110,
    "NadeshikoUma": 921677406849363989,
    "NanaJam": 882894763987177493,
    "NanaYay": 837211306293067797,
    "NanaYes": 877679734547427349,
    "NekoGero": 936524524231458897,
    "Peek": 918616198302793739,
    "ShimarinDango": 921677567084359702,
    "SugoiAA": 678245454068056097,
    "TachiSmile": 688824520362164303,
    "TohruFlex": 926637533994037328,
    "Yay": 658999234787278848,
    "Yousoroo": 698293340881289221,
    "Yousoroo2": 709339172602904586,
    "YuiPeace": 918623813552447529,
    "ajatt": 783749154807087134,
    "anki": 688802971089371185,
    "kanadestanding": 1221064050046144603,
    "pregnant_man_kneeling": 1223330275883487284,
    "10smartgirlcat": 1224470325140394014,
    "10smartchefcat": 1224475222703341661,
    "10smartmadcat": 1224732251087179806,
    "10smartblushcat": 1224732320842383383,
    "10smartuchagi": 1225129378736771172,
    "ankihug": 1197968379051515998,
    "kannabear": 1186993056017289277,
    "NanaAnki": 1193117011945984070,
    "ankilove": 1195483801464344638,
    "KimoiHuh": 931588710473031761,
}

TIMEFRAMES = ["WEEK, MONTH, YEAR, All"]

JACK_FILTER = ["imouto", "sister", "いもうと", "妹", "sis", "sisters", "お兄ちゃん", "兄", "ブラコン", "きょうだい"]

timezones = {
    "UTC": 0,
    "America/New_York": -5,  # Eastern Time (ET)
    "America/Toronto": -5,  # Eastern Time (ET)
    "America/Chicago": -6,  # Central Time (CT)
    "America/Denver": -7,  # Mountain Time (MT)
    "America/Los_Angeles": -8,  # Pacific Time (PT)
    "Europe/London": 0,  # Greenwich Mean Time (GMT)
    "Europe/Madrid": 1,  # Central European Time (CET)
    "Europe/Rome": 1,  # Central European Time (CET)
    "Europe/Kiev": 2,  # Eastern European Time (EET)
    "Asia/Tokyo": 9,  # Japan Standard Time (JST)
    "Asia/Shanghai": 8,  # China Standard Time (CST)
    "Asia/Kolkata": 5.5,  # Indian Standard Time (IST)
    "Australia/Sydney": 10,  # Australian Eastern Time (AEST)
    "Pacific/Auckland": 12,  # New Zealand Standard Time (NZST)
    "America/Mexico_City": -6,  # Central Time (CT)
    "America/Bogota": -5,  # Colombia Time (COT)
    "America/Lima": -5,  # Peru Time (PET)
    "Asia/Dubai": 4,  # Gulf Standard Time (GST)
    "Asia/Singapore": 8,  # Singapore Standard Time (SGT)
    "Asia/Hong_Kong": 8,  # Hong Kong Standard Time (HKT)
    "Europe/Istanbul": 3,  # Turkey Time (TRT)
    "Asia/Bangkok": 7,  # Indochina Time (ICT)
    "Africa/Johannesburg": 2,  # South Africa Standard Time (SAST)
}

MESSAGE_FORMATS = {
    "VN": "{conversion} points/characters → +{points} points",
    "MANGA": "{conversion} points per page → +{points} points",
    "BOOK": "{conversion} point per page → +{points} points",
    "ANIME": "{conversion} points per eps → +{points} points",
    "READING": "{conversion} points/character of reading → +{points} points",
    "READTIME": "{conversion} points/min of readtime → +{points} points",
    "LISTENING": "{conversion} points/min of listening → +{points} points"
}