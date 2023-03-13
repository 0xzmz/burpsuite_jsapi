# coding=utf-8
# Burp Extension - JsApi
# Copyright : 0x_zmz <github.com/0x-zmz>

import json
import re

from burp import IBurpExtender
from burp import IMessageEditorTabFactory
from burp import IMessageEditorTab
from burp import IParameter
from burp import IContextMenuFactory

# Java imports
from javax.swing import JMenuItem
from java.util import List, ArrayList

# Menu items
menuItems = {
    False: "Turn JsApi active detection on",
    True: "Turn JsApi active detection off"
}

# Global Switch
_forceJsApi = False

print("Burp Extension - JsApi\nUsed to find API interface in JS file.\nBy 0x_zmz <github.com/0x-zmz>")

class BurpExtender(IBurpExtender, IMessageEditorTabFactory, IContextMenuFactory):
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()

        callbacks.setExtensionName('JsApi')
        callbacks.registerMessageEditorTabFactory(self)
        callbacks.registerContextMenuFactory(self)

        return

    def createNewInstance(self, controller, editable):
        return JsApiTab(self, controller, editable)

    def createMenuItems(self, IContextMenuInvocation):
        global _forceJsApi
        menuItemList = ArrayList()
        menuItemList.add(JMenuItem(menuItems[_forceJsApi], actionPerformed=self.onClick))

        return menuItemList

    def onClick(self, event):
        global _forceJsApi
        _forceJsApi = not _forceJsApi


class JsApiTab(IMessageEditorTab):
    def __init__(self, extender, controller, editable):
        self._extender = extender
        self._helpers = extender._helpers
        self._editable = editable

        self._txtInput = extender._callbacks.createTextEditor()
        self._txtInput.setEditable(editable)

        self._jsonMagicMark = ['{"', '["', '[{']
        self.api_regex = r"[\"|\'](\/[a-zA-Z0-9|\/]+)[\"|\']"
        return

    def getTabCaption(self):
        return "JsApi"

    def getUiComponent(self):
        return self._txtInput.getComponent()

    def isEnabled(self, content, isRequest):
        global _forceJsApi

        if isRequest:
            r = self._helpers.analyzeRequest(content)
        else:
            r = self._helpers.analyzeResponse(content)

        msg = content[r.getBodyOffset():].tostring()
        matches = re.findall(self.api_regex, msg, re.MULTILINE)

        #
        # if matches:
        #     return True

        # 下面这个判断是限制必须是js文件并且匹配到才显示，如果不想只限定js文件，取消注释上面2句话即可
        for header in r.getHeaders():
            if header.lower().startswith("content-type:"):
                content_type = header.split(":")[1].lower()
                return bool(content_type.find("/javascript") > 0 and matches)
        return False

    def setMessage(self, content, isRequest):
        if content is None:
            self._txtInput.setText(None)
            self._txtInput.setEditable(False)
        else:
            if isRequest:
                r = self._helpers.analyzeRequest(content)
            else:
                r = self._helpers.analyzeResponse(content)

            msg = content[r.getBodyOffset():].tostring()
            api_list = []
            matches = re.finditer(self.api_regex, msg, re.MULTILINE)
            for matchNum, match in enumerate(matches, start=1):
                for groupNum in range(len(match.groups())):
                    groupNum = groupNum + 1
                    # print(match.group(groupNum))
                    api = match.group(groupNum)
                    if api.replace("/", ""):
                        api_list.append(api)
            # 去重
            # Remove duplication
            api_list = list(set(api_list))
            pretty_msg = ",\n".join(api_list)

            self._txtInput.setText(pretty_msg)
            self._txtInput.setEditable(self._editable)

        self._currentMessage = content
        return

    def getMessage(self):
        if not self._txtInput.isTextModified():
            return self._currentMessage
        try:
            pre_data = self._txtInput.getText()
            garbage = pre_data[:pre_data.find("{")]
            clean = pre_data[pre_data.find("{"):]
            data = garbage + json.dumps(json.loads(clean))
        except:
            data = self._helpers.bytesToString(self._txtInput.getText())

        # Reconstruct request/response
        r = self._helpers.analyzeRequest(self._currentMessage)

        return self._helpers.buildHttpMessage(r.getHeaders(), self._helpers.stringToBytes(data))

    def isModified(self):
        return self._txtInput.isTextModified()

    def getSelectedData(self):
        return self._txtInput.getSelectedText()
