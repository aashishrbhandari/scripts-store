#### Step1 : Get All Nic Card
#ls -l /sys/class/net/ | grep ^l | tr -s " " | cut -d" " -f9 | grep -v "lo"
#
#### Step [Optional]
## If NIC card is UP or Down: cat /sys/class/net/eth0/carrier # 1 is UP , 0 is DOWN
#
#### Get Each NIC TX(Transmitted Traffic/Send from this NIC) & RX(Received On this NIC)
#cat /sys/class/net/eth0/statistics/rx_bytes
#cat /sys/class/net/eth0/statistics/tx_bytes

function BYTES_TO_HR() {
  local SIZE=$1
  local UNITS="B KB MB GB TB PB"
  for F in $UNITS; do
    local UNIT=$F
    test ${SIZE%.*} -lt 1024 && break;
    SIZE=$(echo "$SIZE / 1024" | bc -l)
  done

  if [ "$UNIT" == "B" ]; then
    printf "%4.0f%s\n" $SIZE $UNIT
  else
    printf "%7.02f%s\n" $SIZE $UNIT
  fi
}

function BYTES_TO_HR() {
  local SIZE=$1
  SIZE=$(( ${SIZE}*8 ));
  local UNITS="b Kb Mb Gb Tb Pb"
  for F in $UNITS; do
    local UNIT=$F
    test ${SIZE%.*} -lt 1024 && break;
    SIZE=$(echo "$SIZE / 1024" | bc -l)
  done

  if [ "$UNIT" == "b" ]; then
    printf "%4.0f%s\n" $SIZE $UNIT
  else
    printf "%7.02f%s\n" $SIZE $UNIT
  fi
}


# New Dict Kindof Array
declare -A NIC_DICT

ALL_NIC=$(ls -l /sys/class/net/ | grep ^l | tr -s " " | cut -d" " -f9 | grep -v "lo")

for ONE_NIC in ${ALL_NIC};
do
    START_RX_BYTES=$(cat /sys/class/net/${ONE_NIC}/statistics/rx_bytes);
    START_TX_BYTES=$(cat /sys/class/net/${ONE_NIC}/statistics/tx_bytes);
    NIC_DICT["${ONE_NIC}_RX"]=${START_RX_BYTES}
    NIC_DICT["${ONE_NIC}_TX"]=${START_TX_BYTES}
done

sleep 1s;

for ONE_NIC in ${ALL_NIC};
do
    NOW_RX_BYTES=$(cat /sys/class/net/${ONE_NIC}/statistics/rx_bytes);
    NOW_TX_BYTES=$(cat /sys/class/net/${ONE_NIC}/statistics/tx_bytes);
    SPEED_RX=$(echo $(( $NOW_RX_BYTES - ${NIC_DICT["${ONE_NIC}_RX"]} )) | bc);
    SPEED_TX=$(echo $(( $NOW_TX_BYTES - ${NIC_DICT["${ONE_NIC}_TX"]} )) | bc);
    SPEED_RX_CALC=$(BYTES_TO_HR ${SPEED_RX})
    SPEED_TX_CALC=$(BYTES_TO_HR ${SPEED_TX})

    TOTAL_SPEED=$(( ${SPEED_RX} + ${SPEED_TX} ));
    TOTAL_SPEED_CALC=$(BYTES_TO_HR ${TOTAL_SPEED});
    printf "%-30s| %-20s%-20s%-20s%-20s\n" "NIC:[${ONE_NIC}]" "RX: ${SPEED_RX_CALC}" "TX: ${SPEED_TX_CALC}" "TOTAL: ${TOTAL_SPEED_CALC}"
done
