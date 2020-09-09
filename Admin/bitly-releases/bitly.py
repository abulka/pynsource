"""
Generate the links for
    - DOWNLOADS.md
    - Bitly
    - Main website html
from parsing the Github release page HTML information
"""

import requests
from bs4 import BeautifulSoup
import bs4
import os
from dataclasses import dataclass  # requires 3.7
from typing import List, Set, Dict, Tuple, Optional
import pprint
from beautifultable import BeautifulTable

releaseUrl = "https://github.com/abulka/pynsource/releases/tag/version-1.77"

response = requests.get(releaseUrl)
assert response.status_code == 200

html_doc = response.text
with open("junk.html", "w") as fp:
    fp.write(html_doc)

soup = BeautifulSoup(html_doc, "html.parser")
# print(soup)


@dataclass
class DownloadEntity:
    # link: bs4.element.Tag
    url: str
    basename: str
    basenameNoExtension: str
    bitlyUrl: str


downloads: Dict[str, DownloadEntity] = {}

for link in soup.find_all("a"):
    if "/abulka/pynsource/releases/download/" in link.get("href"):
        # print(link.get('href'))
        url = f"https://github.com{link.get('href')}"  # e.g. https://github.com/abulka/pynsource/releases/download/version-1.77/pynsource-1.77-macosx.zip
        basename = os.path.basename(url)  # e.g. pynsource-1.77-macosx.zip
        basenameNoExtension = os.path.splitext(basename)[0]  # e.g. pynsource-1.77-macosx
        basenameNoExtension = basenameNoExtension.replace('.', '-')  # get rid of the illegal '.' chars bitly doesn't like e.g. pynsource-1-77-macosx
        bitlyUrl = f"http://bit.ly/{basenameNoExtension}"  # e.g. http://bit.ly/pynsource-1-77-macosx
        entity = DownloadEntity(
            basename=basename,
            basenameNoExtension=basenameNoExtension,
            url=url,
            bitlyUrl=bitlyUrl,
        )
        if "-macosx" in basename:
            downloads["mac"] = entity
        elif "-win-" in basename:
            downloads["win"] = entity
        elif "-ubuntu-18" in basename:
            downloads["ubuntu-18"] = entity
        elif "-ubuntu-16" in basename:
            downloads["ubuntu-16"] = entity
        else:
            raise RuntimeError(
                f"Unknown url on Github releases page {url} - cannot detect OS"
            )

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

downloadMarkdown = f"""
 * [Mac download]({downloads["mac"].bitlyUrl}) (unzip and drag app into the Applications directory) 
 * [Windows 10 download]({downloads["win"].bitlyUrl}) (unzip and run the installer) 
 * [Ubuntu Linux 18.0.4 download]({downloads["ubuntu-18"].bitlyUrl}) (unzip and run the executable) 
 * [Ubuntu Linux 16.0.4 download]({downloads["ubuntu-16"].bitlyUrl}) (unzip and run the executable) 
 * [Linux snap installer](http://bit.ly/pynsource-snap) (one-click install on any Ubuntu distro) 
"""
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
