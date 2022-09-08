
ifeq ($(USER),root)
    $(info )
    $(info "$0 can't run by $(USER). exit." )
    $(info )
    $(error exit )
endif
define EOL


endef
define callFUNC
$1 :
    @echo
    $($1)
endef

PWD         := $(shell pwd)
KVERSION    := $(shell uname -r)
KERNEL_DIR  ?= /lib/modules/$(KVERSION)/build


makefile_real:=$(shell realpath Makefile)
makefile_dir:=$(shell dirname $(makefile_real))

uname_p:=$(shell uname -p)

dateX1:=$(shell LC_ALL=C date +%Y_%m%d_%H%M%P_%S )

all: 

ca: clean_all

m:
	vim Makefile ; echo
v:
	vim Makefile.msp430v001 ; echo

vp : vim_prepare
Makefile:=$(shell test -L Makefile && realpath --relative-to=. Makefile || echo Makefile)
vim_prepare :
	rm -f tags \
        cscope.in.out \
        cscope.out \
        cscope.po.out
	mkdir -p _vim/
	echo $(Makefile)                            > _vim/file01.txt
	echo Makefile.env                          >> _vim/file01.txt
	echo $(vim_tags_objS) |sort |xargs -n 1    >> _vim/file01.txt
	sed -i -e '/^\.$$/d' -e '/^$$/d'              _vim/file01.txt
	cscope -q -R -b -i                            _vim/file01.txt
	ctags -L                                      _vim/file01.txt


clean_all:
	rm -f ` \
        find -type f \
        -name "*.o" \
        -o -name "*.d" \
        -o -name "*.d_raw" \
        -o -name "*.obj" \
        -o -name "*.map" \
        -o -name "*~" \
        -o -name "*_linkInfo.xml" \
        -o -name "BlinkLED*.out.elf" \
        -o -name "BlinkLED*.out.strip" \
        -o -name "BlinkLED*.txt" \
        -o -name "BlinkLED*.ss.elf" \
        `

srcList:=q_calc_ntc_resistor
srcC:=$(foreach aa1,$(srcList),$(firstword $(wildcard src0?/$(aa1).c)))
binS:=$(foreach aa1,$(srcList),obj01/$(aa1).bin)


obj01/q_calc_ntc_resistor.bin : src01/q_calc_ntc_resistor.c
	gcc -o $@    $^



all: $(binS)

t test:
	obj01/q_calc_ntc_resistor.bin

v1 :  src01/q_calc_ntc_resistor.c
	vim $^
