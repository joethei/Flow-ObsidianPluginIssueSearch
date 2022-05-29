# -*- coding: utf-8 -*-

import sys, os

parent_folder_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(parent_folder_path)
sys.path.append(os.path.join(parent_folder_path, 'lib'))
sys.path.append(os.path.join(parent_folder_path, 'plugin'))

from flox import Flox
import urllib.request
import json
import webbrowser

####
# Copy to clipboard function (put) compatible with x64 from https://forums.autodesk.com/t5/maya-programming/ctypes-bug-cannot-copy-data-to-clipboard-via-python/td-p/9195866
import ctypes
from ctypes import wintypes

CF_UNICODETEXT = 13

user32 = ctypes.WinDLL('user32')
kernel32 = ctypes.WinDLL('kernel32')

OpenClipboard = user32.OpenClipboard
OpenClipboard.argtypes = wintypes.HWND,
OpenClipboard.restype = wintypes.BOOL
CloseClipboard = user32.CloseClipboard
CloseClipboard.restype = wintypes.BOOL
EmptyClipboard = user32.EmptyClipboard
EmptyClipboard.restype = wintypes.BOOL
GetClipboardData = user32.GetClipboardData
GetClipboardData.argtypes = wintypes.UINT,
GetClipboardData.restype = wintypes.HANDLE
SetClipboardData = user32.SetClipboardData
SetClipboardData.argtypes = (wintypes.UINT, wintypes.HANDLE)
SetClipboardData.restype = wintypes.HANDLE

GlobalLock = kernel32.GlobalLock
GlobalLock.argtypes = wintypes.HGLOBAL,
GlobalLock.restype = wintypes.LPVOID
GlobalUnlock = kernel32.GlobalUnlock
GlobalUnlock.argtypes = wintypes.HGLOBAL,
GlobalUnlock.restype = wintypes.BOOL
GlobalAlloc = kernel32.GlobalAlloc
GlobalAlloc.argtypes = (wintypes.UINT, ctypes.c_size_t)
GlobalAlloc.restype = wintypes.HGLOBAL
GlobalSize = kernel32.GlobalSize
GlobalSize.argtypes = wintypes.HGLOBAL,
GlobalSize.restype = ctypes.c_size_t

GMEM_MOVEABLE = 0x0002
GMEM_ZEROINIT = 0x0040

unicode = type(u'')


def put(s):
    if not isinstance(s, unicode):
        s = s.decode('mbcs')
    data = s.encode('utf-16le')
    OpenClipboard(None)
    EmptyClipboard()
    handle = GlobalAlloc(GMEM_MOVEABLE | GMEM_ZEROINIT, len(data) + 2)
    pcontents = GlobalLock(handle)
    ctypes.memmove(pcontents, data, len(data))
    GlobalUnlock(handle)
    SetClipboardData(CF_UNICODETEXT, handle)
    CloseClipboard()


######

class ObsidianPlugins(Flox):

    def paste(self, title, link):
        self.show_msg("Copied to clipboard", "Help")
        put("_" + title + "_(<" + link + ">)")

    def open_in_browser(self, url):
        webbrowser.open(url)

    def query(self, query):
        url = "https://api.obsidian.joethei.xyz/plugins/issues"
        data = urllib.request.urlopen(url).read().decode()
        obj = json.loads(data)
        var = filter(lambda x: self.args.lower() in x['title'].lower()
                               or self.args.lower() in x['plugin']['name'].lower()
                     , obj)

        for plugin in var:
            self.add_item(title=plugin['title'],
                          subtitle=plugin['description'][:80],
                          method=self.paste,
                          parameters=[plugin['title'], plugin['url']],
                          context=[plugin])

    def context_menu(self, data):
        plugin = data[0]
        self.add_item(title=plugin['title'],
                      subtitle=plugin['description'],
                      method=self.paste,
                      parameters=[plugin['title'], plugin['url']],
                      context=[plugin])
        self.add_item(
            title="Open in browser",
            subtitle=plugin['title'],
            icon="github.png",
            method=self.open_in_browser,
            parameters=[plugin['url']]
        )


if __name__ == "__main__":
    ObsidianPlugins()
