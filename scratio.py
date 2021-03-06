# coding=utf-8

from server import *
import serial.tools.list_ports
import wx
import json
import os
import sys
import time
import logging
import webbrowser

class scratio:
    def __init__(self):
        self.oflg = 0
        self.sflg = 0
        self.selectflg = [0,0]
        self.lang = 'ja'
        self.getportlist()
        self.openjson()
        self.icon = self.find_data_file('images/icon_256x256.ico')

    def find_data_file(self,filename):
        if getattr(sys, 'frozen', False):
            # The application is frozen
            datadir = os.path.dirname(sys.executable)
        else:
            # The application is not frozen
            # Change this bit to match where you store your data files:
            datadir = os.path.dirname(__file__)

        return os.path.join(datadir, filename)

    def openjson(self):
        #json_path = os.path.abspath("setting.json")
        json_path = self.find_data_file("setting.json")
        f = open(json_path, 'r', encoding='utf-8')
        self.jsonData = json.load(f)

    def getportlist(self):
        self.ports = []
        lists = list(serial.tools.list_ports.comports())
        for x in lists:
            self.ports.append(x[0])

        return self.ports

    def getExtensionlist(self):
        self.extensions = []
        self.extensions = self.jsonData[u"extensions"]

    def connectServer(self):
        self.server = server(self.sock_port)
        self.server.main()
        self.server.call_arduino(self.port)
        self.sflg = 1

    def click_button(self,event):
        if self.oflg == 0:
            self.connectServer()
            self.button.SetLabel(self.jsonData[self.lang][u"connecting"])
            self.oflg = 1
            self.button2.Disable()
        else:
            self.server.close()
            self.button.SetLabel(self.jsonData[self.lang][u"connect"])
            self.oflg = 0
            self.button2.Enable()

    def click_refresh(self,event):
      if self.sflg == 1:
          self.server.close()
      self.ports = self.getportlist()
      self.combobox_ports.SetItems(self.ports)
      self.selectflg[0] = 0
      self.button.Disable()

    def selectMenu(self,event):
        val = event.GetId()

        if val == 1 or val == 2:
            if val == 1:
                self.lang = 'ja'
            else:
                self.lang = 'en'
            self.s_text_extension.SetLabel(self.jsonData[self.lang][u"extension"])
            self.s_text_serial.SetLabel(self.jsonData[self.lang][u"serial"])
            if self.oflg == 0:
                self.button.SetLabel(self.jsonData[self.lang][u"connect"])
            else:
                self.button.SetLabel(self.jsonData[self.lang][u"connecting"])
        elif val == 3:
            webbrowser.open_new_tab(self.jsonData[self.lang][u"site"])
        elif val == 4:
            wx.MessageBox(self.jsonData[u'version'], 'Version', wx.OK)

    def addMenu(self):
        menu_lang = wx.Menu()
        self.menu_about = wx.Menu()
        self.menu_bar = wx.MenuBar()

        self.menu_bar.Append(menu_lang,u"View")
        menu_lang.AppendRadioItem(1,u"日本語")
        menu_lang.AppendRadioItem(2,u"English")

        self.menu_bar.Append(self.menu_about,u"Help")
        self.menu_about.Append(3,u"Documents")
        self.menu_about.Append(4,u"Version Info")
        self.frame.Bind(wx.EVT_MENU,self.selectMenu)

    def addExtentionComboBox(self):
        self.getExtensionlist()
        element_array = list(self.extensions.keys())
        self.combobox_extensions = wx.ComboBox(self.panel,wx.ID_ANY,u"select extension",choices=element_array,style=wx.CB_READONLY)
        self.combobox_extensions.Bind(wx.EVT_COMBOBOX,self.extentions_combobox_select)

    def extentions_combobox_select(self,event):
        val = event.GetEventObject().GetStringSelection()
        self.sock_port = int(self.extensions[val])
        self.selectflg[1] = 1
        if self.selectflg[0] == 1:
            self.button.Enable()

    def addPortList(self):
        element_array = self.ports
        self.combobox_ports = wx.ComboBox(self.panel,wx.ID_ANY,u"select Extension",choices=element_array,style=wx.CB_READONLY)
        self.combobox_ports.Bind(wx.EVT_COMBOBOX,self.ports_combobox_select)

    def ports_combobox_select(self,event):
        obj = event.GetEventObject()
        self.port = obj.GetStringSelection()
        self.selectflg[0] = 1
        if self.selectflg[1] == 1:
            self.button.Enable()

    def addConnectButton(self):
        self.button = wx.Button(self.panel,wx.ID_ANY,self.jsonData[self.lang][u"connect"])
        self.button.Bind(wx.EVT_BUTTON,self.click_button)
        self.button.Disable()

    def addRefreshButton(self):
        self.button2 = wx.Button(self.panel,wx.ID_ANY,self.jsonData[self.lang][u"refresh"])
        self.button2.Bind(wx.EVT_BUTTON,self.click_refresh)

    def main(self):
        app = wx.App()
        self.frame = wx.Frame(None, wx.ID_ANY, u'Scratio',size=(300,290))
        #self.frame = wx.Frame(None, wx.ID_ANY, u'Scratio')

        application = wx.App()

        icon = wx.Icon(self.icon,wx.BITMAP_TYPE_ICO)

        self.panel = wx.Panel(self.frame,wx.ID_ANY)
        self.panel.SetBackgroundColour("#AFAFAF")

        #add menu
        self.addMenu()

        #add Extention selector
        self.addExtentionComboBox()

        #add Serial Port selector
        self.s_text_extension = wx.StaticText(self.panel,wx.ID_ANY,self.jsonData[self.lang][u"extension"])
        self.s_text_serial = wx.StaticText(self.panel,wx.ID_ANY,self.jsonData[self.lang][u"serial"])

        #add Port list
        self.addPortList()

        #add connect button
        self.addRefreshButton()

        #add connect button
        self.addConnectButton()

        layout = wx.BoxSizer(wx.VERTICAL)
        layout.Add(self.s_text_extension,flag=wx.GROW|wx.LEFT|wx.TOP,border=10)
        layout.Add(self.combobox_extensions,flag=wx.GROW|wx.ALL,border=10)
        layout.Add(self.s_text_serial,flag=wx.GROW|wx.LEFT|wx.TOP,border=10)
        layout.Add(self.combobox_ports,flag=wx.GROW|wx.ALL,border=10)
        layout.Add(self.button2,flag=wx.GROW|wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT|wx.BOTTOM,border=10)
        layout.Add(self.button,flag=wx.GROW|wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT|wx.BOTTOM,border=10)

        self.frame.SetIcon(icon)
        self.panel.SetSizer(layout)
        self.frame.SetMenuBar(self.menu_bar)
        self.frame.Show()
        application.MainLoop()

    def close(self):
        if self.oflg == 1:
            self.server.close()
            self.oflg = 0

if __name__ == '__main__':
    if hasattr(time, 'tzset'):
        os.environ['TZ'] = 'Asia/Tokyo'
        time.tzset()
    log_fmt = '%(asctime)s- %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=log_fmt, filename='scratio.log', filemode='a')
    #logging.info("start")
    scratio = scratio()
    scratio.main()
