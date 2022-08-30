{
    'name': 'Audio field',
    'version': '14.0.0.1.0',
    'category': 'Extra Tools',
    'summary': 'Audio player widget for char fields with url.',
    'author': 'Oleksandr Komarov',
    'website': 'https://modool.pro',
    'license': 'LGPL-3',
    'price': '12',
    'currency': "EUR",
    'depends': ['base', 'web'],
    'data': [
        'views/assets.xml',
    ],
    'qweb': [
        'static/src/xml/widget.xml',
        'static/src/components/audio_player/audio_player.xml',
    ],
    'images': [
        'static/description/main_screenshot.png',
    ],
    'application': False,
    'auto_install': False,
}
