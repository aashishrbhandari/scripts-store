from timeit import default_timer as timer
import os
from hashlib import md5 as md5_hash

status_code_dict = {}

""" ---- ALL Download, Upload(Accessed Blocked) ---- """
total_download_bytes_count = 0
total_upload_bytes_count = 0
total_upload_and_download_bytes_count = 0
total_request_count = 0

total_blocked_download_bytes_count = 0
total_blocked_upload_bytes_count = 0
total_blocked_upload_and_download_bytes_count = 0
total_blocked_request_count = 0

""" ---- ---- """

""" ---- Detailed Stats of website and user-based ---- """
website_stats_dict = {}
user_stats_dict = {}
""" ---- ---- """

""" ---- Simple Table of WebSiteName and Count Stats ---- """
blocked_website_dict = {}
dns_failed_website_dict = {}
conn_failed_website_dict = {}
unknown_cachecode_website_dict = {}
""" ---- ---- """

""" ---- Simple Table of Field and Count Stats ---- """
cache_code_dict = {}
time_steps_stats_dict = {}
useragent_dict = {}
categories_dict = {}
http_method_dict = {}
""" ---- ---- """


""" Filters """

filter_name_reason_dict = {}

"""" username, url, download_size, upload_size, request_count, elapsed_time, filter_name, filter_reason """
filter_name_reason_stats_dict = {}

""" --- --- """


""" [COPIED] To Get The Human Readable Form [Later will be Changed] """


def fmt_bytes_to_hr(num, suffix='B'):
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024.0:
            return "%3.3f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.3f%s%s" % (num, 'Yi', suffix)


""" Convert SafeSquid Log File to Array[List] Also Trimming the DOUBLE_COAT """


def get_array(one_line: str):
    return [one_line_field.strip('"') for one_line_field in one_line.split("\t")]


""" Generate The Status Dict [Key: Value Pair] With HTTP_STATUS: COUNT 
Get Status With the CACHE_CODE """


def status_code_processor(line_array):
    curr_status = line_array[5]
    cache_code = line_array[20]

    if cache_code:
        curr_status_with_cache_code = curr_status + \
            "(" + cache_code + ")"  # Can Be Changed
        curr_status_val = status_code_dict.get(
            curr_status_with_cache_code, None)
        if curr_status_val:
            status_code_dict[curr_status_with_cache_code] = curr_status_val + 1
        else:
            status_code_dict[curr_status_with_cache_code] = 1

    curr_status_val = status_code_dict.get(curr_status, None)
    if curr_status_val:
        status_code_dict[curr_status] = curr_status_val + 1
    else:
        status_code_dict[curr_status] = 1


""" ALL CACHE-CODE Details Get a DICT of it """


def cache_code_processor(line_array):
    curr_cache_code = line_array[20]
    curr_cache_code_val = cache_code_dict.get(curr_cache_code, None)
    if curr_cache_code_val:
        cache_code_dict[curr_cache_code] = curr_cache_code_val + 1
    else:
        cache_code_dict[curr_cache_code] = 1


""" UserAgent Dict """


def useragent_processor(line_array):
    curr_useragent = line_array[15]
    curr_useragent_value = useragent_dict.get(curr_useragent, None)
    if curr_useragent_value:
        useragent_dict[curr_useragent] = curr_useragent_value + 1
    else:
        useragent_dict[curr_useragent] = 1


""" Category Dict [Categories] """


def categories_processor(line_array):
    curr_category_list = line_array[32]
    for one_category in curr_category_list.split(","):
        if one_category != "" and one_category != " " and one_category != "-":
            curr_category_value = categories_dict.get(one_category, None)
            if curr_category_value:
                categories_dict[one_category] = curr_category_value + 1
            else:
                categories_dict[one_category] = 1


""" HTTP Methods Dict [Method] """


def http_method_processor(line_array):
    curr_http_method = line_array[12]
    curr_http_method_value = http_method_dict.get(curr_http_method, None)
    if curr_http_method_value:
        http_method_dict[curr_http_method] = curr_http_method_value + 1
    else:
        http_method_dict[curr_http_method] = 1


""" HTTP Methods Dict [Method] """


def filter_name_reason_processor(line_array):

    curr_cache_code = line_array[20]
    curr_filter_name = line_array[17]
    curr_filter_reason = line_array[18]

    if curr_cache_code == "TCP_DENIED":
        curr_filter_name_reason = curr_filter_name + "|" + curr_filter_reason
        curr_filter_name_reason_value = filter_name_reason_dict.get(
            curr_filter_name_reason, None)
        if curr_filter_name_reason_value:
            filter_name_reason_dict[curr_filter_name_reason] = curr_filter_name_reason_value + 1
        else:
            filter_name_reason_dict[curr_filter_name_reason] = 1


""" Get Website Stats 
Get Details Like: website_name, download_size, upload_size, request_count, elapsed_time
"""


