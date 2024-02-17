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

import base64

resources = {
    "open.png": base64.b64decode(
        b"iVBORw0KGgoAAAANSUhEUgAAAGAAAABgCAYAAADimHc4AAAABHNCSVQICAgIfAhkiAAAAAlwSFlz"
        b"AAA7DgAAOw4BzLahgwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAH2SURB"
        b"VHic7dw9ThtRFIbhF2IXIKXKAqiQgou0rICshIWkAwlIQk/LGgjeAiVR0qKUScdfAZagsKVEIDw3"
        b"eIbPw7yPdLvDeO75fHxNMQZJkiRJkiRJkqTHBsAX4DtwCdw1vD69yK5aoA/sAyOab7ohPNADjnj5"
        b"xhvCxC7Z5nc6hFXghnzzOxvCFvmmP1zbje54zpyQb3inJ+E3+Wa/2klYKKi5ApabvpEWuwLOgCFw"
        b"APxo4gXS7/S2rBHj/5X6z+r0E67nYGNtW0MKQ1gsKdJ/2wB2SgpLzoBrYGmm2+mmEfAB+DmtqGQC"
        b"SkLSYz1gs6qoJIC72e+lsz5WFTgBzVqpKujV8CJdD2jaJ8Tbqj92AsL8GhpmAGEGEGYAYR7CYU5A"
        b"mAGEGUCYAYR5CIc5AWEGEGYAYQYQ5iEc5gSEGUCYAYR5BoQ5AWEGEGYAYQYQ5iEc5gSEGUCYAYQZ"
        b"QJiHcJgTEGYAYQYQZgBhHsJhTkCYAYQZQJgBhJU8J3zB9OddfZL+aedVBSUT8KuGG+mqyt6VBDCs"
        b"4Ua66lsdFxmQ+bXctq9b4H1Vc99UFQB/gHfAekGt/toHDuu6WJ/xR1H6XdWWdUzNvxvH5IJfGY9W"
        b"eoPzum6BzzTQ/H8NgD3glPFX1PSm0+ti0otdYG2GvkqSJEmSJEmSpFfqHosQ5fEZtBzCAAAAAElF"
        b"TkSuQmCC"
    ),
    "import.png": base64.b64decode(
        b"iVBORw0KGgoAAAANSUhEUgAAAGAAAABgCAYAAADimHc4AAAABHNCSVQICAgIfAhkiAAAAAlwSFlz"
        b"AAA7DgAAOw4BzLahgwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAJRSURB"
        b"VHic7dwxihRRFIXhXwMnNnAVowtwdAua6XY0NNJAFNyCS1DQRegKDEbQSFswGWmDQRjE6vF13ffO"
        b"va/PB5U11K37VzVD99BgZmZmZmaH5op6AGCrHqCznTu+OmoK+zcHEHMAMQcQcwAxBxBzALFDCvAV"
        b"eAjcBz6LZ0llO+B4Ddy4cM7rwKtB506v58V/AR7sOPc94LTzDOmNuuuX9H4a0ht91y/p9TSkp7jr"
        b"l/R4GtJT3vVLIp+G9NR3/ZKop2Enfx/Qn78PyMwBxBxAzAHEHEDMAcQcQMwBxBxAzAHEHEDMAcQc"
        b"QMwBxBxAzAHEHEDMAcQcQKxHgCeNr990mOGgbWmLcAJ8I/4forIcw/05sSOIA7RGuM2cEYb7e4C1"
        b"EbJLH2BthOxKBFgTIbsyAfaNkF2pAK0RTsKni1cuQGuE7EoGmClC2QCzROgeoGWh+xzVI5QPUD3C"
        b"FAEqR5gmQNUIqwJk+0Lmp3qAjEbd/Y9GXVCwKd6Cqi4fJghQefkwIED0QDMtHwoHmGH5UDTALMuH"
        b"ggFaln83fLp4pQK0LP8O8D18unhlAuyzfMkFNCoRYN/lO0DAQGuW7wArB1q7/BmO4bz8BAG8fGGA"
        b"x42v36BfkiyAfzOuP/9mXGYOIOYAYhkC/FAP0NGln2VlCPBJPUBHl15bhgBv1QN09EY9wP+4BfxC"
        b"//d69HEGHAfuqauX6BcWfTwP3VBnR8B79EuLOt4B10I3NMAR8ILzR1e9wH2PM87v/HLLv+gm8Az4"
        b"SI3PiTbAB+Aphd7zzczMzMxM5zfAhr2E0AA5NAAAAABJRU5ErkJggg=="
    ),
    "export.png": base64.b64decode(
        b"iVBORw0KGgoAAAANSUhEUgAAAGAAAABgCAYAAADimHc4AAAABHNCSVQICAgIfAhkiAAAAAlwSFlz"
        b"AAA7DgAAOw4BzLahgwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAJTSURB"
        b"VHic7dwvi1RhGIbxyz9gUBCbxS9gEsymbTaDUWx2k9HZZjcpKCtGQbDYFL+EaBQxGDY6CrLjGnbD"
        b"Ih7nnfE855495/rBsBuG2YfnOi87Z8KAJEmSpKk50fCcefkUWWeTf/xk8o/LAHEGCDNAmAHCDBBm"
        b"gLBNCrAL3AJuAl/DswxmUwK8BK4e/nx9+PvT6EQDSd8J7wJ3OVj831wHHgIXC2eY7J3w0au+y+hP"
        b"Q+IELLvqu1SdhkmdgJarvssoT8NQJ2Ddq75Ln6dh9Cfgf676LqM5Del3QWn7wLnkAJtyH5CySA8w"
        b"9QBxBggzQJgBwgwQZoAwA4QZIMwAYQYIM0CYAcIMEGaAMAOEGSDMAGEGCDPAcg8qX9wAy92jMIIB"
        b"2pRFMEC70pPwL/Mlj7Hb/+MxeAQDhCMYIBzBAOEIBghHMEA4ggHCEQwQjjC2AKssdJ1H7xEMEI5g"
        b"gHAEAxRG8MO4Wj/6eBFPwHqP+30NbIDg8sEA0eXD+AKsKrp8MEB0+WCA6PLBANHlgwGiywcDRJcP"
        b"BoguHwxQuvzTPbzGcY6wB5xf4fkzYLvPAfwwrt2MnpcPBmg1o2D5YIAW2xQtH/zOuFX/B/TOExBm"
        b"gDADhLUE+FY+Rc739AAtAb6UT5HzKT1AS4A35VPkvE0P0BLgGfCrepCAPeB5eoiWAO+BJ9WDBDwG"
        b"PqaHaLkRAzgDvAKuFc4ypHfADeBneA5ONT5vAbwALgBXOL5vXxfAI+AOG7B8aD8BR10GbgNbwCXC"
        b"X//eYA585uDNxA7wITqNJEmSpMn7DU+aJ9jsfpbEAAAAAElFTkSuQmCC"
    ),
    "icon.png": base64.b64decode(
        b"iVBORw0KGgoAAAANSUhEUgAAAGAAAABgCAYAAADimHc4AAAABHNCSVQICAgIfAhkiAAAAAlwSFlz"
        b"AAA7DgAAOw4BzLahgwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAApSSURB"
        b"VHic5Z3rbxTXGcZ/Z7mIrCEQMESkjVRR2RhKhGhwRQhOG+JQm9AKCgGCgaY4TRHhAx/4B/ohaoRa"
        b"qUR8Qb1I0CBIGkNIhbmljajJVpikiKRgYzehKq0QNikkBgKO8dMPs2uM7d2d2TlzWfJII693z7zv"
        b"meeZc+bc5j2GmELSWKAcmApUpD8/DJSkjwfSfwGuA1fSf68DF4A2oBU4B7QZYz4LM/9uYaLOQAaS"
        b"RgNzgOr0MQtIWHTxCfBO5jDGXLFouzgh6QFJP5PUJKlH4aFH0l8lvShpXNQ8hApJCUmLJP1R0hch"
        b"kp4NX0h6Q9IzkmyWuHhBDvHPSjoTJdt5cEbSWknDo+bLGiQNl/RTSR9HSq03/FPSCyp2ISTNk/Rh"
        b"tFz6wmlJj0fNo2dIGi9pq6Tb0fJnBb2SdkqaFARX1puhkpYAvwXG27YdMT4F6o0x+20atfbUl1PX"
        b"vwI0cO+RDzABeEvSdkkjbRm1UgIkTQFeB2bbsFcEaAZWGmPO+zXkWwBJlcABYKJfW0WG/wGLjDF/"
        b"82PEVxUk6Sngz8SI/FQqxeLFi7l27VrQrsYDRyXVBO1oSEhaJak7knZJFrz33nuaNGmSksmkqqur"
        b"1dXVFYbbW5Kei4L8WDUx+5OfOUIU4bbCEkHSU5JuhnFVbjEU+RGI0K2gqyNJlZJCuRq3yEV+BCJc"
        b"l/RYUORPkdQZxlW4hRvyIxChQ9I33PLqqhUkaQSwCygtUD/rSKVSLFmyxHVrx2t6H5gIvCGXnTW3"
        b"zdBf4sxWxQKFkhmiCJXAL9wkzNsRk7QIeNtN2jBgg8S5c+eyb98+Ro8ebTFngyBgqTFmX65EOUmV"
        b"NBFnYjsWYzs27+CQRPgUqDDGXM6WIF8VtIV7kPwg7GXBBOCVXAmylgA5ExFNudKEhSDJCqEkCHg8"
        b"25jRkOTKmYp7H5gZVK7cIow7NQQRPgK+bYzpGfhDtiroJ3xFyA/JzyPA2qF+GFQCJA0DWoCyoHLj"
        b"BiE2GfsQcEn4GOeBfFcpGKoEPMdXkPwQ/H4TeHbgl3eVAEkG+BCYEUQO3CAq8vsjwJJwFnjEGNOb"
        b"+WJgCVhIhOQ3NTVZmUyZNm0alZWVjBo1qqDzU6kUy5Yt4/r1677yMQSmA3eNmA4sAW8wRDEJAzbv"
        b"/JEjR7Jr1y4WLFhAe3s7p06d6jtOnz7NjRs3XNkJqCS8boxZmfmnTwA5y8EvAvfZ9OYGTU1NLF26"
        b"1OodN2rUKPbs2cPTTz991/c9PT20tLT0CbJ3714uX87aUaWqqoqGhgZKSkqypvGIm8BkY8zVu76V"
        b"s0o5dHgZUvZ6jBs3TgcOHMjpf9OmTVEMZddneO//DFhtS2K3CPqB293dTV1dHY2NjVnTzJo1K6+d"
        b"APK5JvMhAX3VTzAzOVkQVmsnnwhuBADr+X1c0v1wpwR8Dxhmw7IbhN3UzCXCtGnTuO8+d489i/ke"
        b"DlTBHQGe9GvRLaJq52cTYfjw4cyY4b7lbTH/T8IdAeb7teYGUXeysongthrKwNJ1zAdIpOv/wDtf"
        b"x48fz9vJqqur48EHHww0H93d3axZs4ajR4/2fedVALDSWZspaUwC5zXQQMf8U6lU3nZ+fX0927dv"
        b"5/Dhw0yePDnI7HDz5k2WL1/eVxIKEQB899wTQHlGgMDgprjW19ezdetWjDGUlZVx8ODBwEXoXx15"
        b"eRAPhM/qaGqgAnglP4OwRThy5IinB/FA+BAhOAHc1PkbNmwYRH4GZWVlNDY2hvZM8NswSKVSrF07"
        b"5JxLLkxNAF/z5TlLZtzU+Vu2bBmS/AzKy8tDeya0tLT4spFMJtm0aZPX0x5OAPf78jwAhVY72RBW"
        b"deQHyWSShoYGnnjiCa+njk4A1sZabZOfQZxF8EE+wJgEMMZGRoIiP4M4iuCTfIAxRtItwNdbf0GT"
        b"3x/t7e3U1tZy8eJFX3b8wgL5ALd8v6YaJvkQj5JgiXzA6Y0V3P4Km/wMohTBJvlAVwLoKuTMqMjP"
        b"IAoRLJMP0GUk/QP4lpezmpubWbRoUc52fkVFBSdPniSRCDYET1tbGzU1NVy6dClQPyUlJTQ0NFBV"
        b"VWXT7IcJ4HMvZ1y5coUVK1bkHQVsbW1l48aN9Pb25kznF+Xl5Rw6dCjQHnNA5EO6CvqvlzO2bdtG"
        b"R0eHq7Q7duwoehECJB/gPwmcqIKusX+/t2AhxSxCwOQDnPMswPnz3uNTFKMIIZAPhQgwYsSIgjzt"
        b"2LGDl156KRQR/A7gJZNJ3nzzzaDJh7QArThvcbjCzJmFvzawc+fOUEqCn6HskpIS9u7da7OpmQ29"
        b"QFvCGPM5zhscrrB6tb/1W3GujkKqdjI4bYzpyjTS/+L2rFWrVjF37lxfnuMoQsjkgxPmp29Zyrtu"
        b"zxo2bBi7d++moqLCl/ewRCgrK6O6ujpnmgjIh/6cSxorj6GDOzo6NHv2bN8LaNevX6/bt4OJfNPb"
        b"26vNmzfn9F9aWqpjx44F4j8HvlR6aWJ/ETznIs4ixJh8SRpc5csJZO0ZcRQh5uRL0rqhBBgr6UYh"
        b"1uIkQhGQ/4WyRWyX9HqhVuMgQhGQL0m7sz6WJS30YzlKEYqEfEmqzSWAkfSRH+tRiFBE5J9Rvj0K"
        b"JNX59RKmCEVEviStzEl+WoBhktr8egpDhCIjv11OGIj8kFRvw2OQIhQZ+ZL0vCvy+5WCUza8BiFC"
        b"EZL/gdze/f1E+I4sRce1KUJPT0+xkX9bOWKJ5osZ9ztgcK+tAHR0dFBbW0tra6svOxUVFTltZMbz"
        b"582b58uPRfzGGPNith/zCVCKM2EzwUZOOjs7WbhwIWfPnrVhbhCS9tft+MVlnBhBn2ZLkLNNmo72"
        b"92M8zJjlwsSJE2lsbGT69Ok2zN2FGJIv4IVc5IOLwK3GmAPAr23lKggRYkg+wK/c7Dfjas2gnNDF"
        b"x7AYzsBWdRRT8puBKmNMd76ErhdtyglI3YzF3TL8ihBT8juASmPMv90kdr1w0xjzL5yIWgUt5h0K"
        b"fqqjmJLfBdS6JR887iFjjHkfWAzc8pixrChEhJiS3w0sM8b8PXBPklbK8hYmbjtrMetkZXBb0orA"
        b"iR8gwo9keTvazs5OVVdXZyV/ypQpOnHihE2XNnBLbkY5AxJhvqTPbF5NT0+PXnvtNdXU1Oihhx5S"
        b"aWmp5syZo5dffllXr1616coGuiR93w+HNjZyexRoBALZ7DLGuAQ8Y4z5wI8R36+vpDMwG0j5tVVE"
        b"OAk85pd8sLSZpzHmAvBd4Oc4i07vVQh4FZhnYx9JCGY72x8Cv8fSAF6McBlYZ4z5k02j1t+gM8a8"
        b"jRP8+1XujdIg4A/AdNvkBw5Jj0pqjrSd4g+nJPlbCh415ExvrpOFif4QcU7S8/I6jRhnSEpI+oGc"
        b"+dG44iNJa+Vs4XJvQs7ir1pJe1TgWlTLuCFpt5w8Rb5hUaiQsyC4XtK7ctbMh4Uv0z7XyQnbGRli"
        b"o7ikEpwJn+r0MQu7rbRPgHfSx9FB4eMjQmwEGAhJY3ACCpYDFenPX8eJ8DUaGMedaF/XgKvpv9eA"
        b"C0AbzoKCc0CbMcbaPIZN/B/mIYMlXZD0tgAAAABJRU5ErkJggg=="
    )
}
