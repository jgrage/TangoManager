#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Easy to use manager for configuring and registering tango device servers"""

__author__ = "Jonas Grage"
__copyright__ = "Copyright 2020"
__license__ = "GPLv3"
__version__ = "1.0"
__maintainer__ = "Jonas Grage"
__email__ = "grage@physik.tu-berlin.de"
__status__ = "Production"

import os
import sys
import errno
import argparse
from tango import Database, DbDevInfo
from configparser import ConfigParser


class TangoManager:
    def __init__(self, instance, dir=None):
        self.config = ConfigParser()
        self.db_handler = Database()
        self._instance = instance
        self._choose_config_dir(dir)
        self._load_config_file()
    
        self._name = self.config.get("device", "name")
        self._prefix = self.config.get("device", "class")
        self._class = self.config.get("device", "class")
        
        
    def _choose_config_dir(self, dir):
        if dir is not None:
            self._dir = dir
        elif "TANGO_CONFIG_DIR" in os.environ:
            self._dir = os.environ["TANGO_CONFIG"]
        else:
            self._dir = "/opt/tango/etc"
            
            
    def _load_config_file(self):
        filename="{0}/{1}.conf".format(self._dir, self._instance)

        if os.path.isfile(filename) is not True:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), filename)

        if os.access(filename, os.R_OK) is not True:
            raise PermissionError(errno.EACCES, os.strerror(errno.EACCES), filename)

        print("reading config file {0}".format(filename))
        self.config.read(filename)
        
        
    def add_tango_device(self):
        print("registering device {0}".format(self._name))
    
        new_device = DbDevInfo()
        new_device.name = self._name
        new_device._class = self._class
        new_device.server = "{0}/{1}".format(self._prefix, self._instance)
    
        properties = {}
        for key, val in self.config.items("properties"):
            maybe_a_list = val.split(",")
            if len(maybe_a_list) > 1:
                properties[key] = maybe_a_list
            else:
                properties[key]=val

        self.db_handler.put_device_property(self._name, properties)
        self.db_handler.add_device(new_device)
        
        
    def remove_tango_device(self):
        print("deleting device {0}".format(self._name))
        #self.db_handler.delete_device(self._name)
        self.db_handler.delete_server("{0}/{1}".format(self._prefix, self._instance))
        
        
    def unexport_tango_device(self):
        if self.is_exported() == True:
            print("unexporting device {0}".format(self._name))
            self.db_handler.unexport_server("{0}/{1}".format(self._prefix, self._instance))
        else:
            return
            
            
    def is_exported(self):
        if bool(self.db_handler.import_device(self._name).exported) == True:
            print("device {0} is exported".format(self._name))
            return True
        else:
            print("device {0} is not exported".format(self._name))
            return False
            
            
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", "-d")
    parser.add_argument("action", choices=["add", "remove", "unexport", "status"])
    parser.add_argument("instance")
    args = parser.parse_args()
    
    try:
        
        manager = TangoManager(args.instance, dir=args.dir)

        if args.action == "add":
            manager.add_tango_device()

        elif args.action == "remove":
            manager.remove_tango_device()

        elif args.action == "unexport":
            manager.unexport_tango_device()

        elif args.action == "status":
            manager.is_exported()
    
    except Exception as e:
        print(e)
        exit()

    


