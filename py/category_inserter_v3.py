#!/usr/bin/python3


''' 
#Import Libs 
pip3 install mysql-connector-python
'''
import mysql.connector as MySqlConnector
import sys, time, re
from os import path as os_path

'''
Constant Data are All Capital Cases
'''

## Global Controller
#DEFAULT_ZONE = "c.ssquid.in";
DEFAULT_ZONE = "c.ssquid.in.";

# DB Details
DB_USER = 'mydns'
DB_USER_PASSWD = 'mydns'
DB_HOST = '127.0.0.1'
DB_NAME = "mydns"

# Commit Limit
DB_COMMIT_LIMIT = 100;

mysql_mydns_connection = None;
mydns_cursor = None;

CREATE_DB_ZONE = False

categories_list = {}
zone_name_list = {}

class DatabaseConnector:
    
    def create_connection():
        try:
            # MySQL Connection
            global mysql_mydns_connection
            mysql_mydns_connection = MySqlConnector.connect(user=DB_USER, password=DB_USER_PASSWD, host=DB_HOST, database=DB_NAME)

            #MySQL Cursor
            global mydns_cursor
            mydns_cursor = mysql_mydns_connection.cursor()
            
            return True
        except Exception as except_me:
            print(f"Check if MySQL is Running, Error: [{str(except_me)}]")
            return False


class DatabaseQuery:

    def get_categories_list(db_cursor,):
        
        try:
            sql_query = "SELECT * FROM category_data;";
            db_cursor.execute(sql_query)
        
            query_result = db_cursor.fetchall()
            
            global categories_list
            
            for one_result in query_result:
                categories_list[str(one_result[0])] = one_result[1]
            
            return True
            
        except Exception as except_me:
            print(f"No Category List Found, Failed Fetching Category List, Error: [{str(except_me)}]")
            return False
            
    """ Once Validate The Zone Check [Got Created Or Nor]"""
    def get_zone_name_list(db_cursor,):
        
        # Create Default Zone  [IMP]
        if DatabaseQuery.get_zone_id(db_cursor = mydns_cursor, zone_name = DEFAULT_ZONE) == 0:
            DatabaseQuery.create_zone(db_cursor = mydns_cursor, zone_name = DEFAULT_ZONE)
        
        try:
            sql_query = "SELECT * FROM soa;";
            db_cursor.execute(sql_query)
        
            query_result = db_cursor.fetchall()
            
            global zone_name_list
            
            for one_result in query_result:
                zone_name_list[str(one_result[0])] = one_result[1]
            
            return True
            
        except Exception as except_me:
            print(f"No Zone Name List Found, Failed Fetching Category List, Error: [{str(except_me)}]")
            return False
    
    """ Insert To DB Table RR """
    def insert_into_rr(zone_id, domain_name, record_type, curr_category_id, column_aux):
        try:
            sql_query = "INSERT INTO rr(zone,name,type,data,aux) VALUES (%s, %s, %s, %s, %s);"
            query_params = [zone_id, domain_name, record_type, curr_category_id, column_aux];
            mydns_cursor.execute(sql_query, query_params);
            return True
        except Exception as except_me:
            print(f"Insert Failed!!! DomainRecord: {domain_name}, Check: {str(except_me)}")
            return False

    """ Insert To DB Table RR """
    def update_rr(curr_category_id, domain_name, zone_id):
        try:
            sql_query = "UPDATE rr SET data = %s WHERE name = %s and zone = %s";
            query_params = [str(curr_category_id), domain_name, zone_id];
            mydns_cursor.execute(sql_query, query_params);
            return True
        except Exception as except_me:
            print(f"Update Failed!!! DomainRecord: {domain_name}, Check: {str(except_me)}")
            return False

    
    ''' 
        Check if a Zone Exists
    '''
    def check_zone(db_cursor, zone_name):

        if Validators.validate_domain_name(zone_name):
            
            if not zone_name.endswith("."):
                zone_name = zone_name + "."
            
            # We made sure that the DEFAULT_ZONE(c.ssquid.in.) is already there
            if zone_name == DEFAULT_ZONE:
                return True
            else:
                if DatabaseQuery.get_zone_id(db_cursor=mydns_cursor, zone_name=zone_name) == 0:
                    return False
            return True
        else:
            return False
        
    '''
        Since Zone Numbering will Start from 1
        We can Provide Directly the Zone Number
        DB Query: SELECT * FROM soa WHERE origin = %s
    '''
    def get_zone_id(db_cursor, zone_name):
        
        if not zone_name.endswith("."):
            zone_name = zone_name + "."
        
        sql_query = "SELECT * FROM soa WHERE origin = %s";
        query_params = [zone_name];
        db_cursor.execute(sql_query, query_params)
        
        query_result = db_cursor.fetchone()
        
        if query_result:
            return query_result[0]
        else:
            return 0

    ''' SQL Query: INSERT INTO soa(origin,ns,mbox) VALUES("c.ssquid.in.","c.ssquid.in","mailbox.c.ssquid.in"); '''
    def create_zone(db_cursor, zone_name):
        
        if not zone_name.endswith("."):
            zone_name = zone_name + "."
        print("Create Zone: ", zone_name)
        try:
            sql_query = "INSERT INTO soa(origin,ns,mbox) VALUES(%s, %s, %s);";
            query_params = [zone_name,"ns." + zone_name,"mailbox." + zone_name];
            db_cursor.execute(sql_query, query_params)
            return True
        except Exception as except_me:
            print(f"Create Zone: Insert: FAILED!!! , Error: [{str(except_me)}]")
            return False


    ''' Check If Data Exists '''
    def check_if_rr_exists(db_cursor, domain_name, zone_id):
                
        sql_query = "SELECT * FROM rr WHERE name = %s and zone = %s";
        query_params = [domain_name, zone_id];
        db_cursor.execute(sql_query, query_params)
        
        query_result = db_cursor.fetchone()
        
        if query_result:
            prevRecord = DomainRecord.generateDomainRecordFromDB(query_result)
            return True, prevRecord
        else:
            return False, None


    
