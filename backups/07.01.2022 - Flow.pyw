from tkinter import*
from tkinter.messagebox import*
from tkinter.simpledialog import*
from tkinter.filedialog import*
from tkinter.ttk import*
from functools import partial
from subprocess import Popen, call, check_call
from time import sleep
from datetime import datetime
from ast import literal_eval
from copy import deepcopy
from _thread import start_new_thread
import json, string, keyword, shutil
import os, sys

"""

** Flow **
A Powerful Visual Programming Language
Created by Professor Dragon


** How to configure Flow as the default program for .flow files **

Run these commands in command prompt:
assoc .flow=Flow.File
ftype Flow.File=pyw "(this file)" "%1"

"""

# {name: Display name, symbol: Letter(s) shown in sidebar, color: Color of blocks, blocks: Block id list}
categories = []
category = 0
# id: {text: Display text, args: [[Type, Display name], ...], scaffold: Code scaffold, postscaffold: Code scaffold that goes on the next line(s) for extra configuring, help: Help when block is right-clicked}
# Argument types:
# in = Text/generic input
# ni = Number/generic input (same as in but 0 is the default value)
# vi = Variable input
# si = Script input
# c = C-block (does not need display name) - multiple c arguments not supported!
# oi = Other input
blocks = {}
block = []
# {name: Display name, scripts: Scripts to be added}
presets = []
argdefault = {"c": [], "in": '""', "ni": "0", "si": "", "vi": "", "oi": ""}
setblocks = ["var_set", "var_increment", "array_replace", "dict_set"]
builtins = []
data = []
scripts = [{"name": "main", "blocks": [["script_start"]]}]
script = 0
modules = []
functionalities = {"console": True, "autoinstall": True, "windows": True, "dialogs": True, "modernwindows": True, "random": True, "time": True, "json": True,
                   "keyboard": False, "playsound": False, "tts": False, "translate": False}
# id: {name: Display name, imports: Import code, modules: Module names for auto-install, functions: Define scripts, init: Initialisation code, globals: Global variables}
funcscaffold = {"console": {"name": "Console"},
                "autoinstall": {"name": "Auto-install modules", "imports": "autoinstall = []"},
                "windows": {"name": "Windows + canvas", "imports": "from tkinter import*", "functions": """\
def _tk_create_rect(x, y, w, h, **kwargs):
    return tkvars['canvas'].create_rectangle(x, y, x+w, y+h, **kwargs)
def _tk_create_oval(x, y, w, h, **kwargs):
    return tkvars['canvas'].create_oval(x, y, x+w, y+h, **kwargs)
def _tk_find_overlap(obj):
    bbox = tkvars['canvas'].bbox(obj)
    return tkvars['canvas'].find_overlapping(*bbox)[1:]
def _tk_set_position(obj, x, y):
    bbox = tkvars['canvas'].bbox(obj)
    return tkvars['canvas'].move(obj, x-bbox[0], y-bbox[1])
def _tk_button(btn, release=False):
    return '<Button%s-%d>'%('Release' if release else '', {'left': 1, 'right': 3, 'middle': 2}[btn.lower()])
def _tk_packed(wid):
    wid.pack()
    return wid""", "init": """\
tkvars = {'window': None, 'canvas': None, 'fill': 'white', 'outline': 'black', 'outlinewidth': 1, 'font': 'Verdana 20'}""", "globals": ["tkvars"]},
                "modernwindows": {"name": "Modern windows", "imports": "from tkinter.ttk import*"},
                "dialogs": {"name": "Dialogs", "imports": """\
import tkinter.messagebox as tkmb
import tkinter.simpledialog as tksd
import tkinter.filedialog as tkfd"""},
                "random": {"name": "Random values + shuffle", "imports": "import random"},
                "time": {"name": "Wait seconds", "imports": "import time"},
                "json": {"name": "JSON", "imports": "import json"},
                "keyboard": {"name": "Keyboard + mouse", "imports": "import keyboard\nimport mouse", "modules": ["keyboard", "mouse"]},
                "playsound": {"name": "Play sound", "imports": "from playsound import playsound", "modules": ["playsound"]},
                "tts": {"name": "Text-to-speech", "imports": "import pyttsx3", "modules": ["pyttsx3"], "functions": """\
def _tts_speak(text, fn):
    if fn: ttseng.say(text)
    else: ttseng.save_to_file(text, fn)
    ttseng.runAndWait()""", "init": """\
ttseng = pyttsx3.init()
ttsvoices = ttseng.getProperty("voices")""", "globals": ["ttseng"]},
                "translate": {"name": "Translate", "imports": "import googletrans", "modules": ["googletrans"],
                              "init": "transeng = googletrans.Translator()", "globals": ["transeng"]}
                }
extpaths = []
font, fontbig, fontsize, fonty = "Tahoma", "Verdana", 0, 0
blocksize = 11
saveloc = ""
mouseoncanvas = False
scrollpos = {"blockbar": 0, "blockbarmin": 0, "blockbarmax": 0,
             "canvas": 0, "canvasmin": 0, "canvasmax": 0, "canvasx": 0,
             "scriptbar": 0, "scriptbarmin": 0, "scriptbarmax": 0}
scriptscrollpos = {}
scrollspeed = 40
dodemo = False
hiddenpanes = {"blockbar": False, "canvas": False, "scriptbar": False}
backpack = {}
previewmode = 1
argcolor, varargcolor, scriptargcolor = "limegreen", "darkorange", "peru"
redcompile = False
ignorewarnings = False
shortmode = False
lastvar = None
dragging = []
lastfield = None
btnmode = "ButtonRelease"
title = "Flow"
temploc = os.path.expandvars("%localappdata%\\Temp\\Flow")
if not os.path.isdir(temploc): os.mkdir(temploc)
#sys.stderr = open(os.path.join(temploc, "flow.log"), "w")

def varstojson(*names):
    j = {}
    for n in names:
        j[n] = eval(n, globals())
    return j
def jsontovars(json, merge=False):
    for k, v in json.items():
        if merge: mergedict(eval(k), v)
        else: exec(f"{k} = {repr(v)}", globals())
def filtname(n, non=None):
    if len(n) == 0 and non == None: return ""
    f = ("".join([c for c in n if c in string.ascii_letters+string.digits+"_"])).lstrip(string.digits+"_")
    return f if len(f) > 0 else ("_" if non == None else non)
def mergedict(d, d2):
    if type(d2) == dict:
        for k, v in d2.items():
            if k in d and type(d[k]) == dict:
                mergedict(d[k], d2[k])
            elif not k in d:
                d[k] = d2[k]
    elif type(d2) == list:
        d.extend(d2)
def getblock(b):
    return blocks.get(b, {"text": "Unknown block", "short": "Unknown", "args": [], "scaffold": "None", "help": f"Unknown block: {b}. Returns none."})
def drawblock(b, x, y, cat=None, menu=False, absolute=False, preview=None, color=None, notext=False, tags=None):
    if not cat: cat = blockcategory(b)
    textcol = "black"
    if not color: color = cat["color"]
    if color == "system": color, textcol = "indigo", "white"
    elif color == "error": color, textcol = "red", "white"
    if menu:
        widget = blockbar
        yscroll, xscroll = scrollpos["blockbar"], 0
    else:
        widget = canvas
        yscroll, xscroll = scrollpos["canvas"], scrollpos["canvasx"]
    if absolute: yscroll, xscroll = 0, 0
    blockinfo = getblock(b)
    ltz = y+yscroll < -blocksize-20
    if not ltz or notext:
        if notext: rect = widget.create_rectangle(x+xscroll-8, y+yscroll-6, x+xscroll+40, y+yscroll+12, fill=color, tags=tags)
        else: rect = widget.create_rectangle(0, 0, 0, 0, fill=color, tags=tags)
    if shortmode and "short" in blockinfo: disp = blockinfo["short"]
    else: disp = blockinfo["text"]
    if preview != None: disp = preview
    if len(disp) > 100: disp = disp[:98]+".."
    if notext: return [rect, widget.bbox(rect), blockinfo]
    text = widget.create_text(x+xscroll, y+fonty+yscroll, text=disp, anchor=NW, font=f"{font} {blocksize+fontsize}", fill=textcol, tags=tags)
    bbox = widget.bbox(text)
    if ltz:
        return [[text], bbox, blockinfo]
    else:
        widget.coords(rect, bbox[0]-8, bbox[1]-6-fonty, bbox[2]+10, bbox[3]+7-fonty)
        return [[rect, text], bbox, blockinfo]
