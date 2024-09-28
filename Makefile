SIM ?= icarus
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES = $(shell pwd)/DM_Cache.v
TOPLEVEL = DirectMappedCache
COCOTB_TEST_MODULES = test_core

include $(shell cocotb-config --makefiles)/Makefile.sim
