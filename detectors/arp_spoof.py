from scapy.layers.l2 import ARP
import time

mac_ip_map = {}
attack_state = {}

COOLDOWN = 30


def detect(packet):

    if not packet.haslayer(ARP):
        return None

    ip = packet[ARP].psrc
    mac = packet[ARP].hwsrc
    now = time.time()

    # first time
    if mac not in mac_ip_map:
        mac_ip_map[mac] = ip
        attack_state[mac] = {
            "last_alert_time": 0,
            "last_ip": ip
        }
        return None

    old_ip = mac_ip_map[mac]

    # update mapping
    mac_ip_map[mac] = ip

    # no spoof
    if old_ip == ip:
        return None

    state = attack_state[mac]

    # prevent duplicate spam
    if state["last_ip"] == ip:
        return None

    # cooldown
    if now - state["last_alert_time"] < COOLDOWN:
        return None

    # update state
    state["last_alert_time"] = now
    state["last_ip"] = ip

    return {
        "type": "ARP Spoofing",
        "mac": mac,
        "old_ip": old_ip,
        "new_ip": ip
    }