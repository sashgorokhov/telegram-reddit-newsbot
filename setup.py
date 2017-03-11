from distutils.core import setup

with open('README.md') as readme:
    long_description = readme.read()

try:
    import pypandoc

    long_description = pypandoc.convert(long_description, 'rst', 'markdown')
except(IOError, ImportError):
    long_description = long_description

VERSION = '0.3'

setup(
    name='telegram-reddit-newsbot',
    packages=['newsbot'],
    version=VERSION,
    url='https://github.com/sashgorokhov/telegram-reddit-newsbot',
    download_url='https://github.com/sashgorokhov/telegram-reddit-newsbot/archive/v%s.zip' % VERSION,
    keywords=['python', 'asyncio', 'telegram', 'bot', 'reddit'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Communications :: Chat',
    ],
    long_description=long_description,
    license='MIT License',
    author='sashgorokhov',
    author_email='sashgorokhov@gmail.com',
    description='Telegram bot to stay in tune with favourite reddit channels.',
)
