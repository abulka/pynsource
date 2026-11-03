"""
Generate the download links for DOWNLOADS.md, bit.ly and the website, from the GitHub
release page.

    $ python bitly.py                    # latest release
    $ python bitly.py pre-2026-dustoff-7 # a specific tag

Asset names it understands (the ones CI produces today):
    pynsource-macos-<tag>.zip
    pynsource-win-<tag>-setup.exe
    pynsource-linux-<tag>-x86_64.AppImage
    pynsource-linux-<tag>-aarch64.AppImage
Legacy release assets (pynsource-1.77-macosx.zip, -win-, -ubuntu-16/-18) are recognised too, so
old tags still work. Missing assets are skipped rather than raising, so a half-built release
still generates something usable.
"""

import sys
import requests
import os
from dataclasses import dataclass  # requires 3.7
from typing import List, Set, Dict, Tuple, Optional
import pprint
from beautifultable import BeautifulTable
from textwrap import dedent

tag = sys.argv[1] if len(sys.argv) > 1 else None
# Use the API, not the release page: the page is client-rendered these days, so scraping it
# silently finds zero assets and prints an empty download list.
releaseApi = (
    f"https://api.github.com/repos/abulka/pynsource/releases/tags/{tag}"
    if tag
    else "https://api.github.com/repos/abulka/pynsource/releases/latest"
)

response = requests.get(releaseApi, headers={"Accept": "application/vnd.github+json"})
assert response.status_code == 200, f"{releaseApi} -> {response.status_code}"
release = response.json()
if not tag:
    tag = release["tag_name"]


@dataclass
class DownloadEntity:
    # link: bs4.element.Tag
    url: str
    basename: str
    basenameNoExtension: str
    bitlyUrl: str


downloads: Dict[str, DownloadEntity] = {}

for asset in release["assets"]:
    url = asset["browser_download_url"]  # e.g. .../releases/download/pre-x/pynsource-macos-pre-x.zip
    basename = os.path.basename(url)  # e.g. pynsource-macos-pre-x.zip
    basenameNoExtension = os.path.splitext(basename)[0]  # e.g. pynsource-1.77-macosx
    basenameNoExtension = basenameNoExtension.replace('.', '-')  # get rid of the illegal '.' chars bitly doesn't like e.g. pynsource-1-77-macosx
    bitlyUrl = f"http://bit.ly/{basenameNoExtension}"  # e.g. http://bit.ly/pynsource-1-77-macosx
    entity = DownloadEntity(
        basename=basename,
        basenameNoExtension=basenameNoExtension,
        url=url,
        bitlyUrl=bitlyUrl,
    )
    if "-macos" in basename or "-macosx" in basename:
        downloads["mac"] = entity
    elif "-win-" in basename:
        downloads["win"] = entity
    elif "-x86_64.AppImage" in basename:
        downloads["linux-x86_64"] = entity
    elif "-aarch64.AppImage" in basename:
        downloads["linux-aarch64"] = entity
    elif "-ubuntu-18" in basename:
        downloads["ubuntu-18"] = entity
    elif "-ubuntu-16" in basename:
        downloads["ubuntu-16"] = entity
    else:
        print(f"skipping {url} - cannot detect OS")

# validate that each download url exists OK - requests can't seem to handle it ?
# 

# headers = {
#     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36 Edg/84.0.522.52",
#     "Referer": "https://github.com/abulka/pynsource/releases/edit/untagged-3ddd799663921fd65d7a",
#     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
#     "Accept-Encoding": "gzip, deflate, br",
#     "Accept-Language": "en-AU,en-GB;q=0.9,en;q=0.8,en-US;q=0.7",
#     "Cache-Control": "max-age=0",
#     "Connection": "keep-alive",
#     "Host": "github.com",
#     "Sec-Fetch-Dest": "document",
#     "Sec-Fetch-Mode": "navigate",
#     "Sec-Fetch-Site": "same-origin",
#     "Sec-Fetch-User": "?1",
#     "Upgrade-Insecure-Requests": "1",
# }
# for downloadEntity in downloads.values():
#     r = requests.head(downloadEntity.url, allow_redirects=True, headers=headers)
#     print(r.url)

#     # try again - doesn't seem to work, still get a 403
#     if r.status_code == 403:
#         newUrl = r.url  # probably to amazon
#         print("trying again...")
#         r = requests.head(newUrl, allow_redirects=True, headers=headers)

#     if r.status_code == 200:
#         print(f"Url {downloadEntity.url} exists OK")
#     elif r.status_code == 403:
#         raise RuntimeError(
#             f"Forbidden download url {downloadEntity.url} status {r.status_code}"
#         )
#     else:
#         raise RuntimeError(
#             f"Malformed download url {downloadEntity.url} status {r.status_code}"
#         )

# print(downloads)
# pprint.pprint(downloads)

# Now that we have gathered up the information, generate the needed outputs

# One table drives both outputs, so a missing asset (an older or half-built release) is simply
# left out instead of raising a KeyError.
ENTRIES = [
    ("mac", "Mac download", "(unzip and drag app into the Applications directory)"),
    ("win", "Windows 10 download", "(run the installer)"),
    ("linux-x86_64", "Linux x86_64 download", "(make executable and run the AppImage)"),
    ("linux-aarch64", "Linux arm64 download", "(make executable and run the AppImage)"),
    ("ubuntu-18", "Ubuntu Linux 18.04 download", "(unzip and run the executable)"),
    ("ubuntu-16", "Ubuntu Linux 16.04 download", "(unzip and run the executable)"),
]
SNAP = ("http://bit.ly/pynsource-snap", "Linux snap installer",
        "(one-click install on any Ubuntu distro)")

downloadMarkdown = "\n".join(
    [f" * [{label}]({downloads[key].bitlyUrl}) {suffix}"
     for key, label, suffix in ENTRIES if key in downloads]
    + [f" * [{SNAP[1]}]({SNAP[0]}) {SNAP[2]}"]
)
print("DOWNLOADS.md")
print(downloadMarkdown)

t = BeautifulTable(max_width=760)
t.column_headers = [
    "OS",
    "download-url",
    "customize back half / title",
    "final bitly-url",
]
t.column_alignments["download-url"] = BeautifulTable.ALIGN_LEFT
t.column_alignments["final bitly-url"] = BeautifulTable.ALIGN_LEFT
for os, downloadEntity in downloads.items():
    t.append_row(
        [os, downloadEntity.url, downloadEntity.basenameNoExtension, downloadEntity.bitlyUrl,]
    )
print("Bitly Entries to create (click on each link in turn (in vscode terminal) to ensure it exists and triggers a download)")
print(t)
print()

htmlItems = "\n".join(
    [f'    <li><a href="{downloads[key].bitlyUrl}" rel="nofollow">{label}</a> {suffix}</li>'
     for key, label, suffix in ENTRIES if key in downloads]
    + [f'    <li><a href="{SNAP[0]}" rel="nofollow">{SNAP[1]}</a> {SNAP[2]}</li>']
)
htmlFragmentForWebsite = (
    f"<p>The latest version is <code>{tag or 'latest'}</code></p>\n<ul>\n{htmlItems}\n</ul>"
)
print("Fragment of HTML to put on official website on downloads page")
print(htmlFragmentForWebsite)
