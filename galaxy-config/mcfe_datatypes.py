"""
Classes for MCFE added datatypes
"""

from galaxy.datatypes import data

import logging

log = logging.getLogger(__name__)


class vtp(data.Data):
    file_ext = "vtp"


class vtk(data.Data):
    file_ext = "vtk"


class usd(data.Data):
    file_ext = "usd"


class usda(data.Data):
    file_ext = "udsa"


class usdc(data.Data):
    file_ext = "usdc"


class usdz(data.Data):
    file_ext = "usdz"


class obj(data.Data):
    file_ext = "obj"


class stp(data.Data):
    file_ext = "stp"


class step(data.Data):
    file_ext = "step"


class h5(data.Data):
    file_ext = "h5"


class h5m(data.Data):
    file_ext = "h5m"


class out(data.Data):
    file_ext = "out"


class xml(data.Data):
    file_ext = "xml"


class stl(data.Data):
    file_ext = "stl"


class npz(data.Data):
    file_ext = "npz"
