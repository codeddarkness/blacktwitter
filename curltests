#!/usr/bin/env bash 

echo "# curl localhost:8000/login_backup" > web.tests 
curl localhost:8000/login_backup >> web.tests 

echo -e "\n# curl localhost:8000/simple_login" >> web.tests 
curl localhost:8000/simple_login >> web.tests 
echo -e "\n# curl localhost:8000" >> web.tests 
curl localhost:8000 >> web.tests 

echo -e "\n# curl localhost:8000/no_csrf_login" >> web.tests 
curl localhost:8000/no_csrf_login >> web.tests 

cat web.tests 
