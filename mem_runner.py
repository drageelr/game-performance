import sys
import subprocess
import csv
import time
import pprint
import datetime

csv_data = []

def inline_data_ext(data_str, delim, double_split = False):
    end_index = data_str.index(delim) + len(delim)
    temp_ext = data_str[end_index:]
    if not double_split:
        return temp_ext.lstrip().split(' ')[0]
    else:
        return temp_ext.lstrip().split(' ')[0].split('\n')[0]

def extract_proc(data_list):
    '''
    MemTotal:       Line 1
    MemFree:        Line 2
    MemAvailable:   Line 3
    SwapTotal:      Line 15
    SwapFree:       Line 16
    '''
    arg_list = ['MemTotal:', 'MemFree:', 'MemAvailable:', 'SwapTotal:', 'SwapFree:']

    data_str = '\n'.join(data_list)

    ext_list = []

    for arg in arg_list:
        ext_list.append(inline_data_ext(data_str, arg))

    return ext_list

def extract_dumpsys(data_list):
    '''
    Total PSS:      Line 36
    Total Swap PSS: Line 36
    '''
    line = '\n'.join(data_list)
    pss = inline_data_ext(line, 'TOTAL:', True)
    swap_pss = inline_data_ext(line, 'PSS:', True)
    return [pss, swap_pss]

def command_executor(command_list):
    process = subprocess.Popen(command_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    data_list = []
    while True:
        output = process.stdout.readline()
        # print(output.strip())
        data_list.append(output.strip())
        # Do something else
        return_code = process.poll()
        if return_code is not None:
            # print('RETURN CODE', return_code)
            # Process has finished, read rest of the output 
            return data_list

def exec_dumpsys(proc_name):
    return command_executor(['adb', 'shell', 'dumpsys', 'meminfo', proc_name])

def exec_proc():
    return command_executor(['adb', 'shell', 'cat', '/proc/meminfo'])

def save_csv(file_name):
    with open(file_name, 'w') as csv_file:
        file_writer = csv.writer(csv_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        file_writer.writerow(['Timestamp', 'Total PSS', 'Total Swap PSS', 'MemTotal', 'MemFree', 'MemAvailable', 'SwapTotal', 'SwapFree'])
        for data in csv_data:
            file_writer.writerow(data)
    print('Data written to file:', file_name)

def run_algo(proc_name, count, delay_sec):
    time_start = time.time()
    for i in range(count):
        time_before = time.time()
        data_dumpsys = exec_dumpsys(proc_name)
        data_proc = exec_proc()
        time_after = time.time()
        time_avg = (time_after + time_before) / 2
        ts = time_avg - time_start
        data_dumpsys_list = extract_dumpsys(data_dumpsys)
        data_proc_list = extract_proc(data_proc)
        print('tim:', ts)
        print('Dumpsys:', data_dumpsys_list)
        print('Proc:', data_proc_list)
        csv_data.append([ts] + data_dumpsys_list + data_proc_list)
        time.sleep(delay_sec)

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print('Illegal number of arguments')
        print('Args: <proc_name> <count> <delay_sec> <out_file_name>')
        exit()

    run_algo(sys.argv[1], int(sys.argv[2]), float(sys.argv[3]))
    save_csv(sys.argv[4])