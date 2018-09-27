import pytest
from pathlib import Path

from bnmutils import ConfigParser
from bnmutils.exceptions import InvalidConfig, InvalidConfigOption

from . import data


class TestConfigParser:

    @classmethod
    def setup_class(cls):
        cls.config = ConfigParser()

    @pytest.mark.parametrize('filenames',
                             [
                                 pytest.param(data.config_path,
                                              id='parse with pathlib.Path object'),
                                 pytest.param(str(data.config_path),
                                              id='parse with string'),
                                 pytest.param([data.config_path],
                                              id='parse as list')
                             ])
    def test_init_from_files(self, filenames):
        config = ConfigParser.from_files(filenames)
        assert set(config.sections()) == {'my_config', 'Fish_Profiles', 'date_format'}

    def test_init_from_files_empty(self, tmpdir):
        file = tmpdir.join('foo.ini')
        file.open('w').close()

        assert Path(file).exists()

        with pytest.raises(InvalidConfig):
            ConfigParser.from_files(file)

    def test_init_from_files_non_exist(self):
        with pytest.raises(InvalidConfig):
            ConfigParser.from_files('blah.ini')

    def test_init_from_files_raise(self, tmpdir):
        ini_path = tmpdir.join('test.ini')

        with pytest.raises(InvalidConfig):
            ConfigParser.from_files(ini_path)

    def test_init_from_dict(self):
        config = ConfigParser.from_dict(data.config_dict)

        assert set(config.sections()) == {'my_config', 'Fish_Profiles', 'date_format'}

    # ---------------------------------------------------------------------------
    # Tests for .to_dict() and helper methods
    # ---------------------------------------------------------------------------

    @pytest.mark.parametrize('parse_args, expected',
                             [
                                 pytest.param({'section': 'my_config'},
                                              data.config_dict['my_config'],
                                              id='when section is passed'),
                                 pytest.param({'section': 'my_config', 'option': 'profile'},
                                              data.config_dict['my_config']['profile'],
                                              id='when both section and option are passed'),
                                 # pytest.param({'section': 'my_config', 'option': 'Active'},
                                 #              True,
                                 #              id='when both value passed. return value is none dict'),
                                 pytest.param({}, data.config_dict,
                                              id='when no args passed')
                             ])
    def test_to_dict(self, parse_args, expected):
        config = ConfigParser.from_files(data.config_path)

        assert config.to_dict(**parse_args) == expected

    def test_to_dict_raise(self):
        config = ConfigParser.from_files(data.config_path)

        with pytest.raises(ValueError):
            config.to_dict(option='profile')

    def test_to_dict_with_datefmt(self):
        config = ConfigParser.from_files(data.config_path)
        expected = {
            'formatter': {
                'fmt': '{asctime} - {name} - {levelname} - {message}',
                'datefmt': '%Y/%m/%d',
                'style': '{'
            },
            'Active': True
        }
        assert config.to_dict(section='date_format') == expected

    def test_option_to_dict(self):
        parse_option = "\nclownfish: 2\nchalk_goby:1\nyellow_clown_goby: 1"

        expected = {
            'clownfish': 2,
            'chalk_goby': 1,
            'yellow_clown_goby': 1,
        }

        result = self.config._option_to_dict(parse_option)

        assert result == expected

    @pytest.mark.parametrize('parse_option',
                             [pytest.param(" \ntype: option \n second_val : my_val ",
                                           id='config options with blank space in the beginning and middle'),
                              pytest.param("\n  type  : option    \n  second_val : my_val \n",
                                           id='config option with blank space after new line, '
                                              'and new line after last option'),
                              pytest.param("\ntype: option \nsecond_val: my_val ",
                                           id='config option with no blank space')])
    def test_conf_item_to_dict(self, parse_option):
        expected_dict = {'type': 'option',
                         'second_val': 'my_val'}
        output = self.config._option_to_dict(parse_option)

        assert expected_dict == output

    def test_option_to_dict_multiple_colons(self):
        parse_item = '\nactive: True' \
                     '\nlevel: INFO' \
                     '\nformatter: {funcName} :: {levelname} :: {message}'

        expected = {
            'active': True,
            'level': 'INFO',
            'formatter': '{funcName} :: {levelname} :: {message}',
        }

        assert self.config._option_to_dict(parse_item) == expected

    @pytest.mark.parametrize('parse_option',
                             [pytest.param(['blah', 'test'], id='when option passed is a list'),
                              pytest.param(20, id='when option passed is an int'),
                              pytest.param({'blah': 'test'}, id='when option passed is a dict'),
                              pytest.param("\nhello\nbye", id='when string option passed is in invalid format'),
                              pytest.param("\nhello: hi\nbye", id='when string option passed is in invalid format'),
                              ])
    def test_option_to_dict_raise_invalidoption(self, parse_option):
        with pytest.raises(InvalidConfigOption):
            self.config._option_to_dict(parse_option)

    def test_option_to_dict_raise_option_none_dict(self):
        with pytest.raises(ValueError) as e_info:
            self.config._option_to_dict('HELLO')

        assert e_info.value.args[0] == "'HELLO' cannot be converted to dict. alternatively, " \
                                       "use ConfigParser.get(section, value) to get the value."

    def test_section_to_dict(self):
        parse_section = [('profile', '\nname: Luna\nprofession:software engineer\nHobby: Marine fish'),
                         ('projects', '["hello", 1, 3]'),
                         ('Active', 'True'),
                         ('Posts', 'None')]

        expected = {
            'profile': {
                'name': 'Luna',
                'profession': 'software engineer',
                'Hobby': 'Marine fish'
            },
            'projects': ['hello', 1, 3],
            'Posts': None,
            'Active': True
        }

        result = self.config._section_to_dict(parse_section)
        assert result == expected

    def test_section_to_dict_raise(self):
        with pytest.raises(ValueError) as e_info:
            self.config._section_to_dict('\nname: Luna\nprofession: software engineer\nHobby: Marine fish')

        assert e_info.value.args[0] == "Invalid section type 'str'"

    # ---------------------------------------------------------------------------
    # Test helpers
    # ---------------------------------------------------------------------------

    def test_flatten_section_dict(self):
        expected = {
            'profile': '\nname: Luna\nprofession: software engineer\nHobby: Marine fish',
            'projects': "['hello', 1, 3]",
            'Active': 'True',
            'Posts': 'None',
            'Users': '5',
        }

        output = self.config._flatten_section_dict(data.config_dict['my_config'])

        assert output == expected
        assert self.config._section_to_dict(output) == data.config_dict['my_config']

