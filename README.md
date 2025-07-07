# Unlimited IP List v1.0.1

**UnlimitedIPList** is a high-performance, thread-safe, pure Python class to manage large lists of IPv4/IPv6 networks and perform ultra-fast lookups using bisect and integer-based IP operations. It supports both IPv4 and IPv6 CIDRs, normalizes invalid CIDRs, and efficiently handles large datasets with minimal memory overhead.

## Features

- ✅ Works simultaneously with IPv4 and IPv6 addressess or networks
- ⚡ Processes 10,000 CIDRs in ~0.05s and an IP verification takes ~0.000005s regardless of list size
- 🔍 CIDR normalization and validation
- 🧹 Removes duplicates and overlapping CIDRs
- 🔐 Thread-safe with internal locking
- 📏 Balanced chunking for performance
- 🐍 Pure Python, no external dependencies (Works on PyPy3 also!)

---

## 📦 Installation

You can install the package via pip:

```bash
pip install unlimitediplist
```

Or, if you prefer to use it directly without installation, you can clone the repository:

```bash
git clone https://github.com/rabuchaim/UnlimitedIPList.git
cd unlimitediplist
```

Just include the `unlimitediplist.py` file in your project. There are no external dependencies.

And there is a minified version available for production use with 300 lines, see `unlimitediplist_min.py`.

---

## 🚀 Usage

### Creating an instance

```python
from unlimitediplist import UnlimitedIPList

iplist = UnlimitedIPList([
    "10.0.0.0/8",
    "192.168.1.0/24",
    "2001:db8::/32"
])
```

### Check if an IP is in the list

```python
iplist.check_ipaddr("10.0.0.42")         # ➜ "10.0.0.0/8"
iplist.check_ipaddr("192.168.2.1")       # ➜ False
iplist.check_ipaddr("2001:db8::1")       # ➜ "2001:db8::/32"
```

### Add or remove networks

```python
iplist.add_ip_network("172.16.0.0/12")
iplist.remove_ip_network("192.168.1.0/24")
```

### Get all stored networks

```python
networks = iplist.get_ip_networks_list()
```

---

## ⚙️ Constructor Parameters

```python
UnlimitedIPList(
    ip_networks_list: List[str],
    normalize_invalid_cidr: bool = False,
    raise_on_error: bool = False,
    debug: bool = False
)
```

| Parameter                  | Description                                                                 |
|----------------------------|-----------------------------------------------------------------------------|
| `ip_networks_list`         | Initial list of IPv4/IPv6 networks in CIDR format                          |
| `normalize_invalid_cidr`   | If `True`, tries to normalize invalid CIDRs (e.g., `10.0.0.10/8` → `10.0.0.0/8`) |
| `raise_on_error`           | If `True`, raises exceptions on failure (UnlimitedIPListException)                                    |
| `debug`                    | If `True`, prints debug logs to console                                    |

---

## 📚 API Overview (supports IPv4 and IPv6, don´t worry)

### Validation & Conversion 

- `is_valid_ipaddr(str)` → Check if a string is a valid IP
- `is_valid_iplong(int)` → Check if integer is a valid IP
- `is_valid_cidr(str)` → Check if CIDR is valid (optionally strict)
- `get_valid_cidr(str)` → Normalize and validate CIDR
- `ip_to_int(str)` → IP to integer
- `int_to_ip(int)` → Integer to IP
- `compress_ipv6(str)` → Compress IPv6 address

### List Operations

- `add_ip_network(str)` → Add a IP/CIDR to the list
- `add_ip_networks_list(list)` → Add multiple IP/CIDRs
- `remove_ip_network(str)` → Remove a IP/CIDR
- `remove_ip_networks_list(list)` → Remove multiple IP/CIDRs
- `set_ip_networks_list(list)` → Replace the entire list
- `get_ip_networks_list()` → Get current list
- `clear_ip_networks_list()` → Clear the IP networks list (and all internal lists)

- `discarded_cidrs` → is a list containing the most recent discarded CIDRs (invalid or overlapping) after each `add_ip_network`, `add_ip_networks_list` or `set_ip_networks_list` operation. The value is a list of strings and is cleared before each operation.

### Lookup

- `check_ipaddr(str or int)` → Check if an IP address (IPv4 or IPv6) is in the list. Returns the CIDR if found, or `False` if not found. Accepts both string and integer formats for IP addresses.


---

