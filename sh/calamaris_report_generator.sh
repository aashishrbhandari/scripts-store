#!/bin/bash

###################
##
## ARGUMENT as Date in date command format
## Example: "today", "1 day ago", '2 day ago'
##
##
###################


DAY=${1?Error: Please provide the day for which you want to generate reports Example: "today", "1 day ago", '2 day ago'};

# The OUTPUT LOOKS LIKE : date +%d/%m/%Y --> 20191213
STANDARD_LOG_FILE_FORMAT=$(date +%Y%m%d --date "${DAY}");

# The OUTPUT LOOKS LIKE : date +%d/%m/%Y --> 13/12/2019
SARG_DATE_FORMAT=$(date +%d/%m/%Y --date "${DAY}");

## current day which will hold all data of today
EXTENDED_LOG_CURRENT_DAY_FILE_NAME="$(date +%Y%m%d --date "${DAY}").*log$";
EXTENDED_ZIP_LOG_CURRENT_DAY_FILE_NAME="$(date +%Y%m%d --date "${DAY}").*gz$";

## A day previous: yesterday which might hold current day log lines
EXTENDED_LOG_PREVIOUS_DAY_FILE_NAME="$(date +%Y%m%d --date "${DAY}-1 day").*log$";
EXTENDED_ZIP_LOG_PREVIOUS_DAY_FILE_NAME="$(date +%Y%m%d --date "${DAY}-1 day").*gz$";

# The OUTPUT LOOKS LIKE : date +%d/%m/%Y --> 13/Dec/2019
DATE_FORMAT_INSIDE_SAFESQUID_EXTENDED_LOG=$(date +%d/%b/%Y --date "${DAY}");

IS_CALAMARIS_INSTALLED() {	
	apt-get install -y ${PACKAGE_NAME};
}

##################################################################
#################### All IMP Parameters needed ###################
##################################################################

CREATE_DIR_IF_NOT() {
	if [[ ! -d $1 ]];
	then
		echo "Creating DIR -> ${1}";
		mkdir -p $1
	else
		echo "DIR -> ${1} Already Present";
	fi
}

## extended log Dir
EXTENDED_LOG_DIR="/var/log/safesquid/extended";

## access log Dir
ACCESS_LOG_DIR="/var/log/safesquid/access";
CREATE_DIR_IF_NOT ${ACCESS_LOG_DIR};

## Calamaris Dir
CALAMARIS_REPORTS_DIR="/var/www/safesquid/calamaris";
CREATE_DIR_IF_NOT ${CALAMARIS_REPORTS_DIR};

## Sarg Dir
SARG_REPORTS_DIR="/var/www/safesquid/sarg";
CREATE_DIR_IF_NOT ${CALAMARIS_REPORTS_DIR};

# This DIRECTORY CONTAINS the FILE RUNNING the SCRIPT
SCRIPT_DIR="/usr/local/safesquid/ui_root/cgi-bin";
CREATE_DIR_IF_NOT ${SCRIPT_DIR};

EXTENDED_TO_ACCESS_SCRIPT="${SCRIPT_DIR}/extendedToAccess";

CREATED_EXTENDED_LOG_FILE="${ACCESS_LOG_DIR}/${STANDARD_LOG_FILE_FORMAT}_$(hostname)_Extended.log"

CREATED_ACCESS_LOG_FILE="${ACCESS_LOG_DIR}/${STANDARD_LOG_FILE_FORMAT}_$(hostname)_Access.log"

#SAFESQUID_ACCESS_LOG_DATE_FORMAT="";

ARE_SCRIPTS_PRESENT() {
	if [[ -f ${EXTENDED_TO_ACCESS_SCRIPT} ]];
	then
		echo -e "Script is Present Inside ${SCRIPT_DIR}. Began the Process";
	else
		echo -e "Script NOT Present in ${SCRIPT_DIR}\nPlease add the script and then start the script again";
		echo "Downloading The Script From drive.safesquid.com and storing it..."
        curl -sk "https://drive.safesquid.com/public.php?service=files&t=567a6ed35596441adc85a6cb93cb7b34&path=%2Fsh&files=extended_log_to_access&download" -o ${EXTENDED_TO_ACCESS_SCRIPT};   
		
	fi
	chmod +x ${EXTENDED_TO_ACCESS_SCRIPT};
}

