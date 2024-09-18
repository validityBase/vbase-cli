"""
vBase Unified Command Line Interface (CLI)
"""

from setuptools import find_packages, setup

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

with open("requirements.txt", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="vbase-cli",
    version="0.0.1",
    author="PIT Labs, Inc.",
    author_email="tech@vbase.com",
    description="vBase Unified Command Line Interface (CLI)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/validityBase/vbase-py",
    packages=find_packages(),
    package_data={
        "": ["../requirements.txt", "abi/*.json"],
    },
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": ["vbase=vbasecli.vbase:cli"],
    },
)
