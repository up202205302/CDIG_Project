# ! bin/bash

# Create FIFO only if missing
if [[ ! -p /tmp/wifi.pcap ]]; then
	mkfifo /tmp/wifi.pcap
fi

# Start Wireshark on the FIFO
wireshark -k -i /tmp/wifi.pcap -y IEEE802_11 &

# Start GNU Radio Companion
killall gnuradio-companion 2>/dev/null
gnuradio-companion
