import requests
import hashlib
import time

# Floodlight REST API URLs
FLOODLIGHT_BASE_URL = "http://127.0.0.1:8080"
FLOW_PUSHER_URL = f"{FLOODLIGHT_BASE_URL}/wm/staticflowpusher/json"
TOPOLOGY_URL = f"{FLOODLIGHT_BASE_URL}/wm/topology/links/json"

# List of servers
servers = ['10.0.0.1', '10.0.0.2', '10.0.0.3']

# Global variable to store topology state
current_topology = set()

def ip_hash(client_ip):
    """Hash the client IP and map to a server"""
    hash_value = int(hashlib.md5(client_ip.encode()).hexdigest(), 16)
    server_index = hash_value % len(servers)
    return servers[server_index]

def add_flow_rule(switch, client_ip, server_ip):
    """Add a flow rule to the Floodlight controller"""
    flow_rule = {
        "switch": switch,
        "name": f"flow_{client_ip}_to_{server_ip}",
        "cookie": "0",
        "priority": "32768",
        "in_port": "1",  # Assume client connects on port 1
        "eth_type": "0x0800",
        "ipv4_src": client_ip,
        "ipv4_dst": server_ip,
        "active": "true",
        "actions": f"output=2"  # Assume server is on port 2
    }

    response = requests.post(FLOW_PUSHER_URL, json=flow_rule)
    if response.status_code == 200:
        print(f"Flow rule added for {client_ip} -> {server_ip}")
    else:
        print(f"Failed to add flow rule: {response.text}")

def delete_flow_rule(flow_name):
    """Delete a flow rule by name"""
    delete_payload = {"name": flow_name}
    response = requests.delete(FLOW_PUSHER_URL, json=delete_payload)
    if response.status_code == 200:
        print(f"Flow rule {flow_name} deleted")
    else:
        print(f"Failed to delete flow rule: {response.text}")

def get_topology():
    """Fetch the current topology from Floodlight"""
    response = requests.get(TOPOLOGY_URL)
    if response.status_code == 200:
        links = response.json()
        topology = set((link['src-switch'], link['dst-switch']) for link in links)
        return topology
    else:
        print(f"Failed to fetch topology: {response.text}")
        return set()

def update_topology_and_flows():
    """Check topology for changes and update flow rules"""
    global current_topology
    new_topology = get_topology()

    if new_topology != current_topology:
        print("Topology change detected!")
        # Remove old flow rules
        for client_ip in ['10.0.0.4', '10.0.0.5']:
            for server_ip in servers:
                delete_flow_rule(f"flow_{client_ip}_to_{server_ip}")

        # Add new flow rules based on the updated topology
        for client_ip in ['10.0.0.4', '10.0.0.5']:
            server_ip = ip_hash(client_ip)
            add_flow_rule("00:00:00:00:00:00:00:01", client_ip, server_ip)

        # Update the topology state
        current_topology = new_topology
    else:
        print("No topology change detected.")

def main():
    # Initial flow setup
    for client_ip in ['10.0.0.4', '10.0.0.5']:
        server_ip = ip_hash(client_ip)
        add_flow_rule("00:00:00:00:00:00:00:01", client_ip, server_ip)

    # Monitor topology changes
    while True:
        update_topology_and_flows()
        time.sleep(10)  # Check topology every 10 seconds

if __name__ == "__main__":
    main()