def updateall(e=None):
    updateblockbar(e=e)
    updatescriptbar(e=e)
    updatecanvas(e=e)
def updateblockbar(e=None):
    global scrollpos
    blockbar.delete("all")
    if hiddenpanes["blockbar"]:
        blockbar.create_rectangle(0, 0, blockbar.winfo_width(), blockbar.winfo_height(), fill="black", stipple="gray50", outline="")
        return
    blockbar.create_line(50, 0, 50, blockbar.winfo_height())
    x, y = 25, 12+scrollpos["blockbar"]
    for i, c in enumerate(categories):
        if len(c["symbol"]) < 1: continue
        cc = category == i
        rect = blockbar.create_rectangle(x-15, y-3, x+15, y+27, fill=("black" if cc else c["color"]), outline=(c["color"] if cc else "black"), width=(2 if cc else 1))
        s = {1: 16, 2: 14}.get(len(c["symbol"]), 22-4*len(c["symbol"]))
        text = blockbar.create_text(x, y+12+fonty/2-(1 if cc else 0), text=c["symbol"], anchor=CENTER, font=f"{font} {fontsize+s}"+(" bold" if cc else ""), fill=(c["color"] if cc else "black"))
        for obj in [rect, text]:
            blockbar.tag_bind(obj, "<Button-1>", partial(changecategory, i))
        y += 36
    oy = y-scrollpos["blockbar"]
    blockbar.create_text(60, 10+fonty+scrollpos["blockbar"], text=categories[category]["name"], anchor=NW, font=f"{fontbig} {fontsize+15}")
    x, y = 70, 50
    for i, b in enumerate(categories[category]["blocks"]):
        objs, bbox, info = drawblock(b, x, y, cat=categories[category], menu=True)
        for obj in objs:
            blockbar.tag_bind(obj, f"<{btnmode}-1>", partial(addblock, b))
            blockbar.tag_bind(obj, f"<Shift-{btnmode}-1>", partial(addblock, b, auto=True))
            blockbar.tag_bind(obj, f"<{btnmode}-2>", partial(addblock, b, auto=True))
            blockbar.tag_bind(obj, "<ButtonRelease-3>", partial(blockhelp, b))
        y += bbox[3]-bbox[1]+18
    scrollpos["blockbarmin"] = min(0, -max(y, oy)+blockbar.winfo_height())
def updatescriptbar(e=None):
    global scrollpos
    scriptbar.delete("all")
    if hiddenpanes["scriptbar"]:
        scriptbar.create_rectangle(0, 0, scriptbar.winfo_width(), scriptbar.winfo_height(), fill="black", stipple="gray50", outline="")
        return
    y = scrollpos["scriptbar"]
    playrect = scriptbar.create_rectangle(10, y+10, 46, y+40, fill="green")
    playtriangle = scriptbar.create_polygon(20, y+17, 36, y+25, 20, y+33, fill="lightgray")
    for obj in [playrect, playtriangle]:
        scriptbar.tag_bind(obj, f"<{btnmode}-1>", partial(play, 1))
    comprect = scriptbar.create_rectangle(55, y+10, 91, y+40, fill=("red" if redcompile else "royalblue"))
    if not redcompile:
        compcirc = scriptbar.create_oval(66, y+18, 80, y+32, fill="lightgray", outline="")
    for obj in [comprect] if redcompile else [comprect, compcirc]:
        scriptbar.tag_bind(obj, f"<{btnmode}-1>", partial(play, 0))
    y += 48
    for i, s in enumerate(scripts):
        rect = scriptbar.create_rectangle(10, y, 91, y+30, fill=("silver" if script == i else "white"))
        disp = s["name"]
        if len(disp) > 10:
            disp = disp[:8]+".."
        text = scriptbar.create_text(15, y+9+fonty, text=disp, anchor=NW, font=f"{font} {fontsize+8}")
        for obj in [rect, text]:
            scriptbar.tag_bind(obj, f"<Button-1>", partial(changescript, i))
            scriptbar.tag_bind(obj, "<ButtonRelease-3>", partial(scriptrightclick, i))
        y += 38
    plusrect = scriptbar.create_rectangle(10, y, 46, y+30, fill="white")
    plusver = scriptbar.create_line(27.5, y+5, 27.5, y+26, fill="gray", width=4)
    plushor = scriptbar.create_line(18, y+15, 38, y+15, fill="gray", width=4)
    for obj in [plusrect, plusver, plushor]:
        scriptbar.tag_bind(obj, f"<{btnmode}-1>", partial(newscript, False))
    downrect = scriptbar.create_rectangle(55, y, 91, y+30, fill="white")
    downline = scriptbar.create_line(65, y+11, 72.5, y+20, 81, y+11, fill="gray", width=4)
    for obj in [downrect, downline]:
        scriptbar.tag_bind(obj, f"<{btnmode}-1>", partial(newscript, True))
    scrollpos["scriptbarmin"] = min(0, -y+scrollpos["scriptbar"]-40+scriptbar.winfo_height())
