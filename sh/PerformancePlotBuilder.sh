#!/bin/bash

# This script analyses SafeSquid's performance.log

. /opt/safesquid/safesquid_params.sh && EXPORT_INI

## INPUT

START_DURATION=${1?Error: Please Specify the First Argument as Start Duration}

END_DURATION=${2?Error: Please Specify the Second Argument as End Duration}

PERFORMANCE_FILE_NAME=${3?Error: Please Specify the Third Argument as Name of the file to be Created which will store the Performance Plot}

PERFORMANCE_LOG_FILE=${4:-/var/log/safesquid/performance/performance.log}


### Create the Log File TO Store the Script Status
_OUTDIR="/tmp/$$"
mkdir -p "${_OUTDIR}/"
export EXE_LOG_SOURCE="${_OUTDIR}/plot_exe.log"
env > ${EXE_LOG_SOURCE}

echo "[START_DURATION: ${START_DURATION}], [END_DURATION: ${END_DURATION}]";
echo "[PERFORMANCE_FILE_NAME: ${PERFORMANCE_FILE_NAME}], [PERFORMANCE_LOG_FILE: ${PERFORMANCE_LOG_FILE}]";

### comment the specification of LOG_SOURCE here if you wish to analyze a local performance.log

CUR_TIME=`date +%Y-%m-%d-%H-%M-%S`

OUTPUT="${PERFORMANCE_FILE_NAME}"

REPORT_DATE=`date +%Y-%m-%d%t%H:%M:%S`

REPORT_TITLE="Analysis of SafeSquid Performance Logs"

DATE=`date`;

PLOT_WIDTH=1200

LOG() {
	echo "${DATE}:  ${*}" >> ${EXE_LOG_SOURCE}
}