GENERATE_ACCESS_LOG() {
	
	## Get all the files holding the extended log into one log file of the current date
	ALL_EXTENDED_LOG_FILES+=($(ls ${EXTENDED_LOG_DIR} | grep -E ${EXTENDED_LOG_CURRENT_DAY_FILE_NAME}));
	ALL_EXTENDED_LOG_FILES+=($(ls ${EXTENDED_LOG_DIR} | grep -E ${EXTENDED_LOG_PREVIOUS_DAY_FILE_NAME}));
	
	ALL_EXTENDED_ZIP_LOG_FILES+=($(ls ${EXTENDED_LOG_DIR} | grep -E ${EXTENDED_ZIP_LOG_CURRENT_DAY_FILE_NAME}));
	ALL_EXTENDED_ZIP_LOG_FILES+=($(ls ${EXTENDED_LOG_DIR} | grep -E ${EXTENDED_ZIP_LOG_PREVIOUS_DAY_FILE_NAME}));
	
	echo "ALL_EXTENDED_LOG_FILES => ${ALL_EXTENDED_LOG_FILES[@]}"
	echo "ALL_EXTENDED_ZIP_LOG_FILES => ${ALL_EXTENDED_ZIP_LOG_FILES[@]}"

	## Empty the Extended Log FIle [If it already contain some data]
	echo "" > ${CREATED_EXTENDED_LOG_FILE};
	
	EXTENDED_LOG_CURR_FILE_PATH=$(readlink -f extended.log);
	EXTENDED_LOG_CURR_FILE=$(basename ${EXTENDED_LOG_CURR_FILE_PATH});

	if [[ ! "${ALL_EXTENDED_LOG_FILES[@]}" =~ ${EXTENDED_LOG_CURR_FILE} ]]
	then
		ALL_EXTENDED_LOG_FILES+=(${EXTENDED_LOG_CURR_FILE});
	fi
	
	for ONE_LOG_FILE in ${ALL_EXTENDED_LOG_FILES[@]};
	do
		grep -a ${DATE_FORMAT_INSIDE_SAFESQUID_EXTENDED_LOG} ${EXTENDED_LOG_DIR}/${ONE_LOG_FILE} >> ${CREATED_EXTENDED_LOG_FILE} ;
	done
	
	for ONE_ZIP_LOG_FILE in ${ALL_EXTENDED_ZIP_LOG_FILES[@]};
	do
		zcat ${EXTENDED_LOG_DIR}/${ONE_ZIP_LOG_FILE} | grep -a ${DATE_FORMAT_INSIDE_SAFESQUID_EXTENDED_LOG} >> ${CREATED_EXTENDED_LOG_FILE};
	done
	
	## Start Generating Access log
	${EXTENDED_TO_ACCESS_SCRIPT} ${CREATED_EXTENDED_LOG_FILE} ${CREATED_ACCESS_LOG_FILE};
}

CALAMARIS_CMD_GENERATOR() {
	
	ACCESS_LOG_FILE_WITH_FULLPATH=$1;
	OUTPUT_FILE_NAME=$2;
	OUTPUT_DIR=$3;
	CALAMARIS_CONF_FILE="/etc/calamaris/calamaris.conf";
	
	CALAMARIS_CMD+=("cat ${ACCESS_LOG_FILE_WITH_FULLPATH} |");
	CALAMARIS_CMD+=("/usr/bin/calamaris");
	CALAMARIS_CMD+=("--config-file ${CALAMARIS_CONF_FILE}");
	CALAMARIS_CMD+=("-F html");
	CALAMARIS_CMD+=("--domain-report 50");
	CALAMARIS_CMD+=("--performance-report 60");
	CALAMARIS_CMD+=("--requester-report 20");
	CALAMARIS_CMD+=("--status-report");
	CALAMARIS_CMD+=("--type-report 20");
	CALAMARIS_CMD+=("--response-time-report");
	CALAMARIS_CMD+=("--errorcode-distribution-report");
	CALAMARIS_CMD+=("--domain-report-limit 3");
	CALAMARIS_CMD+=("--domain-report-n-level 10");
	CALAMARIS_CMD+=("--requester-report-with-targets 10");
	CALAMARIS_CMD+=("--size-distribution-report 2");
	CALAMARIS_CMD+=("--requester-report-use-user-info");
	CALAMARIS_CMD+=("--output-file ${OUTPUT_FILE_NAME}");
	CALAMARIS_CMD+=("--output-path ${OUTPUT_DIR}");
	
	echo ${CALAMARIS_CMD[@]}
	eval ${CALAMARIS_CMD[@]}
}

SARG_CMD_GENERATOR() {
	
	SARG_REPORT_FOR_DATE=$1;
	ACCESS_LOG_FILE_WITH_FULLPATH=$2;
	OUTPUT_DIR=$3;
	
	SARG_CMD+=("sarg");
	SARG_CMD+=("-d ${SARG_REPORT_FOR_DATE}");
	SARG_CMD+=("-l ${ACCESS_LOG_FILE_WITH_FULLPATH}");
	SARG_CMD+=("-o ${OUTPUT_DIR}");

	echo ${SARG_CMD[@]}
	${SARG_CMD[@]}
}



GENERATE_CALAMARIS_REPORT() {
	CALAMARIS_CMD_GENERATOR ${CREATED_ACCESS_LOG_FILE} "${STANDARD_LOG_FILE_FORMAT}_$(hostname)_Calamaris.html" ${CALAMARIS_REPORTS_DIR};
	cp "${CALAMARIS_REPORTS_DIR}/${STANDARD_LOG_FILE_FORMAT}_$(hostname)_Calamaris.html" .
    echo "Calamaris Log Created... @ ${STANDARD_LOG_FILE_FORMAT}_$(hostname)_Calamaris.html"
}

GENERATE_SARG_REPORT() {
	SARG_CMD_GENERATOR ${SARG_DATE_FORMAT} ${CREATED_ACCESS_LOG_FILE} ${SARG_REPORTS_DIR};
}

C_CLEANER() {
	rm -rfv ${CREATED_EXTENDED_LOG_FILE} ${CREATED_ACCESS_LOG_FILE};
}

MAIN() {
	ARE_SCRIPTS_PRESENT;
	IS_CALAMARIS_INSTALLED;
	
	GENERATE_ACCESS_LOG;
	GENERATE_CALAMARIS_REPORT;
	#GENERATE_SARG_REPORT;
	C_CLEANER;
}

MAIN
