from pathlib import Path
from setuptools import setup, find_packages

README = Path(__file__).parent / "README.md"

setup(
    name="vett",
    version="0.1.0",
    description="AI-powered codebase health scanner",
    long_description=README.read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    author="Vett contributors",
    license="MIT",
    url="https://github.com/your-org/vett",
    packages=find_packages(),
    install_requires=["anthropic>=0.25.0", "click>=8.1.0", "rich>=13.0.0"],
    entry_points={"console_scripts": ["vett=vett.cli:main"]},
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Quality Assurance",
    ],
)
