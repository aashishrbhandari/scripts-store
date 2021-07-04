#!/usr/bin/python3

''' 
Few Analysis

root@swg-t-1:~# python3
Python 3.6.9 (default, Jan 26 2021, 15:33:00)
[GCC 8.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>>
>>> # How Range Works
...
>>> for one_d in range(1,5):
...   print(one_d)
...
1
2
3
4
>>> for one_d in range(1,5+1):
...   print(one_d)
...
1
2
3
4
>>> 


'''


''' Import Libs 
pip3 install mysql-connector-python

Make sure to udpate the details of mysql server

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
DB_USER = 'mydns_user'
DB_USER_PASSWD = 'mydNs_password $@13'
DB_HOST = '127.0.0.1'
DB_NAME = "mydns"

# Commit Limit
DB_COMMIT_LIMIT = 100;

DIGIT_ZERO = "0";
DIGIT_ONE = "1";

mysql_mydns_connection = None;
mydns_cursor = None;

CREATE_DB_ZONE = False


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
            print("# Trace Logs Left")
            print("Check if MySQL is Running")
            return False

    
class Validators:

    ''' Validate a Domain Name '''
    def validate_domain_name(domain_name):
        domain_valid_regex = "^((?!-)[A-Za-z0-9_-]{1,63}(?<!-)\\.)+[A-Za-z]{2,6}$"
        
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
            INPUT: 1001000000000010000000000010000000000000001000000000100000000000010
            OUTPUT_EXPECTED: 1,4,15,27,43,53,66
    '''
    def get_category_code_list(category_code):
        category_code_list = []
        for seq_num in range(1, len(category_code) + 1):
            if category_code[seq_num - 1] == DIGIT_ONE:
                category_code_list.append(seq_num)
        return category_code_list
        
            
    ''' 
        Generate Category Code
            Input
                1. category_id: 57
                2. prev_category_code: 1001000000000010000000000010000000000000001000000000100000000000010
                
        Test Case:
        >>> get_category_code(12)
        '000000000001'
        >>> get_category_code(12, "01001000000000000000")
        '01001000000100000000'
        >>> get_category_code(12, "010010")
        '010010000001'

    '''
    def get_category_code(category_id, prev_category_code = None):
        
        DIGIT_ZERO = "0";
        DIGIT_ONE = "1";
        category_code = "";
        category_id = int(category_id)
       
        if prev_category_code:
            prev_category_code_digits = list(prev_category_code)
            category_code = prev_category_code
            if category_id > len(prev_category_code_digits):
                for one_digit in range(len(prev_category_code_digits) + 1, category_id + 1):
                    if category_id == one_digit:
                        category_code += DIGIT_ONE;
                    else:
                        category_code += DIGIT_ZERO;
            else:        
                prev_category_code_digits[category_id - 1] = DIGIT_ONE; # Since Array/List Start from 0
                category_code = "".join(prev_category_code_digits);
        
        else:
            # Create New
            for one_digit in range(1, category_id + 1):
                if category_id == one_digit:
                    category_code += DIGIT_ONE;
                else:
                    category_code += DIGIT_ZERO;
        
        return category_code
        
        
    '''
        Know Only COnsidering;
        Wildcard as *
        Not Considering '*.subdomain'
    '''
    def validate_wildcard(wildcard):
        valid_wildcard_regex = "^\*$"
        
        wildcard_pattern = re.compile(valid_wildcard_regex) # Compiling
 
        if(re.search(wildcard_pattern, wildcard)):
            return True
        else:
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
        
            return True
            
        else:
            return False
        
        '''
        sql_query = "SELECT * FROM soa WHERE origin = %s";
        query_params = [zone_name];
        db_cursor.execute(sql_query, query_params)
        
        query_result = db_cursor.fetchone()
        
        if query_result:
            return True
        else:
            return False
        '''
        

    '''
        Since ZOne Numbering will Start from 1
        We can Provide Directly the Zone Number
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
    
    '''
        Same As Above Will Remove Either one
    '''
    def check_get_zone_id(db_cursor, zone_name):
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
    
    def create_zone(db_cursor, zone_name):
        ''' SQL Query: INSERT INTO soa(origin,ns,mbox) VALUES("c.ssquid.in.","c.ssquid.in","mailbox.c.ssquid.in"); '''
        if not zone_name.endswith("."):
            zone_name = zone_name + "."
        
        sql_query = "INSERT INTO soa(origin,ns,mbox) VALUES(%s, %s, %s);";
        query_params = [zone_name,"ns." + zone_name,"mailbox." + zone_name];
        db_cursor.execute(sql_query, query_params)
        
        query_result = db_cursor.fetchone()
        
        print("Zone Created: ", zone_name)
        print(query_result)
        
        if query_result:
            return query_result[0]
        else:
            return 0
            
        
    
    ''' Check If Data Exists '''
    def check_if_rr_exists(db_cursor, domain_name, zone_id):
        
        ''' 
        Query: SELECT * FROM rr WHERE name = "google.com"; 
        Result: (1, 1, 'nic.gov.in', 'TXT', '0000000000000000000000100000000000000000000000000000000000000000000', 0, 86400)
        
        Analysis:
        Table 
        +----+------+-----------------------+------+---------------------------------------------------------------------+-----+-------+
        | id | zone | name                  | type | data                                                                | aux | ttl   |
        +----+------+-----------------------+------+---------------------------------------------------------------------+-----+-------+
        |  1 |    1 | nic.gov.in            | TXT  | 0000000000000000000000100000000000000000000000000000000000000000000 |   0 | 86400 |
        |  2 |    1 | tristantaormino.com   | TXT  | 0000000000000000000000000000000000000000000000000000100000000000000 |   0 | 86400 |
        |  3 |    1 | *.tristantaormino.com | TXT  | 0000000000000000000000000000000000000000000000000000100000000000000 |   0 | 86400 |
        +----+------+-----------------------+------+---------------------------------------------------------------------+-----+-------+
        '''
        
        sql_query = "SELECT * FROM rr WHERE name = %s and zone = %s";
        query_params = [domain_name, zone_id];
        db_cursor.execute(sql_query, query_params)
        
        query_result = db_cursor.fetchone()
        
        if query_result:
            prevRecord = DomainRecord.generateDomainRecordFromDB(query_result)
            return True, prevRecord
        else:
            return False, None
        
    
        

class DomainRecord:

    def __init__(self):
        self.category_id = None
        self.domain_name = None
        self.wildcard = None
        self.domain_zone = None
        self.domain_zone_id = 0
        self.is_record_present = False
        self.categories_list = None
        self.categories_list_from_db = []
        self.is_ipaddress = False
        
        self.record_type = "TXT"
        self.column_aux = "0" # Not Sure Need to Research [aux]
        self.category_code = "0"
        
        # Other Fields
        self.update_record = False
        self.record_inserted = False
        self.error = False
        self.error_desc = "NO-ERROR"
    
    def generateDomainRecordFromDB(query_result):
        prev_record_id = query_result[0]
        zone_id = query_result[1]
        domain_name = query_result[2]
        type = query_result[3]
        category_code = query_result[4]
        return DomainRecord.createDomainRecordFromDB(prev_record_id = prev_record_id, zone_id = zone_id, domain_name = domain_name, type = type, category_code = category_code)
        
    
    def createDomainRecordFromDB(prev_record_id = 0, zone_id = 0, domain_name = None, type = "TXT", category_code = None):
        _domainRecord = DomainRecord()
        _domainRecord.is_record_present = True
        _domainRecord.prev_record_id = prev_record_id
        _domainRecord.domain_zone_id = zone_id
        _domainRecord.domain_name = domain_name
        _domainRecord.record_type = type
        _domainRecord.category_code = category_code
        return _domainRecord
    
    def __init__(self, category_id = 0, domain_name = None, wildcard=None, domain_zone=DEFAULT_ZONE, is_ipaddress=False):
        self.category_id = category_id
        self.domain_name = domain_name
        self.wildcard = wildcard
        self.domain_zone = domain_zone
        self.domain_zone_id = 0
        self.is_record_present = False
        self.categories_list = [category_id]                
        self.categories_list_from_db = []
        self.is_ipaddress = is_ipaddress
        
        self.prev_record_id = 0;
        
        self.record_type = "TXT"
        self.column_aux = "0" # Not Sure Need to Research [aux]
        self.category_code = "0"
        
        # Other Fields
        self.update_record = False
        self.record_inserted = False
        self.error = False
        self.error_desc = "NO-ERROR"
        
    def set_category_id(self, category_id):
        self.category_id = category_id
    
    def set_categories_list(self, categories_list):
        self.categories_list = categories_list

    def set_categories_list_from_db(self, category_code_from_db):
        self.categories_list_from_db = Validators.get_category_code_list(category_code_from_db)
    
    
    def set_category_code(self, category_code):
        self.category_code = category_code
        self.categories_list = Validators.get_category_code_list(category_code)
    
    def __repr__(self): 
        dataRecords = "{ category_id: " + str(self.category_id) + ", domain_name: " + str(self.domain_name) + ", wildcard: " + str(self.wildcard) + ", domain_zone: " + str(self.domain_zone) + ", is_ipaddress: " + str(self.is_ipaddress) + ", is_present_record: " + str(self.prev_record_id) + " }"
        return dataRecords
    
    def __str__(self):
        dataRecords = "{ category_id: " + str(self.category_id) + ", domain_name: " + str(self.domain_name) + ", wildcard: " + str(self.wildcard) + ", domain_zone: " + str(self.domain_zone) + ", is_ipaddress: " + str(self.is_ipaddress) + ", is_present_record: " + str(self.prev_record_id) + " }"
        return dataRecords
    
'''
    Provide Error String In Return if False
