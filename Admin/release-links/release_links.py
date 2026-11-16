"""
Generate the download links for DOWNLOADS.md and the website, from the GitHub release.

    $ python release_links.py                    # latest release
    $ python release_links.py version-1.86       # a specific tag

Prints three things, all with direct github.com URLs:

  * markdown bullets (for DOWNLOADS.md or a release announcement)
  * an HTML fragment (for the download page on pynsource.com)
  * a table of asset -> url, for a quick eyeball check

The bit.ly shortener is deliberately not used any more: the old free plan is gone, the links
rotted silently, and a 404 shortener is worse than a long URL. The website therefore links
straight at the release assets.

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
from dataclasses import dataclass
from typing import Dict
from beautifultable import BeautifulTable

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
    url: str
    basename: str


downloads: Dict[str, DownloadEntity] = {}

for asset in release["assets"]:
    url = asset["browser_download_url"]  # .../releases/download/<tag>/pynsource-macos-<tag>.zip
    basename = os.path.basename(url)
    entity = DownloadEntity(url=url, basename=basename)
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
SNAP = ("https://snapcraft.io/pynsource", "Linux snap installer",
        "(one-click install on any Ubuntu distro)")

downloadMarkdown = "\n".join(
    [f" * [{label}]({downloads[key].url}) {suffix}"
     for key, label, suffix in ENTRIES if key in downloads]
    + [f" * [{SNAP[1]}]({SNAP[0]}) {SNAP[2]}"]
)
print("Markdown bullets")
print(downloadMarkdown)

t = BeautifulTable(max_width=200)
t.column_headers = ["OS", "download-url"]
t.column_alignments["download-url"] = BeautifulTable.ALIGN_LEFT
for os_name, entity in downloads.items():
    t.append_row([os_name, entity.url])
print()
print(t)
print()

htmlItems = "\n".join(
    [f'    <li><a href="{downloads[key].url}" rel="nofollow">{label}</a> {suffix}</li>'
     for key, label, suffix in ENTRIES if key in downloads]
    + [f'    <li><a href="{SNAP[0]}" rel="nofollow">{SNAP[1]}</a> {SNAP[2]}</li>']
)
htmlFragmentForWebsite = (
    f"<p>The latest version is <code>{tag or 'latest'}</code></p>\n<ul>\n{htmlItems}\n</ul>"
)
print("Fragment of HTML for the download page on pynsource.com")
print(htmlFragmentForWebsite)
