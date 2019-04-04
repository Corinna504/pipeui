#############################################################################
##
## Author: Corinna Lorenz
## Date: 02/2019
## Contact: corinna@ini.ethz.ch
##
#############################################################################
"""PySide2 portfrom Qt v5.x"""

# the usual
import numpy as np
import pandas as pd
from importlib import reload


# graphic modules from PySide2 
from PySide2 import QtGui, QtWidgets
from PySide2.QtMultimedia import (QAudio, QAudioDeviceInfo, QAudioFormat, QAudioInput)
from PySide2.QtCore import QPointF, QRect, QSize
from PySide2.QtCharts import QtCharts

# recording modules from pipefinch
from pipefinch import pipeline


#reload(et)
sess_par = {'bird': 'p14r14',
           'sess': '2019-02-15_3125_0102'}
#kwik_folder = exp_struct['folders']['kwik']
#kwd_path = exp_struct['files']['kwd']
nchan = 3
#exp_struct = et.get_exp_struct(sess_par['bird'], sess_par['sess'])

resolution = 4
sampleCount = 2000


# the main window
class ZeguiWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(ZeguiWindow, self).__init__()
        self.setWindowTitle("Zegui")

        # microphone input (placeholder for the data streams)
        self.audioDevice = QAudioDeviceInfo.defaultInputDevice()
        if (self.audioDevice.isNull()):
            QMessageBox.warning(None, "audio", "There is no audio input device available.")
            sys.exit(-1)

        # File information
        #self.currSession = RecordingSession('','')

        # Status bar
        self.status = self.statusBar()

        # Menu
        self.createActions()
        self.createMenu()

        # Window dimension
        geometry = app.desktop().availableGeometry(self)
        self.setFixedSize(geometry.width() * 0.8, geometry.height() * 0.7)

        # Widget with panels
        self.zewidget = ZeWidget(self.audioDevice)
        self.setCentralWidget(self.zewidget)


    #$ Application menu
    def createMenu(self):
        self.menu = self.menuBar().addMenu("&File")
        self.menu.addAction(self.newAct)
        self.menu.addAction(self.openAct)
        self.menu.addAction(self.updateAct)
        self.menu.addAction(self.settingsAct)
        self.menu.addAction(self.saveAct)
        self.menu.addAction(self.exitAct)


    #$ Menu actions...
    def createActions(self):
        self.newAct = QtWidgets.QAction("&New", self, shortcut="Ctrl+N",
                statusTip="Create a new .kwd file from raw data", triggered=self.newFile)
        self.openAct = QtWidgets.QAction("Open", self, shortcut="Ctrl+O",
                statusTip="Open an existing .kwd file", triggered=self.openFile)
        self.updateAct = QtWidgets.QAction("Update", self, shortcut="Ctrl+U",
                statusTip="Update the current file (during recording only)", triggered=self.updateFile)
        self.settingsAct = QtWidgets.QAction("Create", self, shortcut="Ctrl+J",
                statusTip="Create settings.json", triggered=self.setjson)
        self.saveAct = QtWidgets.QAction("Save", self, shortcut="Ctrl+S",
                statusTip="Save as .kwd file", triggered=self.saveFile)
        self.exitAct = QtWidgets.QAction("E&xit", self, shortcut="Ctrl+Q",
                statusTip="Exit the application", triggered=self.close)


    #$ ... open a file
    def openFile(self):
        self.status.showMessage("loading file")
        fileDir, fileName = QtWidgets.QFileDialog.getOpenFileName(self,
                "Open kwd file", "home", self.currSession.fileName)
        if fileName:
            #self.currSession = RecordingSession(fileDir, fileName)
            #self.zewidget.loadFile(self.currSession)

            self.status.showMessage("loading " + fileName + " in " + fileDir + " ...")


    #$ ... create a new file from raw recording data
    def newFile(self):
        # todo
        # get directory
        sessionDir = QtWidgets.QFileDialog.getExistingDirectory(self)
        # ezequiels code for reading
        #self.currSession.createKWD()

        # load in zewidget
        #self.zewidget.loadFile(self.currDir, self.currFile)
        self.status.showMessage("creating a new file")


    #$ ... update the current file by appending new recordings
    def updateFile(self):
        # todo
        # convert and add new recording files from the given directory to the current kwd file
        self.status.showMessage("update current file")


    #$ ... save the file
    def saveFile(self):
        # todo
        self.status.showMessage("saving")

    #$ ... create/set json file for setting parameters (to be used when creating the file or while the experiment runs)
    def setjson(self):
        # todo
        self.status.showMessage("create settings.json file")


