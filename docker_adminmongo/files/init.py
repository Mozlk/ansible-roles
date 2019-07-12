#!/usr/bin/python

import pymongo
import random,string
import os
import json

os.system('systemctl restart mongod')

new_password = ''.join(random.sample(string.ascii_letters + string.digits, 8))

username = 'root'

with open('/credentials/password.txt','r') as f:
  old_password = f.read().split(':')[1].replace('\n','')

client = pymongo.MongoClient("mongodb://%s:%s@127.0.0.1/" % (username, old_password))
db =  client['admin']
db.add_user(username,new_password)

# change adminmongo
docker_id = os.popen("docker inspect $(docker ps -q) | grep Id | awk -F ':' '{print $2}' | awk -F '\"' '{print $2}'").read().replace("\n", "")
os.system('systemctl stop docker')
config_path = "/var/lib/docker/containers/%s/config.v2.json" %(docker_id)

with open(config_path,'r') as f:
  config = json.load(f)
  config['Config']['Env'].remove('PASSWORD=admin')
  config['Config']['Env'].append('PASSWORD=%s'%(new_password))

with open(config_path,'w') as f:
  json.dump(config,f)

os.system('systemctl start docker')


with open('/credentials/password.txt','w') as f:
  f.write('MySQL Password:%s\n'%(new_password))
  f.write('adminMongo Password:%s\n'%(new_password))

with open("/etc/rc.local","r") as f:
  lines = f.readlines()
with open("/etc/rc.local","w") as f_w:
  for line in lines:
    if "/root/init.py" in line:
      continue
    f_w.write(line)

os.remove('/root/init.py')