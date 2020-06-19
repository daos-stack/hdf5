NAME      := hdf5
SRC_EXT   := bz2

include packaging/Makefile_packaging.mk

PR_REPOS := 

hdf5_1.10.4+repack-1.debian.tar.xz:
	curl -f -L -O http://ftp.us.debian.org/debian/pool/main/h/hdf5/hdf5_1.10.4+repack-1.debian.tar.xz

hdf5comp:
	curl -f -L -O https://src.fedoraproject.org/rpms/hdf5/raw/master/f/$@

%.patch:
	curl -f -L -O https://src.fedoraproject.org/rpms/hdf5/raw/master/f/$@

test:
	$(call install_repos,$(NAME)@$(BRANCH_NAME):$(BUILD_NUMBER))
	yum -y install $(NAME) java-$(NAME) $(NAME)-devel $(NAME)-static $(NAME)-tests
	yum -y install $(NAME)-mpich $(NAME)-mpich-devel $(NAME)-mpich-static
