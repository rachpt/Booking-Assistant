#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    : test.py
@Time    : 2019/11/15 23:38:29
@Author  : rachpt
@Version : 0.1
@Contact : rachpt@126.com
"""

# here put the import lib
import requests
import binascii
import Crypto
from Crypto.PublicKey import RSA


def get_zerobytes(N):
    return b"\0" * N


def encr_pw(pw):
    key = RSA.construct(
        [
            0x89B7AD1090FE776044D393A097E52F99FC3F97690C90215ECB01F1B3DFC4D8B0226A4B16F51A884E0C1545180EB40365DBEC848CC0DF52F515512E2317BF9D82B6F4C9CAFCC94082FD86C97E77A4D3AA44CBA54F8D94F5757CE3CC82C3ADF31082738CFE531B4B4675F35A0C8401745DBED15C92D0747C6349915378FFF22B9B,
            0x10001,
        ]
    )
    ohdave = ""
    length = len(pw)
    for i in range(0, length):
        ohdave += pw[length - 1 - i]
    try:
        ciphertxt = key.encrypt(bytes(ohdave, "us-ascii"), 0)[0]
    except NotImplementedError:
        cipher = PKCS1_v1_5.new(key)
        ciphertxt = cipher.encrypt(bytes(ohdave, "us-ascii"))
    return ciphertxt


pw = "rc@0511416752"
res = binascii.hexlify(encr_pw(pw)).decode("ascii")

print(res)

url = "https://pass.hust.edu.cn/cas/login?service=http://pecg.hust.edu.cn/cggl/"

headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 7.0; SM-G892A Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/67.0.3396.87 Mobile Safari/537.36"
}

data = {
    "username": "16cadbd7cac92532aa266125409d86c5b4aaf1cc349676d967e983436b32b9e1b764b3fafb9d75b6711ba3e72964578a60bc92c664323fed3572894e9c76e47ed279a8bcc8ba099d1c8f6ac0834dadd5865223dc5ec050da91d76703912f701b4ff49fb20d52b725abf58c9f878c6af9036fa7cc58d3058418b3e606ca2364a9",
    "password": "0d446c82a7fc28304b7a9fe93e82115b935334dfa1f07a8703c97eaa9cd5224571febddfe4df15b1dc10870af513c49146d48a0e6101dee701cda1b5b85402cee39f55f4a9ecf3c4acc957e06e296d5c900e3141a7fff23f3c25cee2f95986ca7fb31c8bbfe97885e01cbe3a68d0380a6e621e3fa5b22b25ceca98549f393edb",
    "lt": "LT-NeusoftAlwaysValidTicket",
    "code": "code",
    "_eventId": "submit",
    "execution": "e12s1",
}

r = requests.post(url, data=data, headers=headers)

print(r.status_code)
print(r.cookies)
print(r.history)
