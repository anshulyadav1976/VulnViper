"""# For pip installation"""

from setuptools import setup, find_packages

setup(
    name="vulnviper",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "openai",
        "google-generativeai",
        # tiktoken is likely used by chunker.py or ast_parser.py via openai, add explicitly if needed
        # "tiktoken", 
    ],
    entry_points={
        'console_scripts': [
            'vulnviper=cli:main',
        ],
    },
    author="Your Name/Org",
    author_email="your.email@example.com",
    description="A LLM-powered code security scanner for Python, now named VulnViper.",
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/vulnviper",
)
