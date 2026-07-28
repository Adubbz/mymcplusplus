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

from mymcplusplus import mymc


def md5(fn):
    import hashlib
    return hashlib.md5(open(fn, "rb").read()).hexdigest()


def patch_fixed_time(monkeypatch, mod):
    def tod_now():
        return 42, 37, 22, 20, 4, 2018
    monkeypatch.setattr(mod, "tod_now", tod_now)


def patch_localtime(monkeypatch):
    import time
    def localtime(secs=None):
        return time.gmtime(secs)
    monkeypatch.setattr(time, "localtime", localtime)


def test_ls(monkeypatch, capsys, data):
    patch_localtime(monkeypatch)
    mymc.main(["mymcplus",
               "-i", data.join("mc01.ps2").strpath,
               "ls"])

    output = capsys.readouterr()
    assert output.err == ""
    assert output.out == ("rwx--d----+----       4 2018-04-21 14:53:07 .\n"
                          "-wx--d----+--H-       0 2018-04-21 14:53:00 ..\n"
                          "rwx--d-------H-       4 2018-04-21 14:53:01 BEDATA-SYSTEM\n"
                          "rwx--d----+----       5 2018-04-21 14:53:09 BESCES-50501REZ\n")


def test_extract(capsys, data, tmpdir):
    out_file = tmpdir.join("BESCES-50501REZ").strpath

    mymc.main(["mymcplus",
               "-i", data.join("mc01.ps2").strpath,
               "extract", "-o", out_file, "BESCES-50501REZ/BESCES-50501REZ"])

    output = capsys.readouterr()
    assert output.err == ""
    assert output.out == ""

    assert md5(out_file) == "5388344a2d4bb429b9a18ff683a8a691"


def test_add(monkeypatch, capsys, mc01_copy, tmpdir):
    from mymcplusplus import ps2mc
    patch_fixed_time(monkeypatch, ps2mc)
    patch_localtime(monkeypatch)

    file = tmpdir.join("helloworld.txt").strpath
    with open(file, "w") as f:
         f.write("Hello World!\n")

    mc_file = mc01_copy.join("mc01.ps2").strpath

    mymc.main(["mymcplus",
               "-i", mc_file,
               "add", file])

    output = capsys.readouterr()
    assert output.out == ""
    assert output.err == ""

    mymc.main(["mymcplus",
               "-i", mc_file,
               "ls"])

    output = capsys.readouterr()
    assert output.out == ("rwx--d----+----       5 2018-04-20 13:37:42 .\n"
                          "-wx--d----+--H-       0 2018-04-21 14:53:00 ..\n"
                          "rwx--d-------H-       4 2018-04-21 14:53:01 BEDATA-SYSTEM\n"
                          "rwx--d----+----       5 2018-04-21 14:53:09 BESCES-50501REZ\n"
                          "rwx-f-----+----      13 2018-04-20 13:37:42 helloworld.txt\n")
    assert output.err == ""

    assert md5(mc_file) == "faa75353a97328c7d8fe38756c38fdd9"


def test_check_ok(capsys, data):
    mymc.main(["mymcplus",
               "-i", data.join("mc01.ps2").strpath,
               "check"])

    output = capsys.readouterr()
    assert output.out == "No errors found.\n"
    assert output.err == ""


def test_check_root_directory(capsys, mc01_copy):
    mc_file = mc01_copy.join("mc01.ps2").strpath
    with open(mc_file, "r+b") as f:
        f.seek(0x200)
        f.write(b"\x13\x37")

    assert md5(mc_file) == "bec7e8c3884806024b9eb9599dc4315f"

    mymc.main(["mymcplus",
               "-i", mc_file,
               "check"])

    output = capsys.readouterr()
    assert output.err == mc_file + ": Root directory damaged.\n"
    assert output.out == ""

# TODO: Should probably make more tests for check


def test_clear(capsys, mc01_copy):
    mc_file = mc01_copy.join("mc01.ps2").strpath

    mymc.main(["mymcplus",
               "-i", mc_file,
               "clear", "-x", "BESCES-50501REZ"])

    output = capsys.readouterr()
    assert output.err == ""
    assert output.out == ""

    assert md5(mc_file) == "defaeba9b480676e8666dd4f3ff16643"


def test_set(capsys, mc01_copy):
    mc_file = mc01_copy.join("mc01.ps2").strpath

    mymc.main(["mymcplus",
               "-i", mc_file,
               "set", "-K", "BESCES-50501REZ"])

    output = capsys.readouterr()
    assert output.err == ""
    assert output.out == ""

    assert md5(mc_file) == "d235a085e75a8201bd417b127ccd8908"


