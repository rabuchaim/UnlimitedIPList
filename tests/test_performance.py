#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from unlimitediplist import UnlimitedIPList

##──── TESTS ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
import socket, struct, random, time
def randomipv4():
    return socket.inet_ntoa(struct.pack(">L", random.randint(16777216, 3758096383)))
def randomipv6():
    return ":".join([f"{random.randint(0, 0xffff):04x}" for _ in range(8)])

if __name__ == "__main__":
    max_ips = 200000
    # creates a list with {max_ips} random ipv4 and ipv6 addresses
    start_time = time.monotonic()
    print(f"\n- Preparing an IP addressess list a with {max_ips} randomic ipv4 and ipv6 addresses... ", end="", flush=True)
    ip_network_list, ip_random_list = [], []
    ip_random_list.extend([randomipv4() for i in range(int(max_ips / 2))])
    ip_random_list.extend([randomipv6() for i in range(int(max_ips / 2))])
    random.shuffle(ip_random_list)
    print(f"Done in {'%.6f'%(time.monotonic()-start_time)} second(s)!")

    # creates an IP networks list with {max_ips/2} random ipv4/ipv6 network addresses
    start_time = time.monotonic()
    print(f"- Creating an IP network list with {int(max_ips/2)} networks based on IP addressess list... ", end="", flush=True)
    while len(ip_network_list) < int(max_ips / 2):
        while len(ip_network_list) < int(max_ips / 2):
            ip = random.choice(ip_random_list)
            if ":" in ip:  # IPv6 address, convert to CIDR /64
                hexblock = ip.split(":")
                cidr = f"{hexblock[0]}:{hexblock[1]}:{hexblock[2]}:{hexblock[3]}::/64"
            else:  # IPv4 address, convert to CIDR /24
                octet = ip.split(".")
                cidr = f"{octet[0]}.{octet[1]}.{octet[2]}.0/24"
            ip_network_list.append(cidr)  # allow duplicates for testing
        ip_network_list = list(set(ip_network_list))  # remove duplicates
    random.shuffle(ip_random_list)
    print(f"Done in {'%.6f'%(time.monotonic()-start_time)} second(s)!")

    print(f"- Creating the UnlimitedIPList with {len(ip_network_list)} permitted networks... ", end="", flush=True)
    start_time = time.monotonic()
    total_time_list = []
    unlimited_ip_list = UnlimitedIPList(ip_networks_list=ip_network_list, raise_on_error=False, debug=False)
    print(f"Done in {'%.6f'%(time.monotonic()-start_time)} second(s)!")
    print("")
    
    # countdown of 5 seconds before starting the performance test
    print("- Starting the performance test in 5 seconds...", end="", flush=True)
    for i in range(5, 0, -1):
        print(f"\r- Starting the performance test in {i} second(s)...", end="", flush=True)
        time.sleep(1)
    print("\r- Starting the performance test now! (this may take a while, please wait...)\n", flush=True)
    print("")
    
    total_start_time = time.monotonic()
    for ip in ip_random_list:
        start_time = time.monotonic()
        result = unlimited_ip_list.check_ipaddr(ip)
        # let´s simulate the use of the result variable
        if result:  # result is a network address, meaning the IP is accepted
            end_time = time.monotonic() - start_time
            total_time_list.append(end_time)
            print(f"[{end_time:.9f}] \033[36;1mACCEPTED\033[0m IP {ip.ljust(40)} (Network: {result})")
        else: # result is False, meaning the IP is blocked
            end_time = time.monotonic() - start_time
            total_time_list.append(end_time)
            print(f"[{end_time:.9f}] \033[91;1mBLOCKED\033[0m  IP {ip}")

    print("")
    print("- Statistics:")
    total_end_time = time.monotonic()
    print(f"Total elapsed time (printing the result): {total_end_time-total_start_time:.9f}")
    print(f"Total ip_random_list items: {len(ip_random_list)} - Total ip_network_list items: {len(ip_network_list)}")
    print(f"Average checks per second: {len(total_time_list)/sum(total_time_list):.2f} - " f"Average seconds per check: {sum(total_time_list)/len(total_time_list):.9f}")
    print("")
