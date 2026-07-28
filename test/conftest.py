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

import sys, os
import pytest
import tarfile
import shutil

test_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(test_dir, "..")))

@pytest.fixture(scope="session")
def data(tmpdir_factory):
    data_dir = tmpdir_factory.mktemp("data")
    path = os.path.join(test_dir, "data.tar.gz")
    tar = tarfile.open(path)
    tar.extractall(data_dir.strpath, filter="data")
    return data_dir

@pytest.fixture
def mc01_copy(data, tmpdir):
    shutil.copy(data.join("mc01.ps2").strpath, tmpdir.strpath)
    return tmpdir

@pytest.fixture
def mc02_copy(data, tmpdir):
    shutil.copy(data.join("mc02.ps2").strpath, tmpdir.strpath)
    return tmpdir
