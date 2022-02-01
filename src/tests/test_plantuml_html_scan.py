import unittest
import os
import sys

sys.path.append("../src")
from generate_code.plantuml_html_scan import extract_image_url


class TestCasePlantUmlServerHtmlScan(unittest.TestCase):

    def test_original_server_format(self):
        response_text = """
            <p id="diagram">
                
                    <img src="http://plantuml.dokku.nas/png/NP1DJyCm38Rl-HK-mc6LEB4J4b-2IGmg8Ku8LIRnMal5cPACCZx-EquBMzTBzFhn-rfsR8inmd9R1fRaDmc-3815USUeelMrlbN5mgcgZewrU90BgbcklDsyaQG_TYrkGdfNFvMbthicf0oqna07z1PZYJNr-ePIrWjP-Lr2hRl-GcmWZCE0SvMF_9axFyRO_hBkGoyokHQV2332vUdyP6wKSuJK4Bng70QpNur-eZ3tEP4QzR4q53YXM890BIRs4XjUvnakO2UcuzG0GbIFm-3WQNa7BGifsRPK6187UGDZHdyzctsVvGt7h2Y63IVmkM7dI5x-cvhQE_lYqF4B" alt="PlantUML diagram" />
                
            </p>
        """
        image_url = extract_image_url(response_text)
        self.assertIsNotNone(image_url)

    def test_2021_server_format(self):
        response_text = """
            <p id="diagram">
                
                <img id="theimg" src="//www.plantuml.com/plantuml/png/NP1DJyCm38Rl-HK-mc6LEB4J4b-2IGmg8Ku8LIRnMal5cPACCZx-EquBMzTBzFhn-rfsR8inmd9R1fRaDmc-3815USUeelMrlbN5mgcgZewrU90BgbcklDsyaQG_TYrkGdfNFvMbthicf0oqna07z1PZYJNr-ePIrWjP-Lr2hRl-GcmWZCE0SvMF_9axFyRO_hBkGoyokHQV2332vUdyP6wKSuJK4Bng70QpNur-eZ3tEP4QzR4q53YXM890BIRs4XjUvnakO2UcuzG0GbIFm-3WQNa7BGifsRPK6187UGDZHdyzctsVvGt7h2Y63IVmkM7dI5x-cvhQE_jYwlW5" style="max-width: 100%; height: auto;" alt="PlantUML diagram"/>
                
            </p>
        """
        image_url = extract_image_url(response_text)
        self.assertIsNotNone(image_url)

    def test_2022_server_format(self):
        response_text = """
            </div>\n\n<div id="diagram">\n \n <img id="theimg"
                    src="//www.plantuml.com/plantuml/png/NP1DJyCm38Rl-HK-mc6LEB4J4b-2IGmg8Ku8LIRnMal5cPACCZx-EquBMzTBzFhn-rfsR8inmd9R1fRaDmc-3815USUeelMrlbN5mgcgZewrU90BgbcklDsyaQG_TYrkGdfNFvMbthicf0oqna07z1PZYJNr-ePIrWjP-Lr2hRl-GcmWZCE0SvMF_9axFyRO_hBkGoyokHQV2332vUdyP6wKSuJK4Bng70QpNur-eZ3tEP4QzR4q53YXM890BIRs4XjUvnakO2UcuzG0GbIFm-3WQNa7BGifsRPK6187UGDZHdyzctsVvGt7h2Y63IVmkM7dI5x-cvhQE_jYwlW5"
                    style="max-width: 100%; height: auto;" alt="PlantUML diagram" />\n \n</div>\n\n<div>\n
        """
        image_url = extract_image_url(response_text)
        self.assertIsNotNone(image_url)


def suite():
    suite1 = unittest.makeSuite(TestCasePlantUmlServerHtmlScan, "test")
    alltests = unittest.TestSuite((suite1,))
    return alltests


def main():
    runner = unittest.TextTestRunner(
        descriptions=0, verbosity=2
    )  # default is descriptions=1, verbosity=1
    runner.run(suite())


if __name__ == "__main__":
    main()
