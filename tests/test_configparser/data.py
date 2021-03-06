from pathlib import Path

current_dir = Path(__file__).parent

config_path = current_dir / 'dummy_config.ini'

config_dict = {
            'my_config': {
                'profile': {
                    'name': 'Luna',
                    'profession': 'software engineer',
                    'Hobby': 'Marine fish'
                },
                'projects': ['hello', 1, 3],
                'Active': True,
                'Posts': None,
                'Users': 5,
            },
            'Fish_Profiles': {
                'Tank_type': 'Reef Tank',
                'Tank_size': '50 gal',
                'Age': '1 year',
                'Fish': {
                    'clownfish': 2,
                    'chalk_goby': 1,
                    'yellow_clown_goby': 1
                },
                'invertebrates': {
                    'snails': 3,
                    'Shrimps': 1
                },
                'Others': {'Liverock': 1},
                'Corals': {
                    'toadstool': 2,
                    'ricordia': 1,
                    'euphyllia': 2}
            },
            'date_format': {
                'formatter': {
                    'fmt': '{asctime} - {name} - {levelname} - {message}',
                    'datefmt': '%Y/%m/%d',
                    'style': '{'
                },
                'Active': True
            }

        }