def website_stats_processor(line_array):
    curr_website = line_array[23]
    curr_cache_code = line_array[20]

    if curr_cache_code != "TCP_DENIED" and curr_cache_code != "TCP_DNS_FAILED" and curr_cache_code != "TCP_CONNECTION_FAILED":
        download_bytes = line_array[8]
        upload_bytes = line_array[7]
        elapsed_time = line_array[4]
        curr_website_value = website_stats_dict.get(curr_website, None)

        if curr_website_value:
            prev_this_website_stats = curr_website_value
            website_stats_dict[curr_website] = {
                "d": prev_this_website_stats.get("d") + int(download_bytes),
                "u": prev_this_website_stats.get("u") + int(upload_bytes),
                "rc": prev_this_website_stats.get("rc") + 1,
                "et": prev_this_website_stats.get("et") + int(elapsed_time),
            }
        else:
            website_stats_dict[curr_website] = {
                "d": int(download_bytes),
                "u": int(upload_bytes),
                "rc": 1,
                "et": int(elapsed_time),
            }

    elif curr_cache_code == "TCP_DENIED":

        download_bytes = line_array[8]
        upload_bytes = line_array[7]
        elapsed_time = line_array[4]
        curr_blocked_website_value = blocked_website_dict.get(
            curr_website, None)

        if curr_blocked_website_value:
            prev_this_blocked_website_stats = curr_blocked_website_value
            blocked_website_dict[curr_website] = {
                "d": prev_this_blocked_website_stats.get("d") + int(download_bytes),
                "u": prev_this_blocked_website_stats.get("u") + int(upload_bytes),
                "rc": prev_this_blocked_website_stats.get("rc") + 1,
                "et": prev_this_blocked_website_stats.get("et") + int(elapsed_time),
            }
        else:
            blocked_website_dict[curr_website] = {
                "d": int(download_bytes),
                "u": int(upload_bytes),
                "rc": 1,
                "et": int(elapsed_time),
            }

        """ Previous Code Only SHows Blocked Website and COunt
        curr_blocked_website_value = blocked_website_dict.get(curr_website, None)
        if curr_blocked_website_value:
            blocked_website_dict[curr_website] = curr_blocked_website_value + 1
        else:
            blocked_website_dict[curr_website] = 1
        """

    elif curr_cache_code == "TCP_DNS_FAILED":
        curr_dns_failed_website_value = dns_failed_website_dict.get(
            curr_website, None)
        if curr_dns_failed_website_value:
            dns_failed_website_dict[curr_website] = curr_dns_failed_website_value + 1
        else:
            dns_failed_website_dict[curr_website] = 1

    elif curr_cache_code == "TCP_CONNECTION_FAILED":
        curr_conn_failed_website_value = conn_failed_website_dict.get(
            curr_website, None)
        if curr_conn_failed_website_value:
            conn_failed_website_dict[curr_website] = curr_conn_failed_website_value + 1
        else:
            conn_failed_website_dict[curr_website] = 1

    else:
        curr_website_with_unknown_cache_code = curr_website + \
            "|" + curr_cache_code  # Need To CHeck Later
        curr_unknown_cachecode_website_value = unknown_cachecode_website_dict.get(
            curr_website_with_unknown_cache_code, None)
        if curr_unknown_cachecode_website_value:
            unknown_cachecode_website_dict[curr_website] = curr_unknown_cachecode_website_value + 1
        else:
            unknown_cachecode_website_dict[curr_website] = 1


""" Get User Stats 
Get Details Like: username, website_name, download_size, upload_size, request_count, elapsed_time
"""


def user_stats_processor(line_array):

    curr_username = line_array[11]
    if curr_username == "" or curr_username == " " or curr_username == "-":
        curr_username = line_array[10]
    curr_website = line_array[23]
    curr_cache_code = line_array[20]

    if curr_cache_code != "TCP_DENIED" and curr_cache_code != "TCP_DNS_FAILED" and curr_cache_code != "TCP_CONNECTION_FAILED":
        download_bytes = line_array[8]
        upload_bytes = line_array[7]
        elapsed_time = line_array[4]

        curr_username_website = curr_username + "|" + curr_website
        curr_username_website_value = user_stats_dict.get(
            curr_username_website, None)

        if curr_username_website_value:
            prev_this_user_stats = curr_username_website_value
            user_stats_dict[curr_username_website] = {
                "d": prev_this_user_stats.get("d") + int(download_bytes),
                "u": prev_this_user_stats.get("u") + int(upload_bytes),
                "rc": prev_this_user_stats.get("rc") + 1,
                "et": prev_this_user_stats.get("et") + int(elapsed_time),
            }
        else:
            user_stats_dict[curr_username_website] = {
                "d": int(download_bytes),
                "u": int(upload_bytes),
                "rc": 1,
                "et": int(elapsed_time),
            }


""" Get Filter name & Reason Stats 
Get Details Like: username, url, download_size, upload_size, request_count, elapsed_time, filter_name, filter_reason

filter_name_reason_stats_dict = {}
"""


