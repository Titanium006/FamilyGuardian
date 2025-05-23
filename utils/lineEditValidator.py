from PyQt5 import QtWidgets, QtCore, QtGui, Qt
import re
from PyQt5.QtWidgets import QMessageBox

class LineEditValidator(QtGui.QValidator):
    def __init__(
            self,
            # 编辑状态框输入结束允许的字符串
            fullPatterns,
            # 编辑状态框输入尚未结束允许的字符串
            partialPatterns,
            fixupString
    ):

        super(LineEditValidator, self).__init__()
        self.fullPatterns = fullPatterns
        self.partialPatterns = partialPatterns
        self.fixupString = fixupString

    # 实时监听文本框的改变
    # 可能是键盘单个字符'n'输入, 也有可能是粘贴多个字符'nan'输入
    def validate(self, string, pos) -> QtGui.QValidator.State:  # string为编辑状态框中可见的字符串+输入字符/字符串

        # 编辑过程结束，若返回True，将编辑状态框中的字符串填入LineEdit,若返回Flase则自动调用self.fixup方法，将fixup方法返回的字符串填入LineEdit
        if self.acceptable_check(string):
            # print(f'QtGui.QValidator.Acceptable:{QtGui.QValidator.Acceptable}')
            return QtGui.QValidator.Acceptable, string, pos  # QtGui.QValidator.Acceptable = 2;

        # 编辑过程中允许出现的字符串
        if self.intermediate_check(string):
            # print(f'QtGui.QValidator.Intermediate:{QtGui.QValidator.Intermediate}')
            return QtGui.QValidator.Intermediate, string, pos  # QtGui.QValidator.State = 1;
        # 编辑过程中不允许出现的字符串(本次输入的单个字符或字符串无效)
        else:
            # print(f'QtGui.QValidator.Invalid:{QtGui.QValidator.Invalid}')
            return QtGui.QValidator.Invalid, string, pos

    # 编辑状态框验证通过, 编辑状态框单个字输入符成功
    def acceptable_check(self, string) -> bool:
        True_ = 0
        for fullPattern in self.fullPatterns:
            if re.fullmatch(fullPattern, string):
                True_ += 1
            else:
                continue
        if True_ != 0:
            return True
        else:
            return False

    # 输入还未结束允许的字符串
    def intermediate_check(self, string):  # -> bool;    string为编辑状态框中可见的字符串
        """
        Checks if string makes a valid partial float, keeping in mind locale dependent decimal separators.
        """
        if string == '':
            return True
        for partialPattern in self.partialPatterns:
            if re.fullmatch(partialPattern, string):
                return True
            else:
                pass

    #
    def eventFilter(self, lineEdit, event):  # -> bool
        # FocusIn event
        # 每当fous in时，更新LineEditRegExpValidator的fixupString
        # 输入验证器

        if event.type() == QtCore.QEvent.FocusIn:
            # do custom stuff
            # print('focus in')

            # self.lineEdit_zhuansu.installEventFilter(SciNotValidator)， 在本类中，widget是self.lineEdit，执行函数self.lineEdit.text(),  其它类不一定有text()方法

            # lineEdit.selectAll()
            QtCore.QTimer.singleShot(0, lineEdit.selectAll)  # 0ms
            # self.fixupString = lineEdit.text()

            # print(self.fixupString)
            # return False so that the lineEdit will also handle the event
            # otherwise it won't focus out
            return False
        else:
            # we don't care about other events
            return False

    # 重写QValidator的fixup(str)方法。可以在切换焦点后，直接修改不合规则的字符串。参数str是经过validate()方法验证后的字符串；
    def fixup(self, string) -> str:
        """
        Fixes up input text to create a valid float. Puts an empty string on failure.
        """
        print(string)

        True_ = 0
        for fullPattern in self.fullPatterns:
            if re.fullmatch(fullPattern, string):
                True_ += 1
            else:
                continue
        if True_ != 0:
            return string
        else:
            return self.fixupString
            # return ''

