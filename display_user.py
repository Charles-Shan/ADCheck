from ldap3 import Server, Connection, ALL, LEVEL, ServerPool
from datetime import datetime, timezone, timedelta
import time
import sys
import getpass

class Account:
    '''
    self.displayname
    self.account_expires
    self.pwd_last_set
    self.lockout_time
    self.last_logon
    self.last_logon_Timestamp
    self.mail
    self.department
    '''

    def __init__(self, nni):
        self.nni = nni

class LDAPClient:
    def __init__(self, host, port, login, password):
        server = Server(host, port = port, use_ssl = True, get_info=ALL)
        self.conn = Connection(server, login, password, auto_bind=True)
        self.basesearch = ",".join(["dc=" + a for a in host.split(".")])

    def searchUserNNI(self, nni):
        '''Search user using its NNI'''
        self.conn.search(self.basesearch, '(&(objectclass=person)(sAMAccountName=' + nni + '))', \
                attributes=['displayName','accountExpires', 'pwdLastSet', 'lockoutTime','lastLogon','lastLogonTimestamp','mail','department'])
        
        account = None
        if self.conn.entries:
            account = LDAPClient.__userFromAttr(nni, self.conn.entries[0])
        
        return account
    
    @staticmethod
    def __userFromAttr(nni, entry):
        '''Create account object from entry'''
        account = Account(nni)
        account.displayname = entry["displayName"].values[0]
        account.account_expires = LDAPClient.__takeRawTime(entry, "accountExpires")
        account.pwd_last_set = LDAPClient.__takeRawTime(entry, "pwdLastSet")
        account.lockout_time = LDAPClient.__takeRawTime(entry, "lockoutTime")
        #account.last_logon = LDAPClient.__takeRawTime(entry, "lastLogon")
        account.last_logon_Timestamp = LDAPClient.__takeRawTime(entry, "lastLogonTimestamp")
        account.mail = entry["mail"].values[0]
        account.department = entry["department"].values[0]
        
        

        return account
        
    @staticmethod
    def __takeRawTime(attrDict, key):
        res = None
        if key in attrDict:
            values = attrDict[key].values
            raw_values = attrDict[key].raw_values
            
            if (values and int(attrDict[key].raw_values[0].decode()[0]) <= 2
                and datetime(1601, 1, 1, tzinfo=timezone.utc) != values[0]):
                res = attrDict[key].values[0]
            
        return res

def main(argv):
    if len(argv) != 2:
        print("Usage: python display_user.py <Access_NNI> <NNI_to_check>")
        return
        
    username = sys.argv[1]
    password = getpass.getpass("Input Password：")
    nni = sys.argv[2]

    ldap_client = LDAPClient('atlas.edf.fr', 636, 'ATLAS\\' + username, password)
    
    
    account = ldap_client.searchUserNNI(nni)
    print(nni + " (" + account.displayname + ")")
    print('account_expires' + " = " + str(account.account_expires))
    print('pwd_last_set'+ " = " + str(account.pwd_last_set))
    print('lockout_time'+ " = " + str(account.lockout_time))
    #print('last_logon'+ " = " + str(account.last_logon))
    print('last_logon_Timestamp'+ " = " + str(account.last_logon_Timestamp))
    print('mail'+ " = " + account.mail)
    print('department'+ " = " + account.department)
    
   
            
main(sys.argv[1:])

