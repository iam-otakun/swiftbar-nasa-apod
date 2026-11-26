#!/usr/bin/env python3

# Copyright 2019 Jacob Vossen 

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# <xbar.title>NASA 每日一图 / NASA APOD</xbar.title>
# <xbar.version>v1.9.2</xbar.version>
# v1.9.2: image extraction rewritten for NASA's current page design — the day's picture now comes from the hero figure in front of the title (its link is the original file); the old image-article match and the og:image fallback are gone (on most days they silently substituted the site's template image for the real picture). Video days are now recognised as videos: the menu offers the video link and nothing is archived.
# v1.9.1: date fix — NASA's redesigned page broke the old extraction (the first image-article slug and the "YYYY Month DD" text on the page both belong to the PREVIOUS entry's navigation, so every picture was stamped one day early). The date now comes from the byline under the entry's own title ("November 25, 2026"), with America/New_York "today" as the fallback (APOD days roll over at midnight ET, not local time)
# v1.9.0: fetch hardening on par with the Windows version — browser User-Agent and timeouts on every request, the page fetch itself is inside the error path now (a failed fetch shows the error menu instead of dying), and a diagnostic log is kept at ~/.nasa-apod.log
# v1.8.2: About submenu (unified About: Version, Idea: Otakun, Coding: Dash, GitHub Repository link)
# <xbar.author>Otakun and Dash</xbar.author>
# <xbar.author.github>iam-otakun</xbar.author.github>
# <xbar.desc>Shows the NASA Astronomy Picture of the Day in the menu bar and archives the original picture every day (archive folder configurable in the dropdown menu; UI language follows the system). 在菜单栏显示 NASA 每日一图，并把原图按日期归档（归档文件夹可在下拉菜单里设置；界面语言跟随系统）。Based on Jake Vossen's plugin, revived after NASA redesigned the APOD page. 基于 Jake Vossen 的插件，因 NASA 改版 APOD 页面而复活并重写取图逻辑。</xbar.desc>
# <xbar.dependencies>python3,pillow</xbar.dependencies>
# <xbar.abouturl>https://github.com/iam-otakun/swiftbar-nasa-apod</xbar.abouturl>



# May need to pip(3) install pillow
# May need to install certificates: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
import base64
import html
import urllib.request
from PIL import Image
import io
from io import BytesIO
import os
import sys
import subprocess

# ---------- 归档设置：下拉菜单里的「归档：…」子菜单会带参数再次调用本脚本 ----------
_CONF = os.path.expanduser('~/.nasa-apod.conf')
_STATE = os.path.expanduser('~/.nasa-apod.state')

# ---------- 界面语言：跟随系统（中文系统用中文，其它语言用英文）；环境变量 APOD_LANG 可覆盖 ----------
def _detect_zh():
    ov = os.environ.get('APOD_LANG', '').strip().lower()
    if ov.startswith('zh'):
        return True
    if ov:
        return False
    try:
        langs = subprocess.run(['defaults', 'read', '-g', 'AppleLanguages'], capture_output=True, text=True, timeout=5).stdout
        q1 = langs.find('"')
        q2 = langs.find('"', q1 + 1) if q1 >= 0 else -1
        if q1 >= 0 and q2 > q1:
            return langs[q1 + 1:q2].lower().startswith('zh')
        loc = subprocess.run(['defaults', 'read', '-g', 'AppleLocale'], capture_output=True, text=True, timeout=5).stdout.strip().lower()
        return loc.startswith('zh')
    except Exception:
        return False

_ZH = _detect_zh()

if _ZH:
    S = {
        'setup_title': '归档设置',
        'first_msg': '欢迎使用 NASA 每日一图。',
        'first_body': '每天的原图会归档到下面的文件夹：可以直接改，也可以点「选择文件夹…」挑选；清空则不归档。点「取消」将使用默认目录，之后随时可在下拉菜单的「归档」里更改。',
        'cancel': '取消', 'ok': '确定', 'save': '保存', 'choose_btn': '选择文件夹…',
        'choose_prompt': '选择归档 NASA 每日图片的文件夹',
        'input_msg': '输入归档目录（清空 = 不归档）',
        'archive': '归档', 'colon': '：', 'off': '已关闭',
        'm_choose': '选择文件夹…', 'm_input': '输入路径…', 'm_disable': '关闭归档', 'm_default': '恢复默认目录', 'm_refresh': '刷新', 'm_about': '关于',
        'msg_uptodate': 'Up to date!', 'msg_updated': 'Update successfully',
        'error': '未能完成请求：今天的每日一图可能是视频，或缺少必要的依赖（Pillow）',
        'm_watch': '观看今日视频', 'm_videonote': '今日条目是视频',
    }
