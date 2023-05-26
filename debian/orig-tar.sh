#!/bin/sh
set -x
# Called from uscan with parameters:
# --upstream-version <release>
#
# Require git
set -e

UPSTREAM_VERSION="$2"
MANGLED_UPSTREAM_VERSION="$(echo "$UPSTREAM_VERSION" | sed 's/-\(alpha\|pre\)/~\1/')+repack"
UPSTREAM_DOC_VERSION="${UPSTREAM_VERSION%-*}"
if [ "$UPSTREAM_DOC_VERSION" = 1.10.2 ]; then
  UPSTREAM_DOC_VERSION=1.10.1
fi
PACKAGE=hdf5
DOWNLOADED_TARBALL=../${PACKAGE}_${UPSTREAM_VERSION}.orig.tar.gz

SOURCE_DIR="$PACKAGE-$UPSTREAM_VERSION"
DEBIAN_SOURCE_DIR="$PACKAGE-$MANGLED_UPSTREAM_VERSION"
TAR="../${PACKAGE}_$MANGLED_UPSTREAM_VERSION.orig.tar.gz"

# extract the upstream archive
tar xf $DOWNLOADED_TARBALL

# get docs
# No more html docs after release 1.10.2:
# > The latest documentation is on the support portal only, which is freely
# > available. However, it's not easily downloadable.
# > We are no longer updating the User's Guide/Reference Manual in the hdf5doc
# > repo, and there is now only one version of the documentation. See the
# > history at the end of an API to determine when it was introduced.
if dpkg --compare-versions "$UPSTREAM_DOC_VERSION" '<=' 1.10.2; then
  git clone --depth 1 --single-branch --branch hdf5_"$(echo "$UPSTREAM_DOC_VERSION" | sed 's/\./_/g')" https://bitbucket.hdfgroup.org/scm/hdffv/hdf5doc.git
  mv hdf5doc/html $SOURCE_DIR
  rm -fr hdf5doc
  # remove empty directories
  find "$SOURCE_DIR/html" -type d -empty -delete
fi

# rename upstream source dir
# excluding files matched by debian/orig-tar.exclude
tar c -X debian/orig-tar.exclude "$SOURCE_DIR" | tar x --transform "s,^$SOURCE_DIR,$DEBIAN_SOURCE_DIR,"

# repack into orig.tar.gz
tar -c -z -f "$TAR" "$DEBIAN_SOURCE_DIR/"
rm -rf "$SOURCE_DIR" "$DEBIAN_SOURCE_DIR" "$(readlink -f "$DOWNLOADED_TARBALL")" "$DOWNLOADED_TARBALL" ../${PACKAGE}.[1-9]*.git

echo "$PACKAGE: downloaded docs and renamed archive to $(basename "$TAR")"
