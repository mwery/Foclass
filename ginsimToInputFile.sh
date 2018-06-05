#!/bin/bash

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

usage="Usage: ./ginsimToInputFile.sh -d|--directory [Directory] -a|--archive [GINsim Archive] -o|--option [Options]\n\n

where:\n
    \t -h  show help text\n
    \t -d  directory to save all results\n
    \t -a  GINsim archive\n
    \t -o  type of option :\n
            \t\t r :  No input environment - no initialState AND Remove input in the stable state value\n
            \t\t ri : With input environment - no initialState AND Remove input in the stable state value\n
            \t\t riis : With input environment - with initialState AND Remove input in the stable state value\n
            \t\t ris : No input environment - with initialState AND Remove input in the stable state value\n
            \t\t k : No input environment - no initialState AND Keep input in the stable state value\n
            \t\t ki : With input environment - no initialState AND Keep input in the stable state value\n
            \t\t kiis : With input environment - with initialState AND Keep input in the stable state value\n
            \t\t kis : No input environment - with initialState AND Keep input in the stable state value\n"



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
elif [[ $# -lt 6 || $# -gt 6 ]]; then
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
    -a|--archive)
    Arc="$2"
    shift # past argument
    shift # past value
    ;;
    -o|--option)
    opt="$2"
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
fullfile=$Dir/matricemutantFullTab.csv
# Put your Science related commands here
#Dir=${1:?"A Directory is required. Usage: ./ginsimToInputFile.sh -d|--directory [Directory] -a|--archive [GINsim Archive] -o|--option [Options]"}
#Arc=${2:?"A GINsim archive is required. Usage: ./ginsimToInputFile.sh -d|--directory [Directory] -a|--archive [GINsim Archive] -o|--option [Options]"}


#echo "Directory is $Dir"
#echo "Ginsim File is $Arc"
if [ ! -d "$Dir" ]; then
  # Control will enter here if $DIRECTORY doesn't exist.
  mkdir $Dir
fi

case $opt in
    r)
    python3 ./scripts/analysisGINsimRemInput.py $Arc $Dir
    ;;
    ri)
    python3 ./scripts/analysisGINsimSpecRemInput.py $Arc $Dir
    ;;
    riis)
    python3 ./scripts/analysisGINsimSpecRemInputInitialState.py $Arc $Dir
    ;;
    ris)
    python3 ./scripts/analysisGINsimRemInputInitialState.py $Arc $Dir
    ;;
    k)
    python3 ./scripts/analysisGINsimKeepInput.py $Arc $Dir
    ;;
    ki)
    python3 ./scripts/analysisGINsimSpecKeepInput.py $Arc $Dir
    ;;
    kiis)
    python3 ./scripts/analysisGINsimSpecKeepInputInitialState.py $Arc $Dir
    ;;
    kis)
    python3 ./scripts/analysisGINsimKeepInputInitialState.py $Arc $Dir
    ;;
esac



cp $Arc $Dir
python3 ./scripts/splitFull_KOE1.py $fullfile
python3 ./matrix_FCA.py $Dir/matricemutantProtTab.csv
