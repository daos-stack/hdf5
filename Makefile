NAME          := hdf5
SRC_EXT       := gz
TEST_PACKAGES := $(NAME) java-$(NAME) $(NAME)-devel $(NAME)-static $(NAME)-mpich-tests $(NAME)-openmpi3-tests
DL_VERSION    := fa40c6c59af5d9aabd4b478cd02f8a9f7ebf7922
GIT_SHORT     := $(shell git rev-parse --short $(DL_VERSION))
BUILD_DEFINES := --define "%relval .g$(GIT_SHORT)" --define "%hdf5_commit $(DL_VERSION)"

include packaging/Makefile_packaging.mk

PR_REPOS := 

hdf5_1.12.0+repack-1~exp2.debian.tar.xz:
	curl -f -L -O http://ftp.us.debian.org/debian/pool/main/h/hdf5/hdf5_1.12.0+repack-1~exp2.debian.tar.xz

hdf5comp:
	curl -f -L -O https://src.fedoraproject.org/rpms/hdf5/raw/master/f/$@

%.patch:
	curl -f -L -O https://src.fedoraproject.org/rpms/hdf5/raw/master/f/$@