def filter_name_reason_stats_processor(line_array):

    curr_cache_code = line_array[20]

    if curr_cache_code == "TCP_DENIED":

        curr_username = line_array[11]
        if curr_username == "" or curr_username == " " or curr_username == "-":
            curr_username = line_array[10]
        curr_url = line_array[13]
        curr_filter_name = line_array[17]
        curr_filter_reason = line_array[18]
        curr_download_bytes = line_array[8]
        curr_upload_bytes = line_array[7]
        curr_elapsed_time = line_array[4]

        curr_u_u_f_f = curr_username + curr_url + curr_filter_name + curr_filter_reason

        curr_key_md5 = md5_hash(
            bytes(curr_u_u_f_f, 'utf-8')).hexdigest()  # Full Unique Key

        curr_key_md5_value = filter_name_reason_stats_dict.get(
            curr_key_md5, None)

        if curr_key_md5_value:
            prev_this_filter_stats = curr_key_md5_value

            filter_name_reason_stats_dict[curr_key_md5]["d"] = prev_this_filter_stats.get(
                "d") + int(curr_download_bytes)
            filter_name_reason_stats_dict[curr_key_md5]["u"] = prev_this_filter_stats.get(
                "u") + int(curr_upload_bytes)
            filter_name_reason_stats_dict[curr_key_md5]["rc"] = prev_this_filter_stats.get(
                "rc") + 1
            filter_name_reason_stats_dict[curr_key_md5]["et"] = prev_this_filter_stats.get(
                "et") + int(curr_elapsed_time)
        else:
            filter_name_reason_stats_dict[curr_key_md5] = {
                "un": curr_username,
                "f_n": curr_filter_name,
                "f_r": curr_filter_reason,
                "d": int(curr_download_bytes),
                "u": int(curr_upload_bytes),
                "rc": 1,
                "et": int(curr_elapsed_time),
                "url": curr_url
            }


""" filter_name_reason_stats_dict : To HTML   """


def filter_name_reason_stats_html(filter_name_reason_stats_dict):

    filter_name_reason_stats_dict = {k: v for k, v in sorted(
        filter_name_reason_stats_dict.items(), key=lambda item: item[1]["rc"], reverse=True)}

    table_data = "<tbody>"
    count = 1
    for one_username_key, one_filter_stats in filter_name_reason_stats_dict.items():
        table_data += f'''
        <tr>
            <td> {count}  </td>
            <td> {one_filter_stats.get("un", "NO_USERNAME")} </td>
            <td> {one_filter_stats.get("url", "NO_URL_CHECK")} </td>
            <td data-order="{one_filter_stats.get("d")}"> {fmt_bytes_to_hr(one_filter_stats.get("d"))} </td>
            <td data-order="{one_filter_stats.get("u")}"> {fmt_bytes_to_hr(one_filter_stats.get("u"))} </td>            
            <td> {one_filter_stats.get("f_n")} </td>            
            <td> {one_filter_stats.get("f_r")} </td>            
            <td> {one_filter_stats.get("rc")} </td>            
            <td> {one_filter_stats.get("et")} </td>            
        </tr>
        '''
        count = count + 1

    table_data += "</tbody>"
    full_table = f'''
          <table class="content-table table-sortable">
            <thead>
                <tr>
                    <th>Sr.No.<br />({len(website_stats_dict)})</th>
                    <th>UserName</th>
                    <th>URL</th>
                    <th>Download Size</th>
                    <th>Upload Size</th>
                    <th>Filter Name</th>
                    <th>Filter Reason</th>
                    <th>Request Count</th>
                    <th>Elapsed Time</th>
                </tr>
            </thead>
            {table_data}
          </table>
        '''
    return full_table


# Currently it will also cout bandwidth of Request taht were blocked [Need To CHeck]
def total_bandwidth_processor(line_array):
    upload_bytes = line_array[7]
    download_bytes = line_array[8]

    if line_array[20] != "TCP_DENIED":
        global total_download_bytes_count
        total_download_bytes_count = total_download_bytes_count + \
            int(download_bytes)

        global total_upload_bytes_count
        total_upload_bytes_count = total_upload_bytes_count + int(upload_bytes)

        global total_request_count
        total_request_count = total_request_count + 1
    else:
        global total_blocked_download_bytes_count
        total_blocked_download_bytes_count = total_blocked_download_bytes_count + \
            int(download_bytes)

        global total_blocked_upload_bytes_count
        total_blocked_upload_bytes_count = total_blocked_upload_bytes_count + \
            int(upload_bytes)

        global total_blocked_request_count
        total_blocked_request_count = total_blocked_request_count + 1


