import pytest
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtTest import QSignalSpy
from pytestqt import qtbot
from PageButton import UserDelButton  # 替换为实际的模块名


def test_button_click_sends_signal(qtbot):
    button = UserDelButton()
    button.userID = 'admin1'
    button.btnNo = 5
    spy = QSignalSpy(button.send_myNo)

    # 模拟鼠标按下事件
    qtbot.mouseClick(button, Qt.LeftButton)

    # 验证信号是否被发送
    assert len(spy) == 1

    # 验证信号发送时包含的信息是否正确
    call_args = spy[0]
    expected_info = [button.userID, button.btnNo]
    assert call_args == [expected_info]
