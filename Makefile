NAME      := hdf5
SRC_EXT   := bz2

LOCAL_REPOS := false

include packaging/Makefile_packaging.mk

hdf5_$(VERSION)-4.debian.tar.gz:
	curl -f -L -O https://src.fedoraproject.org/repo/pkgs/hdf5/hdf5_$(VERSION)-4.debian.tar.gz/918828a109a7c4ee0639a7515fcfb1e0/hdf5_$(VERSION)-4.debian.tar.gz

