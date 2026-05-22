from setuptools import setup, find_packages

setup(
    name="songdl",
    version="1.0.0",
    description="YouTube audio downloader with search and playlist management",
    packages=find_packages(),
    install_requires=["youtube-dl"],
    entry_points={
        "console_scripts": [
            "songdl=songdl.cli:main",
        ],
    },
    python_requires=">=3.6",
)
