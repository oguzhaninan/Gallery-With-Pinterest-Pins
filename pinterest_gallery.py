# coding: utf-8
import json
import requests
import sys
import argparse
import os

class colors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    ENDC = '\033[0m'

parser = argparse.ArgumentParser()
parser.add_argument("-d", dest = "d", help="Description [0|1]", default=0, type=int)
parser.add_argument("-i", dest = "i", help="Images Download [0|1]", default=0, type=int)
parser.add_argument("-l", dest = "l", help="Number of pins", default=10, type=int)
parser.add_argument("-o", dest = "o", help="Html file name", default="index", type=str)
args = parser.parse_args()

token = "<TOKEN>"

username = str(input("User Name: "))
board    = str(input("Board Name: "))

url = "https://api.pinterest.com/v1/boards/%s/%s/pins/" % (username,board)

response = requests.get(url,params={"access_token": token, "limit": args.l, "fields":"note,image"})
data = json.loads(response.text)

html = """
      <html>
         <head>
          <style>
#wrapper {{
	width: 90%;
	max-width: 1100px;
	min-width: 800px;
	margin: 50px auto;
}}

#columns {{
	-webkit-column-count: 3;
	-webkit-column-gap: 10px;
	-webkit-column-fill: auto;
	-moz-column-count: 3;
	-moz-column-gap: 10px;
	-moz-column-fill: auto;
	column-count: 3;
	column-gap: 15px;
	column-fill: auto;
}}

.pin {{
	display: inline-block;
	background: #FEFEFE;
	border: 2px solid #FAFAFA;
	box-shadow: 0 1px 2px rgba(34, 25, 25, 0.4);
	margin: 0 2px 15px;
	-webkit-column-break-inside: avoid;
	-moz-column-break-inside: avoid;
	column-break-inside: avoid;
	padding: 15px;
	padding-bottom: 5px;
	background: -webkit-linear-gradient(45deg, #FFF, #F9F9F9);
	opacity: 1;
	-webkit-transition: all .2s ease;
	-moz-transition: all .2s ease;
	-o-transition: all .2s ease;
	transition: all .2s ease;
}}

.pin img {{
	width: 100%;
	margin-bottom: 10px;
}}

.pin p {{
	font: 12px/18px Arial, sans-serif;
	color: #333;
	border-top: 1px solid #ccc;
	padding-top: 10px;
	margin: 0;
}}

@media (min-width: 960px) {{
	#columns {{
		-webkit-column-count: 4;
		-moz-column-count: 4;
		column-count: 4;
	}}
}}

@media (min-width: 1100px) {{
	#columns {{
		-webkit-column-count: 5;
		-moz-column-count: 5;
		column-count: 5;
	}}
}}

#columns:hover .pin:not(:hover) {{
	opacity: 0.4;
  }}
        </style>
      </head>
      <body>
        <div id="wrapper">
	  <div id="columns">
               {}
	  </div>
      </div>
      </body>
    </html>
"""


images, c = "", 0
if args.i == 1:
    for im in data["data"]:
        link = im["image"]["original"]["url"]
        fname = "image{}.jpg".format(c)
        if not os.path.exists(args.o):
            os.makedirs(args.o)
        with open(args.o+"/"+fname, "wb") as f:
            res = requests.get(link,stream=True)
            total_length = res.headers.get("content-length")
            if total_length is None:
                f.write(res.content)
                c+=1
            else:
                dl, total_length = 0, int(total_length)
                for d in res.iter_content():
                    dl += len(d)
                    f.write(d)
                    done = int(30 * dl / total_length)
                    sys.stdout.write("\r[%s%s] %%%-6.2f %s %s" %
                                     ("■" * done,
                                      ' ' * (31 - done),
                                      100 * dl / total_length,
                                      colors.OKGREEN + "Downloading... " + colors.ENDC,
                                      colors.WARNING + fname + colors.ENDC))
                    sys.stdout.flush()
                c += 1
        print("")
    for i in range(0,c):
        images += """
        <div class="pin">
         <a href="{0}" target="blank"><img src="{0}" /></a>
            {1}
        </div>
        """.format("image"+str(i)+".jpg","")
else:
    for dat in data["data"]:
        img = str(dat["image"]["original"]["url"])
        desc = "<p>"+str(dat["note"].encode("utf8"))+"</p>" if args.d == 0 else ""
        images += """
        <div class="pin">
         <a href="{0}" target="blank"><img src="{0}" /></a>
          {1}
        </div>
        """.format(img, desc)

html = html.format(images)

path = "%s/%s.html" % (args.o,args.o)
with open(path, "wb") as f:
    f.write(html.encode("utf-16"))

print("\nGallery created with %s pictures" % len(data["data"]))
