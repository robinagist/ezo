import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setuptools.setup(
    name="ezo",
    version="0.0.1",
    author="Robin A. Gist",
    author_email="robinagist@gmail.com",
    description="ezo - easy Ethereum oracles",
    long_description="quickly create Ethereum oracles and other event responders.  Write handlers in Python",
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/ezo",
    packages=setuptools.find_packages(),
    install_requires=required,
    include_package_data=True,
    classifiers=(
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)