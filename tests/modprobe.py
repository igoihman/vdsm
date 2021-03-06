#
# Copyright 2015 Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
#
# Refer to the README and COPYING files for full details of the license
import os
from functools import wraps
from nose.plugins.skip import SkipTest

from vdsm import commands
from vdsm import utils

modprobe = utils.CommandPath("modprobe",
                             "/usr/sbin/modprobe",  # Fedora, EL7
                             )


def RequireDummyMod(f):
    """
    Assumes root privileges to be used after
    ValidateRunningAsRoot decoration.
    """
    return _require_mod(f, 'dummy')


def RequireBondingMod(f):
    """
    Assumes root privileges to be used after
    ValidateRunningAsRoot decoration.
    """
    return _require_mod(f, 'bonding')


def RequireVethMod(f):
    """
    Assumes root privileges to be used after
    ValidateRunningAsRoot decoration.
    """
    return _require_mod(f, 'veth')


def _require_mod(f, name):
    @wraps(f)
    def wrapper(*args, **kwargs):
        _validate_module(name)
        return f(*args, **kwargs)

    return wrapper


def _validate_module(name):
    if not os.path.exists('/sys/module/' + name):
        cmd_modprobe = [modprobe.cmd, name]
        rc, out, err = commands.execCmd(cmd_modprobe, sudo=True)
        if rc != 0:
            raise SkipTest("This test requires %s module "
                           "(failed to load module: rc=%s, out=%s, err=%s)" %
                           (name, rc, out, err))
