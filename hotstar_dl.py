import requests
import uuid
import os
import re
import pyfiglet
from utils.helper import generate_hmac_id, generate_user_token, ffmpeg_download


def video_extractor(url):
    id = url.split("/")[6]
    auth = generate_hmac_id()
    user_token = generate_user_token()
    response = requests.get(
        "https://api.hotstar.com/play/v2/playback/content/" + id,
        headers={
            "hotstarauth": auth,
            "x-hs-appversion": "7.15.1",
            "x-hs-platform": "web",
            "x-hs-usertoken": user_token,
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36",
        },
        params={
            "desired-config": "audio_channel:stereo|dynamic_range:sdr|encryption:plain|ladder:tv|package:dash|resolution:hd|subs-tag:HotstarVIP|video_codec:vp9",
            "device-id": str(uuid.uuid4()),
            "os-name": "Windows",
            "os-version": "10",
        },
    )

    data = response.json()
    if data["message"] != "Playback URL's fetched successfully":
        print("DRM Protected..! || Premium pack Required")
        return

    return data


def main():
    ascii_art = pyfiglet.figlet_format("Hotstar dl")
    print(ascii_art)
    url = str(input("Enter the Hotstar URL: "))
    url_regex = r'https?://(?:www\.)?hotstar\.com/(?:.+[/-])?(?P<id>\d{10})'
    valid_url = re.match(url_regex, url)
    if valid_url:
        video_data = video_extractor(url)
        playBackSets = video_data["data"]["playBackSets"]
        for playBackSet in playBackSets:
            if "encryption:plain;ladder:phone;package:hls" in playBackSet["tagsCombination"]:
                hls_url = playBackSet["playbackUrl"]
        ffmpeg_download(hls_url, url)


if __name__ == '__main__':
    main()

