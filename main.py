
'''
Widget animation
================

This example demonstrates creating and applying a multi-part animation to
a button widget. You should see a button labelled 'plop' that will move with
an animation when clicked.
'''

import kivy
kivy.require('1.0.7')

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput

from jnius import autoclass, cast

import functools
import time


class TestApp(App):

    def load(self, _):
        try:
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Calls = autoclass('android.provider.CallLog.Calls')
            currentActivity = cast('android.app.Activity', PythonActivity.mActivity)
            # context = cast('android.content.Context', currentActivity.getApplicationContext())
            cursor = cast(
                'android.database.Interfaces.Cursor',
                currentActivity.getApplicationContext().getContentResolver().query(
                    Calls.CONTENT_URI, [CallLog.Calls.NUMBER], None, None, None
                )

            )
            self.txt.text += str(cursor)
            self.txt.text += '\n'

        except Exception as e:
            self.txt.text += str(type(e))
            self.txt.text += '\n'
            self.txt.text += type(e)

    def build(self):
        acquire_permissions(['android.permission.READ_CALL_LOG'])
        # create a button, and  attach animate() method as a on_press handler
        button = Button(size_hint=(None, None), text='plop')
        layout = BoxLayout(orientation='vertical')
        btn1 = Button(text='Load', on_press=self.load)
        self.txt = TextInput(text='', multiline=True, readonly=True)
        layout.add_widget(btn1)
        layout.add_widget(self.txt)
        return layout

def acquire_permissions(permissions, timeout=30):
    """
    blocking function for acquiring storage permission

    :param permissions: list of permission strings , e.g. ["android.permission.READ_EXTERNAL_STORAGE",]
    :param timeout: timeout in seconds
    :return: True if all permissions are granted
    """

    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Compat = autoclass('android.support.v4.content.ContextCompat')
    currentActivity = cast('android.app.Activity', PythonActivity.mActivity)

    checkperm = functools.partial(Compat.checkSelfPermission, currentActivity)

    def allgranted(permissions):
        """
        helper function checks permissions
        :param permissions: list of permission strings
        :return: True if all permissions are granted otherwise False
        """
        return functools.reduce(lambda a, b: a and b,
                    [True if p == 0 else False for p in map(checkperm, permissions)]
                    )

    haveperms = allgranted(permissions)
    if haveperms:
        # we have the permission and are ready
        return True

    # invoke the permissions dialog
    currentActivity.requestPermissions(permissions, 0)

    # now poll for the permission (UGLY but we cant use android Activity's onRequestPermissionsResult)
    t0 = time.time()
    while time.time() - t0 < timeout and not haveperms:
        # in the poll loop we could add a short sleep for performance issues?
        haveperms = allgranted(permissions)

    return haveperms

if __name__ == '__main__':
    TestApp().run()

