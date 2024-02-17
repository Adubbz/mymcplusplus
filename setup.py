#
# This file is part of mymc+, based on mymc by Ross Ridge.
#
# mymc+ is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# mymc+ is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with mymc+.  If not, see <http://www.gnu.org/licenses/>.
#

from setuptools import setup

long_description = \
"""mymc++ is a PlayStation 2 memory card manager for to be used with .ps2 images as created by the PCSX2 emulator for example.
It is based on mymc+ by Florian Märkl and the classic mymc utility created by Ross Ridge."""

setup(
    name="mymcplusplus",
    version="3.1.0",
    description="A PlayStation 2 memory card manager",
    long_description=long_description,
    long_description_content_type="text/plain",
    url="https://github.com/Adubbz/mymcplusplus",
    author="Adubbz",
    license="GPLv3",
    clasifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Environment :: MacOS X :: Cocoa",
        "Environment :: Win32 (MS Windows)",
        "Environment :: X11 Applications :: GTK",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Natural Language :: English",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Games/Entertainment",
        "Topic :: Multimedia :: Graphics :: 3D Rendering",
        "Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator",
        "Topic :: System :: Archiving",
        "Topic :: System :: Archiving :: Backup",
        "Topic :: System :: Filesystems",
        "Topic :: Utilities"
    ],
    keywords="playstation ps2 mymc memory card save",
    packages=["mymcplusplus", "mymcplusplus.gui", "mymcplusplus.save"],
    entry_points={
        "console_scripts": [
            "mymcplusplus = mymcplusplus.mymc:main"
        ]
    },
    python_requires=">=3.4",
    install_requires=[],
    extras_require={
        "gui": ["wxPython", "pyopengl"]
    }
)
