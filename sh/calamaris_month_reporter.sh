## *******IMP*******
## It is Important to Have SSH Setup (Key-Based Access) Done Prior This Script
## SSH Key based Access
## ssh-keygen -t rsa # Generate Keys Default Adds it in ~/.ssh as id_rsa
## copy the id_rsa.pub to Remote Linux Machine @ ~/.ssh in authorized_keys
## Make Sure Permissions are in Place (600)


REMOTE_CONN="root@127.0.0.1"


COPY_TO="/var/www/safesquid/calamaris"

PROCESSING_DIR="/var/log/safesquid/tmp_reports/"


OUR_LOG_DIR="${PROCESSING_DIR}/log_dir/"
OUR_TEMP_DIR="${PROCESSING_DIR}/temp_dir/"

echo "Step 0: Setting Dir";

echo "Checking If ${PROCESSING_DIR}, ${OUR_LOG_DIR} & ${OUR_TEMP_DIR} Exits!!!!";
[ ! -d "${OUR_LOG_DIR}" ] && echo "Directory: ${OUR_LOG_DIR} DOES NOT Exists. Creating One..."; mkdir -p ${OUR_LOG_DIR} ;
[ ! -d "${OUR_TEMP_DIR}" ] && echo "Directory: ${OUR_TEMP_DIR} DOES NOT Exists. Creating One..."; mkdir -p ${OUR_TEMP_DIR} ;
[ ! -d "${COPY_TO}" ] && echo "Directory: ${COPY_TO} DOES NOT Exists. Creating One..."; mkdir -p ${COPY_TO} ;

echo "Step 1: Get Last Month";

LAST_MONTH=$(date +'%b' -d 'last month')
LAST_MONTH_YEAR=$(date +'%Y' -d 'last month')

echo "Last Month & Last Month's Year is ${LAST_MONTH} & ${LAST_MONTH_YEAR} respectively.";

echo "Step 2: Find Logs Files of This TimeStamp";

FOR_MONTH="${LAST_MONTH}-${LAST_MONTH_YEAR}"
echo "TimeStamp: ${FOR_MONTH}";

LOG_FILES_SYS_1=($(find /var/log/safesquid/extended/ -type f -regex '.*[0-9+]-extended.log.*' -newermt "01-$FOR_MONTH -1 sec" -and -not -newermt "01-$FOR_MONTH +1 month -1 sec") )

echo "Get a Log File Which is Ahead in Time To Get Logs Captured in New Dated File";
LOG_FILE_AHEAD_IN_TIME=$(ls -rt `find /var/log/safesquid/extended/ -newermt "01-$FOR_MONTH +1 month" -type f` | head -n 1)

echo "Add it To the LOG_FILES_SYS_1";
LOG_FILES_SYS_1+=($LOG_FILE_AHEAD_IN_TIME)

echo "All Log Files For SYS 1:";
ls -lrth ${LOG_FILES_SYS_1[@]}

echo "Step 2(A): Extract Logs & Insert it to One File";

zgrep -iEa "${LAST_MONTH}/${LAST_MONTH_YEAR}" ${LOG_FILES_SYS_1[@]} > ${OUR_LOG_DIR}/${LAST_MONTH}-${LAST_MONTH_YEAR}-Full-extended.log

if [[ $REMOTE_CONN == "" ]];
then
    echo "Step 2(B): Omitted Since No Remote Conn To Extract Logs";
