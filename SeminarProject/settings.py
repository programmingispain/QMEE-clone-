from os import environ

SESSION_CONFIGS = [
     dict(
         name='centipede_game',
         display_name='Centipede Game',
         app_sequence=['centipede_game'],
         num_demo_participants=2,
     ),
     dict(
        name='centipede_game_control',
        display_name='Centipede Game - Control',
        app_sequence=['centipede_game'],
        treatment='control',
        num_demo_participants=2,
     ),
     dict(
        name='centipede_game_higher_fixed',
        display_name='Centipede Game - Higher Fixed',
        app_sequence=['centipede_game'],
        treatment='higher_fixed',
        num_demo_participants=2,
     ),
     dict(
        name='centipede_game_higher_random',
        display_name='Centipede Game - Higher Random',
        app_sequence=['centipede_game'],
        treatment='higher_random',
        num_demo_participants=2,
     ),
]

ROOMS = [
    dict(
        name='QMEE_test',
        display_name='Stone Cold Creamery GmbH',
        participant_label_file='_rooms/participant_labels_copy.txt'
    )
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = []
SESSION_FIELDS = []

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '3984403655334'
