NAME           := hdf5
SRC_EXT        := gz
TEST_PACKAGES  := $(NAME) java-$(NAME) $(NAME)-devel $(NAME)-static $(NAME)-mpich-tests $(NAME)-openmpi3-tests
VERSION        = $(eval VERSION := $(shell rpm --specfile --qf '%{version}\n' $(NAME).spec | sed -n '1p'))$(VERSION)
HDF5_VERSION   = $(echo $VERSION | sed 's/\./\_/g' | sed 's/\~/\-/g')


include packaging/Makefile_packaging.mk

PR_REPOS := 

hdf5_1.12.0+repack-1~exp2.debian.tar.xz:
	curl -f -L -O http://ftp.us.debian.org/debian/pool/main/h/hdf5/hdf5_1.12.0+repack-1~exp2.debian.tar.xz

hdf5comp:
	curl -f -L -O https://src.fedoraproject.org/rpms/hdf5/raw/master/f/$@

%.patch:
	curl -f -L -O https://src.fedoraproject.org/rpms/hdf5/raw/master/f/$@

hdf5-$(HDF5_VERSION).tar.$(SRC_EXT):
	rm -f ./*.tar.{gz,bz*,xz}
	spectool -g $(NAME).spec