class Validators:

    ''' Validate a Domain Name '''
    def validate_domain_name(domain_name):
        domain_valid_regex = "^((?!-)[A-Za-z0-9_-]{1,63}(?<!-)\\.)+[A-Za-z]{2,6}$"
        
        if domain_name.endswith("."):
            domain_name = domain_name[:-1]
        
        domain_pattern = re.compile(domain_valid_regex) # Compiling
 
        if(re.search(domain_pattern, domain_name)):
            return True
        else:
            if Validators.is_ipaddress(domain_name):
                return True
            else:
                return False

    ''' Validate Fields are COntaining Data '''
    def is_empty(data_str):
        return data_str.strip() == ""


    ''' Check if a Given data is a IP Address '''
    def is_ipaddress(data_str):
        # A Quick way to check if a String is IP Pattern
        try:            
            return data_str.count('.') == 3 and  all(0<=int(num)<256 for num in data_str.rstrip().split('.'))
        except Exception as except_me:
            return False
    
    '''
        Get the Category Code ID List 
        Test Case:
            Category Code
            INPUT 1: 1,4,15,27,43,53,66 # Str For MySQL Database
            INPUT 2: 66 # Str For MySQL Database
            OUTPUT_EXPECTED: [1,4,15,27,43,53,66] # Py List
    '''
    def get_category_code_list(category_code):
        if type(category_code) == list:
            return ",".join(category_code)
        else:
            return category_code
            
            
    def get_category_id_str(category_id_list):
        if type(category_id_list) == list:
            return ",".join(category_id_list)
        else:
            return category_id_list


    '''
        Now Only Considering Wildcard as *
        Not Considering '*.subdomain'
    '''
    def validate_wildcard(wildcard):
        valid_wildcard_regex = "^\*$"
        
        wildcard_pattern = re.compile(valid_wildcard_regex) # Compiling
 
        if(re.search(wildcard_pattern, wildcard)):
            return True
        else:
            return False




