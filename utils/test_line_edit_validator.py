import pytest
from lineEditValidator import LineEditValidator

"""
    userNameValidator = LineEditValidator(
        fullPatterns=['', r'^[a-zA-Z0-9]{6,12}$'],  # 完整匹配模式
        partialPatterns=['', r'^[a-zA-Z0-9]{1,12}$'],   # 部分匹配模式
        fixupString=''
    )
    userPasswordValidator = LineEditValidator(
        fullPatterns=['', r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z0-9]{8,16}$'],    # 完整匹配模式
        partialPatterns=['', r'^[a-zA-Z0-9]{1,16}$'],   # 部分匹配模式
        fixupString=''
    )
"""


@pytest.fixture
def validator():
    fullPatterns = ['', r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z0-9]{8,16}$']
    partialPatterns = ['', r'^[a-zA-Z0-9]{1,16}$']
    fixupString = ''
    return LineEditValidator(fullPatterns, partialPatterns, fixupString)


def test_acceptable_check(validator):
    assert validator.acceptable_check('aA123456')  # Testing a valid input
    assert not validator.acceptable_check('aB3913bA2345616242')  # Testing an invalid input


def test_intermediate_check(validator):
    assert validator.intermediate_check('aA12')  # Testing a valid partial input
    assert not validator.intermediate_check('.;ab')  # Testing an invalid partial input


def test_fixup(validator):
    assert validator.fixup('aA123456') == 'aA123456'  # Testing a valid input
    assert validator.fixup('.;ab') == ''  # Testing an invalid input
