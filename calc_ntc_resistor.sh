#!/bin/bash
down0H=6015     # 40 Ceies degree : 6.015 k
down0L=26300    #  0 Ceies degree : 26.3  k
targetH=0.481
targetL=0.708

bb9=
#  E12
#for aa1 in 10  12  15  18  22  27  33  39  47  56  68  82
#  E24
#for aa1 in 10  11  12  13  15  16  18  20  22  24  27  30  33  36  39  43  47  51  56  62  68  75  82  91
#  E48
#for aa1 in 10.0  10.5  11.0  11.5  12.1  12.7  13.3  14.0  14.7  15.4  16.2  16.9  17.8  18.7  19.6  20.5  21.5  22.6  23.7  24.9  26.1  27.4  28.7  30.1  31.6  33.2  34.8  36.5  38.3  40.2  42.2  44.2  46.4  48.7  51.1  53.6  56.2  59.0  61.9  64.9  68.1  71.5  75.0  78.7  82.5  86.6  90.9  95.3
#  E96
for aa1 in 10.0  10.2  10.5  10.7  11.0  11.3  11.5  11.8  12.1  12.4  12.7  13.0  13.3  13.7  14.0  14.3  14.7  15.0  15.4  15.8  16.2  16.5  16.9  17.4  17.8  18.2  18.7  19.1  19.6  20.0  20.5  21.0  21.5  22.1  22.6  23.2  23.7  24.3  24.9  25.5  26.1  26.7  27.4  28.0  28.7  29.4  30.1  30.9  31.6  32.4  33.2  34.0  34.8  35.7  36.5  37.4  38.3  39.2  40.2  41.2  42.2  43.2  44.2  45.3  46.4  47.5  48.7  49.9  51.1  52.3  53.6  54.9  56.2  57.6  59.0  60.4  61.9  63.4  64.9  66.5  68.1  69.8  71.5  73.2  75.0  76.8  78.7  80.6  82.5  84.5  86.6  88.7  90.9  93.1  95.3 
do
    bb1=$( bc -l <<< "${aa1} * 10" )
    bb2=$( bc -l <<< "${aa1} * 100" )
    bb3=$( bc -l <<< "${aa1} * 1000" )
    bb4=$( bc -l <<< "${aa1} * 10000" )

    bb9="${bb9} ${aa1} ${bb1} ${bb2} ${bb3} ${bb4}"
done

echo ${bb9} > /dev/stderr
for aa1 in ${bb9}
do
    echo -n "<${aa1}> " > /dev/stderr
done ; echo > /dev/stderr

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
