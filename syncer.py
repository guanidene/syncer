# -*- coding: utf-8 -*-

import csv
from pprint import pprint
from os import walk, makedirs
from os.path import exists, join
from hashlib import sha256
import shutil

SOURCE = '/home/pushpak/downloads/temp/testing-sync/source'
SYNCFOLDER = '.sync'
DEST = '/home/pushpak/downloads/temp/testing-sync/dest'
DETAILS_LASTSYNC = 'details.lastsync'
DETAILS_NOW = 'details.now'


#create_details('/home/fun/music', '/home/pushpak/desktop/a')


class FileOps():
    def move(self, *args, **kwargs):
        return shutil.move(*args, **kwargs)

    def copy(self, *args, **kwargs):
        return shutil.copy(*args, **kwargs)

#    def test():
#        fo = FileOps()
#        fo.copy('/home/pushpak/desktop/a', '/home/pushpak/desktop/b')


class FolderAnalyzer():
    @staticmethod
    def create_details(dirpath, filepath_details):
        with open(filepath_details, 'w') as f:
            csvwriter = csv.writer(f, delimiter=' ', quotechar="'")

            for root, dirs, files in walk(dirpath):
                if not SYNCFOLDER in root:
                    for filename in files:
                        filepath = join(root, filename)
                        csvwriter.writerow([filepath, sha256(open(filepath, 'rb').read()).hexdigest()])

    def __init__(self, dirpath):
        self.dirpath = dirpath
        self.syncfolderpath = join(self.dirpath, SYNCFOLDER)
        if not exists(self.syncfolderpath):
            makedirs(self.syncfolderpath)
        self.detailsnowpath = join(self.syncfolderpath, DETAILS_NOW)
        self.detailslastsyncpath = join(dirpath, SYNCFOLDER, DETAILS_LASTSYNC)
        self.syncsuccessful = False
        FolderAnalyzer.create_details(dirpath, self.detailsnowpath)
        self.list_additions, self.list_deletions = self.get_list_add_del()
        pprint(self.list_additions)
        pprint(self.list_deletions)
        self.fo = FileOps()

    def get_list_add_del(self):
        if exists(self.detailslastsyncpath):
            f1 = open(self.detailsnowpath)
            f2 = open(self.detailslastsyncpath)
            detailsnow = set([line.strip() for line in f1])
            detailslastsync = set([line.strip() for line in f2])
            f1.close()
            f2.close()
            return list(detailsnow.difference(detailslastsync)),  \
                   list(detailslastsync.difference(detailsnow))
        else:
            return ([], [])

    def __del__(self):
        if self.syncsuccessful:
            self.fo.move(self.detailsnowpath, self.detailslastsyncpath)


class FoldersSyncer():
    def __init__(self, sourcepath, destpath):
        pass


if __name__ == '__main__':
    f = FolderAnalyzer('/home/pushpak/downloads/temp/testing-sync/source')
