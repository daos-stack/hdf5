NAME          := hdf5
SRC_EXT       := gz
GIT_COMMIT    := 5b5a1a81029eb7bdc975beff5f18c9c440f5de56
TEST_PACKAGES := $(NAME) java-$(NAME) $(NAME)-devel $(NAME)-static $(NAME)-mpich-tests $(NAME)-openmpi3-tests
GIT_SHORT     := $(shell git rev-parse --short $(GIT_COMMIT))
BUILD_DEFINES := --define "%relval .g$(GIT_SHORT)"

include packaging/Makefile_packaging.mk

PR_REPOS := 

hdf5_1.12.0+repack-1~exp2.debian.tar.xz:
	curl -f -L -O http://ftp.us.debian.org/debian/pool/main/h/hdf5/hdf5_1.12.0+repack-1~exp2.debian.tar.xz

hdf5comp:
	curl -f -L -O https://src.fedoraproject.org/rpms/hdf5/raw/master/f/$@
