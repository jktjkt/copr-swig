# Makefile for source rpm: swig
# $Id$
NAME := swig
SPECFILE = $(firstword $(wildcard *.spec))

include ../common/Makefile.common
