##
## Copyright:	(c) 1997-2008 Lawrence Livermore National Security, LLC
## Revision:	$LastChangedRevision: 2219 $
## Modified:	$LastChangedDate: 2008-06-12 13:14:48 -0700 (Thu, 12 Jun 2008) $
##

include $(PARFLOW_DIR)/config/Makefile.config

PARFLOW=$(PARFLOW_DIR)/bin/parflow

default: scaling

scaling:
	@for i in `seq 3`; do                                  \
	   echo $${s};                                         \
	   for s in `seq 8` ; do	                       \
	       name=scaling.$${s}.$${i};                       \
	       echo "Running $${name}";	                       \
	       /usr/bin/time --format "CSV,Total Time,$${s},$${i},%e" tclsh scaling.tcl $${s} $${name}; \
	   done;                                               \
	done

small:
	@tclsh small_domain.tcl
	@mv gmon.out gmon.sum
	@for i in `seq 9` ; do	                              \
	    echo $${i};                                       \
	    parflow small_domain;                             \
	    gprof -s $(PARFLOW) gmon.out gmon.sum;            \
	done
	@gprof $(PARFLOW) gmon.sum > small_domain.gprof.txt

big:
	@tclsh big_domain.tcl
	@mv gmon.out gmon.sum
	@for i in `seq 9` ; do	                              \
	    echo $${i};                                       \
	    parflow big_domain;                             \
	    gprof -s $(PARFLOW) gmon.out gmon.sum;            \
	done
	@gprof $(PARFLOW) gmon.sum > big_domain.gprof.txt

.PHONY: plot post-cpu
post-cpu:
	./extract_times --output=cpu-times.csv

.PHONY: plot post-seq
post-seq:
	./extract_times --output=seq-times.csv

.PHONY: plot post-cuda
post-cuda:
	./extract_times --output=cuda-times.csv

.PHONY: plot
plot:
	./plot

clean:
	@rm -f gmon.sum gmon.txt
	@rm -f gmon.out
	@rm -f *.pfb*
	@rm -f *.pfidb*
	@rm -f *.silo*
	@rm -f *.pfsb*
	@rm -f *.log
	@rm -f .hostfile
	@rm -f .amps.*
	@rm -f *.out.pftcl
	@rm -f *.out.txt
	@rm -f rsl.*
	@rm -f *.pfmetadata

veryclean: clean
	@rm -f *.csv
	@rm -f out.png