def time_steps_stats_processor(line_array):
    date_time = line_array[3]
    curr_date_time_step = date_time[:14]

    download_bytes = line_array[8]
    upload_bytes = line_array[7]
    elapsed_time = line_array[4]

    curr_date_time_step_val = time_steps_stats_dict.get(
        curr_date_time_step, None)
    if curr_date_time_step_val:

        prev_this_download_size = curr_date_time_step_val["d"]
        prev_this_upload_size = curr_date_time_step_val["u"]
        prev_this_req_count = curr_date_time_step_val["rc"]
        prev_this_e_t = curr_date_time_step_val["et"]

        time_steps_stats_dict[curr_date_time_step] = {
            "rc": prev_this_download_size + 1,
            "d": prev_this_download_size + int(download_bytes),
            "u": prev_this_upload_size + int(upload_bytes),
            "et": prev_this_e_t + int(elapsed_time)
        }
    else:
        time_steps_stats_dict[curr_date_time_step] = {
            "rc": 1,
            "d": int(download_bytes),
            "u": int(upload_bytes),
            "et": int(elapsed_time)
        }


def time_steps_stats_html(time_steps_stats_dict):

    time_steps_stats_dict = {k: v for k, v in sorted(
        time_steps_stats_dict.items(), key=lambda item: item[1]["rc"], reverse=True)}

    table_data = "<tbody>"
    count = 1
    for one_time_steps_stats_key, one_time_steps_stats_details in time_steps_stats_dict.items():
        table_data += f'''
        <tr>
            <td> {count}  </td>
            <td> {one_time_steps_stats_key}*</td>
            <td> {one_time_steps_stats_details["rc"]} </td>       
            <td data-order="{one_time_steps_stats_details.get("d")}"> {fmt_bytes_to_hr(one_time_steps_stats_details["d"])} </td>       
            <td data-order="{one_time_steps_stats_details.get("u")}"> {fmt_bytes_to_hr(one_time_steps_stats_details["u"])} </td>
            <td> {one_time_steps_stats_details["et"]} </td>
        </tr>
        '''
        count = count + 1

    table_data += "</tbody>"
    full_table = f'''
          <table class="content-table table-sortable">
            <thead>
                <tr>
                    <th>Sr.No.<br />({len(time_steps_stats_dict)})</th>
                    <th>Time Frame</th>
                    <th>Request Count</th>
                    <th>Download Size</th>
                    <th>Upload Size</th>
                    <th>Elapsed Time (In Millis)</th>
                </tr>
            </thead>
            {table_data}
          </table>
        '''
    return full_table


""" STATUS Dict Stats HTML Table """


def status_code_html(status_dict):

    status_dict = {k: v for k, v in sorted(
        status_dict.items(), key=lambda item: item[1], reverse=True)}

    table_data = "<tbody>"
    count = 1
    for one_status_code_name, one_status_code_count in status_dict.items():
        table_data += f'''
        <tr>
            <td> {count}  </td>
            <td> {one_status_code_name} </td>
            <td> {one_status_code_count} </td>       
        </tr>
        '''
        count = count + 1

    table_data += "</tbody>"
    full_table = f'''
          <table class="content-table table-sortable">
            <thead>
                <tr>
                    <th>Sr.No.<br />({len(status_dict)})</th>
                    <th>Status Code</th>
                    <th>Status Code Count</th>
                </tr>
            </thead>
            {table_data}
          </table>
        '''
    return full_table


""" STATUS Dict Stats HTML Table """


def filter_name_reason_html(filter_name_reason_dict):

    filter_name_reason_dict = {k: v for k, v in sorted(
        filter_name_reason_dict.items(), key=lambda item: item[1], reverse=True)}

    table_data = "<tbody>"
    count = 1
    for one_filter_key, one_filter_count in filter_name_reason_dict.items():
        table_data += f'''
        <tr>
            <td> {count}  </td>
            <td> {one_filter_key.split("|")[0]} </td>
            <td> {one_filter_key.split("|")[1]} </td>             
            <td> {one_filter_count} </td>       
        </tr>
        '''
        count = count + 1

    table_data += "</tbody>"
    full_table = f'''
          <table class="content-table table-sortable">
            <thead>
                <tr>
                    <th>Sr.No.<br />({len(filter_name_reason_dict)})</th>
                    <th>Filter Name</th>
                    <th>Filter Reason</th>
                    <th>Filter Count</th>
                </tr>
            </thead>
            {table_data}
          </table>
        '''
    return full_table


""" All Total Stats Like: total_download_bytes, total_upload_and_download_bytes_count etc"""


