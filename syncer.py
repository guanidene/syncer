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


class FileOps(object):
    """
    Class to provide basic file operations - copy, move, delete - across
    multiple filesystems, especially local and over ssh.
    """

    @classmethod
    def move(classobj, *args, **kwargs):
        return shutil.move(*args, **kwargs)

    @classmethod
    def copy(classobj, *args, **kwargs):
        return shutil.copy(*args, **kwargs)

#    def test():
#        fo = FileOps()
#        fo.copy('/home/pushpak/desktop/a', '/home/pushpak/desktop/b')


class Details():
    def __init__(self, dirpath, filepath=None, read_details=False):
        self.dirpath = dirpath
        if not filepath:
            self.filepath = join(self.dirpath, SYNCFOLDER, DETAILS_NOW)
        else:
            self.filepath = filepath
        self.details = {}
        if read_details is True:
            self.read_details()

    def read_details(self):
        """
        Populate self.details dictionary as per this format:
        <filepath>:<hash>
        """
        with open(self.filepath, 'r') as f:
            csvreader = csv.reader(f, delimiter=' ', quotechar="'")
            for line in csvreader:
                self.details[line[0]] = line[1]

    def create_details(self):
        self.details = {}
        with open(self.filepath, 'w') as f:
            csvwriter = csv.writer(f, delimiter=' ', quotechar="'")

            for root, dirs, files in walk(self.dirpath):
                if not SYNCFOLDER in root:
                    for filename in files:
                        filepath = join(root, filename)
                        hash_ = sha256(open(filepath, 'rb').read()).hexdigest()
                        relfilepath = filepath[len(self.dirpath):].lstrip('/')     # Remove self.dirpath from filepath before saving. XXX. find a better way to do this
                        csvwriter.writerow([relfilepath, hash_])
                        self.details[relfilepath] = hash_


class FolderAnalyzer():

    def __init__(self, dirpath):
        self.dirpath = dirpath
        self.metadatapath = join(self.dirpath, SYNCFOLDER)
        if not exists(self.metadatapath):
            makedirs(self.metadatapath)
        self.detailsnowpath = join(self.metadatapath, DETAILS_NOW)
        self.detailslastsyncpath = join(dirpath, SYNCFOLDER, DETAILS_LASTSYNC)
#        self.syncsuccessful = False
        self.detailsnow = Details(dirpath)
        self.detailsnow.create_details()
        self.details_additions = {}
        self.details_deletions = {}
        self.get_additions()
        self.get_deletions()
        self.fileops = FileOps

#        print 'New files:\n', pprint(self.details_additions)
#        print 'Deleted files:\n', pprint(self.details_deletions)

#        self.syncsuccessful = True
#        self.moveXXX()


    def get_additions(self):
        """
        Returns a list of "<filepath> <hash>" strings of
        <filepath>(s) new or modified from the previous sync
        """
        if exists(self.detailslastsyncpath):
            self.detailslastsync = Details(self.dirpath, self.detailslastsyncpath, True)
            for relfilepath in self.detailsnow.details:
                if relfilepath not in self.detailslastsync.details:
                    self.details_additions[relfilepath] = self.detailsnow.details[relfilepath]
        else:
            self.details_additions = self.detailsnow.details

    def get_deletions(self):
        """
        Returns a list of "<filepath> <hash>" strings of
        <filepath>(s) deleted from the previous sync
        """
        if exists(self.detailslastsyncpath):
            self.detailslastsync = Details(self.dirpath, self.detailslastsyncpath, True)
            for relfilepath in self.detailslastsync.details:
                if relfilepath not in self.detailsnow.details:
                    self.details_deletions[relfilepath] = self.detailslastsync.details[relfilepath]
        else:
            self.details_deletions = {}

    # XXX. move this method to Syncer class
    def moveXXX(self):
        FileOps.move(self.detailsnowpath, self.detailslastsyncpath)


class Syncer():
    def __init__(self, sourcepath, destpath):
        self.sourcepath = sourcepath
        self.destpath = destpath
        self.sourceanalyzer = FolderAnalyzer(self.sourcepath)
        self.destanalyzer = FolderAnalyzer(self.destpath)
        self.moves = {} # <sourcepath>:<destpath>
        self.deletes = [] # <sourcepath>

    def get_moves(self):
        """
        From self.list_additions_source and self.list_additions_dest,
        generate a list of "<sourcepath> <destpath>" ie list of "moves" to be
        done to keep the folders in sync
        """
        for relfilepath in self.sourceanalyzer.details_additions:
            if relfilepath in self.destanalyzer.details_additions:
                # file exists at both places
                if self.sourceanalyzer.details_additions[relfilepath] == \
                   self.destanalyzer.details_additions[relfilepath]:
                       #if hash matches, do nothing.
                       pass
                else:
                    print 'File "%s" exists at dest, but with different hash. Adding to list of moves...' % relfilepath
                    self.moves[join(self.sourcepath, relfilepath)] = join(self.destpath, relfilepath)
            elif relfilepath in self.destanalyzer.details_deletions:
                print 'Something wrong here... "%s" is added at source but deleted at dest. This can\'t happen if both source dest were in sync previously... Aborting....' % filepath
                raise SystemExit
            else:
                print 'File "%s" exists at source but not at dest. Adding to list of moves...' % relfilepath
                self.moves[join(self.sourcepath, relfilepath)] = join(self.destpath, relfilepath)

        for relfilepath in self.destanalyzer.details_additions:
            if relfilepath in self.sourceanalyzer.details_additions:
                # this case covered above, so simply ignore here (Note: Don't delete this if clause)
                pass
            elif relfilepath in self.sourceanalyzer.details_deletions:
               print 'Something wrong here... "%s" is added at dest but deleted at source. This can\'t happen if both source dest were in sync previously... Aborting....' % filepath
               raise SystemExit
            else:
               print 'File "%s" exists at dest but not at source. Adding to list of moves...' % relfilepath
               self.moves[join(self.destpath, relfilepath)] = join(self.sourcepath, relfilepath)

    def get_deletes(self):
        """
        From self.list_additions_source and self.list_additions_dest,
        generate a list of "<sourcepath>" ie list of files to be "deleted"
        to keep the folders in sync
        """
        raise NotImplemented

if __name__ == '__main__':
#    f = FolderAnalyzer('/home/pushpak/downloads/temp/testing-sync/source')
    syncer = Syncer('/home/pushpak/downloads/temp/testing-sync/source', '/home/pushpak/downloads/temp/testing-sync/dest')
    syncer.get_moves()
    print
    print '='*20
    pprint(syncer.moves)
