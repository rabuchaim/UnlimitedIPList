#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unlimited IP List v1.0.1"""
"""
 _   _       _ _           _ _           _   ___ ____    _     _     _
| | | |_ __ | (_)_ __ ___ (_) |_ ___  __| | |_ _|  _ \  | |   (_)___| |_
| | | | '_ \| | | '_ ` _ \| | __/ _ \/ _` |  | || |_) | | |   | / __| __|
| |_| | | | | | | | | | | | | ||  __/ (_| |  | ||  __/  | |___| \__ \ |_
 \___/|_| |_|_|_|_| |_| |_|_|\__\___|\__,_| |___|_|     |_____|_|___/\__|
 
 A list-type object to manage the list of IPv4/IPv6 networks and perform 
 quick searches using bisect and working with IPs as integers.
 A list with 10000 IP/CIDR (IPv4 and IPv6) took 0.05 to be processed. 
 The verification is around 0.000005 regardless of the list size.

 by Ricardo Abuchaim - ricardoabuchaim@gmail.com
"""
import socket
import struct
import bisect
import threading
import math
import typing
import datetime

__all__ = ["UnlimitedIPList", "UnlimitedIPListException"]

class UnlimitedIPListException(Exception): ...
"""Custom exception for UnlimitedIPList errors."""