"""
Requirement
------------

DomainRecord
curr_category_id [str]
domain_name [str]
wildcard [bool]
zone_name [str]
zone_id [computed from zone_name]
rr_present [bool]
category_id_list = [] [list]
category_id_list = [] [list]
is_ip [bool]
rr_type = "TXT" # Record Type
rr_aux = "0" # Not Sure Need to Research [aux] 

"""
class DomainRecord:
    
    def __init__(self, curr_category_id, domain_name, wildcard, zone_name, zone_id, rr_present=False, is_ip=False, db_record_id=0):
        self.curr_category_id = str(curr_category_id)
        self.domain_name = domain_name
        self.wildcard = True if wildcard else False
        self.wildcard_domain_name = "*." + domain_name if wildcard else ""
        self.zone_name = zone_name
        self.zone_id = zone_id
        self.rr_present = rr_present
        self.category_id_list = self.create_category_id_list(curr_category_id)
        self.is_ip = is_ip
        
        # Extra
        self.db_record_id = db_record_id
        
        # Set Default
        self.rr_type = "TXT" # Record Type
        self.rr_aux = "0" # Not Sure Need to Research [aux] 

    def create_category_id_list(self, category_ids):
        return str(category_ids).split(",")


    """ Here we make sure that the Category List is Unique"""
    def append_to_category_id_list(self, category_list):
        _new_category_list = self.category_id_list
        if type(category_list) == int:
            _new_category_list = _new_category_list + str(category_list).split(",")
        if type(category_list) == str:
            _new_category_list = _new_category_list + str(category_list).split(",")
        if type(category_list) == list:
             _new_category_list = _new_category_list + category_list
        
        _new_category_list = list(set(_new_category_list))
        _new_category_list.sort()
        self.category_id_list = _new_category_list
    
    def generateDomainRecordFromDB(query_result):
        db_record_id = query_result[0]
        zone_id = query_result[1]
        domain_name = query_result[2]
        type = query_result[3]
        category_ids = query_result[4]
        domainRecord = DomainRecord(curr_category_id=category_ids, domain_name=domain_name, wildcard=False, zone_name="", is_ip = None, db_record_id=db_record_id, zone_id=zone_id)   
        return domainRecord
    
    def __repr__(self): 
        dataRecords = f"[ curr_category_id: {str(self.curr_category_id)}, domain_name: {str(self.domain_name)}, wildcard: {str(self.wildcard)}, zone_name: {str(self.zone_name)}, zone_id: {str(self.zone_id)}, is_ip: {str(self.is_ip)}, rr_present: {str(self.rr_present)}, category_id_list: {str(self.category_id_list)} ]"
        return dataRecords

    __str__ = __repr__


