NAME          := hdf5
SRC_EXT       := gz
TEST_PACKAGES := $(NAME) java-$(NAME) $(NAME)-devel $(NAME)-static $(NAME)-mpich-tests $(NAME)-openmpi3-tests
# release package tarballs are of the format: hdf5-1_13_0-rc5.tar.gz
# so convert . to _ and ~ to - from $(VERSION)
DL_VERSION     = $(subst ~,-,$(subst .,_,$(VERSION)))

include source_deps.mk

include packaging/Makefile_packaging.mk

source_deps.mk:
	for s in $(SOURCES); do \
		echo $${s##*/}:; \
	done > $@