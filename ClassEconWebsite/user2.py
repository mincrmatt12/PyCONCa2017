import threading, os, sqlite3
import hashlib

## --taken from hashlib. is not in 2.7.6

import binascii
import struct

_trans_5C = b"".join(chr(x ^ 0x5C) for x in range(256))
_trans_36 = b"".join(chr(x ^ 0x36) for x in range(256))

def pbkdf2_hmac(hash_name, password, salt, iterations, dklen=None):
        """Password based key derivation function 2 (PKCS #5 v2.0)

        This Python implementations based on the hmac module about as fast
        as OpenSSL's PKCS5_PBKDF2_HMAC for short passwords and much faster
        for long passwords.
        """
        if not isinstance(hash_name, str):
            raise TypeError(hash_name)

        if not isinstance(password, (bytes, bytearray)):
            password = bytes(buffer(password))
        if not isinstance(salt, (bytes, bytearray)):
            salt = bytes(buffer(salt))

        # Fast inline HMAC implementation
        inner = hashlib.new(hash_name)
        outer = hashlib.new(hash_name)
        blocksize = getattr(inner, 'block_size', 64)
        if len(password) > blocksize:
            password = hashlib.new(hash_name, password).digest()
        password = password + b'\x00' * (blocksize - len(password))
        inner.update(password.translate(_trans_36))
        outer.update(password.translate(_trans_5C))

        def prf(msg, inner=inner, outer=outer):
            # PBKDF2_HMAC uses the password as key. We can re-use the same
            # digest objects and just update copies to skip initialization.
            icpy = inner.copy()
            ocpy = outer.copy()
            icpy.update(msg)
            ocpy.update(icpy.digest())
            return ocpy.digest()

        if iterations < 1:
            raise ValueError(iterations)
        if dklen is None:
            dklen = outer.digest_size
        if dklen < 1:
            raise ValueError(dklen)

        hex_format_string = "%%0%ix" % (hashlib.new(hash_name).digest_size * 2)

        dkey = b''
        loop = 1
        while len(dkey) < dklen:
            prev = prf(salt + struct.pack(b'>I', loop))
            rkey = int(binascii.hexlify(prev), 16)
            for i in xrange(iterations - 1):
                prev = prf(prev)
                rkey ^= int(binascii.hexlify(prev), 16)
            loop += 1
            dkey += binascii.unhexlify(hex_format_string % rkey)

        return dkey[:dklen]

hashlib.pbkdf2_hmac = pbkdf2_hmac

AUTH_VIEW = 1
AUTH_POST_FORUM = 2
AUTH_POST_BLOG = 4
AUTH_POST_QUESTION = 8
AUTH_INVITE_USER = 16
AUTH_ADMIN_CHANGEAUTH = 32
AUTH_ADMIN_MANAGEACCOUNTS = 64

AUTH_ALL = 1 + 2 + 4 + 8 + 16 + 32 + 64

USERNAME_FORMAT = '<span data-toggle="tooltip" title="Full Name: {}">{}</span>'

def format_username(uid, user_handle):
    return USERNAME_FORMAT.format(user_handle.get_user_data(uid)["FullName"], user_handle.get_user_data(uid)["Username"])

class Logins:
    def __init__(self, cursor, con):
        self.tokens = {}
        self.remaining_time = {}
        self.account_create_tokens = {}
        self.cursor = cursor
        self.connection = con
        self.start_timer()

    def change_username(self, uid, name):
        phrase = "UPDATE Users SET Username=? WHERE ID=?"
        data = (name,uid,)
        self.cursor.execute(phrase, data)
        self.connection.commit()
        

    def _do_timer(self):

        remain = {}

        for i in self.remaining_time:
            self.remaining_time[i] -= 1

            if self.remaining_time[i] == 0:
                remain[i] = 0
                del self.tokens[i]

        for i in remain:
            del self.remaining_time[i]
            
        for i in self.account_create_tokens:
            self.account_create_tokens[i] -= 1
            if self.account_create_tokens[i] <= 0:
                del self.account_create_tokens[i]

        threading.Timer(1, self._do_timer).start()

    def start_timer(self):
        self._do_timer()

    def _login_valid(self, user, password):
        self.cursor.execute("SELECT * FROM Users WHERE Username=?", (user,))
        h = self.cursor.fetchone()
        if h == None:
            hashlib.pbkdf2_hmac("sha512", "abc123456", "trhisisasdgafb466f", 400000)
            return -1
        salt = h["PassSalt"]
        password = password.encode('utf-8')
        calculated = hashlib.pbkdf2_hmac("sha512", password, salt, 400000)
        if str(calculated) == str(h["PassHash"]):
            return int(h["ID"])
        return -1
    
    def add_service(self, uid, service):
        old = self.get_user_data(uid)
        c = ';'.join([x for x in (old["Services"]+';'+service).split(';') if x != ''])
        phrase = "UPDATE Users SET Services=? WHERE ID=?"
        data = (c, uid,)
        self.cursor.execute(phrase, data)
        self.connection.commit()
    
    def get_user_data(self, uid):
        phrase = "SELECT * FROM Users WHERE ID=? LIMIT 1"
        data = (uid,)
        
        self.cursor.execute(phrase, data)
        return self.cursor.fetchone()
    
    def is_auth(self, uid, authlevel):
        udata = self.get_user_data(uid)
        return (int(udata["AuthLevel"]) & authlevel) == authlevel
    
    def account_token_valid(self, token):
        if token in self.account_create_tokens:
            return True
        return False
    
    def create_account_token(self, timeinsecs):
        token = os.urandom(64)
        self.account_create_tokens[token] = timeinsecs
        return token
    
    def use_token(self, token):
        if self.account_token_valid(token):
            del self.account_create_tokens[token]
    
    def revalidate_token(self, token):
        if self.is_token_valid(token):
            self.remaining_time[token] = 800 if self.remaining_time[token] < 800 else self.remaining_time[token]

    def do_login(self, user, password):
        uid = self._login_valid(user, password)
        if uid != -1:
            access_token = str(os.urandom(32))
            self.tokens[access_token] = uid
            self.remaining_time[access_token] = 1600
            return access_token
        else:
            return -1

    def create_account(self, user, password, fullname, auth=3):
        salt = str(os.urandom(32))
        calculated = hashlib.pbkdf2_hmac("sha512", password, salt, 400000)
        self.cursor.execute("insert into Users (Username, PassHash, PassSalt, AuthLevel, FullName, Services) values (?, ?, ?, ?, ?, ?)",
                            (user, sqlite3.Binary(calculated), sqlite3.Binary(salt), auth, fullname, '',))
        print 'test'
        self.connection.commit()

    def is_token_valid(self, token):
        return token in self.tokens

    def invalidate_token(self, token):
        del self.tokens[token]
        del self.remaining_time[token]

    def uid_for_token(self, token):
        return self.tokens[token] if self.is_token_valid(token) else -1