else:
    S = {
        'setup_title': 'Archive Settings',
        'first_msg': 'Welcome to NASA APOD.',
        'first_body': 'Each day\'s original picture is archived to the folder below. Edit it, or click "Choose Folder..." to pick one; clear it to disable archiving. "Cancel" uses the default folder. You can change this any time in the dropdown\'s Archive submenu.',
        'cancel': 'Cancel', 'ok': 'OK', 'save': 'Save', 'choose_btn': 'Choose Folder...',
        'choose_prompt': 'Choose a folder for archiving the NASA picture of the day',
        'input_msg': 'Archive folder (clear it to disable archiving)',
        'archive': 'Archive', 'colon': ': ', 'off': 'Off',
        'm_choose': 'Choose Folder...', 'm_input': 'Type a Path...', 'm_disable': 'Turn Off Archiving', 'm_default': 'Restore Default Folder', 'm_refresh': 'Refresh', 'm_about': 'About',
        'msg_uptodate': 'Up to date!', 'msg_updated': 'Update successfully',
        'error': 'Could not complete the request: today\'s picture may be a video, or a dependency (Pillow) is missing.',
        'm_watch': 'Watch Today\'s Video', 'm_videonote': 'Today\'s entry is a video',
    }

_VER = 'v1.9.2'
_UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
_LOG = os.path.expanduser('~/.nasa-apod.log')

class _ApodDone(Exception):
    # 主流程里提前收尾（视频日、抓取失败）时用它跳出大 try，
    # 不能用 sys.exit——会被主流程的裸 except 当成失败再兜一次。
    pass

def _log(msg):
    # 与 Windows 版的 NasaApod.log 同义：取图成败都留一行，方便事后定位
    try:
        import datetime as _dt
        with open(_LOG, 'a') as _lf:
            _lf.write('%s %s\n' % (_dt.datetime.now().isoformat(timespec='seconds'), msg))
    except Exception:
        pass

def _fetch(url, timeout):
    return urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': _UA}), timeout=timeout).read()

def _page_date(page):
    # 条目日期取标题附近署名行的「Month D, YYYY」；整页第一个 image-article
    # 链接与「YYYY Month DD」字样都是上一篇的导航信息，用了就会差一天。
    import re as _re3
    _months3 = {'January':1,'February':2,'March':3,'April':4,'May':5,'June':6,'July':7,'August':8,'September':9,'October':10,'November':11,'December':12}
    _tm3 = _re3.search(r'display-48 margin-top-0 margin-bottom-3">([^<]+)<', page)
    _seg = page[max(0, _tm3.start() - 4000):_tm3.start() + 8000] if _tm3 else page
    _md = _re3.search(r'(January|February|March|April|May|June|July|August|September|October|November|December) (\d{1,2}), (\d{4})', _seg)
    if _md:
        return '%s-%02d-%02d' % (_md.group(3), _months3[_md.group(1)], int(_md.group(2)))
    return None

def _hero(page):
    # 当日条目的主媒体挂在标题前的图版块里（hds-media-inner figure）：
    # 图日子里 figure 的链接就是原图、<img> 是渲染图；视频日子里是 <video>。
    # 页面前部的 image-article 链接全是导航/相关条目，og:image 是站点模板图，
    # 两者都不能当当日图（v1.9.1 及以前在这里栽过：多数日子存下的是模板图）。
    import re as _re4
    import html as _html4
    _tm4 = _re4.search(r'display-48 margin-top-0 margin-bottom-3">([^<]+)<', page)
    if not _tm4:
        return None
    _win = page[max(0, _tm4.start() - 30000):_tm4.start()]
    _fi = _win.rfind('<figure class="hds-media-inner')
    if _fi >= 0:
        _seg = _win[_fi:_fi + 6000]
        _am = _re4.search(r'<a[^>]+href="([^"]+)"', _seg)
        _im = _re4.search(r'<img[^>]+src="([^"]+)"', _seg)
        if _im:
            _disp = _html4.unescape(_im.group(1))
            _href = _html4.unescape(_am.group(1)) if _am else ''
            if '/content/dam/' in _href or _re4.search(r'\.(jpg|jpeg|png)$', _href.split('?')[0], _re4.I):
                _orig = _href
            else:
                _orig = _re4.sub(r'dynamicimage/assets/science/', 'content/dam/science/', _disp).split('?')[0]
            return {'image_url': _disp, 'archive_url': _orig}
    _vi = _win.rfind('<video')
    if _vi >= 0:
        _seg = _win[_vi:_vi + 4000]
        _sm = _re4.search(r'<source[^>]+src="([^"]+)"', _seg)
        if _sm:
            return {'video_url': _html4.unescape(_sm.group(1))}
    return None