def full_bandwidth_html(total_upload_and_download_bytes, total_download_bytes, total_upload_bytes, total_request_count, total_blocked_upload_and_download_bytes, total_blocked_download_bytes, total_blocked_upload_bytes, total_blocked_request_count):
    table_data = "<tbody>"
    table_data += "</tbody>"
    full_table = f'''
          <table class="content-table table-sortable">
            <thead>
                <tr>
                    <th>Sr.No.<br />(1)</th>
                    <th>Total (Download+Upload)(MB)</th>
                    <th>Total Download(MB)</th>
                    <th>Total Upload(MB)</th>
                    <th>Total Request Count</th>
                    <th>Allow/Block</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>1</td>
                    <td>{fmt_bytes_to_hr(total_upload_and_download_bytes)}</td>
                    <td>{fmt_bytes_to_hr(total_download_bytes)}</td>
                    <td>{fmt_bytes_to_hr(total_upload_bytes)}</td>
                    <td>{total_request_count}</td>
                    <td>ALLOWED</td>                    
                </tr>
                <tr>
                    <td>1</td>
                    <td>{fmt_bytes_to_hr(total_blocked_upload_and_download_bytes)}</td>
                    <td>{fmt_bytes_to_hr(total_blocked_download_bytes)}</td>
                    <td>{fmt_bytes_to_hr(total_blocked_upload_bytes)}</td>
                    <td>{total_blocked_request_count}</td>
                    <td>BLOCKED</td>
                </tr>
           </tbody>
            {table_data}
          </table>
        '''
    return full_table


""" website_stats_dict : To HTML   """


def website_stats_html(website_stats_dict):

    website_stats_dict = {k: v for k, v in sorted(
        website_stats_dict.items(), key=lambda item: item[1]["d"], reverse=True)}

    table_data = "<tbody>"
    count = 1
    for one_web_name, one_web_stats in website_stats_dict.items():
        table_data += f'''
        <tr>
            <td> {count}  </td>
            <td> {one_web_name} </td>
            <td data-order="{one_web_stats.get("d")}"> {fmt_bytes_to_hr(one_web_stats.get("d"))} </td>
            <td data-order="{one_web_stats.get("u")}"> {fmt_bytes_to_hr(one_web_stats.get("u"))} </td>            
            <td> {one_web_stats.get("rc")} </td>            
            <td> {one_web_stats.get("et")} </td>            
        </tr>
        '''
        count = count + 1

    table_data += "</tbody>"
    full_table = f'''
          <table class="content-table table-sortable">
            <thead>
                <tr>
                    <th>Sr.No.<br />({len(website_stats_dict)})</th>
                    <th>WebSite Name</th>
                    <th>Download Size</th>
                    <th>Upload Size</th>
                    <th>Request Count</th>
                    <th>Elapsed Time</th>
                </tr>
            </thead>
            {table_data}
          </table>
        '''
    return full_table


""" user_stats_dict : To HTML   """


def user_stats_html(user_stats_dict):

    user_stats_dict = {k: v for k, v in sorted(
        user_stats_dict.items(), key=lambda item: item[1]["d"], reverse=True)}

    table_data = "<tbody>"
    count = 1
    for one_web_username_key, one_web_stats in user_stats_dict.items():
        table_data += f'''
        <tr>
            <td> {count}  </td>
            <td> {one_web_username_key.split("|")[0]} </td>
            <td> {one_web_username_key.split("|")[1]} </td>
            <td data-order="{one_web_stats.get("d")}"> {fmt_bytes_to_hr(one_web_stats.get("d"))} </td>
            <td data-order="{one_web_stats.get("u")}"> {fmt_bytes_to_hr(one_web_stats.get("u"))} </td>            
            <td> {one_web_stats.get("rc")} </td>            
            <td> {one_web_stats.get("et")} </td>            
        </tr>
        '''
        count = count + 1

    table_data += "</tbody>"
    full_table = f'''
          <table class="content-table table-sortable">
            <thead>
                <tr>
                    <th>Sr.No.<br />({len(user_stats_dict)})</th>
                    <th>UserName</th>
                    <th>WebSite Name</th>
                    <th>Download Size</th>
                    <th>Upload Size</th>
                    <th>Request Count</th>
                    <th>Elapsed Time</th>
                </tr>
            </thead>
            {table_data}
          </table>
        '''
    return full_table


def cache_code_html(cache_code_dict):
    # pprint(cache_code_dict)
    cache_code_dict = {k: v for k, v in sorted(
        cache_code_dict.items(), key=lambda item: item[1], reverse=True)}

    table_data = "<tbody>"
    count = 1
    for one_cache_code_name, one_cache_code_count in cache_code_dict.items():
        table_data += f'''
        <tr>
            <td> {count}  </td>
            <td> {one_cache_code_name} </td>
            <td> {one_cache_code_count} </td>
        </tr>
        '''
        count = count + 1

    table_data += "</tbody>"
    full_table = f'''
          <table class="content-table table-sortable">
            <thead>
                <tr>
                    <th>Sr.No.<br />({len(cache_code_dict)})</th>
                    <th>CACHE CODE</th>
                    <th>Count</th>
                </tr>
            </thead>
            {table_data}
          </table>
        '''
    return full_table


"""
blocked_website_dict = {}

"""


