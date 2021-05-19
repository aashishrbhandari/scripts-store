"""
from timeit import default_timer as timer

status_dict_var = {};


def get_array(one_line: str):
    return one_line.split("\t")



def status_dict(line_array):
    print(len(line_array))
    curr_status = line_array[5]
    print(curr_status)
    curr_status_val = status_dict_var.get(curr_status, None)
    print("Val is: ", curr_status_val)
    if curr_status_val not None:
        print("if: ", curr_status_val)
        status_dict_var[curr_status] = curr_status_val + 1
    else:
        print("else")
        status_dict_var[curr_status] = '1'



def read_file():
    print_it = True
    with open('20190408130737-extended-GU.log') as file_obj:
        for one_line in file_obj:
            curr_line_array = get_array(one_line)
            if print_it:
                print(curr_line_array)
                print_it = False
            status_dict(curr_line_array)
            

start = timer()
read_file()
print(status_dict_var)
end = timer()
print(end - start)

'''
for i in range(10):
    start = timer()
    read_file()
    end = timer()
    print("Time Taken: ",end - start)
    
 
'''
"""
