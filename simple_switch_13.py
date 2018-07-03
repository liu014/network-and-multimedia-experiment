# Copyright (C) 2011 Nippon Telegraph and Telephone Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import icmp
from ryu.lib.packet import ether_types
from ryu.lib import hub


class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
	self.threshold = 10485760
        self.datapaths = {}
        self.monitor_thread = hub.spawn(self._monitor)
	self.bandwidth = {}
	self.band = {}
        self.mac_to_port = {}
	self.traffic_info = []
	self.firewall_scr = []
	self.firewall_dst = []
	

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        dpid = datapath.id
        self.datapaths[dpid] = datapath

        # install table-miss flow entry
        #
        # We specify NO BUFFER to max_len of the output action due to
        # OVS bug. At this moment, if we specify a lesser number, e.g.,
        # 128, OVS will send Packet-In with invalid buffer_id and
        # truncated packet data. In that case, we cannot output packets
        # correctly.  The bug has been fixed in OVS v2.1.0.
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)


	#if dpid == 1:
	 #   self.add_flow(datapath,1,parser.OFPMatch(ipv4_src = '10.0.0.1',ipv4_dst = '10.0.0.3',eth_type='0x800'),[parser.OFPActionOutput(1)])
	  #  self.add_flow(datapath,1,parser.OFPMatch(ipv4_src = '10.0.0.3',ipv4_dst = '10.0.0.1',eth_type='0x800'),[parser.OFPActionOutput(3)])


        #elif dpid == 2:
	 #   self.add_flow(datapath,1,parser.OFPMatch(ipv4_src = '10.0.0.1',ipv4_dst = '10.0.0.3',eth_type='0x800'),[parser.OFPActionOutput(1)])
	  #  self.add_flow(datapath,1,parser.OFPMatch(ipv4_src = '10.0.0.3',ipv4_dst = '10.0.0.1',eth_type='0x800'),[parser.OFPActionOutput(3)])


#	elif dpid == 4:
#	    self.add_flow(datapath,1,parser.OFPMatch(ipv4_src = '10.0.0.1',ipv4_dst = '10.0.0.3',eth_type='0x800'),[parser.OFPActionOutput(3)])
#	    self.add_flow(datapath,1,parser.OFPMatch(ipv4_src = '10.0.0.3',ipv4_dst = '10.0.0.1',eth_type='0x800'),[parser.OFPActionOutput(1)])

        



    def _monitor(self):
        while True:
	    for dp in self.datapaths.values():
		self._request_stats(dp)
	    hub.sleep(1)

    def _request_stats(self,datapath):
        ofproto = datapath.ofproto
	parser = datapath.ofproto_parser
	
	req = parser.OFPPortStatsRequest(datapath,0,ofproto.OFPP_ANY)
	datapath.send_msg(req)




    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def _port_stats_reply_handler(self,ev):
	body = ev.msg.body
	parser = ev.msg.datapath.ofproto_parser
	dpid = ev.msg.datapath.id
	while len(self.traffic_info) < dpid:
		self.traffic_info.append('')
	

	



	self.logger.info('datapath         port     '
                         'rx-pkts  rx-bytes '
                         'tx-pkts  tx-bytes bandwidth')

        self.logger.info('---------------- -------- '
                         '-------- -------- '
                         '-------- -------- --------')
	
	self.traffic_info[dpid - 1] = ''
        self.traffic_info[dpid - 1] += 'datapath         port     rx-pkts  rx-bytes tx-pkts  tx-bytes bandwidth';
        self.traffic_info[dpid - 1] += '\n';                 
        self.traffic_info[dpid - 1] += '---------------- -------- -------- -------- -------- -------- --------';
        self.traffic_info[dpid - 1] += '\n';  
                        

	for stat in sorted(body):
	    if stat.port_no < 5:
	        index = str(ev.msg.datapath.id) + '-' + str(stat.port_no)
		if index not in self.bandwidth:
		    self.bandwidth[index] = 0
		    self.band[index] = 0
		transfer_bytes = stat.rx_bytes + stat.tx_bytes
		speed = (transfer_bytes - self.band[index]) / 3
		self.logger.info('%016x %8x %8d %8d %8d %8d %8d',
                                  ev.msg.datapath.id,stat.port_no,
                                  stat.rx_packets,stat.rx_bytes,stat.tx_packets,stat.rx_bytes,speed)
		self.traffic_info[dpid - 1] += '%016x' % (ev.msg.datapath.id);
		self.traffic_info[dpid - 1] += '%9x' % (stat.port_no)
		self.traffic_info[dpid - 1] += '%9d' % (stat.rx_packets)
		self.traffic_info[dpid - 1] += '%9d' % (stat.rx_bytes)
		self.traffic_info[dpid - 1] += '%9d' % (stat.tx_packets)
		self.traffic_info[dpid - 1] += '%9d' % (stat.rx_bytes)
		self.traffic_info[dpid - 1] += '%9d' % (speed)
                self.traffic_info[dpid - 1] += '\n'
				

		self.band[index] = transfer_bytes
		self.bandwidth[index] = speed#transfer_bytes
 #               if speed > self.threshold and index == '1-1':
#		    self.add_flow(self.datapaths[1],5,parser.OFPMatch(eth_src == '00:00:00:00:00:02'),[parser.OFPActionOutput(2)])
#		    self.add_flow(self.datapaths[3],5,parser.OFPMatch(eth_src == '00:00:00:00:00:02'),[parser.OFPActionOutput(2)])
#		    self.add_flow(self.datapaths[3],5,parser.OFPMatch(eth_dst == '00:00:00:00:00:02'),[parser.OFPActionOutput(1)])
#		    self.add_flow(self.datapaths[4],5,parser.OFPMatch(eth_dst == '00:00:00:00:00:02'),[parser.OFPActionOutput(2)])



    def get_traffic_info(self):
	tmp = ''
	for strin in self.traffic_info:
	    tmp += strin 
	return tmp

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)

	
    def fill_firewall(self,scr,dst):
	self.firewall_scr.append(scr);
	self.firewall_dst.append(dst);

	

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        # If you hit this you might want to increase
        # the "miss_send_length" of your switch
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]



        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return
        dst = eth.dst
        src = eth.src

        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})

        #self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)

        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = in_port



        pkt_icmp = pkt.get_protocol(icmp.icmp)
	
	for index in range(len(self.firewall_scr)):  
	    
	    if pkt_icmp and src == self.firewall_scr[index] and dst == self.firewall_dst[index] and pkt_icmp.type == icmp.ICMP_ECHO_REQUEST:
	        #print(dst)
		return 



        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        # install a flow to avoid packet_in next time
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
            # verify if we have a valid buffer_id, if yes avoid to send both
            # flow_mod & packet_out
	    
            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                self.add_flow(datapath, 1, match, actions, msg.buffer_id)
                return
            else:
                self.add_flow(datapath, 1, match, actions)
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)



#
	

   	cookie = cookie_mask = 0
    	matc = None
    	req = parser.OFPFlowStatsRequest(datapath, 0,
                                        ofproto.OFPTT_ALL,
                                        ofproto.OFPP_ANY, ofproto.OFPG_ANY,
                                        cookie, cookie_mask,
                                        matc)
    	datapath.send_msg(req)





#


	


