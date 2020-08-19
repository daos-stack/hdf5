%global macrosdir %(d=%{_rpmconfigdir}/macros.d; [ -d $d ] || d=%{_sysconfdir}/rpm; echo $d)
%{!?_fmoddir:%global _fmoddir %{_libdir}/gfortran/modules}

%global daos_major 0

# Patch version?
%global snaprel %{nil}
# HDF5 versions
%global major 1.12
%global minor 0

# NOTE:  Try not to release new versions to released versions of Fedora
# You need to recompile all users of HDF5 for each version change
Name: hdf5
Version: %{major}.%{minor}
Release: 3%{?dist}
Summary: A general purpose library and file format for storing scientific data
License: BSD
URL: https://portal.hdfgroup.org/display/HDF5/HDF5

Source0: http://www.hdfgroup.org/ftp/HDF5/releases/hdf5-%{major}/hdf5-%{version}%{?snaprel}/src/hdf5-%{version}%{?snaprel}.tar.bz2
Source1: h5comp
# For man pages
Source2: http://ftp.us.debian.org/debian/pool/main/h/hdf5/hdf5_%{version}+repack-1~exp2.debian.tar.xz
Patch0: hdf5-LD_LIBRARY_PATH.patch
# Fix some warnings
Patch2: hdf5-warning.patch
# Fix java build
Patch3: hdf5-build.patch
# Disable tests that don't work with DAOS
Patch11: daos.patch
# Example file move to DESTDIR
Patch12: examples.patch

%if (0%{?suse_version} >= 1500)
BuildRequires:  gcc-fortran
%else
BuildRequires: gcc-gfortran
%endif
BuildRequires: java-devel
BuildRequires: javapackages-tools
BuildRequires: hamcrest
BuildRequires: junit
BuildRequires: slf4j
BuildRequires: krb5-devel
BuildRequires: openssl-devel
BuildRequires: time
BuildRequires: zlib-devel
# For patches/rpath
BuildRequires: automake
BuildRequires: libtool
# Needed for mpi tests
%if (0%{?suse_version} >= 1500)
BuildRequires: openssh
%else
BuildRequires: openssh-clients
%endif
BuildRequires: libaec-devel
BuildRequires: gcc, gcc-c++
%if (0%{?suse_version} >= 1500)
BuildRequires: ed
BuildRequires: Modules
%else
BuildRequires: environment-modules
%endif
Provides:       %{name}-daos-%{daos_major} = %{version}-%{release}

%global with_mpich 1
%global with_openmpi 0
%global with_openmpi3 1
%if 0%{?rhel}
%ifarch ppc64
# No mpich2 on ppc64 in EL
%global with_mpich 0
%endif
%endif
%if 0%{?fedora} < 26
%ifarch s390 s390x
# No openmpi on s390(x)
%global with_openmpi 0
%endif
%endif

%if (0%{?suse_version} >= 1500)
%global module_load() if [ "%{1}" == "openmpi3" ]; then MODULEPATH=/usr/share/modules module load gnu-openmpi; else MODULEPATH=/usr/share/modules module load gnu-%{1}; fi
%else
%global module_load() module load mpi/%{1}-%{_arch}
%endif

%if %{with_mpich}
%global mpi_list mpich
%endif
%if %{with_openmpi}
%global mpi_list %{?mpi_list} openmpi
%endif
%if %{with_openmpi3}
%global mpi_list %{?mpi_list} openmpi3
%endif

%if (0%{?suse_version} >= 1500)
%global mpi_libdir %{_libdir}/mpi/gcc
%global mpi_incldir  %{_includedir}/mpi/gcc
%else
%if (0%{?rhel} >= 7)
%global mpi_libdir %{_libdir}
%global mpi_incldir  %{_includedir}
%else
%{error: only rhel and suse supported}
%endif
%endif

%description
HDF5 is a general purpose library and file format for storing scientific data.
HDF5 can store two primary objects: datasets and groups. A dataset is
essentially a multidimensional array of data elements, and a group is a
structure for organizing objects in an HDF5 file. Using these two basic
objects, one can create and store almost any kind of scientific data
structure, such as images, arrays of vectors, and structured and unstructured
grids. You can also mix and match them in HDF5 files according to your needs.


%package devel
Summary: HDF5 development files
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: libaec-devel%{?_isa}
Requires: zlib-devel%{?_isa}
%if (0%{?suse_version} >= 1500)
Requires: gcc-fortran%{?_isa}
%else
Requires: gcc-gfortran%{?_isa}
%endif

%description devel
HDF5 development headers and libraries.

%package -n java-hdf5
Summary: HDF5 java library
Requires:  slf4j
Obsoletes: jhdf5 < 3.3.1-2
Provides: %{name}-java-hdf5-daos-%{daos_major} = %{version}-%{release}

%description -n java-hdf5
HDF5 java library

%package static
Summary: HDF5 static libraries
Requires: %{name}-devel = %{version}-%{release}

%description static
HDF5 static libraries.


%if %{with_mpich}
%package mpich
Summary: HDF5 mpich libraries
BuildRequires: mpich-devel
Provides: %{name}-mpich2 = %{version}-%{release}
Obsoletes: %{name}-mpich2 < 1.8.11-4
Provides: %{name}-mpich2-daos-%{daos_major} = %{version}-%{release}

%description mpich
HDF5 parallel mpich libraries


%package mpich-devel
Summary: HDF5 mpich development files
Requires: %{name}-mpich%{?_isa} = %{version}-%{release}
Requires: libaec-devel%{?_isa}
Requires: zlib-devel%{?_isa}
Requires: mpich-devel%{?_isa}
Provides: %{name}-mpich2-devel = %{version}-%{release}

%description mpich-devel
HDF5 parallel mpich development files


