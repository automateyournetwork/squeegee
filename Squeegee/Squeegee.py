import platform
import socket
import json
import re
import uuid
import psutil
import logging
from datetime import datetime

def getSystemInfo():
    try:
        info={}
# System
        info['system']=platform.system()
        info['platform']=platform.platform()
        info['platform_release']=platform.release()
        info['platform_version']=platform.version()
        info['architecture']=platform.machine()
# CPU
        info['processor']=platform.processor()
        info['phys_cores']=psutil.cpu_count(logical=False)
        info['total_cores']=psutil.cpu_count(logical=True)
        cpuFreq = psutil.cpu_freq()
        info['max_cpu_freq'] = cpuFreq.max
        info['min_cpu_freq'] = cpuFreq.min
        for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
            info[f'Core_{i}']= percentage
        info['total_cpu_usage'] = psutil.cpu_percent()
# Memory
        info['total_ram']=str(round(psutil.virtual_memory().total / (1024.0 **3)))+" GB"
        info['available_ram']=str(round(psutil.virtual_memory().available / (1024.0 **3)))+" GB"
        info['used_ram']=str(round(psutil.virtual_memory().used / (1024.0 **3)))+" GB"
        info['ram_percentage']=str(psutil.virtual_memory().percent)
        info['total_swap']=str(round(psutil.swap_memory().total / (1024.0 **3)))+" GB"
        info['available_swap']=str(round(psutil.swap_memory().free / (1024.0 **3)))+" GB"
        info['used_swap']=str(round(psutil.swap_memory().used / (1024.0 **3)))+" GB"
        info['swap_percentage']=str(psutil.swap_memory().percent)
# Disk
        info['all_partitions']=psutil.disk_partitions()
        for partition in info['all_partitions']:
            info[f'device_{ partition.device }']=partition.device
            info[f'mountpoint_{ partition.device }']=partition.mountpoint
            info[f'file_system_type_{ partition.device }']=partition.fstype
            try:
                partitionUsage = psutil.disk_usage(partition.mountpoint)
                info[f'total_partition_total_{ partition.device }']=str(round(partitionUsage.total / (1024.0 **3)))+" GB"
                info[f'total_partition_used_{ partition.device }']=str(round(partitionUsage.used / (1024.0 **3)))+" GB"
                info[f'total_partition_free_{ partition.device }']=str(round(partitionUsage.free / (1024.0 **3)))+" GB"
                info[f'total_partition_percent_{ partition.device }']=partitionUsage.percent
            except PermissionError:
                # this can be catched due to the disk that
                # isn't ready
                continue
        disk_io = psutil.disk_io_counters()
        info['total_disk_read']=str(round(disk_io.read_bytes / (1024.0 **3)))+" GB"
        info['total_disk_write']=str(round(disk_io.write_bytes / (1024.0 **3)))+" GB"    
# Network
        info['hostname']=socket.gethostname()
        ifAddrs = psutil.net_if_addrs()
        for interface_name, interface_addresses in ifAddrs.items():
            for address in interface_addresses:
                if str(address.family) == 'AddressFamily.AF_INET':
                    info[f'{interface_name}_ip_address']=address.address
                    info[f'{interface_name}_netmask']=address.netmask
                    info[f'{interface_name}_default_gateway']=address.broadcast
                elif str(address.family) == 'AddressFamily.AF_PACKET':
                    info[f'{interface_name}_mac_address']=address.address
                    info[f'{interface_name}_netmask']=address.netmask
                    info[f'{interface_name}_default_mac']=address.broadcast
        ## statistics since boot
        net_io = psutil.net_io_counters()
        info['total_bytes_sent']=str(round(net_io.bytes_sent/ (1024.0 **3)))+" GB"
        info['total_bytes_received']=str(round(net_io.bytes_recv/ (1024.0 **3)))+" GB"

# Boot Time
        tempTime = psutil.boot_time()
        bt = datetime.fromtimestamp(tempTime)
        info['boot_year'] = bt.year
        info['boot_month'] = bt.month
        info['boot_day'] = bt.day
        info['boot_hour'] = bt.hour
        info['boot_minute'] = bt.minute
        info['boot_second'] = bt.second
        return json.dumps(info)
    except Exception as e:
        logging.exception(e)

systemInfo = json.loads(getSystemInfo())
print (systemInfo)