#---------------------------------------------
# show and stream data  
# this class handles the file structure, its loading and processing
# processed data are handed to Zeraster and Zestreamwidget
#---------------------------------------------
class ZeWidget(QtWidgets.QWidget):
    def __init__(self, inputDevice):
        super(ZeWidget, self).__init__()

        # File specific variables''
        
        self.numberChannels = nchan
        self.allRec = [];
        self.curChannels = [1, 2, 3]

        self.audioDevice = inputDevice

        self.createStreamingGroup()
        self.createRasterGroup()

        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.streamingBox, 0, 0, 2, 2)
        layout.addWidget(self.rasterBox, 0, 2, 1, 1)
        self.setLayout(layout)


    #$ Panel of spiking events (aka spike raster)
    def createRasterGroup(self):
        self.rasterBox = QtWidgets.QGroupBox("spike raster")
        layout = QtWidgets.QGridLayout()

        for i in self.curChannels:
            button = QtWidgets.QPushButton("Button %d" % (i + 3))
            layout.addWidget(button)

        self.rasterBox.setLayout(layout)


    #$ Panel of data streams
    def createStreamingGroup(self):
        self.streamingBox = QtWidgets.QGroupBox("data streams")
        layout = QtWidgets.QVBoxLayout()

        for i in self.curChannels:
            button = QtWidgets.QPushButton("Button %d" % (i + 1))
            layout.addWidget(button)

        self.chartWidget = ZeStreamWidget(self.audioDevice, "Default mic",
            [0, sampleCount], [-1,1])
        self.chart = self.chartWidget.chart
        self.chartView = QtCharts.QChartView(self.chart)
        layout.addWidget(self.chartView)

        self.chartWidget2 = ZeStreamWidget(self.audioDevice, "Default mic2",
            [0, sampleCount], [-1,1])
        self.chart2 = self.chartWidget2.chart
        self.chartView2 = QtCharts.QChartView(self.chart2)
        layout.addWidget(self.chartView2)

        self.streamingBox.setLayout(layout)


    #$ how to load the file, who should have access to it?
    #def loadFile(fileDir, fileName):
        #self.allRec = self.get_all_rec_meta(exp_struct['files']['kwd'])
        


#class ZeRasterWidget(QtWidgets.QWidget):
#    def __init__(self, stream, trigger, xlim):
#        super(ZeRasterWidget, self).__init__()
#
#        self.stream = stream # data stream for one channel of each recording file, format?
#        self.trigger = trigger # trigger times, format?


#$ -------------------------------------------------------------------------
class ZeStreamWidget(QtWidgets.QWidget):
    def __init__(self, inputDevice, title, xlim, ylim):
        super(ZeStreamWidget, self).__init__()

        self.inputDevice = inputDevice

        # Creating QChart
        self.series = QtCharts.QLineSeries()
        self.chart = QtCharts.QChart()
        self.chart.addSeries(self.series)

        self.axisX = QtCharts.QValueAxis()
        self.axisX.setRange(0, sampleCount)
        self.axisX.setLabelFormat("%g")
        self.axisX.setTitleText("Samples")
        self.chart.setAxisX(self.axisX, self.series)

        self.axisY = QtCharts.QValueAxis()
        self.axisY.setRange(-1, 1)
        self.chart.setAxisY(self.axisY, self.series)

        self.chart.legend().hide()

        self.chart.setTitle(title)

        formatAudio = QAudioFormat()
        formatAudio.setSampleRate(8000)
        formatAudio.setChannelCount(1)
        formatAudio.setSampleSize(8)
        formatAudio.setCodec("audio/pcm")
        formatAudio.setByteOrder(QAudioFormat.LittleEndian)
        formatAudio.setSampleType(QAudioFormat.UnSignedInt)

        self.audioInput = QAudioInput(self.inputDevice, formatAudio, self)
        self.ioDevice = self.audioInput.start()
        self.ioDevice.readyRead.connect(self._readyRead)

        self.buffer = [QPointF(x, 0) for x in range(sampleCount)]
        self.series.append(self.buffer)


    def _readyRead(self):

        data = self.ioDevice.readAll()
        availableSamples = data.size() // resolution
        start = 0
        if (availableSamples < sampleCount):
            start = sampleCount - availableSamples
            for s in range(start):
                self.buffer[s].setY(self.buffer[s + availableSamples].y())

        dataIndex = 0
        for s in range(start, sampleCount):
            value = (ord(data[dataIndex]) - 128) / 128
            self.buffer[s].setY(value)
            dataIndex = dataIndex + resolution
        self.series.replace(self.buffer)


    def closeEvent(self, event):
        if self.audioDevice is not None:
            self.audioDevice.stop()
        event.accept()


