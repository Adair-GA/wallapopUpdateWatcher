from setuptools import setup,find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

VERSION = '0.0.5'
DESCRIPTION = 'A library to watch for new items at wallapop.es '
LONG_DESCRIPTION = 'A package that allows to create alerts that will trigger a callback when a new product meeting that criteria appears on Wallapop.'

# Setting up
setup(
    name="wallapopUpdateWatcher",
    version=VERSION,
    author="Adair Gondan",
    author_email="<adairyves@gmail.com>",
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=['httpx'],
    classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Topic :: Software Development',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'
    ],
    keywords="wallapop api updates",
    project_urls={
    'Source': 'https://github.com/Adair-GA/wallapopUpdateWatcher',
    'Tracker': 'https://github.com/Adair-GA/wallapopUpdateWatcher/issues',
    },
    python_requires='>=3'
)