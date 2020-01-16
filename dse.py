import os, re, functools, webbrowser, cPickle, logging, cStringIO, platform, zipfile, sys, types, shutil
from maya  import cmds, mel, OpenMayaUI, OpenMaya
import maya.api.OpenMaya as om
import xml.etree.ElementTree as xml 

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin, MayaQDockWidget

from qtUtil import *

sys.path.append(os.path.dirname(WORKDIRECTORY))
ui_main_window, ui_base_class = loadUiType( '%s/dialog_main.ui'%WORKDIRECTORY )

preview_mobjs = []
event_callback_idx = []

class DuplicateSEUI(MayaQWidgetDockableMixin, ui_main_window, ui_base_class):
    def __init__(self, parent=None):
        super(DuplicateSEUI, self).__init__(parent)
        self.setupUi(self)
        self._connectInterface();
        self.show()

    def _connectInterface(self):
        self.copies_slider.valueChanged.connect(self.onCopiesSlider)
        self.number_copies.valueChanged.connect(self.onNumCopies)
        self.t_x.valueChanged.connect(self.onTranslate)
        self.t_y.valueChanged.connect(self.onTranslate)
        self.t_z.valueChanged.connect(self.onTranslate)


    def onTranslate(self, *args):
        tx = self.t_x.value()
        ty = self.t_y.value()
        tz = self.t_z.value()
        p = (tx,ty,tz)
        updatePreviewPosition(p)

    def onRotate(self, *args):
        rx = self.r_x.value()
        ry = self.r_y.value()
        rz = self.r_z.value()
        r = (rx,ry,rz)
        updatePreviewRotation(r)

    def onScale(self, *args):
        sx = self.s_x.value()
        sy = self.s_y.value()
        sz = self.s_z.value()
        s = (sx,sy,sz)
        updatePreviewScale(s)

    def onNumCopies(self, *args):
        count = args[0]
        # update copies slider
        smaxv = self.copies_slider.maximum()
        if count > smaxv:
            self.copies_slider.setMaximum(count)
        self.copies_slider.setValue(args[0])
    def onCopiesSlider(self,*args):
        # update number copies displayed value
        self.number_copies.setValue(args[0])
    
    def closeEvent(self, event):
        for mobj in preview_mobjs:
            fn_dag = om.MFnDagNode(mobj)
            print fn_dag.fullPathName()
        om.MMessage.removeCallbacks(event_callback_idx)

def onLiveUpdate(*args):
    print args
    print 'scriptjob live update'

def buildPreviewObjs():
    print 'building preview'
    sl = om.MGlobal.getActiveSelectionList()
    i = 0
    while i < sl.length():
        fn_dagnode = om.MFnDagNode(sl.getDagPath(i))
        d = fn_dagnode.duplicate()
        if i == 0:
            acc = om.MNodeMessage.addAttributeChangedCallback(d,onLiveUpdate, clientData='fart')
            event_callback_idx.append(acc)
        preview_mobjs.append(d)
        i += 1
def updatePreviewCount(count):
    print'jajaj'

def updatePreviewPosition(p):
    print 'updating positions'

def updatePreviewRotation(r):
    print 'updatin rotations'

def updatePreviewScale(s):
    print 'updating scale'


def show():
    maya_window_ptr = wrapinstance(long(OpenMayaUI.MQtUtil.mainWindow()))
    duplicatee_main_window = DuplicateSEUI(maya_window_ptr)
    buildPreviewObjs()