## 🧪 Example Benchmark

```python
import time, socket, struct, random
from unlimitediplist import UnlimitedIPList
random.seed(42)  # For reproducibility

def random_ipv4_cidr(): # generates a random IPv4 CIDR in the range from 190.0.0.0 to 193.255.255.255
    ip =  socket.inet_ntoa(struct.pack(">L", random.randint(3187671040, 3254779903)))
    octet = ip.split(".")
    return f"{octet[0]}.{octet[1]}.{octet[2]}.0/24"

start = time.monotonic()
cidrs = [random_ipv4_cidr() for _ in range(10000)]
end = time.monotonic()
print(f"Created an IP CIDR list with {len(cidrs)} CIDRs in {(end - start):.9f} seconds.")

start = time.monotonic()
uiplist = UnlimitedIPList(cidrs)
end = time.monotonic()
# the difference between the number of CIDRs in the original list and the number of CIDRs in the UnlimitedIPList is due to duplicates
print(f"Created UnlimitedIPList with {len(uiplist)} CIDRs in {(end - start):.9f} seconds.")

start = time.monotonic()
result = uiplist.check_ipaddr("192.168.214.100")
print(f"Check result for 192.168.214.100: {f'Exists! Network {result}' if result else 'Does not exist!'}")
end = time.monotonic()
print(f"Check took: {(end - start):.9f} seconds")

start = time.monotonic()
result = uiplist.check_ipaddr("192.168.0.100")
print(f"Check result for 192.168.0.100: {f'Exists! Network {result}' if result else 'Does not exist!'}")
end = time.monotonic()
print(f"Check took: {(end - start):.9f} seconds")
```

Output:

```
Created an IP CIDR list with 10000 CIDRs in 0.011325242 seconds.
Created UnlimitedIPList with 9817 CIDRs in 0.050823510 seconds.
Check result for 192.168.214.100: Exists! Network 192.168.214.0/24
Check took: 0.000007471 seconds
Check result for 192.168.0.100: Does not exist!
Check took: 0.000003132 seconds
```

---

## 🧠 Example: WITHOUT Invalid CIDR normalization

In this example, the CIDR `10.10.10.10/8` is not normalized, and it will be discarded as invalid. 

The `normalize_invalid_cidr` parameter is set to `False`, and the `raise_on_error` parameter is also set to `False`, allowing the code to continue without raising exceptions for invalid CIDRs. And the debug mode is enabled to show internal processing steps.

```python
from unlimitediplist import UnlimitedIPList

ip_networks_list = ['a.b.c.d', '100.200.300.400', '1.0.0.0/24', '1.1.1.1/32', '10.10.10.10/32', '10.10.10.10/8', '2001:db8::/32'] 
print(f"IP Networks List: {ip_networks_list}")   
ip_list = UnlimitedIPList(ip_networks_list=ip_networks_list, normalize_invalid_cidr=False, raise_on_error=False, debug=True)

print(f"Last Discarded CIDR: {ip_list.discarded_cidrs}")
print(f"Current IP Networks List: {ip_list.get_ip_networks_list()}")
```
Output:
```bash
IP Networks List: ['a.b.c.d', '100.200.300.400', '1.0.0.0/24', '1.1.1.1/32', '10.10.10.10/32', '10.10.10.10/8', '2001:db8::/32']
25/07/06 00:15:47.309440 [UNLIMITED_IP_LIST_DEBUG] Processing the ip_networks_list with 7 unique items.
25/07/06 00:15:47.309528 [UNLIMITED_IP_LIST_DEBUG] Normalizing the list of IPs in CIDR format without removing invalid CIDRs.
25/07/06 00:15:47.309662 [UNLIMITED_IP_LIST_DEBUG] Removing invalid CIDRs from the list. Current size: 7
25/07/06 00:15:47.309781 [UNLIMITED_IP_LIST_DEBUG] After removing invalid CIDRs, the list size is 4.
25/07/06 00:15:47.309827 [UNLIMITED_IP_LIST_DEBUG] Processing 4 CIDRs to remove overlaps and sorting them.
25/07/06 00:15:47.310014 [UNLIMITED_IP_LIST_DEBUG] Discarded 3 invalid or overlapping CIDRs from the list (['100.200.300.400/32', 'a.b.c.d/32', '10.10.10.10/8'])
25/07/06 00:15:47.310108 [UNLIMITED_IP_LIST_DEBUG] Splitting the list into chunks of size 4 for better performance.
Last Discarded CIDR: ['100.200.300.400/32', 'a.b.c.d/32', '10.10.10.10/8']
Current IP Networks List: ['1.0.0.0/24', '1.1.1.1/32', '10.10.10.10/32', '2001:db8::/32']
```

