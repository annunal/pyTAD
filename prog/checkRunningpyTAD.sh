#. /home/critechuser/.bashrc

file_age() {
    local filename=$1
    echo $(( $(date +%s) - $(date -r $filename +%s) ))
}

is_stale() {
    local filename=$1
    local max_minutes=20
    [ $(file_age $filename) -gt $(( $max_minutes*60 )) ]
}

type=$1
dir=$2

FILE=$dir/running.txt
echo $FILE

echo $(file_age $FILE)
if test -f "$FILE"; then
    if is_stale $FILE; then
        echo 'old'
        rm $FILE
    else
        echo 'not old'
    fi
fi
if test -f "$FILE"; then
    echo "$FILE exists. aborting"
else
    touch $FILE
    echo "python3 /home/pyTAD/programs/pyTAD/checkRunningpyTAD.py "$type" /home/pyTAD/programs/DATA/"$dir
    python3 /home/pyTAD/programs/pyTAD/checkRunningpyTAD.py  $type /home/pyTAD/programs/DATA/$dir
    echo 'removing '$FILE
    rm $FILE
fi
    
