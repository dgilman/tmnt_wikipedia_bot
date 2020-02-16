import re

# Constants for use throughout the application.
# Someday maybe I'll use configs or CLI args. For now this is easier.

MAX_ATTEMPTS = 1000
MAX_STATUS_LEN = 280
BACKOFF = 0.5
TIMEOUT_BACKOFF = 240
LOGO_PATH = r'/tmp/logo.png'
SCREENSHOT_PATH = r'/tmp/screenshot.png'
CHROME_PATH = r'google-chrome'
KEY_PATH = r'twitter_keys.txt'
URL = 'file:///home/catherine_lee_ball/tmnt.html'
# Article titles the contain strings in BANNED_WORDS are skipped.
# Banned words are things that are very inappropriate, or things
# that are oversaturating the timeline, i.e. historic districts
BANNED_WORDS = ("rape", "nazi", "victim", "shootings")
BANNED_PHRASES = (r"(", "shooting", "railway station", "rugby union", "historic district", "murder of", "killing of", "rugby player", ", baron ")
PRONUNCIATION_OVERRIDES = (("HD", "10"), ("U.S.", "10"), ("Laos", "1"))
TMNT_STRESSES = re.compile(r"1[02]1[02]")
CHARS_ONLY = re.compile("[^a-zA-Z]")
DAVY_CROCKETT_LYRICS = ("king of the wild frontier!",
                        "the one who don't know fear!",
                        "the buckskin buccaneer!",
                        "the champion of us all!",
                        # Hmmm
                        # "trackin' the redskins down!"
                        "holdin' their promise dear!",
                        "holdin' their young'uns dear!",
                        "headin' on West again!",
                        "lookin' fer Paradise!",
                        "beginnin' their campaign!",
                        "choice of the whole frontier!",
                        "the Canebrake Congressman!",
                        "seein' their duty clear!",
                        "helpin' their legend grow!",
)
WIKIDATA_REGEX = re.compile('https://www.wikidata.org/wiki/(Q\d+)')
