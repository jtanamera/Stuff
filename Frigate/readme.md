
Install docker on LXC using proxmox helper script

```
bash -c "$(wget -qLO - https://github.com/tteck/Proxmox/raw/main/ct/docker.sh)"

```

settings
Debian 12
4gb Ram
64gb HD
2CPU
Choose no for portainer, yes for docker compose

on Proxmox, edit the file 122.conf

```
nano /etc/pve/lxc/122.conf
```

```
arch: amd64
cores: 2
features: keyctl=1,nesting=1
hostname: frigate4
memory: 4096
net0: name=eth0,bridge=vmbr0,hwaddr=0A:BD:95:78:7B:C7,ip=dhcp,type=veth
onboot: 1
ostype: debian
rootfs: SSD:vm-122-disk-0,size=64G
swap: 1024
lxc.cgroup2.devices.allow: c 189:* rwm
lxc.mount.entry: /dev/bus/usb/002/005 dev/bus/usb/002/005 none bind,optional,create=file 0, 0
lxc.mount.entry: /dev/bus/usb/002/002 dev/bus/usb/002/002 none bind,optional,create=file 0, 0
lxc.mount.entry: /dev/bus/usb/002/003 dev/bus/usb/002/003 none bind,optional,create=file 0, 0
lxc.mount.entry: /dev/dri/renderD128 dev/dri/renderD128 none bind,optional,create=file 0, 0
lxc.apparmor.profile: unconfined
lxc.cgroup2.devices.allow: a
lxc.cap.drop: 
```



create docker-compose.yml file

```

services:
  frigate:
    container_name: frigate
    privileged: true # this may not be necessary for all setups
    restart: unless-stopped
    image: ghcr.io/blakeblackshear/frigate:stable
    shm_size: "164mb" # update for your cameras based on calculation above
    devices:
      - /dev/bus/usb:/dev/bus/usb # passes the USB Coral, needs to be modified for other versions
      - /dev/dri/renderD128 # for intel hwaccel, needs to be updated for your hardware
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - /home:/config
      - /media/frigate:/media/frigate
      - type: tmpfs # Optional: 1GB of memory, reduces SSD/SD Card wear
        target: /tmp/cache
        tmpfs:
          size: 1000000000
    ports:
      - "5000:5000"
      - "8554:8554" # RTSP feeds
      - "8555:8555/tcp" # WebRTC over tcp
      - "8555:8555/udp" # WebRTC over udp
    environment:
      FRIGATE_RTSP_PASSWORD: "PASSWORD"
```

```
docker compose up -d

```

in Frigate Configuration editor, edit the following based on your cameras

```
mqtt:
  enabled: false

cameras:
  name_of_your_camera: # <------ Name the camera
    enabled: true
    ffmpeg:
      inputs:
        - path: rtsp://10.0.10.10:554/rtsp # <----- The stream you want to use for detection
          roles:
            - detect
    detect:
      enabled: false # <---- disable detection until you have a working camera feed
      width: 1280
      height: 720
version: 0.14
```

example

```
mqtt:
  host: 192.168.2.16
  user: mosquitto
  password: PASSWORD


record:
  enabled: True
  retain:
    days: 7
    mode: motion
  events:
    retain:
      default: 30
      mode: motion

snapshots:
  enabled: True
  timestamp: true
  clean_copy: true
  bounding_box: true
  retain:
    default: 30

go2rtc:
  streams:
     # High res main stream name
    sunroom_cam:
      - "ffmpeg:rtsp://administrator:PASSWORD@192.168.30.102:554/stream1#video=copy#audio=copy#audio=aac"
     # Low res sub stream name
    sunroom_cam_sd:
      - rtsp://administrator:PASSWORD@192.168.30.102:554/stream2

cameras:
  doorbell_cam:
    enabled: true
    ffmpeg:
      inputs:
        - path: rtsp://admin:PASSWORD@192.168.30.101:8554/Streaming/Channels/102
          roles:
            - detect
    detect:
      enabled: true
    objects:
      track:
        - person
        - dog
        - car
        - cat

  backyard_cam:
    enabled: true
    ffmpeg:
      inputs:
        - path: 
            rtsp://administrator:PASSWORD@192.168.30.93:554/cam/realmonitor?channel=1&subtype=00
          roles:
            - detect
    detect:
      enabled: true
    objects:
      track:
        - person
        - dog
        - car
        - cat

  sunroom_cam:
    ffmpeg:
      output_args:
        record: preset-record-generic-audio-copy
      inputs:
        - path: rtsp://192.168.30.102:8554/stream1
          input_args: preset-rtsp-restream
          roles:
            - record
        - path: rtsp://192.168.30.102:8554/stream2
          input_args: preset-rtsp-restream
          roles:
            - detect 
    detect:
      width: 640 
      height: 360
      fps: 5
    enabled: true
    objects:
      track:
        - person
        - dog
        - car
        - cat

  backyard_west:
    enabled: true
    ffmpeg:
      input_args: ''
      inputs:
        - path: http://192.168.30.103:8080  #ESp32 camera location  
          roles:
            - detect
            - record
      output_args:
        record: -f segment -pix_fmt yuv420p -segment_time 10 -segment_format mp4 -reset_timestamps
          1 -strftime 1 -c:v libx264 -preset ultrafast -an
    objects:
      track:
        - person
        - dog
        - car
        - cat
    detect:
      enabled: true
     # width: 800  
     # height: 600  
     # fps: 20      #Adjust the fps based on what suits your hardware.  

  backyard_east:
    enabled: false
    ffmpeg:
      input_args: ''
      inputs:
        - path: http://192.168.30.104:8080  #ESp32 camera location  
          roles:
            - detect
            - record
      output_args:
        record: -f segment -pix_fmt yuv420p -segment_time 10 -segment_format mp4 -reset_timestamps
          1 -strftime 1 -c:v libx264 -preset ultrafast -an
    objects:
      track:
        - person
        - dog
        - car
        - cat
    detect:
      enabled: true
      # width: 800  
      # height: 600  
      #fps: 20      #Adjust the fps based on what suits your hardware.  

detectors:
  coral:
    type: edgetpu
    device: usb

version: 0.14

```
