# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# See http://www.gnu.org/licenses/gpl.html for a copy of the GNU General
# Public License.
#--------------------------------------------------------------------------------------
QT_VERSION = "none"
ERROR_LIST = []
try:
    from PySide2.QtGui import * 
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    from PySide2.QtCore import Signal as pyqtSignal  
    from PySide2 import QtGui
    import shiboken2 as shiboken
    QT_VERSION = "pyside2"
except Exception, e:
    ERROR_LIST.append(["Pyside2 import", e ])
    try:
        from PySide.QtGui  import * 
        from PySide.QtCore import *
        from PySide.QtCore import Signal as pyqtSignal  
        from PySide import QtGui
        import shiboken
        QT_VERSION = "pyside"
    except Exception, e:
        ERROR_LIST.append(["Pyside import", e ])
        try:
            from PyQt4.QtCore import *
            from PyQt4.QtGui  import * 
            from PyQt4 import QtGui
            import sip
            QT_VERSION = "pyqt4"
        except Exception, e:
            ERROR_LIST.append(["PyQt4 import", e ])

if QT_VERSION == "none":
    for version, error in ERROR_LIST.iteritems():
      print version, error 

import logging, os, cStringIO

# @TODO: Dont care about stylesheets yet...
# QT_STYLESHEET = os.path.normpath(os.path.join(__file__, "../qOrange.stylesheet"))

try:
    from PyQt4 import uic
    uic.uiparser.logger.setLevel( logging.CRITICAL )
    uic.properties.logger.setLevel( logging.CRITICAL )
except:
    pass
try:
    import pysideuic
    pysideuic.uiparser.logger.setLevel( logging.CRITICAL )
    pysideuic.properties.logger.setLevel( logging.CRITICAL )
except:
    pass
try:
    import pyside2uic as pysideuic
    pysideuic.uiparser.logger.setLevel( logging.CRITICAL )
    pysideuic.properties.logger.setLevel( logging.CRITICAL )
except:
    pass

import xml.etree.ElementTree as xml 
from maya  import cmds, mel, OpenMayaUI, OpenMaya


WORKDIRECTORY = os.path.dirname(__file__) 

def loadUiType( uiFile ):
    '''workaround to be able to load QT designer uis with both PySide and PyQt4'''
    # http://nathanhorne.com/?p=451
    if QT_VERSION ==  "pyqt4":
        form_class, base_class =  uic.loadUiType( uiFile )
    else:
        parsed = xml.parse( uiFile )
        widget_class = parsed.find( 'widget' ).get( 'class' )
        form_class = parsed.find( 'class' ).text

        with open( uiFile, 'r' ) as f:
            o = cStringIO.StringIO()
            frame = {}

            pysideuic.compileUi( f, o, indent=0 )
            pyc = compile( o.getvalue(), '<string>', 'exec' )
            exec pyc in frame

            form_class = frame[ 'Ui_%s'%form_class ]
            base_class = eval( '%s'%widget_class )
    return form_class, base_class

def wrapinstance( ptr, base=None ):
    '''workaround to be able to wrap objects with both PySide and PyQt4'''
    # http://nathanhorne.com/?p=485'''
    if ptr is None:
        return None
    ptr = long( ptr ) 
    if globals().has_key( 'shiboken' ):
        if base is None:
            qObj = shiboken.wrapInstance( long( ptr ), QObject )
            metaObj = qObj.metaObject()
            cls = metaObj.className()
            superCls = metaObj.superClass().className()
            if hasattr( QtGui, cls ):
                base = getattr( QtGui, cls )
            elif hasattr( QtGui, superCls ):
                base = getattr( QtGui, superCls ) 
            else:
                base = QWidget
        return shiboken.wrapInstance( long( ptr ), base )
    elif globals().has_key( 'sip' ):
        base = QObject
        return sip.wrapinstance( long( ptr ), base )
    else:
        return None
