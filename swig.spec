Summary: Connects C/C++/Objective C to some high-level programming languages.
Name: swig
Version: 1.1p5
Release: 12
Copyright: BSD
Group: Development/Tools
URL: http://swig.sourceforge.net/
Source: http://download.sourceforge.net/swig/swig1.1p5.tar.gz
Source1: ftp://ftp.cs.utah.edu/pub/beazley/SWIG/swigdoc_html.tar.bz2
BuildRoot: %{_tmppath}/swig-root

%description
Simplified Wrapper and Interface Generator (SWIG) is a software
development tool for connecting C, C++ and Objective C programs with a
variety of high-level programming languages.  SWIG is primarily used
with Perl, Python and Tcl/TK, but it has also been extended to Java,
Eiffel and Guile.  SWIG is normally used to create high-level
interpreted programming environments, systems integration, and as a
tool for building user interfaces.

%prep
%setup -q -n SWIG1.1p5 -a1

%build
%configure
make
make runtime

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT{%{_bindir},%{_libdir},%{_mandir},%{_includedir}}
%makeinstall MAN_DIR=$RPM_BUILD_ROOT%{_mandir}/man1 

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%doc SWIGDoc1.1/* 
%doc CHANGES Copyright INSTALL NEW README TROUBLESHOOTING ToDo 
%doc Doc/*
%{_bindir}/*
%{_includedir}/*
%{_mandir}/*/*
%{_libdir}/*.a
%{_libdir}/*.so
%{_libdir}/swig_lib

%changelog
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
