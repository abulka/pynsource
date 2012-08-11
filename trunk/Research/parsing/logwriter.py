import os

class LogWriter:
    def __init__(self, in_filename=None, out_filename=None, do_prints=False):
        
        self.do_prints = do_prints

        if in_filename:
            out_filename = os.path.basename(in_filename)
            fileName, fileExtension = os.path.splitext(out_filename)
            self.out_filename = "logs/debug_%s.html" % fileName
        else:
            self.out_filename = out_filename
        assert self.out_filename, "Must specify either in or out filename"
        
        self.f = open(self.out_filename, 'w')
        
    
    def finish(self):
        self.f.close()
        
    def out(self, s):
        if self.do_prints:
            print s
        self.f.write("%s\n"%s)

    def out_divider(self):
        if self.do_prints:
            print "-"*80
        self.f.write("<HR>\n")
        
    def out_wrap_in_html(self, s, style_class='dump1'):
        self.out("<div class=%s><pre> %s</div></pre>" % (style_class, s))
            
    def out_html_header(self):
        self.f.write("""
            <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN">
            <html>
            <head>
              <title>My first styled page</title>
              <style type="text/css">
                body { background:DarkSeaGreen; font-family:monospace; }
                .dump1 { background:lightblue; margin:3px; padding:5px; font-size:1.2em;}
                .dumpdiff { background:black; color: white; padding:5px;}
                .mynote0 { font-family:monospace; font-size:1.5em; }
                .mynote1 { color:MediumBlue ; font-size:1.1em; }
                .mynote2 { color:FireBrick ; font-size:1.2em; }
                .mynote3 { background-color:AntiqueWhite; font-size:1.1em; }
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
            """)
        
    def out_html_footer(self):
        self.f.write("""
            </body>
            </html>
        """)
        