def _fail():
    print(S['error'])
    print(S['m_refresh'] + ' | refresh=true')
    print('---')
    print(S['m_about'])
    print('--Version ' + _VER)
    print('--Idea: Otakun')
    print('--Coding: Dash')
    print('--GitHub Repository | href=https://github.com/iam-otakun/swiftbar-nasa-apod')

def _conf_value():
    # 未设过返回 None；空字符串表示关闭归档；否则返回用户填的路径
    try:
        with open(_CONF) as _f:
            for _line in _f:
                if _line.startswith('ARCHIVE_DIR='):
                    return _line.split('=', 1)[1].strip()
    except Exception:
        pass
    return None

def _effective_dir():
    v = _conf_value()
    if v is None:
        return os.path.expanduser('~/Pictures/NASA-Apod')
    if v == '':
        return None
    return os.path.expanduser(v)

def _save_conf(value):
    with open(_CONF, 'w') as _f:
        _f.write('ARCHIVE_DIR=' + value + '\n')

def _osa(script):
    try:
        out = subprocess.run(['osascript', '-e', script], capture_output=True, text=True, timeout=180)
        if out.returncode == 0:
            return out.stdout.strip()
    except Exception:
        pass
    return None

def _as_escape(s):
    return s.replace('\\', '\\\\').replace('"', '\\"')

if len(sys.argv) > 1:
    _act = sys.argv[1]
    if _act == 'choose-dir':
        _p = _osa('POSIX path of (choose folder with prompt "' + _as_escape(S['choose_prompt']) + '")')
        if _p:
            _save_conf(_p.rstrip('/') or '/')
    elif _act == 'input-dir':
        _cur = _effective_dir() or ''
        _p = _osa('text returned of (display dialog "' + _as_escape(S['input_msg']) + '" default answer "' + _as_escape(_cur) + '" buttons {"' + _as_escape(S['cancel']) + '", "' + _as_escape(S['save']) + '"} default button "' + _as_escape(S['save']) + '")')
        if _p is not None:
            _save_conf(_p.strip())
    elif _act == 'refresh':
        # 手动刷新：先比对「上次显示的日期」与 NASA 最新日期，给一句提示，再由 refresh=true 重跑主流程
        import re as _re2
        _prev = None
        try:
            with open(_STATE) as _f:
                _prev = _f.read().strip() or None
        except Exception:
            pass
        _new = None
        try:
            _html = str(_fetch('https://apod.nasa.gov/apod/', 30))
            _new = _page_date(_html)
        except Exception:
            _new = None
        if _new is None:
            _msg = S['error']
        elif _prev is not None and _new <= _prev:
            _msg = S['msg_uptodate']
        else:
            _msg = S['msg_updated']
        _osa('display dialog "' + _as_escape(_msg) + '" buttons {"' + _as_escape(S['ok']) + '"} default button "' + _as_escape(S['ok']) + '" with title "NASA APOD" giving up after 3')
    elif _act == 'disable':
        _save_conf('')
    elif _act == 'default':
        try:
            os.remove(_CONF)
        except Exception:
            pass
    sys.exit(0)

# with open("/tmp/temp.jpg", "rb") as image_file:
    # encoded_string = str(base64.b64encode(image_file.read()))[2:][:-1]
