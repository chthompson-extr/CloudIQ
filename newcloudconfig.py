#!/usr/bin/env python
import exsh
import sys
import re
from time import sleep
version = exsh.clicmd('show version detail', capture=True)

def main(): 
    def snmpconfig():
        print('Getting ready to configure SNMP for CloudIQ....')
        time.sleep(2)
        exsh.clicmd('enable snmp access snmp-v1v2c', True)
        exsh.clicmd('enable snmp access snmpv3', True)
        exsh.clicmd('enable snmp access snmpv3', True)
        exsh.clicmd('enable snmp access snmpv3', True)
        exsh.clicmd('enable snmpv3 default-group', True)
        exsh.clicmd('configure snmpv3 add access "admin" sec-model usm sec-level priv', True)
        exsh.clicmd('configure snmpv3 add access "initial" sec-model usm sec-level noauth', True)
        exsh.clicmd('configure snmpv3 add access "initial" sec-model usm sec-level authnopriv', True)
        exsh.clicmd('configure snmpv3 add access "v1v2c_ro" sec-model snmpv1 sec-level noauth', True)
        exsh.clicmd('configure snmpv3 add access "v1v2c_ro" sec-model snmpv2c sec-level noauth', True)
        exsh.clicmd('configure snmpv3 add access "v1v2c_rw" sec-model snmpv1 sec-level noauth', True)
        exsh.clicmd('configure snmpv3 add access "v1v2c_rw" sec-model snmpv2c sec-level noauth', True)
        exsh.clicmd('configure snmpv3 add group "v1v2c_ro" user "v1v2c_ro" sec-model snmpv1', True)
        exsh.clicmd('configure snmpv3 add group "v1v2c_rw" user "v1v2c_rw" sec-model snmpv1', True)
        exsh.clicmd('configure snmpv3 add group "v1v2c_ro" user "v1v2c_ro" sec-model snmpv2c', True)
        exsh.clicmd('configure snmpv3 add group "v1v2c_rw" user "v1v2c_rw" sec-model snmpv2c', True)
        exsh.clicmd('configure snmpv3 add access "v1v2cNotifyGroup" sec-model snmpv1 sec-level noauth', True)
        exsh.clicmd('configure snmpv3 add access "v1v2cNotifyGroup" sec-model snmpv2c sec-level noauth', True)
        snmpconfig = exsh.clicmd('show configuration snmp', capture=True)
        print('This is your new SNMP configuration: ')
        print(snmpconfig)
    
    def cloud_connect(vr):
        cloud_status = exsh.clicmd('show iqagent', capture=True)
        print('Trying to gather output of connection status to CloudIQ...')
        print('Please wait 15 seconds while status updates......')
        time.sleep(15)
        print(cloud_status)
    def cloud_connect30(vr):
        cloud_30 = exsh.clicmd('show process iqagent', capture=True)
        print('Trying to gather output of connection status to CloudIQ...')
        print('Please wait 15 seconds while status updates......')
        time.sleep(15)
        print(cloud_30)
    
    
    def check_ip(ip):
        """
        check_ip is called from all_check.
        check_ip takes arguments src_ip and dst_ip from acl_data one at a time and parses through
        both variables to make sure they are correct ip addresses.
        Returns True if IP is correct, returns False if IP is wrong format.
        """
        ip = ip.split('.')

        if len(ip) != 4:
            return False
        for ock in ip:
            if not ock.isdigit():
                return False
            i = int(ock)
            if i < 0 or i > 255:
                return False
        return True
        
        
    def dns_vr_mgmt():
        print('Testing DNS for VR Vr-Mgmt')
        dnsvrd = exsh.clicmd('ping vr vr-Mgmt google.com', capture=True)
        if str('host name') or str('transmit error') in dnsvrd:
            dnsconf= raw_input('DNS is not able to resolve CloudiQ, would you like this script to reconfigure DNS? {y} to continue and (n) to exit: ')
            if dnsconf.lower() == 'y':
                print('Configuring DNS for VR-Mgmt')
               
                time.sleep(2)
                exsh.clicmd('configure dns-client add name-server 1.1.1.1 vr VR-Mgmt')
                exsh.clicmd('configure dns-client add name-server 4.2.2.2 vr VR-Mgmt')
                exsh.clicmd('create process iqagent python-module exos.apps.iqagent start auto vr VR-MGMT')
                dnsvrd2 = exsh.clicmd('ping vr vr-mgmt google.com', capture=True)
                if str('host name') in dnsvrd2:
                    print('Unable to resolve DNS, please verify this switch has internet connectivity')
                    main()
                elif str('transmit error') in dnsvrd2:
                    print('Unable to resolve DNS, please verify this switch has internet connectivity and correct VR was choosen')
                    main()
                elif str('bytes from') in dnsvrd2:
                    print('DNS is now working as expected')
                    pass
                else:
                    print('Error in script, please run again')
                    main()
            else:
                main()
        elif str('bytes from') in dnsvrd:
            print('DNS is working as expected')
        elif str('transmit error') in dnssrd:
                    print('Unable to resolve DNS, please verify this switch has internet connectivity and correct VR was choosen')    
        else:
            print('Error in script, please run again')
            main()
    def vr_choice():
        
        vr = raw_input('Which VR are you using to connect to the CloudIq? Press (1) for VR-Default\n Press (2) for VR VR-Mgmt')
        
        if vr == '1':
            vr = 'VR-Default'
        elif vr == '2':
            vr = 'VR-Mgmt'
        else:
            print('Please enter 1 or 2')
            snmpconfig()
        return vr
        
    print('This tool will assist in configuring and verifying connectivity to ExtremeCloudIQ ')
    dec = raw_input('Would you like to configure snmp to connect to CloudIQ? Press (y) to configure, (c) to continue without configuring or (x) to quit: ')
    if dec.lower() == 'y':
        snmpconfig()
    elif dec.lower() == 'c':
        pass
    elif dec.lower() == 'x':
        return
    else:
        pass
    vr_choice()
    dns_dec = raw_input('Would you like to configure DNS servers as well?  (y) for yes or (n) for no')
    if dns_dec.lower() == 'y':
        dns_server = raw_input('Which DNS servers would you like to configure ')
        check_dns = check_ip(dns_server)
        
        if check_dns:
            print('Configuring DNS for {0}'.format(vr))
            time.sleep(2)
            exsh.clicmd('configure dns-client add name-server {0} vr {1}'.format(dns_server,vr))
            
        else:
            pass
    else:
        pass
        
    
    patch11 = re.findall('ExtremeXOS version 30.6.1.11 30.6.1.11-patch1-11', version)
    if patch11:
        vr = raw_input('You are on 30.6.1.11-patch1-11.  Which VR are you using to to connect to CloudIQ? Enter (1) for VR-Default or (2) for VR-Mgmt? ')
        if vr == '1':
            exsh.clicmd('configure iqagent server vr VR-Default', True)
            dns_vr_default()
            cloud_connect()
        elif vr == '2':
            exsh.clicmd('configure iqagent server vr VR-Mgmt', True)
            dns_vr_mgmt()
            cloud_connect()
        elif vr != '1' or '2':
            print('Please enter 1 or 2, exiting script')
            return        
        else:
            pass
    elif False:
        dns = raw_input('You are on 30.x. Which VR are you using to to connect to CloudIQ? Enter (1) for VR-Default or (2) for VR-Mgmt? ')
        if dns == '1':
            dns_vr_default()
            cloud_connect30()
        elif dns == '2':
            dns_vr_mgmt()
            cloud_connect30()
        else:
            pass
        
    else:
        pass
          
  
    
if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        # catch SystemExit to prevent EXOS shell from exiting to the login prompt
        pass