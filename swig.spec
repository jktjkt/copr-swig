# We can skip tests
%bcond_without testsuite

%{!?tcl:%global tcl 1}
%{!?guile:%global guile 0}
%{!?lualang:%global lualang 1}
# Disable PHP tests, because they fail with PHP 7.2.0
%{!?phplang:%global phplang 0}
%{!?rubylang:%global rubylang 1}

%ifarch aarch64 %{arm} %{mips} ppc64le ppc %{power64} s390 s390x
%{!?golang:%global golang 0}
%{!?Rlang:%global Rlang 0}
%{!?javalang:%global javalang 0}
%else
%if 0%{?rhel}
%{!?golang:%global golang 0}
%{!?Rlang:%global Rlang 0}
%else
%{!?golang:%global golang 1}
%{!?Rlang:%global Rlang 1}
%endif
%{!?javalang:%global javalang 1}
%endif

%if 0%{?rhel}
%{!?octave:%global octave 0}
%else
%{!?octave:%global octave 1}
%endif

Summary: Connects C/C++/Objective C to some high-level programming languages
Name:    swig
Version: 3.0.12
Release: 14%{?dist}
License: GPLv3+ and BSD
URL:     http://swig.sourceforge.net/
Source0: http://downloads.sourceforge.net/project/swig/swig/swig-%{version}/swig-%{version}.tar.gz
# Define the part of man page sections
Source1: description.h2m
Source2: description-ccache.h2m
Source3: ccache-swig.sh
Source4: ccache-swig.csh

Patch0:  swig308-Do-not-use-isystem.patch
Patch1:  swig-3.0.12-Fix-testsuite-to-work-without-.-in-INC.patch
# Upstream pull request to support Node v7/v8
Patch2:  https://patch-diff.githubusercontent.com/raw/swig/swig/pull/968/swig-node-v7.patch
# Fix generated code for constant expressions containing wchar_t L
# literals.
Patch3:  swig-3.0.12-Fix-generated-code-for-constant-expressions-containi.patch
Patch4:  swig-3.0.12-Fix-type-promotion-wrapping-some-non-trivial-constan.patch
Patch5:  swig-3.0.12-Correct-php-testcase.patch

BuildRequires: perl-interpreter, pcre-devel
BuildRequires: python2-devel, python3-devel
BuildRequires: autoconf, automake, gawk, dos2unix
BuildRequires: gcc-c++
BuildRequires: help2man
BuildRequires: perl-devel
BuildRequires: perl(base)
BuildRequires: perl(Config)
BuildRequires: perl(Devel::Peek)
BuildRequires: perl(ExtUtils::MakeMaker)
BuildRequires: perl(fields)
BuildRequires: perl(Math::BigInt)
BuildRequires: perl(strict)
BuildRequires: perl(Test::More)
BuildRequires: perl(vars)
BuildRequires: perl(warnings)
BuildRequires: boost-devel
# Need when Source/CParse/parser.y is patched
BuildRequires: bison
%if %{tcl}
BuildRequires: tcl-devel
%endif
%if %{guile}
BuildRequires: guile-devel
%endif
%if %{octave}
BuildRequires: octave-devel
%endif
%if %{golang}
BuildRequires: golang
BuildRequires: golang-src
%endif
%if %{lualang}
BuildRequires: lua-devel
%endif
%if %{rubylang}
BuildRequires: ruby-devel
%endif
%if %{Rlang}
BuildRequires: R-devel
%endif
%if %{javalang}
BuildRequires: java, java-devel
%endif
%if %{phplang}
BuildRequires: php, php-devel
%endif

%description
Simplified Wrapper and Interface Generator (SWIG) is a software
development tool for connecting C, C++ and Objective C programs with a
variety of high-level programming languages.  SWIG is primarily used
with Perl, Python and Tcl/TK, but it has also been extended to Java,
Eiffel and Guile. SWIG is normally used to create high-level
interpreted programming environments, systems integration, and as a
tool for building user interfaces

%package -n ccache-swig
Summary:   Fast compiler cache
License:   GPLv2+
Group:     Development/Tools
Requires:  ccache
Requires:  swig
Conflicts: swig < 3.0.8-2

%description -n ccache-swig
ccache-swig is a compiler cache. It speeds up re-compilation of C/C++/SWIG
code by caching previous compiles and detecting when the same compile is
being done again. ccache-swig is ccache plus support for SWIG.

