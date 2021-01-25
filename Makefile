NAME          := hdf5
SRC_EXT       := gz
TEST_PACKAGES := $(NAME) java-$(NAME) $(NAME)-devel $(NAME)-static $(NAME)-mpich-tests $(NAME)-openmpi3-tests
HDF5_MAJOR    := 1
HDF5_MINOR    := 13
HDF5_RELEASE  := 0-rc5
HDF5_TAG      := hdf5-$(HDF5_MAJOR)_$(HDF5_MINOR)_$(HDF5_RELEASE)
SOURCE_COMMIT := $(shell git rev-list -n 1 $(HDF5_TAG))
GIT_SHORT     := $(shell git rev-parse --short $(SOURCE_COMMIT))
BUILD_DEFINES := --define "%relval .g$(GIT_SHORT)" --define "%hdf5_major $(HDF5_MAJOR)"  --define "%hdf5_minor $(HDF5_MINOR)  --define "%hdf5_release $(HDF5_RELEASE)
RPM_BUILD_OPTIONS := $(BUILD_DEFINES)

include packaging/Makefile_packaging.mk

PR_REPOS := 

hdf5_1.12.0+repack-1~exp2.debian.tar.xz:
	curl -f -L -O http://ftp.us.debian.org/debian/pool/main/h/hdf5/hdf5_1.12.0+repack-1~exp2.debian.tar.xz

hdf5comp:
	curl -f -L -O https://src.fedoraproject.org/rpms/hdf5/raw/master/f/$@

%.patch:
	curl -f -L -O https://src.fedoraproject.org/rpms/hdf5/raw/master/f/$@
