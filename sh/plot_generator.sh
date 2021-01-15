######################################################################
#1. One Day [Past 24 Hours From Now(When Script Runs)]
#2. Last 3 Days [Past 72 Hours From Now(When Script Runs)]
#3. Last 7 Days [Past 168 Hours From Now(When Script Runs)]
#4. Last 15 Days [Past 360 Hours From Now(When Script Runs)]
#5. Last 30 Days [Past 720 Hours From Now(When Script Runs)]
######################################################################


#declare -A plots=( ["oneday"]="1" ["last3days"]="3"  ["last7days"]="7" ["last15days"]="15" ["last30days"]="30" )
declare -A plots=( ["1"]="oneday" ["3"]="last3days"  ["7"]="last7days" ["15"]="last15days" ["30"]="last30days" )

##################################
##	PreDefined Store Location
##################################
PERFORMANCE_PLOT_BUILDER_SCRIPT="/usr/local/safesquid/ui_root/cgi-bin/PerformancePlotBuilder.sh"
PERFORMANCE_STATS_STORE="/var/log/safesquid/performance_processing/"
PERFORMANCE_PLOT_STORE="${PERFORMANCE_STATS_STORE}/plots/"
PERFORMANCE_LOG_STORE="${PERFORMANCE_STATS_STORE}/logs/"
PERFORMANCE_LOG_DIR="/var/log/safesquid/performance/"

CHECK_EXIT_IF_NOT() {
	FILE_TO_CHECK=$1
	if [[ ! -f ${FILE_TO_CHECK} ]]
	then
		echo "[-]Please Check PerformancePlotBuilder.sh File Exists in Path: ${PERFORMANCE_PLOT_BUILDER_SCRIPT}, if not add it";
		exit;
	fi
}

CREATE_IF_NOT_EXISTS() { 
	DIR=$1;
	if [[ ! -d ${DIR} ]]
	then 
		mkdir $1; 
	fi 
}

CREATE_DIRS() {
	
	CREATE_IF_NOT_EXISTS ${PERFORMANCE_STATS_STORE};
	CREATE_IF_NOT_EXISTS ${PERFORMANCE_PLOT_STORE};
	CREATE_IF_NOT_EXISTS ${PERFORMANCE_LOG_STORE};
	
	for day_plot in ${plots[@]};
	do
		if [[ ! -d ${PERFORMANCE_PLOT_STORE}/${day_plot} ]]
		then 
			mkdir ${PERFORMANCE_PLOT_STORE}/${day_plot}; 
		fi 
	done
}


GET_LOGS() {
	
	GET_LOG_FOR=$1
	FROM_DAY=$(date '+%Y%m%d' --date "${GET_LOG_FOR} day ago");
	LOG_GREP_STRING=${FROM_DAY};
	for ((i=0;i<${GET_LOG_FOR};i++)); 
	do
		TEMP_DAY=$(date '+%Y%m%d' --date "${i} day ago");
		LOG_GREP_STRING="${LOG_GREP_STRING}|${TEMP_DAY}";
	done
	# GLOB to Take only Performance.log into Account
	zgrep -iEah ${LOG_GREP_STRING} ${PERFORMANCE_LOG_DIR}/*performance.log* > "${PERFORMANCE_LOG_STORE}/${plots[${GET_LOG_FOR}]}.log";
	
}


#########################
## Not Optimized To Get the Logs and Reuse it for other Plot Making
## Sending All Keys, Make Sure Dictionary/Hash Table is: ["0"]="oneday"
########################
PLOT_BUILDER() {
	for day_plot in ${!plots[@]};
	do
		GET_LOGS ${day_plot};
		FROM_DATE_TIME=$(date '+%Y%m%d' --date "${GET_LOG_FOR} day ago");
		FROM_DATE_TIME="${FROM_DATE_TIME}000000";
		TO_DATE_TIME=$(date '+%Y%m%d%H%M');
		TO_DATE_TIME="${TO_DATE_TIME}00";
		GENERATE_PLOT ${PERFORMANCE_PLOT_BUILDER_SCRIPT} ${FROM_DATE_TIME} ${TO_DATE_TIME} "${PERFORMANCE_PLOT_STORE}/${plots[${GET_LOG_FOR}]}/${plots[${GET_LOG_FOR}]}_${FROM_DATE_TIME}_${TO_DATE_TIME}.png" "${PERFORMANCE_LOG_STORE}/${plots[${GET_LOG_FOR}]}.log"
	done
	
}


GENERATE_PLOT() {
	
	PERFORMANCE_PLOT_BUILDER_SCRIPT=$1
	START_TIME=$2 
	END_TIME=$3 
	PERFORMANCE_PLOT_IMAGE_FILE=$4 
	SPECIFIC_PERFORMANCE_LOG=$5	

	echo "[PERFORMANCE_PLOT_BUILDER_SCRIPT: ${PERFORMANCE_PLOT_BUILDER_SCRIPT}]"
	echo "[START_TIME: ${START_TIME}]"
	echo "[END_TIME: ${END_TIME}]"
	echo "[PERFORMANCE_PLOT_IMAGE_FILE: ${PERFORMANCE_PLOT_IMAGE_FILE}]"
	echo "[SPECIFIC_PERFORMANCE_LOG: ${SPECIFIC_PERFORMANCE_LOG}]"
	# Performance Plot Builder Script Call
	bash ${PERFORMANCE_PLOT_BUILDER_SCRIPT} ${START_TIME} ${END_TIME} ${PERFORMANCE_PLOT_IMAGE_FILE} ${SPECIFIC_PERFORMANCE_LOG}
}

C_CLEANER() {
	rm -rfv ${PERFORMANCE_LOG_STORE}/*;
}


MAIN() {
	CHECK_EXIT_IF_NOT ${PERFORMANCE_PLOT_BUILDER_SCRIPT};
	CREATE_DIRS;
	PLOT_BUILDER;
	C_CLEANER;
}

MAIN;