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
done ; echo > /dev/stderr

down0H=6015     # 40 Ceies degree : 6.015 k
down0L=26300    #  0 Ceies degree : 26.3  k
targetH=0.481
targetL=0.708
for aa1 in ${bb9} ; do 
    for aa2 in ${bb9} ; do 
        Rup=${aa1}
        Rdown1=${aa2}
        Rdown2H=`bc -l <<< "${Rdown1}*${down0H}/(${Rdown1}+${down0H})"`
        Rdown2L=`bc -l <<< "${Rdown1}*${down0L}/(${Rdown1}+${down0L})"`
        VsplitH=`bc -l <<< "${Rdown2H}/(${Rdown2H}+${Rup})"`
        VsplitL=`bc -l <<< "${Rdown2L}/(${Rdown2L}+${Rup})"`
        VdiffH=$(printf "%8.5f" `bc -l <<< "sqrt((${VsplitH}-${targetH})^2)*100"`)
        VdiffL=$(printf "%8.5f" `bc -l <<< "sqrt((${VsplitL}-${targetL})^2)*100"`)
        diffH2=$(printf "%8.0f" `bc -l <<< "((${VsplitH}-${targetH})^2)*1000000"`)
        diffL2=$(printf "%8.0f" `bc -l <<< "((${VsplitL}-${targetL})^2)*1000000"`)
        test ${diffH2} -lt ${diffL2} \
            && diffF1=$(( ${diffL2} - ${diffH2} )) \
            || diffF1=$(( ${diffH2} - ${diffL2} ))
        diffF2=$(( ${diffH2} + ${diffL2} ))
        echo ${diffF1} ${diffF2} : Rup ${Rup} , Rdown1 ${Rdown1} , down0H ${down0H} Rdown2H ${Rdown2H} , \
            down0L ${down0L} Rdown2L ${Rdown2L} : \
            VsplitH ${VsplitH} VsplitL ${VsplitL} , \
            VdiffH ${VdiffH}  VdiffL ${VdiffL} : \
            diffH2 ${diffH2}  diffL2 ${diffL2} : \
            diffF1 ${diffF1} diffF2 ${diffF2} 
    done
done

#cat 3.txt |grep -v ^diff |sort -n -k1 > 51.txt

cat > /dev/stderr << EOF1

cat 3.txt |grep -v ^diff |sort -n -k2 > 52.txt

EOF1