PLOT() {

	LOG "PERFORMANCE_LOG_FILE: ${PERFORMANCE_LOG_FILE}"

	START_DATE=$START_DURATION
	END_DATE=$END_DURATION

	LOG "START DATE from env :${START_DATE}"
	LOG "END DATE from env :${END_DATE}"

	A=${START_DATE}
	B=${END_DATE}

	echo "[START_DATE: ${START_DATE}], [END_DATE: ${END_DATE}]"

	LOG A: $A
	LOG B: $B

	LOG "Plotting: started: `date +%Y-%m-%d.%H:%M:%S.%N` "
	ST=`date +%s`


### Using the New GnuPlot Version 5.2 PatchLevel 7 to create Plot: The Binary File Path is /usr/local/bin/gnuplot

/usr/bin/gnuplot << _EOF

set style fill transparent solid 0.4 noborder

##### template #####

# CPU Utilization
# PLOT38="Running Processes"
# PLOT39="Waiting Processes"
# PLOT40="User Time"
# PLOT41="System Time"
# PLOT42="Total (user + system) Time"
# PLOT43="User Time Delta"
# PLOT44="System Time Delta"
# PLOT45="Total Time Delta"

# unset label; unset logscale y
# p=2 ; d=(d == 0 ? n : 0 ) ; c = l - d -1  ; j=1 ;

# set autoscale y ; set autoscale y2 ;

#print PLOT4
#print PLOT5
#print PLOT6

# set label j PLOT4 at graph 0,0  rotate left  tc lt j offset -c,0 ; c = c - 2 ; j=j + 1

# c = l - d -1  ;
# set label j PLOT5 at graph 1,0  rotate left tc lt j offset c,0 ; c = c - 2 ; j=j + 1
# set label j PLOT6 at graph 1,0  rotate left tc lt j offset c,0 ; c = c - 2 ; j=j + 1


# plot \
#       "${PERFORMANCE_LOG_FILE}" usi 1:32 ti PLOT4 w impulses  lw 3,\
#       "${PERFORMANCE_LOG_FILE}" usi 1:33 ti PLOT5 w lines  lw 2 axes x1y2,\
#       "${PERFORMANCE_LOG_FILE}" usi 1:35 ti PLOT6 w lines  lw 1 axes x1y2


##### - #####


# total number of plots
t=18.0
# width of individual plots
# w=1024
w=${PLOT_WIDTH}
# height of individual plots
h=150
# left margin
l=30
# right margin
r=l


set datafile commentschars "#T"

# set term png size 600,400

# set term png size 800,1000
# set output "figure.png"

# set term dumb 144 200 enhanced

#set terminal png  size w,( (t + 1.5) * h)


set terminal png  transparent interlace  truecolor size w,(( t * h) + ( 19 * 25) + h )

#set terminal png interlace  truecolor size w,(( t * h) + ( 19 * 25) + h ) \
#                      x00ffffff x000000 x404040 \
#                      xFFff0000 x00007700 x000000ff x00ffff00 \
#                      x0000ffff x00ff00ff x00dda0dd x009500d3    # defaults


set output "${OUTPUT}"


# set timefmt "<format string>"
set timefmt "%Y%m%d%H%M%S"
set xdata time          # The x axis data is time
# set format x "%Y-%m-%d %H:%M:%S"      # On the x-axis, we want tics like Jun 10
# set xtics 2
# Input file contains comma-separated values fields
set datafile separator ","
# set xrange [0:400]
set xtics border mirror out
set ytics border nomirror out
set y2tics border nomirror out
set key off
#set xtics autofreq   rotate by 90
set xtics autofreq
set autoscale y ; set autoscale y2 ; set autoscale x

# set xrange ["20150327000000":"20150327010000"]
# set xrange ["20150327000000":*]
# test to pass env variables
#set xrange ["${A}":"${B}"]




set xrange ["${START_DATE}":"${END_DATE}"]
show xrange

n=l/3
d=0

set grid

# set multiplot

set multiplot layout t,1 rowsfirst title "${REPORT_TITLE}\n${RESTART}"

set bmargin 0
set tmargin 1
set rmargin r
set lmargin l


# set key outside rmargin center vertical


set macros
set format x ""


plot_reset = " d=(d == 0 ? n : 0 ) ; j=1 ; unset label; unset logscale y ; unset autoscale y; unset autoscale y2 ; set autoscale y ; set autoscale y2 ;"

lreset = "c = l - d -1;"
left_side = "at graph 0,0  rotate left  tc lt j offset -c,0 ; c= c - 2 ; j=j + 1 ;"

right_side = "at graph 1,0  rotate left  tc lt j offset c,0 ; c= c - 2 ; j=j + 1 ;"


##################################################### Connections #####################################################################
# first plot

@plot_reset
# chart 1

PLOT1="Concurrent Client Connections"
PLOT2="Concurrent Active Requests"


#print PLOT1
#print PLOT2

@lreset
set label j PLOT1 @left_side

@lreset
set label j PLOT2 @right_side

plot 	"${PERFORMANCE_LOG_FILE}" usi 1:(\$3-\$4) ti PLOT1 w impulses  lw 3,\
		"${PERFORMANCE_LOG_FILE}" usi 1:(\$8) ti PLOT2 w impulses lw 1 lc rgb "#F8009D73" axes x1y2


##### Incoming Pressure #####
@plot_reset
# chart 2

PLOT4="New Incoming Connections"
PLOT5="Client Connections in Pool"

#print PLOT4
#print PLOT5

@lreset
set label j PLOT4 @left_side

@lreset
set label j PLOT5 @right_side


plot 	"${PERFORMANCE_LOG_FILE}" usi 1:32 ti PLOT4 w impulses  lw 3,\
		"${PERFORMANCE_LOG_FILE}" usi 1:6 ti PLOT5 w impulses  lw 1 lc rgb "#F8009D73" axes x1y2



##### Request Handling #####
@plot_reset
# chart 3

PLOT7="Client Transactions Handled"
PLOT8="Outbound Connections demanded"

#print PLOT7
#print PLOT8

@lreset
set label j PLOT7 @left_side

@lreset
set label j PLOT8 @right_side


plot 	"${PERFORMANCE_LOG_FILE}" usi 1:34 ti PLOT7 w impulses  lw 3 axes x1y1,\
		"${PERFORMANCE_LOG_FILE}" usi 1:(\$42 + \$43 + +\$44 + \$51) ti PLOT8 w impulses  lw 1 lc rgb "#F8009D73" axes x1y2

##### - #####



##### WAN Pressure #####
@plot_reset
# chart 4

PLOT13="Outbound Connection Pool Reused"
PLOT14="Outbound Connections in Pool"

#print PLOT13
#print PLOT14

@lreset
set label j PLOT13 @left_side

@lreset
set label j PLOT14 @right_side


plot 	"${PERFORMANCE_LOG_FILE}" usi 1:44 ti PLOT13 w impulses  lw 3,\
		"${PERFORMANCE_LOG_FILE}" usi 1:16 ti PLOT14 w impulses  lw 1 lc rgb "#F8009D73" axes x1y2



# Network Pressure
@plot_reset
# chart 5

PLOT3="Total TCP Connections"
PLOT4="Idle TCP Connections"
#print PLOT3
#print PLOT4


@lreset
set label j PLOT3 @left_side


@lreset
set label j PLOT4 @right_side

plot 	"${PERFORMANCE_LOG_FILE}" usi 1:(\$3 - \$4 + \$42 + \$16) ti PLOT3 w impulses  lw 3,\
		"${PERFORMANCE_LOG_FILE}" usi 1:(\$6 + \$16) ti PLOT4 w impulses  lw 1 lc rgb "#F8009D73" axes x1y2


##### Data Xfer #####

# Data Xfer
@plot_reset
# chart 6

PLOT16="Bytes In (MBytes)"
PLOT17="Bytes Out (MBytes)"

#print PLOT16
#print PLOT17

@lreset
set label j PLOT16 @left_side


@lreset
set label j PLOT17 @right_side


plot 	"${PERFORMANCE_LOG_FILE}" usi 1:(\$46 / 1048576) ti PLOT16 w impulses  lw 3,\
		"${PERFORMANCE_LOG_FILE}" usi 1:(\$47 / 1048576) ti PLOT17 w impulses  lw 1 lc rgb "#F8009D73" axes x1y2

##### Caching #####


# Caching
@plot_reset
# chart 7

PLOT18="Caching Objects in Memory"
PLOT19="Caching Objects Removed from Memory"
PLOT20="Caching Objects Added into Memory"

#print PLOT18
#print PLOT19
#print PLOT20

@lreset
set label j PLOT18 @left_side
set label j PLOT19 @left_side


@lreset
set label j PLOT20 @right_side


plot 	"${PERFORMANCE_LOG_FILE}" usi 1:(\$19-\$20) ti PLOT18 w impulses  lw 5,\
		"${PERFORMANCE_LOG_FILE}" usi 1:49 ti PLOT19 w impulses  lw 1 lc rgb "#F8009D73" axes x1y2,\
		"${PERFORMANCE_LOG_FILE}" usi 1:48 ti PLOT20 w impulses  lw 1 lc rgb "#F856B4E9" axes x1y2


##### DNS #####
@plot_reset
# chart 8

PLOT22="New DNS Queries"
PLOT23="DNS Query Reused"

#print PLOT22
#print PLOT23

@lreset
set label j PLOT22 @left_side


@lreset
set label j PLOT23 @right_side


plot 	"${PERFORMANCE_LOG_FILE}" usi 1:51 ti PLOT22 w impulses  lw 3 ,\
		"${PERFORMANCE_LOG_FILE}" usi 1:50 ti PLOT23 w impulses  lw 1 lc rgb "#F8009D73" axes x1y2


##### Threading Capacity #####

@plot_reset
# chart 9

PLOT8="Spare Client Threads"
PLOT9="Client Threads in Use"
PLOT10="Client Threads in Waiting"


#print PLOT8
#print PLOT9
#print PLOT10


@lreset
set label j PLOT8 @left_side


@lreset
set label j PLOT9 @right_side
set label j PLOT10 @right_side


plot 	"${PERFORMANCE_LOG_FILE}" usi 1:7 ti PLOT8 w lines  lw 5,\
		"${PERFORMANCE_LOG_FILE}" usi 1:8 ti PLOT9 w impulses  lw 1 lc rgb "#F8009D73" axes x1y2,\
		"${PERFORMANCE_LOG_FILE}" usi 1:9 ti PLOT10 w impulses lw 1 lc rgb "#F256B4E9" axes x1y2

##### System Memory #####


# System Memory
PLOT24="Total System Memory (GBytes)"
PLOT25="Free System Memory (MBytes)"

@plot_reset
# chart 10

#print PLOT24
#print PLOT25

@lreset
set label j PLOT24 @left_side


@lreset
set label j PLOT25 @right_side

plot 	"${PERFORMANCE_LOG_FILE}" usi 1:(\$24 / 1048576) ti PLOT24 w lines  lw 3,\
		"${PERFORMANCE_LOG_FILE}" usi 1:(\$25 / 1024) ti PLOT25 w impulses  lw 1 lc rgb "#F8009D73" axes x1y2


##### SafeSquid Memory #####

# SafeSquid Memory
PLOT26="SafeSquid Virtual Memory (MBytes)"
PLOT27="SafeSquid Library Memory (MBytes)"
PLOT28="SafeSquid Resident Memory (MBytes)"
PLOT29="SafeSquid Shared Memory (MBytes)"
PLOT30="SafeSquid Code Memory (MBytes)"
PLOT31="SafeSquid Data Memory (MBytes)"


@plot_reset
# chart 11

#print PLOT26	-> DEFAULT COLOR CODE : lc rgb "#009400D3"
#print PLOT27	-> COLOR CODE : lc rgb "#F8009D73"
#print PLOT28	-> COLOR CODE : lc rgb "#F856B4E9"
#print PLOT29	-> COLOR CODE : lc rgb "#F8E69F00"
#print PLOT30	-> COLOR CODE : lc rgb "#F8F0E442" 
#print PLOT31	-> COLOR CODE : lc rgb "#F8F0E442" 


@lreset
set label j PLOT26 @left_side
set label j PLOT27 @left_side



@lreset
set label j PLOT28 @right_side
set label j PLOT29 @right_side
set label j PLOT30 @right_side
set label j PLOT31 @right_side


plot 	"${PERFORMANCE_LOG_FILE}" usi 1:(\$26 / 1024) ti PLOT26 w lines  lw 11,\
		"${PERFORMANCE_LOG_FILE}" usi 1:(\$31 / 1024) ti PLOT27 w lines  lw 9,\
		"${PERFORMANCE_LOG_FILE}" usi 1:(\$27 / 1024) ti PLOT28 w lines  lw 7 axes x1y2,\
		"${PERFORMANCE_LOG_FILE}" usi 1:(\$28 / 1024) ti PLOT29 w lines  lw 5 axes x1y2,\
		"${PERFORMANCE_LOG_FILE}" usi 1:(\$29 / 1024) ti PLOT30 w lines  lw 3 axes x1y2,\
		"${PERFORMANCE_LOG_FILE}" usi 1:(\$30 / 1024) ti PLOT31 w lines  lw 1 axes x1y2

##### Errors #####

# Errors
PLOT32="DNS Query failures"
PLOT33="Outbound Connections Failed"
PLOT34="Threading Errors"


@plot_reset
# chart 12

#print PLOT32
#print PLOT33
#print PLOT34


@lreset
set label j PLOT32 @left_side
set label j PLOT33 @left_side


@lreset
set label j PLOT34 @right_side


plot 	"${PERFORMANCE_LOG_FILE}" usi 1:52 ti PLOT32 w impulses  lw 5,\
		"${PERFORMANCE_LOG_FILE}" usi 1:43 ti PLOT33 w impulses  lw 3 axes x1y2,\
		"${PERFORMANCE_LOG_FILE}" usi 1:41 ti PLOT34 w impulses  lw 1 axes x1y2


##### System Load #####

# System Load
PLOT35="load avg.(1 min)"
PLOT36="load avg.(5 min)"
PLOT37="load avg.(15 min)"


@plot_reset
# chart 13

#print PLOT35
#print PLOT36
#print PLOT37


@lreset
set label j PLOT35 @left_side


@lreset
set label j PLOT36 @right_side
set label j PLOT37 @right_side


plot 	"${PERFORMANCE_LOG_FILE}" usi 1:53 ti PLOT35 w steps  lw 3,\
		"${PERFORMANCE_LOG_FILE}" usi 1:54 ti PLOT36 w steps  lw 2 axes x1y2,\
		"${PERFORMANCE_LOG_FILE}" usi 1:55 ti PLOT37 w steps  lw 1 axes x1y2


##### CPU Switching #####

# CPU Switching
PLOT38="Running Processes"
PLOT39="Waiting Processes"


@plot_reset
# chart 14

#print PLOT38
#print PLOT39


@lreset
set label j PLOT38 @left_side

@lreset
set label j PLOT39 @right_side


plot 	"${PERFORMANCE_LOG_FILE}" usi 1:56 ti PLOT38 w impulses  lw 3,\
		"${PERFORMANCE_LOG_FILE}" usi 1:63 ti PLOT39 w impulses  lw 1 lc rgb "#F8009D73" axes x1y2


##### CPU Utilization 1 #####

# CPU Utilization
@plot_reset
# chart 15

PLOT43="Total CPU Use Delta (msecs)"
PLOT44="User Time (msecs)"
PLOT45="System Time (msecs)"

#print PLOT43
#print PLOT44
#print PLOT45

@lreset
set label j PLOT43 @left_side

@lreset
set label j PLOT44 @right_side
set label j PLOT45 @right_side

plot 	"${PERFORMANCE_LOG_FILE}" usi 1:(\$63 * 1000) ti PLOT43 w impulses  lw 5,\
		"${PERFORMANCE_LOG_FILE}" usi 1:(\$61 * 1000) ti PLOT44 w lines  lw 3 axes x1y2,\
		"${PERFORMANCE_LOG_FILE}" usi 1:(\$62 * 1000) ti PLOT45 w lines  lw 1 axes x1y2

##### CPU Utilization 2 #####

# CPU Utilization
PLOT40="Total CPU Use Trend"
PLOT41="User Time Trend"
PLOT42="System Time Trend"


@plot_reset
# chart 16

#print PLOT40
#print PLOT41
#print PLOT42

@lreset
set label j PLOT40 @left_side

@lreset
## LEFT EMPTY BY DEFAULT


plot 	"${PERFORMANCE_LOG_FILE}" usi 1:( (\$60 + \$63 ) / \$2) ti PLOT40 w steps  lw 5,\
		"${PERFORMANCE_LOG_FILE}" usi 1:( (\$58 + \$61 ) / \$2) ti PLOT41 w steps  lw 3,\
		"${PERFORMANCE_LOG_FILE}" usi 1:( (\$59 + \$62) / \$2) ti PLOT42 w steps  lw 1



##### Process Life #####

# last plot must LOG time as the significant x values
set format x "%Y-%m-%d %H:%M:%S"
set xtics rotate

@plot_reset
# chart 17

set logscale y2

PLOT46="SafeSquid Virtual Memory (MBytes)"
PLOT47="Process Age"

#print PLOT46
#print PLOT47



@lreset
set label j PLOT46 @left_side

@lreset
set label j PLOT47 @right_side


set style fill transparent solid 0.4
plot 	"${PERFORMANCE_LOG_FILE}" usi 1:(\$26 / 1024 ) ti PLOT46 w lines  lw 3 axes x1y1,\
		"${PERFORMANCE_LOG_FILE}" usi 1:2 ti PLOT47 w lines lw 1 axes x1y2

# last plot
set bmargin 0

##### - #####



unset multiplot
exit

_EOF

	ET=`date +%s`
	LOG "Plotting: ended: `date +%Y-%m-%d.%H:%M:%S.%N` "
	LOG "Processing time $[ ${ET} - ${ST} ] seconds"
}

START() {
	
	echo "PERFORMANCE_LOG_FILE: [${PERFORMANCE_LOG_FILE}]"
	[ -f ${PERFORMANCE_LOG_FILE} ] && PLOT
	[ -f ${PERFORMANCE_LOG_FILE} ] || LOG "log file not found"
	#sleep 3s
	LOG `stat ${OUTPUT}`
}

START 2>> ${EXE_LOG_SOURCE} > /dev/null

echo "START SCRIPT"
START;

exit 0