def _OLD_blocked_website_html(blocked_website_dict):
    blocked_website_dict = {k: v for k, v in sorted(
        blocked_website_dict.items(), key=lambda item: item[1], reverse=True)}

    table_data = "<tbody>"
    count = 1
    for one_blocked_website_name, one_blocked_website_count in blocked_website_dict.items():
        table_data += f'''
        <tr>
            <td> {count}  </td>
            <td> {one_blocked_website_name} </td>
            <td> {one_blocked_website_count} </td>
        </tr>
        '''
        count = count + 1

    table_data += "</tbody>"
    full_table = f'''
          <table class="content-table table-sortable">
            <thead>
                <tr>
                    <th>Sr.No.<br />({len(blocked_website_dict)})</th>
                    <th>Blocked Website Name</th>
                    <th>Block Count</th>
                </tr>
            </thead>
            {table_data}
          </table>
        '''
    return full_table


"""
blocked_website_dict = {}

"""


def blocked_website_html(blocked_website_dict):

    blocked_website_dict = {k: v for k, v in sorted(
        blocked_website_dict.items(), key=lambda item: item[1]["d"], reverse=True)}

    table_data = "<tbody>"
    count = 1
    for one_blocked_web_name, one_blocked_web_stats in blocked_website_dict.items():
        table_data += f'''
        <tr>
            <td> {count}  </td>
            <td> {one_blocked_web_name} </td>
            <td data-order="{one_blocked_web_stats.get("d")}"> {fmt_bytes_to_hr(one_blocked_web_stats.get("d"))} </td>
            <td data-order="{one_blocked_web_stats.get("u")}"> {fmt_bytes_to_hr(one_blocked_web_stats.get("u"))} </td>            
            <td> {one_blocked_web_stats.get("rc")} </td>            
            <td> {one_blocked_web_stats.get("et")} </td>            
        </tr>
        '''
        count = count + 1

    table_data += "</tbody>"
    full_table = f'''
          <table class="content-table table-sortable">
            <thead>
                <tr>
                    <th>Sr.No.<br />({len(blocked_website_dict)})</th>
                    <th>(Blocked)WebSite Name</th>
                    <th>Download Size</th>
                    <th>Upload Size</th>
                    <th>Request Count</th>
                    <th>Elapsed Time</th>
                </tr>
            </thead>
            {table_data}
          </table>
        '''
    return full_table


"""
dns_failed_website_dict = {}

"""


def dns_failed_website_html(dns_failed_website_dict):
    dns_failed_website_dict = {k: v for k, v in sorted(
        dns_failed_website_dict.items(), key=lambda item: item[1], reverse=True)}

    table_data = "<tbody>"
    count = 1
    for one_dns_failed_website_name, one_dns_failed_website_count in dns_failed_website_dict.items():
        table_data += f'''
        <tr>
            <td> {count}  </td>
            <td> {one_dns_failed_website_name} </td>
            <td> {one_dns_failed_website_count} </td>
        </tr>
        '''
        count = count + 1

    table_data += "</tbody>"
    full_table = f'''
          <table class="content-table table-sortable">
            <thead>
                <tr>
                    <th>Sr.No.<br />({len(dns_failed_website_dict)})</th>
                    <th>DNS Failed Website Name</th>
                    <th>Count</th>
                </tr>
            </thead>
            {table_data}
          </table>
        '''
    return full_table


"""
conn_failed_website_dict = {}
"""


def conn_failed_website_html(conn_failed_website_dict):
    conn_failed_website_dict = {k: v for k, v in sorted(
        conn_failed_website_dict.items(), key=lambda item: item[1], reverse=True)}

    table_data = "<tbody>"
    count = 1
    for one_conn_failed_website_name, one_conn_failed_website_count in conn_failed_website_dict.items():
        table_data += f'''
        <tr>
            <td> {count}  </td>
            <td> {one_conn_failed_website_name} </td>
            <td> {one_conn_failed_website_count} </td>
        </tr>
        '''
        count = count + 1

    table_data += "</tbody>"
    full_table = f'''
          <table class="content-table table-sortable">
            <thead>
                <tr>
                    <th>Sr.No.<br />({len(conn_failed_website_dict)})</th>
                    <th>CONN Failed Website Name</th>
                    <th>Count</th>
                </tr>
            </thead>
            {table_data}
          </table>
        '''
    return full_table


"""
unknown_cachecode_website_dict = {}
"""


def unknown_cachecode_website_html(unknown_cachecode_website_dict):
    unknown_cachecode_website_dict = {k: v for k, v in sorted(
        unknown_cachecode_website_dict.items(), key=lambda item: item[1], reverse=True)}

    table_data = "<tbody>"
    count = 1
    for one_unknown_cachecode_website_name, one_unknown_cachecode_website_count in unknown_cachecode_website_dict.items():
        table_data += f'''
        <tr>
            <td> {count}  </td>
            <td> {one_unknown_cachecode_website_name} </td>
            <td> {one_unknown_cachecode_website_count} </td>
        </tr>
        '''
        count = count + 1

    table_data += "</tbody>"
    full_table = f'''
          <table class="content-table table-sortable">
            <thead>
                <tr>
                    <th>Sr.No.<br />({len(unknown_cachecode_website_dict)})</th>
                    <th>UNKNOWN Website Name</th>
                    <th>Count</th>
                </tr>
            </thead>
            {table_data}
          </table>
        '''
    return full_table


