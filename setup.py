"""
vBase Unified Command Line Interface (CLI)
"""

from pathlib import Path

from setuptools import find_packages, setup

ROOT_DIR = Path(__file__).resolve().parent

long_description = (ROOT_DIR / "README.md").read_text(encoding="utf-8")

requirements = [
    line.strip()
    for line in (ROOT_DIR / "requirements.in").read_text(encoding="utf-8").splitlines()
    if line.strip() and not line.strip().startswith("#")
]

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
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    entry_points={
        "console_scripts": ["vbase=vbasecli.cli:cli"],
    },
)
