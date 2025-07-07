#!/usr/bin/env python3
""" 
 Unlimited IP List v1.0.1 Minified
 
 Unlimited IP Lists is a list-type object to manage the list of IPv4/IPv6 
 networks and perform quick searches using bisect and working with IPs 
 as integers. A list with 10000 IP/CIDR (IPv4 and IPv6) took 0.05 to be 
 processed. The verification is around 0.000005 regardless of the list size.

 by Ricardo Abuchaim - ricardoabuchaim@gmail.com
"""
import socket,struct,bisect,threading,math,typing,datetime
__all__=['UnlimitedIPList','UnlimitedIPListException']
class UnlimitedIPListException(Exception):...
'Custom exception for UnlimitedIPList errors.'
class UnlimitedIPList:
	'A list-type object to manage the list of IPv4/IPv6 networks and perform quick searches using bisect and working with IPs as integers.\n    A list with 10000 IP/CIDR (IPv4 and IPv6) took 0.05 to be processed. The verification is around 0.000005 regardless of the list size.\n    '
	def __init__(A,ip_networks_list,normalize_invalid_cidr=False,raise_on_error=False,debug=False):A._log_debug=A._log_debug if debug else lambda msg:None;A._lock=threading.RLock();A.__raise_on_error=raise_on_error;A.__normalize_invalid_cidr=normalize_invalid_cidr;A.discarded_cidrs=[];A.__list_chunks,A.__list_index=[],[];A.__first_ip_chunks,A.__last_ip_chunks=[],[];A._cidrs=[];A.__process_list(ip_networks_list)
	def __getitem__(A,index):return A._cidrs[index]
	def __iter__(A):return iter(A._cidrs)
	def __len__(A):return len(A._cidrs)
	def __contains__(A,item):return item.strip()in A._cidrs
	def __repr__(A):return repr(A._cidrs)
	def _log_debug(A,msg):'Log debug messages if debug mode is enabled';print(f"[38;2;0;255;0m{datetime.datetime.now().strftime('%y/%m/%d %H:%M:%S.%f')} [UNLIMITED_IP_LIST_DEBUG] {str(msg)}[0m")
	def is_valid_ipaddr(A,ipaddr):'Check if an IP address is valid. Accepts IPv4 or IPv6. (Elapsed average time: 0.000001)';return A.ip_to_int(ipaddr.strip())is not None
	def is_valid_iplong(A,iplong):'Check if an integer is a valid IPv4/IPv6 address. (Elapsed average time: 0.000001)';return A.int_to_ip(iplong)is not None
	def is_valid_cidr(H,cidr,strict=True):
		'Check if an IPv4/IPv6 CIDR is valid in pure Python.\n          \n           Accepts ONLY CIDR with the network address, not the host address.\n        \n        with strict=True, it checks if the bits outside the mask are zero.\n            Ex: 10.0.0.10/8 is INVALID, 10.0.0.0/8 is VALID, 10.0.0.10/32 is VALID\n            c1a5:9ba4:8d92:636e:60fd:8756:430b:0000/64 is INVALID, c1a5:9ba4:8d92:636e::/64 is VALID\n        \n        with strict=False, it only checks if the CIDR is well-formed.\n            Ex: 10.0.0.10/8 is VALID, 10.0.0.0/8 is VALID, 10.0.0.10/32 is VALID\n            c1a5:9ba4:8d92:636e:60fd:8756:430b:0000/64 is VALID, c1a5:9ba4:8d92:636e::/64 is VALID\n        ';C=strict;A=cidr
		try:
			A=A.strip()
			if'/'not in A:
				if C:return False
				else:A=H._normalize_cidr_suffix(A)
			D,I=A.split('/');B=int(I)
			if'.'in D:
				E=socket.inet_aton(D);F=struct.unpack('!L',E)[0]
				if not 0<=B<=32:return False
				if C:G=(1<<B)-1<<32-B;return F&~G==0
				return True
			else:
				E=socket.inet_pton(socket.AF_INET6,D);F=int.from_bytes(E,byteorder='big')
				if not 0<=B<=128:return False
				if C:G=(1<<B)-1<<128-B;return F&~G==0
				return True
		except Exception:return False
	def get_valid_cidr(F,cidr,normalize=True):
		'Returns a valid normalized CIDR (IPv4 or IPv6) in pure Python.\n        \n        If normalize is False, it returns the CIDR as it is, without checking if the bits outside the mask are zero.\n        \n        If normalize is True, it returns the CIDR with the network address, ensuring that the bits outside the mask are zero.\n        ';G=normalize;B=cidr
		try:
			B=B.strip()
			if'/'not in B:
				if not G:return
				B=F._normalize_cidr_suffix(B)
			D,K=B.split('/');A=int(K)
			if'.'in D:
				if not 0<=A<=32:return
				H=socket.inet_aton(D);E=struct.unpack('!L',H)[0]
				if G:C=(1<<A)-1<<32-A;I=E&C;J=socket.inet_ntoa(struct.pack('!L',I));return f"{J}/{A}"
				else:
					C=(1<<A)-1<<32-A
					if E&~C!=0:return
					return f"{D}/{A}"
			else:
				H=socket.inet_pton(socket.AF_INET6,D)
				if not 0<=A<=128:return
				E=int.from_bytes(H,byteorder='big')
				if G:C=(1<<A)-1<<128-A;I=E&C;J=F.compress_ipv6(F.int_to_ip(I));return f"{J}/{A}"
				else:
					C=(1<<A)-1<<128-A
					if E&~C!=0:return
					return f"{D}/{A}"
		except Exception as L:F._log_debug(f"Failed at UnlimitedIPList.get_valid_cidr({B}): {str(L)}");return
	def ip_to_int(B,ipaddr):
		'Converts an IPv4/IPv6 address to an integer. (Elapsed average time: 0.000001)';A=ipaddr
		try:return struct.unpack('!L',socket.inet_aton(A.strip()))[0]
		except Exception:
			try:return int.from_bytes(socket.inet_pton(socket.AF_INET6,A.strip()),byteorder='big')
			except Exception:return
	def int_to_ip(D,iplong):
		'Convert an integer to IP Address (IPv4 or IPv6). For IPv6, returns the full expanded zero-padded form.';A=iplong
		try:
			if A<=2**32:return socket.inet_ntoa(struct.pack('>L',A))
			else:B=A.to_bytes(16,byteorder='big');C=[f"{B[A]<<8|B[A+1]:04x}"for A in range(0,16,2)];return':'.join(C)
		except Exception:return
	def compress_ipv6(G,hextets):
		'Compresses an IPv6 address represented as a list of hextets.';A=hextets
		if isinstance(A,str):
			if'/'in A:A=A.split('/')[0]
			A=A.split(':')
		A=[A if A else'0000'for A in A]
		if len(A)!=8:A=A+['0000']*(8-len(A))
		D=B=-1;E=C=-1
		for F in range(8):
			if A[F]=='0000':
				if E==-1:E=F;C=1
				else:C+=1
			else:
				if C>B:D,B=E,C
				E=C=-1
		if C>B:D,B=E,C
		if B>1:
			A=A[:D]+['']+A[D+B:]
			if D==0:A=['']+A
			if D+B==8:A+=['']
		return':'.join(A).replace(':::','::')
	def _normalize_cidr_suffix(B,ipaddr):
		'Converts an IP address to CIDR format. Add /32 to the IPv4 address if it is not present \n        or add /128 to the IPv6 address if it is not present. (Elapsed average time 0.0000006)';A=ipaddr.strip()
		if'/'in A:return A
		return f"{A}/32"if':'not in A else f"{A}/128"
	def __split_list(B,a_list,size):
		'Split a_list in chunks defined by size';A=a_list
		try:return[A[B:B+size]for B in range(0,len(A),size)]
		except Exception as C:
			if B.__raise_on_error:raise UnlimitedIPListException(f"Failed at UnlimitedIPList.__split_list(): {str(C)}")
			return[]
	def __get_first_last_ip_cidr(F,cidr):
		'Get the first and last IP of a CIDR in integer format.'
		try:
			C,G=cidr.split('/');B=int(G);H=F.ip_to_int(C)
			if':'in C:A=128
			else:A=32
			D=(1<<B)-1<<A-B;D&=(1<<A)-1;E=H&D;I=E|(1<<A-B)-1;return E,I
		except Exception:return 0,0
	def __find_balanced_chunk_size(G,list_size,min_chunk_size=100,max_chunk_size=5000):
		'Finds a balanced chunk size for splitting a list of size n into chunks,\n        such that the difference between the number of chunks and the chunk size is minimized.';B=list_size
		if B<=min_chunk_size:return B
		D=1;E=float('inf')
		for A in range(1,max_chunk_size+1):
			F=math.ceil(B/A);C=abs(A-F)
			if C<=1:return A
			elif C<E:E=C;D=A
		return D
	def __clear_lists(A,clear_discarded_cidr=False):
		'Clear the internal lists used for processing'
		with A._lock:
			A._cidrs.clear();A.__list_chunks.clear();A.__first_ip_chunks.clear();A.__last_ip_chunks.clear();A.__list_index.clear()
			if clear_discarded_cidr:A.discarded_cidrs.clear()
	def __ip_ranges_overlap(A,first1,last1,first2,last2):'Check if two IP ranges overlap.';return not(last1<first2 or first1>last2)
	def _find_cidr_overlap(A,cidr):
		'Detects if a CIDR overlaps with any existing CIDR in the already processed list.'
		try:
			if not A._cidrs:return False
			E,F=A.__get_first_last_ip_cidr(A._normalize_cidr_suffix(cidr));B=bisect.bisect_right(A.__list_index,E)-1
			if B<0:B=0
			for C in range(len(A.__first_ip_chunks[B])):
				if A.__ip_ranges_overlap(E,F,A.__first_ip_chunks[B][C],A.__last_ip_chunks[B][C]):return A.__list_chunks[B][C]
			for G in[-1,1]:
				D=B+G
				if 0<=D<len(A.__first_ip_chunks):
					for C in range(len(A.__first_ip_chunks[D])):
						if A.__ip_ranges_overlap(E,F,A.__first_ip_chunks[D][C],A.__last_ip_chunks[D][C]):return A.__list_chunks[D][C]
		except Exception as H:
			if A.__raise_on_error:raise UnlimitedIPListException(f"Failed at UnlimitedIPList._find_cidr_overlap(): {str(H)}")
		return False
	def _remove_overlapping_cidrs(C,new_list):
		'Remove overlapping CIDRs from the new_list and sort them.';A=new_list;C._log_debug(f"Processing {len(A)} CIDRs to remove overlaps and sorting them.");D=[(A,*C.__get_first_last_ip_cidr(A))for A in A];D.sort(key=lambda x:x[1]);B=[];G,J,E=D[0];B.append(G)
		for(F,H,I)in D[1:]:
			if H<=E:C.discarded_cidrs.append(F)
			else:B.append(F);E=I
		A=B.copy();B.clear();return A
	def __normalize_and_remove_invalid_cidr(B,ip_networks_list):
		'Normalize the list of IPs in CIDR format and remove invalid CIDRs.';D=[]
		for A in ip_networks_list:
			C=B.get_valid_cidr(A,normalize=True)
			if C:
				if C!=A:B._log_debug(f"Normalized CIDR: {A} => {C}")
				D.append(C)
			else:B._log_debug(f"Invalid CIDR: {A}");B.discarded_cidrs.append(A)
		return D
	def __normalize_cidr(B,ip_networks_list):
		'Normalize the list of IPs in CIDR format and remove invalid CIDRs. \n        Just add /32 to IPv4 addresses and /128 to IPv6 addresses if they are not present.';A=[]
		for C in ip_networks_list:A.append(B._normalize_cidr_suffix(C))
		return A
	def __discard_invalid_cidr(B,ip_networks_list):
		'Remove invalid CIDRs from the list.';C=[]
		for A in ip_networks_list:
			if B.is_valid_cidr(A):C.append(A)
			else:B._log_debug(f"Invalid CIDR: {A}");B.discarded_cidrs.append(A)
		return C
	def __process_list(A,ip_networks_list,**E):
		'Process the ip_networks_list'
		try:
			if E.get('discarded_cidrs',[])==[]:A.discarded_cidrs.clear()
			B=list(set(ip_networks_list));B=[A.strip()for A in B if A.strip()];A._log_debug(f"Processing the ip_networks_list with {len(B)} unique items.")
			if len(B)==0:A._log_debug('The list is empty after removing duplicates and blank items, clearing the lists.');A.__clear_lists();return False
			else:
				if A.__normalize_invalid_cidr:A._log_debug(f"Normalizing the list of IPs in CIDR format and removing invalid CIDRs. Current size: {len(B)}");B=A.__normalize_and_remove_invalid_cidr(B);A._log_debug(f"After normalization, the list size is {len(B)}.")
				else:A._log_debug('Normalizing the list of IPs in CIDR format without removing invalid CIDRs.');B=A.__normalize_cidr(B)
				A._log_debug(f"Removing invalid CIDRs from the list. Current size: {len(B)}");B=A.__discard_invalid_cidr(B);A._log_debug(f"After removing invalid CIDRs, the list size is {len(B)}.")
				if len(B)==0:A._log_debug('All CIDRs were discarded, clearing the lists.');A.__clear_lists();return False
				else:
					B=sorted(list(filter(None,sorted(list(dict.fromkeys(B))))),key=lambda ip:A.ip_to_int(ip.split('/')[0]))
					if E.get('check_overlap',True):B=A._remove_overlapping_cidrs(B)
					A._log_debug(f"Discarded {len(A.discarded_cidrs)} invalid or overlapping CIDRs from the list ({A.discarded_cidrs})");C=len(B)if len(B)<=100 else A.__find_balanced_chunk_size(len(B));A._log_debug(f"Splitting the list into chunks of size {C} for better performance.");D=[A.__get_first_last_ip_cidr(B)for B in B]
					with A._lock:A.__list_chunks=A.__split_list(B,C);A.__first_ip_chunks=A.__split_list([A[0]for A in D],C);A.__last_ip_chunks=A.__split_list([A[1]for A in D],C);A.__list_index=[A[0]for A in A.__first_ip_chunks];A._cidrs=B.copy()
					D.clear();B.clear();return True
		except Exception as F:
			A.clear_ip_networks_list()
			if A.__raise_on_error:raise UnlimitedIPListException(f"Failed at UnlimitedIPList.__process_list(): {str(F)}")
			return False
	def set_ip_networks_list(A,list_items):'Set a new networks list';A.clear_ip_networks_list();A.__process_list(list_items)
	def get_ip_networks_list(A):'Get the current unlimited ip networks list';return list(A._cidrs)
	def clear_ip_networks_list(A):'Clear the unlimited ip networks list';A.__clear_lists(clear_discarded_cidr=True);A._log_debug('Cleared the unlimited ip networks list.')
	def test_is_valid_ip_network(A,ipaddr):
		' Check if the provided IP address or CIDR is valid to be added into the unlimited ip list.\n            Returns the CIDR (normalized with /32 or /128) if valid, otherwise returns False.\n        ';D=ipaddr
		if not isinstance(D,str):raise TypeError('ipaddr must be a string (IPv4/IPv6 address or CIDR)')
		try:
			B=A._normalize_cidr_suffix(D.strip())
			if not A.is_valid_cidr(B):
				A._log_debug(f"Invalid CIDR: {B}")
				if A.__raise_on_error:raise UnlimitedIPListException(f"Invalid CIDR {B}.")
				return False
			if B in A._cidrs:
				A._log_debug(f"CIDR {B} already exists in the list.")
				if A.__raise_on_error:raise UnlimitedIPListException(f"CIDR {B} already exists in the list.")
				return False
			C=A._find_cidr_overlap(B)
			if C:
				A._log_debug(f"CIDR {B} overlaps with existing CIDRs ({C}) in the list.")
				if A.__raise_on_error:raise UnlimitedIPListException(f"CIDR {B} overlaps with existing CIDRs ({C}) in the list.")
				return False
			return B
		except Exception as E:
			if A.__raise_on_error:raise UnlimitedIPListException(f"Failed at UnlimitedIPList.add_ip(): {str(E)}")
		return False
	def add_ip_network(A,ipaddr):
		'Add an IPv4/IPv6 address or CIDR to unlimited ip list';C=ipaddr
		if not isinstance(C,str):raise TypeError('ipaddr must be a string (IPv4/IPv6 address or CIDR)')
		try:
			A.discarded_cidrs.clear();B=C.strip()
			if A.__normalize_invalid_cidr:
				B=A.get_valid_cidr(B,normalize=True)
				if not B:A.discarded_cidrs.append(C.strip());return False
			B=A.test_is_valid_ip_network(B)
			if not B:A.discarded_cidrs.append(C.strip());return False
			A._cidrs.append(B);A.__process_list(A._cidrs,check_overlap=False,discarded_cidrs=A.discarded_cidrs);return True
		except Exception as D:
			if A.__raise_on_error:raise UnlimitedIPListException(f"Failed at UnlimitedIPList.add_ip(): {str(D)}")
		return False
	def add_ip_networks_list(A,ipaddr_list):
		'Add a list of IPv4/IPv6 addresses or CIDRs to unlimited ip list';D=ipaddr_list
		if not isinstance(D,list):raise TypeError('ipaddr_list must be a list of strings (IPv4/IPv6 addresses or valid CIDRs)')
		try:
			A.discarded_cidrs.clear()
			for C in D:
				B=C.strip()
				if A.__normalize_invalid_cidr:B=A.get_valid_cidr(B,normalize=True)
				if not B:A.discarded_cidrs.append(C.strip());continue
				B=A.test_is_valid_ip_network(B)
				if not B:A.discarded_cidrs.append(C.strip())
				else:A._cidrs.append(B)
			A.__process_list(A._cidrs,check_overlap=True,discarded_cidrs=A.discarded_cidrs);return True
		except Exception as E:
			if A.__raise_on_error:raise UnlimitedIPListException(f"Failed at UnlimitedIPList.add_ip_list(): {str(E)}")
		return False
	def remove_ip_network(A,ipaddr):
		'Remove an IPv4/IPv6 or a CIDR from unlimited ip list';C=ipaddr
		if not isinstance(C,str):raise TypeError('ipaddr must be a string (a valid IPv4/IPv6 address or valid CIDR)')
		if not A._cidrs:return False
		try:
			B=A._normalize_cidr_suffix(C.strip())
			if B and B in A._cidrs:A._cidrs.remove(B);A.__process_list(A._cidrs,check_overlap=False);return True
			else:A._log_debug(f"IP address or CIDR {B} not found in the list.");return False
		except Exception as D:
			if A.__raise_on_error:raise UnlimitedIPListException(f"Failed at UnlimitedIPList.remove_ip_network(): {str(D)}")from None
		return False
	def remove_ip_networks_list(A,ipaddr_list):
		'Remove a list of IPv4/IPv6 addresses or CIDRs from unlimited ip list';C=ipaddr_list
		if not isinstance(C,list):raise TypeError('ipaddr_list must be a list of strings (IPv4/IPv6 addresses or valid CIDRs)')
		if not A._cidrs:return False
		try:
			for B in C:
				B=A._normalize_cidr_suffix(B.strip())
				if B and B in A._cidrs:A._cidrs.remove(B)
				else:A._log_debug(f"IP address or CIDR {B} not found in the list.")
			A.__process_list(A._cidrs,check_overlap=False);return True
		except Exception as D:
			if A.__raise_on_error:raise UnlimitedIPListException(f"Failed at UnlimitedIPList.remove_ip_network_list(): {str(D)}")from None
		return False
	def __call__(A,ipaddr):
		'Check if an IP address is in the unlimited ip list. Returns the network CIDR if the IP is in the list,\n        otherwise it returns False. (Elapsed average time: 0.000002)\n\n        Ex:\n\n         result = self.unlimited_ip_list("192.168.1.1")\n            `result` can be a network CIDR or False\n        ';B=ipaddr
		try:
			if not A._cidrs:return False
			if isinstance(B,int):C=B
			elif isinstance(B,str):C=A.ip_to_int(B.strip())
			if C is None or C<=0:
				A._log_debug(f"Invalid IP address: {B.strip()}")
				if A.__raise_on_error:raise UnlimitedIPListException(f"Invalid IP address: {B.strip()}")
				return False
			D=bisect.bisect_right(A.__list_index,C)-1;E=bisect.bisect_right(A.__first_ip_chunks[D],C)-1
			try:F=A.__list_chunks[D][E]
			except Exception:F=False
			G=C>=A.__first_ip_chunks[D][E]and C<=A.__last_ip_chunks[D][E];return F if G else False
		except Exception as H:
			if A.__raise_on_error:raise UnlimitedIPListException(f"Failed at NoLimitList.check_ipaddr({B.strip()}): {str(H)}")
			return False
	def check_ipaddr(A,ipaddr):'Check if an IP address is in the unlimited ip list. Returns the network CIDR if the IP is in the list,\n        otherwise it returns False. Accepts both IPv4 and IPv6 addresses as strings or integers.\n\n        Ex:\n\n         result = self.unlimited_ip_list.check_ipaddr(123456789)\n\n         `result` can be a network CIDR or False\n        ';return A.__call__(ipaddr)
if __name__=='__main__':print('This module is not meant to be run directly. Please import it in your code.')