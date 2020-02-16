#!/usr/bin/env python3
import os
import sys
import time
import random

import requests
import wikipedia

from lib.constants import (
    BACKOFF, MAX_ATTEMPTS, MAX_STATUS_LEN,
    TIMEOUT_BACKOFF, DAVY_CROCKETT_LYRICS,
    WIKIDATA_REGEX, DEL_CHARS, SWAP_CHARS,
)
from lib import twitter
from lib import words


rng = random.SystemRandom()


def main():
    title = searchForTMNT(MAX_ATTEMPTS, BACKOFF)
    lyrics = formatLyrics(title)
    profile_pic = getProfilePicture(title)
    status_text = "\n".join((lyrics, words.getWikiUrl(title)))
    twitter.sendTweet(status_text, profile_pic)
    print((status_text, profile_pic))


def searchForTMNT(attempts=MAX_ATTEMPTS, backoff=BACKOFF):
    """Loop MAX_ATTEMPT times, searching for a TMNT meter wikipedia title.

    Args:
        Integer: attempts, retries remaining.
        Integer: backoff, seconds to wait between each loop.
    Returns:
        String or False: String of wikipedia title in TMNT meter, or False if
                         none found.
    """
    for attempt in range(attempts):
        print(f"\r{str(attempt * 10)} articles fetched...", end="")
        sys.stdout.flush()
        title = checkTenPagesForTMNT()

        if type(title) == str and len(title) > 1:
            print(f"\nMatched: {title}")
            return title

        time.sleep(backoff)

    print(f"\nNo matches found.")
    sys.exit(1)


def checkTenPagesForTMNT():
    """Get 10 random wiki titles, check if any of them isTMNT().

    We grab the max allowed Wikipedia page titles (10) using wikipedia.random().
    If any title is in TMNT meter, return the title. Otherwise, return False.

    Args:
        None
    Returns:
        String or False: The TMNT compliant title, or False if none found.
    """
    wikipedia.set_rate_limiting(True)
    try:
        titles = wikipedia.random(10)
    except wikipedia.exceptions.HTTPTimeoutError as e:
        print(f"Wikipedia timout exception: {e}")
        time.sleep(TIMEOUT_BACKOFF)
        main()
    except wikipedia.exceptions.WikipediaException as e:
        print(f"Wikipedia exception: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Exception while fetching wiki titles: {e}")
        sys.exit(1)

    for title in titles:
        if words.isTMNT(title):
            return title
    return False


def formatLyrics(word):
    # This is, of course, hacky, but we need to figure out
    # how the syllable stress code interpreted our wiki title
    # and break it up along the correct lines.

    # To estimate, we call getTitleStresses on increasing slices of
    # the input word and use whatever maximum span resulted in two syllables.
    # Unfortunately, for some words the greedy algorithm is unlucky:
    # this carves 'Antismoking' into 'Antis' 'moking',
    # which is wrong but still entertaining.

    max_two_syllables = None
    for char_idx in range(len(word)):
        cleaned_word = words.cleanStr(word[:char_idx+1])
        stresses = words.getTitleStresses(cleaned_word)
        if len(stresses) == 2:
            max_two_syllables = word[:char_idx+1].strip()

    if max_two_syllables is None:
        max_two_syllables = word

    # Examples:
    # George A. Archer -> George A., George A. Archer, king of the wild frontier!
    # Anti-fashion -> Anti-, Anti-fashion, king of the wild frontier!
    # Antismoking -> Anti, Antismoking, king of the wild frontier!

    epithet = rng.choice(DAVY_CROCKETT_LYRICS)
    return f"{max_two_syllables}, {word}, {epithet}"


def getProfilePicture(word):
    # I don't know how reliably page.references is going to work, it seems like the
    # wikipedia module doesn't really have a good way of dealing with this data.
    try:
        page = wikipedia.page(word)
    except wikipedia.exceptions.DisambiguationError as e:
        return getProfilePicture(e.options[0])
    except wikipedia.exceptions.WikipediaException as e:
        print(f"Wikipedia exception: {e}")
        sys.exit(1)
    wikidatas = []
    for url in page.references:
        match = WIKIDATA_REGEX.search(url)
        if not match:
            continue
        wikidata_ref = match.group(1)
        wikidata_json = requests.get(f"https://www.wikidata.org/wiki/Special:EntityData/{wikidata_ref}.json").json()
        relevant_wikidata = wikidata_json['entities'][wikidata_ref]
        # If there happen to be more than one wikidata link on the page
        # skip the offenders.
        if relevant_wikidata.get('labels', {}).get('en', {}).get('value') != word:
            continue
        images = relevant_wikidata.get('claims', {}).get('P18', [])
        if len(images) == 0:
            continue
        image_name = images[0]['mainsnak']['datavalue']['value']
        commons_query = f"https://commons.wikimedia.org/w/api.php?action=query&titles=File:{image_name}&format=json&prop=imageinfo&iiprop=url"
        commons_resp = requests.get(commons_query).json()
        pages = commons_resp.get('query', {}).get('pages', {})
        # I guess this API can return multiple pages, but it returns them as object keys, not a list (???)
        page_ids = list(pages.keys())
        if len(page_ids) != 1:
            continue
        page_obj = pages[page_ids[0]]
        imageinfos = page_obj.get('imageinfo', [])
        if len(imageinfos) == 0:
            continue
        imageinfo = imageinfos[0]
        return imageinfo['url']
    return


if __name__ == "__main__":
    main()