def updatecanvas(e=None, mousemove=False):
    def blockchain(array, i, x, y, arg=None, indents=0):
        b = array[i]
        objs, bbox, info = drawblock(b[0], x, y)
        cat = blockcategory(b[0])
        fixed = cat["name"] == "System"
        ac, cc = 0, 0
        for a in info.get("args", []):
            if a[0] == "c": cc += 1
            else: ac += 1
        for obj in objs:
            if arg:
                canvas.tag_bind(obj, f"<{btnmode}-1>", partial(argclick, array, i, arg))
                canvas.tag_bind(obj, f"<Shift-{btnmode}-1>", partial(blockctrlclick, array, i, arg=True))
                canvas.tag_bind(obj, f"<{btnmode}-2>", partial(blockctrlclick, array, i, arg=True))
                canvas.tag_bind(obj, "<ButtonRelease-3>", partial(argrightclick, array, i, arg))
            else:
                kwargs = {"fixed": fixed, "cpart": (1 if cc > 0 else 0)}
                canvas.tag_bind(obj, f"<{btnmode}-1>", partial(blockclick, array, i, **kwargs))
                canvas.tag_bind(obj, f"<Shift-{btnmode}-1>", partial(blockctrlclick, array, i, **kwargs))
                canvas.tag_bind(obj, f"<{btnmode}-2>", partial(blockctrlclick, array, i, **kwargs))
                canvas.tag_bind(obj, "<ButtonRelease-3>", partial(blockrightclick, array, i, **kwargs))
        nx = bbox[2]+13
        if ac > 0 and y+scrollpos["canvas"] >= -blocksize-20:
            openb = canvas.create_text(nx, (bbox[1]+bbox[3])/2-1, text="(", anchor=W, font=f"{font} {blocksize+fontsize+4}")
            nx = canvas.bbox(openb)[2]+9
            for a, v in enumerate(info.get("args", [])):
                if v[0] == "c": continue
                if type(b[a+1]) == list:
                    chain = blockchain(b, a+1, nx-scrollpos["canvasx"], y, arg=v[0])
                    if not chain[-1]: return [x, y, bbox, nx, None, False]
                    nbox, nx = chain[2], chain[3]+8
                    if len(getblock(b[a+1][0]).get("args", [])) == 0:
                        nx += 18
                else:
                    col = "inherit"
                    if v[0] in ["in", "ni"]: col = argcolor
                    elif v[0] == "vi": col = varargcolor
                    elif v[0] == "si": col = scriptargcolor
                    elif v[0] == "oi": col = "system"
                    if col == "inherit": col = cat["color"]
                    preview = None
                    if previewmode == 1: preview = array[i][a+1]
                    elif previewmode == 2: preview = v[1]
                    objs, nbox, info = drawblock("etc", nx-scrollpos["canvasx"], bbox[1]-fonty-scrollpos["canvas"], preview=preview, color=col)
                    for obj in objs:
                        canvas.tag_bind(obj, f"<{btnmode}-1>", partial(etcclick, array[i], a+1, v))
                    nx = nbox[2]+40
                canvas.create_text(nx-28, (bbox[1]+bbox[3])/2-1, text=(")" if a == ac-1 else ","), anchor=W, font=f"{font} {blocksize+fontsize+4}")
        if cc > 0:
            y += bbox[3]-bbox[1]+20
            y = drawblocks(b[-1], y=y, indents=indents+1, prevy=bbox[3]+7-fonty, prevbx=bbox[2])[1]
            if y == None: return [x, y, bbox, nx, None, False]
            caprect, nbox, info = drawblock(b[0], x-1, y, notext=True)
            siderect = canvas.create_rectangle(nbox[0]+1, bbox[3]+7-fonty, bbox[0]+10, nbox[1]+1, fill="black", width=0)
            siderect2 = canvas.create_rectangle(nbox[0]+2, bbox[3]+7-fonty-1, bbox[0]+9, nbox[1]+2, fill=cat["color"], width=0)
            for obj in [caprect, siderect, siderect2]:
                canvas.tag_bind(obj, f"<{btnmode}-1>", partial(blockclick, array, i, cpart=2))
                canvas.tag_bind(obj, f"<Shift-{btnmode}-1>", partial(blockctrlclick, array, i, cpart=2))
                canvas.tag_bind(obj, f"<{btnmode}-2>", partial(blockctrlclick, array, i, cpart=2))
                canvas.tag_bind(obj, "<ButtonRelease-3>", partial(blockrightclick, array, i, cpart=2))
        return [x, y, bbox, nx, [nbox[3], nbox[3]-nbox[1]+20-13] if cc > 0 else None, True]
    def drawblocks(array, y=20, indents=0, prevy=None, prevbx=None):
        x = 35+indents*25
        for i, b in enumerate(array):
            if y+scrollpos["canvas"] > canvas.winfo_height():
                return [x, y, False]
            x, y, bbox, nx, ny, ok = blockchain(array, i, x, y, indents=indents)
            if not ok: return [x, y, False]
            if prevy != None:
                if i == 0: lx = min((bbox[0]-8+prevbx+10)/2, bbox[0]+10)
                else: lx = bbox[0]+10
                canvas.create_line(lx, bbox[1]-5-fonty, lx, prevy, width=blocksize//5)
            if ny == None:
                prevy = bbox[3]+7-fonty
                y += bbox[3]-bbox[1]+20
            else:
                prevy = ny[0]
                y += ny[1]
        return [x, y, True]
    global scrollpos
    if mousemove:
        canvas.delete("mouseblocks")
    else:
        canvas.delete("all")
        blockobjs = []
        if hiddenpanes["canvas"]:
            canvas.create_rectangle(0, 0, canvas.winfo_width(), canvas.winfo_height(), fill="black", stipple="gray50", outline="")
            return
        x, y, ok = drawblocks(scripts[script]["blocks"])
        bkpk = canvas.create_text(canvas.winfo_width()-10, canvas.winfo_height()-10, text="Backpack", anchor=SE, font=f"{font} {blocksize+fontsize}")
        canvas.tag_bind(bkpk, f"<{btnmode}-1>", backpackclick)
        canvas.tag_bind(bkpk, "<ButtonRelease-3>", backpackrightclick)
        scrollpos["canvasmin"], scrollpos["canvasmax"] = min(0, -y+100), canvas.winfo_height()-100
    if e and len(block) > 0 and mouseoncanvas:
        objs, bbox, info = drawblock(block[0][0], e.x+10, e.y+10, absolute=True, tags="mouseblocks")
        if len(block) > 1:
            ext = canvas.create_text(e.x+8, bbox[3]+12, text=f"+{len(block)-1} block{'s' if len(block) > 2 else ''}",
                                     anchor=NW, font=f"{font} {blocksize+fontsize}", tags="mouseblocks")
def argclick(path, num, typ, e=None):
    global block
    if len(block) > 0:
        if typ == "vi" or (typ == "si" and block[0][0] != "dummy_script"): return
        if block[0][0] in setblocks: return
        if "c" in [a[0] for a in getblock(block[0][0]).get("args", [])]: return
        path[num], block[0] = block[0], path[num]
    else:
        block = [path[num]]
        path[num] = argdefault[typ]
    updatecanvas(e=e)
def argrightclick(path, num, typ, e=None):
    global block, data
    if len(block) > 0: rightclick(e=e)
    else:
        data = [path, num, typ]
        argctxmenu.tk_popup(e.x_root, e.y_root, 0)
        argctxmenu.grab_release()
def deletearg():
    global scripts
    data[0][data[1]] = argdefault[data[2]]
    updatecanvas()
def etcclick(path, num, arg, e=None):
    global block, lastvar, lastfield
    lastfield = [path, num]
    if len(block) > 0:
        if arg[0] == "vi" or (arg[0] == "si" and block[0][0] != "dummy_script"): return
        if block[0][0] in setblocks: return
        if "c" in [a[0] for a in getblock(block[0][0]).get("args", [])]: return
        path[num] = block[0]
        block = block[1:]
    else:
        titl = "Argument value - "
        if arg[0] in ["in", "ni"]: titl += "Generic"
        elif arg[0] == "si": titl += "Script"
        elif arg[0] == "vi": titl += "Variable"
        else: titl += "Other"
        value = askstring(titl, arg[1].ljust(70), initialvalue=path[num])
        if value == None: return
        iftext, change = "If you want to insert text, make sure you have double quotes before and after it.", "Change it to avoid problems."
        mayerr, willerr = "This may cause errors at runtime.", "This will cause errors at runtime."
        if arg[0] in ["in", "ni"] and value:
            try:
                ev = literal_eval(value)
            except SyntaxError:
                showerror(titl, f"The argument value syntax is incorrect. {willerr} {iftext}")
            except ValueError:
                if value in ["true", "false", "none"]:
                    if askyesno(titl, f"Did you mean to write {value.capitalize()} instead of {value}?"):
                        value = value.capitalize()
##                if not ignorewarnings:
##                    showwarning(titl, f"The argument value is malformed. {mayerr} {iftext}")
        elif arg[0] == "vi":
            value = filtname(value)
            lastvar = value
            if keyword.iskeyword(value):
                showerror(titl, f"This variable name is reserved for built-in methods. {willerr} {change}")
            elif value in dir(__builtins__) or value in builtins:
                if not ignorewarnings:
                    showwarning(titl, f"This variable name is used by build-in methods. {mayerr} {change}")
            elif value in [s["name"] for s in scripts]:
                if not ignorewarnings:
                    showwarning(titl, f"This variable name is the same as a script name. {mayerr} {change}")
        elif arg[0] == "si":
            if value.isdigit():
                if (int(value) > len(scripts)-1 or int(value) < 0) and not ignorewarnings:
                    showwarning(titl, f"The script index {value} does not exist. {mayerr} {change}")
            else:
                ok = False
                for s in scripts:
                    if s["name"] == value:
                        ok = True
                        break
                if not ok and not ignorewarnings:
                    showwarning(titl, f"The script '{value}' does not exist. {mayerr} {change}")
        path[num] = value
    updatecanvas(e=e)
def nextfield(e=None):
    global lastfield
    if lastfield == None: return
    if lastfield[1] < len(lastfield[0])-1:
        n = lastfield[1]+1
        if type(lastfield[0][n]) == str:
            etcclick(lastfield[0], n, getblock(lastfield[0][0]).get("args", [])[n-1])
        else:
            lastfield = [lastfield[0], n]
            nextfield()
def backpackclick(e=None):
    def choosescript(name):
        global block
        block = backpack[name]
        bw.destroy()
    def removescript(name, e=None):
        global backpack
        if askyesno("Backpack", "Would you like to remove script '%s'?"%name):
            backpack.pop(name)
            bw.destroy()
            savesettings()
    global block, backpack
    if len(block) > 0:
        name = askstring("Backpack", "Enter a name for the script:", initialvalue="script")
        if not name: return
        backpack[name] = block
        block = []
        savesettings()
        updatecanvas()
    else:
        bw = Toplevel(root)
        bw.title("Backpack")
        bw.grab_set()
        bw.focus_set()
        Label(bw, text="Backpack").pack()
        sframe = Frame(bw)
        if len(backpack) > 0:
            for i, kv in enumerate(backpack.items()):
                btn = Button(sframe, text=kv[0], command=partial(choosescript, kv[0]))
                btn.bind("<ButtonRelease-3>", partial(removescript, kv[0]))
                btn.grid(row=i//2, column=i%2, sticky=NSEW)
        else: Label(sframe, text="There are no scripts in the backpack.").grid()
        sframe.pack()
def backpackrightclick(e=None):
    global backpack
    if len(backpack) == 0: return
    elif len(backpack) == 1:
        ok = askyesno("Clear backpack", f"Would you like to clear the script in the backpack?")
    else:
        ok = askyesno("Clear backpack", f"Would you like to clear all {len(backpack)} scripts in the backpack?")
    if ok:
        backpack = {}
        savesettings()
def changescript(s, e=None, savescroll=True):
    global script, scrollpos, scriptscrollpos, lastfield
    if savescroll:
        scriptscrollpos[scripts[script]["name"]] = (scrollpos["canvas"], scrollpos["canvasx"])
    script = s
    if not scripts[script]["name"] in scriptscrollpos:
        scriptscrollpos[scripts[script]["name"]] = (0, 0)
    scrollpos["canvas"], scrollpos["canvasx"] = scriptscrollpos[scripts[script]["name"]]
    lastfield = None
    updatescriptbar()
    updatecanvas()
def newscript(preset, e=None):
    def usepreset(i):
        global scripts
        for ps in presets[i]["scripts"]:
            for s in scripts:
                if s["name"] == ps["name"]:
                    showerror("New script from preset", f"This preset cannot be added. Please rename the script '{ps['name']}' to add it.")
                    return
        for ps in presets[i]["scripts"]:
            scripts.append({"name": ps["name"], "blocks": ps["blocks"]})
        pw.destroy()
        changescript(len(scripts)-1)
    global scripts
    blocks = [["script_start"]]
    if preset:
        pw = Toplevel(root)
        pw.title("New script from preset")
        pw.grab_set()
        pw.focus_set()
        Label(pw, text="New script from preset").pack()
        bframe = Frame(pw)
        for i, p in enumerate(presets):
            btn = Button(bframe, text=p["name"], command=partial(usepreset, i))
            btn.grid(row=i//2, column=i%2, sticky=NSEW)
        bframe.pack()
    else:
        name = askstring("New script", "Enter the script name:", initialvalue="script")
        if not name: return
        name = filtname(name, non="")
        if not name:
            showerror("New script", "Invalid name.")
            return
        for s in scripts:
            if s["name"] == name:
                showerror("New script", f"The script '{name}' already exists.")
                return
        scripts.append({"name": name, "blocks": [["script_start"]]})
        changescript(len(scripts)-1)
def blockcategory(b):
    for c in categories:
        if b in c["blocks"]:
            return c
    return {"name": "Error", "symbol": "", "color": "error", "blocks": []}
def changecategory(c, e=None):
    global category, scrollpos
    if c != category:
        category = c
        scrollpos["blockbar"] = 0
        updateblockbar()
def blockclick(path, num, e=None, fixed=False, cpart=0):
    global block, scripts
    if len(block) > 0:
        if cpart == 1:
            for i, b in enumerate(block):
                path[num][-1].insert(i, b)
        else:
            for i, b in enumerate(block):
                path.insert(num+i+1, b)
        block = []
    elif not fixed:
        block = path[num:]
        for i in range(len(block)):
            path.pop(num)
    updatecanvas(e=e)
def blockctrlclick(path, num, e=None, fixed=False, cpart=0, arg=False):
    global block, scripts
    if len(block) > 0:
##        if arg and block[0][0] in setblocks: return
##        if len(path[num]) != len(block[0]): return
##        if "c" in [a[0] for a in getblock(block[0][0]).get("args", [])]: return
##        path[num][0], block[0][0] = block[0][0], path[num][0]
        if path[num][0] in setblocks: return
        n = 0
        for i, a in enumerate(getblock(block[0][0]).get("args", [])):
            if a[0] in ["in", "ni", "oi"]:
                n = i+1
                break
        if n == 0: return
        block[0][n] = deepcopy(path[num])
        path[num] = block[0]
        block = block[1:]
        updatecanvas(e=e)
    elif not fixed and not arg:
        block = [path[num]]
        path.pop(num)
        updatecanvas(e=e)
def blockrightclick(path, num, e=None, fixed=False, cpart=0):
    global block, data
    if len(block) > 0: rightclick(e=e)
    elif not fixed:
        data = [path, num]
        blockctxmenu.tk_popup(e.x_root, e.y_root, 0)
        blockctxmenu.grab_release()
def addblock(b, e=None, auto=False):
    global block, scripts
    tmp = [b]
    args = getblock(b).get("args", [])
    for a in args:
        if a[0] == "vi" and lastvar: tmp.append(lastvar)
        elif type(argdefault[a[0]]) == str: tmp.append(argdefault[a[0]])
        else: tmp.append(deepcopy(argdefault[a[0]]))
    if auto:
        scripts[script]["blocks"].append(tmp)
        block = []
        updatecanvas()
    else: block = [tmp]
def duplicateblock():
    global block
    block = [deepcopy(data[0][data[1]])]
def duplicateblocks():
    global block
    block = deepcopy(data[0][data[1]:])
def deleteblock():
    global scripts
    data[0].pop(data[1])
    updatecanvas()
def deleteblocks():
    global scripts
    for i in range(len(data[0][data[1]:])):
        data[0].pop(data[1])
    updatecanvas()
def rightclick(e=None):
    global block
    if len(block) > 0:
        block = []
        updatecanvas()
def scriptrightclick(num, e=None):
    global data
    scriptctxmenu.entryconfigure("Delete", state=(NORMAL if len(scripts) > 1 else DISABLED))
    scriptctxmenu.entryconfigure("Move up", state=(NORMAL if num > 0 else DISABLED))
    scriptctxmenu.entryconfigure("Move down", state=(NORMAL if num < len(scripts)-1 else DISABLED))
    scriptctxmenu.entryconfigure("Move to top", state=(NORMAL if num > 0 else DISABLED))
    data = [num]
    scriptctxmenu.tk_popup(e.x_root, e.y_root, 0)
    scriptctxmenu.grab_release()
def renamescript():
    global scripts
    name = askstring("Rename script", "Enter the script name:", initialvalue=scripts[data[0]]["name"])
    if not name: return
    name = filtname(name, non="")
    if not name:
        showerror("Rename script", "Invalid name.")
        return
    for s in scripts:
        if s["name"] == name:
            showerror("Rename script", f"The script '{name}' already exists.")
            return
    scripts[data[0]]["name"] = name
    updatescriptbar()
def deletescript():
    global scripts, script
    if askyesno("Delete script", "Are you sure you want to delete '%s'?"%scripts[data[0]]["name"]):
        scripts.pop(data[0])
        changescript(0, savescroll=False)
def movescript(i):
    global scripts, script
    if i == None:
        scripts[data[0]], scripts[0] = scripts[0], scripts[data[0]]
        if script == data[0]: changescript(0)
        elif script == 0: changescript(data[0])
    else:
        scripts[data[0]], scripts[data[0]+i] = scripts[data[0]+i], scripts[data[0]]
        if script == data[0]: changescript(data[0]+i)
        elif script == data[0]+i: changescript(data[0])
    updatescriptbar()
def scroll(name, e=None, delta=None):
    global scrollpos
    if delta == None: delta = e.delta
    if delta < 0: scrollpos[name] -= scrollspeed
    elif delta > 0: scrollpos[name] += scrollspeed
    scrollpos[name] = max(scrollpos[name+"min"], min(scrollpos[name+"max"], scrollpos[name]))
    if delta == 0: return
    elif name == "canvas" or name == "canvasx": updatecanvas(e=e)
    elif name == "blockbar": updateblockbar(e=e)
    elif name == "scriptbar": updatescriptbar(e=e)
def scrollx(name, e=None, delta=None):
    global scrollpos
    if delta == None: delta = e.delta
    if delta < 0: scrollpos[name] -= scrollspeed
    elif delta > 0: scrollpos[name] += scrollspeed
    scrollpos[name] = min(scrollpos[name], 200)
    if delta == 0: return
    elif name == "canvasx": updatecanvas(e=e)
def resetscroll():
    global scrollpos
    for sp in ["canvas", "canvasx", "blockbar", "scriptbar"]:
        scrollpos[sp] = 0
    updateall()
def newfile(e=None):
    global scripts, saveloc
    if askyesno("New file", "Are you sure you want to make a new file?"):
        scripts = [{"name": "main", "blocks": [["script_start"]]}]
        saveloc = None
        root.title(title)
        updatescriptbar()
        updatecanvas()
def openfile(e=None, fn=None):
    global saveloc, script
    if not fn:
        fn = askopenfilename(title="Open", filetypes=(("Flow files", "*.flow"), ("All files", "*.*")))
        if not fn: return
    if not os.path.isfile(fn):
        showerror("Open file", "File not found - '%s'"%fn)
        closefile()
        return
    saveloc = fn
    savesettings()
    root.title(f"{title} - {os.path.basename(saveloc)}")
    with open(saveloc) as f:
        jsontovars(json.load(f))
    changescript(0)
def save(e=None, handle=False):
    global saveloc
    if not saveloc or handle:
        fn = asksaveasfilename(title="Save As" if handle else "Save", filetypes=(("Flow file", "*.flow"), ("All files", "*.*")))
        if not fn: return
        saveloc = fn
        if not os.path.splitext(saveloc)[-1]: saveloc += ".flow"
        savesettings()
        root.title(f"{title} - {os.path.basename(saveloc)}")
    with open(saveloc, "w") as f:
        json.dump(varstojson("scripts", "modules", "functionalities"), f)
    return saveloc
def clearscript():
    global scripts
    if askyesno("Clear script", "Are you sure you want to clear this script?"):
        scripts[script]["blocks"] = [["script_start"]]
        updatecanvas()
def managefunctionalities():
    def apply():
        global functionalities
        for i, kv in enumerate(fvars.items()):
            functionalities[kv[0]] = True if kv[1].get() else False
        fw.destroy()
    global functionalities
    fw = Toplevel(root)
    fw.title("Manage functionalities")
    fw.grab_set()
    fw.focus_set()
    Label(fw, text="Manage functionalities").pack()
    cframe = Frame(fw)
    fvars = {}
    for i, kv in enumerate(funcscaffold.items()):
        value = IntVar()
        btn = Checkbutton(cframe, text=kv[1]["name"], variable=value)
        fvars[kv[0]] = value
        value.set(1 if checkfunc(kv[0]) else 0)
        btn.grid(row=i//2, column=i%2, sticky=NW)
    cframe.pack()
    Label(fw, text="Using functionalities which are not checked may result in errors!").pack()
    Button(fw, text="OK", command=apply).pack()
def manageextensions():
    def apply():
        global extpaths, exttemp
        ew.destroy()
        extpaths = exttemp[:]
        savesettings()
        loadextensions()
        updateall()
    def add():
        global extpaths, exttemp
        fn = askopenfilename(title="Open", filetypes=(("JSON files", "*.json"), ("All files", "*.*")))
        if not fn: return
        exttemp.append(fn)
        lb.insert(END, os.path.basename(fn))
    def remove():
        global extpaths, exttemp
        if len(lb.curselection()) == 0:
            showerror("Manage extensions", "An extension must be selected.")
            return
        exttemp.pop(lb.curselection()[0])
        lb.delete(lb.curselection()[0])
    global extpaths, exttemp
    exttemp = extpaths[:]
    ew = Toplevel(root)
    ew.title("Manage extensions")
    ew.grab_set()
    ew.focus_set()
    Label(ew, text="Manage extensions").pack()
    lb = Listbox(ew)
    lb.pack(fill=BOTH, expand=True)
    for p in extpaths:
        lb.insert(END, os.path.basename(p))
    bf = Frame(ew)
    Button(bf, text="Add", command=add).grid(row=0, column=0, sticky=NSEW)
    Button(bf, text="Remove", command=remove).grid(row=0, column=1, sticky=NSEW)
    bf.pack()
    Button(ew, text="OK", command=apply).pack()
def loadextensions():
    global extpaths, builtins
    with open("flow_data.json") as f:
        jsontovars(json.load(f))
    for p in extpaths:
        with open(p) as f:
            try: jsontovars(json.load(f), merge=True)
            except Exception as e:
                showerror("Load extensions", f"Error loading extension {os.path.basename(p)}:\n{e}")
    builtins = ["autoinstall"]
    for k, v in funcscaffold.items():
        if "globals" in v:
            builtins.extend(v["globals"])
def togglefont(n):
    global font, fontbig, fontsize, fonty
    if n == 0:
        font, fontbig, fontsize, fonty = "Tahoma", "Verdana", 0, 0
    elif n == 1:
        font, fontbig, fontsize, fonty = "Arial", "Helvetica", 0, 1
    elif n == 2:
        font, fontbig, fontsize, fonty = "BlokFont", "BlokFont", 3, 3
    elif n == 3:
        font, fontbig, fontsize, fonty = "Courier", "Courier", 0, 1
    savesettings()
    updateall()
def savesettings():
    with open("flow_settings.json", "w") as f:
        json.dump(varstojson("font", "fontbig", "fontsize", "fonty", "blocksize", "scrollspeed", "saveloc", "previewmode",
                             "argcolor", "varargcolor", "scriptargcolor", "redcompile", "ignorewarnings", "shortmode", "backpack", "extpaths"), f)
def closefile(e=None):
    global saveloc
    saveloc = ""
    savesettings()
    root.title(title)
def about():
    showinfo("About Flow", "Flow is designed to be a powerful drag-and-drop coding language based off of Scratch. Go to View -> Show demo to learn the basics of Flow.\n\nCreated by Professor Dragon.\nDiscord server: https://discord.gg/PGEdxBR")
def showdemo(auto=False):
    def hide(bb, c, sb):
        hiddenpanes["blockbar"], hiddenpanes["canvas"], hiddenpanes["scriptbar"] = bb, c, sb
        updateall()
    global hiddenpanes
    if auto:
        if not askyesno("Welcome", "Welcome to Flow. Would you like to see the demo now?"):
            return
    hide(True, False, True)
    showinfo("Workspace", "This is the workspace. It is where you put all of the blocks to create your program.")
    hide(False, True, True)
    showinfo("Block bar", "This is the block bar. It is where you take blocks from to put them onto the workspace.")
    hide(True, True, False)
    showinfo("Script bar", "This is the script bar. It is where you can add and manage extra scripts in the project.")
    hide(True, False, True)
    showinfo("The start script block", "The 'start script' block will always be the first block in a script. Everything underneath it will be run when the script is called.")
    hide(True, True, False)
    showinfo("The play button", "The two colored buttons at the top of the script bar are the compile buttons. The left one will compile and run, and the right one will just compile. It will run the top script in the script bar first, so all if the initialization code should go there.")
    hide(False, False, True)
    showinfo("Adding blocks to the workspace", "Add blocks to the workspace by clicking on one in the block bar, and then moving your mouse over to the workspace. Then click on a block to insert the block you are holding underneath it. You can also shift-click a block in the block bar to quickly add it to the end of the current script.")
    showinfo("More about blocks", "To get rid of the blocks you are holding, right-click on the workspace. Click on a block in the script to select it and the following blocks. Shift-click a block to just select it. Right-click on a block to view more options about the block.")
    showinfo("Block arguments", "Most blocks take arguments, which are represented by an empty block (or three dots if preview mode is off) to the side of the main script. Click on them to change its value, or click on them with a block to insert the block there.")
    showinfo("Block arguments continued", "Green argument blocks take text and numbers as input. Text must be surrounded by single or double quotes, whereas numbers can be inserted by themselves. Orange argument blocks take variable inputs, which is just raw text with no quotes or special characters.")
    hide(False, True, True)
    showinfo("Block categories", "Blocks are divided into categories which each have their own unique color. Change categories by clicking on one of the square buttons on the left of the script bar.")
    hide(True, True, False)
    showinfo("Extra scripts", "You can add more scripts to the project by clicking the + button. They can be run with the 'run script' block in the events category. Click the arrow to the right of that button to quickly add a script from a preset, such as one that creates a game window and canvas for you.")
    hide(False, False, False)
    showinfo("Managing functionalities", "Not all blocks will work by default. You can enable/disable settings like keyboard/mouse support, text-to-speech, and so on - but they must be enabled in Edit -> Manage functionalities before compilation!")
    showinfo("End of demo", "This is the end of the demo. Go to https://discord.gg/PGEdxBR if you have any questions or suggestions.")
def enterblock(e=None):
    entry.grid(row=1, column=1, sticky=NSEW)
    entry.focus_set()
def blockhelp(b=None, e=None):
    if not b: b = data[0][data[1]][0]
    i = getblock(b)
    showinfo(i["text"], i["help"])
def checkprojectsaved():
    if saveloc:
        with open(saveloc) as f:
            if varstojson("scripts", "modules", "functionalities") != json.load(f):
                return False
    else: return False
    return True
def saveconfirm():
    if not checkprojectsaved():
        ok = askyesnocancel("Exit Flow", "You have unsaved changes - would you like to save before exiting?")
        if ok == True:
            save()
            root.destroy()
        elif ok == False: root.destroy()
    else: root.destroy()
def arrowscroll(name, e):
    if e.keysym == "Up": scroll("canvas", delta=1)
    elif e.keysym == "Down": scroll("canvas", delta=-1)
    elif e.keysym == "Left": scrollx("canvasx", delta=1)
    elif e.keysym == "Right": scrollx("canvasx", delta=-1)
def zoom(e=None, amount=None):
    if amount == None:
        if e.delta > 0: amount = 1
        elif e.delta < 0: amount = -1
    a = blocksize+amount
    if a <= 1 or a > 69: return
    toggle("blocksize", a)
def setdragging(s, e=None):
    global dragging
    if s and e: dragging = [scrollpos["canvasx"]-e.x, scrollpos["canvas"]-e.y]
    else: dragging = []
def mousecanvasmove(e):
    global scrollpos
    if len(dragging) > 0:
        scrollpos["canvasx"], scrollpos["canvas"] = dragging[0]+e.x, dragging[1]+e.y
        scroll("canvas", delta=0)
        scrollx("canvasx", delta=0)
        updatecanvas(e=e)
    elif len(block) > 0:
        updatecanvas(e=e, mousemove=True)
def toggle(var, val=None, e=None):
    if val == None: exec(f"{var} = not {var}", globals())
    else: exec(f"{var} = {repr(val)}", globals())
    if var == "ignorewarnings":
        if ignorewarnings: showinfo("Toggle warnings", "Warnings will now be hidden.")
        else: showinfo("Toggle warnings", "Warnings will now be shown.")
    savesettings()
    updateall()
def toggleargcolor(ac, vac=None, sac=None):
    global argcolor, varargcolor, scriptargcolor
    if vac == None: vac = ac
    if sac == None: sac = ac
    argcolor, varargcolor, scriptargcolor = ac, vac, sac
    savesettings()
    updatecanvas()
def opentemploc():
    Popen(["explorer", temploc])
def backupflow():
    d = "Backups"
    if not os.path.isdir(d): os.mkdir(d)
    ext = datetime.now().strftime("%m.%d.%Y - ")
    for fn in [__file__, "flow_data.json"]+extpaths:
        n = os.path.join(d, ext+os.path.basename(fn))
        shutil.copy(fn, n)
    showinfo("Backup Flow", "Backup successful.")
def checkfunc(k):
    return functionalities.get(k, False)
def play(run, e=None, debug=False):
    # Run values
    # 0: Compile
    # 1: Compile and run
    # 2: Compile to executable
    def getfn(temp=True):
        n = os.path.splitext(saveloc)[0]+(".py" if functionalities["console"] else ".pyw")
        if temp:
            n = os.path.join(temploc, os.path.basename(n))
        return n
    def finishexe(cd, n):
        call(f"cmd /c python setup.py py2exe") # todo - make one file
        os.chdir(cd)
        shutil.move(os.path.join(temploc, "dist"), n)
        showinfo("Compile to executable", "Compilation complete!")
    def blockchain(array, i, c, indents=0, arg=False, globs=[], addglobs=False):
        b = array[i]
        args = []
        ps = []
        info = getblock(b[0])
        ccode = ""
        if b[0] == "var_set" and addglobs and not b[1] in globs:
            globs.append(b[1])
        for a, v in enumerate(info.get("args", [])):
            bap = b[a+1]
            if v[0] == "in" or v[0] == "ni":
                if type(bap) == list:
                    bc = blockchain(b, a+1, c, indents=indents, arg=True, addglobs=addglobs, globs=globs)
                    args.append(bc[0])
                    ps.extend(bc[1])
                elif bap: args.append(bap)
                else: args.append(None)
            elif v[0] == "vi":
                if bap: args.append(bap)
                else: args.append("_tmp")
            elif v[0] == "si":
                if type(bap) == str:
                    args.append(scripts[int(bap)]["name"] if bap.isdigit() else bap)
                elif bap[0] == "dummy_script":
                    args.append("_flow_dummyscript")
            elif v[0] == "c":
                ccode, globs = iterblocks(bap, indents=indents+1, addglobs=addglobs, globs=globs)
            else: args.append(b[a+1])
        if "postscaffold" in info:
            if array[0] in setblocks:
                args.append(array[1])
            else: args.append("_tmp")
            ps = info["postscaffold"].format(*args).split("\n")
        if debug: print(b[0])
        if "scaffold" in info: tmp = info["scaffold"].format(*args)
        else: tmp = f"{b[0]}({', '.join(args)})"
        if "postscaffold" in info and not array[0] in setblocks:
            tmp = "_tmp = "+tmp
        if arg: return [tmp, ps, globs]
        elif tmp: return ["    "*indents+tmp+"\n"+ccode, ps, globs]
        return ["", ps, globs]
    def iterblocks(array, indents=0, globs=[], addglobs=False):
        c = ""
        ok = False
        for i, b in enumerate(array):
            bc = blockchain(array, i, c, indents=indents, globs=globs, addglobs=addglobs)
            c += bc[0]
            if not ok:
                ls = bc[0].lstrip()
                if len(ls) > 0 and ls[0] != "#":
                    ok = True
            for s in bc[1]:
                c += "    "*indents+s+"\n"
            globs = bc[2]
        if not ok:
            c += "    "*indents+"pass\n"
        return [c, globs]
    def compil(fn):
        c = """
######################################
###         Made with Flow         ###
###   Created by Professor Dragon  ###
###        discord.gg/PGEdxBR      ###
######################################

import os, sys, math
import subprocess, traceback
from multiprocessing import Process
from ast import literal_eval
"""
        globs = []
        for k, v in funcscaffold.items():
            if checkfunc(k):
                if "imports" in v:
                    if functionalities["autoinstall"] and "modules" in v:
                        c += "try:\n"
                        for ln in v["imports"].split("\n"):
                            c += "    "+ln+"\n"
                        c += f"except ImportError: autoinstall.extend({repr(v['modules'])})\n"
                    else: c += v["imports"]+"\n"
                if "globals" in v:
                    globs.extend(v["globals"])
        c += "\n"
        for n, s in enumerate(scripts):
            c += f"def {s['name']}(event=None, *_tmp):\n"
            if debug: print(f"Compile script '{s['name']}'")
            it = iterblocks(s["blocks"], indents=1, globs=globs, addglobs=(n == 0))
            if len(it[1]) > 0:
                c += "    global "+", ".join(it[1])+"\n"
            c += it[0]
        c += "\n"
        if functionalities["autoinstall"]:
            if not functionalities["console"] or functionalities["windows"]:
                if not functionalities["dialogs"]:
                    c += "from tkinter.messagebox import*\n"
                c += f"""\
def _flow_autoinstall():
    if askyesno("Modules missing", f"Critical error - missing module(s) {{', '.join(autoinstall)}}. This program will not function without them. \\
Would you like to install them now?"):
        for mod in autoinstall:
            subprocess.check_call(["python", "-m", "pip", "install", mod])
        showinfo("Modules installed", "All modules successfully installed! Restart the program to continue.")
        exit()
"""
            else:
                c += f"""\
def _flow_autoinstall():
    if input(f"Critical error - missing module(s) {{', '.join(autoinstall)}}. This program will not function without them. \\
Would you like to install them now? <type Y to confirm>\\n").lower() == "y":
        for mod in autoinstall:
            subprocess.check_call(["python", "-m", "pip", "install", mod])
        input("All modules successfully installed! Restart the program to continue.\\n")
        exit()
"""
        c += f"""\
def _flow_dummyscript(*a, **k):
    pass
def _flow_fromstring(text):
    try: return literal_eval(text)
    except Exception: return None
def _flow_split(base, sep, lim):
    if not sep: return list(base)
    if not lim: return base.split(sep)
    if lim < 0: return base.rsplit(sep, -lim)
    return base.split(sep, lim)
def _flow_add(p1, p2):
    if type(p1) == str or type(p2) == str:
        return str(p1)+str(p2)
    return p1+p2
def _flow_specialop(typ, num):
    if typ == "round": return round(num)
    elif typ == "ceil": return math.ceil(num)
    elif typ == "floor": return math.floor(num)
    elif typ == "abs": return abs(num)
    elif typ == "sqrt": return math.sqrt(num)
    elif typ == "sin": return math.sin(math.radians(num))
    elif typ == "cos": return math.cos(math.radians(num))
    elif typ == "tan": return math.tan(math.radians(num))
    elif typ == "asin": return math.degrees(math.asin(num))
    elif typ == "acos": return math.degrees(math.acos(num))
    elif typ == "atan": return math.degrees(math.atan(num))
    elif typ == "log": return math.log(num, 10)
    elif typ == "ln": return math.log(num)
def _flow_exception(typ, val, tb):
    traceback.print_exception(typ, val, tb)
    input("\\n")
"""
        for k, v in funcscaffold.items():
            if checkfunc(k) and "functions" in v:
                c += v["functions"]+"\n"
        c += """
sys.excepthook = _flow_exception
if __name__ == '__main__':
"""
        if functionalities["autoinstall"]:
            c += "    if len(autoinstall) > 0: _flow_autoinstall()\n"
        for k, v in funcscaffold.items():
            if checkfunc(k) and "init" in v:
                for ln in v["init"].split("\n"):
                    c += "    "+ln+"\n"
        c += f"    {scripts[0]['name']}()"
        with open(fn, "w") as f:
            f.write(c)
    if debug: print(f"Build with run value {run}")
    if not save(): return
    fn = getfn(run != 0)
    compil(fn)
    if debug: print("Build finished")
    if run == 0:
        showinfo("Compile", f"Compiled project successfully.\nLocation: {fn}")
    elif run == 1:
        Popen(["python" if functionalities["console"] else "pythonw", fn])
    elif run == 2:
        try: import py2exe as _
        except ImportError:
            if not askyesno("Module missing", "Cannot compile without py2exe. Would you like to install it now?"):
                return
            check_call(["python", "-m", "pip", "install", "py2exe"])
            showinfo("Module installed", "Successfully installed py2exe.")
        cd = os.getcwd()
        os.chdir(temploc)
        sfn = os.path.join(temploc, "setup.py")
        includes = []
        for k, v in funcscaffold.items():
            if "modules" in v and checkfunc(k):
                includes.extend(v["modules"])
        with open(sfn, "w") as f:
            f.write(f"""\
from distutils.core import setup
import py2exe

setup(
    {"console" if functionalities["console"] else "windows"} = [{repr(fn)}],
    zipfile = None,
    options = {{
        "py2exe": {{
            "bundle_files": 1,
            "compressed": True
        }}
    }}
)
""")
        start_new_thread(finishexe, (cd, os.path.splitext(os.path.basename(fn))[0]))

if os.path.isfile("flow_settings.json"):
    with open("flow_settings.json") as f:
        jsontovars(json.load(f))
else:
    savesettings()
    dodemo = True

root = Tk()
root.title(title)

if len(sys.argv) > 0 and os.path.basename(sys.argv[0]) == os.path.basename(__file__):
    sys.argv.pop(0)
if len(sys.argv) > 0:
    saveloc = sys.argv[0]

root.geometry("1100x600")
root.protocol("WM_DELETE_WINDOW", saveconfirm)
root.columnconfigure(1, weight=1)
root.rowconfigure(0, weight=1)
root.bind("<Configure>", updateall)
root.bind("/", enterblock)
root.bind("<Tab>", nextfield)
root.bind("<Control-=>", partial(zoom, amount=1))
root.bind("<Control-minus>", partial(zoom, amount=-1))
for d in ["Up", "Down", "Left", "Right"]:
    root.bind(f"<{d}>", partial(arrowscroll, "canvas"))

blockbar = Canvas(root, width=300, bg="#ccc", highlightbackground="black", highlightthickness=2)
blockbar.grid(row=0, column=0, sticky=NSEW, rowspan=2)
blockbar.bind("<MouseWheel>", partial(scroll, "blockbar"))

canvas = Canvas(root, bg="#eee")
canvas.grid(row=0, column=1, sticky=NSEW)
canvas.bind("<Motion>", mousecanvasmove)
canvas.bind("<Enter>", partial(toggle, "mouseoncanvas", True))
canvas.bind("<Leave>", partial(toggle, "mouseoncanvas", False))
canvas.bind("<MouseWheel>", partial(scroll, "canvas"))
canvas.bind("<Shift-MouseWheel>", partial(scrollx, "canvasx"))
canvas.bind("<Control-MouseWheel>", zoom)
canvas.bind("<Button-1>", partial(setdragging, True))
canvas.bind("<ButtonRelease-1>", partial(setdragging, False))
canvas.bind("<ButtonRelease-3>", rightclick)
entry = Entry(root)

scriptbar = Canvas(root, width=100, bg="#ccc", highlightbackground="black", highlightthickness=2)
scriptbar.grid(row=0, column=2, sticky=NSEW, rowspan=2)
scriptbar.bind("<MouseWheel>", partial(scroll, "scriptbar"))

menu = Menu(root)

filemenu = Menu(menu, tearoff=False)
filemenu.add_command(label="New", accelerator="Ctrl+N", command=newfile)
root.bind("<Control-n>", newfile)
filemenu.add_command(label="Open", accelerator="Ctrl+O", command=openfile)
root.bind("<Control-o>", openfile)
filemenu.add_command(label="Save", accelerator="Ctrl+S", command=save)
root.bind("<Control-s>", save)
filemenu.add_command(label="Save As", accelerator="Ctrl+Shift+S", command=partial(save, handle=True))
root.bind("<Control-S>", partial(save, handle=True))
filemenu.add_separator()
filemenu.add_command(label="Close", accelerator="Ctrl+W", command=closefile)
root.bind("<Control-w>", closefile)
filemenu.add_command(label="Exit", command=root.destroy)

editmenu = Menu(menu, tearoff=False)
editmenu.add_command(label="Undo", accelerator="Ctrl+Z")
editmenu.add_command(label="Redo", accelerator="Ctrl+Shift+Z")
editmenu.add_separator()
editmenu.add_command(label="New script", accelerator="Ctrl+Shift+N", command=partial(newscript, False))
root.bind("<Control-N>", partial(newscript, False))
editmenu.add_command(label="New script from preset", command=partial(newscript, True))
editmenu.add_command(label="Clear script", command=clearscript)
editmenu.add_separator()
editmenu.add_command(label="Toggle warnings", command=partial(toggle, "ignorewarnings"))
editmenu.add_command(label="Manage functionalities", command=managefunctionalities)
editmenu.add_command(label="Manage extensions", command=manageextensions)

viewmenu = Menu(menu, tearoff=False)
fontmenu = Menu(viewmenu, tearoff=False)
fontmenu.add_command(label="Tahoma / Verdana", command=partial(togglefont, 0))
fontmenu.add_command(label="Arial / Helvetica", command=partial(togglefont, 1))
fontmenu.add_command(label="BlokFont", command=partial(togglefont, 2))
fontmenu.add_command(label="Courier", command=partial(togglefont, 3))
viewmenu.add_cascade(label="Font", menu=fontmenu)
blocksizemenu = Menu(viewmenu, tearoff=False)
blocksizemenu.add_command(label="Extra small", command=partial(toggle, "blocksize", 6))
blocksizemenu.add_command(label="Small", command=partial(toggle, "blocksize", 9))
blocksizemenu.add_command(label="Medium", accelerator="Ctrl+0", command=partial(toggle, "blocksize", 11))
root.bind("<Control-0>", partial(toggle, "blocksize", 11))
blocksizemenu.add_command(label="Large", command=partial(toggle, "blocksize", 13))
blocksizemenu.add_command(label="Extra large", command=partial(toggle, "blocksize", 16))
viewmenu.add_cascade(label="Block size", menu=blocksizemenu)
scrollspeedmenu = Menu(viewmenu, tearoff=False)
scrollspeedmenu.add_command(label="Slow", command=partial(toggle, "scrollspeed", 20))
scrollspeedmenu.add_command(label="Medium", command=partial(toggle, "scrollspeed", 40))
scrollspeedmenu.add_command(label="Fast", command=partial(toggle, "scrollspeed", 70))
viewmenu.add_cascade(label="Scroll speed", menu=scrollspeedmenu)
argdispmenu = Menu(viewmenu, tearoff=False)
argdispmenu.add_command(label="Value", command=partial(toggle, "previewmode", 1))
argdispmenu.add_command(label="Name", command=partial(toggle, "previewmode", 2))
argdispmenu.add_command(label="...", command=partial(toggle, "previewmode", 0))
viewmenu.add_cascade(label="Argument display", menu=argdispmenu)
argcolormenu = Menu(viewmenu, tearoff=False)
argcolormenu.add_command(label="Green / orange / brown", command=partial(toggleargcolor, "limegreen", "darkorange", "peru"))
argcolormenu.add_command(label="Gray / red / cyan", command=partial(toggleargcolor, "gainsboro", "red", "cyan"))
argcolormenu.add_command(label="Purple", command=partial(toggleargcolor, ""))
argcolormenu.add_command(label="Inherit", command=partial(toggleargcolor, "inherit"))
viewmenu.add_cascade(label="Argument colors", menu=argcolormenu)
viewmenu.add_separator()
viewmenu.add_command(label="Reset scroll positions", command=resetscroll)
viewmenu.add_command(label="Toggle short mode", command=partial(toggle, "shortmode"))
viewmenu.add_command(label="Toggle red compile button", command=partial(toggle, "redcompile"))

buildmenu = Menu(menu, tearoff=False)
buildmenu.add_command(label="Compile and run", accelerator="F5", command=partial(play, 1))
root.bind("<F5>", partial(play, 1))
buildmenu.add_command(label="Compile", accelerator="Ctrl+F5", command=partial(play, 0))
root.bind("<Control-F5>", partial(play, 0))
buildmenu.add_command(label="Compile to executable", command=partial(play, 2))

helpmenu = Menu(menu, tearoff=False)
helpmenu.add_command(label="Show demo", command=showdemo)
helpmenu.add_command(label="About Flow", command=about)
helpmenu.add_separator()
helpmenu.add_command(label="Open log directory", command=opentemploc)
helpmenu.add_command(label="Backup Flow", command=backupflow)

menu.add_cascade(label="File", menu=filemenu)
menu.add_cascade(label="Edit", menu=editmenu)
menu.add_cascade(label="View", menu=viewmenu)
menu.add_cascade(label="Build", menu=buildmenu)
menu.add_cascade(label="Help", menu=helpmenu)

blockctxmenu = Menu(root, tearoff=False)
blockctxmenu.add_command(label="Duplicate", command=duplicateblock)
blockctxmenu.add_command(label="Duplicate with following", command=duplicateblocks)
blockctxmenu.add_command(label="Delete", command=deleteblock)
blockctxmenu.add_command(label="Delete with following", command=deleteblocks)
blockctxmenu.add_command(label="Help", command=blockhelp)

argctxmenu = Menu(root, tearoff=False)
argctxmenu.add_command(label="Duplicate", command=duplicateblock)
argctxmenu.add_command(label="Delete", command=deletearg)
argctxmenu.add_command(label="Help", command=blockhelp)

scriptctxmenu = Menu(root, tearoff=False)
scriptctxmenu.add_command(label="Rename", command=renamescript)
scriptctxmenu.add_command(label="Delete", command=deletescript)
scriptctxmenu.add_command(label="Move up", command=partial(movescript, -1))
scriptctxmenu.add_command(label="Move down", command=partial(movescript, 1))
scriptctxmenu.add_command(label="Move to top", command=partial(movescript, None))

root.configure(menu=menu)
loadextensions()
if saveloc: openfile(fn=saveloc)
if dodemo: showdemo(auto=True)
root.mainloop()

sys.stderr.close()
