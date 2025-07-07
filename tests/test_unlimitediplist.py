#!/usr/bin/env python3
import unittest, sys
from unlimitediplist import UnlimitedIPList, UnlimitedIPListException

import socket, struct, random, time
def randomipv4():
    return socket.inet_ntoa(struct.pack(">L", random.randint(184549376, 3758096383)))
def randomipv6():
    return ":".join([f"{random.randint(0, 0xffff):04x}" for _ in range(8)])

class TestUnlimitedIPList(unittest.TestCase):

    def setUp(self):
        random.seed(42)
        self.max_ips = 1000  # Set the maximum number of IPs to generate
        ip_network_list, ip_random_list = [], []
        ip_random_list.extend([randomipv4() for i in range(int(self.max_ips / 2))])
        ip_random_list.extend([randomipv6() for i in range(int(self.max_ips / 2))])
        random.shuffle(ip_random_list)
        for ip in ip_random_list[-(int(self.max_ips/2)) :]:
            if ":" in ip:  # IPv6 address, convert to CIDR /64
                hexblock = ip.split(":")
                ip_network_list.append(f"{hexblock[0]}:{hexblock[1]}:{hexblock[2]}:{hexblock[3]}::/64")
            else:  # IPv4 address, convert to CIDR /24
                octet = ip.split(".")
                ip_network_list.append(f"{octet[0]}.{octet[1]}.{octet[2]}.0/24")
        random.shuffle(ip_random_list)
        self.ip_random_list = ip_random_list
        self.ip_network_list = ip_network_list
        self.unlimited_ip_list = UnlimitedIPList(ip_networks_list=ip_network_list,normalize_invalid_cidr=True,raise_on_error=False,debug=False)
        self.ip_network_list_length = len(self.unlimited_ip_list.get_ip_networks_list())
        
    def test_01_ip_network_list_empty(self):
        self.unlimited_ip_list.clear_ip_networks_list()
        current_list = self.unlimited_ip_list.get_ip_networks_list()
        self.assertEqual(len(current_list), 0)        

    def test_02_set_ip_networks_list(self):
        self.unlimited_ip_list.clear_ip_networks_list()
        self.assertEqual(len(self.unlimited_ip_list.get_ip_networks_list()), 0)
        self.unlimited_ip_list.set_ip_networks_list(self.ip_network_list)
        current_list = self.unlimited_ip_list.get_ip_networks_list()
        self.assertEqual(len(current_list), self.ip_network_list_length)

    def test_03_add_ipv4_network(self):
        new_ip = "1.1.1.0/24"
        result = self.unlimited_ip_list.add_ip_network(new_ip)
        self.assertTrue(result)
        current_list = self.unlimited_ip_list.get_ip_networks_list()
        self.assertIn(new_ip, current_list)
        
    def test_04_add_ipv6_network(self):
        new_ip = self.unlimited_ip_list.get_valid_cidr("2001:db8::/64")
        result = self.unlimited_ip_list.add_ip_network(new_ip)
        self.assertTrue(result)
        current_list = self.unlimited_ip_list.get_ip_networks_list()
        self.assertIn(new_ip, current_list)

    def test_05_add_duplicate_ipv4_network(self):
        new_ip = self.unlimited_ip_list.get_ip_networks_list()[-1]
        result = self.unlimited_ip_list.add_ip_network(new_ip)
        self.assertFalse(result)
        
    def test_06_add_duplicate_ipv6_network(self):
        new_ip = self.unlimited_ip_list.get_ip_networks_list()[-1]
        result = self.unlimited_ip_list.add_ip_network(new_ip)
        self.assertFalse(result)

    def test_07_ipv4_overlap(self):
        new_ip = "1.1.1.0/24"
        result = self.unlimited_ip_list.add_ip_network(new_ip)
        self.assertTrue(result)
        current_list = self.unlimited_ip_list.get_ip_networks_list()
        self.assertIn(new_ip, current_list)
        # Test overlapping IP
        overlapping_ip = "1.1.1.128/25"
        result = self.unlimited_ip_list.add_ip_network(overlapping_ip)
        self.assertFalse(result)
        
    def test_08_ipv6_overlap(self):
        new_ip = self.unlimited_ip_list.get_valid_cidr("2001:db8::/64")
        result = self.unlimited_ip_list.add_ip_network(new_ip)
        self.assertTrue(result)
        current_list = self.unlimited_ip_list.get_ip_networks_list()
        self.assertIn(new_ip, current_list)
        # Test overlapping IP
        overlapping_ip = "2001:db8::1/128"
        result = self.unlimited_ip_list.add_ip_network(overlapping_ip)
        self.assertFalse(result)

    def test_09_check_ipv4_addr(self):
        new_ip = "10.0.0.0/8"
        result = self.unlimited_ip_list.add_ip_network(new_ip)
        self.assertTrue(result)
        result = self.unlimited_ip_list.check_ipaddr("10.10.10.10")
        self.assertEqual(result,new_ip)
    
    def test_10_check_ipv6_addr(self):
        new_ip = "2001:db8::/32"
        result = self.unlimited_ip_list.add_ip_network(new_ip)
        self.assertTrue(result)
        result = self.unlimited_ip_list.check_ipaddr("2001:0db8::1")
        self.assertEqual(result,self.unlimited_ip_list.get_valid_cidr(new_ip))

    def test_11_check_nonexistent_ipv4_addr(self):
        result = self.unlimited_ip_list.check_ipaddr("10.10.10.11")
        self.assertFalse(result)

    def test_12_check_nonexistent_ipv6_addr(self):
        result = self.unlimited_ip_list.check_ipaddr("1001:0db8::2")
        self.assertFalse(result)

    def test_13_remove_ipv4_network(self):
        new_ip = "10.0.0.0/8"
        result = self.unlimited_ip_list.add_ip_network(new_ip)
        self.assertTrue(result)
        result = self.unlimited_ip_list.remove_ip_network(new_ip)
        self.assertTrue(result)
        current_list = self.unlimited_ip_list.get_ip_networks_list()
        self.assertNotIn(new_ip, current_list)

    def test_14_remove_ipv6_network(self):
        new_ip = self.unlimited_ip_list.get_valid_cidr("2001:db8::/32")
        result = self.unlimited_ip_list.add_ip_network(new_ip)
        self.assertTrue(result)
        result = self.unlimited_ip_list.remove_ip_network(new_ip)
        self.assertTrue(result)
        current_list = self.unlimited_ip_list.get_ip_networks_list()
        self.assertNotIn(new_ip, current_list)
        
    def test_15_remove_nonexistent_ipv4_network(self):
        new_ip = "10.10.10.11/32"
        result = self.unlimited_ip_list.remove_ip_network(new_ip)
        self.assertFalse(result)

    def test_16_remove_nonexistent_ipv6_network(self):
        new_ip = "2001:db8::2/128"
        result = self.unlimited_ip_list.remove_ip_network(new_ip)
        self.assertFalse(result)

    def test_17_add_invalid_ipv4_network(self):
        new_ip = "999.999.999.999/32"
        self.unlimited_ip_list.add_ip_network(new_ip)
        current_list = self.unlimited_ip_list.get_ip_networks_list()
        self.assertNotIn(new_ip, current_list)

    def test_18_add_invalid_ipv6_network(self):
        new_ip = "2001:db8::g/64"
        self.unlimited_ip_list.add_ip_network(new_ip)
        current_list = self.unlimited_ip_list.get_ip_networks_list()
        self.assertNotIn(new_ip, current_list)
        
    def test_19_is_valid_ipv4addr(self):
        valid_ipv4 = "192.168.1.1"
        self.assertTrue(self.unlimited_ip_list.is_valid_ipaddr(valid_ipv4))
        self.assertTrue(self.unlimited_ip_list.is_valid_iplong(self.unlimited_ip_list.ip_to_int(valid_ipv4)))

    def test_20_is_valid_ipv6addr(self):
        valid_ipv6 = "2001:0db8:85a3:0000:0000:8a2e:0370:7334"
        self.assertTrue(self.unlimited_ip_list.is_valid_ipaddr(valid_ipv6))
        self.assertTrue(self.unlimited_ip_list.is_valid_iplong(self.unlimited_ip_list.ip_to_int(valid_ipv6)))

    def test_21_is_valid_cidr_ipv4(self):
        valid_ipv4 = "192.168.1.1"
        self.assertFalse(self.unlimited_ip_list.is_valid_cidr(valid_ipv4 + "/24",strict=True))
        self.assertTrue(self.unlimited_ip_list.is_valid_cidr(valid_ipv4 + "/24",strict=False))

    def test_22_is_valid_cidr_ipv6(self):
        valid_ipv6 = "2001:0db8:85a3:0000:0000:8a2e:0370:7334"
        self.assertFalse(self.unlimited_ip_list.is_valid_cidr(valid_ipv6 + "/64",strict=True))
        self.assertTrue(self.unlimited_ip_list.is_valid_cidr(valid_ipv6 + "/64",strict=False))

    def test_23_get_valid_cidr_ipv4(self):
        valid_ipv4 = "10.10.10.10/8"
        self.assertEqual(self.unlimited_ip_list.get_valid_cidr(valid_ipv4, normalize=True),'10.0.0.0/8')
        self.assertIsNone(self.unlimited_ip_list.get_valid_cidr(valid_ipv4, normalize=False))

    def test_24_get_valid_cidr_ipv6(self):
        valid_ipv6 = "2001:db8::1/64"
        self.assertEqual(self.unlimited_ip_list.get_valid_cidr(valid_ipv6, normalize=True),'2001:0db8::/64')
        self.assertIsNone(self.unlimited_ip_list.get_valid_cidr(valid_ipv6, normalize=False))

    def test_25_check_all_ipaddr(self):
        ipv4_count, ipv4_false_count = 0, 0
        ipv6_count, ipv6_false_count = 0, 0
        time_list = []
        for ip in self.ip_random_list:
            start_time = time.monotonic()
            result = self.unlimited_ip_list.check_ipaddr(ip)
            if ":" in ip:
                if result is False:
                    ipv6_false_count += 1
                else:
                    self.assertTrue(result.endswith('/64'))
                    ipv6_count += 1
            else:   
                if result is False:
                    ipv4_false_count += 1
                else:
                    self.assertTrue(result.endswith('/24'))
                    ipv4_count += 1
            elapsed_time = time.monotonic() - start_time
            time_list.append(elapsed_time)
        self.assertGreater(ipv4_count, 0)
        self.assertGreater(ipv6_count, 0)
        self.assertEqual(ipv4_false_count+ipv4_count, len([ip for ip in self.ip_random_list if ":" not in ip]))
        self.assertEqual(ipv6_false_count+ipv6_count, len([ip for ip in self.ip_random_list if ":" in ip]))

        if BENCH:
            self.print_stats(len(self.ip_random_list), time_list, ipv4_count, ipv4_false_count, ipv6_count, ipv6_false_count)

    def print_stats(self, total, time_list, ipv4_count, ipv4_false_count, ipv6_count, ipv6_false_count):
        print()
        print(f"Elapsed time for checking {total} IP addresses: {sum(time_list):.9f} seconds")
        print(f"Average time per IP address: {sum(time_list)/total:.9f} seconds")
        print(f"IPv4 addresses checked: {ipv4_count}, False: {ipv4_false_count}")
        print(f"IPv6 addresses checked: {ipv6_count}, False: {ipv6_false_count}")

if __name__ == "__main__":
    BENCH = "--bench" in sys.argv
    if BENCH:
        sys.argv.remove("--bench")
    else:
        print("\nRun with --bench to enable performance testing.\n")
    unittest.main(verbosity=2)
