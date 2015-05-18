
# Location of the CUDA Toolkit
#Workstation
#CUDA_PATH       ?= /usr/
#Laptop
CUDA_PATH       ?= /usr/local/cuda-6.5

OSUPPER = $(shell uname -s 2>/dev/null | tr "[:lower:]" "[:upper:]")
OSLOWER = $(shell uname -s 2>/dev/null | tr "[:upper:]" "[:lower:]")

OS_SIZE = $(shell uname -m | sed -e "s/i.86/32/" -e "s/x86_64/64/" -e "s/armv7l/32/")
OS_ARCH = $(shell uname -m | sed -e "s/i386/i686/")

# Common binaries
GCC ?= g++
NVCC := $(CUDA_PATH)/bin/nvcc -ccbin $(GCC)

# internal flags
NVCCFLAGS   := -m${OS_SIZE} 
CCFLAGS     := -g
LDFLAGS     :=

# Extra user flags
EXTRA_NVCCFLAGS   ?=
EXTRA_LDFLAGS     ?=
EXTRA_CCFLAGS     ?=

# Debug build flags
ifeq ($(dbg),1)
      NVCCFLAGS += -g -G
      TARGET := debug
else
      TARGET := release
endif

ALL_CCFLAGS :=
ALL_CCFLAGS += $(NVCCFLAGS)
ALL_CCFLAGS += $(EXTRA_NVCCFLAGS)
ALL_CCFLAGS += $(addprefix -Xcompiler ,$(CCFLAGS))
ALL_CCFLAGS += $(addprefix -Xcompiler ,$(EXTRA_CCFLAGS))

ALL_LDFLAGS :=
ALL_LDFLAGS += $(ALL_CCFLAGS)
ALL_LDFLAGS += $(addprefix -Xlinker ,$(LDFLAGS))
ALL_LDFLAGS += $(addprefix -Xlinker ,$(EXTRA_LDFLAGS))

# Common includes and paths for CUDA
INCLUDES  := -I../../common/inc
LIBRARIES :=

################################################################################

GENCODE_SM20    := -gencode arch=compute_20,code=sm_20
GENCODE_SM30    := -gencode arch=compute_30,code=sm_30
GENCODE_SM32    := -gencode arch=compute_32,code=sm_32
GENCODE_SM35    := -gencode arch=compute_35,code=sm_35
GENCODE_SM50    := -gencode arch=compute_50,code=sm_50
GENCODE_SMXX    := -gencode arch=compute_50,code=compute_50
GENCODE_FLAGS   ?=  $(GENCODE_SM35) $(GENCODE_SM10) $(GENCODE_SM20) $(GENCODE_SM30) $(GENCODE_SM32) $(GENCODE_SM50) $(GENCODE_SMXX)

################################################################################

# Target rules
all: build

build: cppIntegration

cppIntegration.o:cppIntegration.cu
	$(NVCC) $(INCLUDES) $(ALL_CCFLAGS) $(GENCODE_FLAGS) -o $@ -c $<

#cppIntegration_gold.o:cppIntegration_gold.cpp
#	$(NVCC) $(INCLUDES) $(ALL_CCFLAGS) $(GENCODE_FLAGS) -lm -o $@ -c $<

main.o:main.cpp
	$(NVCC) $(INCLUDES) $(ALL_CCFLAGS) $(GENCODE_FLAGS) -o $@ -c $<

cppIntegration: cppIntegration.o main.o
	$(NVCC) $(ALL_LDFLAGS) $(GENCODE_FLAGS) -o $@ $+ $(LIBRARIES)
	mkdir -p ../../bin/$(OS_ARCH)/$(OSLOWER)/$(TARGET)$(if $(abi),/$(abi))
	cp $@ ../../bin/$(OS_ARCH)/$(OSLOWER)/$(TARGET)$(if $(abi),/$(abi))

run: build
	./cppIntegration

clean:
	rm -f cppIntegration cppIntegration.o main.o
	rm -rf ../../bin/$(OS_ARCH)/$(OSLOWER)/$(TARGET)$(if $(abi),/$(abi))/cppIntegration