else
    echo "Step 2(B): Extract Logs From Remote Server(SSH) & Append it to the Same File";

    time LOG_FILES_SYS_2=($(ssh root@127.0.0.1 'FOR_MONTH=$(date +"%b-%Y" -d "last month") ; LOG_FILES_SYS=($(find /var/log/safesquid/extended/ -newermt "01-$FOR_MONTH -1 sec" -and -not -newermt "01-$FOR_MONTH +1 month -1 sec") ); LOG_FILE_AHEAD_IN_TIME=$(ls -rt `find /var/log/safesquid/extended/ -newermt "01-$FOR_MONTH +1 month" -type f` | head -n 1); LOG_FILES_SYS+=($LOG_FILE_AHEAD_IN_TIME); echo ${LOG_FILES_SYS[@]}'))

    echo "All Log Files For SYS 2: (Yet To be Downloaded are:)";
    echo ${LOG_FILES_SYS_2[@]};

    for ONE_LOG_FILE in ${LOG_FILES_SYS_2[@]};
    do
        echo "Downloading File: ${ONE_LOG_FILE} from ${REMOTE_CONN} & Adding to Dir: $OUR_TEMP_DIR";
        time scp ${REMOTE_CONN}:${ONE_LOG_FILE} ${OUR_TEMP_DIR}/ ;
    done

    echo "All LOG_FILES_SYS_2 Files:";

    ls -lrth ${OUR_TEMP_DIR};

    echo "Appending Logs to Same File"

    zgrep -iEa "${LAST_MONTH}/${LAST_MONTH_YEAR}" ${OUR_TEMP_DIR}/* >> ${OUR_LOG_DIR}/${LAST_MONTH}-${LAST_MONTH_YEAR}-Full-extended.log

    echo "Step 2(C): Removing Temp Dir: ${OUR_TEMP_DIR} Which Holds all the Remote Conn Log Files To Save Space Before Generating Access Log";
    rm -rfv ${OUR_TEMP_DIR}/*
    
fi

echo "Step 3: Convert Extended To Access Log";
echo "Make Sure extended_log_to_access file is Present and In Path & Executable Permission.."

${PROCESSING_DIR}/extended_log_to_access ${OUR_LOG_DIR}/${LAST_MONTH}-${LAST_MONTH_YEAR}-Full-extended.log ${OUR_LOG_DIR}/${LAST_MONTH}-${LAST_MONTH_YEAR}-Full-access.log

echo "Converted Check:";

ls -lrth ${OUR_LOG_DIR}/;

echo "Make Sure Calamaris is Installed in the System..";

#time apt update
time apt install calamaris

echo "Generating Calamaris Report:"

# More Detailed Report
#time cat ${OUR_LOG_DIR}/${LAST_MONTH}-${LAST_MONTH_YEAR}-Full-access.log | /usr/bin/calamaris -F html --domain-report 50 --performance-report 60  --requester-report 20 --status-report --type-report 20 --response-time-report --errorcode-distribution-report --domain-report-limit 3 --domain-report-n-level 10 --requester-report-with-targets 10 --size-distribution-report 2  --requester-report-use-user-info --output-file CalamarisReport-${LAST_MONTH}-${LAST_MONTH_YEAR}-Full.html --output-path ${PROCESSING_DIR}

# Client Specific Report
time cat ${OUR_LOG_DIR}/${LAST_MONTH}-${LAST_MONTH_YEAR}-Full-access.log | /usr/bin/calamaris --config-file /etc/calamaris/calamaris.conf -F html --domain-report 20 --performance-report 60 --requester-report 20 --type-report 20 --response-time-report --requester-report-with-targets 20 --domain-report-n-level 4 --output-file CalamarisReport-${LAST_MONTH}-${LAST_MONTH_YEAR}-Full.html --output-path ${PROCESSING_DIR}

cp ${PROCESSING_DIR}/CalamarisReport-${LAST_MONTH}-${LAST_MONTH_YEAR}-Full.html ${COPY_TO}/

echo "Calamaris Report Generated Check... & Copied To ${COPY_TO}...";

echo "Removing Contents of ${OUR_LOG_DIR} & ${OUR_TEMP_DIR}";
rm -rfv ${OUR_LOG_DIR}/*
rm -rfv ${OUR_TEMP_DIR}/*

###########
## Cron 
## Monthly Log Reporting
###########
#  0 1 1 * *    root /bin/bash /usr/local/src/scripts/sh/calamaris_month_reporter.sh &>> /var/log/safesquid/script_logs/calamaris_month_reporter.sh.log