# Common Makefile for including
# Needs the following variables set at a minium:
# NAME :=
# SRC_EXT :=

# Put site overrides (i.e. REPOSITORY_URL, DAOS_STACK_*_LOCAL_REPO) in here
-include Makefile.local

include packaging/Makefile_distro_vars.mk

ifeq ($(DEB_NAME),)
DEB_NAME := $(NAME)
endif

CALLING_MAKEFILE := $(word 1, $(MAKEFILE_LIST))

DOT     := .
RPM_BUILD_OPTIONS += $(EXTERNAL_RPM_BUILD_OPTIONS)

# some defaults the caller can override
BUILD_OS ?= leap.15
CHROOT_NAME ?= opensuse-leap-15-x86_64
PACKAGING_CHECK_DIR ?= ../packaging
LOCAL_REPOS ?= true

COMMON_RPM_ARGS  := --define "%_topdir $$PWD/_topdir" $(BUILD_DEFINES)
SPEC             := $(shell if [ -f $(NAME)-$(DISTRO_BASE).spec ]; then echo $(NAME)-$(DISTRO_BASE).spec; else echo $(NAME).spec; fi)
VERSION           = $(eval VERSION := $(shell rpm $(COMMON_RPM_ARGS) --specfile --qf '%{version}\n' $(SPEC) | sed -n '1p'))$(VERSION)
DEB_VERS         := $(subst rc,~rc,$(VERSION))
DEB_RVERS        := $(subst $(DOT),\$(DOT),$(DEB_VERS))
DEB_BVERS        := $(basename $(subst ~rc,$(DOT)rc,$(DEB_VERS)))
RELEASE           = $(eval RELEASE := $(shell rpm $(COMMON_RPM_ARGS) --specfile --qf '%{release}\n' $(SPEC) | sed -n '$(SED_EXPR)'))$(RELEASE)
SRPM              = _topdir/SRPMS/$(NAME)-$(VERSION)-$(RELEASE)$(DIST).src.rpm
RPMS              = $(eval RPMS := $(addsuffix .rpm,$(addprefix _topdir/RPMS/x86_64/,$(shell rpm --specfile $(SPEC)))))$(RPMS)
DEB_TOP          := _topdir/BUILD
DEB_BUILD        := $(DEB_TOP)/$(NAME)-$(DEB_VERS)
DEB_TARBASE      := $(DEB_TOP)/$(DEB_NAME)_$(DEB_VERS)
SOURCE            = $(eval SOURCE := $(shell spectool -S -l $(SPEC) | sed -e 2,\$$d -e 's/.*:  *//'))$(SOURCE)
PATCHES           = $(eval PATCHES := $(shell spectool -l $(SPEC) | sed -e 1d -e 's/.*:  *//' -e 's/.*\///'))$(PATCHES)
SOURCES          := $(addprefix _topdir/SOURCES/,$(notdir $(SOURCE)) $(PATCHES))
ifeq ($(ID_LIKE),debian)
DEBS             := $(addsuffix _$(DEB_VERS)-1_amd64.deb,$(shell sed -n '/-udeb/b; s,^Package:[[:blank:]],$(DEB_TOP)/,p' debian/control))
DEB_PREV_RELEASE := $(shell dpkg-parsechangelog -S version)
DEB_DSC          := $(DEB_NAME)_$(DEB_PREV_RELEASE)$(GIT_INFO).dsc
#Ubuntu Containers do not set a UTF-8 environment by default.
ifndef LANG
export LANG = C.UTF-8
endif
ifndef LC_ALL
export LC_ALL = C.UTF-8
endif
TARGETS := $(DEBS)
else
# CentOS/Suse packages that want a locale set need this.
ifndef LANG
export LANG = en_US.utf8
endif
ifndef LC_ALL
export LC_ALL = en_US.utf8
endif
TARGETS := $(RPMS) $(SRPM)
endif

