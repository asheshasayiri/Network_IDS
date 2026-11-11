import os, sys, time
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from scapy.all import DNS, IP, UDP
from core.logger import log

# ---------------- STATE ----------------
# { domain: [(ip, timestamp), ...] }
dns_records = {}

# to avoid repeated alerts
alerted = set()

# config
TIME_WINDOW = 30        # seconds
MAX_IP_THRESHOLD = 3    # allowed IP changes


# ---------------- DETECT ----------------
def detect_dns_spoof(packet):

    # ✅ Only DNS responses
    if not (packet.haslayer(DNS) and packet[DNS].qr == 1):
        return None

    # ✅ Must have answers
    if packet[DNS].ancount == 0:
        return None

    # ✅ Ignore mDNS (port 5353)
    if packet.haslayer(UDP) and packet[UDP].sport == 5353:
        return None

    try:
        dns = packet[DNS]

        for i in range(dns.ancount):
            answer = dns.an

            # walk answer chain
            for _ in range(i):
                answer = answer.payload

            # ✅ Only A records (IPv4)
            if answer.type != 1:
                continue

            # extract domain & IP
            domain = answer.rrname.decode(errors="ignore") if isinstance(answer.rrname, bytes) else str(answer.rrname)
            ip = answer.rdata if isinstance(answer.rdata, str) else str(answer.rdata)

            if not domain or not ip:
                continue

            # ✅ Ignore .local domains (BIG FIX)
            if domain.endswith(".local."):
                return None

            now = time.time()

            # first time seen
            if domain not in dns_records:
                dns_records[domain] = [(ip, now)]
                print(f"  [DNS] Learned  {domain:<35} → {ip}")
                continue

            # add new record
            dns_records[domain].append((ip, now))

            # remove old entries
            dns_records[domain] = [
                (i, t) for (i, t) in dns_records[domain]
                if now - t < TIME_WINDOW
            ]

            # unique IPs in time window
            unique_ips = set(i for (i, _) in dns_records[domain])

            # normal behavior → multiple IPs allowed
            if len(unique_ips) <= MAX_IP_THRESHOLD:
                continue

            # 🚨 SPOOF DETECTED (too many IP changes quickly)
            alert_key = (domain, tuple(sorted(unique_ips)))
            if alert_key in alerted:
                continue
            alerted.add(alert_key)

            old_ips = ", ".join(set(i for (i, _) in dns_records[domain][:-1]))
            new_ip = ip

            alert = {
                "type": "DNS Spoofing",
                "mac": packet[IP].src if packet.haslayer(IP) else "N/A",
                "old_ip": old_ips,
                "new_ip": new_ip,
                "status": "DETECTED",
                "domain": domain,
            }

            print(f"""
  ╔══════════════════════════════════════════════════════════╗
  ║          ⚠  DNS SPOOFING DETECTED                       ║
  ╠══════════════════════════════════════════════════════════╣
  ║  Domain       : {domain:<40}                             ║
  ║  Previous IPs : {old_ips:<40}                            ║
  ║  New Suspicious IP : {new_ip:<34}                         ║
  ╚══════════════════════════════════════════════════════════╝
""")

            log(alert)
            return alert

    except Exception:
        pass

    return None