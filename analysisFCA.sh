#!/usr/bin/env bash

# SGE Options

#It's a bash file
#$ -S /bin/bash

#Job's Name
#$ -N mel-concept-pyth

#Mail to send informations
#$ -M meline.wery@irisa.fr

#Options
#$ -m beas

# Run python3
#. /softs/local/env/envpython-3.3.2.sh
usage="Usage: ./analysisFCA.sh -d [Directory] -s [Signature File]\n\n

where:\n
    \t -h  show help text\n
    \t -d  directory to save all results\n
    \t -s  Signature file\n"


POSITIONAL=()
if [[ $# -eq 1 ]]; then
    if [[ $1 == '-h' ]]; then
        echo -e $usage
        exit
    else
        echo "Missing some arguments."
        echo -e $usage
        exit
    fi
elif [[ $# -lt 4 || $# -gt 4 ]]; then
    echo "Error in the arguments"
    echo -e $usage
    exit
fi


while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    -d|--directory)
    Dir="$2"
    shift # past argument
    shift # past value
    ;;
    -s|--signature)
    Sign="$2"
    shift # past argument
    shift # past value
    ;;
    *)    # unknown option
    POSITIONAL+=("$1") # save it in an array for later
    echo -e $usage
    shift # past argument
    ;;
esac
done
set -- "${POSITIONAL[@]}" # restore positional parametersr


#Data
protdata=./$Dir/matricemutantProtTab.csv
mutdata=./$Dir/matricemutantWTKOE1Tab.csv
#signature=signature_drug.txt


# Put your Science related commands here
#Dir=${1:?"A Directory is required. Usage: ./analysisFCA.sh [Directory] [Signature File]"}
#Signature=${2:?"A Signature File is required. Usage: ./analysisFCA.sh [Directory] [Signature File]"}
#echo "Debut"
cp $Sign $Dir

python3 ./scripts/class_canoniq_hybrid.py $protdata $mutdata $Dir/$Sign
python3 ./scripts/analysisPythResults.py $Dir