def test_delete(capsys, mc01_copy):
    mc_file = mc01_copy.join("mc01.ps2").strpath

    mymc.main(["mymcplus",
               "-i", mc_file,
               "delete", "BESCES-50501REZ"])

    output = capsys.readouterr()
    assert output.err == ""
    assert output.out == ""

    assert md5(mc_file) == "143e640ccf3f22e48e1d1d4b10300d57"


def test_df(capsys, data):
    mc_file = data.join("mc01.ps2").strpath

    mymc.main(["mymcplus",
               "-i", mc_file,
               "df"])

    output = capsys.readouterr()
    assert output.out == mc_file + ": 8268800 bytes free.\n"
    assert output.err == ""


def test_dir(capsys, data):
    mc_file = data.join("mc01.ps2").strpath

    mymc.main(["mymcplus",
               "-i", mc_file,
               "dir", "-a"])

    output = capsys.readouterr()
    assert output.out == ("BEDATA-SYSTEM                    Your System\n"
                          "   5KB Not Protected             Configuration\n"
                          "\n"
                          "BESCES-50501REZ                  Rez\n"
                          "  53KB Not Protected             \n"
                          "\n"
                          "8,075 KB Free\n")
    assert output.err == ""


def test_format(monkeypatch, capsys, tmpdir):
    from mymcplusplus import ps2mc
    patch_fixed_time(monkeypatch, ps2mc)

    mc_file = tmpdir.join("mc.ps2").strpath

    mymc.main(["mymcplus",
               "-i", mc_file,
               "format"])

    output = capsys.readouterr()
    assert output.out == ""
    assert output.err == ""

    assert md5(mc_file) == "18ab430278362e6e70ce7cda9081888f"


def test_mkdir(monkeypatch, capsys, mc01_copy):
    from mymcplusplus import ps2mc
    patch_fixed_time(monkeypatch, ps2mc)

    mc_file = mc01_copy.join("mc01.ps2").strpath

    mymc.main(["mymcplus",
               "-i", mc_file,
               "mkdir", "p0rn"])

    output = capsys.readouterr()
    assert output.out == ""
    assert output.err == ""

    assert md5(mc_file) == "2be30a14246f34cdb157ea68f4905b85"


def test_remove(capsys, mc01_copy):
    mc_file = mc01_copy.join("mc01.ps2").strpath

    mymc.main(["mymcplus",
               "-i", mc_file,
               "remove", "BESCES-50501REZ/BESCES-50501REZ"])

    output = capsys.readouterr()
    assert output.out == ""
    assert output.err == ""

    assert md5(mc_file) == "5d0ffec85ad1dc9a371e0ead55f4932b"


def test_remove_nonempty(capsys, mc01_copy):
    mc_file = mc01_copy.join("mc01.ps2").strpath

    mymc.main(["mymcplus",
               "-i", mc_file,
               "remove", "BESCES-50501REZ"])

    output = capsys.readouterr()
    assert output.out == ""
    assert output.err == "BESCES-50501REZ: directory not empty\n"


def test_export_psu(capsys, data, tmpdir):
    mc_file = data.join("mc01.ps2").strpath

    mymc.main(["mymcplus",
               "-i", mc_file,
               "export", "-d", tmpdir.strpath, "-p", "BESCES-50501REZ"])

    output = capsys.readouterr()
    # "Exporing" typo fixed to "Exporting" in code; longname is default since PR #22
    assert output.out == "Exporting BESCES-50501REZ to SCES-50501 Rez (DD5DAEA3).psu\n"
    assert output.err == ""

    # Filename uses make_longname by default since PR #22
    assert md5(tmpdir.join("SCES-50501 Rez (DD5DAEA3).psu").strpath) == "d86c82e559c8250c894fbbc4405d8789"


def test_export_max(capsys, data, tmpdir):
    mc_file = data.join("mc01.ps2").strpath

    mymc.main(["mymcplus",
               "-i", mc_file,
               "export", "-d", tmpdir.strpath, "-m", "BESCES-50501REZ"])

    output = capsys.readouterr()
    # "Exporing" typo fixed to "Exporting" in code; longname is default since PR #22
    assert output.out == "Exporting BESCES-50501REZ to SCES-50501 Rez (DD5DAEA3).max\n"

    # Filename uses make_longname by default since PR #22
    assert md5(tmpdir.join("SCES-50501 Rez (DD5DAEA3).max").strpath) == "3f63d38668a0a5a5fa508ab8c3bb469a"


def test_import_psu(monkeypatch, capsys, data, mc02_copy):
    from mymcplusplus import ps2mc
    patch_fixed_time(monkeypatch, ps2mc)

    mc_file = mc02_copy.join("mc02.ps2").strpath
    psu_file = data.join("BESCES-50501REZ.psu").strpath

    mymc.main(["mymcplus",
               "-i", mc_file,
               "import", psu_file])

    output = capsys.readouterr()
    assert output.out == "Importing " + psu_file + " to BESCES-50501REZ\n"
    assert output.err == ""

    assert md5(mc_file) == "4085992c23fc38d6c4ece5303dc77e74"


