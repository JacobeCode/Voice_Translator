# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'VT_ui.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.

from TTSTechmo.synthesize import synthesize
from TTSTechmo.settings import setup
from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Voice_Translator(object):
    settings = setup()
    def SynthesisFunction(self):
        synthesize(self.settings)
    def GenderPickFunction(self):
        if str(self.GenderComboBox.currentText()) == "Male":
            self.settings.voice_gender = "male"
        elif str(self.GenderComboBox.currentText()) == "Female":
            self.settings.voice_gender = "female"
    def AgePickFunction(self):
        pass
    def SpeechPitchPickFunction(self):
        pass
    def SpeechRatePickFunction(self):
        pass
    def SpeechVolumePickFunction(self):
        pass
    def FolderPickFunction(self):
        pass
    def SamplingFreqPickFunction(self):
        pass
    def AudioEncodingPickFunction(self):
        pass
    def SynthesisTextChangeFunction(self):
        self.settings.text = self.lineEdit_2.text()
    def LanguagePickFunction(self):
        pass