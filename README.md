# FAT-File-Recovery-Project
Python script used to recover files from a disk image that is missing the Bios Parameter Block
The goal of this project was to recover files from a disk image. Not all of the files are contiguous, meaning some of the files are fragmented across the disk. 
The python script walks the FAT to identify which clusters to read in which orders to dump the files.
