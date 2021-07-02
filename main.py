# -*- coding: utf-8 -*-
# author:yangtao
# time: 2021/07/01


import random

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omui
try:
    from shiboken2 import wrapInstance
    from PySide2 import QtWidgets
    from PySide2 import QtCore
except ImportError:
    from shiboken import wrapInstance
    from PySide import QtGui as QtWidgets
    from PySide import QtCore


class RandomColorMaterial():
    def __init__(self):
        self.name_suffix = "_randommtl"    # 材质球命名后缀

    def clear(self):
        """
        删除所有创建的颜色材质球
        Returns:

        """
        shds = cmds.ls(materials=True)
        for shd in shds:
            if shd.endswith(self.name_suffix):
                obj_list = cmds.listConnections("%s.outColor"%shd)
                for obj in obj_list:
                    cmds.select(obj)
                    cmds.sets(e=True, forceElement="initialShadingGroup")
                try:
                    cmds.delete(shd, icn=True)
                except Exception as e:
                    print(e)
        cmds.select(cl=True)

        # 清理残留的渲染节点
        mel.eval('hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes");')

    def create_shadingnode(self, obj):
        # 找到这个命名材质球, 没有就创建
        obj_name = obj.rsplit("|", 1)[-1]
        shd_name = '%s_%s' % (obj_name, self.name_suffix)
        shds = cmds.ls(shd_name, materials=True)
        if shds:
            return shds[0]
        else:
            shd = cmds.shadingNode('lambert', asShader=True, n=shd_name)
            return shd

    def set_material_to_sel(self):
        sel = cmds.ls(sl=True, l=True)
        for obj in sel:
            # 只对有 shape 节点的模型操作
            if cmds.listRelatives(obj, s=True):
                # 创建材质球
                shd = self.create_shadingnode(obj)
                # 为材质球设置随机颜色
                r = [random.random() for i in range(3)]
                cmds.setAttr('%s.color' % shd, r[0], r[1], r[2], type='double3')
                # 连接材质球和模型
                sg = cmds.sets(n='%s_sg' % obj, renderable=True, noSurfaceShader=True, empty=True)
                cmds.connectAttr('%s.outColor' % shd, '%s.surfaceShader' % sg, f=True)
                cmds.sets(obj, e=True, fe=sg)


def getMayaWindow():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class MainUI(QtWidgets.QWidget):
    instance = None
    def __init__(self):
        super(MainUI, self).__init__()
        self.RCM = RandomColorMaterial()

        self.setParent(getMayaWindow(), QtCore.Qt.Window)  # 设置maya为父级窗口

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.setWindowTitle(u"随机着色器")
        self.setMinimumWidth(250)
        self.set_color_button = QtWidgets.QPushButton(u"随机着色")
        self.set_color_button.setStyleSheet(":hover{background-color: Green;}")
        self.clear_color_button = QtWidgets.QPushButton(u"清除材质球")
        self.clear_color_button.setStyleSheet(":hover{background-color: Brown;}")
        self.main_layout.addWidget(self.set_color_button)
        self.main_layout.addWidget(self.clear_color_button)

        self.set_color_button.clicked.connect(self.RCM.set_material_to_sel)
        self.clear_color_button.clicked.connect(self.RCM.clear)


def load_ui():
    if not MainUI.instance:
        MainUI.instance = MainUI()
    MainUI.instance.show()
    MainUI.instance.raise_()