%package doc
Summary:   Documentation files for SWIG
License:   BSD
Group:     Development/Tools
BuildArch: noarch

%description doc
This package contains documentation for SWIG and useful examples

%package gdb
Summary:   Commands for easier debugging of SWIG
License:   BSD
Requires:  swig

%description gdb
This package contains file with commands for easier debugging of SWIG
in gdb.

%prep
%setup -q

%patch0 -p1 -b .isystem
%patch1 -p1
%patch2 -p1 -b .bak
%patch3 -p1
%patch4 -p1
%patch5 -p1

for all in CHANGES README; do
    iconv -f ISO88591 -t UTF8 < $all > $all.new
    touch -r $all $all.new
    mv -f $all.new $all
done

%build
./autogen.sh

# Disable maximum compile warnings when octave is supported, because Octave
# code produces lots of the warnings demanded by strict ISO C and ISO C++.
# It causes that log had more then 600M.
%configure \
  --without-ocaml \
%if %{phplang}
  --with-php=%{__php} \
%endif
%if ! %{javalang}
  --without-java \
%endif
%if ! %{Rlang}
  --without-r \
%endif
%if ! %{golang}
  --without-go \
%endif
%if %{octave}
  --with-octave=/usr/bin/octave \
  --without-maximum-compile-warnings \
%endif
;
make %{?_smp_mflags}

%if %{with testsuite}
# Test suite
make check
%endif

%install
# Remove all arch dependent files in Examples/ created during tests
make clean-examples

pushd Examples/
# Remove all arch dependent files in Examples/
find -type f -name 'Makefile.in' -delete -print

# We don't want to ship files below.
rm -rf test-suite
find -type f -name '*.dsp' -delete -print
find -type f -name '*.dsw' -delete -print

# Convert files to UNIX format
for all in `find -type f`; do
    dos2unix -k $all
    chmod -x $all
done
popd

make DESTDIR=%{buildroot} install

#################################################
# Use help output for generating of man page swig
echo "Options:" >help_swig
%{buildroot}%{_bindir}/swig --help >>help_swig

# Update the output to be correctly formatted be help2man
sed -i -e 's/^\(\s\+-[^-]\+\)- \(.*\)$/\1 \2/' help_swig
sed -i -e 's/^\(\s\+-\w\+-[^-]*\)- \(.*\)$/\1 \2/' help_swig

# Generate a helper script that will be used by help2man
cat >h2m_helper_swig <<'EOF'
#!/bin/bash
[ "$1" == "--version" ] && echo "" || cat help_swig
EOF
chmod a+x h2m_helper_swig

# Generate man page
help2man -N --section 1 ./h2m_helper_swig --include %{SOURCE1} -o %{name}.1

########################################################
# Use help output for generating of man page ccache-swig
%{buildroot}%{_bindir}/ccache-swig -h >>help_ccache

# Update the output to be correctly formatted be help2man
sed -i -e '/compiler cache/ d' help_ccache
sed -i -e '/Copyright/ d' help_ccache
sed -i -e 's/^Usage:/[synopsis]/' help_ccache
sed -i -e 's/^Options:/[options]/' help_ccache
sed -i -e 's/^\s\+/ /' help_ccache
sed -i -e 's/^\(-[^- ] <\w\+>\s\+\) \(\w.\+\)$/ \1 \2/' help_ccache
sed -i -e 's/^\(-[^- ]\s\+\) \(\w.\+\)$/ \1 \2/' help_ccache

# Generate a helper script that will be used by help2man
cat >h2m_helper_ccache <<'EOF'
#!/bin/bash
[ "$1" == "--version" ] && echo ""
[ "$1" == "--help" ] && echo "" || echo ""
EOF
chmod a+x h2m_helper_ccache

cat %{SOURCE2} >>help_ccache
sed -i -e 's#@DOCDIR@#%{_docdir}#' help_ccache

# Generate man page
help2man -N --section 1 ./h2m_helper_ccache --include help_ccache -o ccache-swig.1

# Add man page for swig to repository
mkdir -p %{buildroot}%{_mandir}/man1/
install -p -m 0644 %{name}.1 %{buildroot}%{_mandir}/man1/
install -p -m 0644 ccache-swig.1 %{buildroot}%{_mandir}/man1/

