#!/bin/bash
# E12
# 10, 12, 15, 18, 22, 27, 33, 39, 47, 56, 68, 82
# E24:
# 10, 11, 12, 13, 15, 16, 18, 20, 22, 24, 27, 30, 33, 36, 39, 43, 47, 51, 56, 62, 68, 75, 82, 91

bb9=
for aa1 in 10  12  15  18  22  27  33  39  47  56  68  82
#for aa1 in 10  11  12  13  15  16  18  20  22  24  27  30  33  36  39  43  47  51  56  62  68  75  82  91
do
    bb1=$(( ${aa1} * 10 ))
    bb2=$(( ${aa1} * 100 ))
    bb3=$(( ${aa1} * 1000 ))
    bb4=$(( ${aa1} * 10000 ))

    bb9="${bb9} ${aa1} ${bb1} ${bb2} ${bb3} ${bb4}"
done

echo ${bb9} > /dev/stderr
for aa1 in ${bb9}
do
    echo -n "<${aa1}> " > /dev/stderr
done ; echo 

down0H=6.015    # 40 Ceies degree
down0L=26.30    # 0 Ceies 
for aa1 in ${bb9} ; do 
    for aa2 in ${bb9} ; do 
        up=${aa1}
        down1=${aa2}
        down2H=`bc -l <<< "${down1}*${down0H}/(${down1}+${down0H})"`
        down2L=`bc -l <<< "${down1}*${down0L}/(${down1}+${down0L})"`
        splitH=`bc -l <<< "${down2H}/(${down2H}+${up})"`
        splitL=`bc -l <<< "${down2L}/(${down2L}+${up})"`
        #diffH=`bc -l <<< "(${splitH}-.481)"`
        #diffL=`bc -l <<< "(${splitL}-.708)"`
        diffH2=$(echo `bc -l <<< "(${splitH}-.481)^2 * 1000000"`|sed -e 's;\..*;;g')0
        diffL2=$(echo `bc -l <<< "(${splitL}-.708)^2 * 1000000"`|sed -e 's;\..*;;g')0
        diffF1=$(( ${diffH2} + ${diffL2} ))
        diffF2=$(( ${diffH2} - ${diffL2} ))
        diffK1=$(( ${diffF1} * ${diffF1} ))
        diffK2=$(( ${diffF1} * ${diffF1} ))
        echo "diffF1 : Rup , Rdown1 , RdownH, RdownL , splitH, splitL , diffH diffL , diffF1"
        echo ${diffK2} ${up} ${down1}  ${down2H} ${down2L} ${splitH} ${splitL} ${diffH2}  ${diffL2} ${diffF1} ${diffF2} ${diffK1}  ${diffK2} 
    done
done
cat > /dev/stderr << EOF1

cat 3.txt |grep -v ^diff |sort -n -k1 > 5.txt

EOF1
