import json
import ast
import socket


import simple_switch_13
from webob import Response
from ryu.controller import ofp_event
from ryu.controller import dpset
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.app.wsgi import ControllerBase, WSGIApplication, route
from ryu.lib import hub
from ryu.lib import dpid as dpid_lib
from ryu.lib import ofctl_v1_0
from ryu.lib import ofctl_v1_2
from ryu.lib import ofctl_v1_3
from ryu.lib import ofctl_v1_4
from ryu.lib import ofctl_v1_5
from ryu.ofproto import ofproto_v1_0
from ryu.ofproto import ofproto_v1_2
from ryu.ofproto import ofproto_v1_3
from ryu.ofproto import ofproto_v1_4
from ryu.ofproto import ofproto_v1_5



simple_switch_instance_name = 'simple_switch_api_app'
url = '/simpleswitch/mactable/{dpid}'


supported_ofctl = {
    ofproto_v1_0.OFP_VERSION: ofctl_v1_0,
    ofproto_v1_2.OFP_VERSION: ofctl_v1_2,
    ofproto_v1_3.OFP_VERSION: ofctl_v1_3,
    ofproto_v1_4.OFP_VERSION: ofctl_v1_4,
    ofproto_v1_5.OFP_VERSION: ofctl_v1_5,
}







class SimpleSwitchRest13(simple_switch_13.SimpleSwitch13):
	_CONTEXTS = {
        'dpset': dpset.DPSet,
        'wsgi': WSGIApplication
    }

	def __init__(self, *args, **kwargs):
		super(SimpleSwitchRest13, self).__init__(*args, **kwargs)
		self.switches = {}
		wsgi = kwargs['wsgi']
		wsgi.register(SimpleSwitchController, {simple_switch_instance_name : self})
		
		#self.dpset = kwargs['dpset']
		self.flows = []
                self.flows.append([])
		self.flow_msg = []
       		
        	#self.waiters = {}
        	#self.data = {}
        	#self.data['dpset'] = self.dpset
        	#self.data['waiters'] = self.waiters
		#self.data['simple_switch_api_app'] = {simple_switch_instance_name : self}
        	#mapper = wsgi.mapper

        	#wsgi.registory['SimpleSwitchController'] = self.data
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_address = ('127.0.0.1', 8082)
		self.sock.connect(server_address)
		

	

	@set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
     	def bandwidth_sender(self,ev):
		#bandwidth_string = []
#		
		data = json.dumps(self.bandwidth)
		#print(data)
		data = 'x' + data
		self.sock.sendall(data)
	 	
		#hub.sleep(1);
	@set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
	def switch_features_handler(self, ev):
		super(SimpleSwitchRest13, self).switch_features_handler(ev)
		datapath = ev.msg.datapath
		self.switches[datapath.id] = datapath
		self.mac_to_port.setdefault(datapath.id, {})


	@set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
	def flow_stats_reply(self,ev):
		
		dpid = ev.msg.datapath.id
		
                while len(self.flows) < dpid:
			self.flows.append('')
			
		
		while len(self.flow_msg) < dpid:
			self.flow_msg.append('')
		self.flow_msg[dpid - 1] = ev.msg
		flow_string = []
		count = 0
		for stat in ev.msg.body:
			flow_string.append('match=%s instructions=%s '
                                     'duration_sec=%d duration_nsec=%d '
                                     'priority=%d '
                                     'idle_timeout=%d hard_timeout=%d flags=0x%04x '
                                     'cookie=%d packet_count=%d byte_count=%d '
                                     'table_id=%s' %
                                     (stat.match, stat.instructions,
                                      stat.duration_sec, stat.duration_nsec,
                                      stat.priority,
                                      stat.idle_timeout, stat.hard_timeout, stat.flags,
                                      stat.cookie, stat.packet_count, stat.byte_count,
                                      stat.table_id)) 
			
		self.flows[dpid - 1] = flow_string


	def modify_flow(self,dpid,match,action):
		datapath = self.flow_msg[int(dpid) - 1].datapath
		ofp = datapath.ofproto
		ofp_parser = datapath.ofproto_parser
		for stat in self.flow_msg[int(dpid) - 1].body:
			if str(stat.match).find(match["dl_dst"]) != -1:
				cookie = int(stat.cookie)
				cookie_mask = 0
				table_id = int(stat.table_id)
				idle_timeout = int(stat.idle_timeout)
				hard_timeout = int(stat.hard_timeout)
				priority = int(stat.priority)
				buffer_id = ofp.OFP_NO_BUFFER
				matchh = ofp_parser.OFPMatch(eth_dst = match["dl_dst"],in_port = int(match["in_port"]))
				actions = action
				inst = [ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS,actions)]
				req = ofp_parser.OFPFlowMod(datapath,cookie,cookie_mask,table_id,ofp.OFPFC_MODIFY,idle_timeout,hard_timeout,
                                                                      priority,buffer_id,ofp.OFPG_ANY,ofp.OFPG_ANY,ofp.OFPFF_SEND_FLOW_REM,matchh,inst)
				datapath.send_msg(req)
				break


	

	def set_mac_to_port(self, dpid, entry):
		mac_table = self.mac_to_port.setdefault(dpid, {})
		datapath = self.switches.get(dpid)

		entry_port = entry['port']
		entry_mac = entry['mac']
		if datapath is not None:
			parser = datapath.ofproto_parser
			if entry_port not in mac_table.values():
				for mac, port in mac_table.items():
					actions = [parser.OFPActionOutput(entry_port)]
					match = parser.OFPMatch(in_port=port, eth_dst=entry_mac)
					self.add_flow(datapath, 1, match, actions)
					actions = [parser.OFPActionOutput(port)]
					match = parser.OFPMatch(in_port=entry_port, eth_dst=mac)
					self.add_flow(datapath, 1, match, actions)
				mac_table.update({entry_mac : entry_port})

		return mac_table


	def set_traffic_info(self):
		traffic = self.get_traffic_info()
		return traffic

	def get_flows(self):
		return self.flows