class UnlimitedIPList:
    """A list-type object to manage the list of IPv4/IPv6 networks and perform quick searches using bisect and working with IPs as integers.
    A list with 10000 IP/CIDR (IPv4 and IPv6) took 0.05 to be processed. The verification is around 0.000005 regardless of the list size.
    """
    def __init__(self, ip_networks_list: typing.List[str], normalize_invalid_cidr: bool = False, raise_on_error: bool = False, debug: bool = False):
        self._log_debug = self._log_debug if debug else lambda msg: None
        self._lock = threading.RLock()
        
        self.__raise_on_error = raise_on_error
        self.__normalize_invalid_cidr = normalize_invalid_cidr
        
        self.discarded_cidrs = []
        self.__list_chunks, self.__list_index = [], []
        self.__first_ip_chunks, self.__last_ip_chunks = [], []

        self._cidrs: typing.List[str] = []
        self.__process_list(ip_networks_list)

    def __getitem__(self, index: int) -> str:
        return self._cidrs[index]

    def __iter__(self) -> typing.Iterator[str]:
        return iter(self._cidrs)

    def __len__(self) -> int:
        return len(self._cidrs)

    def __contains__(self, item: str) -> bool:
        return item.strip() in self._cidrs

    def __repr__(self):
        return repr(self._cidrs)

    def _log_debug(self, msg: str):
        """Log debug messages if debug mode is enabled"""
        print(f"\x1b[38;2;0;255;0m{datetime.datetime.now().strftime('%y/%m/%d %H:%M:%S.%f')} [UNLIMITED_IP_LIST_DEBUG] {str(msg)}\x1b[0m")

    def is_valid_ipaddr(self, ipaddr: str) -> bool:
        """Check if an IP address is valid. Accepts IPv4 or IPv6. (Elapsed average time: 0.000001)"""
        return self.ip_to_int(ipaddr.strip()) is not None

    def is_valid_iplong(self, iplong: int) -> bool:
        """Check if an integer is a valid IPv4/IPv6 address. (Elapsed average time: 0.000001)"""
        return self.int_to_ip(iplong) is not None

    def is_valid_cidr(self, cidr: str, strict: bool = True) -> bool:
        """Check if an IPv4/IPv6 CIDR is valid in pure Python.
          
           Accepts ONLY CIDR with the network address, not the host address.
        
        with strict=True, it checks if the bits outside the mask are zero.
            Ex: 10.0.0.10/8 is INVALID, 10.0.0.0/8 is VALID, 10.0.0.10/32 is VALID
            c1a5:9ba4:8d92:636e:60fd:8756:430b:0000/64 is INVALID, c1a5:9ba4:8d92:636e::/64 is VALID
        
        with strict=False, it only checks if the CIDR is well-formed.
            Ex: 10.0.0.10/8 is VALID, 10.0.0.0/8 is VALID, 10.0.0.10/32 is VALID
            c1a5:9ba4:8d92:636e:60fd:8756:430b:0000/64 is VALID, c1a5:9ba4:8d92:636e::/64 is VALID
        """
        try:
            cidr = cidr.strip()
            if '/' not in cidr:
                if strict:
                    return False  # sem prefixo é inválido como CIDR
                else:
                    cidr = self._normalize_cidr_suffix(cidr)  # adiciona /32 para IPv4 ou /128 para IPv6 se não tiver prefixo
            ip_part, prefix_str = cidr.split('/')
            prefix = int(prefix_str)
            if '.' in ip_part:
                packed_ip = socket.inet_aton(ip_part)
                ip_int = struct.unpack("!L", packed_ip)[0]
                if not (0 <= prefix <= 32):
                    return False
                if strict:
                    mask = ((1 << prefix) - 1) << (32 - prefix)
                    return ip_int & ~mask == 0  # os bits fora da máscara devem ser zero
                return True
            else:
                packed_ip = socket.inet_pton(socket.AF_INET6, ip_part)
                ip_int = int.from_bytes(packed_ip, byteorder='big')
                if not (0 <= prefix <= 128):
                    return False
                if strict:
                    mask = ((1 << prefix) - 1) << (128 - prefix)
                    return ip_int & ~mask == 0
                return True
        except Exception:
            return False

    def get_valid_cidr(self, cidr: str, normalize: bool = True) -> str:
        """Returns a valid normalized CIDR (IPv4 or IPv6) in pure Python.
        
        If normalize is False, it returns the CIDR as it is, without checking if the bits outside the mask are zero.
        
        If normalize is True, it returns the CIDR with the network address, ensuring that the bits outside the mask are zero.
        """
        try:
            cidr = cidr.strip()
            if '/' not in cidr:
                if not normalize:
                    return None
                cidr = self._normalize_cidr_suffix(cidr)
            ip_str, prefix_str = cidr.split('/')
            prefix = int(prefix_str)
            if '.' in ip_str:
                if not (0 <= prefix <= 32):
                    return None
                packed = socket.inet_aton(ip_str)
                ip_int = struct.unpack("!L", packed)[0]
                if normalize:
                    mask = ((1 << prefix) - 1) << (32 - prefix)
                    network_int = ip_int & mask
                    network_ip = socket.inet_ntoa(struct.pack("!L", network_int))
                    return f"{network_ip}/{prefix}"
                else:
                    mask = ((1 << prefix) - 1) << (32 - prefix)
                    if ip_int & ~mask != 0:
                        return None
                    return f"{ip_str}/{prefix}"
            else:
                packed = socket.inet_pton(socket.AF_INET6, ip_str)
                if not (0 <= prefix <= 128):
                    return None
                ip_int = int.from_bytes(packed, byteorder='big')
                if normalize:
                    mask = ((1 << prefix) - 1) << (128 - prefix)
                    network_int = ip_int & mask
                    # network_bytes = network_int.to_bytes(16, byteorder='big')
                    # network_ip = socket.inet_ntop(socket.AF_INET6, network_bytes)
                    network_ip = self.compress_ipv6(self.int_to_ip(network_int))
                    return f"{network_ip}/{prefix}"
                else:
                    mask = ((1 << prefix) - 1) << (128 - prefix)
                    if ip_int & ~mask != 0:
                        return None
                    return f"{ip_str}/{prefix}"
        except Exception as ERR:
            self._log_debug(f"Failed at UnlimitedIPList.get_valid_cidr({cidr}): {str(ERR)}")
            return None
        
    def ip_to_int(self, ipaddr: str) -> int:
        """Converts an IPv4/IPv6 address to an integer. (Elapsed average time: 0.000001)"""
        try:
            return struct.unpack("!L", socket.inet_aton(ipaddr.strip()))[0]
        except Exception:
            try:
                return int.from_bytes(socket.inet_pton(socket.AF_INET6, ipaddr.strip()), byteorder="big")
            except Exception:
                return None

    def int_to_ip(self, iplong: int) -> str:
        """Convert an integer to IP Address (IPv4 or IPv6). For IPv6, returns the full expanded zero-padded form."""
        try:
            if iplong <= 2**32:  # MAX IPv4
                return socket.inet_ntoa(struct.pack(">L", iplong))
            else:
                ip_bytes = iplong.to_bytes(16, byteorder="big")
                hextets = [f"{(ip_bytes[i] << 8 | ip_bytes[i+1]):04x}" for i in range(0, 16, 2)]
                return ":".join(hextets)
        except Exception:
            return None

    def compress_ipv6(self, hextets: typing.Union[str, list]) -> str:
        """Compresses an IPv6 address represented as a list of hextets."""
        if isinstance(hextets, str):
            if "/" in hextets:
                hextets = hextets.split("/")[0]
            hextets = hextets.split(":")
        hextets = [h if h else "0000" for h in hextets]  # replace empty hextets with "0000"
        if len(hextets) != 8: # fill missing hextets with "0000"
            hextets = hextets + ["0000"] * (8 - len(hextets))
        best_start = best_len = -1
        curr_start = curr_len = -1
        for i in range(8):
            if hextets[i] == "0000":
                if curr_start == -1:
                    curr_start = i
                    curr_len = 1
                else:
                    curr_len += 1
            else:
                if curr_len > best_len:
                    best_start, best_len = curr_start, curr_len
                curr_start = curr_len = -1
        if curr_len > best_len:
            best_start, best_len = curr_start, curr_len
        if best_len > 1:
            hextets = hextets[:best_start] + [""] + hextets[best_start + best_len:]
            if best_start == 0:
                hextets = [""] + hextets
            if best_start + best_len == 8:
                hextets += [""]
        return ":".join(hextets).replace(":::", "::")

    def _normalize_cidr_suffix(self, ipaddr: str):
        """Converts an IP address to CIDR format. Add /32 to the IPv4 address if it is not present 
        or add /128 to the IPv6 address if it is not present. (Elapsed average time 0.0000006)"""
        ip = ipaddr.strip()
        if '/' in ip:
            return ip
        return f"{ip}/32" if ':' not in ip else f"{ip}/128"

    def __split_list(self, a_list, size):
        """Split a_list in chunks defined by size"""
        try:
            return [a_list[i:i + size] for i in range(0, len(a_list), size)]
        except Exception as ERR:
            if self.__raise_on_error:
                raise UnlimitedIPListException(f"Failed at UnlimitedIPList.__split_list(): {str(ERR)}")
            return []
        
    def __get_first_last_ip_cidr(self, cidr: str) -> tuple:
        """Get the first and last IP of a CIDR in integer format."""
        try:
            ip_part, prefix_part = cidr.split("/")
            prefix = int(prefix_part)
            ip_int = self.ip_to_int(ip_part)
            if ":" in ip_part:  # IPv6
                bits = 128
            else:  # IPv4
                bits = 32
            mask = ((1 << prefix) - 1) << (bits - prefix)
            mask &= (1 << bits) - 1  # garante que só usamos os bits válidos
            network_ip = ip_int & mask
            broadcast_ip = network_ip | ((1 << (bits - prefix)) - 1)
            return network_ip, broadcast_ip
        except Exception:
            return 0,0
        
    def __find_balanced_chunk_size(self, list_size, min_chunk_size: int = 100, max_chunk_size: int = 5000):
        """Finds a balanced chunk size for splitting a list of size n into chunks,
        such that the difference between the number of chunks and the chunk size is minimized."""
        if list_size <= min_chunk_size:
            return list_size  # if the list is smaller than the minimum chunk size, return the list size
        best_chunk_size = 1
        best_diff = float("inf")
        for chunk_size in range(1, max_chunk_size + 1):
            q = math.ceil(list_size / chunk_size)
            diff = abs(chunk_size - q)
            if diff <= 1:  # the best value!
                return chunk_size
            elif diff < best_diff:
                best_diff = diff
                best_chunk_size = chunk_size
        return best_chunk_size

    def __clear_lists(self, clear_discarded_cidr: bool = False):
        """Clear the internal lists used for processing"""
        with self._lock:
            self._cidrs.clear()
            self.__list_chunks.clear()
            self.__first_ip_chunks.clear()
            self.__last_ip_chunks.clear()
            self.__list_index.clear()
            if clear_discarded_cidr:
                self.discarded_cidrs.clear()

    def __ip_ranges_overlap(self, first1: int, last1: int, first2: int, last2: int) -> bool:
        """Check if two IP ranges overlap."""
        return not (last1 < first2 or first1 > last2)

    def _find_cidr_overlap(self, cidr: str) -> tuple:
        """Detects if a CIDR overlaps with any existing CIDR in the already processed list."""
        try:
            if not self._cidrs:
                return False
            first_ip, last_ip = self.__get_first_last_ip_cidr(self._normalize_cidr_suffix(cidr))
            match_root_index = bisect.bisect_right(self.__list_index, first_ip) - 1
            if match_root_index < 0:
                match_root_index = 0
            # Verify current chunk
            for i in range(len(self.__first_ip_chunks[match_root_index])):
                if self.__ip_ranges_overlap(first_ip, last_ip, self.__first_ip_chunks[match_root_index][i], self.__last_ip_chunks[match_root_index][i]):
                    return self.__list_chunks[match_root_index][i]
            # Verify the prior and the next chunk (if exists)
            for offset in [-1, 1]:
                idx = match_root_index + offset
                if 0 <= idx < len(self.__first_ip_chunks):
                    for i in range(len(self.__first_ip_chunks[idx])):
                        if self.__ip_ranges_overlap(first_ip, last_ip, self.__first_ip_chunks[idx][i], self.__last_ip_chunks[idx][i]):
                            return self.__list_chunks[idx][i]
        except Exception as ERR:
            if self.__raise_on_error:
                raise UnlimitedIPListException(f"Failed at UnlimitedIPList._find_cidr_overlap(): {str(ERR)}")
        return False
    
    def _remove_overlapping_cidrs(self, new_list: typing.List[str]) -> None:
        """Remove overlapping CIDRs from the new_list and sort them."""
        self._log_debug(f"Processing {len(new_list)} CIDRs to remove overlaps and sorting them.")
        cidrs = [(cidr, *self.__get_first_last_ip_cidr(cidr)) for cidr in new_list]
        cidrs.sort(key=lambda x: x[1])  # Ordena por first_ip
        filtered = []
        prev_cidr, prev_first, prev_last = cidrs[0]
        filtered.append(prev_cidr)
        for cidr, first, last in cidrs[1:]:
            if first <= prev_last:  # overlap
                self.discarded_cidrs.append(cidr)
            else:
                filtered.append(cidr)
                # prev_first, prev_last = first, last
                prev_last = last
        new_list = filtered.copy()
        filtered.clear()
        return new_list
    
    def __normalize_and_remove_invalid_cidr(self, ip_networks_list: typing.List[str]) -> typing.List[str]:
        """Normalize the list of IPs in CIDR format and remove invalid CIDRs."""
        normalized_list = []
        for cidr in ip_networks_list:
            valid_cidr = self.get_valid_cidr(cidr, normalize=True)
            if valid_cidr:
                if valid_cidr != cidr:
                    self._log_debug(f"Normalized CIDR: {cidr} => {valid_cidr}")
                normalized_list.append(valid_cidr)
            else:
                self._log_debug(f"Invalid CIDR: {cidr}")
                self.discarded_cidrs.append(cidr)
        return normalized_list

    def __normalize_cidr(self, ip_networks_list: typing.List[str]) -> typing.List[str]:
        """Normalize the list of IPs in CIDR format and remove invalid CIDRs. 
        Just add /32 to IPv4 addresses and /128 to IPv6 addresses if they are not present."""
        normalized_list = []
        for cidr in ip_networks_list:
            normalized_list.append(self._normalize_cidr_suffix(cidr))
        return normalized_list

    def __discard_invalid_cidr(self, ip_networks_list: typing.List[str]) -> typing.List[str]:
        """Remove invalid CIDRs from the list."""
        valid_list = []
        for cidr in ip_networks_list:
            if self.is_valid_cidr(cidr):
                valid_list.append(cidr)
            else:
                self._log_debug(f"Invalid CIDR: {cidr}")
                self.discarded_cidrs.append(cidr)
        return valid_list

    def __process_list(self, ip_networks_list: typing.List[str], **kwargs) -> typing.List[str]:
        """Process the ip_networks_list"""
        try:
            if kwargs.get("discarded_cidrs", []) == []:
                self.discarded_cidrs.clear()  # Clear the last discarded CIDR list
            
            new_list = list(set(ip_networks_list))  # remove duplicates
            new_list = [item.strip() for item in new_list if item.strip()]  # remove blank items
            self._log_debug(f"Processing the ip_networks_list with {len(new_list)} unique items.")
            
            if len(new_list) == 0:
                self._log_debug("The list is empty after removing duplicates and blank items, clearing the lists.")
                self.__clear_lists()
                return False  # No valid CIDRs to process
            else:
                # normalize the list of IPs in cidr format and test if the IP is valid
                if self.__normalize_invalid_cidr:
                    # Normalize the CIDRs and remove duplicates
                    # Example: 10.10.10.10/8 => 10.0.0.0/8
                    self._log_debug(f"Normalizing the list of IPs in CIDR format and removing invalid CIDRs. Current size: {len(new_list)}")
                    new_list = self.__normalize_and_remove_invalid_cidr(new_list)
                    self._log_debug(f"After normalization, the list size is {len(new_list)}.")
                else:
                    # Just normalize the CIDRs adding /32 to IPv4 addresses and /128 to IPv6 addresses if they are not present
                    # Do not remove invalid CIDRs
                    # Example: 10.10.10.10 => 10.10.10.10/32
                    self._log_debug("Normalizing the list of IPs in CIDR format without removing invalid CIDRs.")
                    new_list = self.__normalize_cidr(new_list)
                
                self._log_debug(f"Removing invalid CIDRs from the list. Current size: {len(new_list)}")
                new_list = self.__discard_invalid_cidr(new_list)
                self._log_debug(f"After removing invalid CIDRs, the list size is {len(new_list)}.")
                
                if len(new_list) == 0:
                    self._log_debug("All CIDRs were discarded, clearing the lists.")
                    self.__clear_lists()
                    return False  # No valid CIDRs to process
                else:
                    new_list = sorted(list(filter(None, sorted(list(dict.fromkeys(new_list))))), key=lambda ip: self.ip_to_int(ip.split("/")[0]))
                    
                    if kwargs.get("check_overlap", True):
                        new_list = self._remove_overlapping_cidrs(new_list)
                    self._log_debug(f"Discarded {len(self.discarded_cidrs)} invalid or overlapping CIDRs from the list ({self.discarded_cidrs})")
                  
                    chunk_size = len(new_list) if len(new_list) <= 100 else self.__find_balanced_chunk_size(len(new_list))
                    self._log_debug(f"Splitting the list into chunks of size {chunk_size} for better performance.")
                  
                    ip_temp_list = [self.__get_first_last_ip_cidr(item) for item in new_list]
                    with self._lock:
                        self.__list_chunks = self.__split_list(new_list, chunk_size)
                        self.__first_ip_chunks = self.__split_list([item[0] for item in ip_temp_list], chunk_size)
                        self.__last_ip_chunks = self.__split_list([item[1] for item in ip_temp_list], chunk_size)
                        self.__list_index = [item[0] for item in self.__first_ip_chunks]
                        self._cidrs = new_list.copy()
                    ip_temp_list.clear()
                    new_list.clear()
                    return True  # Successfully processed the list
        except Exception as ERR:
            self.clear_ip_networks_list() # Clear the list on error
            if self.__raise_on_error:
                raise UnlimitedIPListException(f"Failed at UnlimitedIPList.__process_list(): {str(ERR)}")
            return False

    def set_ip_networks_list(self, list_items: typing.List[str]):
        """Set a new networks list"""
        self.clear_ip_networks_list()
        self.__process_list(list_items)

    def get_ip_networks_list(self) -> typing.List[str]:
        """Get the current unlimited ip networks list"""
        return list(self._cidrs)  # returns a copy of the list

    def clear_ip_networks_list(self):
        """Clear the unlimited ip networks list"""
        self.__clear_lists(clear_discarded_cidr=True)
        self._log_debug("Cleared the unlimited ip networks list.")

    def test_is_valid_ip_network(self, ipaddr: str) -> str:
        """ Check if the provided IP address or CIDR is valid to be added into the unlimited ip list.
            Returns the CIDR (normalized with /32 or /128) if valid, otherwise returns False.
        """
        if not isinstance(ipaddr, str):
            raise TypeError("ipaddr must be a string (IPv4/IPv6 address or CIDR)")
        try:
            cidr = self._normalize_cidr_suffix(ipaddr.strip())
           
            if not self.is_valid_cidr(cidr):
                self._log_debug(f"Invalid CIDR: {cidr}")
                if self.__raise_on_error:
                    raise UnlimitedIPListException(f"Invalid CIDR {cidr}.")
                return False  # Invalid CIDR
           
            if cidr in self._cidrs:
                self._log_debug(f"CIDR {cidr} already exists in the list.")
                if self.__raise_on_error:
                    raise UnlimitedIPListException(f"CIDR {cidr} already exists in the list.")
                return False  # CIDR already exists in the list
           
            overlap_result = self._find_cidr_overlap(cidr)
            if overlap_result:
                self._log_debug(f"CIDR {cidr} overlaps with existing CIDRs ({overlap_result}) in the list.")
                if self.__raise_on_error:
                    raise UnlimitedIPListException(f"CIDR {cidr} overlaps with existing CIDRs ({overlap_result}) in the list.")
                return False  # CIDR overlaps with existing CIDRs
           
            return cidr
        except Exception as ERR:
            if self.__raise_on_error:
                raise UnlimitedIPListException(f"Failed at UnlimitedIPList.add_ip(): {str(ERR)}")
        return False
        
    def add_ip_network(self, ipaddr: str) -> bool:
        """Add an IPv4/IPv6 address or CIDR to unlimited ip list"""
        if not isinstance(ipaddr, str):
            raise TypeError("ipaddr must be a string (IPv4/IPv6 address or CIDR)")
        try:
            self.discarded_cidrs.clear()  # Clear the last discarded CIDR
            cidr = ipaddr.strip()
           
            if self.__normalize_invalid_cidr:
                cidr = self.get_valid_cidr(cidr, normalize=True)
                if not cidr:
                    self.discarded_cidrs.append(ipaddr.strip())
                    return False
           
            cidr = self.test_is_valid_ip_network(cidr)
            if not cidr:
                self.discarded_cidrs.append(ipaddr.strip())
                return False
           
            self._cidrs.append(cidr)
            self.__process_list(self._cidrs, check_overlap=False, discarded_cidrs=self.discarded_cidrs)  # Process the list without check overlaps because is not needed
           
            return True
        except Exception as ERR:
            if self.__raise_on_error:
                raise UnlimitedIPListException(f"Failed at UnlimitedIPList.add_ip(): {str(ERR)}")
        return False

    def add_ip_networks_list(self, ipaddr_list: typing.List[str]) -> bool:
        """Add a list of IPv4/IPv6 addresses or CIDRs to unlimited ip list"""
        if not isinstance(ipaddr_list, list):
            raise TypeError("ipaddr_list must be a list of strings (IPv4/IPv6 addresses or valid CIDRs)")
        try:
            self.discarded_cidrs.clear()  # Clear the last discarded CIDR
          
            for ip in ipaddr_list:
                cidr = ip.strip()
          
                if self.__normalize_invalid_cidr:
                    cidr = self.get_valid_cidr(cidr, normalize=True)
                if not cidr:
                    self.discarded_cidrs.append(ip.strip())
                    continue
          
                cidr = self.test_is_valid_ip_network(cidr)
                if not cidr:
                    self.discarded_cidrs.append(ip.strip())
                else:
                    self._cidrs.append(cidr)
            self.__process_list(self._cidrs, check_overlap=True, discarded_cidrs=self.discarded_cidrs) # reprocess the list to check overlaps for the last time
            return True
        except Exception as ERR:
            if self.__raise_on_error:
                raise UnlimitedIPListException(f"Failed at UnlimitedIPList.add_ip_list(): {str(ERR)}")
        return False

    def remove_ip_network(self, ipaddr: str):
        """Remove an IPv4/IPv6 or a CIDR from unlimited ip list"""
        if not isinstance(ipaddr, str):
            raise TypeError("ipaddr must be a string (a valid IPv4/IPv6 address or valid CIDR)")
        if not self._cidrs:
            return False
        try:
            ip = self._normalize_cidr_suffix(ipaddr.strip())
            if ip and ip in self._cidrs:
                self._cidrs.remove(ip)
                self.__process_list(self._cidrs, check_overlap=False)  # Process the list without check overlaps because is not needed
                return True
            else:
                self._log_debug(f"IP address or CIDR {ip} not found in the list.")
                return False
        except Exception as ERR:
            if self.__raise_on_error:
                raise UnlimitedIPListException(f"Failed at UnlimitedIPList.remove_ip_network(): {str(ERR)}") from None
        return False

    def remove_ip_networks_list(self, ipaddr_list: typing.List[str]):
        """Remove a list of IPv4/IPv6 addresses or CIDRs from unlimited ip list"""
        if not isinstance(ipaddr_list, list):
            raise TypeError("ipaddr_list must be a list of strings (IPv4/IPv6 addresses or valid CIDRs)")
        if not self._cidrs:
            return False
        try:
            for ip in ipaddr_list:
                ip = self._normalize_cidr_suffix(ip.strip())
                if ip and ip in self._cidrs:
                    self._cidrs.remove(ip)
                else:
                    self._log_debug(f"IP address or CIDR {ip} not found in the list.")
            self.__process_list(self._cidrs, check_overlap=False)  # Process the list to remove overlaps and sort it
            return True
        except Exception as ERR:
            if self.__raise_on_error:
                raise UnlimitedIPListException(f"Failed at UnlimitedIPList.remove_ip_network_list(): {str(ERR)}") from None
        return False

    def __call__(self, ipaddr: typing.Union[str, int]) -> typing.Union[str, bool]:
        """Check if an IP address is in the unlimited ip list. Returns the network CIDR if the IP is in the list,
        otherwise it returns False. (Elapsed average time: 0.000002)

        Ex:

         result = self.unlimited_ip_list("192.168.1.1")
            `result` can be a network CIDR or False
        """
        try:
            if not self._cidrs:
                return False
            
            if isinstance(ipaddr, int):
                iplong = ipaddr
            elif isinstance(ipaddr, str):
                iplong = self.ip_to_int(ipaddr.strip())
            if iplong is None or iplong <= 0:
                self._log_debug(f"Invalid IP address: {ipaddr.strip()}")
                if self.__raise_on_error:
                    raise UnlimitedIPListException(f"Invalid IP address: {ipaddr.strip()}")
                return False

            match_root_index = bisect.bisect_right(self.__list_index, iplong) - 1
            match_list_index = bisect.bisect_right(self.__first_ip_chunks[match_root_index], iplong) - 1
            try:
                network = self.__list_chunks[match_root_index][match_list_index]
            except Exception:
                network = False
            inside_network = (iplong >= self.__first_ip_chunks[match_root_index][match_list_index]) and (iplong <= self.__last_ip_chunks[match_root_index][match_list_index])
            return network if inside_network else False
        except Exception as ERR:
            if self.__raise_on_error:
                raise UnlimitedIPListException(f"Failed at NoLimitList.check_ipaddr({ipaddr.strip()}): {str(ERR)}")
            return False
    
    def check_ipaddr(self, ipaddr: typing.Union[str, int]) -> typing.Union[str, bool]:
        """Check if an IP address is in the unlimited ip list. Returns the network CIDR if the IP is in the list,
        otherwise it returns False. Accepts both IPv4 and IPv6 addresses as strings or integers.

        Ex:

         result = self.unlimited_ip_list.check_ipaddr(123456789)

         `result` can be a network CIDR or False
        """
        return self.__call__(ipaddr)

if __name__ == "__main__":
    print("This module is not meant to be run directly. Please import it in your code.")
