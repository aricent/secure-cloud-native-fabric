old_ip=SCF_IP
new_ip=`/sbin/ifconfig eth0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}'`
new_path="$PWD"
old_path="PROJ_PATH"

find ./scf_agent -type f -exec sed -i -e "s/$old_ip/$new_ip/g" {} \;
find ./SCRM -type f -exec sed -i -e "s/$old_ip/$new_ip/g" {} \;
find ./extra -type f -exec sed -i -e "s/$old_ip/$new_ip/g" {} \;

sed -i "s~$old_path~$new_path~g" SCRM/util/elastic_search_client.py;
sed -i "s~$old_path~$new_path~g" SCRM/audit/auditor_service.py;
#find ./SecurityControllerFabric -type f -exec sed -i -e "s/$old_ip/$new_ip/g" {} \;
#find ./static/assets -type f -exec sed -i -e "s/$old_ip/$new_ip/g" {} \;
#find ./update_ip.sh -type f -exec sed -i -e "s/$old_ip/$new_ip/g" {} \;
#find ./templates -type f -exec sed -i -e "s/$old_ip/$new_ip/g" {} \;