# print(encoded_string)
# 首次运行（尚无配置文件）：先给一次归档目录设置入口，预填默认路径，
# 不改就直接点「确定」；点「取消」同样按默认走，之后不再打扰（菜单里随时可改）。
if not os.path.exists(_CONF):
    _script = (
        'set curPath to "~/Pictures/NASA-Apod"\nrepeat\n'
        '\tset dlg to display dialog "' + _as_escape(S['first_msg']) + '" & return & return & "' + _as_escape(S['first_body']) + '" default answer curPath buttons {"' + _as_escape(S['cancel']) + '", "' + _as_escape(S['choose_btn']) + '", "' + _as_escape(S['ok']) + '"} default button "' + _as_escape(S['ok']) + '" with title "' + _as_escape(S['setup_title']) + '"\n'
        '\tset btn to button returned of dlg\n'
        '\tif btn is "' + _as_escape(S['ok']) + '" then\n'
        '\t\treturn text returned of dlg\n'
        '\telse if btn is "' + _as_escape(S['cancel']) + '" then\n'
        '\t\treturn "~/Pictures/NASA-Apod"\n'
        '\telse\n'
        '\t\ttry\n'
        '\t\t\tset chosen to choose folder with prompt "' + _as_escape(S['choose_prompt']) + '"\n'
        '\t\t\tset curPath to POSIX path of chosen\n'
        '\t\t\tif curPath ends with "/" then set curPath to text 1 thru -2 of curPath\n'
        '\t\tend try\n'
        '\tend if\n'
        'end repeat'
    )
    _first = _osa(_script)
    if _first is None:
        _save_conf('~/Pictures/NASA-Apod')
    else:
        _save_conf(_first.strip())
print('🔭') # The telescope emoji is here, if your text editor does not render it
print('---')
try:
    r = str(_fetch('https://apod.nasa.gov/apod/', 30))
except Exception as _e:
    _log('page fetch failed: %r' % (_e,))
    _fail()
    sys.exit(0)
