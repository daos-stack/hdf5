NAME      := hdf5
SRC_EXT   := bz2

include packaging/Makefile_packaging.mk

PR_REPOS := mpich@PR-10

hdf5_1.10.4+repack-1.debian.tar.xz:
	curl -f -L -O http://ftp.us.debian.org/debian/pool/main/h/hdf5/hdf5_1.10.4+repack-1.debian.tar.xz

hdf5comp:
	curl -f -L -O https://src.fedoraproject.org/rpms/hdf5/raw/master/f/$@

%.patch:
	curl -f -L -O https://src.fedoraproject.org/rpms/hdf5/raw/master/f/$@