define distro_map
	    case $(DISTRO_ID) in           \
	        el7) distro="centos7"      \
	        ;;                         \
	        el8) distro="centos8"      \
	        ;;                         \
	        sle12.3) distro="sles12.3" \
	        ;;                         \
	        sl42.3) distro="leap42.3"  \
	        ;;                         \
	        sl15.1) distro="leap15"    \
	        ;;                         \
	    esac;
endef

define install_repos
	for repo in $($(DISTRO_BASE)_PR_REPOS)                              \
	            $(PR_REPOS) $(1); do                                    \
	    branch="master";                                                \
	    build_number="lastSuccessfulBuild";                             \
	    if [[ $$repo = *@* ]]; then                                     \
	        branch="$${repo#*@}";                                       \
	        repo="$${repo%@*}";                                         \
	        if [[ $$branch = *:* ]]; then                               \
	            build_number="$${branch#*:}";                           \
	            branch="$${branch%:*}";                                 \
	        fi;                                                         \
	    fi;                                                             \
	    $(call distro_map)                                              \
	    baseurl=$${JENKINS_URL:-https://build.hpdd.intel.com/}job/daos-stack/job/$$repo/job/$$branch/; \
	    baseurl+=$$build_number/artifact/artifacts/$$distro/;           \
	    $(call install_repo,$$baseurl);                                 \
        done
endef

all: $(TARGETS)

%/:
	mkdir -p $@

%.gz: %
	rm -f $@
	gzip $<

_topdir/SOURCES/%: % | _topdir/SOURCES/
	rm -f $@
	ln $< $@

# At least one spec file, SLURM (sles), has a different version for the
# download file than the version in the spec file.
ifeq ($(DL_VERSION),)
DL_VERSION = $(VERSION)
endif

$(NAME)-$(DL_VERSION).tar.$(SRC_EXT).asc:
	rm -f ./$(NAME)-*.tar.{gz,bz*,xz}.asc
	curl -f -L -O '$(SOURCE).asc'

$(NAME)-$(DL_VERSION).tar.$(SRC_EXT):
	rm -f ./$(NAME)-*.tar.{gz,bz*,xz}
	curl -f -L -O '$(SOURCE)'

v$(DL_VERSION).tar.$(SRC_EXT):
	rm -f ./v*.tar.{gz,bz*,xz}
	curl -f -L -O '$(SOURCE)'

$(DL_VERSION).tar.$(SRC_EXT):
	rm -f ./*.tar.{gz,bz*,xz}
	curl -f -L -O '$(SOURCE)'

$(DEB_TOP)/%: % | $(DEB_TOP)/

$(DEB_BUILD)/%: % | $(DEB_BUILD)/

$(DEB_BUILD).tar.$(SRC_EXT): $(notdir $(SOURCE)) | $(DEB_TOP)/
	ln -f $< $@

$(DEB_TARBASE).orig.tar.$(SRC_EXT) : $(DEB_BUILD).tar.$(SRC_EXT)
	rm -f $(DEB_TOP)/*.orig.tar.*
	ln -f $< $@

$(DEB_TOP)/.detar: $(notdir $(SOURCE)) $(DEB_TARBASE).orig.tar.$(SRC_EXT) 
	# Unpack tarball
	rm -rf ./$(DEB_BUILD)/*
	mkdir -p $(DEB_BUILD)
	tar -C $(DEB_BUILD) --strip-components=1 -xpf $<
	touch $@

# Extract patches for Debian
$(DEB_TOP)/.patched: $(PATCHES) check-env $(DEB_TOP)/.detar | \
	$(DEB_BUILD)/debian/
	mkdir -p ${DEB_BUILD}/debian/patches
	mkdir -p $(DEB_TOP)/patches
	for f in $(PATCHES); do \
          rm -f $(DEB_TOP)/patches/*; \
	  if git mailsplit -o$(DEB_TOP)/patches < "$$f" ;then \
	      fn=$$(basename "$$f"); \
	      for f1 in $(DEB_TOP)/patches/*;do \
	        [ -e "$$f1" ] || continue; \
	        f1n=$$(basename "$$f1"); \
	        echo "$${fn}_$${f1n}" >> $(DEB_BUILD)/debian/patches/series ; \
	        mv "$$f1" $(DEB_BUILD)/debian/patches/$${fn}_$${f1n}; \
	      done; \
	  else \
	    fb=$$(basename "$$f"); \
	    cp "$$f" $(DEB_BUILD)/debian/patches/ ; \
	    echo "$$fb" >> $(DEB_BUILD)/debian/patches/series ; \
	    if ! grep -q "^Description:\|^Subject:" "$$f" ;then \
	      sed -i '1 iSubject: Auto added patch' \
	        "$(DEB_BUILD)/debian/patches/$$fb" ;fi ; \
	    if ! grep -q "^Origin:\|^Author:\|^From:" "$$f" ;then \
	      sed -i '1 iOrigin: other' \
	        "$(DEB_BUILD)/debian/patches/$$fb" ;fi ; \
	  fi ; \
	done
	touch $@


# Move the debian files into the Debian directory.
ifeq ($(ID_LIKE),debian)
$(DEB_TOP)/.deb_files : $(shell find debian -type f) \
	  $(DEB_TOP)/.detar | \
	  $(DEB_BUILD)/debian/
	find debian -maxdepth 1 -type f -exec cp '{}' '$(DEB_BUILD)/{}' ';'
	if [ -e debian/source ]; then \
	  cp -r debian/source $(DEB_BUILD)/debian; fi
	if [ -e debian/local ]; then \
	  cp -r debian/local $(DEB_BUILD)/debian; fi
	if [ -e debian/examples ]; then \
	  cp -r debian/examples $(DEB_BUILD)/debian; fi
	if [ -e debian/upstream ]; then \
	  cp -r debian/upstream $(DEB_BUILD)/debian; fi
	if [ -e debian/tests ]; then \
	  cp -r debian/tests $(DEB_BUILD)/debian; fi
	rm -f $(DEB_BUILD)/debian/*.ex $(DEB_BUILD)/debian/*.EX
	rm -f $(DEB_BUILD)/debian/*.orig
	touch $@
endif

# see https://stackoverflow.com/questions/2973445/ for why we subst
# the "rpm" for "%" to effectively turn this into a multiple matching
# target pattern rule
$(subst rpm,%,$(RPMS)): $(SPEC) $(SOURCES)
	rpmbuild -bb $(COMMON_RPM_ARGS) $(RPM_BUILD_OPTIONS) $(SPEC)

$(subst deb,%,$(DEBS)): $(DEB_BUILD).tar.$(SRC_EXT) \
	  $(DEB_TOP)/.deb_files $(DEB_TOP)/.detar $(DEB_TOP)/.patched
	rm -f $(DEB_TOP)/*.deb $(DEB_TOP)/*.ddeb $(DEB_TOP)/*.dsc \
	      $(DEB_TOP)/*.dsc $(DEB_TOP)/*.build* $(DEB_TOP)/*.changes \
	      $(DEB_TOP)/*.debian.tar.*
	rm -rf $(DEB_TOP)/*-tmp
	cd $(DEB_BUILD); debuild --no-lintian -b -us -uc
	cd $(DEB_BUILD); debuild -- clean
	git status
	rm -rf $(DEB_TOP)/$(NAME)-tmp
	lfile1=$(shell echo $(DEB_TOP)/$(NAME)[0-9]*_$(DEB_VERS)-1_amd64.deb);\
	  lfile=$$(ls $${lfile1}); \
	  lfile2=$${lfile##*/}; lname=$${lfile2%%_*}; \
	  dpkg-deb -R $${lfile} \
	    $(DEB_TOP)/$(NAME)-tmp; \
	  if [ -e $(DEB_TOP)/$(NAME)-tmp/DEBIAN/symbols ]; then \
	    sed 's/$(DEB_RVERS)-1/$(DEB_BVERS)/' \
	    $(DEB_TOP)/$(NAME)-tmp/DEBIAN/symbols \
	    > $(DEB_BUILD)/debian/$${lname}.symbols; fi
	cd $(DEB_BUILD); debuild -us -uc
	rm $(DEB_BUILD).tar.$(SRC_EXT)
	for f in $(DEB_TOP)/*.deb; do \
	  echo $$f; dpkg -c $$f; done

$(SRPM): $(SPEC) $(SOURCES)
	rpmbuild -bs $(COMMON_RPM_ARGS) $(RPM_BUILD_OPTIONS) $(SPEC)

srpm: $(SRPM)

$(RPMS): $(SRPM) $(CALLING_MAKEFILE)

rpms: $(RPMS)

$(DEBS): $(CALLING_MAKEFILE)

debs: $(DEBS)

ls: $(TARGETS)
	ls -ld $^

ifeq ($(ID_LIKE),rhel fedora)
chrootbuild: $(SRPM) $(CALLING_MAKEFILE)
	if [ -w /etc/mock/default.cfg ]; then                                    \
	    echo -e "config_opts['yum.conf'] += \"\"\"\n" >> /etc/mock/default.cfg;  \
	    for repo in $(ADD_REPOS); do                                             \
	        if [[ $$repo = *@* ]]; then                                          \
	            branch="$${repo#*@}";                                            \
	            repo="$${repo%@*}";                                              \
	        else                                                                 \
	            branch="master";                                                 \
	        fi;                                                                  \
	        echo -e "[$$repo:$$branch:lastSuccessful]\n\
name=$$repo:$$branch:lastSuccessful\n\
baseurl=$${JENKINS_URL}job/daos-stack/job/$$repo/job/$$branch/lastSuccessfulBuild/artifact/artifacts/centos7/\n\
enabled=1\n\
gpgcheck = False\n" >> /etc/mock/default.cfg;                                        \
	    done;                                                                    \
	    echo "\"\"\"" >> /etc/mock/default.cfg;                                  \
	else                                                                         \
	    echo "Unable to update /etc/mock/default.cfg.";                          \
            echo "You need to make sure it has the needed repos in it yourself.";    \
	fi
	mock $(MOCK_OPTIONS) $(RPM_BUILD_OPTIONS) $<
else
sle12_REPOS += --repo https://download.opensuse.org/repositories/science:/HPC/openSUSE_Leap_42.3/     \
	       --repo http://cobbler/cobbler/repo_mirror/sdkupdate-sles12.3-x86_64/                   \
	       --repo http://cobbler/cobbler/repo_mirror/sdk-sles12.3-x86_64                          \
	       --repo http://download.opensuse.org/repositories/openSUSE:/Backports:/SLE-12/standard/ \
	       --repo http://cobbler/cobbler/repo_mirror/updates-sles12.3-x86_64                      \
	       --repo http://cobbler/cobbler/pub/SLES-12.3-x86_64/

sl42_REPOS += --repo https://download.opensuse.org/repositories/science:/HPC/openSUSE_Leap_42.3 \
	      --repo http://download.opensuse.org/update/leap/42.3/oss/                         \
	      --repo http://download.opensuse.org/distribution/leap/42.3/repo/oss/suse/

sl15_REPOS += --repo http://download.opensuse.org/update/leap/15.1/oss/            \
	      --repo http://download.opensuse.org/distribution/leap/15.1/repo/oss/

chrootbuild: $(SRPM) $(CALLING_MAKEFILE)
	if [ -w /etc/mock/$(CHROOT_NAME).cfg ]; then                                        \
	    echo -e "config_opts['yum.conf'] += \"\"\"\n" >> /etc/mock/$(CHROOT_NAME).cfg;  \
	    $(call distro_map)                                                              \
	    for repo in $($(DISTRO_BASE)_PR_REPOS) $(PR_REPOS); do                          \
	        branch="master";                                                            \
	        build_number="lastSuccessfulBuild";                                         \
	        if [[ $$repo = *@* ]]; then                                                 \
	            branch="$${repo#*@}";                                                   \
	            repo="$${repo%@*}";                                                     \
	            if [[ $$branch = *:* ]]; then                                           \
	                build_number="$${branch#*:}";                                       \
	                branch="$${branch%:*}";                                             \
	            fi;                                                                     \
	        fi;                                                                         \
	        echo -e "[$$repo:$$branch:$$build_number]\n\
name=$$repo:$$branch:$$build_number\n\
baseurl=$${JENKINS_URL:-https://build.hpdd.intel.com/}job/daos-stack/job/$$repo/job/$$branch/$$build_number/artifact/artifacts/$$distro/\n\
enabled=1\n\
gpgcheck=False\n" >> /etc/mock/$(CHROOT_NAME).cfg;                                          \
	    done;                                                                           \
	    if ! $(LOCAL_REPOS); then                                                       \
	        LOCAL_REPOS="";                                                             \
	    else                                                                            \
	        LOCAL_REPOS="$($(DISTRO_BASE)_LOCAL_REPOS)";                                \
	    fi;                                                                             \
	    for repo in $$LOCAL_REPOS $($(DISTRO_BASE)_REPOS); do                           \
	        repo_name=$${repo##*://};                                                   \
	        repo_name=$${repo_name//\//_};                                              \
	        echo -e "[$$repo_name]\n\
name=$${repo_name}\n\
baseurl=$${repo}\n\
enabled=1\n" >> /etc/mock/$(CHROOT_NAME).cfg;                                               \
	    done;                                                                           \
	    echo "\"\"\"" >> /etc/mock/$(CHROOT_NAME).cfg;                                  \
	else                                                                                \
	    echo "Unable to update /etc/mock/$(CHROOT_NAME).cfg.";                          \
            echo "You need to make sure it has the needed repos in it yourself.";           \
	fi
	mock -r $(CHROOT_NAME) $(MOCK_OPTIONS) $(RPM_BUILD_OPTIONS) $<
endif

docker_chrootbuild:
	docker build --build-arg UID=$$(id -u) -t $(BUILD_OS)-chrootbuild \
	             -f packaging/Dockerfile.$(BUILD_OS) .
	docker run --privileged=true -w $$PWD -v=$$PWD:$$PWD              \
	           -it $(BUILD_OS)-chrootbuild bash -c "make chrootbuild"

rpmlint: $(SPEC)
	rpmlint $<

packaging_check:
	if grep -e --repo $(CALLING_MAKEFILE); then                                    \
	    echo "SUSE repos in $(CALLING_MAKEFILE) don't need a \"--repo\" any more"; \
	    exit 2;                                                                    \
	fi
	if ! diff --exclude \*.sw?                              \
	          --exclude debian                              \
	          --exclude .git                                \
	          --exclude Jenkinsfile                         \
	          --exclude libfabric.spec                      \
	          --exclude Makefile                            \
	          --exclude README.md                           \
	          --exclude _topdir                             \
	          --exclude \*.tar.\*                           \
	          --exclude \*.code-workspace                   \
	          --exclude install                             \
	          --exclude packaging                           \
	          -bur $(PACKAGING_CHECK_DIR)/ packaging/; then \
	    exit 1;                                             \
	fi

check-env:
ifndef DEBEMAIL
	$(error DEBEMAIL is undefined)
endif
ifndef DEBFULLNAME
	$(error DEBFULLNAME is undefined)
endif

show_version:
	@echo $(VERSION)

show_release:
	@echo $(RELEASE)

show_rpms:
	@echo $(RPMS)

show_source:
	@echo $(SOURCE)

show_sources:
	@echo $(SOURCES)

show_targets:
	@echo $(TARGETS)

show_makefiles:
	@echo $(MAKEFILE_LIST)

show_calling_makefile:
	@echo $(CALLING_MAKEFILE)

.PHONY: srpm rpms debs ls chrootbuild rpmlint FORCE \
        show_version show_release show_rpms show_source show_sources \
        show_targets check-env show_git_metadata 
