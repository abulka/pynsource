import os


class LogWriter:
    def __init__(self, in_filename=None, out_filename=None, print_to_console=False):

        self.print_to_console = print_to_console
        self.out_filename = ""

        # TODO should allow both 'in_filename' and 'out_filename' to be separately specified

        if in_filename:
            out_filename = os.path.basename(in_filename)
            fileName, fileExtension = os.path.splitext(out_filename)
            # self.out_filename = "tests/logs/debug_%s.html" % fileName
            self.out_filename = "src/tests/logs/debug_%s.html" % fileName
        else:
            self.out_filename = out_filename
        assert self.out_filename, "Must specify either in or out filename"

        self.f = open(self.out_filename, "w")

    def finish(self):
        self.f.close()

    def ensure_is_open(self):
        try:
            # file is sometimes closed in error conditions, so reopen it
            self.out("<br/>")
        except ValueError as e:
            print(e, "re-opening html log file cos it was closed...")
            self.f = open(self.out_filename, "a")

    def out(self, s, force_print=False):
        if self.print_to_console or force_print:
            print(s)
        self.f.write("%s\n" % s)

    def out_divider(self):
        if self.print_to_console:
            print("-" * 80)
        self.f.write("<HR>\n")

    def out_wrap_in_html(self, s, style_class="dump1", heading="click", force_print=False):
        self.out("<div class=%s><pre>%s</div></pre>" % (style_class, s))

    def out_html_header(self):
        self.out(
            """
            <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN">
            <html>
            <head>
              <title>Pynsource Parse Log as HTML</title>
              <style type="text/css">
                body { background:DarkSeaGreen; font-family:monospace; }
                .dump1 { background:lightblue; margin:3px; padding:5px; font-size:1.2em;}
                .dumpdiff { background:black; color: white; padding:5px;}
                .mynote0 { font-family:monospace; font-size:1.5em; }
                .mynote1 { color:MediumBlue ; font-size:1.1em; }
                .mynote2 { color:FireBrick ; font-size:1.2em; }
                .mynote3 { background-color:AntiqueWhite; font-size:1.1em; }
                .stacktrace { background-color:IndianRed; font-size:1.2em; 
                            border-style:dashed; border-width:3px; margin:5px;
                            padding:5px; margin:8px; }
                .quick_findings { background:MidnightBlue; color:white; font-style: italic;
                                    margin:13px; padding:5px; font-size:1.4em; }
                table, td, th
                {
                border:1px solid green;
                border-collapse:collapse;
                padding:5px;
                font-size:0.8em;
                font-family:"Times New Roman",Georgia,Serif;
                background-color:PaleGreen;
                }
              </style>
            </head>
            
            <body>
            """
        )

    def out_html_footer(self):
        self.out(
            """
            </body>
            </html>
        """
        )


class LogWriterNull:
    def __init__(self, in_filename=None, out_filename=None, print_to_console=False):
        self.print_to_console = print_to_console
        self.out_filename = out_filename

    def finish(self):
        pass

    def out(self, s, force_print=False):
        pass

    def out_divider(self):
        pass

    def out_wrap_in_html(self, s, style_class="dump1", heading="click", force_print=False):
        pass

    def out_html_header(self):
        pass

    def out_html_footer(self):
        pass