def test_import_max(monkeypatch, capsys, data, mc02_copy):
    from mymcplusplus import ps2mc
    from mymcplusplus import ps2mc_dir
    from mymcplusplus.save import ps2save
    patch_fixed_time(monkeypatch, ps2mc)
    patch_fixed_time(monkeypatch, ps2mc_dir)
    patch_fixed_time(monkeypatch, ps2save)

    mc_file = mc02_copy.join("mc02.ps2").strpath
    max_file = data.join("BESCES-50501REZ.max").strpath

    mymc.main(["mymcplus",
               "-i", mc_file,
               "import", max_file])

    output = capsys.readouterr()
    assert output.out == "Importing " + max_file + " to BESCES-50501REZ\n"

    assert md5(mc_file) == "0e2dd8d53f05f6debe7d93aa726fc6e6"


def test_import_sps(monkeypatch, capsys, data, mc02_copy):
    from mymcplusplus import ps2mc
    patch_fixed_time(monkeypatch, ps2mc)

    mc_file = mc02_copy.join("mc02.ps2").strpath
    sps_file = data.join("BESCES-50501REZ.sps").strpath

    mymc.main(["mymcplus",
               "-i", mc_file,
               "import", sps_file])

    output = capsys.readouterr()
    assert output.out == "Importing " + sps_file + " to BESCES-50501REZ\n"
    assert output.err == ""

    assert md5(mc_file) == "9726ad34016df2586eb9663a12f9ba02"


def test_import_xps(monkeypatch, capsys, data, mc02_copy):
    from mymcplusplus import ps2mc
    patch_fixed_time(monkeypatch, ps2mc)

    mc_file = mc02_copy.join("mc02.ps2").strpath
    xps_file = data.join("BESCES-50501REZ.xps").strpath

    mymc.main(["mymcplus",
               "-i", mc_file,
               "import", xps_file])

    output = capsys.readouterr()
    assert output.out == "Importing " + xps_file + " to BESCES-50501REZ\n"
    assert output.err == ""

    assert md5(mc_file) == "9726ad34016df2586eb9663a12f9ba02"


def test_import_cbs(monkeypatch, capsys, data, mc02_copy):
    from mymcplusplus import ps2mc
    from mymcplusplus import ps2mc_dir
    from mymcplusplus.save import ps2save
    patch_fixed_time(monkeypatch, ps2mc)
    patch_fixed_time(monkeypatch, ps2mc_dir)
    patch_fixed_time(monkeypatch, ps2save)

    mc_file = mc02_copy.join("mc02.ps2").strpath
    cbs_file = data.join("BESCES-50501REZ.cbs").strpath

    mymc.main(["mymcplus",
               "-i", mc_file,
               "import", cbs_file])

    output = capsys.readouterr()
    assert output.out == "Importing " + cbs_file + " to BESCES-50501REZ\n"
    assert output.err == ""

    assert md5(mc_file) == "897b0fbd1965dc02a442e1723bd3df27"


def test_import_psv_ps2(monkeypatch, capsys, data, mc02_copy):
    from mymcplusplus import ps2mc
    from mymcplusplus import ps2mc_dir
    patch_fixed_time(monkeypatch, ps2mc)
    patch_fixed_time(monkeypatch, ps2mc_dir)

    mc_file = mc02_copy.join("mc02.ps2").strpath
    psv_file = data.join("BESCES-5050152455A.PSV").strpath

    mymc.main(["mymcplus",
               "-i", mc_file,
               "import", psv_file])

    output = capsys.readouterr()
    assert output.out == "Importing " + psv_file + " to BESCES-50501REZ\n"
    assert output.err == ""

    assert md5(mc_file) == "2872c456bcb647e78aeb3ce29e718309"


def test_import_psv_ps1(monkeypatch, capsys, data, mc02_copy):
    from mymcplusplus import ps2mc
    from mymcplusplus import ps2mc_dir
    patch_fixed_time(monkeypatch, ps2mc)
    patch_fixed_time(monkeypatch, ps2mc_dir)

    mc_file = mc02_copy.join("mc02.ps2").strpath
    psv_file = data.join("BASLUS-006623030303030303041.PSV").strpath

    mymc.main(["mymcplus",
               "-i", mc_file,
               "import", psv_file])

    output = capsys.readouterr()
    assert output.out == "Importing " + psv_file + " to BASLUS-006620000000A\n"
    assert output.err == ""

    assert md5(mc_file) == "c9f26130a5de7548248a5fec80593a4d"
