from setuptools import setup, find_packages

setup(
    name="bonded",
    version="1.0.0",
    description="CLI tool for content generation and quality control",
    author="Bonded Team",
    packages=find_packages(),
    install_requires=[
        "click>=8.1.0",
        "pandas>=2.0.0",
        "openai>=1.0.0",
        "aiohttp>=3.8.0",
        "asyncio-throttle>=1.0.0",
        "validators>=0.20.0",
        "python-dotenv>=1.0.0",
        "colorama>=0.4.6",
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "bonded=bonded.cli:main",
        ],
    },
    python_requires=">=3.8",
)