import socket
import os
import json
serverName = 'localhost'
serverPort = 12000

ip_port = (serverName, serverPort)
sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sk.connect(ip_port)
base_path="F:\Desktop\大三下作业实验\计网\实验\客户端发送文件/" #客户端文件位置
while True:
    op = input("请选择功能：（u）文件传输 （d）文件下载 (c) 发消息 (ls) 列出服务器文件 （ls-l) 列出本地文件（q）退出 ");
    if op == "u":
        file_name = input('输入文件名(含后缀）：')
        path = base_path + file_name
        if (not os.path.exists(path)):
            print("本地文件不存在")
            continue
        sk.send(op.encode())

        # 客户端输入要上传文件的路径
        # 获取文件大小
        file_size = os.path.getsize(path)
        # 发送文件名 和 文件大小u
        Informf = (str(file_name) +'|'+ str(file_size))
        sk.send(Informf.encode())
        # 为了防止粘包，将文件名和大小发送过去之后，等待服务端收到，直到从服务端接受一个信号（说明服务端已经收到）
        print(sk.recv(1024).decode())
        #指定了缓冲区的大小为1024字节，因此需要对于文件循环读取，直到文件的数据填满了一个缓冲区，此时将缓冲区数据发送出去，
        # 继续读取下一部分文件；或是当缓冲区未填满，而文件读取完毕，此时应当将这个未满的缓冲区发送给服务器。
        send_size = 0
        f = open(path, 'rb')
        Flag = True
        while Flag:
            if send_size + 1024 > file_size:
                data = f.read(file_size - send_size)
                Flag = False
            else:
                data = f.read(1024)
                send_size += 1024
            sk.send(data)
        msg = sk.recv(1024)
        print(msg.decode())
        f.close()
        print()
    elif op == 'd':
        sk.send(op.encode())
        file_name = input('输入文件名(含后缀）：')
        sk.send(file_name.encode())

        path = base_path + file_name
        ans = sk.recv(1024).decode()
        if ( ans == "no"):
            print("服务器中找不到该文件")
            continue

        file_inf = sk.recv(1024).decode()
        # 获取请求方法、文件名、文件大小
        file_name, file_size = file_inf.split('|')  # 分割 文件名和大小

        id = 1
        while (os.path.exists(base_path + '/' + file_name)):
            file_name = '1' + file_name
            id += 1
        if (id != 1):
            print('收到文件名重复,已重命名为：', file_name)
        # 已经接收文件的大小
        recv_size = 0
        # 上传文件路径拼接
        file_dir = os.path.join(base_path, file_name)
        f = open(file_dir, 'wb')
        Flag = True
        while Flag:
            # 未上传完毕，
            if int(file_size) > recv_size:
                # 最多接收1024，可能接收的小于1024
                data = sk.recv(1024)
                recv_size += len(data)
                # 写入文件
                f.write(data)
            # 上传完毕，则退出循环
            else:
                recv_size = 0
                Flag = False
        msg = "Download successed."
        print(msg)
        sk.sendall(msg.encode())
        f.close()
        print()
    elif op=='ls':
        sk.sendall(op.encode())
        json_string = json.loads(sk.recv(1024).decode())
        print("服务器根目录：",json_string)
        sk.send("ok".encode())
        # 防止粘包，给客户端发送一个信号。
        # 当发送内容较大时，由于服务器端的recv（buffer_size）方法中的buffer_size较小，不能一次性完全接收全部内容，
        # 因此在下一次请求到达时，接收的内容依然是上一次没有完全接收完的内容，因此造成粘包现象。
        json_string = json.loads(sk.recv(1024).decode())
        print("根目录下文件夹：",json_string)
        sk.send("ok".encode())
        json_string = json.loads(sk.recv(1024).decode())
        print("目录下文件：", json_string)
        sk.send("ok".encode())
        print()
    elif op=="ls-l":
        for root, dirs, files in os.walk(base_path):
            # 当前目录路径
            print(root)
            # 当前路径下所有子目录
            print(dirs)
            # 当前路径下所有非目录子文件
            print(files)
            print()
    elif op=="c":
        sk.send(op.encode())
        messa=input("请输入消息：")
        sk.send(messa.encode())
        print('服务器回应：',sk.recv(1024).decode())

    elif op=='q':
        print("连接断开")
        break
    else:
        print('功能选择有误，请重输！')
        continue
sk.close()
