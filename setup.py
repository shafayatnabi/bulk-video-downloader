#!/usr/bin/env python3
"""
Setup script for Bulk Video Downloader
A PyQt-based application for downloading multiple videos from web pages
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Bulk Video Downloader - A PyQt-based application for downloading multiple videos from web pages"

# Read requirements from requirements.txt
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="bulk-video-downloader",
    version="1.0.0",
    author="Shafayat Nabi Chowdhury",
    author_email="snabi3@gmail.com",
    description="A PyQt-based bulk video downloader with web crawling capabilities",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/shafayatnabi/bulk-video-downloader",
    project_urls={
        "Bug Tracker": "https://github.com/shafayatnabi/bulk-video-downloader/issues",
        "Documentation": "https://github.com/shafayatnabi/bulk-video-downloader/blob/main/README.md",
        "Source Code": "https://github.com/shafayatnabi/bulk-video-downloader",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Video",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: X11 Applications :: Qt",
    ],
    keywords="video, downloader, bulk, PyQt, GUI, web scraping, crawler",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-qt>=4.2.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "test": [
            "pytest>=7.4.0",
            "pytest-qt>=4.2.0",
            "pytest-asyncio>=0.21.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "bulk-video-downloader=bulk_video_downloader.main:main",
        ],
        "gui_scripts": [
            "bulk-video-downloader-gui=bulk_video_downloader.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "bulk_video_downloader": [
            "resources/icons/*",
            "resources/images/*",
            "gui/styles.qss",
            "config/*.yaml",
        ],
    },
    #data_files=[
        #("share/applications", ["data/bulk-video-downloader.desktop"]),
        #("share/icons/hicolor/256x256/apps", ["data/bulk-video-downloader.png"]),
    #],
    zip_safe=False,
    platforms=["any"],
    license="MIT",
    maintainer="Shafayat Nabi Chowdhury",
    maintainer_email="snabi3@gmail.com",
)
