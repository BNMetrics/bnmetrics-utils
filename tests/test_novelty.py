import pytest
from pathlib import Path

from bnmutils.novelty import doc_parametrize, cd, strip_blank_recursive, str_eval, is_pypkg


def test_doc_parametrize():
    @doc_parametrize(val1='hello', val2='world')
    def dummy_func():
        """
        This is my docstring, {val1}, {val2}
        """

    assert dummy_func.__doc__.strip() == 'This is my docstring, hello, world'


def test_cd(tmpdir):

    original_cwd = Path.cwd()

    with cd(tmpdir):
        assert Path.cwd() == tmpdir
        assert Path.cwd() != original_cwd

    assert original_cwd == Path.cwd()


@pytest.mark.parametrize('iterable_, expected, evaluate',
                         [pytest.param(['hello ', '\nhi ', '1'], ['hello', 'hi', 1],
                                       True,
                                       id='when the iterable passed is not nested, evaluate=True'),
                          pytest.param([[' hello ', 'hi \n'], ['1', ' blah ', ' bye']],
                                       [['hello', 'hi'], [1, 'blah', 'bye']],
                                       True,
                                       id='when the iterable passed has nested list, evaluate=True'),
                          pytest.param([[' hello ', 'hi \n'], ['2.5', ' blah ', ' bye'], 'greet '],
                                       [['hello', 'hi'], [2.5, 'blah', 'bye'], 'greet'],
                                       True,
                                       id='when a tuple is passed and it has nested list and string, '
                                          'evaluate=True'),
                          pytest.param([['True', 'False', '2.5'], 'False'],
                                       [['True', 'False', '2.5'], 'False'],
                                       False,
                                       id='Nested list and String, evaluate=False')
                          ])
def test_strip_blank_recursive(iterable_, expected, evaluate):
    strip_blank_recursive(iterable_, evaluate=evaluate)

    assert iterable_ == expected


@pytest.mark.parametrize('parse_arg', [pytest.param(1, id='int value passed'),
                                       pytest.param('hello foo bar', id='string value passed'),
                                       pytest.param(('hello', 'hi'), id='tuple value passed')
                                       ])
def test_strip_blank_recursive_raise(parse_arg):
    with pytest.raises(ValueError):
        strip_blank_recursive(parse_arg)


@pytest.mark.parametrize('parse_str, expected',
                         [
                             pytest.param('None', None, id='Passing a None value'),
                             pytest.param('False', False, id='Passing a boolean value'),
                             pytest.param('Hello world', 'Hello world', id='Passing a regular string'),
                             pytest.param('[1, 2, 3]', [1,2,3], id='Passing a list value'),
                         ])
def test_str_eval(parse_str, expected):
    result = str_eval(parse_str)

    assert result == expected


def test_is_pypkg():
    path = Path(__file__).parent / 'test_configparser'
    assert is_pypkg(path)
    assert not is_pypkg(Path(__file__))
