# Copyright (c) 2018 SONATA-NFV, 5GTANGO and Paderborn University
# ALL RIGHTS RESERVED.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Neither the name of the SONATA-NFV, 5GTANGO, Paderborn University
# nor the names of its contributors may be used to endorse or promote
# products derived from this software without specific prior written
# permission.
#
# This work has also been performed in the framework of the 5GTANGO project,
# funded by the European Commission under Grant number 761493 through
# the Horizon 2020 and 5G-PPP programmes. The authors would like to
# acknowledge the contributions of their colleagues of the 5GTANGO
# partner consortium (www.5gtango.eu).
import logging
from turtle import delay
from mininet.log import setLogLevel

from emuvim.dcemulator.net import DCNetwork
from containernet.node import DockerSta
from mininet.node import RemoteController, Controller

from emuvim.api.rest.rest_api_endpoint import RestApiEndpoint
from emuvim.api.tango import TangoLLCMEndpoint

logging.basicConfig(level=logging.DEBUG)
setLogLevel('info')  # set Mininet loglevel
logging.getLogger('werkzeug').setLevel(logging.DEBUG)
logging.getLogger('5gtango.llcm').setLevel(logging.DEBUG)


def create_topology():
    net = DCNetwork(monitor=False, enable_learning=True, controller=Controller)
    # create two data centers
    ap1 = net.addAccessPoint('ap1', channel="6", mode="g",ssid="ap1-ssid",
                            position='30,60,0', range="30")
    ap2 = net.addAccessPoint('ap2', channel="11", mode="g",ssid="ap2-ssid",
                            position='90,60,0',range="30")

    sta1 = net.addStation('sta1', position='40,50,0',
                          cls=DockerSta, dimage="iperf_test_1:latest")
    sta2 = net.addStation('sta2', position='80,70,0',
                          cls=DockerSta, dimage="iperf_test_1:latest")
    
    #c0 = net.addController('c0')
    controllers = net.controllers
    c0 = controllers[0]

    # print("Controller info : \n")
    # print(c0)

    # dc1 = net.addDatacenter("dc1")
    # dc2 = net.addDatacenter("dc2")
 
    net.configureWifiNodes()
    # s1 = net.addSwitch('s1')
    # s2 = net.addSwitch('s2')
    
    # interconnect data centers, switches and access points
 #   net.addLink(s1, ap1)
 #   net.addLink(s1, s2)
 #   net.addLink(s1, dc1, delay="10ms")
    net.addLink(ap1,ap2)
    # net.addLink(dc1, dc2, delay="20ms")
    # net.addLink(ap1, dc1, delay="10ms")
    # net.addLink(ap2, dc2, delay="30ms")

    net.build()

    #c0.start()
    ap1.start([c0])
    ap2.start([c0])
    # add the command line interface endpoint to the emulated DC (REST API)
    # rapi1 = RestApiEndpoint("0.0.0.0", 5001)
    # rapi1.connectDCNetwork(net)
    # rapi1.connectDatacenter(dc1)
    # rapi1.connectDatacenter(dc2)
    # rapi1.start()
    # # add the 5GTANGO lightweight life cycle manager (LLCM) to the topology
    # llcm1 = TangoLLCMEndpoint("0.0.0.0", 5000, deploy_sap=False)
    # llcm1.connectDatacenter(dc1)
    # llcm1.connectDatacenter(dc2)
    # # run the dummy gatekeeper (in another thread, don't block)
    # llcm1.start()
    # start the emulation and enter interactive CLI
    """plot graph"""
    net.plotGraph(max_x=100, max_y=100)

    net.start()

    sta1.cmd('iw dev sta1-wlan0 connect ap1-ssid')
    sta2.cmd('iw dev sta2-wlan0 connect ap2-ssid')
    
    net.CLI()
    # when the user types exit in the CLI, we stop the emulator
    net.stop()

def main():
    create_topology()


if __name__ == '__main__':
    main()
