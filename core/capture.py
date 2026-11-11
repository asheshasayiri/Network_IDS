import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from scapy.all import sniff, ARP, IP, TCP, UDP, DNS

# detectors
from detectors.arp_spoof import detect as detect_arp
from detectors.dns_detector import detect_dns_spoof
from core.logger import log


def process_packet(packet):

    alerts = []

    # ───────── KNOWN ATTACK DETECTORS ─────────

    if packet.haslayer(ARP):
        a = detect_arp(packet)
        if a:
            alerts.append(a)

    # DNS (optional)
    if packet.haslayer(DNS) and packet.haslayer(UDP):
         a = detect_dns_spoof(packet)
         if a:
             alerts.append(a)

    
    # ───────── OUTPUT ─────────

    for alert in alerts:
        print("\n🚨 ALERT DETECTED")
        print(alert)
        print("-" * 40)
        log(alert)


print("🚀 Capturing packets and identifying anomolies!!!!!!!")
sniff(prn=process_packet, store=False)