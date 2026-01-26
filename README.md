# env

## on windows 
C:\Users\swapa\.wslconfig

```
[wsl2]
networkingMode=Mirrored
```

## on Linux host

etc /etc/wsl.conf

```
systemd=true

[user]
default=swapanc

[network]
generateResolvConf = false
```

/etc/resolv.conf

```
nameserver 8.8.8.8
nameserver 8.8.4.4
```

## restart wsl and test dns lookup

```
wsl --shutdown
wsl
ping -c 3 google.com
```