# Quiet some rpmlint complaints - remove empty file
rm -f %{buildroot}%{_datadir}/%name/%{version}/octave/std_carray.i

# Enable ccache-swig by default
mkdir -p %{buildroot}%{_sysconfdir}/profile.d/
install -dm 755 %{buildroot}%{_sysconfdir}/profile.d
install -pm 644 %{SOURCE3} %{SOURCE4} %{buildroot}%{_sysconfdir}/profile.d

# Add swig.gdb sub-package gdb
mkdir -p %{buildroot}%{_datadir}/%{name}/gdb
install -pm 644 Tools/swig.gdb %{buildroot}%{_datadir}/%{name}/gdb

%files
%{_bindir}/%{name}
%{_datadir}/%{name}
%exclude %{_datadir}/%{name}/gdb
%{_mandir}/man1/swig.1*
%license LICENSE LICENSE-GPL LICENSE-UNIVERSITIES
%doc ANNOUNCE CHANGES CHANGES.current
%doc COPYRIGHT README TODO

%files -n ccache-swig
%{_bindir}/ccache-swig
%config(noreplace) %{_sysconfdir}/profile.d/ccache-swig.*sh
%{_mandir}/man1/ccache-swig.1*

%files doc
%license LICENSE LICENSE-GPL LICENSE-UNIVERSITIES
%doc Doc Examples COPYRIGHT

%files gdb
%{_datadir}/%{name}/gdb

%changelog
* Tue Jan 23 2018 Jonathan Wakely <jwakely@redhat.com> - 3.0.12-14
- Rebuilt for Boost 1.66

* Tue Nov 21 2017 Jitka Plesnikova <jplesnik@redhat.com> - 3.0.12-13
- Disable PHP tests, because they fail with PHP 7.2.0-RC

* Wed Sep 20 2017 Jitka Plesnikova <jplesnik@redhat.com> - 3.0.12-12
- Fix generated code for constant expressions containing wchar_t L
  literals

* Thu Sep 07 2017 Jared Smith <jsmith@fedoraproject.org> - 3.0.12-11
- Add patch to support NodeJS versions 7 and 8, fixes FTBFS

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.0.12-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.0.12-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Wed Jun 14 2017 Jitka Plesnikova <jplesnik@redhat.com> - 3.0.12-8
- Fixed tests to building on Perl 5.26 without dot in INC

* Mon May 15 2017 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.0.12-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_27_Mass_Rebuild

* Sat Apr 29 2017 Björn Esser <besser82@fedoraproject.org> - 3.0.12-6
- Rebuilt for bootstrapping new arch: s390x

* Mon Feb 13 2017 Björn Esser <besser82@fedoraproject.org> - 3.0.12-5
- Rebuilt with R-testsuite enabled

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.0.12-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Wed Feb 01 2017 Björn Esser <besser82@fedoraproject.org> - 3.0.12-3
- Rebuilt with Octave-testsuite enabled

* Sun Jan 29 2017 Björn Esser <besser82@fedoraproject.org> - 3.0.12-2
- Rebuilt for Boost 1.63

* Sat Jan 28 2017 Björn Esser <besser82@fedoraproject.org> - 3.0.12-1
- Update to 3.0.12
- Drop Patch1 and Patch2, applied in upstream-tarball
- Build without Octave and R testsuite, since they are broken due to GCC-7

* Sat Jan 14 2017 Björn Esser <besser82@fedoraproject.org> - 3.0.11-2
- Add Patch1 from upstream
  - Do not dump Octave core in examples/test suite scripts
- Add Patch2 for Fedora >= 26, backported from upstream
  - Support for Octave 4.2

* Mon Jan 02 2017 Jitka Plesnikova <jplesnik@redhat.com> - 3.0.11-1
- Update to 3.0.11
  - Add support for PHP 7
  - Disable guile tests

