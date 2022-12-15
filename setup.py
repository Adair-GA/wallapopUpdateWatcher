from setuptools import setup, find_packages


VERSION = '0.0.1'
DESCRIPTION = 'An library to watch for new items at wallapop.es '
LONG_DESCRIPTION = 'A package that allows to create alerts that will trigger a callback when a new product meeting that criteria appears on Wallapop.'

# Setting up
setup(
    name="wallapopUpdateWatcher",
    version=VERSION,
    author="Adair Gondan",
    author_email="<adairyves@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=['httpx'],

)