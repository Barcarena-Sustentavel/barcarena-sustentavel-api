#/bin/sh
userName=$(whoami) 
file_name=".cache/pypoetry/virtualenvs/barcarena-sustentavel-api-HY_lHiAc-py3.10/bin/activate"
file_path=$(find / -name "$file_name" 2>/dev/null)

source /home/"$userName"/"$file_name"
TIPO='development'
uvicorn --port 8081 main:app --reload

