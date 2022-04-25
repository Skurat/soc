#!/bin/bash
if [ -z "$1" ]; then
	echo "Need argument - path to target file."
    exit
elif [ ! -f "$1" ]; then
	echo "File does not exist"
    exit
elif ! grep -Pq "([0-9]{1,3}\.){3}[0-9]{1,3}" $1; then
    echo "File does not have any IP"
    exit
fi

### Declare variables
PATH_TO_SCRIPT="/home/silent4s/hack/soc/external_scan"
TARGETS_IPS=$(cat $1)
BOT_TOKEN="871783617:AAFcIkJ-Yytvq7IVxQkBbKAKPdDGoarve7U"
CHAT_ID="300576657"
date=`date "+%F %H:%M"`
TARGET_FILE="$1"
ROOT_OF_SCAN_RESULTS="$PATH_TO_SCRIPT/scan_results"
DIR_OF_SCAN_RESULTS=""
LOG_FILE="$PATH_TO_SCRIPT/response.log"
declare -a FOR_SED=("/Nmap/d" "/Not shown/d" "/SERVICE/d" "s/^+/%2b\ /g" "s/^-/\-\ \ /g" )
TEXT=""

### Create root dir of scan results
[ ! -d "$ROOT_OF_SCAN_RESULTS" ] && mkdir $ROOT_OF_SCAN_RESULTS

### Function for scan network
### $1 - ip address
### $2 - port range
### $3 - other options
function scanning (){
    nmap $1 -p $2 $3 -oA $FILE > /dev/null
}

### Function build path for scan results
### $1 - ip address
### $2 - sequense number
function build_path (){
    DIR_OF_SCAN_RESULTS="$ROOT_OF_SCAN_RESULTS/$1"
    [ ! -d "$DIR_OF_SCAN_RESULTS" ] && mkdir "$DIR_OF_SCAN_RESULTS"
    FILE="$DIR_OF_SCAN_RESULTS/$2-scan-current"
    COMPARE_FILE="$DIR_OF_SCAN_RESULTS/$2-compare-file"
    DIFF_FILE="$DIR_OF_SCAN_RESULTS/$2-diff"
}

### function delete information, that is not need
function fix_diff_file (){
        for val in "${FOR_SED[@]}"; do
            sed -i "$val" $DIFF_FILE
        done
}

function send_message (){
        if [[ -n "$TEXT" ]]; then
            TEXT_FOR_SEND=${TEXT//,/}
            resp_code=$(curl -d "text=$TEXT_FOR_SEND&chat_id=$CHAT_ID" --silent -i -o - -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" | grep HTTP)
            echo "$date - Status code of send to telegram is $resp_code" >> $LOG_FILE
            # cp $FILE.xml "to-approve-$(date +%F-%H).xml"
        fi
}

function check_first_scan_or_not (){
    if [ -e $COMPARE_FILE.xml ]; then
        ndiff $COMPARE_FILE.xml $FILE.xml > $DIFF_FILE
        fix_diff_file
        TEXT+="$(cat $DIFF_FILE),"
    else
        echo "$date - FILE \"$FILE.xml\" WAS CREATED AND COPY TO \"$COMPARE_FILE.xml\"" >> $LOG_FILE
        cp $FILE.xml $COMPARE_FILE.xml
    fi
}

### main function
### $1 - ip address
### $2 - sequense number
### $3 - port range
function main (){
    build_path "$1" "$2"
    scanning "$ip" "$3" "-T4"
    rm $DIR_OF_SCAN_RESULTS/*.gnmap
    check_first_scan_or_not
}

function save_ports_to_file (){
    WEB_PATH="$PATH_TO_SCRIPT/web"
    [ ! -d "$WEB_PATH" ] && mkdir "$WEB_PATH"
    echo $TEXT > "$WEB_PATH/res.txt"
}

for ip in $TARGETS_IPS
do
    echo -e "$ip"
    main $ip "1" "1-10000"
    sleep 5
    main $ip "2" "10001-20000"
    sleep 5
    main $ip "3" "20001-30000"
    sleep 5
    main $ip "4" "30001-40000"
    sleep 5
    main $ip "5" "40001-50000"
    sleep 5
    main $ip "6" "50001-65535"
done    
send_message
save_ports_to_file