%package mpich-static
Summary: HDF5 mpich static libraries
Requires: %{name}-mpich-devel%{?_isa} = %{version}-%{release}
Provides: %{name}-mpich2-static = %{version}-%{release}

%description mpich-static
HDF5 parallel mpich static libraries


%package mpich-tests
Summary: HDF5 tests with mpich
Group: Development/Libraries
Requires: %{name}-mpich2 = %{version}-%{release}
Provides: %{name}-mpich2-tests-daos-%{daos_major} = %{version}-%{release}

%description mpich-tests
HDF5 tests with mpich

%endif


%if %{with_openmpi3}
%package openmpi3
Summary: HDF5 openmpi3 libraries
BuildRequires: openmpi3-devel
Provides: %{name}-openmpi3 = %{version}-%{release}
Provides: %{name}-openmpi3-daos-%{daos_major} = %{version}-%{release}

%description openmpi3
HDF5 parallel openmpi3 libraries


%package openmpi3-devel
Summary: HDF5 openmpi3 development files
Requires: %{name}-openmpi3%{?_isa} = %{version}-%{release}
Requires: libaec-devel%{?_isa}
Requires: zlib-devel%{?_isa}
Requires: openmpi3-devel%{?_isa}
Provides: %{name}-openmpi3-devel = %{version}-%{release}

%description openmpi3-devel
HDF5 parallel openmpi3 development files


%package openmpi3-static
Summary: HDF5 openmpi3 static libraries
Requires: %{name}-openmpi3-devel%{?_isa} = %{version}-%{release}
Provides: %{name}-openmpi3-static = %{version}-%{release}

%description openmpi3-static
HDF5 parallel openmpi3 static libraries


%package openmpi3-tests
Summary: HDF5 tests with openmpi3
Group: Development/Libraries
Requires: %{name}-openmpi3 = %{version}-%{release}
Provides: %{name}-openmpi3-tests-daos-%{daos_major} = %{version}-%{release}

%description openmpi3-tests
HDF5 tests with openmpi3

%endif

%prep
%setup -q -a 2 -n %{name}-%{version}%{?snaprel}
%patch0 -p1 -b .LD_LIBRARY_PATH
%patch2 -p1 -b .warning
%patch3 -p1 -b .build
%patch11 -p1 -b .daos
%patch12 -p1 -b .examples
# Leap 15.1 wants jars in /usr/lib64/java
%if (0%{?suse_version} >= 1500)
ed java/src/Makefile.am << EOF
/^hdf5_javadir =/s/lib/lib64/
wq
EOF
%endif

# Replace jars with system versions
find -name \*.jar -delete
ln -s %{_javadir}/hamcrest/core.jar java/lib/hamcrest-core.jar
ln -s %{_javadir}/junit.jar java/lib/junit.jar
ln -s %{_javadir}/slf4j/api.jar java/lib/slf4j-api-1.7.25.jar
ln -s %{_javadir}/slf4j/nop.jar java/lib/ext/slf4j-nop-1.7.25.jar
ln -s %{_javadir}/slf4j/simple.jar java/lib/ext/slf4j-simple-1.7.25.jar
# Fix test output
# junit_ver=$(sed -n '/<version>/{s/^.*>\([0-9]\.[0-9]*\)<.*/\1/;p;q}' /usr/share/maven-poms/JPP-junit.pom)
# sed -i -e "s/JUnit version .*/JUnit version $junit_ver/" java/test/testfiles/JUnit-*.txt

