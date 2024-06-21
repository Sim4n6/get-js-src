#!/bin/bash

# retrieve the arguments
if [ ! $# -eq 2 ]; then
  echo "Usage: $0 <url> <directory>"
  exit 1
fi

url=$1
# append the number of the day in the year 
directory="$2-$(date +%j)"

# create directory if it doesn't exist
if [ ! -d "./targets/$directory/js_files" ]; then
  mkdir -p "./targets/$directory/js_files"
fi

# download the target JS file
# echo "$url" | getJS --resolve --verbose --complete --insecure | tee "./targets/$directory/js.files" | sort -u | wget -N -P "./targets/$directory/js_files/" -i -
python3 getjssrc.py "$url" "./targets/$directory/js_files/"

# rename if necessary 
for jsfile in $(ls ./targets/$directory/js_files); do
  mv "./targets/$directory/js_files/$jsfile" "./targets/$directory/js_files/$(basename $jsfile | cut -d'?' -f1)"
done

# beautify the target JS file
for jsfile in $(ls ./targets/$directory/js_files); do
  js-beautify --replace  "./targets/$directory/js_files/$jsfile"
done

# create CodeQL database
if [ ! -d "./targets/$directory/codeql-database" ]; then
  rm -rf "./targets/$directory/codeql-database"
fi
codeql database create "./targets/$directory/codeql-database" --threads=0 --overwrite --language=javascript --source-root "./targets/$directory/js_files/"

# analyze the target JS file
CODEQL_SUITES_PATH=$HOME/Codeql-Home/codeql-repo/javascript/ql/src/codeql-suites
# --sarif-add-snippets 
codeql database analyze --threads=0 --ram=16384 --format=sarif-latest --output="./targets/$directory/results-$directory.sarif" --  "./targets/$directory/codeql-database" "$CODEQL_SUITES_PATH/javascript-security-extended.qls"
#codeql database analyze --threads=8 --format=sarif-latest --output="./targets/$directory/codeql-results.sarif" --  "./targets/$directory/codeql-database" "$CODEQL_SUITES_PATH/javascript-security-experimental.qls"
