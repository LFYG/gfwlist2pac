# A Python script for converting gfwlist to autoconfig pac file

Command line help:  
  
```
usage: gfwlist2pac.py [-h] [-t {PROXY,SOCKS5,SOCKS4,SOCKS}] [-a ADDR] -p PORT  
                      [-g] [-s] [-o OUTPUT]  
                      [USERFILE [USERFILE ...]]  
  
positional arguments: 
  USERFILE              user provided gfwlist compatible file(s)  
  
optional arguments:  
  -h, --help            show this help message and exit  
  -t {PROXY,SOCKS5,SOCKS4,SOCKS}, --proxy-type {PROXY,SOCKS5,SOCKS4,SOCKS}  
                        proxy server type, use PROXY(http) or SOCKS5 (default:  
                        SOCKS5)  
  -a ADDR, --proxy-addr ADDR  
                        proxy server address (default: 127.0.0.1)  
  -p PORT, --proxy-port PORT  
                        proxy server listening port  
  -g, --fetch-gfwlist   fetch gfwlist from https://raw.githubusercontent.com/  
                        gfwlist/gfwlist/master/gfwlist.txt  
  -s, --shexpmatch      use own shExpMatch, instead of depending on the host  
                        implementation  
  -o OUTPUT, --output OUTPUT  
                        output file (default: autoconfig.pac)  
```

### Further explanation for the arguments:  

- `-a` : the default is 127.0.0.1, if you want to share your proxy, use 0.0.0.0.  
- `-p` : no default, but it's usually 1080 for SS.  
- `-s` : use my own implementation of [shExpMatch](https://gist.github.com/meoow/e74946245a74116a0d0a01e98dcba962) function for wildcard matching, in case the target application doesn't have a built-in one which actually happens sometimes.  
- `USERFILE` : user can privode file with extra url list in the same syntax of gfwlist.  

