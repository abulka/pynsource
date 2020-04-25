# See ztree1.js approx line 724 for exact same javascript versions.
REGEX_FOR_CLASSES = r"^\s*class (.*?)[\(:]"  # https://regex101.com/r/W2JF51/1
REGEX_FOR_METHODS = r"^(?:async |)def (.*?)\(.*\):"  # https://regex101.com/r/z6PHoB/1
REGEX_FOR_MODULE_ATTRS = r"^([a-zA-Z]+\w*)[\.\w]*[ \t]*=(?!=).+"  # https://regex101.com/r/0cxbZR/6


class QuickParse(object):
    """
    Class representing source code's approximate classname, module functions and module attributes.
    Achieved via cheap and nasty regex.

    Results stored in class instance as properties e.g. ``self.quick_found_classes``
    """

    def __init__(self, filename, logh=None):
        import re

        # secret regular expression based preliminary scan for classes and module defs
        # Feed the file text into findall(); it returns a list of all the found strings
        with open(filename, "r", encoding='utf-8') as f:
            source = f.read()
        self.quick_found_classes = re.findall(
            REGEX_FOR_CLASSES, source, re.MULTILINE
        )  #: list of classes
        self.quick_found_module_defs = re.findall(
            REGEX_FOR_METHODS, source, re.MULTILINE
        )  #: list of module functions
        self.quick_found_module_attrs = re.findall(
            REGEX_FOR_MODULE_ATTRS, source, re.MULTILINE
        )  #: list of module attributes

        if logh:
            logh.out_wrap_in_html(
                "quick_found_classes %s<br>quick_found_module_defs %s<br>quick_found_module_attrs %s<br>"
                % (
                    self.quick_found_classes,
                    self.quick_found_module_defs,
                    self.quick_found_module_attrs,
                ),
                style_class="quick_findings",
            )