'''
def check_fields(one_data_line):
    
    category_id = None
    domain_name = None
    wildcard = None
    domain_zone = None
    is_ipaddress = False

    data_list = one_data_line.split(",")
    
    try:
        if len(data_list) < 2:
            return False, None
        else:
            # Make Sure they are Not Empty
            pass
        
            
        if len(data_list) == 2:
            category_id = int(data_list[0])
            
            if Validators.validate_domain_name(data_list[1]):
                domain_name = data_list[1]
                is_ipaddress = Validators.is_ipaddress(data_list[1])
            else:
                return False, "Domain Name Regex Violation"
            
            domain_zone = DEFAULT_ZONE
        
        elif len(data_list) == 3:
            category_id = int(data_list[0])
            
            if Validators.validate_domain_name(data_list[1]):
                domain_name = data_list[1]
                is_ipaddress = Validators.is_ipaddress(data_list[1])
            else:
                return False, "Domain Name Regex Violation"
            
            #print(" Scenario: Example: [23,a.b.c,] \n Use Case: Where data is 2 comma is 3 @ end , Still consider the data But No Wildcard since not explicitly specified: data_line: [", one_data_line, "] , Extracted: ", data_list);
            
            if Validators.is_empty(data_list[2]):
                wildcard = None
            elif Validators.validate_wildcard(data_list[2]):
                wildcard = data_list[2]
            else:
                return False, "Wildcard Regex Violation"
            
            domain_zone = DEFAULT_ZONE
            
        elif len(data_list) == 4:
            category_id = int(data_list[0])
            
            if Validators.validate_domain_name(data_list[1]):
                domain_name = data_list[1]
                is_ipaddress = Validators.is_ipaddress(data_list[1])
            else:
                return False, "Domain Name Regex Violation"
            
            #print(" Scenario: Example: [23,a.b.c,] \n Use Case: Where data is 2 comma is 3 @ end , Still consider the data But No Wildcard since not explicitly specified: data_line: [", one_data_line, "] , Extracted: ", data_list);
            if Validators.is_empty(data_list[2]):
                wildcard = None
            elif Validators.validate_wildcard(data_list[2]):
                wildcard = data_list[2]
            else:
                return False, "Wildcard Regex Violation"
            
            #print(" Scenario: Example: [23,a.b.c,,zone.co] \n Use Case: Where We need a New Zone But No Wildcard : [", one_data_line, " ,] Extracted: ", data_list);
            if Validators.is_empty(data_list[3]):
                domain_zone = DEFAULT_ZONE
            elif Validators.validate_domain_name(data_list[3]):
                domain_zone = data_list[3]
            else:
                return False, "Domain Name Regex Violation"
            
            
            # Zone Validation Left
            #if Validators.check_zone(data_list[3]):
            #    domain_zone = data_list[3]
            #else:
            #    return False, None
            
        ''' '''
        domainRecord = DomainRecord(category_id=category_id, domain_name=domain_name, wildcard=wildcard, domain_zone=domain_zone, is_ipaddress = is_ipaddress)   
        return True, domainRecord
        
    except Exception as except_me:
        print("# Trace Logs Left ", except_me)
        return False, None


def db_transaction(domainRecord):
    #print("DB Transaction ", domainRecord);
        
    domainRecord.domain_zone_id = Validators.check_get_zone_id(db_cursor = mydns_cursor, zone_name = domainRecord.domain_zone);
    
    # Create the Zone If Zone is 0 [Not Present] and CREATE_DB_ZONE is triggered with Script 2nd Argument as cz
    if domainRecord.domain_zone_id == 0 and CREATE_DB_ZONE:
        Validators.create_zone(db_cursor = mydns_cursor, zone_name = domainRecord.domain_zone)
        domainRecord.domain_zone_id = Validators.check_get_zone_id(db_cursor = mydns_cursor, zone_name = domainRecord.domain_zone);
    
    if domainRecord.domain_zone_id == 0 and not CREATE_DB_ZONE:
        return False, "No Zone Exists & No Request for New Zone Present, Discarding Result", domainRecord
    
    # Check if Data Exists for this
    is_record_present, present_record = Validators.check_if_rr_exists(db_cursor = mydns_cursor, domain_name = domainRecord.domain_name, zone_id = domainRecord.domain_zone_id)
    
    
    if is_record_present:
        
        # Also Get the Wildcard If Possible [For Future Check]
    
        domainRecord.is_record_present = is_record_present
        _category_code = Validators.get_category_code(domainRecord.category_id, present_record.category_code)
        
        domainRecord.set_category_code(category_code = _category_code)
        domainRecord.set_categories_list_from_db(category_code_from_db = domainRecord.category_code)
    else:
        _category_code = Validators.get_category_code(domainRecord.category_id)
        domainRecord.set_category_code(category_code = _category_code)
        domainRecord.set_categories_list_from_db(category_code_from_db = domainRecord.category_code)
    
    if is_record_present:
        # Check If Update is Required By Checking the category_id against Prev Category_id_List
        #print("Check This: category_id: ", domainRecord.category_id, " , categories_list: ", domainRecord.categories_list_from_db, " Type: ", type(domainRecord.category_id))
        if domainRecord.category_id in domainRecord.categories_list_from_db:
            # Do Not Process the Data
            domainRecord.prev_record_id = present_record.prev_record_id
            return False, "Record & Fields Exists, Skipping Update(No DB Transaction)", domainRecord
            
        else:
            # Update the Record
            try:
                sql_query = "UPDATE rr SET data = %s WHERE name = %s and zone = %s";
                query_params = [domainRecord.category_code, domainRecord.domain_name, domainRecord.domain_zone_id];
                mydns_cursor.execute(sql_query, query_params);
                domainRecord.prev_record_id = present_record.prev_record_id
                return True, "Record Updated", domainRecord
            except Exception as except_me:
                print("# Trace Logs Left: ", except_me)
                domainRecord.prev_record_id = present_record.prev_record_id
                return False, "Skipping Record Update Due to Error: [" + str(except_me) + "]", domainRecord
    else:
        # Insert a New Record
        """ DO Insert """    
        try:
            sql_query = "INSERT INTO rr(zone,name,type,data,aux) VALUES (%s, %s, %s, %s, %s);"
            query_params = [domainRecord.domain_zone_id, domainRecord.domain_name, domainRecord.record_type, domainRecord.category_code, domainRecord.column_aux];
            mydns_cursor.execute(sql_query, query_params);
        except Exception as except_me:
            print("# Trace Logs Left: ", except_me)
            return False, "Skipping Record Insert Due to Error: [" + str(except_me) + "]", domainRecord
    
        # Validate Wildcard is to be added & is Provided in Proper Form [*] or [*.sub]
        if domainRecord.wildcard and not domainRecord.is_ipaddress:
            """ DO Insert of Wildcard [If Not ] """
            try:
                sql_query = "INSERT INTO rr(zone,name,type,data,aux) VALUES (%s, %s, %s, %s, %s);"
                query_params = [domainRecord.domain_zone_id, domainRecord.wildcard + '.' + domainRecord.domain_name, domainRecord.record_type, domainRecord.category_code, domainRecord.column_aux];
                mydns_cursor.execute(sql_query, query_params);
            except Exception as except_me:
                print("# Trace Logs Left: ", except_me)
                return False, "Skipping Record Insert Due to Error: [" + str(except_me) + "]", domainRecord
    
        return True, "Record Inserted", domainRecord
        
    # Check if Data Exists if Wildcard is Present Now [Will handle it Later]
    
    

def process_data(process_file):
    pass
    '''
    # Step 1: Setup Database Connection
    # - If Problem Occurs Send Error
    
    # Step 2: Read the File Line By Line
    # - Skip Comments(Lines Starting with #)
    
    # Step 3: Validate Each Fields of the Line and add it to the Object
    # - Validate if they are correct
    # - Check if Minimum Data Exists -> Category_id & domain_name
    # - Check if All data Follows the Restriction
    # - A) Category_id: Numeric Value
    # - B) domain_name: Follows Domain Name Restriction Since Adding Garbage Domain Name data is Inefficient & Can create Problem
    # - C) wildcard: Important Field Should be accurate like [*] or [*.sub]
    # - D) Zone: We can Add multiple Zones, We want to make sure that their is a Zone of that Name if Not Create One and get the Zone Id and add it to that Zone 
    
    # Step 4: Adding Data to Database
    # Step 4.A) Check If Entry Exists of that Data
            # - If Exists Then Check if we have to Update it
                # - Condition: 1. New Category ID (In New Category)
                #              2. Add Wildcard Now
            # - Else i.e if Not Exists (If New Entry)
                # - Add it with the Category ID
                # - Also Check for Wildcard 
    
    # Here we want to also Log Which Data is Entered in the Database and Which are Not & Possible Error Reason
    # So that we can correct the Data or the Script.
    # 
            
    '''
    # Create Default Zone 
    if Validators.check_get_zone_id(db_cursor = mydns_cursor, zone_name = DEFAULT_ZONE) == 0:
        Validators.create_zone(db_cursor = mydns_cursor, zone_name = DEFAULT_ZONE)
    
    line_counter = 1;
    
    # Read the File
    with open(process_file) as file_obj:    
        for one_data_line in file_obj:
            one_data_line = one_data_line.strip(); # Strip Remove Unnecessary \n & Spaces 
            
            if one_data_line.startswith("#"):
                #print("Skipping Comment Line: ", one_data_line)
                pass
            elif one_data_line == "":
                #print("Skipping Empty Line: ", one_data_line)
                pass
            else:
                result, domainRecord = check_fields(one_data_line)
                if result:
                    trans_status, trans_desc, _domainRecord = db_transaction(domainRecord)
                    _result = "[+]" if trans_status else "[-]"
                    #_result = trans_status ? "[+]" : "[-]"
                    print(line_counter, _result, trans_status, trans_desc, _domainRecord)
                else:
                    print(line_counter, "[-] Data Incorrect: [", one_data_line, "] , Reason: [", domainRecord ,"] -> Processing Next")
            
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
            process_data(process_file=process_file)
        
    else:
        sys.exit("Please Provide A Filename to Process.... \n" + script_usage)
        
    
        
main()