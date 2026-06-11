This project works only for minimserver.
# **server:**
1. Modify the configuration file at `/upotserver/settings.json`.
   
   **Must Replace:**
   * `minimserver_ip`: Your own Minimserver IP address.
   * `server_ip`: Your own public IP address.
   * `port`: Your service port.
     * *Note: If you change this port, you must also update the `EXPOSE` value in `/upotserver/docker_related/Dockerfile_ver1`.*

   **Optional Fields:**
   * `account` / `password`: The credentials required by your Foobar2000.
   * `friendlyName`: The display name that appears on the internet.
   * `UDN`: The unique ID that Foobar2000 looks for.
        

### **docker:**
1. you may want to change your image name in .env file and your container name in docker-compose.yml
2. for building docker image, you need a Dockerfile
docker build -t <image name> . --no-cache 
3. for running a container, you need a docker-compose.yml
docker-compose up -d


# **client:**
1.install foo_upnp to your foobar
2.go to View->UPnp Browser 
3.right click and click Add remote internet Upnp Server...
4.type in your public ip to Host and account, password

---
### checking log
docker-compose logs --tail=100
### get in docker container
docker exec -it <container name> /bin/bash
### remove container
docker rm <container name>
#remoce image
docker rmi <image name>
### tool might use full
apt-get update
apt-get install net-tools
netstat -tulpn | grep :58055
apt-get install procps
ps a