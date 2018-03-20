import ctypes, sys
import os
import urllib.request
import subprocess
import re
import datetime
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if is_admin():
    # Create a list of ad domains from hosts files found online
    def get_ad_domains(src_urls):
        domains = set()
        for src in src_urls:
            entries = [line.decode('utf-8') for line in list(urllib.request.urlopen(src))]
            for entry in entries:
                # If hosts file entry is a valid block rule, add domain to list
                if entry.startswith(('0.0.0.0', '127.0.0.1')):
                    domains.add(entry.split()[1])
        return domains

# Create a list of domains found in the user's DNS cache
    def get_dns_domains():
        dns_cache = subprocess.check_output('ipconfig /displaydns').decode('utf-8')
        # Regex pattern to match domains in the DNS cache
        pattern = '\n\s+(\S+)\r\n\s+-'
        domains = re.findall(pattern, dns_cache)
        return domains

# Create a list of domains currently in the user's hosts file
    def get_cur_domains(hosts_dir):
        os.chdir(hosts_dir)
        domains = set()
        hosts_file = open('hosts', 'r')
        for entry in hosts_file:
            if entry.startswith(('0.0.0.0', '127.0.0.1')):
                domains.add(entry.split()[1])
        hosts_file.close()
        return domains

# Write new domains to the hosts file   
    def write_hosts_file(domains, hosts_dir):
        os.chdir(hosts_dir)
        hosts_file = open('hosts', 'a')
        hosts_file.write('\n# Updated: {}\n'.format(datetime.datetime.now()))
        for dmn in domains:
            hosts_file.write('0.0.0.0 {}\n'.format(dmn))
        hosts_file.close()

    def main():
        hosts_dir = 'C:/Windows/System32/drivers/etc'
        srcs = ['http://winhelp2002.mvps.org/hosts.txt',
            'http://someonewhocares.org/hosts/zero/hosts']
        ad_domains = get_ad_domains(srcs)
        dns_domains = get_dns_domains()
        cur_domains = get_cur_domains(hosts_dir)
        domains_to_add = [dmn for dmn in dns_domains if dmn in ad_domains and dmn not in cur_domains]
        if domains_to_add:
            print ('Adding {} domain(s)...'.format(len(domains_to_add)))
            write_hosts_file(domains_to_add, hosts_dir)

    if __name__ == '__main__':
        main()

else:
    # Re-run the program with admin rights
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, "", None, 1)
