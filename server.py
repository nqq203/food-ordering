from os import access
from pkgutil import get_data
import socket 
import json 
import threading
from datetime import datetime
import time
import os 

#---------------------------------------------
HOST = '127.0.0.1'
PORT = 65432
FORMAT = 'utf8'


#-----SERVER-----
def getTime():
    now = datetime.now()
    date = datetime.today()

    curr_time = {}
    curr_time['hour'] = now.hour
    curr_time['minutes'] = now.minute
    curr_time['second'] = now.second

    curr_date = {}
    curr_date['day'] = date.day
    curr_date['month'] = date.month  
    curr_date['year'] = date.year

    return curr_time, curr_date

class Data: 
    def __init__(self, status, tableNumber, countAmount, moneyPrice, total, cardNumber):
        self.status = status
        self.tableNumber = tableNumber
        self.countAmount = countAmount
        self.moneyPrice = moneyPrice
        self.total = total
        self.cardNumber = cardNumber

    def getStatus(self):
        return self.status

    def getTableNumber(self):
        return self.tableNumber

    def getCountAmount(self):
        return self.countAmount

    def getMoneyPrice(self):
        return self.total

    def getCardNumber(self):
        return self.cardNumber

    def setStatus(self, status):
        self.status = status
    
    def setTableNumber(self, tableNumber):
        self.tableNumber = tableNumber
    
    def setCountAmount(self, countAmount):
        self.countAmount = countAmount
    
    def setMoneyPrice(self, moneyPrice):
        self.moneyPrice = moneyPrice
    
    def setTotal(self, total):
        self.total = total

    def setCardNumbeR(self, cardNumber):
        self.cardNumber = cardNumber
    
    def checkFile(self):
        time, date = getTime()
        filename = f"Data/{self.tableNumber}_{date['day']}.{date['month']}.{date['year']}.json"
        if os.path.isfile(filename) == True:
            with open (filename, "r") as read_file:
                data = json.load(read_file)
                read_file.close()
            return True, data
        else:
            data = None
            return False, data

    def updateDataBefore2Hours(self, data):
        time, date = getTime()
        hour_in_data = data["bill"]["time"]["hour"]
        hour_real_time = time["hour"]
        gap_time = abs(hour_real_time - hour_in_data)
        filename =  f"Data/{self.tableNumber}_{date['day']}.{date['month']}.{date['year']}_update.json"
            
        if gap_time < 2:
            data["bill"]["total money"] += self.total
            data["bill"]["card number"] += self.cardNumber
            index = 0
            for item in data["bill"]["milk tea"]:
                if (index > 3):
                    break
                item["amount"] += self.countAmount[index]
                item["into money"] += self.moneyPrice[index]
                index += 1
            index = 4
            for item in data["bill"]["topping"]:
                if (index > 7):
                    break
                item["amount"] += self.countAmount[index]
                item["into money"] += self.moneyPrice[index]
                index += 1
            with open (filename, "w") as write_file:
                json.dump(data, write_file, indent=2)
                write_file.close()

    def saveDataToJson(self):
        update_time, update_date = getTime()
        new_data = updateData()
        new_data["bill"]["date"] = update_date
        new_data["bill"]["time"] = update_time
        filename=f"Data/{self.tableNumber}_{update_date['day']}.{update_date['month']}.{update_date['year']}.json"
        with open (filename, 'w') as write_file:
            json.dump(new_data, write_file, indent= 2)
            write_file.close()
        
        def updateData():
            with open ('order.json', 'r') as f:
                data = json.load(f)
                f.close()
            data["bill"]["status"] = self.status
            data["bill"]["total money"] = self.total
            data["bill"]["card number"] = self.cardNumber
            data["bill"]["id"] = self.tableNumber
            index = 0
            for item in data["bill"]["milk tea"]:
                if (index > 3):
                    break
                item["amount"] = self.countAmount[index]
                item["into money"] = self.moneyPrice[index]
                index += 1 
            index = 4
            for item in data["bill"]["topping"]:
                if (index > 7):
                    break
                item["amount"] = self.countAmount[index]
                item["into money"] = self.moneyPrice[index]
                index += 1
            return data

class Server:
    def __init__(self, s):
        self.s = s
    
    def handleClient(self, conn: socket, addr):
        data = Data()
        print(addr, " has connected!!")
        click = conn.recv(1024).decode(FORMAT)
        print(addr, click)
        if (click == 'menu'):
            msg = 'download'
            conn.sendall(msg.encode(FORMAT))
            #RECEIVE TABLE NUMBER
            data.setTableNumber(recvTableNumber(conn))
            #RECEIVE COUNT AMOUNT
            data.setCountAmount(recvCountAmount(conn))
            #RECEIVE MONEY PRICE
            data.setMoneyPrice(recvMoneyPrice(conn))
            #RECEIVE TOTAL
            data.setTableNumber(recvTotal(conn))
            #RECEIVE CARD NUMBER
            data.setCardNumbeR(recvCardNumber(conn))
        click = conn.recv(1024).decode(FORMAT)
        print(addr, click)
        if (click == 'exit'):
            data.setStatus('unpaid')
        elif (click == 'money' or click == 'card'):
            data.setStatus('paid')
        #SPECTIAL FUNCTION
        #CHECK TABLE NUMBER, BEFORE 2 HOURS, STILL ORDER FOOD AND ADD NEW OREDR INTO THE BILL BEFORE
        valid, d = data.checkFile()
        if (valid == True):
            data.updateDataBefore2Hours(d)
        else:
            data.saveDataToJson()
        if (click):
            print(addr, "end")
        
        # FUNCTION RECEIVE INFORMATION FROM CLIENT 
        def recvTableNumber(conn):
            msg = conn.recv(1024).decode(FORMAT)
            tableNumber = int(msg)
            conn.sendall(str(msg).encode(FORMAT))
            return tableNumber
        
        def recvCountAmount(conn):
            countAmount = []
            msg = None
            while msg != "x":
                msg = conn.recv(1024).decode(FORMAT)
                if msg != "x":
                    self.countAmount.append(int(msg))
                conn.sendall(str(msg).encode(FORMAT))
            return countAmount
        
        def recvMoneyPrice(conn):
            moneyPrice = []
            msg = None
            while msg != "x":
                msg = conn.recv(1024).decode(FORMAT)
                if msg != "x":
                    moneyPrice.append(int(msg))
                conn.sendall(str(msg).encode(FORMAT))
            return moneyPrice
        
        def recvTotal(conn):
            msg = conn.recv(1024).decode(FORMAT)
            total = int(msg)
            conn.sendall(str(msg)).encode(FORMAT)
            return total

        def recvCardNumber(self, conn, server):
            msg = conn.recv(1024).decode(FORMAT)
            cardNumber = int(msg)
            conn.sendall(str(msg)).encode(FORMAT)
            return cardNumber

    def process(self):
        print("WATING TO CLIENT")
        print("Ready to get order")
        try:
            nClient = 0
            while True:
                if nClient == 5:
                    break
                conn, addr = self.s.accept()
                thr = threading.Thread(target=self.handleClient, args=(conn, addr))
                thr.daemon = False
                thr.start()
                nClient+=1
        except:
            conn.close()
            print("Error")
        finally:
            print("End app")
            conn.close()
        self.s.close()
    
    
def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(5)
    server = Server(s)

if __name__ == "__main__":
    main()
    