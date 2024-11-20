from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel

def custom_topology():
    net = Mininet(controller=RemoteController, link=TCLink)

    # Add Floodlight Controller
    controller = net.addController(
        'floodlight',
        controller=RemoteController,
        ip='127.0.0.1',
        port=6653
    )

    # Add Switch
    s1 = net.addSwitch('s1')

    # Add Hosts (Servers and Clients)
    h1 = net.addHost('h1', ip='10.0.0.1')
    h2 = net.addHost('h2', ip='10.0.0.2')
    h3 = net.addHost('h3', ip='10.0.0.3')
    h4 = net.addHost('h4', ip='10.0.0.4')
    h5 = net.addHost('h5', ip='10.0.0.5')

    # Add Links
    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(h3, s1)
    net.addLink(h4, s1)
    net.addLink(h5, s1)

    # Start the network
    net.build()
    controller.start()
    s1.start([controller])

    # Start CLI
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    custom_topology()

# sudo python custom_topology.py