"""
useragent_dict = {}

"""


def useragent_html(useragent_dict):
    #useragent_dict = {k: v for k, v in sorted(useragent_dict.items(), key=lambda item: item[1], reverse=True)}

    table_data = "<tbody>"
    count = 1
    for one_useragent_name, one_useragent_count in useragent_dict.items():
        table_data += f'''
        <tr>
            <td> {count}  </td>
            <td> {one_useragent_name} </td>
            <td> {one_useragent_count} </td>
        </tr>
        '''
        count = count + 1

    table_data += "</tbody>"
    full_table = f'''
          <table class="content-table table-sortable">
            <thead>
                <tr>
                    <th>Sr.No.<br />({len(useragent_dict)})</th>
                    <th>UserAgent</th>
                    <th>Count</th>
                </tr>
            </thead>
            {table_data}
          </table>
        '''
    return full_table


"""
categories_dict = {}
"""


def categories_html(categories_dict):
    #useragent_dict = {k: v for k, v in sorted(useragent_dict.items(), key=lambda item: item[1], reverse=True)}

    table_data = "<tbody>"
    count = 1
    for one_category_name, one_category_count in categories_dict.items():
        table_data += f'''
        <tr>
            <td> {count}  </td>
            <td> {one_category_name} </td>
            <td> {one_category_count} </td>
        </tr>
        '''
        count = count + 1

    table_data += "</tbody>"
    full_table = f'''
          <table class="content-table table-sortable">
            <thead>
                <tr>
                    <th>Sr.No.<br />({len(categories_dict)})</th>
                    <th>Category Name</th>
                    <th>Count</th>
                </tr>
            </thead>
            {table_data}
          </table>
        '''
    return full_table


"""
http_method_dict = {}
"""


def http_method_html(http_method_dict):
    #useragent_dict = {k: v for k, v in sorted(useragent_dict.items(), key=lambda item: item[1], reverse=True)}

    table_data = "<tbody>"
    count = 1
    for one_http_method_name, one_http_method_count in http_method_dict.items():
        table_data += f'''
        <tr>
            <td> {count}  </td>
            <td> {one_http_method_name} </td>
            <td> {one_http_method_count} </td>
        </tr>
        '''
        count = count + 1

    table_data += "</tbody>"
    full_table = f'''
          <table class="content-table table-sortable">
            <thead>
                <tr>
                    <th>Sr.No.<br />({len(http_method_dict)})</th>
                    <th>HTTP Method</th>
                    <th>Count</th>
                </tr>
            </thead>
            {table_data}
          </table>
        '''
    return full_table


""" Create The Actual Report """


