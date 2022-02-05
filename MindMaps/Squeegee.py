import platform
import socket
import json
import re
import uuid
import psutil
import logging
import wmi
from datetime import datetime

# -------------------------
# Jinja2
# -------------------------

from jinja2 import Environment, FileSystemLoader
template_dir = 'Templates/'
env = Environment(loader=FileSystemLoader(template_dir))
squeegee_template = env.get_template('Squeegee.j2')

# -------------------------
# WMI / Win Reg
# -------------------------
c = wmi.WMI ()

def getSystemInfo():
    try:
        info={}
        info['partition_list'] = []
        info['interface_list'] = []
        info['processes'] = []
        info['auto_services'] = []
        info['startup'] = []
        info['registry'] = []
        info['sound_cards'] = []
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
            info[f'Core {i}']= percentage
        info['total_cpu_usage'] = str(psutil.cpu_percent())+"%"
# Memory
        info['total_ram']=str(round(psutil.virtual_memory().total / (1024.0 **3)))+" GB"
        info['available_ram']=str(round(psutil.virtual_memory().available / (1024.0 **3)))+" GB"
        info['used_ram']=str(round(psutil.virtual_memory().used / (1024.0 **3)))+" GB"
        info['ram_percentage']=str(psutil.virtual_memory().percent)+"%"
        info['total_swap']=str(round(psutil.swap_memory().total / (1024.0 **3)))+" GB"
        info['available_swap']=str(round(psutil.swap_memory().free / (1024.0 **3)))+" GB"
        info['used_swap']=str(round(psutil.swap_memory().used / (1024.0 **3)))+" GB"
        info['swap_percentage']=str(psutil.swap_memory().percent)+"%"
# Disk
        allPartitions=psutil.disk_partitions()
        for partition in allPartitions:
            info['partition_list'].append(f'Device: { partition.device }')
            info['partition_list'].append(f'Mountpoint: { partition.mountpoint }')
            info['partition_list'].append(f'File System Type: { partition.fstype }')
            try:
                partitionUsage = psutil.disk_usage(partition.mountpoint)
                info['partition_list'].append(f'Total: { partitionUsage.total }')
                info['partition_list'].append(f'Used: { partitionUsage.used }')
                info['partition_list'].append(f'Free: { partitionUsage.free }')
                info['partition_list'].append(f'Percent: { partitionUsage.percent } %')
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
            info['interface_list'].append(f'Interface: { interface_name }')
            for address in interface_addresses:
                if str(address.family) == 'AddressFamily.AF_INET':
                    info['interface_list'].append(f'IP Address: { address.address }')
                    info['interface_list'].append(f'Subnet Mask: { address.netmask }')
                elif str(address.family) == 'AddressFamily.AF_PACKET':
                    info['interface_list'].append(f'MAC Address: { address.address }')
                    info['interface_list'].append(f'Subet Mask: { address.netmask }')
        ## statistics since boot
        net_io = psutil.net_io_counters()
        info['total_bytes_sent']=str(round(net_io.bytes_sent/ (1024.0 **3)))+" GB"
        info['total_bytes_received']=str(round(net_io.bytes_recv/ (1024.0 **3)))+" GB"
# Processes 
        for process in c.Win32_Process():
            info['processes'].append(f'Process Name: { process.Name }')
            info['processes'].append(f'Process ID: { process.ProcessId }')
# Automatic Startup Services and State
        for service in c.Win32_Service():
            info['auto_services'].append(f'Service Name: { service.Name } State: { service.State }')
# Startup
        for app in c.Win32_StartupCommand ():
            info['startup'].append(f'Location: { app.Location }')
            info['startup'].append(f'Caption: { app.Caption }')
            info['startup'].append(f'Command: { app.Command }')
# Graphics Card
        for detail in c.Win32_VideoController ():
            info['video_adapter_compatibility'] = detail.AdapterCompatibility
            info['video_adapter_DAC_type'] = detail.AdapterDACType
            info['video_adapter_RAM'] = detail.AdapterRAM
            info['video_adapter_caption'] = detail.Caption
            info['video_adapter_current_bits_per_pixel'] = detail.CurrentBitsPerPixel
            info['video_adapter_current_horizon'] = detail.CurrentHorizontalResolution
            info['video_adapter_current_number_colors'] = detail.CurrentNumberOfColors
            info['video_adapter_current_refresh_rate'] = detail.CurrentRefreshRate
            info['video_adapter_current_scan_mode'] = detail.CurrentScanMode
            info['video_adapter_current_vertical'] = detail.CurrentVerticalResolution
            info['video_adapter_description'] = detail.Description
            info['video_adapter_deviceid'] = detail.DeviceID
            info['video_adapter_dither'] = detail.DitherType
            info['video_adapter_driver_date'] = detail.DriverDate
            info['video_adapter_driver_version'] = detail.DriverVersion
            info['video_adapter_inf_filename'] = detail.InfFilename
            info['video_adapter_inf_section'] = detail.InfSection
            info['video_adapter_drivers'] = detail.InstalledDisplayDrivers
            info['video_adapter_max_refresh'] = detail.MaxRefreshRate
            info['video_adapter_min_refresh'] = detail.MinRefreshRate
            info['video_adapter_mono'] = detail.Monochrome
            info['video_adapter_name'] = detail.Name
            info['video_adapter_pnpid'] = detail.PNPDeviceID
            info['video_adapter_status'] = detail.Status
            info['video_adapter_arch'] = detail.VideoArchitecture
            info['video_adapter_memory'] = detail.VideoMemoryType
            info['video_adapter_mode'] = detail.VideoModeDescription
            info['video_adapter_processor'] = detail.VideoProcessor
# Graphics Card
        for detail in c.Win32_SoundDevice ():
            info['sound_cards'].append(f'Caption: { detail.Caption }')
            info['sound_cards'].append(f'Description: { detail.Description }')
            info['sound_cards'].append(f'Device ID: { detail.DeviceID }')
            info['sound_cards'].append(f'Manufacturer: { detail.Manufacturer }')
            info['sound_cards'].append(f'Name: { detail.Name }')
            info['sound_cards'].append(f'Plug N Play DeviceID: { detail.PNPDeviceID }')
            info['sound_cards'].append(f'Power Management Supported: { detail.PowerManagementSupported }')
            info['sound_cards'].append(f'Product Name: { detail.ProductName }')
            if detail.Status:
                info['sound_cards'].append(f'Status: { detail.Status }')
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

# -------------------------
# Pass to Jinja2 Template 
# -------------------------

parsed_output = squeegee_template.render(systemInfo = systemInfo)

# -------------------------
# Save the markdown file
# -------------------------

with open(f"Windows/{ systemInfo['hostname'] }.md", "w") as fh:
    fh.write(parsed_output)               
    fh.close()