* Wed Oct 19 2016 Jitka Plesnikova <jplesnik@redhat.com> - 3.0.10-2
- Sub-package file swig.gdb (bug #1332673)

* Mon Jun 13 2016 Jitka Plesnikova <jplesnik@redhat.com> - 3.0.10-1
- Update to 3.0.10

* Wed May 25 2016 Jitka Plesnikova <jplesnik@redhat.com> - 3.0.8-8
- Fix Ruby opaque pointer handling (bug #1299502)

* Mon Apr 18 2016 Jitka Plesnikova <jplesnik@redhat.com> - 3.0.8-7
- Add support for Go 1.6

* Fri Mar 11 2016 Michal Toman <mtoman@fedoraproject.org> - 3.0.8-6
- Do not build R, Java and Go on MIPS

* Tue Mar 01 2016 Jitka Plesnikova <jplesnik@redhat.com> - 3.0.8-5
- Used updated upstream fix for GCC 6 issue

* Mon Feb 22 2016 Jitka Plesnikova <jplesnik@redhat.com> - 3.0.8-4
- Patched to build against GCC 6
- Disable Go tests, because they failed against new Go 1.6

* Fri Feb 05 2016 Fedora Release Engineering <releng@fedoraproject.org> - 3.0.8-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Thu Jan 14 2016 Jitka Plesnikova <jplesnik@redhat.com> - 3.0.8-2
- Move ccache-swig to sub-package
- Generate man page for ccache-swig from help

* Mon Jan 04 2016 Jitka Plesnikova <jplesnik@redhat.com> - 3.0.8-1
- Update to 3.0.8

* Sun Dec 06 2015 Björn Esser <fedora@besser82.io> - 3.0.7-10
- fix hunk-offsets in patches

* Sun Dec 06 2015 Björn Esser <fedora@besser82.io> - 3.0.7-9
- add Patch10: Python 3.5, -builtin, excess elements in struct initializer
- add Patch11: Fix incorrect director_classic_runme.py test
- add Patch12: Python SystemError fix with -builtin
- add Patch13: size_type-correction for SwigPySequence_Cont
- add Patch14: Python use Py_ssize_t instead of int for better portability
- add Patch15: Add python inplace-operator caveats to pyopers.swg

* Wed Oct 21 2015 David Sommerseth <davids@redhat.com> - 3.0.7-8
- Ignore locally installed ccache when running CCache unit tests
- Resolves: bz#1274031

* Wed Sep 16 2015 Jitka Plesnikova <jplesnik@redhat.com> - 3.0.7-7
- Remove the old setools patch. The bug was already fixed by upstream
- Resolves: bz#1180257

* Mon Sep 14 2015 Jitka Plesnikova <jplesnik@redhat.com> - 3.0.7-6
- Fix Ruby tracking code (BZ#1225140)

* Thu Sep 03 2015 Jonathan Wakely <jwakely@redhat.com> - 3.0.7-5
- Rebuilt for Boost 1.59

* Tue Sep 01 2015 Jitka Plesnikova <jplesnik@redhat.com> - 3.0.7-4
- Disable Ruby tests

* Thu Aug 27 2015 Jonathan Wakely <jwakely@redhat.com> - 3.0.7-3
- Rebuilt for Boost 1.59

* Wed Aug 05 2015 Jonathan Wakely <jwakely@redhat.com> 3.0.7-2
- Rebuilt for Boost 1.58

* Tue Aug 04 2015 Björn Esser <bjoern.esser@gmail.com> - 3.0.7-1
- Update to 3.0.7 (#1249845)
- Dropped Patch2, changes applied in upstream tarball

* Wed Jul 29 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.0.6-6
- Rebuilt for https://fedoraproject.org/wiki/Changes/F23Boost159

* Thu Jul 23 2015 Jitka Plesnikova <jplesnik@redhat.com> - 3.0.6-5
- rebuild for Boost 1.58

* Thu Jul 23 2015 Jitka Plesnikova <jplesnik@redhat.com> - 3.0.6-4
- Disable Ruby tests on Fedora 23 and higher when building on armv7
- Update list of Perl dependencies

* Wed Jul 22 2015 David Tardon <dtardon@redhat.com> - 3.0.6-3
- rebuild for Boost 1.58

* Fri Jul 10 2015 Orion Poplawski <orion@cora.nwra.com> - 3.0.6-2
- Add patch for octave 4.0.0 support

* Mon Jul 06 2015 Björn Esser <bjoern.esser@gmail.com> - 3.0.6-1
- Update to 3.0.6 (#1240107)
- Dropped Patch2 and Patch3, changes applied in upstream tarball

* Fri Jun 19 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.0.5-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Tue May 26 2015 Dan Horák <dan[at]danny.cz> - 3.0.5-7
- skip ruby also on s390 (#1225140)

* Sat Apr 25 2015 Björn Esser <bjoern.esser@gmail.com> - 3.0.5-6
- Updated Patch3 with a more elaborated approach

* Sat Apr 04 2015 Björn Esser <bjoern.esser@gmail.com> - 3.0.5-5
- Disable Ruby-testsuite on fc23 when building on armv7.  It currently
  segfaults for unknown reason.
- Add a notice about Patch2 got accepted by upstream and can be dropped
  on next version.

* Fri Apr 03 2015 Björn Esser <bjoern.esser@gmail.com> - 3.0.5-4
- Add Patch3 to fix segfaults of Python-wrappers when generating
  code with `-buildin -modern -modernargs`-flags

* Thu Feb 19 2015 Orion Poplawski <orion@cora.nwra.com> - 3.0.5-3
- Rebuild for gcc 5 C++11 ABI

* Tue Feb 10 2015 Björn Esser <bjoern.esser@gmail.com> - 3.0.5-2
- Enable ccache-swig by default, if ccache is installed (#1176861)

* Tue Feb 03 2015 Jitka Plesnikova <jplesnik@redhat.com> - 3.0.5-1
- Update to 3.0.5 (#1178440)

* Tue Jan 27 2015 Petr Machata <pmachata@redhat.com> - 3.0.2-3
- Rebuild for boost 1.57.0

* Mon Aug 18 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.0.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Mon Jun 09 2014 Jitka Plesnikova <jplesnik@redhat.com> - 3.0.2-1
- Update to 3.0.2

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.0.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Thu May 29 2014 Jitka Plesnikova <jplesnik@redhat.com> - 3.0.1-1
- Update to 3.0.1
- Updated parameters for configure and conditions for BRs

* Fri May 23 2014 Petr Machata <pmachata@redhat.com> - 3.0.0-7
- Rebuild for boost 1.55.0

* Thu May 22 2014 Dan Horák <dan[at]danny.cz> 3.0.0-6
- java unit tests fail on s390(x), too. disable for now

* Mon May 12 2014 Peter Robinson <pbrobinson@fedoraproject.org> 3.0.0-5
- unit tests fail on aarch64, too. disable for now

* Fri Apr 25 2014 Peter Robinson <pbrobinson@fedoraproject.org> 3.0.0-4
- No golang or R on aarch64 (currently)

* Tue Apr 22 2014 Karsten Hopp <karsten@redhat.com> 3.0.0-3
- golang is exclusivearch %%{ix86} x86_64 %%{arm}, don't BR it on ppc*, s390*
- unit tests fail on other ppc archs, too. disable for now

* Fri Mar 28 2014 Jitka Plesnikova <jplesnik@redhat.com> - 3.0.0-2
- Small changes to enable ppc64le (BZ#1081724)

* Thu Mar 20 2014 Jitka Plesnikova <jplesnik@redhat.com> - 3.0.0-1
- Update to 3.0.0
- Update BRs to run tests for Java, Ruby, Lua, R, Go
- Replace %%define by %%global (BZ#1063589)
- Remove Group tag (BZ#1063589)
- Generate man page from help to have the correct list of options

* Fri Feb 28 2014 Orion Poplawski <orion@cora.nwra.com> - 2.0.12-1
- Update to 2.0.12
- A patch to fix guile locale

* Wed Oct 09 2013 Jitka Plesnikova <jplesnik@redhat.com> - 2.0.11-2
- Use bconds for enabling testsuite

* Mon Sep 16 2013 Jitka Plesnikova <jplesnik@redhat.com> - 2.0.11-1
- Update to 2.0.11

* Wed Aug 21 2013 Jitka Plesnikova <jplesnik@redhat.com> - 2.0.10-4
- Fixed BZ#994120
  - Remove the req/prov filtering from version docdir (BZ#489421), because
    it is not needed

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.10-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Tue Jul 30 2013 Petr Machata <pmachata@redhat.com> - 2.0.10-2
- Rebuild for boost 1.54.0

* Fri May 31 2013 Jitka Plesnikova <jplesnik@redhat.com> - 2.0.10-1
- Update to 2.0.10
- swig203-rh706140.patch merged
- swig204-rh752054.patch merged
- Create swig-2.0.10-Fix-x390-build.patch

* Fri May 24 2013 Jitka Plesnikova <jplesnik@redhat.com> - 2.0.9-3
- Add man page for swig (BZ#948407)

* Fri Feb 15 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.9-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Mon Jan 07 2013 Adam Tkac <atkac redhat com> 2.0.9-1
- update to 2.0.9

* Wed Sep 12 2012 Adam Tkac <atkac redhat com> 2.0.8-1
- update to 2.0.8 (#851364)
- swig207-rh830660.patch merged
- swig207-r13128.patch merged
- swig-rh841245.patch merged

* Thu Jul 19 2012 Adam Tkac <atkac redhat com> 2.0.7-4
- don't clean "bool" definition in PERL 5 environment (#841245)

* Wed Jun 27 2012 Adam Tkac <atkac redhat com> 2.0.7-3
- fix building of setools package

* Tue Jun 12 2012 Adam Tkac <atkac redhat com> 2.0.7-2
- fix generating of python3 wrappers (#830660)
- don't crash when attepmting to warn about wrong descructor (#830249)

* Thu Jun 07 2012 Adam Tkac <atkac redhat com> 2.0.7-1
- update to 2.0.7
- swig-1.3.23-pylib.patch is no longer needed

* Thu May 10 2012 Adam Tkac <atkac redhat com> 2.0.6-1
- update to 2.0.6

* Mon Apr 23 2012 Adam Tkac <atkac redhat com> 2.0.5-1
- update to 2.0.5
- patches merged
  - swig204-rh753321.patch
  - swig204-rh679948.patch
  - swig204-rh770696.patch

* Thu Apr 19 2012 Adam Tkac <atkac redhat com> - 2.0.4-7
- drop Octave support on RHEL

* Fri Feb 10 2012 Petr Pisar <ppisar@redhat.com> - 2.0.4-6
- Rebuild against PCRE 8.30

* Thu Jan 05 2012 Adam Tkac <atkac redhat com> 2.0.4-5
- fix for PHP 5.4 bindings (#770696)

* Tue Nov 15 2011 Adam Tkac <atkac redhat com> 2.0.4-4
- don't apply patch for #752054 till guile2 gets into distro

* Mon Nov 14 2011 Adam Tkac <atkac redhat com> 2.0.4-3
- backport r12814 from trunk (#753321)
- use scm_to_utf8_string instead of SCM_STRING_CHARS in guile bindings (#752054)
- improve Octave compatibility (#679948)

* Mon Aug 1 2011 Nick Bebout <nb@fedoraproject.org> 2.0.4-2
- rebuild to fix 2.0.3 being tagged in over 2.0.4-1

* Mon Jun 20 2011 Adam Tkac <atkac redhat com> 2.0.4-1
- update to 2.0.4
- patches merged
  - swig200-rh666429.patch
  - swig200-rh623854.patch

* Mon Jun 20 2011 Marcela Mašláňová <mmaslano@redhat.com> 2.0.3-3
- Perl mass rebuild

* Fri May 20 2011 Adam Tkac <atkac redhat com> 2.0.3-2
- make guile generator compatible with guile2 (#706140)

* Fri Apr 22 2011 Adam Tkac <atkac redhat com> 2.0.3-1
- update to 2.0.3
- swig202-rh691513.patch merged

* Tue Mar 29 2011 Adam Tkac <atkac redhat com> 2.0.2-2
- bacport fix for preprocessor regression (#691513)

* Mon Feb 21 2011 Adam Tkac <atkac redhat com> 2.0.2-1
- update to 2.0.2

* Wed Feb 16 2011 Adam Tkac <atkac redhat com> 2.0.1-4
- improve fix for PySlice issue (#666429)

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Jan 03 2011 Adam Tkac <atkac redhat com> 2.0.1-2
- attempt to fix PySlice* API/ABI issues with the Python 3.2 (#666429)

* Thu Oct 07 2010 Adam Tkac <atkac redhat com> 2.0.1-1
- update to 2.0.1 (#640354)
- BR pcre-devel

* Fri Aug 27 2010 Adam Tkac <atkac redhat com> 2.0.0-5
- make PyCObjects->PyCapsule patch C++ compatible (#627310)

* Fri Aug 20 2010 Adam Tkac <atkac redhat com> 2.0.0-4
- improve patch for #623854 (PyCObjects->PyCapsule transition)

* Tue Aug 17 2010 Adam Tkac <atkac redhat com> 2.0.0-3
- python: use new PyCapsule API instead of former PyCObjects API

* Mon Jul 12 2010 Adam Tkac <atkac redhat com> 2.0.0-2
- add LICENSE-GPL, LICENSE-UNIVERSITIES and COPYRIGHT to %%doc
- include all license files in the -doc subpkg

* Thu Jun 24 2010 Adam Tkac <atkac redhat com> 2.0.0-1
- update to 2.0.0
- license changed to GPLv3+ and BSD

* Mon Feb 22 2010 Adam Tkac <atkac redhat com> 1.3.40-5
- s/LGPL/LGPLv2+

* Thu Feb 18 2010 Adam Tkac <atkac redhat com> 1.3.40-4
- correct license field again

* Thu Feb 18 2010 Adam Tkac <atkac redhat com> 1.3.40-3
- correct license field

* Mon Dec 07 2009 Adam Tkac <atkac redhat com> 1.3.40-2
- package review related fixes (#226442)

* Wed Sep 02 2009 Adam Tkac <atkac redhat com> 1.3.40-1
- update to 1.3.40

* Tue Aug 11 2009 Adam Tkac <atkac redhat com> 1.3.39-4
- correct source URL

* Mon Aug 03 2009 Adam Tkac <atkac redhat com> 1.3.39-3
- rebuilt

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.39-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Mar 30 2009 Adam Tkac <atkac redhat com> 1.3.39-1
- update to 1.3.39
- swig-1.3.38-rh485540.patch was merged
- add Example/ to -doc again (#489077), filter provides correctly

* Tue Mar 10 2009 Adam Tkac <atkac redhat com> 1.3.38-5
- revert #489077 enhancement due #489421

* Mon Mar 09 2009 Adam Tkac <atkac redhat com> 1.3.38-4
- moved documentation to -doc subpackage and build it as noarch
- added Example/ directory to -doc (#489077)
- fixed build root

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.38-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Feb 16 2009 Adam Tkac <atkac redhat com> 1.3.38-2
- handle -co option gracefully (#485540)

* Thu Feb 12 2009 Adam Tkac <atkac redhat com> 1.3.38-1
- updated to 1.3.38

* Thu Dec 04 2008 Adam Tkac <atkac redhat com> 1.3.36-2
- #470811 is fixed => dropped workaround

* Mon Nov 10 2008 Adam Tkac <atkac redhat com> 1.3.36-1
- updated to 1.3.36
- finally dropped swig-arch.patch
- temporary workaround rpm bug #470811

* Fri May 16 2008 Adam Tkac <atkac redhat com> 1.3.35-2
- readded swig-arch.patch, will be kept downstream

* Mon May 05 2008 Adam Tkac <atkac redhat com> 1.3.35-1
- updated to latest upstream release

* Mon Feb 18 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 1.3.33-2
- Autorebuild for GCC 4.3

* Thu Nov 29 2007 Adam Tkac <atkac redhat com> 1.3.33-1
- 1.3.33
- removed swig-arch.patch because upstream will never accept
  it ("swig is not low-level")

* Wed Aug 22 2007 Adam Tkac <atkac redhat com> 1.31.1-1
- rebuild (BuildID feature)
- BuildRequires gawk

* Tue Nov 28 2006 Adam Tkac <atkac redhat.com> 1.31.1-0
- updated to 1.2.31 (#216991)

* Tue Nov 07 2006 Adam Tkac <atkac@redhat.com> 1.3.29-2
- swig can determine architecture now (#211095)

* Mon Aug 28 2006 Jitka Kudrnacova <jkudrnac@redhat.com> -1.3.29-1
-rebuilt

* Tue Jul 18 2006 Jitka Kudrnacova <jkudrnac@redhat.com> - 1.3.29-0.3
- rebuilt

* Fri Jun 30 2006 Jitka Kudrnacova <jkudrnac@redhat.com> - 1.3.29-0.2
- Build requires autoconf, automake (bug #197132)

* Wed Apr 19 2006 Jitka Kudrnacova <jkudrnac@redhat.com> - 1.3.29-0.1
- folder /usr/share/swig should be owned by swig package (bug #189145)

* Tue Mar 28 2006 Jitka Kudrnacova <jkudrnac@redhat.com> - 1.3.29-0
- update to swig-1.2.29-0

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 1.3.24-2.2.1
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 1.3.24-2.2
- rebuilt for new gcc4.1 snapshot and glibc changes

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Wed Mar 02 2005 Phil Knirsch <pknirsch@redhat.com> 1.3.24-2
- bump release and rebuild with gcc 4

* Thu Feb 03 2005 Karsten Hopp <karsten@redhat.de> 1.3.24-1
- update

* Wed Dec 01 2004 Phil Knirsch <pknirsch@redhat.com> 1.3.23-2
- rebuild

* Tue Nov 23 2004 Karsten Hopp <karsten@redhat.de> 1.3.23-1
- update
- new pylib patch
- remove destdir patch, swig.m4 is no longer included
- remove ldconfig patch, swig now uses *-config to find out linker options

* Mon Nov  8 2004 Jeremy Katz <katzj@redhat.com> - 1.3.21-7
- rebuild against python 2.4

* Mon Oct 11 2004 Tim Waugh <twaugh@redhat.com> 1.3.21-6
- Build requires tcl-devel (bug #134788).

* Thu Sep 30 2004 Joe Orton <jorton@redhat.com> 1.3.21-5
- don't output -L$libdir in -ldflags

* Wed Sep 22 2004 Florian La Roche <Florian.LaRoche@redhat.de>
- add ldconfig calls to post/postun

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Wed May 19 2004 Joe Orton <jorton@redhat.com> 1.3.21-2
- restore missing runtime libraries

* Tue May 04 2004 Phil Knirsch <pknirsch@redhat.com>
- Update to swig-1.3.21

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Sep 23 2003 Florian La Roche <Florian.LaRoche@redhat.de>
- allow compiling without tcl/guile

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Sun May 18 2003 Joe Orton <jorton@redhat.com> 1.3.19-3
- patch to pick up python libdir correctly

* Sun May 18 2003 Joe Orton <jorton@redhat.com> 1.3.19-2
- add BuildPrereqs to ensure all bindings are built

* Wed May 14 2003 Phil Knirsch <pknirsch@redhat.com> 1.3.19-1
- Update to swig-1.3.19
- Major cleanup in specfile, too. :-)
- New lib64 fix.

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Wed Nov 27 2002 Tim Powers <timp@redhat.com> 1.1p5-21
- lib64'ize

* Fri Aug 30 2002 Phil Knirsch <pknirsch@redhat.com> 1.1p5-20
- Patch by Lon Hohberger for ia64.

* Wed Aug 28 2002 Phil Knirsch <pknirsch@redhat.com> 1.1p5-19
- Added multilib safe patch from arjan (#72523)

* Tue Aug 13 2002 Karsten Hopp <karsten@redhat.de>
- rebuilt with gcc-3.2

* Sat Aug 10 2002 Elliot Lee <sopwith@redhat.com>
- rebuilt with gcc-3.2 (we hope)

* Mon Jul 22 2002 Tim Powers <timp@redhat.com>
- rebuild using gcc-3.2-0.1

* Fri Jun 21 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Thu May 23 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Fri Feb  8 2002 Bill Nottingham <notting@redhat.com>
- rebuild

* Wed Jan 09 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Fri Apr 27 2001 Nalin Dahyabhai <nalin@redhat.com>
- use %%{_tmppath} instead of /var/tmp
- remove the postscript docs (pdftops from the xpdf pkg converts them just fine)

* Wed Sep 13 2000 Tim Powers <timp@redhat.com>
- rebuilt for 7.1

* Mon Jul 24 2000 Prospector <prospector@redhat.com>
- rebuilt

* Mon Jul 17 2000 Tim Powers <timp@redhat.com>
- for some reason defattr wasn't before the docs, fixed

* Mon Jul 10 2000 Tim Powers <timp@redhat.com>
- rebuilt

* Fri Jun 2 2000 Tim Powers <timp@redhat.com>
- spec file cleanups

* Sat May 20 2000 Tim Powers <timp@redhat.com>
- rebuilt for 7.0
- man pages in /usr/share/man

* Wed Jan 19 2000 Tim Powers <timp@redhat.com>
- bzipped sources to conserve space

* Thu Jul 22 1999 Tim Powers <timp@redhat.com>
- rebuilt for 6.1

* Thu Apr 15 1999 Michael Maher <mike@redhat.com>
- built package for 6.0

* Tue Sep 15 1998 Michael Maher <mike@redhat.com>
- built package
