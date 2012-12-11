"""
  Modified BaseX client code to encapsulate the DB connection.

  Based on the BSD licensed code from here:
    https://github.com/BaseXdb/basex-api
"""
import hashlib
import socket
import array
import tempfile
import threading
import os

# DB Connection Wrapper
#######################
class BaseX:
    def __init__(self,host,port,user,pw,db_name):
        # create session
        self.session = Session(host,port,user,pw)
        self.session.init()
        self._open(db_name)
        self.db_name = db_name
        self.tmp = tempfile.mkdtemp()
    def _open(self,db_name):
        try:
            return self.session.execute('open %s' % db_name)
        except IOError:
            self.session.execute('create db %s' % db_name)
            return self.session.execute('open %s' % db_name)
    def query(self,xquery):
        xquery = 'xquery '+xquery
        result = self.session.execute(xquery)
        return result
    def add(self,file_path):
        query = 'add '+file_path
        result = self.session.execute(query)
        return result
    def delete(self,file_path):
        query = 'delete '+file_path
        result = self.session.execute(query)
        return result
    def store_file(self,filename,content):
        self.session.execute('delete '+filename)
        filename = os.path.join(self.tmp,filename)
        with open(filename,'w') as tmpfile:
            tmpfile.write(content)
        out = self.session.execute('add '+filename)
        os.remove(filename)
        return out
    def get_index(self):
        # Fetch the metadata index for this db_name separately
        self._open(self.db_name+'__index')
        out = self.query('//root')
        self._open(self.db_name)
        return out
    def store_index(self,index_xml):
        # Store the metadata index for this db_name separately
        self._open(self.db_name+'__index')
        out = self.store_file('index.xml',index_xml)
        self._open(self.db_name)
        return out
    def close(self):
        self.session.close()


# Everything below this line from BaseX official code
# ---------------------------------------------------

class SocketInputReader(object):
    
    def __init__(self, sock):
        self.__s = sock
        self.__buf = array.array('B', chr(0) * 0x1000)
        self.init()
        
    def init(self):
        self.__bpos = 0
        self.__bsize = 0
        
    # Returns a single byte from the socket.
    def read(self):
        # Cache next bytes
        if self.__bpos >= self.__bsize:
            self.__bsize = self.__s.recv_into(self.__buf)
            self.__bpos = 0
        b = self.__buf[self.__bpos]
        self.__bpos += 1
        return b

    # Reads until byte is found.
    def read_until(self, byte):
        # Cache next bytes
        if self.__bpos >= self.__bsize:
            self.__bsize = self.__s.recv_into(self.__buf)
            self.__bpos = 0
        found = False
        substr = ""
        try:
            pos = self.__buf[self.__bpos:self.__bsize].index(byte)
            found = True
            substr = self.__buf[self.__bpos:pos+self.__bpos].tostring()
            self.__bpos = self.__bpos + pos + 1
        except ValueError:
            substr = self.__buf[self.__bpos:self.__bsize].tostring()
            self.__bpos = self.__bsize
        return (found, substr)

    def readString(self):
        strings = []
        found = False
        while not found:
            found, substr = self.read_until(0)
            strings.append(substr)
        return ''.join(strings)

class Session(object):
    # see readme.txt
    def __init__(self, host, port, user, pw):

        self.__info = None

        # create server connection
        self.__s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.__s.connect((host, port))
        
        self.__sreader = SocketInputReader(self.__s)
        
        self.__event_socket = None
        self.__event_host = host
        self.__event_listening_thread = None
        self.__event_callbacks = {}

        # receive timestamp
        ts = self.readString()

        # send username and hashed password/timestamp
        m = hashlib.md5()
        m.update(hashlib.md5(pw).hexdigest())
        m.update(ts)
        self.send(user + chr(0) + m.hexdigest())

        # evaluate success flag
        if self.__s.recv(1) != chr(0):
            raise IOError('Access Denied.')

    # see readme.txt
    def execute(self, com):
        # send command to server
        self.send(com)

        # receive result
        result = self.receive()
        self.__info = self.readString()
        if not self.ok():
            raise IOError(self.__info)
        return result

    # see readme.txt
    def query(self, q):
        return Query(self, q)

    # see readme.txt
    def create(self, name, content):
        self.sendInput(8, name, content)

    # see readme.txt
    def add(self, path, content):
        self.sendInput(9, path, content)

    # see readme.txt
    def replace(self, path, content):
        self.sendInput(12, path, content)

    # see readme.txt
    def store(self, path, content):
        self.sendInput(13, path, content)

    # see readme.txt
    def info(self):
        return self.__info

    # see readme.txt
    def close(self):
        self.send('exit')
        self.__s.close()
        if not self.__event_socket is None:
            self.__event_socket.close()

    def init(self):
        """Initialize byte transfer"""
        self.__sreader.init()
        
    def register_and_start_listener(self):
        self.__s.sendall(chr(10))
        event_port = int(self.readString())
        self.__event_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__event_socket.settimeout(5000)
        self.__event_socket.connect((self.__event_host, event_port))
        token = self.readString()
        self.__event_socket.sendall(token + chr(0))
        if not self.__event_socket.recv(1) == chr(0):
            raise IOError("Could not register event listener")
        self.__event_listening_thread = threading.Thread(
            target=self.event_listening_loop
        )
        self.__event_listening_thread.daemon = True
        self.__event_listening_thread.start()
    
    def event_listening_loop(self):
        reader = SocketInputReader(self.__event_socket)
        reader.init()
        while True:
            name = reader.readString()
            data = reader.readString()
            self.__event_callbacks[name](data)
        
    def is_listening(self):
        return not self.__event_socket is None
        
    def watch(self, name, callback):
        if not self.is_listening():
            self.register_and_start_listener()
        else:
            self.__s.sendall(chr(10))
        self.send(name)
        info = self.readString()
        if not self.ok():
            raise IOError(info)
        self.__event_callbacks[name] = callback
        
    def unwatch(self, name):
        self.send(chr(11) + name)
        info = self.readString()
        if not self.ok():
            raise IOError(info)
        del self.__event_callbacks[name]
            
    def readString(self):
        """Retrieve a string from the socket"""
        return self.__sreader.readString()

    def read(self):
        """Return a single byte from socket"""
        return self.__sreader.read()

    def read_until(self, byte):
        """Read until byte is found"""
        return self.__sreader.read_until(byte)

    def send(self, value):
        """Send the defined string"""
        self.__s.sendall(value + chr(0))

    # see readme.txt
    def sendInput(self, code, arg, content):
        self.__s.sendall(chr(code) + arg + chr(0) + content + chr(0))
        self.__info = self.readString()
        if not self.ok():
            raise IOError(self.info())

    def ok(self):
        """Return success check"""
        return self.read() == 0

    def receive(self):
        """Return received string"""
        self.init()
        return self.readString()
    
    def iter_receive(self):
        self.init()
        typecode = self.read()
        while typecode > 0:
            string = self.readString()
            yield string
            typecode = self.read()
        if not self.ok():
            raise IOError(self.readString())


