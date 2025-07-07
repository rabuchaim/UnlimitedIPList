import codecs
from setuptools import setup, find_packages

setup(
    name='unlimitediplist',
    version='1.0.1',
    description="A list-type object to manage lists of IPv4/IPv6 networks and perform super-fast lookups of IPv4/IPv6 addresses within the networks in that list. A lookup takes around 0.000005 seconds regardless of the size of the list and it´s pure Python!",
    url='https://github.com/rabuchaim/unlimitediplist',
    author='Ricardo Abuchaim',
    author_email='ricardoabuchaim@gmail.com',
    maintainer='Ricardo Abuchaim',
    maintainer_email='ricardoabuchaim@gmail.com',
    project_urls={
        "Issue Tracker": "https://github.com/rabuchaim/unlimitediplist/issues",
        "Source code": "https://github.com/rabuchaim/unlimitediplist"
    },
    bugtrack_url='https://github.com/rabuchaim/unlimitediplist/issues',
    license='MIT',
    keywords=['iplist','unlimited_ip_list','accesslimit','accesslimiter','ratelimit','ratelimiter','fastratelimiter','api','rate limit','firewall','blocking','flask','tornado','fastapi','bottle','purepython','pure','rules','tools'],
    py_modules=['unlimitediplist', 'unlimitediplist'],
    package_dir = {'unlimitediplist': 'unlimitediplist'},
    include_package_data=True,
    zip_safe = False,
    packages=['unlimitediplist'],
    package_data={
        'unlimitediplist': [
            'LICENSE',
            'README.md',
            'unlimitediplist/__init__.py',
            'unlimitediplist/unlimitediplist.py',
        ],
    },
    python_requires=">=3.10",
    install_requires=[],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
        "Topic :: Internet",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    long_description=codecs.open("README.md","r","utf-8").read(),
    long_description_content_type='text/markdown',
)