def create_html_template(file_name, dir_path="."):

    result_html = f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>SafeSquid Log Reports Details</title>

            <style>
                * {{
                    box-sizing: border-box;
                    font-family: sans-serif; /* Change your font family */
                }}

                body {{
                    margin: 0;
                    font-family: sans-serif;
                }}

                .content-table {{
                  border-collapse: collapse;
                  margin: 25px 0;
                  font-size: 0.9em;
                  /*min-width: 400px;*/
                  border-radius: 5px 5px 0 0;
                  overflow: hidden;
                  box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
                }}

                .content-table thead tr {{
                  background-color: #009879;
                  color: #ffffff;
                  text-align: left;
                  font-weight: bold;
                }}

                .content-table th,
                .content-table td {{
                  padding: 12px 15px;
                  max-width: 420px;
                  white-space: pre-wrap;
                  word-wrap: break-word;
                  transition: text-shadow .3s;
                  min-width: 140px;
                }}

                .content-table tbody tr {{
                  border-bottom: 1px solid #dddddd;
                }}

                .content-table tbody tr:nth-of-type(even) {{
                  background-color: #f3f3f3;
                }}

                .content-table tbody tr:last-of-type {{
                  border-bottom: 2px solid #009879;
                }}

                .content-table tbody tr.active-row {{
                  font-weight: bold;
                  color: #009879;
                }}
                
                .content-table tbody tr:hover {{
                  /*font-weight: bold;*/
                  text-shadow: 0 0 0.6px #009879, 0 0 .25px #009879;
                  color: #009879;
                }}
                
                tr > td:first-child, tr > th:first-child {{
                  min-width: 75px!important;
                }}

                .web-content-stats {{
                    display: flex;
                    gap: 1rem;
                    margin: 8px;
                }}
                
                .table-of-stats {{
                    margin: 10px;
                    border: 2px solid #009879;
                    padding: 10px;
                    border-radius: 10px;
                    box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
                }}
                   
                /***
                Extra For DataTables
                ****/
                
                .page-link {{
                    color: #009987!important;
                    background-color: #fff!important;
                    border: 1px solid #dee2e6!important;
                }}
                
                .page-item.active .page-link {{
                    color: #fff!important;
                    background-color: #009987!important;
                    border-color: #009987!important;
                }}
                
                
                    
            </style>

        </head>
        <body>
            
            <div class="web-content-stats">
                <div style="display: flex; flex-direction: column; gap: 1rem;">
                    <div>
                        <div class="table-of-stats">
                        {full_bandwidth_html(total_upload_and_download_bytes_count, total_download_bytes_count, total_upload_bytes_count, total_request_count, total_blocked_upload_and_download_bytes_count, total_blocked_download_bytes_count, total_blocked_upload_bytes_count, total_blocked_request_count)}
                        </div>
                    </div>
                    
                    <div>
                        <div class="table-of-stats">
                            {http_method_html(http_method_dict)}
                        </div>
                    </div>
                    
                    <div>
                        <div class="table-of-stats">
                            {cache_code_html(cache_code_dict)}
                        </div>
                    </div>
                    
                </div>
                
                <div>
                    <div class="table-of-stats">
                        {time_steps_stats_html(time_steps_stats_dict)}
                    </div>
                </div>
                
                <div>
                    <div class="table-of-stats">
                        {blocked_website_html(blocked_website_dict)}
                    </div>
                </div>
                
                <div>
                    <div class="table-of-stats">
                        {dns_failed_website_html(dns_failed_website_dict)}
                    </div>
                </div>
                
                <div>
                    <div class="table-of-stats">
                        {conn_failed_website_html(conn_failed_website_dict)}
                    </div>
                </div>
                
                <div>
                   <div class="table-of-stats">
                        {unknown_cachecode_website_html(unknown_cachecode_website_dict)}
                    </div>
                </div>

                <div>
                    <div class="table-of-stats">
                        {useragent_html(useragent_dict)}
                    </div>
                </div>
                
                <div>
                    <div class="table-of-stats">
                        {categories_html(categories_dict)}
                    </div>
                </div>

                <div>
                    <div class="table-of-stats">
                        {filter_name_reason_html(filter_name_reason_dict)}
                    </div>
                </div>

                <div>
                    <div class="table-of-stats">
                        {filter_name_reason_stats_html(filter_name_reason_stats_dict)}
                    </div>
                </div>
                
                <div>
                    <div class="table-of-stats">
                        {website_stats_html(website_stats_dict)}
                    </div>
                </div>

                <div>
                    <div class="table-of-stats">
                        {user_stats_html(user_stats_dict)}
                    </div>
                </div>

            </div>
            
        </body>
        
        <link href="bootstrap.min.css" rel="stylesheet">

        <link href="datatables.bootstrap4.min.css" rel="stylesheet">

        <!-- Bootstrap core JavaScript-->
        <script src="jquery.min.js"></script>

        <!-- Page level plugin JavaScript-->
        <script src="jquery.datatables.min.js"></script>

        <script src="datatables.bootstrap4.min.js"></script>
        <script>
            $(document).ready(function () {{
                $('.content-table').DataTable();
            }});
        </script>
    
        </html>
    '''

    f = open(f"{dir_path}\\{file_name}.html", "w")
    f.write(result_html)
    f.close()


def create_reports():
    """
        Step1: Create Dir a having all data 
        Step2: Create all respective script(js), css and html

        <filename>-reports/ 
            js/
            css/
            data/
            <filename>-reports.html
    """
    os.mkdir(path)
    pass


def process_log_file(file_dir, file_name):

    file_name_with_path = f'{file_dir}{file_name}'
    with open(file_name_with_path) as file_obj:
        for one_line in file_obj:
            curr_line_array = get_array(one_line)
            try:
                if len(curr_line_array) == 37 and curr_line_array[0] != "record_id":
                    status_code_processor(curr_line_array)
                    cache_code_processor(curr_line_array)
                    useragent_processor(curr_line_array)
                    categories_processor(curr_line_array)
                    http_method_processor(curr_line_array)
                    website_stats_processor(curr_line_array)
                    user_stats_processor(curr_line_array)
                    total_bandwidth_processor(curr_line_array)
                    time_steps_stats_processor(curr_line_array)
                    filter_name_reason_processor(curr_line_array)
                    filter_name_reason_stats_processor(curr_line_array)
            except Exception as e:
                print(e)
                print("An exception occurred While Processing Line: ",
                      curr_line_array)


file_dir = 'reports\\'
file_name = 'sample-1000-ext.log'

start = timer()

process_log_file(file_dir, file_name)

end = timer()

# Calc the Download [Accessed & Blocked] Size
total_upload_and_download_bytes_count = total_download_bytes_count + \
    total_upload_bytes_count
total_blocked_upload_and_download_bytes_count = total_blocked_download_bytes_count + \
    total_blocked_upload_bytes_count

print("Start Creating HTML Template.....")
create_html_template(file_name, dir_path=file_dir)  # Create HTML File
print(end - start)
