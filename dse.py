import os, re, functools, webbrowser, cPickle, logging, cStringIO, platform, zipfile, sys, types, shutil
from maya  import cmds, mel, OpenMayaUI, OpenMaya
import maya.api.OpenMaya as om
import xml.etree.ElementTree as xml 
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin, MayaQDockWidget
from qtUtil import *

sys.path.append(os.path.dirname(WORKDIRECTORY))
ui_main_window, ui_base_class = loadUiType( '%s/dialog_main.ui'%WORKDIRECTORY )

source_dag_paths = []
preview_mobjs = [[]]
event_callback_idx = []
dse_main_window = ()

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
        if self.repeat_first.isChecked() == True:
            return
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
        updatePreviewCount(count)

    def onCopiesSlider(self,*args):
        # update number copies displayed value
        self.number_copies.setValue(args[0])
    
    def getTransform(self):
        tv = om.MVector(self.t_x.value(), self.t_y.value(), self.t_z.value())
        re = om.MEulerRotation(self.r_x.value(), self.r_y.value(), self.r_z.value())
        sv = om.MVector(self.s_x.value(),self.s_y.value(), self.s_z.value())
        return {'translate': tv, 'rotation': re, 'scale': sv }

    def setTransformDisplay(*args):
        s = args[0]
        t = args[1]
        if t['channel'] == 'tx':
            s.t_x.setValue(t['value'])
        if t['channel'] == 'ty':
            s.t_y.setValue(t['value'])
        if t['channel'] == 'tz':
            s.t_z.setValue(t['value'])
        if t['channel'] == 'rx':
            s.r_x.setValue(t['value'])
        if t['channel'] == 'ry':
            s.r_y.setValue(t['value'])
        if t['channel'] == 'rz':
            s.r_z.setValue(t['value'])
        if t['channel'] == 'sx':
            s.s_x.setValue(t['value'])
        if t['channel'] == 'sy':
            s.s_y.setValue(t['value'])
        if t['channel'] == 'sz':
            s.s_z.setValue(t['value'])
    
    def closeEvent(self, event):
        for mobj in preview_mobjs:
            fn_dag = om.MFnDagNode(mobj)
        om.MMessage.removeCallbacks(event_callback_idx)

def createDuplicate(dpath):
    fn_dn = om.MFnDagNode(dpath)
    d = fn_dn.duplicate()
    return d


def onLivePositionUpdate(*args):
    p = om.MPlug(args[1])
    source_dp = args[3]
    fntrans_source = om.MFnTransform(source_dp)
    source_trans = fntrans_source.translation(om.MSpace.kTransform)
    if p.isCompound:
        clen = p.numChildren()
        i = 0
        while i < clen:
            cp = p.child(i)
            cn = cp.partialName()
            v = cp.asDouble()
            if cn == 'tx':
                v -= source_trans.x
            elif cn == 'ty':
                v -= source_trans.y
            elif cn == 'tz':
                v -= source_trans.z
            dse_main_window.setTransformDisplay({'channel': cn, 'value': v})
            i += 1
    cn = p.partialName()
    v = p.asDouble()
    if cn == 'tx':
        v -= source_trans.x
    elif cn == 'ty':
        v -= source_trans.y
    elif cn == 'tz':
        v -= source_trans.z
    dse_main_window.setTransformDisplay({'channel': cn, 'value': v})


def buildPreviewObjs():
    print 'building preview'
    sl = om.MGlobal.getActiveSelectionList()
    if sl.isEmpty():
        om.MGlobal.displayWarning('Selection list empty')
        return
    i = 0
    while i < sl.length():
        try:
            dp = sl.getDagPath(i)
        except TypeError:
            om.MGlobal.displayWarning('One or more wrong selection type')
            i += 1
            continue;
        source_dag_paths.append(dp)
        fn_dagnode = om.MFnDagNode(dp)
        d = fn_dagnode.duplicate()
        acc = om.MNodeMessage.addAttributeChangedCallback(d,onLivePositionUpdate, dp)
        event_callback_idx.append(acc)
        preview_mobjs[i].append(d)
        i += 1

def updatePreviewCount(count):
    print 'updating preview count'
    while len(preview_mobjs[0]) < count:
        trans = dse_main_window.getTransform()
        i = 0
        while i < len(preview_mobjs):
            d = createDuplicate(source_dag_paths[i])
            fn_source_trans = om.MFnTransform(source_dag_paths[i])
            stransform = fn_source_trans.translation(om.MSpace.kTransform)
            # fn_dagnode = om.MFnDagNode(preview_mobjs[i][0])
            # d = fn_dagnode.duplicate()
            fn_trans = om.MFnTransform(d)
            di = len(preview_mobjs[i]) + 1
            fn_trans.setTranslation((trans['translate'] * di) + stransform, om.MSpace.kTransform)
            preview_mobjs[i].append(d)
            i += 1
    while len(preview_mobjs[0]) > count:
        i = 0
        while i < len(preview_mobjs):
            obj = preview_mobjs[i].pop()
            om.MGlobal.deleteNode(obj)
            i += 1

def updatePreviewPosition(p):
    print 'updating positions'

def updatePreviewRotation(r):
    print 'updatin rotations'

def updatePreviewScale(s):
    print 'updating scale'


def show():
    maya_window_ptr = wrapinstance(long(OpenMayaUI.MQtUtil.mainWindow()))
    global dse_main_window
    dse_main_window = DuplicateSEUI(maya_window_ptr)
    buildPreviewObjs()