import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ezo",
    version="0.0.22",
    author="Robin A. Gist",
    author_email="robinagist@gmail.com",
    description="ezo - easy Ethereum oracles",
    long_description="Quickly create Ethereum oracles and other event responders.  Write handlers in Python",
    long_description_content_type="text/markdown",
    url="https://github.com/robinagist/ezo",
    scripts=['ezo/start.py'],
    package_dir = {'': 'ezo'},
    packages=['core', 'cli'], #setuptools.find_packages(where='.'),
    include_package_data=True,
    python_requires='>=3.6',
    classifiers=(
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    entry_points={
        'console_scripts': [
            'ezo = start:main',
        ],
    },

    install_requires=['cement',
                      'configobj',
                      'cytoolz',
                      'eth-abi',
                      'eth-account',
                      'eth-hash',
                      'eth-keyfile',
                      'eth-keys',
                      'eth-rlp',
                      'eth-utils',
                      'hexbytes',
                      'idna',
                      'inflection',
                      'lru-dict',
                      'plyvel',
                      'py-solc',
                      'pycryptodome',
                      'requests',
                      'requests-toolbelt',
                      'web3',
                      "toolz",
                      "tqdm",
                      "urllib3",
                      "websockets",
                      "xkcdpass",
                      "xxhash"
                       ]
)

