NAME          := hdf5
SRC_EXT       := gz
TEST_PACKAGES := $(NAME) java-$(NAME) $(NAME)-devel $(NAME)-static $(NAME)-mpich-tests $(NAME)-openmpi3-tests
# release package tarballs are of the format: hdf5-1_13_0-rc5.tar.gz
# so convert . to _ and ~ to - from $(VERSION)
DL_VERSION     = $(subst ~,-,$(subst .,_,$(VERSION)))

include packaging/Makefile_packaging.mk

hdf5_1.12.0+repack-1~exp2.debian.tar.xz:
	curl -f -L -O http://ftp.us.debian.org/debian/pool/main/h/hdf5/hdf5_1.12.0+repack-1~exp2.debian.tar.xz