class SimpleSwitchController(ControllerBase):

	def __init__(self, req, link, data, **config):
		super(SimpleSwitchController, self).__init__(req, link, data, **config)
		#print(data)		
		#self.dpset = data['dpset']
		#self.waiters = data['waiters']
		self.simple_switch_app = data[simple_switch_instance_name]#[simple_switch_instance_name]
		
		

	@route('simpleswitch', '/simpleswitch/mactable/{dpid}', methods=['GET'], requirements={'dpid':dpid_lib.DPID_PATTERN})
	def list_mac_table(self, req, **kwargs):
		simple_switch = self.simple_switch_app
		dpid = dpid_lib.str_to_dpid(kwargs['dpid'])

		if dpid not in simple_switch.mac_to_port:
		        start_responce('404 Not Found',[('Content-type','text/plain')])
			return [str(dpid) + 'is not exit']

		mac_table = simple_switch.mac_to_port.get(dpid, {})
		body = json.dumps(mac_table)

		return Response(content_type='application/json', body=body)

	@route('simpleswitch', '/simpleswitch/mactable/{dpid}', methods=['PUT'], requirements={'dpid': dpid_lib.DPID_PATTERN})
	def put_mac_table(self, req, **kwargs):

		simple_switch = self.simple_switch_app
		dpid = dpid_lib.str_to_dpid(kwargs['dpid'])
		new_entry = eval(req.body)

		if dpid not in simple_switch.mac_to_port:
			start_responce('404 Not Found',[('Content-type','text/plain')])
			return [str(dpid) + 'is not exit']

		try:
			mac_table = simple_switch.set_mac_to_port(dpid, new_entry)
			body = json.dumps(mac_table)
			return Response(content_type='application/json', body=body)
		except Exception as e:
			print(e)
			return Response(status=500)



	@route('trafficmonitor', '/trafficmonitor/portstat', methods=['GET'])
	def list_traffic_info(self, req, **kwargs):
		simple_switch = self.simple_switch_app
		traffic = simple_switch.set_traffic_info()
		body = traffic
		return Response(content_type='application/json', body=body)




	#@route('trafficmonitor', '/trafficmonitor/flowstat', methods=['GET'])


	@route('stats', '/stats/flow/{dpid}', methods=['GET'], requirements={'dpid': dpid_lib.DPID_PATTERN})
	def list_flow_table(self, req, **kwargs):
		simple_switch = self.simple_switch_app
		dpid = dpid_lib.str_to_dpid(kwargs['dpid'])
		
		if dpid not in simple_switch.mac_to_port:
			start_responce('404 Not Found',[('Content-type','text/plain')])
			return [str(dpid) + 'is not exit']

		
		flows = simple_switch.get_flows()
		#print(flows[dpid - 1])
		body = json.dumps(flows[dpid - 1])
		#print(body)
		return Response(content_type='application/json', body=body)


	@route('stats', '/stats/flow/modify', methods=['POST'])
	def modify_flow_table(self, req, **kwargs):
		simple_switch = self.simple_switch_app
		body = json.loads(req.body)
		dpid = body["dpid"]
		match = body["match"]
		action = body["actions"]
		simple_switch.modify_flow(dpid,match,action)
		return Response(content_type='application/json', body=" ")

	@route('firewall', '/firewall', methods=['POST'])
	def add_firewall(self, req, **kwargs):
		simple_switch = self.simple_switch_app
		change = False
		src = ""
		dst = ""
		print(req.body)
		for i in range(len(req.body)):
			if change == False:
				if req.body[i] == ' ':
					change = True
					continue
				src = src + req.body[i]
			else:
				dst = dst + req.body[i]
		
		simple_switch.fill_firewall(src,dst)
		return Response(content_type='application/json', body=" ")