'''
    Provide Error String In Return if False
'''
def check_fields(one_record):
    
    curr_category_id = None
    domain_name = None
    wildcard = None
    zone_name = None
    is_ip = False

    data_list = one_record.split(",")
    
    try:
        if len(data_list) < 2:
            return False, None
        else:
            # Make Sure they are Not Empty
            pass
        
            
        if len(data_list) == 2:
            curr_category_id = int(data_list[0])
            
            if Validators.validate_domain_name(data_list[1]):
                domain_name = data_list[1]
                is_ip = Validators.is_ipaddress(data_list[1])
            else:
                return False, "Domain Name Regex Violation"
            
            zone_name = DEFAULT_ZONE
        
        elif len(data_list) == 3:
            curr_category_id = int(data_list[0])
            
            if Validators.validate_domain_name(data_list[1]):
                domain_name = data_list[1]
                is_ip = Validators.is_ipaddress(data_list[1])
            else:
                return False, "Domain Name Regex Violation"
            
            #print(" Scenario: Example: [23,a.b.c,] \n Use Case: Where data is 2 comma is 3 @ end , Still consider the data But No Wildcard since not explicitly specified: data_line: [", one_record, "] , Extracted: ", data_list);
            
            if Validators.is_empty(data_list[2]):
                wildcard = None
            elif Validators.validate_wildcard(data_list[2]):
                wildcard = data_list[2]
            else:
                return False, "Wildcard Regex Violation"
            
            zone_name = DEFAULT_ZONE
            
        elif len(data_list) == 4:
            curr_category_id = int(data_list[0])
            
            if Validators.validate_domain_name(data_list[1]):
                domain_name = data_list[1]
                is_ip = Validators.is_ipaddress(data_list[1])
            else:
                return False, "Domain Name Regex Violation"
            
            #print(" Scenario: Example: [23,a.b.c,] \n Use Case: Where data is 2 comma is 3 @ end , Still consider the data But No Wildcard since not explicitly specified: data_line: [", one_record, "] , Extracted: ", data_list);
            if Validators.is_empty(data_list[2]):
                wildcard = None
            elif Validators.validate_wildcard(data_list[2]):
                wildcard = data_list[2]
            else:
                return False, "Wildcard Regex Violation"
            
            #print(" Scenario: Example: [23,a.b.c,,zone.co] \n Use Case: Where We need a New Zone But No Wildcard : [", one_record, " ,] Extracted: ", data_list);
            if Validators.is_empty(data_list[3]):
                zone_name = DEFAULT_ZONE
            elif Validators.validate_domain_name(data_list[3]):
                zone_name = data_list[3]
            else:
                return False, "Domain Name Regex Violation"

        # Check if the requested Category ID and zone_name
        if CREATE_DB_ZONE:
            if DatabaseQuery.get_zone_id(db_cursor = mydns_cursor, zone_name = zone_name) == 0:
                DatabaseQuery.create_zone(db_cursor = mydns_cursor, zone_name = zone_name)

        if categories_list.get(str(curr_category_id), None) and DatabaseQuery.check_zone(db_cursor=mydns_cursor, zone_name=zone_name):
            ''' '''
            zone_id = DatabaseQuery.get_zone_id(db_cursor=mydns_cursor, zone_name=zone_name)
            domainRecord = DomainRecord(curr_category_id=curr_category_id, domain_name=domain_name, wildcard=wildcard, zone_name=zone_name, zone_id=zone_id, is_ip = is_ip)
            return True, domainRecord
        else:
            return False, "Category List or Zone List Voilation"
        
    except Exception as except_me:
        print(f"Exception!! Record Incorrect Check Record: {one_record}, Error: {str(except_me)}")
        return False, None


