NAME          := hdf5
SRC_EXT       := gz
TEST_PACKAGES := $(NAME) java-$(NAME) $(NAME)-devel $(NAME)-static $(NAME)-mpich-tests $(NAME)-openmpi3-tests
SOURCE_COMMIT := 5b5a1a81029eb7bdc975beff5f18c9c440f5de56
DEBIAN_SOURCE := hdf5_1.12.0+repack-1~exp2.debian.tar.xz
HDF5COMP      := hdf5comp
GIT_SHORT     := $(shell git rev-parse --short $(SOURCE_COMMIT))
BUILD_DEFINES := --define "%relval .g$(GIT_SHORT)" --define "%source_commit $(SOURCE_COMMIT)" \
                 --define "%debian_source $(DEBIAN_SOURCE)" --define "%hdf5comp $(HDF5COMP)"
RPM_BUILD_OPTIONS := $(BUILD_DEFINES)
include packaging/Makefile_packaging.mk

$(SOURCE_COMMIT).tar.$(SRC_EXT):
	curl -f -L -O https://github.com/HDFGroup/hdf5/archive/$(SOURCE_COMMIT).tar.$(SRC_EXT)

PR_REPOS := 

$(DEBIAN_SOURCE):
	curl -f -L -O http://ftp.us.debian.org/debian/pool/main/h/hdf5/hdf5_1.12.0+repack-1~exp2.debian.tar.xz

$(HDF5COMP):
	curl -f -L -O https://src.fedoraproject.org/rpms/hdf5/raw/master/f/$@

%.patch:
	curl -f -L -O https://src.fedoraproject.org/rpms/hdf5/raw/master/f/$@