""" class RecordingSession:
    exp_struct = dict() #experiment file structure
    sess_par = dict() # session parameters (bird, rec session)
    evt_par = dict() # event parameters
    rig_par = dict() # here goes the .json file describing the rig (what channels where what)
    
    units = tuple() # tuple with the units
    sorted_recs = np.empty(0)
    events = {}
    pd_meta = pd.DataFrame()
    
    # quick access
    kwd_path = ''
    kwik_path = ''
    kwe_path = ''
    fileName = 'stream.kwd'

    evt_ttl_pd = pd.DataFrame()
    
    mic_streams = np.empty(0)

    def __init__(self, sess_par, viz_par):
        self.sess_par = sess_par
        self.viz_par = viz_par
        
        exp_struct = et.get_exp_struct(sess_par['bird'], sess_par['sess'])
        self.exp_struct = exp_struct
        self.kwd_path = exp_struct['files']['kwd']
        self.kwik_path = exp_struct['files']['kwik']
        self.kwe_path = exp_struct['files']['kwe']

        self.pd_meta = kwdf.get_all_rec_meta(exp_struct['files']['kwd'])
        self.s_f = kutil.get_record_sampling_frequency(exp_struct['files']['kwd'])

        
        self.reset_viz_par()
        
    def reset_viz_par(self):
        vp = self.viz_par
        vp['pre_samples'] = int(vp['pre_ms'] * self.s_f * 0.001)
        vp['post_samples'] = int(vp['post_ms'] * self.s_f * 0.001)
        vp['span'] = vp['post_samples'] - vp['pre_samples']
        
    def load_rig_par(self, rig_par_dict={}):
        if rig_par_dict:
            self.rig_par = rig_par_dict
        else:
            raise NotImplementedError
            # need to load it from the file.
    
    def get_sorted_recs(self):
        return self.sorted_recs
    
            
    def load_event_ttl(self, ev_name, ch_name):
        ttl = ev.TTL(ev_name, ch_name, self.kwd_path)
        ttl.event_pd.set_index(['ch', 'edge'], inplace=True)
        self.events[ev_name] = ttl
    
    def get_event_ttl(self): # get the event in viz_par
        evt_edge = self.viz_par['evt_edge']
        evt_name = self.viz_par['evt_name']
        evt_signal = self.viz_par['evt_signal']
        ch_type, ch_name = lookup_chan(self.rig_par, evt_signal)
        
        try:
            evt_obj = self.events[evt_name]
        except KeyError:
            _, ch_name = lookup_chan(self.rig_par, evt_signal)
            self.load_event_ttl(evt_name, ch_name)
        self.evt_ttl_pd = self.events[evt_name].event_pd.loc[ch_name].loc[evt_edge]
         
    def get_event_stamps(self, filter_recs=np.empty(0)):
        self.get_event_ttl()
        evt_ttl_pd = self.evt_ttl_pd
        
        if filter_recs.size > 0:
            logger.info('filter recs')
            evt_ttl_pd = evt_ttl_pd[evt_ttl_pd['rec'].apply(lambda x: x in filter_recs)]
            
        all_rec = evt_ttl_pd['rec'].values
        all_start = evt_ttl_pd['t'].values            
        return all_rec, all_start
    
    def load_mic_peri_event_streams(self, mic='microphone_0'):
        self.mic_streams = self.get_perievent_stream_frames(mic)
        
    def get_mic_stream(self):
        return self.mic_streams
        
    
    def get_perievent_stream_frames(self, signal_name, filter_recs=np.empty(0)):
        ch_type, ch_name = lookup_chan(self.rig_par, signal_name)
        wanted_chans = np.array([ch_name])
        sel_chan_names = kwdf.get_all_chan_names(self.pd_meta, chan_filt=wanted_chans)
        
        all_rec, all_start = self.get_event_stamps(filter_recs=filter_recs)

        vp = self.viz_par
        stream_pst_array = kwdf.get_frames(self.kwd_path, all_start + vp['pre_samples'], all_rec, vp['span'], sel_chan_names, self.pd_meta)
        return stream_pst_array """
        



if __name__ == '__main__':
    import os
    import sys


    app = QtWidgets.QApplication(sys.argv)
    window = ZeguiWindow()
    window.show()
    sys.exit(app.exec_())