def db_transaction(domainRecord):
    #print("DB Transaction ", domainRecord);
    
    status = ""
    r = 0;
    
    # Check if Data Exists for this
    rr_present, present_record = DatabaseQuery.check_if_rr_exists(db_cursor = mydns_cursor, domain_name = domainRecord.domain_name, zone_id = domainRecord.zone_id)
    
    if not rr_present:
        # Insert the Data
        DatabaseQuery.insert_into_rr(zone_id=domainRecord.zone_id, domain_name=domainRecord.domain_name, record_type="TXT", curr_category_id=domainRecord.curr_category_id, column_aux=domainRecord.rr_aux)
        
    elif rr_present and domainRecord.curr_category_id not in present_record.category_id_list:
        # Update The Data
        present_record.append_to_category_id_list(domainRecord.curr_category_id)
        DatabaseQuery.update_rr(curr_category_id=Validators.get_category_id_str(present_record.category_id_list), domain_name=domainRecord.domain_name, zone_id=domainRecord.zone_id)
    else:
        status = "Domain Record Exists"
        r = 1
    
    if domainRecord.wildcard:
        # Check if Data Exists for this
        rr_present, present_record = DatabaseQuery.check_if_rr_exists(db_cursor = mydns_cursor, domain_name = domainRecord.wildcard_domain_name, zone_id = domainRecord.zone_id)
        
        if domainRecord.is_ip:
            status += ": Domain Record is an IP No Insert"
            return False, status, domainRecord
        
        if not rr_present:
            # Insert the Data
            DatabaseQuery.insert_into_rr(zone_id=domainRecord.zone_id, domain_name=domainRecord.wildcard_domain_name, record_type="TXT", curr_category_id=domainRecord.curr_category_id, column_aux=domainRecord.rr_aux)
            return True, status + ": Wildcard Inserted", domainRecord
        elif rr_present and domainRecord.curr_category_id not in present_record.category_id_list:
            # Update The Data
            present_record.append_to_category_id_list(domainRecord.curr_category_id)
            DatabaseQuery.update_rr(curr_category_id=Validators.get_category_id_str(present_record.category_id_list), domain_name=domainRecord.wildcard_domain_name, zone_id=domainRecord.zone_id)
            return True, status + ": Wildcard Updated", domainRecord
        else:
            status += ": Domain Record Wildcard Exists"
            return False, status, domainRecord
    else:
        if status:
            return False, status, domainRecord
        else:
            return True, "Record Updated", domainRecord
 
    
    

def process_data(process_file):
    
    
    # Create Default Zone  [IMP]
    if DatabaseQuery.get_zone_id(db_cursor = mydns_cursor, zone_name = DEFAULT_ZONE) == 0:
        DatabaseQuery.create_zone(db_cursor = mydns_cursor, zone_name = DEFAULT_ZONE)
    
    line_counter = 1;
    
    # Read the File
    with open(process_file) as record_file:    
        for one_record in record_file:
            one_record = one_record.strip(); # Strip Remove Unnecessary \n & Spaces 
            
            if one_record.startswith("#"):
                #print("Skipping Comment Line: ", one_record)
                pass
            elif one_record == "":
                #print("Skipping Empty Line: ", one_record)
                pass
            else:
                result, domainRecord = check_fields(one_record)
                if result:
                    trans_status, trans_desc, _domainRecord = db_transaction(domainRecord)
                    _result = "[+]" if trans_status else "[-]"
                    print(line_counter, _result, trans_status, trans_desc, _domainRecord)
                else:
                    print(line_counter, f"[-] Data Incorrect: [{one_record}] , Reason: [Validation Fails: {domainRecord}] -> Processing Next")
            
            line_counter = line_counter + 1;


def main():
    script_usage = '''
python3 <SCRIPT_NAME> file_name
file_name: 
    File containing data in CSV Format 
    Example: category_id, domain_name, wildcard, zone
    '#' are indicated as Comments
    
python3 <SCRIPT_NAME> file_name cz
file_name: 
    File containing data in CSV Format 
    Example: category_id, domain_name, wildcard, zone
    '#' are indicated as Comments
    cz -> Create Zone if Not Exists in Database
    '''

    print("Script Arguments Received are : ", sys.argv)

    # Code Does Not handles Will be Later Handled
    if len(sys.argv) > 1:
        process_file = sys.argv[1]
        
        if not os_path.exists(process_file):
            sys.exit("Filename Does Not Exists!!!!.... \n" + script_usage)
        
        if len(sys.argv) > 2 and sys.argv[2] == "cz":
            global CREATE_DB_ZONE
            CREATE_DB_ZONE = True
        
        # Check & Create Connection
        if DatabaseConnector.create_connection():
            if DatabaseQuery.get_categories_list(db_cursor=mydns_cursor) and DatabaseQuery.get_zone_name_list(db_cursor=mydns_cursor):
                process_data(process_file=process_file)
        
    else:
        sys.exit("Please Provide A Filename to Process.... \n" + script_usage)
        
    
        
main()