---

## 🧠 Example: WITH Invalid CIDR normalization

In this example, the CIDR `10.10.10.10/8` is normalized to `10.0.0.0/8` and the CIDR `10.10.10.10/32` is discarded because it overlaps with `10.0.0.0/8`.

The `normalize_invalid_cidr` parameter is set to `True`, and the `raise_on_error` parameter is also set to `False`, allowing the code to continue without raising exceptions for invalid CIDRs. And the debug mode is enabled to show internal processing steps.

```python
from unlimitediplist import UnlimitedIPList

ip_networks_list = ['a.b.c.d', '100.200.300.400', '1.0.0.0/24', '1.1.1.1/32', '10.10.10.10/32', '10.10.10.10/8', '2001:db8::/32'] 
print(f"IP Networks List: {ip_networks_list}")   
ip_list = UnlimitedIPList(ip_networks_list=ip_networks_list, normalize_invalid_cidr=True, raise_on_error=False, debug=True)

print(f"Last Discarded CIDR: {ip_list.discarded_cidrs}")
print(f"Current IP Networks List: {ip_list.get_ip_networks_list()}")
```
Output:
```bash
IP Networks List: ['a.b.c.d', '100.200.300.400', '1.0.0.0/24', '1.1.1.1/32', '10.10.10.10/32', '10.10.10.10/8', '2001:db8::/32']
25/07/06 00:22:16.300848 [UNLIMITED_IP_LIST_DEBUG] Processing the ip_networks_list with 7 unique items.
25/07/06 00:22:16.300899 [UNLIMITED_IP_LIST_DEBUG] Normalizing the list of IPs in CIDR format and removing invalid CIDRs.
25/07/06 00:22:16.301079 [UNLIMITED_IP_LIST_DEBUG] After removing invalid CIDRs, the list size is 5.
25/07/06 00:22:16.301105 [UNLIMITED_IP_LIST_DEBUG] Processing 5 CIDRs to remove overlaps and sorting them.
25/07/06 00:22:16.301160 [UNLIMITED_IP_LIST_DEBUG] Discarded 4 invalid or overlapping CIDRs from the list (['100.200.300.400', '10.10.10.10/8', 'a.b.c.d', '10.10.10.10/32'])
25/07/06 00:22:16.301184 [UNLIMITED_IP_LIST_DEBUG] Splitting the list into chunks of size 4 for better performance.
Last Discarded CIDR: ['100.200.300.400', '10.10.10.10/8', 'a.b.c.d', '10.10.10.10/32']
Current IP Networks List: ['1.0.0.0/24', '1.1.1.1/32', '10.0.0.0/8', '2001:db8::/32']
```

---

## 🧠 Example: Whitelist Filtering

```python
whitelist = UnlimitedIPList(["10.10.0.0/16", "2001:db8::/32"])

if whitelist.check_ipaddr("10.10.5.22"):
    print("Allowed")
else:
    print("Blocked")
```

---

## 🔍 Internal Performance

The list is divided into **balanced chunks** to reduce search time. The `bisect` function is used to quickly identify the relevant chunk, and then CIDR comparison is done only within that chunk.

Check the tests directory for more performance benchmarks.

Below are some performance test results with 200.000 random IPv4/IPv6 addressess and 100.000 IPv4/IPv6 networks:

<img src="https://raw.githubusercontent.com/rabuchaim/UnlimitedIPList/refs/heads/main/tests/test_performance_01.png" alt="Test Performance" />

(... 200.000 random IPv4/IPv6 addressess ...)

<img src="https://raw.githubusercontent.com/rabuchaim/UnlimitedIPList/refs/heads/main/tests/test_performance_02.png" alt="Test Performance" />

---

## 🧰 Requirements

- Python 3.6+ or PyPy3
- No external packages required

---

## 💡 Tip

Use `debug=True` in the constructor to enable verbose logs for internal operations and debugging.

---

## 👨‍💻 Author

Ricardo Abuchaim - 📧 ricardoabuchaim@gmail.com

---

## ⚖️ License

This project is licensed under the MIT License. 
