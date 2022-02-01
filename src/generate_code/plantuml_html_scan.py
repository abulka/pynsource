import re

# Scan for the actual image url within the plantuml html page

"""
ORIGINAL pre 2020 PLANTUML RESPONSE FORMAT

<p id="diagram">
    
        <img src="http://plantuml.dokku.nas/png/NP1DJyCm38Rl-HK-mc6LEB4J4b-2IGmg8Ku8LIRnMal5cPACCZx-EquBMzTBzFhn-rfsR8inmd9R1fRaDmc-3815USUeelMrlbN5mgcgZewrU90BgbcklDsyaQG_TYrkGdfNFvMbthicf0oqna07z1PZYJNr-ePIrWjP-Lr2hRl-GcmWZCE0SvMF_9axFyRO_hBkGoyokHQV2332vUdyP6wKSuJK4Bng70QpNur-eZ3tEP4QzR4q53YXM890BIRs4XjUvnakO2UcuzG0GbIFm-3WQNa7BGifsRPK6187UGDZHdyzctsVvGt7h2Y63IVmkM7dI5x-cvhQE_lYqF4B" alt="PlantUML diagram" />
    
</p>


NEW 2021 PLANTUML RESPONSE - notice the extra id="theimg" tag

<p id="diagram">
    
    <img id="theimg" src="//www.plantuml.com/plantuml/png/NP1DJyCm38Rl-HK-mc6LEB4J4b-2IGmg8Ku8LIRnMal5cPACCZx-EquBMzTBzFhn-rfsR8inmd9R1fRaDmc-3815USUeelMrlbN5mgcgZewrU90BgbcklDsyaQG_TYrkGdfNFvMbthicf0oqna07z1PZYJNr-ePIrWjP-Lr2hRl-GcmWZCE0SvMF_9axFyRO_hBkGoyokHQV2332vUdyP6wKSuJK4Bng70QpNur-eZ3tEP4QzR4q53YXM890BIRs4XjUvnakO2UcuzG0GbIFm-3WQNa7BGifsRPK6187UGDZHdyzctsVvGt7h2Y63IVmkM7dI5x-cvhQE_jYwlW5" style="max-width: 100%; height: auto;" alt="PlantUML diagram"/>
    
</p>

NEW 2022 PLANTUML RESPONSE - (1) the <p id="theimg" tag is now a div e.g. <div id="diagram", and also 
                                (2) the src= is on a totally new line, requiring . to match end of line (hence re.DOTALL) 
                                    and be non greedy hence .*? etc.

</div>\n\n<div id="diagram">\n \n <img id="theimg"
        src="//www.plantuml.com/plantuml/png/NP1DJyCm38Rl-HK-mc6LEB4J4b-2IGmg8Ku8LIRnMal5cPACCZx-EquBMzTBzFhn-rfsR8inmd9R1fRaDmc-3815USUeelMrlbN5mgcgZewrU90BgbcklDsyaQG_TYrkGdfNFvMbthicf0oqna07z1PZYJNr-ePIrWjP-Lr2hRl-GcmWZCE0SvMF_9axFyRO_hBkGoyokHQV2332vUdyP6wKSuJK4Bng70QpNur-eZ3tEP4QzR4q53YXM890BIRs4XjUvnakO2UcuzG0GbIFm-3WQNa7BGifsRPK6187UGDZHdyzctsVvGt7h2Y63IVmkM7dI5x-cvhQE_jYwlW5"
        style="max-width: 100%; height: auto;" alt="PlantUML diagram" />\n \n</div>\n\n<div>\n

"""

def extract_image_url(html_text):
    """
    Extract the image url from the html text
    """
    image_url = None

    regex = r'.*<p id="diagram".*\s*<.*img src=\"(.*?)\"'  # cater for old, original plantuml html format
    image_url = re.findall(regex, html_text, re.MULTILINE)

    if not image_url:
        regex = r'.*<p id="diagram".*\s*<.*img .*src=\"(.*?)\"'  # cater for NEW 2021 PLANTUML RESPONSE
        image_url = re.findall(regex, html_text, re.MULTILINE)

    if not image_url:
        regex = r'.*<div id=\"diagram\".*?\s*<.*?img .*?src=\"(.*?)\"' # cater for NEW 2022 PLANTUML RESPONSE, needs re.DOTALL
        image_url = re.findall(regex, html_text, re.MULTILINE | re.DOTALL)

    return image_url
