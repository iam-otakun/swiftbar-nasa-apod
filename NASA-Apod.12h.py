#!/usr/bin/env python3

# Copyright 2019 Jacob Vossen 

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# <xbar.title>NASA Picture of the Day</xbar.title>
# <xbar.version>v1.0</xbar.version>
# <xbar.author>Jake Vossen</xbar.author>
# <xbar.author.github>jakevossen5</xbar.author.github>
# <xbar.desc>Displays a the NASA picture of the day</xbar.desc>
# <xbar.image>https://raw.githubusercontent.com/jakevossen5/apodbitbar/master/example.png</xbar.image>
# <xbar.dependencies>python3,pillow</xbar.dependencies>
# <xbar.abouturl>https://github.com/jakevossen5/apodbitbar/tree/master</xbar.abouturl>



# May need to pip(3) install pillow
# May need to install certificates: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
import base64
import urllib.request
from PIL import Image
import io
from io import BytesIO

# with open("/tmp/temp.jpg", "rb") as image_file:
    # encoded_string = str(base64.b64encode(image_file.read()))[2:][:-1]
# print(encoded_string)
print('🔭') # The telescope emoji is here, if your text editor does not render it
print('---')
url = 'https://apod.nasa.gov/apod/'
req = urllib.request.Request(url)
# try:
r = str(urllib.request.urlopen(req).read())
# print(r)
# print(r.find('.jpg'))
try:
    import re
    m = re.search(r'property="og:image" content="([^"]+)"', r)
    if m:
        image_url = m.group(1)
    else:
        image_url = ""
        for i in range(r.find('.jpg'), 0, -1):
            if r[i] != '"':
                image_url = r[i] + image_url
            else:
                break
        image_url = image_url + "jpg"
        image_url = "https://apod.nasa.gov/apod/" + image_url


    image_req = urllib.request.Request(image_url)

    image_path = io.BytesIO(urllib.request.urlopen(image_req).read())

    # 保存原图到 ~/Pictures/NASA-Apod/（按 APOD 日期命名，已有则跳过）
    try:
        import os, re as _re, datetime
        _months = {'January':1,'February':2,'March':3,'April':4,'May':5,'June':6,'July':7,'August':8,'September':9,'October':10,'November':11,'December':12}
        _m = _re.search(r'(\d{4}) (January|February|March|April|May|June|July|August|September|October|November|December) (\d{1,2})', r)
        if _m:
            _d = '%s-%02d-%02d' % (_m.group(1), _months[_m.group(2)], int(_m.group(3)))
        else:
            _d = datetime.date.today().isoformat()
        _dir = os.path.expanduser('~/Pictures/NASA-Apod')
        os.makedirs(_dir, exist_ok=True)
        _tm2 = _re.search(r'class="display-48 margin-top-0 margin-bottom-3">([^<]+)<', r)
        _title = _tm2.group(1).strip() if _tm2 else ''
        _title = _title.replace('/', '-').replace(':', '-').replace(chr(92), '-').strip()
        _path = os.path.join(_dir, (_d + ' ' + _title + '.jpg') if _title else (_d + '.jpg'))
        if not os.path.exists(_path):
            with open(_path, 'wb') as _f:
                _f.write(image_path.getvalue())
    except Exception:
        pass
    pillow_image = Image.open(image_path)
    # pillow_image.show()
    maxsize = (720, 720)

    pillow_image.thumbnail(maxsize)
    buff = BytesIO()
    pillow_image.save(buff, format="JPEG")
    encoded_string = base64.b64encode(buff.getvalue())
    # base64_data = base64.b64encode(binary_data)


    # encoded_string = ""
    # except:
    # print("There was an error, most likely with SSL certificates. Click me to fix |href=https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org")
    
    # print(r)
    # image_string = "image=" + encoded_string
    print("| href=https://apod.nasa.gov/apod/ image=" +  str(encoded_string)[2:][:-1])

    _tm = re.search(r'class="display-48 margin-top-0 margin-bottom-3">([^<]+)<', r)
    if _tm:
        print(_tm.group(1).strip())
except:
    print("Could not complete the request. Either the picture of the day is a video, or you do not have the proper dependencies installed")
