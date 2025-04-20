"""
Setup configuration for Spot2 Assistant.

Configures the installation for the real estate chatbot application.
"""
from setuptools import setup, find_packages


with open('requirements/base.txt') as f:
    install_requires = [
        line.strip() for line in f
        if line.strip() and not line.startswith(('#', '-'))
    ]

setup(
    name="spot2_assistant",
    version="0.1.0",
    packages=find_packages(),
    install_requires=install_requires,
    python_requires='>=3.9',
)