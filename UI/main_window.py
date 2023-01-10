# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Voice_Translator.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.

import time
import wave
import pyaudio
import pygame
import os

from os import path
from TTSTechmo.synthesize import synthesize
from TTSTechmo.settings import setup
from EasyNMT.translator import Translator
from Whisper.whisper_class import Whisper
from PyQt5 import QtCore, QtGui, QtWidgets  

class Ui_main_window(object):
    def __init__(self):
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 2
        self.rate = 44100
        self.file_path = 'Whisper/whisper_records/transcribtion.wav'
        self.settings = setup()
        self.asr_model = Whisper()
        self.nmt_model = Translator()
    def RecordInput(self):
        self.data_box.setText("This is recorder window\nPlease say word(s) to microphone\nPress ESC to end recording\nAfter recording - please wait, the processing will be in motion")
        pygame.init()
        screen = pygame.display.set_mode((5, 5))
        pygame.display.set_caption('Recorder')
        app_running=True
        p = pyaudio.PyAudio()

        stream = p.open(format=self.format,
                        channels=self.channels,
                        rate=self.rate,
                        input=True,
                        frames_per_buffer=self.chunk)

        frames = []

        while app_running:
                events = pygame.event.get()
                data = stream.read(self.chunk)
                frames.append(data)
                for e in events:
                    if e.type == pygame.QUIT:
                        app_running = False
                        break
                    elif e.type == pygame.KEYDOWN:
                        if e.key == pygame.K_ESCAPE:
                            app_running = False
                            break
        pygame.quit()

        sample_width = p.get_sample_size(self.format)

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(self.file_path, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(frames))
        wf.close()

        transcription, asr_time = self.asr_model.full_transcription()
        self.input_text_line_edit.setText(transcription)
        self.settings.text_to_translate = transcription
        self.data_box.setText("Processing has finished\nYour text should be in display box above\nTime of ASR process : " + str(asr_time))

    def PlaySynthesis(self):
        if path.exists("TTSTechmo/synthesis_records/synthesis.wav") == True:
            chunk=1024
            file = wave.open("TTSTechmo/synthesis_records/synthesis.wav","rb") 
            p = pyaudio.PyAudio()
            stream = p.open(format = p.get_format_from_width(file.getsampwidth()),  
                    channels = file.getnchannels(),  
                    rate = file.getframerate(),  
                    output = True)
            data = file.readframes(chunk)
            while data:  
                stream.write(data)  
                data = file.readframes(chunk)   
            stream.stop_stream()  
            stream.close()      
            p.terminate()
        elif path.exists("TTSTechmo/synthesis_records/synthesis.wav") == False:
            self.data_box.setText("There is no voice synthesis to listen. It is likely that no synthesis was carried out.")
    def SetInputText(self):
        self.settings.text_to_translate = self.input_text_line_edit.toPlainText()  
    def SetInputLanguage(self):
        if self.source_language_box.currentText() == "English":
            self.settings.language_source = 'en'
        elif self.source_language_box.currentText() == "Polish":
            self.settings.language_source = 'pl'
        elif self.source_language_box.currentText() == "Spanish":
            self.settings.language_source = 'es'
    def SetTranslationLanguage(self):
        if self.translation_language_box.currentText() == "English":
            self.settings.language = 'en'
            self.settings.tts_lang = 'tts-en'
        elif self.translation_language_box.currentText() == "Polish":
            self.settings.language = 'pl'
            self.settings.tts_lang = 'tts-pl'
        elif self.translation_language_box.currentText() == "Spanish":
            self.settings.language = 'es'
    def Translate(self):
        if self.input_text_line_edit.toPlainText() != "":
            if path.exists("TTSTechmo/synthesis_records/synthesis.wav") == True:
                os.remove("TTSTechmo/synthesis_records/synthesis.wav")
            t = time.time()
            self.settings.text = self.nmt_model.translate(self.settings.text_to_translate, self.settings.language_source, self.settings.language)
            self.output_text_edit.setText(self.settings.text)
            elapsed = time.time() - t
            self.data_box.setText("Elapsed time of operation : " + str(elapsed))
        else:
            self.data_box.setText("There is no translation text. Please write something or record your speech.")
    def TranslateAndSynthesize(self):
        if self.input_text_line_edit.toPlainText() != "":
            if path.exists("TTSTechmo/synthesis_records/synthesis.wav") == True:
                os.remove("TTSTechmo/synthesis_records/synthesis.wav")
            t = time.time()
            self.settings.text = self.nmt_model.translate(self.settings.text_to_translate, self.settings.language_source, self.settings.language)
            self.output_text_edit.setText(self.settings.text)
            tsynt = time.time()
            synthesize(self.settings)
            elapsed = time.time() - t
            elapsedsynt = time.time() - tsynt
            if path.exists("TTSTechmo/synthesis_records/synthesis.wav") == True:
                self.data_box.setText("Elapsed time of operation : " + str(elapsed) + "\nSynthesis elapsed time : " + str(elapsedsynt) + "\nTranslation elapsed time : " + str(elapsed - elapsedsynt))
            elif path.exists("TTSTechmo/synthesis_records/synthesis.wav") == False:
                self.data_box.setText("Sorry, but it seems that TTS service is unreachable right now, please try again later.\nTranslation elapsed time : " + str(elapsed - elapsedsynt))
        else:
            self.data_box.setText("There is no translation text. Please write something or record your speech.")    
    def ReplaceLanguages(self):
        source_lang = self.source_language_box.currentIndex()
        self.source_language_box.setCurrentIndex(self.translation_language_box.currentIndex())
        self.translation_language_box.setCurrentIndex(source_lang)
        self.SetInputLanguage()
        self.SetTranslationLanguage()
    def setupUi(self, main_window):
        main_window.setObjectName("main_window")
        main_window.resize(1025, 480)
        main_window.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        main_window.setDocumentMode(False)
        main_window.setDockNestingEnabled(False)
        self.main_widget = QtWidgets.QWidget(main_window)
        self.main_widget.setObjectName("main_widget")
        self.output_text_edit = QtWidgets.QTextEdit(self.main_widget)
        self.output_text_edit.setGeometry(QtCore.QRect(360, 200, 651, 111))
        self.output_text_edit.setFrameShape(QtWidgets.QFrame.WinPanel)
        self.output_text_edit.setFrameShadow(QtWidgets.QFrame.Raised)
        self.output_text_edit.setTextInteractionFlags(QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.output_text_edit.setObjectName("output_text_edit")
        self.data_box = QtWidgets.QTextEdit(self.main_widget)
        self.data_box.setGeometry(QtCore.QRect(20, 360, 991, 71))
        self.data_box.setFrameShape(QtWidgets.QFrame.WinPanel)
        self.data_box.setFrameShadow(QtWidgets.QFrame.Raised)
        self.data_box.setTextInteractionFlags(QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.data_box.setObjectName("data_box")
        self.source_language_box = QtWidgets.QComboBox(self.main_widget)
        self.source_language_box.setGeometry(QtCore.QRect(20, 40, 231, 31))
        self.source_language_box.setObjectName("source_language_box")
        self.source_language_box.addItem("")
        self.source_language_box.addItem("")
        self.source_language_box.addItem("")
        self.translation_language_box = QtWidgets.QComboBox(self.main_widget)
        self.translation_language_box.setGeometry(QtCore.QRect(20, 120, 231, 31))
        self.translation_language_box.setObjectName("translation_language_box")
        self.translation_language_box.addItem("")
        self.translation_language_box.addItem("")
        self.translation_language_box.addItem("")
        self.data_label = QtWidgets.QLabel(self.main_widget)
        self.data_label.setGeometry(QtCore.QRect(20, 330, 991, 21))
        self.data_label.setFrameShape(QtWidgets.QFrame.WinPanel)
        self.data_label.setFrameShadow(QtWidgets.QFrame.Raised)
        self.data_label.setAlignment(QtCore.Qt.AlignCenter)
        self.data_label.setObjectName("data_label")
        self.output_text_label = QtWidgets.QLabel(self.main_widget)
        self.output_text_label.setGeometry(QtCore.QRect(360, 170, 651, 21))
        self.output_text_label.setFrameShape(QtWidgets.QFrame.WinPanel)
        self.output_text_label.setFrameShadow(QtWidgets.QFrame.Raised)
        self.output_text_label.setAlignment(QtCore.Qt.AlignCenter)
        self.output_text_label.setObjectName("output_text_label")
        self.language_choice_label = QtWidgets.QLabel(self.main_widget)
        self.language_choice_label.setGeometry(QtCore.QRect(10, 10, 251, 21))
        self.language_choice_label.setFrameShape(QtWidgets.QFrame.WinPanel)
        self.language_choice_label.setFrameShadow(QtWidgets.QFrame.Raised)
        self.language_choice_label.setAlignment(QtCore.Qt.AlignCenter)
        self.language_choice_label.setObjectName("language_choice_label")
        self.label_6 = QtWidgets.QLabel(self.main_widget)
        self.label_6.setGeometry(QtCore.QRect(420, 270, 47, 13))
        self.label_6.setText("")
        self.label_6.setObjectName("label_6")
        self.to_label = QtWidgets.QLabel(self.main_widget)
        self.to_label.setGeometry(QtCore.QRect(50, 80, 81, 31))
        self.to_label.setFrameShape(QtWidgets.QFrame.WinPanel)
        self.to_label.setFrameShadow(QtWidgets.QFrame.Raised)
        self.to_label.setAlignment(QtCore.Qt.AlignCenter)
        self.to_label.setObjectName("to_label")
        self.translate_button = QtWidgets.QPushButton(self.main_widget)
        self.translate_button.setGeometry(QtCore.QRect(20, 260, 191, 51))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.translate_button.setPalette(palette)
        self.translate_button.setObjectName("translate_button")
        self.translate_and_synthesize_button = QtWidgets.QPushButton(self.main_widget)
        self.translate_and_synthesize_button.setGeometry(QtCore.QRect(20, 200, 191, 51))
        self.translate_and_synthesize_button.setObjectName("translate_and_synthesize_button")
        self.replace_button = QtWidgets.QPushButton(self.main_widget)
        self.replace_button.setGeometry(QtCore.QRect(150, 80, 81, 31))
        self.replace_button.setObjectName("replace_button")
        self.play_synthesis_button = QtWidgets.QPushButton(self.main_widget)
        self.play_synthesis_button.setGeometry(QtCore.QRect(230, 200, 101, 111))
        self.play_synthesis_button.setObjectName("play_synthesis_button")
        self.record_button = QtWidgets.QPushButton(self.main_widget)
        self.record_button.setGeometry(QtCore.QRect(270, 40, 75, 111))
        self.record_button.setObjectName("record_button")
        self.input_voice_label = QtWidgets.QLabel(self.main_widget)
        self.input_voice_label.setGeometry(QtCore.QRect(270, 10, 81, 21))
        self.input_voice_label.setFrameShape(QtWidgets.QFrame.WinPanel)
        self.input_voice_label.setFrameShadow(QtWidgets.QFrame.Raised)
        self.input_voice_label.setAlignment(QtCore.Qt.AlignCenter)
        self.input_voice_label.setObjectName("input_voice_label")
        self.input_text_line_edit = QtWidgets.QTextEdit(self.main_widget)
        self.input_text_line_edit.setGeometry(QtCore.QRect(360, 40, 651, 111))
        self.input_text_line_edit.setFrameShape(QtWidgets.QFrame.WinPanel)
        self.input_text_line_edit.setFrameShadow(QtWidgets.QFrame.Raised)
        self.input_text_line_edit.setObjectName("input_text_line_edit")
        self.input_text_label = QtWidgets.QLabel(self.main_widget)
        self.input_text_label.setGeometry(QtCore.QRect(360, 10, 651, 21))
        self.input_text_label.setFrameShape(QtWidgets.QFrame.WinPanel)
        self.input_text_label.setFrameShadow(QtWidgets.QFrame.Raised)
        self.input_text_label.setAlignment(QtCore.Qt.AlignCenter)
        self.input_text_label.setObjectName("input_text_label")
        self.output_text_label_2 = QtWidgets.QLabel(self.main_widget)
        self.output_text_label_2.setGeometry(QtCore.QRect(20, 170, 321, 21))
        self.output_text_label_2.setFrameShape(QtWidgets.QFrame.WinPanel)
        self.output_text_label_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.output_text_label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.output_text_label_2.setObjectName("output_text_label_2")
        main_window.setCentralWidget(self.main_widget)
        self.menubar = QtWidgets.QMenuBar(main_window)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1025, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuSettings = QtWidgets.QMenu(self.menubar)
        self.menuSettings.setObjectName("menuSettings")
        main_window.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(main_window)
        self.statusbar.setObjectName("statusbar")
        main_window.setStatusBar(self.statusbar)
        self.actionImport = QtWidgets.QAction(main_window)
        self.actionImport.setObjectName("actionImport")
        self.actionExport = QtWidgets.QAction(main_window)
        self.actionExport.setObjectName("actionExport")
        self.actionExit = QtWidgets.QAction(main_window)
        self.actionExit.setObjectName("actionExit")
        self.actionSynthesis_Options = QtWidgets.QAction(main_window)
        self.actionSynthesis_Options.setObjectName("actionSynthesis_Options")
        self.menuFile.addAction(self.actionImport)
        self.menuFile.addAction(self.actionExport)
        self.menuFile.addAction(self.actionExit)
        self.menuFile.addSeparator()
        self.menuSettings.addAction(self.actionSynthesis_Options)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuSettings.menuAction())

        self.retranslateUi(main_window)
        self.source_language_box.currentIndexChanged['QString'].connect(main_window.SetInputLanguage) # type: ignore
        self.translation_language_box.currentIndexChanged['QString'].connect(main_window.SetTranslationLanguage) # type: ignore
        self.translate_button.clicked.connect(main_window.Translate) # type: ignore
        self.translate_and_synthesize_button.clicked.connect(main_window.TranslateAndSynthesize) # type: ignore
        self.input_text_line_edit.textChanged.connect(main_window.SetInputText) # type: ignore
        self.replace_button.clicked.connect(main_window.ReplaceLanguages) # type: ignore
        self.play_synthesis_button.clicked.connect(main_window.PlaySynthesis) # type: ignore
        self.record_button.clicked.connect(main_window.RecordInput) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def retranslateUi(self, main_window):
        _translate = QtCore.QCoreApplication.translate
        main_window.setWindowTitle(_translate("main_window", "MainWindow"))
        self.source_language_box.setItemText(0, _translate("main_window", "English"))
        self.source_language_box.setItemText(1, _translate("main_window", "Polish"))
        self.source_language_box.setItemText(2, _translate("main_window", "Spanish"))
        self.translation_language_box.setItemText(0, _translate("main_window", "English"))
        self.translation_language_box.setItemText(1, _translate("main_window", "Polish"))
        self.translation_language_box.setItemText(2, _translate("main_window", "Spanish"))
        self.data_label.setText(_translate("main_window", "Commends and info"))
        self.output_text_label.setText(_translate("main_window", "Output text - translation"))
        self.language_choice_label.setText(_translate("main_window", "Language Choice"))
        self.to_label.setText(_translate("main_window", "To"))
        self.translate_button.setText(_translate("main_window", "Translate"))
        self.translate_and_synthesize_button.setText(_translate("main_window", "Translate and Synthesize \n"
" (not available for Spanish)"))
        self.replace_button.setText(_translate("main_window", "Replace"))
        self.play_synthesis_button.setText(_translate("main_window", "Play \n"
" Translation"))
        self.record_button.setText(_translate("main_window", "Record"))
        self.input_voice_label.setText(_translate("main_window", "Voice Input"))
        self.input_text_label.setText(_translate("main_window", "Input Text"))
        self.output_text_label_2.setText(_translate("main_window", "Translation and Synthesis"))
        self.menuFile.setTitle(_translate("main_window", "File"))
        self.menuSettings.setTitle(_translate("main_window", "Settings"))
        self.actionImport.setText(_translate("main_window", "Import"))
        self.actionExport.setText(_translate("main_window", "Export"))
        self.actionExit.setText(_translate("main_window", "Exit"))
        self.actionSynthesis_Options.setText(_translate("main_window", "Synthesis Options"))