# Force shared by default for compiler wrappers (bug #1266645)
sed -i -e '/^STATIC_AVAILABLE=/s/=.*/=no/' */*/h5[cf]*.in
# building from git source (essentially)
./autogen.sh
autoreconf -f -i

# Modify low optimization level for gnu compilers
sed -e 's|-O -finline-functions|-O3 -finline-functions|g' -i config/gnu-flags


%build
#Do out of tree builds
%global _configure ../configure
#Common configure options
%global configure_opts \\\
  --disable-silent-rules \\\
  --enable-fortran \\\
  --enable-fortran2003 \\\
  --enable-hl \\\
  --enable-shared \\\
  --with-szlib \\\
%{nil}
# --enable-cxx and --enable-parallel flags are incompatible
# --with-mpe=DIR Use MPE instrumentation [default=no]
# --enable-cxx/fortran/parallel and --enable-threadsafe flags are incompatible

#Serial build
export CC=gcc
export CXX=g++
export F9X=gfortran
export LDFLAGS="%{?__global_ldflags} -fPIC -Wl,-z,now -Wl,--as-needed"
mkdir build
pushd build
ln -s ../configure .
%configure \
  %{configure_opts} \
  --enable-cxx \
  --enable-java

sed -i -e 's! -shared ! -Wl,--as-needed\0!g' libtool
make LDFLAGS="%{?__global_ldflags} -fPIC -Wl,-z,now -Wl,--as-needed" %{?_smp_mflags}
popd

#MPI builds
export CC=mpicc
export CXX=mpicxx
export F9X=mpif90
export LDFLAGS="%{?__global_ldflags} -fPIC -Wl,-z,now -Wl,--as-needed"
for mpi in %{?mpi_list}
do
  mkdir $mpi
  pushd $mpi
  %module_load $mpi
  ln -s ../configure .
  %configure \
    %{configure_opts} \
%if (0%{?rhel} >= 7)
    FCFLAGS="$FCFLAGS -I$MPI_FORTRAN_MOD_DIR" \
%endif
    --enable-parallel \
    --enable-map-api \
    --exec-prefix=%{mpi_libdir}/$mpi \
    --libdir=%{mpi_libdir}/$mpi/lib \
    --bindir=%{mpi_libdir}/$mpi/bin \
    --sbindir=%{mpi_libdir}/$mpi/sbin \
    --includedir=%{mpi_incldir}/$mpi-%{_arch} \
    --datarootdir=%{mpi_libdir}/$mpi/share \
    --mandir=%{mpi_libdir}/$mpi/share/man
  sed -i -e 's! -shared ! -Wl,--as-needed\0!g' libtool
  make LDFLAGS="%{?__global_ldflags} -fPIC -Wl,-z,now -Wl,--as-needed" %{?_smp_mflags}
  module purge
  popd
done


%install
%make_install -C build
rm %{buildroot}%{_libdir}/*.la
#Fortran modules
mkdir -p %{buildroot}%{_fmoddir}
mv %{buildroot}%{_includedir}/*.mod %{buildroot}%{_fmoddir}
for mpi in %{?mpi_list}
do
  %module_load $mpi
  make -C $mpi install DESTDIR=%{buildroot}
  rm %{buildroot}/%{mpi_libdir}/$mpi/lib/*.la
  #Fortran modules
%if (0%{?rhel} >= 7)
  mkdir -p %{buildroot}${MPI_FORTRAN_MOD_DIR}
  mv %{buildroot}%{_includedir}/${mpi}-%{_arch}/*.mod %{buildroot}${MPI_FORTRAN_MOD_DIR}/
%endif
  module purge
done

#Fixup headers and scripts for multiarch
%ifarch x86_64 ppc64 ia64 s390x sparc64 alpha
sed -i -e s/H5pubconf.h/H5pubconf-64.h/ %{buildroot}%{_includedir}/H5public.h
mv %{buildroot}%{_includedir}/H5pubconf.h \
   %{buildroot}%{_includedir}/H5pubconf-64.h
for x in h5c++ h5cc h5fc
do
  mv %{buildroot}%{_bindir}/${x} \
     %{buildroot}%{_bindir}/${x}-64
  install -m 0755 %SOURCE1 %{buildroot}%{_bindir}/${x}
done
%else
sed -i -e s/H5pubconf.h/H5pubconf-32.h/ %{buildroot}%{_includedir}/H5public.h
mv %{buildroot}%{_includedir}/H5pubconf.h \
   %{buildroot}%{_includedir}/H5pubconf-32.h
for x in h5c++ h5cc h5fc
do
  mv %{buildroot}%{_bindir}/${x} \
     %{buildroot}%{_bindir}/${x}-32
  install -m 0755 %SOURCE1 %{buildroot}%{_bindir}/${x}
done
%endif
# rpm macro for version checking
mkdir -p %{buildroot}%{macrosdir}
cat > %{buildroot}%{macrosdir}/macros.hdf5 <<EOF
# HDF5 version is
%%_hdf5_version %{version}
EOF

# Install man pages from debian
mkdir -p %{buildroot}%{_mandir}/man1
cp -p debian/man/*.1 %{buildroot}%{_mandir}/man1/
for mpi in %{?mpi_list}
do
  mkdir -p %{buildroot}%{mpi_libdir}/$mpi/share/man/man1
  cp -p debian/man/h5p[cf]c.1 %{buildroot}%{mpi_libdir}/$mpi/share/man/man1/
done
rm %{buildroot}%{_mandir}/man1/h5p[cf]c*.1

# Java
mkdir -p %{buildroot}%{_libdir}/%{name}
mv %{buildroot}%{_libdir}/libhdf5_java.so %{buildroot}%{_libdir}/%{name}/

# Some hackery to install tests
for mpi in %{?mpi_list}
do
  mkdir -p ${RPM_BUILD_ROOT}%{_libdir}/hdf5/$mpi/tests/{,.libs/}
  for x in t_cache testphdf5 t_mpi t_pflush1 t_pflush2 t_shapesame
  do
    install -m 0755 $mpi/testpar/${x} ${RPM_BUILD_ROOT}%{_libdir}/hdf5/$mpi/tests/
    install -m 0755 $mpi/testpar/.libs/${x} ${RPM_BUILD_ROOT}%{_libdir}/hdf5/$mpi/tests/.libs/
  done
done


%check
exit 0
make -C build check
export HDF5_Make_Ignore=yes
export OMPI_MCA_rmaps_base_oversubscribe=1
# t_cache_image appears to be hanging, others taking very long on s390x
%ifnarch s390x
for mpi in %{?mpi_list}
do
  %module_load $mpi
  make -C $mpi check
  module purge
done
%endif


%ldconfig_scriptlets


%files
%license COPYING
%doc MANIFEST README.txt release_docs/RELEASE.txt
%doc release_docs/HISTORY*.txt
%{_bindir}/gif2h5
%{_bindir}/h52gif
%{_bindir}/h5clear
%{_bindir}/h5copy
%{_bindir}/h5debug
%{_bindir}/h5diff
%{_bindir}/h5dump
%{_bindir}/h5format_convert
%{_bindir}/h5import
%{_bindir}/h5jam
%{_bindir}/h5ls
%{_bindir}/h5mkgrp
%{_bindir}/h5perf_serial
%{_bindir}/h5repack
%{_bindir}/h5repart
%{_bindir}/h5stat
%{_bindir}/h5unjam
%{_bindir}/h5watch
%{_libdir}/libhdf5.so.*
%{_libdir}/libhdf5_cpp.so.*
%{_libdir}/libhdf5_fortran.so.*
%{_libdir}/libhdf5hl_fortran.so.*
%{_libdir}/libhdf5_hl.so.*
%{_libdir}/libhdf5_hl_cpp.so.*
%{_mandir}/man1/gif2h5.1*
%{_mandir}/man1/h52gif.1*
%{_mandir}/man1/h5copy.1*
%{_mandir}/man1/h5diff.1*
%{_mandir}/man1/h5dump.1*
%{_mandir}/man1/h5import.1*
%{_mandir}/man1/h5jam.1*
%{_mandir}/man1/h5ls.1*
%{_mandir}/man1/h5mkgrp.1*
%{_mandir}/man1/h5perf_serial.1*
%{_mandir}/man1/h5repack.1*
%{_mandir}/man1/h5repart.1*
%{_mandir}/man1/h5stat.1*
%{_mandir}/man1/h5unjam.1*

%files devel
%{macrosdir}/macros.hdf5
%{_bindir}/h5c++*
%{_bindir}/h5cc*
%{_bindir}/h5fc*
%{_bindir}/h5redeploy
%{_includedir}/*.h
%{_libdir}/*.so
%{_libdir}/*.settings
%{_fmoddir}/*.mod
%{_datadir}/hdf5_examples/
%{_mandir}/man1/h5c++.1*
%{_mandir}/man1/h5cc.1*
%{_mandir}/man1/h5debug.1*
%{_mandir}/man1/h5fc.1*
%{_mandir}/man1/h5redeploy.1*

%files static
%{_libdir}/*.a

%files -n java-hdf5
%{_jnidir}/hdf5.jar
%{_libdir}/%{name}/libhdf5_java.so

%if %{with_mpich}
%files mpich
%license COPYING
%doc MANIFEST README.txt release_docs/RELEASE.txt
%doc release_docs/HISTORY*.txt
%{mpi_libdir}/mpich/bin/gif2h5
%{mpi_libdir}/mpich/bin/h52gif
%{mpi_libdir}/mpich/bin/h5clear
%{mpi_libdir}/mpich/bin/h5copy
%{mpi_libdir}/mpich/bin/h5debug
%{mpi_libdir}/mpich/bin/h5diff
%{mpi_libdir}/mpich/bin/h5dump
%{mpi_libdir}/mpich/bin/h5format_convert
%{mpi_libdir}/mpich/bin/h5import
%{mpi_libdir}/mpich/bin/h5jam
%{mpi_libdir}/mpich/bin/h5ls
%{mpi_libdir}/mpich/bin/h5mkgrp
%{mpi_libdir}/mpich/bin/h5redeploy
%{mpi_libdir}/mpich/bin/h5repack
%{mpi_libdir}/mpich/bin/h5perf
%{mpi_libdir}/mpich/bin/h5perf_serial
%{mpi_libdir}/mpich/bin/h5repart
%{mpi_libdir}/mpich/bin/h5stat
%{mpi_libdir}/mpich/bin/h5unjam
%{mpi_libdir}/mpich/bin/h5watch
%{mpi_libdir}/mpich/bin/ph5diff
%{mpi_libdir}/mpich/lib/*.so.*

%files mpich-devel
%{mpi_incldir}/mpich-%{_arch}
%if (0%{?rhel} >= 7)
%{_fmoddir}/mpich/*.mod
%endif
%{mpi_libdir}/mpich/bin/h5pcc
%{mpi_libdir}/mpich/bin/h5pfc
%{mpi_libdir}/mpich/lib/lib*.so
%{mpi_libdir}/mpich/lib/lib*.settings
%{mpi_libdir}/mpich/share/hdf5_examples/
%{mpi_libdir}/mpich/share/man/man1/h5pcc.1*
%{mpi_libdir}/mpich/share/man/man1/h5pfc.1*

%files mpich-static
%{mpi_libdir}/mpich/lib/*.a

%files mpich-tests
%{_libdir}/hdf5/mpich/tests

%endif


%if %{with_openmpi3}
%files openmpi3
%license COPYING
%doc MANIFEST README.txt release_docs/RELEASE.txt
%doc release_docs/HISTORY*.txt
%{mpi_libdir}/openmpi3/bin/gif2h5
%{mpi_libdir}/openmpi3/bin/h52gif
%{mpi_libdir}/openmpi3/bin/h5clear
%{mpi_libdir}/openmpi3/bin/h5copy
%{mpi_libdir}/openmpi3/bin/h5debug
%{mpi_libdir}/openmpi3/bin/h5diff
%{mpi_libdir}/openmpi3/bin/h5dump
%{mpi_libdir}/openmpi3/bin/h5format_convert
%{mpi_libdir}/openmpi3/bin/h5import
%{mpi_libdir}/openmpi3/bin/h5jam
%{mpi_libdir}/openmpi3/bin/h5ls
%{mpi_libdir}/openmpi3/bin/h5mkgrp
%{mpi_libdir}/openmpi3/bin/h5perf
%{mpi_libdir}/openmpi3/bin/h5perf_serial
%{mpi_libdir}/openmpi3/bin/h5redeploy
%{mpi_libdir}/openmpi3/bin/h5repack
%{mpi_libdir}/openmpi3/bin/h5repart
%{mpi_libdir}/openmpi3/bin/h5stat
%{mpi_libdir}/openmpi3/bin/h5unjam
%{mpi_libdir}/openmpi3/bin/h5watch
%{mpi_libdir}/openmpi3/bin/ph5diff
%{mpi_libdir}/openmpi3/lib/*.so.*

%files openmpi3-devel
%{mpi_incldir}/openmpi3-%{_arch}
%if (0%{?rhel} >= 7)
%{_fmoddir}/openmpi3/*.mod
%endif
%{mpi_libdir}/openmpi3/bin/h5pcc
%{mpi_libdir}/openmpi3/bin/h5pfc
%{mpi_libdir}/openmpi3/lib/lib*.so
%{mpi_libdir}/openmpi3/lib/lib*.settings
%{mpi_libdir}/openmpi3/share/hdf5_examples/
%{mpi_libdir}/openmpi3/share/man/man1/h5pcc.1*
%{mpi_libdir}/openmpi3/share/man/man1/h5pfc.1*

%files openmpi3-static
%{mpi_libdir}/openmpi3/lib/*.a

%files openmpi3-tests
%{_libdir}/hdf5/openmpi3/tests

%endif

%changelog
* Fri Aug 14 2020 Maureen Jean <maureen.jean@intel.com> - 1.12.0-3
- Enable build with SLES15.2

* Tue Jul 28 2020 Maureen Jean <maureen.jean@intel.com> - 1.12.0-2
- Add enable-map-api for daos-vol build support

* Tue Jul 28 2020 Maureen Jean <maureen.jean@intel.com> - 1.12.0-1
- Update HDF5 to version 1.12.0

* Mon Jul 27 2020 Brian J. Murrell <brian.murrell@intel.com> - 1.10.5-10.g07066a381e
- Skip nocolcause test
- Add version and release to virtual provides
- Drop cart from virtual provides

* Mon Jul 13 2020 Maureen Jean <maureen.jean@intel.com> - 1.10.5-9.g07066a381e
- Add support for openmpi3

* Fri Jun 19 2020 Phil Henderson <phillip.henderson@intel.com> - 1.10.5-8.g07066a381e
- Fix Leap 15 build of %{name}-devel

* Wed Jan 22 2020 Brian J. Murrell <brian.murrell@intel.com> - 1.10.5-7.g07066a381e
- Port to Leap 15.1

* Sun Dec 29 2019 Brian J. Murrell <brian.murrell@intel.com> - 1.10.5-6.g07066a381e
- Add Provides: %{name}-cart-%{cart_major}-daos-%{daos_major}

* Thu Nov 14 2019 Brian J. Murrell <brian.murrell@intel.com> - 1.10.5-5.g07066a381e
- Add patch to catch up to 11.4-g07066a381e
- Add daos patch
- Don't build openmpi* subpackages
- Add tests subpackage and package mpich tests in them
- tests subpackage Requires mpich2 subpackage

* Mon Nov 11 2019 Orion Poplawski <orion@nwra.com> - 1.10.5-4
- Add upstream patch to fix 32-bit java tests

* Thu Jul 25 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.10.5-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Sat Apr  6 2019 Orion Poplawski <orion@nwra.com> - 1.10.5-2
- Enable java

* Sat Mar 16 2019 Orion Poplawski <orion@nwra.com> - 1.10.5-1
- Update to 1.10.5

* Thu Feb 14 2019 Orion Poplawski <orion@nwra.com> - 1.8.20-6
- Rebuild for openmpi 3.1.3

* Fri Feb 01 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.8.20-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.8.20-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Fri Feb 23 2018 Antonio Trande <sagitter@fedoraproject.com> - 1.8.20-3
- Force default ldflags for Fedora (bz#1548533)
- Switch -shared flag to -Wl,--as-needed
- Modify low optimization level for gnu compilers
- New URL

* Tue Feb 20 2018 Antonio Trande <sagitter@fedoraproject.com> - 1.8.20-2
- Devel package with full versioned dependency
- Use %%make_install

* Wed Feb 7 2018 Orion Poplawski <orion@nwra.com> - 1.8.20-1
- Update to 1.8.20

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.8.18-14
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Fri Feb 02 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 1.8.18-13
- Switch to %%ldconfig_scriptlets

* Wed Jan 31 2018 Orion Poplawski <orion@cora.nwra.com> - 1.8.18-12
- Rebuild for gfortran-8

* Fri Sep 08 2017 Dan Horák <dan[at]danny.cz> - 1.8.18-11
- fix the compiler wrapper - s390x is 64-bit (#1489954)

* Wed Aug 16 2017 Orion Poplawski <orion@cora.nwra.com> - 1.8.18-10
- Bump for rebuild

* Wed Aug 16 2017 Orion Poplawski <orion@nwra.com> - 1.8.18-9
- Make hdf5-devel require libaec

* Sun Aug 06 2017 Christoph Junghans <junghans@votca.org> - 1.8.18-8
- enable szip support through libaec

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.8.18-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.8.18-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Sun Feb 05 2017 Kalev Lember <klember@redhat.com> - 1.8.18-5
- Enable testsuite again now that gcc fixes have landed

* Wed Feb 01 2017 Björn Esser <me@besser82.io> - 1.8.18-4
- Ignore testsuite on PPC64LE until GCC-7 is fixed

* Sat Jan 28 2017 Björn Esser <besser82@fedoraproject.org> - 1.8.18-4
- Rebuilt for GCC-7

* Fri Dec 30 2016 Orion Poplawski <orion@cora.nwra.com> - 1.8.18-3
- Install MPI Fortran module into proper location (bug #1409229)
- Use %%license

* Thu Dec 8 2016 Dan Horák <dan[at]danny.cz> - 1.8.18-2
- Enable openmpi for s390(x) on F>=26

* Mon Dec 5 2016 Orion Poplawski <orion@cora.nwra.com> - 1.8.18-1
- Update to 1.8.18
- Add patch to fix build with -Werror=implicit-function-declaration

* Fri Oct 21 2016 Orion Poplawski <orion@cora.nwra.com> - 1.8.17-2
- Rebuild for openmpi 2.0

* Wed Jun 29 2016 Orion Poplawski <orion@cora.nwra.com> - 1.8.17-1
- Update to 1.8.17

* Sun Mar 20 2016 Orion Poplawski <orion@cora.nwra.com> - 1.8.16-4
- Add patch to properly call MPI_Finalize() in t_pflush1

* Wed Mar 2 2016 Orion Poplawski <orion@cora.nwra.com> - 1.8.16-3
- Make hdf5-mpich-devel require mpich-devel (bug #1314091)

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.8.16-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Fri Nov 20 2015 Orion Poplawski <orion@cora.nwra.com> - 1.8.16-1
- Update to 1.8.16

* Fri Nov 20 2015 Orion Poplawski <orion@cora.nwra.com> - 1.8.15-9.patch1
- Use MPI_FORTRAN_MOD_DIR to locate MPI Fortran module

* Fri Sep 25 2015 Orion Poplawski <orion@cora.nwra.com> - 1.8.15-8.patch1
- Force shared by default for compiler wrappers (bug #1266645)

* Tue Sep 15 2015 Orion Poplawski <orion@cora.nwra.com> - 1.8.15-7.patch1
- Rebuild for openmpi 1.10.0

* Sat Aug 15 2015 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 1.8.15-6.patch1
- Rebuild for MPI provides

* Sun Jul 26 2015 Sandro Mani <manisandro@gmail.com> - 1.8.15-5.patch1
- Rebuild for RPM MPI Requires Provides Change

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.8.15-4.patch1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon Jun 8 2015 Orion Poplawski <orion@cora.nwra.com> - 1.8.15-3.patch1
- Update to 1.8.15-patch1

* Fri Jun 05 2015 Dan Horák <dan[at]danny.cz> - 1.8.15-2
- drop unnecessary patch, issue seems fixed with gcc5

* Sat May 16 2015 Orion Poplawski <orion@cora.nwra.com> - 1.8.15-1
- Update to 1.8.15

* Sat May 02 2015 Kalev Lember <kalevlember@gmail.com> - 1.8.14-4
- Rebuilt for GCC 5 C++11 ABI change

* Wed Mar 11 2015 Orion Poplawski <orion@cora.nwra.com> - 1.8.14-3
- Rebuild for mpich 3.1.4 soname change

* Mon Feb 16 2015 Orion Poplawski <orion@cora.nwra.com> - 1.8.14-2
- Rebuild for gcc 5 fortran module

* Tue Jan 6 2015 Orion Poplawski <orion@cora.nwra.com> - 1.8.14-1
- Update to 1.8.14

* Wed Sep 3 2014 Orion Poplawski <orion@cora.nwra.com> - 1.8.13-7
- No longer build with -O0, seems to be working

* Wed Aug 27 2014 Orion Poplawski <orion@cora.nwra.com> - 1.8.13-6
- Rebuild for openmpi Fortran ABI change

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.8.13-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Fri Jun 27 2014 Orion Poplawski <orion@cora.nwra.com> - 1.8.13-4
- Make build work if not building any mpi pacakges (bug #1113610)

* Fri Jun 27 2014 Marcin Juszkiewicz <mjuszkiewicz@redhat.com> - 1.8.13-3
- Drop gnu-config patches replaced by %%configure macro

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.8.13-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Thu May 15 2014 Orion Poplawski <orion@cora.nwra.com> - 1.8.13-1
- Update to 1.8.13

* Mon Mar 24 2014 Orion Poplawski <orion@cora.nwra.com> - 1.8.12-6
- Add patch to add ppc64le to config.guess (bug #1080122)

* Wed Mar 19 2014 Orion Poplawski <orion@cora.nwra.com> - 1.8.12-5
- Add patch to fix long double conversions on ppc64le (bug #1078173)
- Run autoreconf for patches and to remove rpaths

* Sat Feb 22 2014 Deji Akingunola <dakingun@gmail.com> - 1.8.12-4
- Rebuild for mpich-3.1

* Fri Jan 31 2014 Orion Poplawski <orion@cora.nwra.com> 1.8.12-4
- Fix rpm macros install dir

* Wed Jan 29 2014 Orion Poplawski <orion@cora.nwra.com> 1.8.12-3
- Fix rpm/macros.hdf5 generation (bug #1059161)

* Wed Jan 8 2014 Orion Poplawski <orion@cora.nwra.com> 1.8.12-2
- Update debian source
- Add patch for aarch64 support (bug #925545)

* Fri Dec 27 2013 Orion Poplawski <orion@cora.nwra.com> 1.8.12-1
- Update to 1.8.12

* Fri Aug 30 2013 Dan Horák <dan[at]danny.cz> - 1.8.11-6
- disable parallel tests on s390(x)

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.8.11-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Sat Jul 20 2013 Deji Akingunola <dakingun@gmail.com> - 1.8.11-4
- Rename mpich2 sub-packages to mpich and rebuild for mpich-3.0

* Thu Jul 11 2013 Orion Poplawski <orion@cora.nwra.com> 1.8.11-3
- Rebuild for openmpi 1.7.2

* Fri Jun 7 2013 Orion Poplawski <orion@cora.nwra.com> 1.8.11-2
- Add man pages from debian (bug #971551)

* Wed May 15 2013 Orion Poplawski <orion@cora.nwra.com> 1.8.11-1
- Update to 1.8.11

* Mon Mar 11 2013 Ralf Corsépius <corsepiu@fedoraproject.org> - 1.8.10-3
- Remove %%config from %%{_sysconfdir}/rpm/macros.*
  (https://fedorahosted.org/fpc/ticket/259).

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.8.10-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Nov 14 2012 Orion Poplawski <orion@cora.nwra.com> 1.8.10-1
- Update to 1.8.10
- Rebase LD_LIBRARY_PATH patch
- Drop ph5diff patch fixed upstream

* Mon Nov 12 2012 Peter Robinson <pbrobinson@fedoraproject.org> 1.8.9-5
- Enable openmpi support on ARM as we now have it

* Mon Nov 5 2012 Orion Poplawski <orion@cora.nwra.com> 1.8.9-4
- Rebuild for fixed openmpi f90 soname

* Thu Nov 1 2012 Orion Poplawski <orion@cora.nwra.com> 1.8.9-3
- Rebuild for openmpi and mpich2 soname bumps

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.8.9-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue May 15 2012 Orion Poplawski <orion@cora.nwra.com> 1.8.9-1
- Update to 1.8.9

* Mon Feb 20 2012 Dan Horák <dan[at]danny.cz> 1.8.8-9
- use %%{mpi_list} also for tests

* Wed Feb 15 2012 Peter Robinson <pbrobinson@fedoraproject.org> - 1.8.8-8
- disable openmpi for ARM as we currently don't have it

* Fri Feb 10 2012 Orion Poplawski <orion@cora.nwra.com> 1.8.8-7
- Add patch to fix parallel mpi tests
- Add patch to fix bug in parallel h5diff

* Sat Jan 7 2012 Orion Poplawski <orion@cora.nwra.com> 1.8.8-6
- Enable Fortran 2003 support (bug 772387)

* Wed Dec 21 2011 Dan Horák <dan[at]danny.cz> 1.8.8-5
- reintroduce the tstlite patch for ppc64 and s390x

* Thu Dec 01 2011 Caolán McNamara <caolanm@redhat.com> 1.8.8-4
- Related: rhbz#758334 hdf5 doesn't build on ppc64

* Fri Nov 25 2011 Orion Poplawski <orion@cora.nwra.com> 1.8.8-3
- Enable static MPI builds

* Wed Nov 16 2011 Orion Poplawski <orion@cora.nwra.com> 1.8.8-2
- Add rpm macro %%{_hdf5_version} for convenience

* Tue Nov 15 2011 Orion Poplawski <orion@cora.nwra.com> 1.8.8-1
- Update to 1.8.8
- Drop tstlite patch
- Add patch to avoid setting LD_LIBRARY_PATH

* Wed Jun 01 2011 Karsten Hopp <karsten@redhat.com> 1.8.7-2
- drop ppc64 longdouble patch, not required anymore

* Tue May 17 2011 Orion Poplawski <orion@cora.nwra.com> 1.8.7-1
- Update to 1.8.7

* Tue Mar 29 2011 Deji Akingunola <dakingun@gmail.com> - 1.8.6-2
- Rebuild for mpich2 soname bump

* Fri Feb 18 2011 Orion Poplawski <orion@cora.nwra.com> 1.8.6-1
- Update to 1.8.6-1
- Update tstlite patch - not fixed yet

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.8.5.patch1-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Sun Feb 6 2011 Orion Poplawski <orion@cora.nwra.com> 1.8.5.patch1-7
- Add Requires: zlib-devel to hdf5-devel

* Sun Dec 12 2010 Dan Horák <dan[at]danny.cz> 1.8.5.patch1-6
- fully conditionalize MPI support

* Wed Dec 8 2010 Orion Poplawski <orion@cora.nwra.com> 1.8.5.patch1-5
- Add EL6 compatibility - no mpich2 on ppc64

* Wed Oct 27 2010 Orion Poplawski <orion@cora.nwra.com> 1.8.5.patch1-4
- Really fixup all permissions

* Wed Oct 27 2010 Orion Poplawski <orion@cora.nwra.com> 1.8.5.patch1-3
- Add docs to the mpi packages
- Fixup example source file permissions

* Tue Oct 26 2010 Orion Poplawski <orion@cora.nwra.com> 1.8.5.patch1-2
- Build parallel hdf5 packages for mpich2 and openmpi
- Rework multiarch support and drop multiarch patch

* Tue Sep 7 2010 Orion Poplawski <orion@cora.nwra.com> 1.8.5.patch1-1
- Update to 1.8.5-patch1

* Wed Jun 23 2010 Orion Poplawski <orion@cora.nwra.com> 1.8.5-4
- Re-add rebased tstlite patch - not fixed yet

* Wed Jun 23 2010 Orion Poplawski <orion@cora.nwra.com> 1.8.5-3
- Update longdouble patch for 1.8.5

* Wed Jun 23 2010 Orion Poplawski <orion@cora.nwra.com> 1.8.5-2
- Re-add longdouble patch on ppc64 for EPEL builds

* Mon Jun 21 2010 Orion Poplawski <orion@cora.nwra.com> 1.8.5-1
- Update to 1.8.5
- Drop patches fixed upstream

* Mon Mar 1 2010 Orion Poplawski <orion@cora.nwra.com> 1.8.4.patch1-1
- Update to 1.8.4-patch1

* Wed Jan 6 2010 Orion Poplawski <orion@cora.nwra.com> 1.8.4-1
- Update to 1.8.4
- Must compile with -O0 due to gcc-4.4 incompatability
- No longer need -fno-strict-aliasing

* Thu Oct 1 2009 Orion Poplawski <orion@cora.nwra.com> 1.8.3-3.snap12
- Update to 1.8.3-snap12
- Update signal patch
- Drop detect and filter-as-option patch fixed upstream
- Drop ppc only patch
- Add patch to skip tstlite test for now, problem reported upstream
- Fixup some source file permissions

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.8.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Jun 2 2009 Orion Poplawski <orion@cora.nwra.com> 1.8.3-1
- Update to 1.8.3
- Update signal and detect patches
- Drop open patch fixed upstream

* Sat Apr 18 2009 Karsten Hopp <karsten@redhat.com> 1.8.2-1.1
- fix s390x builds, s390x is 64bit, s390 is 32bit

* Mon Feb 23 2009 Orion Poplawski <orion@cora.nwra.com> 1.8.2-1
- Update to 1.8.2
- Add patch to compile H5detect without optimization - make detection
  of datatype characteristics more robust - esp. long double
- Update signal patch
- Drop destdir patch fixed upstream
- Drop scaleoffset patch
- Re-add -fno-strict-aliasing
- Keep settings file needed for -showconfig (bug #481032)
- Wrapper script needs to pass arguments (bug #481032)

* Wed Oct 8 2008 Orion Poplawski <orion@cora.nwra.com> 1.8.1-3
- Add sparc64 to 64-bit conditionals

* Fri Sep 26 2008 Orion Poplawski <orion@cora.nwra.com> 1.8.1-2
- Add patch to filter -little as option used on sh arch (#464052)

* Thu Jun 5 2008 Orion Poplawski <orion@cora.nwra.com> 1.8.1-1
- Update to 1.8.1

* Tue May 27 2008 Orion Poplawski <orion@cora.nwra.com> 1.8.1-0.rc1.1
- Update to 1.8.1-rc1

* Tue May 13 2008 Orion Poplawski <orion@cora.nwra.com> 1.8.0.snap5-2
- Use new %%{_fmoddir} macro
- Re-enable ppc64, disable failing tests.  Failing tests are for
  experimental long double support.

* Mon May 5 2008 Orion Poplawski <orion@cora.nwra.com> 1.8.0.snap5-1
- Update to 1.8.0-snap5
- Remove --enable-threadsafe, incompatible with --enable-cxx and
  --enable-fortran
- ExcludeArch ppc64 until we can get it to build (bug #445423)

* Tue Mar 4 2008 Orion Poplawski <orion@cora.nwra.com> 1.8.0-2
- Remove failing test for now

* Fri Feb 29 2008 Orion Poplawski <orion@cora.nwra.com> 1.8.0-1
- Update to 1.8.0, drop upstreamed patches
- Update signal patch
- Move static libraries into -static sub-package
- Make -devel multiarch (bug #341501)

* Wed Feb  6 2008 Orion Poplawski <orion@cora.nwra.com> 1.6.6-7
- Add patch to fix strict-aliasing
- Disable production mode to enable debuginfo

* Tue Feb  5 2008 Orion Poplawski <orion@cora.nwra.com> 1.6.6-6
- Add patch to fix calling free() in H5PropList.cpp

* Tue Feb  5 2008 Orion Poplawski <orion@cora.nwra.com> 1.6.6-5
- Add patch to support s390 (bug #431510)

* Mon Jan  7 2008 Orion Poplawski <orion@cora.nwra.com> 1.6.6-4
- Add patches to support sparc (bug #427651)

* Tue Dec  4 2007 Orion Poplawski <orion@cora.nwra.com> 1.6.6-3
- Rebuild against new openssl

* Fri Nov 23 2007 Orion Poplawski <orion@cora.nwra.com> 1.6.6-2
- Add patch to build on alpha (bug #396391)

* Wed Oct 17 2007 Orion Poplawski <orion@cora.nwra.com> 1.6.6-1
- Update to 1.6.6, drop upstreamed patches
- Explicitly set compilers

* Fri Aug 24 2007 Orion Poplawski <orion@cora.nwra.com> 1.6.5-9
- Update license tag to BSD
- Rebuild for BuildID

* Wed Aug  8 2007 Orion Poplawski <orion@cora.nwra.com> 1.6.5-8
- Fix memset typo
- Pass mode to open with O_CREAT

* Mon Feb 12 2007 Orion Poplawski <orion@cora.nwra.com> 1.6.5-7
- New project URL
- Add patch to use POSIX sort key option
- Remove useless and multilib conflicting Makefiles from html docs
  (bug #228365)
- Make hdf5-devel own %%{_docdir}/%%{name}

* Tue Aug 29 2006 Orion Poplawski <orion@cora.nwra.com> 1.6.5-6
- Rebuild for FC6

* Wed Mar 15 2006 Orion Poplawski <orion@cora.nwra.com> 1.6.5-5
- Change rpath patch to not need autoconf
- Add patch for libtool on x86_64
- Fix shared lib permissions

* Mon Mar 13 2006 Orion Poplawski <orion@cora.nwra.com> 1.6.5-4
- Add patch to avoid HDF setting the compiler flags

* Mon Feb 13 2006 Orion Poplawski <orion@cora.nwra.com> 1.6.5-3
- Rebuild for gcc/glibc changes

* Wed Dec 21 2005 Orion Poplawski <orion@cora.nwra.com> 1.6.5-2
- Don't ship h5perf with missing library

* Wed Dec 21 2005 Orion Poplawski <orion@cora.nwra.com> 1.6.5-1
- Update to 1.6.5

* Wed Dec 21 2005 Orion Poplawski <orion@cora.nwra.com> 1.6.4-9
- Rebuild

* Wed Nov 30 2005 Orion Poplawski <orion@cora.nwra.com> 1.6.4-8
- Package fortran files properly
- Move compiler wrappers to devel

* Fri Nov 18 2005 Orion Poplawski <orion@cora.nwra.com> 1.6.4-7
- Add patch for fortran compilation on ppc

* Wed Nov 16 2005 Orion Poplawski <orion@cora.nwra.com> 1.6.4-6
- Bump for new openssl

* Tue Sep 20 2005 Orion Poplawski <orion@cora.nwra.com> 1.6.4-5
- Enable fortran since the gcc bug is now fixed

* Tue Jul 05 2005 Orion Poplawski <orion@cora.nwra.com> 1.6.4-4
- Make example scripts executable

* Wed Jun 29 2005 Orion Poplawski <orion@cora.nwra.com> 1.6.4-3
- Add --enable-threads --with-pthreads to configure
- Add %%check
- Add some %%docs
- Use %%makeinstall
- Add patch to fix test for h5repack
- Add patch to fix h5diff_attr.c

* Mon Jun 27 2005 Tom "spot" Callaway <tcallawa@redhat.com> 1.6.4-2
- remove szip from spec, since szip license doesn't meet Fedora standards

* Sun Apr 3 2005 Tom "spot" Callaway <tcallawa@redhat.com> 1.6.4-1
- inital package for Fedora Extras
