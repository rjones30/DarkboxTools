HOME_DIR := .
EVIO_BUILD := /home/halld/evio/Linux-x86_64

ROOTGLIBS   	 := $(shell root-config --glibs) 
ROOTCFLAGS  	 := $(shell root-config --cflags)

CXX           = g++
CXXFLAGS      = -g -Wall -fPIC -D_GNU_SOURCE -D_REENTRANT -D_POSIX_PTHREAD_SEMANTICS
CXXFLAGS      += $(ROOTCFLAGS)  -I. -I$(EVIO_HOME)/include 

GLIBS	      =	 -L$(EVIO_BUILD)/lib  ${ROOTGLIBS}	

THREADLIBS    =  -lpthread 

GLIBS         += $(THREADLIBS) 

OBJS          = $(CRLFILES:.crl=.so)


all:  treemaker

treemaker:		treemaker.o
	$(CXX)	-o $@ $^ ${GLIBS} -levioxx -levio  -lexpat -lieee -lrt -lz -lm -lnsl -lresolv -ldl

.cc.o:
	source /home/halld/setup.sh && \
	$(CXX) $(CXXFLAGS) -c -o $@ $^

clean:
	rm -f treemaker *.o
