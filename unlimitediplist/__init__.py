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
from .unlimitediplist import UnlimitedIPList, UnlimitedIPListException