# print(r)
# print(r.find('.jpg'))
try:
    import re
    # 当日媒体以标题前的图版块为准（见 _hero）；日期以标题署名行为准。
    apod_date = _page_date(r)
    _hero_info = _hero(r)
    if _hero_info is not None and not _hero_info.get('image_url') and _hero_info.get('video_url'):
        # 视频日：给标题与观看入口，不归档、更不拿模板图冒充当日图
        import datetime as _dtv
        if apod_date:
            _dv = apod_date
        else:
            try:
                import zoneinfo as _zi
                _dv = _dtv.datetime.now(_zi.ZoneInfo('America/New_York')).date().isoformat()
            except Exception:
                _dv = _dtv.date.today().isoformat()
        try:
            with open(_STATE, 'w') as _sfv:
                _sfv.write(_dv + '\n')
        except Exception:
            pass
        _log('displaying APOD date ' + _dv + ' (video)')
        _tmv = re.search(r'class="display-48 margin-top-0 margin-bottom-3">([^<]+)<', r)
        if _tmv:
            print(html.unescape(_tmv.group(1).strip()) + ' | href=https://apod.nasa.gov/apod/')
        print(S['m_videonote'])
        print(S['m_watch'] + ' | href=' + _hero_info['video_url'])
        _selfv = os.path.abspath(sys.argv[0])
        print(S['m_refresh'] + ' | bash="' + _selfv + '" param0=refresh terminal=false refresh=true')
        print('---')
        _dir_nowv = _effective_dir()
        print(S['archive'] + S['colon'] + (_dir_nowv if _dir_nowv else S['off']))
        print('--' + S['m_choose'] + ' | bash="' + _selfv + '" param0=choose-dir terminal=false refresh=true')
        print('--' + S['m_input'] + ' | bash="' + _selfv + '" param0=input-dir terminal=false refresh=true')
        print('--' + S['m_disable'] + ' | bash="' + _selfv + '" param0=disable terminal=false refresh=true')
        print('--' + S['m_default'] + ' | bash="' + _selfv + '" param0=default terminal=false refresh=true')
        print('---')
        print(S['m_about'])
        print('--Version ' + _VER)
        print('--Idea: Otakun')
        print('--Coding: Dash')
        print('--GitHub Repository | href=https://github.com/iam-otakun/swiftbar-nasa-apod')
        raise _ApodDone
    if _hero_info is None or not _hero_info.get('image_url'):
        _log('hero extraction failed')
        _fail()
        raise _ApodDone
    image_url = _hero_info['image_url']
    archive_url = _hero_info.get('archive_url')
    image_path = io.BytesIO(_fetch(image_url, 60))

    # 保存原图到归档目录（按 APOD 日期命名，已有则跳过；目录由 ARCHIVE_DIR 决定，见下）
    _saved_path = None
    try:
        import os, re as _re, datetime
        if apod_date:
            _d = apod_date
        else:
            # 兜底：APOD 的一天按美东午夜翻页，本机日期（东八区）会快一天
            try:
                import zoneinfo
                _d = datetime.datetime.now(zoneinfo.ZoneInfo('America/New_York')).date().isoformat()
            except Exception:
                _d = datetime.date.today().isoformat()
        # 记录本次显示的 APOD 日期，供「刷新」比对有没有新图（v1.8）
        try:
            with open(_STATE, 'w') as _sf:
                _sf.write(_d + '\n')
        except Exception:
            pass
        _log('displaying APOD date ' + _d)
        # 归档目录：~/.nasa-apod.conf 里的 ARCHIVE_DIR（下拉菜单的归档设置可改）；
        # 没设过用默认 ~/Pictures/NASA-Apod，设为空则不归档。
        _dir = _effective_dir()
        if _dir:
            os.makedirs(_dir, exist_ok=True)
            _tm2 = _re.search(r'class="display-48 margin-top-0 margin-bottom-3">([^<]+)<', r)
            _title = html.unescape(_tm2.group(1).strip()) if _tm2 else ''
            _title = _title.replace('/', '-').replace(':', '-').replace(chr(92), '-').strip()
            _path = os.path.join(_dir, (_d + ' ' + _title + '.jpg') if _title else (_d + '.jpg'))
            _saved_path = _path
            if not os.path.exists(_path):
                _data = None
                if archive_url:
                    try:
                        _data = _fetch(archive_url, 60)
                    except Exception:
                        _data = None
                with open(_path, 'wb') as _f:
                    _f.write(_data if _data else image_path.getvalue())
    except Exception:
        pass
    pillow_image = Image.open(image_path)
    # NASA 交付的图可能自带纯黑边（竖幅照片塞进宽画布）：显示前裁掉四周整行/整列
    # 纯黑的边，让菜单宽度跟照片本身走；归档存的是原始文件，不受影响。
    try:
        _g = pillow_image.convert('L')
        _w, _h = _g.size
        _px = _g.load()
        def _col_black(x):
            return all(_px[x, y] <= 10 for y in range(0, _h, 7))
        def _row_black(y):
            return all(_px[x, y] <= 10 for x in range(0, _w, 7))
        _l = 0
        while _l < _w and _col_black(_l): _l += 1
        _r = 0
        while _r < _w and _col_black(_w - 1 - _r): _r += 1
        _t = 0
        while _t < _h and _row_black(_t): _t += 1
        _b = 0
        while _b < _h and _row_black(_h - 1 - _b): _b += 1
        if (_l + _r) < _w and (_t + _b) < _h and (_l or _r or _t or _b):
            pillow_image = pillow_image.crop((_l, _t, _w - _r, _h - _b))
    except Exception:
        pass
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
        # 标题可点击：点一下在 Finder 里打开归档文件夹并选中这张图
        if _saved_path:
            print(html.unescape(_tm.group(1).strip()) + ' | bash="/usr/bin/open" param0=-R param1="' + _saved_path + '" terminal=false')
        else:
            print(html.unescape(_tm.group(1).strip()))
    # 手动刷新（v1.8）：点一下先比对日期给提示（Up to date! / Update successfully），随后重跑拉最新一图
    _self = os.path.abspath(sys.argv[0])
    print(S['m_refresh'] + ' | bash="' + _self + '" param0=refresh terminal=false refresh=true')
    # 归档设置子菜单：父项显示当前归档去向，子项带参数回调本脚本改设置
    _dir_now = _effective_dir()
    print('---')
    print(S['archive'] + S['colon'] + (_dir_now if _dir_now else S['off']))
    print('--' + S['m_choose'] + ' | bash="' + _self + '" param0=choose-dir terminal=false refresh=true')
    print('--' + S['m_input'] + ' | bash="' + _self + '" param0=input-dir terminal=false refresh=true')
    print('--' + S['m_disable'] + ' | bash="' + _self + '" param0=disable terminal=false refresh=true')
    print('--' + S['m_default'] + ' | bash="' + _self + '" param0=default terminal=false refresh=true')
    # 统一 About 子菜单：Version、Idea: Otakun、Coding: Dash、GitHub Repository 链接
    print('---')
    print(S['m_about'])
    print('--Version ' + _VER)
    print('--Idea: Otakun')
    print('--Coding: Dash')
    print('--GitHub Repository | href=https://github.com/iam-otakun/swiftbar-nasa-apod')
except _ApodDone:
    pass
except:
    _log('main flow failed: %r' % (sys.exc_info()[1],))
    _fail()
