NAME      := hdf5
SRC_EXT   := bz2
SOURCE     = http://www.hdfgroup.org/ftp/HDF5/releases/$(NAME)-$(basename $(VERSION))/$(NAME)-$(VERSION)/src/$(NAME)-$(VERSION).tar.$(SRC_EXT)
PATCHES    = hdf5-1.8.8-tstlite.patch hdf5-LD_LIBRARY_PATH.patch              \
	     hdf5-aarch64.patch hdf5-ldouble-ppc64le.patch hdf5-ppc64le.patch \
	     hdf51.8-CVE2016.patch h5comp hdf5_$(VERSION)-4.debian.tar.gz

hdf5_$(VERSION)-4.debian.tar.gz:
	curl -f -L -O https://src.fedoraproject.org/repo/pkgs/hdf5/hdf5_$(VERSION)-4.debian.tar.gz/918828a109a7c4ee0639a7515fcfb1e0/hdf5_$(VERSION)-4.debian.tar.gz

include packaging/Makefile_packaging.mk
