import socketserver
import os
import json
serverName = 'localhost'
serverPort = 12000
ip_port = (serverName, serverPort)
print("服务器已启动")
class MyServer(socketserver.BaseRequestHandler):
    def handle(self):
        base_path = 'F:\Desktop\大三下作业实验\计网\实验\服务器接收文件'
        conn = self.request
        while True:
            op = conn.recv(1024).decode()
            if(op=="u"):
                file_inf = conn.recv(1024).decode()

                # 获取请求方法、文件名、文件大小
                file_name, file_size = file_inf.split('|') #分割 文件名和大小

                id=1
                while (os.path.exists(base_path + '/' + file_name)):
                    file_name='1'+file_name
                    id+=1
                if (id!=1):
                    mess="文件重复，已经重命名为 "+file_name
                    print('收到文件名：命名重复，新名称为：', file_name)
                else:
                    mess="等待文件传输"
                    print('收到文件名：', file_name)
                conn.send(mess.encode())
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
                        data = conn.recv(1024)
                        recv_size += len(data)
                        # 写入文件
                        f.write(data)
                    # 上传完毕，则退出循环
                    else:
                        recv_size = 0
                        Flag = False
                msg = "Upload successed."
                print(msg)
                conn.sendall(msg.encode())
                f.close()
            elif op =="d":#请求下载
                pre_data = conn.recv(1024).decode()

                if (os.path.exists(base_path + '/' + pre_data)):
                    conn.send("yes".encode())
                else:
                    conn.send("no".encode())
                    print("请求文件不存在")
                    continue
                path = base_path+ '/' + pre_data
                file_size = os.path.getsize(path)
                # 发送文件名 和 文件大小u
                Informf = (str(pre_data) + '|' + str(file_size))

                conn.sendall(Informf.encode())

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
                    conn.send(data)
                conn.recv(1024)
                f.close()
            elif op =='c':
                pre_data= conn.recv(1024)
                print("收到客户信息：",pre_data.decode())
                conn.send('确认收到！'.encode())
            elif op=="ls":
                for root, dirs, files in os.walk(base_path + '/' ):
                    # 当前目录路径
                    root_inf = json.dumps(root)
                    conn.send(root_inf.encode())
                    conn.recv(1024)
                    # 当前路径下所有子目录
                    dirs_inf = json.dumps(dirs)
                    conn.send(dirs_inf.encode())
                    conn.recv(1024)
                    files_inf = json.dumps(files)
                    conn.send(files_inf.encode())
                    conn.recv(1024)

if __name__ == '__main__':
    instance = socketserver.ThreadingTCPServer(ip_port, MyServer)
    instance.serve_forever()
