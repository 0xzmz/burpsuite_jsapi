# coding=utf-8
"""Burp Suite extension for extracting API endpoints from JavaScript files.

The extension is intentionally compatible with Jython 2.7, which is still the
runtime used by Burp Suite's legacy Python extender support.
"""

import re

from burp import IBurpExtender
from burp import IContextMenuFactory
from burp import IMessageEditorTab
from burp import IMessageEditorTabFactory

from java.util import ArrayList
from javax.swing import JMenuItem


EXTENSION_NAME = "JsApi"
MENU_LABELS = {
    False: "Turn JsApi active detection on",
    True: "Turn JsApi active detection off",
}

JAVASCRIPT_CONTENT_TYPES = (
    "application/javascript",
    "application/ecmascript",
    "application/x-javascript",
    "text/javascript",
    "text/ecmascript",
)

API_PATTERN = re.compile(
    r"""["']((?:https?:)?//[^"'\\\s<>]+|/[A-Za-z0-9._~%-][^"'\\\s<>]*)["']""",
    re.MULTILINE,
)

_force_jsapi = False


class BurpExtender(IBurpExtender, IMessageEditorTabFactory, IContextMenuFactory):
    """Register the JsApi message editor tab and context menu switch."""

    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()

        callbacks.setExtensionName(EXTENSION_NAME)
        callbacks.registerMessageEditorTabFactory(self)
        callbacks.registerContextMenuFactory(self)
        callbacks.printOutput(
            "Burp Extension - {0}\n"
            "Used to find API endpoints in JavaScript files.\n"
            "By 0x_zmz <github.com/0xzmz>".format(EXTENSION_NAME)
        )

    def createNewInstance(self, controller, editable):
        return JsApiTab(self, controller)

    def createMenuItems(self, invocation):
        menu_item_list = ArrayList()
        menu_item_list.add(
            JMenuItem(MENU_LABELS[_force_jsapi], actionPerformed=self.onClick)
        )
        return menu_item_list

    def onClick(self, event):
        global _force_jsapi
        _force_jsapi = not _force_jsapi
        state = "enabled" if _force_jsapi else "disabled"
        self._callbacks.printOutput("JsApi active detection {0}.".format(state))


class JsApiTab(IMessageEditorTab):
    """Read-only editor tab that lists endpoints found in a message body."""

    def __init__(self, extender, controller):
        self._helpers = extender._helpers
        self._current_message = None

        self._txt_input = extender._callbacks.createTextEditor()
        self._txt_input.setEditable(False)

    def getTabCaption(self):
        return EXTENSION_NAME

    def getUiComponent(self):
        return self._txt_input.getComponent()

    def isEnabled(self, content, isRequest):
        if content is None:
            return False

        message_info = self._analyze_message(content, isRequest)
        body = self._get_body(content, message_info)
        endpoints = self._extract_endpoints(body)

        if not endpoints:
            return False

        return _force_jsapi or self._is_javascript_message(message_info)

    def setMessage(self, content, isRequest):
        self._current_message = content

        if content is None:
            self._txt_input.setText(None)
            return

        message_info = self._analyze_message(content, isRequest)
        body = self._get_body(content, message_info)
        endpoints = self._extract_endpoints(body)
        self._txt_input.setText("\n".join(endpoints))
        self._txt_input.setEditable(False)

    def getMessage(self):
        return self._current_message

    def isModified(self):
        return False

    def getSelectedData(self):
        return self._txt_input.getSelectedText()

    def _analyze_message(self, content, is_request):
        if is_request:
            return self._helpers.analyzeRequest(content)
        return self._helpers.analyzeResponse(content)

    def _get_body(self, content, message_info):
        body_offset = message_info.getBodyOffset()
        return self._helpers.bytesToString(content[body_offset:])

    def _extract_endpoints(self, body):
        endpoints = []
        seen = set()

        for match in API_PATTERN.finditer(body):
            endpoint = match.group(1).strip()
            if endpoint and endpoint not in seen:
                seen.add(endpoint)
                endpoints.append(endpoint)

        return endpoints

    def _is_javascript_message(self, message_info):
        for header in message_info.getHeaders():
            if not header.lower().startswith("content-type:"):
                continue

            content_type = (
                header.split(":", 1)[1].split(";", 1)[0].strip().lower()
            )
            return content_type in JAVASCRIPT_CONTENT_TYPES

        return False
