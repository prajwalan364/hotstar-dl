import hashlib
import hmac
import time
import uuid
import random
import json
import requests
import re
import os
from ffmpeg_progress_yield import FfmpegProgress
from tqdm import tqdm

_AKAMAI_ENCRYPTION_KEY = b"\x05\xfc\x1a\x01\xca\xc9\x4b\xc4\x12\xfc\x53\x12\x07\x75\xf9\xee"


def generate_hmac_id():
    st = int(time.time())
    exp = st + 6000
    auth = "st=%d~exp=%d~acl=/*" % (st, exp)
    auth += "~hmac=" + hmac.new(_AKAMAI_ENCRYPTION_KEY, auth.encode(), hashlib.sha256).hexdigest()
    return auth


def generate_user_token():
    auth = generate_hmac_id()
    data = json.dumps({"device_ids": [{"id": str(uuid.uuid4()), "type": "device_id"}]}).encode("utf-8")
    res = requests.post(
        "https://api.hotstar.com/um/v3/users",
        data=data,
        headers={
            "hotstarauth": auth,
            "x-hs-platform": "PCTV",
            "Content-Type": "application/json",
        },
    )
    token = res.json()["user_identity"]
    return token


def ffmpeg_download(hls_url, url):
    name = url.split('/')[5]
    cmd = [
        "ffmpeg",
        "-referer",
        url,
        "-i",
        hls_url,
        "-preset",
        "fast",
        "{}[1080p].mp4".format(name),
    ]
    ff = FfmpegProgress(cmd)
    with tqdm(
        total=100,
        position=1,
        desc="Downloading",
    ) as pbar:
        for progress in ff.run_command_with_progress():
            pbar.update(progress - pbar.n)


# cmd = 'ffmpeg -referer {} -i "{}" -c copy "{} [1080p]".mp4'.format(url, hls_url, name)
# os.system(cmd)


'''

def generate_device_id():
    """
    Reversed from javascript library.
    JS function is generateUUID
    """
    t = int(round(time.time() * 1000))
    e = "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx"  # 4 seems to be interchangeable

    def _replacer():
        n = int((t + 16 * random.random())) % 16 | 0
        return hex(n if "x" == e else 3 & n | 8)[2:]

    return "".join([_.replace("x", _replacer()) for _ in e])

'''