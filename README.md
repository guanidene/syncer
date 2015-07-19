# syncer
Easily keep 2 directories in complete sync. 
By **complete sync** I mean their checksums should match!.

# Notes/Working -
* Changes can be categorized as follows - addition (of new file/folder), deletion (of existing file/folder), modification (of existing file/folder). 
Renaming would not be given special treatment. It will be treated as (deletion + addition).
* To detect whether a file has been modified or not, checksum would be used.
* Syncer will store its own metadata in *.sync* folder within each of the 2 directories in sync. 
This folder will contain a file *details.lastsync*, which will hold information about files and folders which were "correctly" synced the previous time. If no sync has happened, this file would not be present.
* 

# Expected features -
* Syncer should be able to recognize if a previous sync operation got aborted midway. It should not retransmit extra/redundant data.
* Syncer should support sync across atleast networked filesystems (over ssh), besides local filesystems.



# Todos - 
* Should we rename the package? To somethiing like fsyncer/dirsyncer/etc.?
* Should we start commiting from sratch, since the commits pushed in now are not for incremental changed. I have pushed in multiple improvements in a single commit.
