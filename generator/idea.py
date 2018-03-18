理想情况下的基于异步的 server 和 client

s:

def server(port):
    s = socket.socket()
    s.bind(('', port))
    s.listen(5)
    while True:
        conn, addr = yield s.accept()
        deal_client(conn, addr)


def deal_client(connection, addr):
    while True:
        data = yield connection.recv(1024)
        if not data: 
            break
        print(data.decode(), 'length ', len(data))
    connection.close()

c:

def client(addr):
    c = socket.socket()
    c = yield c.connect(addr)
    while True:
        yield c.send(b'request')
        data = yield c.recv(1024)
        

# 感觉....
