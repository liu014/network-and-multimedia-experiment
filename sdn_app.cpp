#include<iostream>
#include<fstream>
#include<sstream>
#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include<string>   
#include<sys/socket.h>
#include<sys/types.h>
#include<unistd.h>
#include<arpa/inet.h>
#include<netdb.h>
#include<errno.h>
#include<vector>


using namespace std;






class HTTP
{
public:
	HTTP()
	{
		socket_desc = socket(AF_INET, SOCK_STREAM, 0);
		if (socket_desc == -1) perror("create socket failed");
	}

	
	void connect_server()
	{
		memset(&server,0,sizeof(server));
		
		server.sin_addr.s_addr = inet_addr("0.0.0.0");
		server.sin_family = AF_INET;
		server.sin_port = htons(8080);
		if (connect(socket_desc, (struct sockaddr *)&server, sizeof(server)) < 0)
		{
			perror("connect error");
			exit(-1);
		}
	}

	void get_mactable(string dpid)const
	{
	
	        string tmp = "GET /simpleswitch/mactable/";
		tmp += dpid;
		tmp += " HTTP/1.1\r\nHost: ";
		//string tmp = "GET /?st=1 HTTP/1.1\r\nHost: ";
		
		tmp +="0.0.0.0";
		tmp += "\r\n\r\n";
		const char* message = tmp.c_str();

		if (send(socket_desc, message, strlen(message), 0) < 0)
		{
			perror("send error");
			exit(-1);
		}

	}


	void get_traffic_info()const
	{
	
	        string tmp = "GET /trafficmonitor/portstat";
		tmp += " HTTP/1.1\r\nHost: ";
		//string tmp = "GET /?st=1 HTTP/1.1\r\nHost: ";
		
		tmp +="0.0.0.0";
		tmp += "\r\n\r\n";
		const char* message = tmp.c_str();

		if (send(socket_desc, message, strlen(message), 0) < 0)
		{
			perror("send error");
			exit(-1);
		}

	}


	void get_flowtable(string dpid)const
	{
	
	        string tmp = "GET /stats/flow/";
		tmp += dpid;
		tmp += " HTTP/1.1\r\nHost: ";
		//string tmp = "GET /?st=1 HTTP/1.1\r\nHost: ";
		
		tmp +="0.0.0.0";
		tmp += "\r\n\r\n";
		const char* message = tmp.c_str();

		if (send(socket_desc, message, strlen(message), 0) < 0)
		{
			perror("send error");
			exit(-1);
		}

	}


	void post_flow_modify(string dpid,string dl_dst,string in_port)const
	{
		string d;
		for(size_t k = 0; k < dpid.size(); ++k) if(dpid[k] != '0') d += dpid[k];
	        string tmp = "POST /stats/flow/modify";
		tmp += " HTTP/1.1\r\nHost: ";
		//string tmp = "GET /?st=1 HTTP/1.1\r\nHost: ";
		tmp +="0.0.0.0";
		tmp += "\r\nContent-Type: application/json\r\nContent-Length: ";
		string tmp1;
    		tmp1 += "{\"dpid\": ";
		tmp1 += d;
		tmp1 += ", \"match\" :{\"dl_dst\": \"";
		tmp1 += dl_dst;
		tmp1 += "\", \"in_port\": ";
		tmp1 += in_port;
		tmp1 += "}, \"actions\": []}";
		char* str;
		sprintf(str,"%d",(int)tmp1.size());
		tmp += str;
		tmp += "\r\n\r\n";
		tmp += tmp1;
		const char* message = tmp.c_str();

		if (send(socket_desc, message, strlen(message), 0) < 0)
		{
			perror("send error");
			exit(-1);
		}

	}




	void post_firewall(string src,string dst)const
	{
	        string tmp = "POST /firewall";
		tmp += " HTTP/1.1\r\nHost: ";
		//string tmp = "GET /?st=1 HTTP/1.1\r\nHost: ";
		tmp +="0.0.0.0";
		tmp += "\r\nContent-Type: application/json\r\nContent-Length: ";
		char str[50];
		int num = (src.size() + dst.size() + 1);
		sprintf(str,"%d",num);
		tmp += str;
		tmp += "\r\n\r\n";
		tmp += (src + ' ');
		//tmp += ' ';
		tmp += dst;
		const char* message = tmp.c_str();

		if (send(socket_desc, message, strlen(message), 0) < 0)
		{
			perror("send error");
			exit(-1);
		}

	}





        void handle_mactable()
	{
		bool print = false;
		size_t n = content.size();
		for(size_t i = 0; i < n; ++i)
		{
			if(content[i] == '\r' )
			{
				++i;
				continue;
			}
			if(content[i] == ',' || content[i] == '}' ) 
			{
				print = false;
				cout << endl;
			}
			if(content[i] == '"') print = true;
			if(print) cout << content[i];
			
		}
		content.clear();	
	}



        void handle_flowtable()
	{
		bool print = false;
		size_t n = content.size();
		for(size_t i = 0; i < n; ++i)
		{
			if(content[i] == '\r' )
			{
				++i;
				continue;
			}
			
			if(content[i] == '"') 
			{
				print ^= true;
				if(!print) cout << endl << "-----------------------------------" << endl;
				else ++i;
			}
			if(print) 
			{
				if(content[i] == '=' && content[i + 1] == 'O')
				{
					cout << ":" << endl << "     ";
					while(content[++i] != char(39))
					{
						if(content[i] == ')') goto match_out;
					}
                                        while(content[i] != ',') cout << content[i++];
					cout << endl << "    ";
                                        ++i;
					while(content[i] != '}') cout << content[i++];
					i += 2;
					match_out:
					cout << endl;
					while(content[i] != '=') ++i;
				}
				
				if(content[i] == '=' && content[i + 1] == '[')
				{
					cout << "action:" << endl << "      ";
					size_t count = 0;
					while(content[i] != 'p' || content[i + 1] != 'o') 
					{
						++i;
						if(content[i] == ']') 
						{
							if(count) goto out_action;
							++count;
						}
					}
					cout << "output";
					while(content[i] != ',') cout << content[i++];
					while(content[i++] != ']');
					while(content[i++] != ']');
					
				}
				out_action :
				if(content[i] == ' ') cout << endl;
				else cout << content[i];
			}
			
		}
		content.clear();	
	}

	void handle_traffic()
	{
		cout << content << endl;
		content.clear();
	}

	






	void receive()
	{ 
		struct timeval timeout = { 1, 0 };
		setsockopt(socket_desc, SOL_SOCKET, SO_RCVTIMEO, (char *)&timeout, sizeof(struct timeval));
		int size_recv, total_size = 0;
		char chunk[3072];
		while (1)
		{
			
			memset(chunk, 0, 3072);
			if ((size_recv = recv(socket_desc, chunk, 3072, 0)) == -1)
			{
				if (errno == EWOULDBLOCK || errno == EAGAIN)
				{
					//printf("recv timeout ...\n");
					break;
				}
				else if (errno == EINTR)
				{
					printf("interrupt by signal...\n");
					continue;
				}
				else if (errno == ENOENT)
				{
					printf("recv RST segement...\n");
					break;
				}
				else
				{
					printf("unknown error!\n");
					exit(1);
				}
			}
			else if (size_recv == 0)
			{
				
				printf("peer closed ...\n");
				break;
			}
			else
			{
				content += chunk;
				total_size += size_recv;
				//handle_switch_state();
			}
		}
		//cout<<content<<endl;//handle_flowtable();////
	}

	

	void close_socket()
	{
		close(socket_desc);
	}
	


private:
	int socket_desc;
	string content;
	
	struct sockaddr_in server;





};



int main(int argc, char *argv[])
{
	
	cout << "connect to SDN app"<< endl;
	while(true)
	{
		cout << "1) get mactable" << endl << "2) get flowtable" << endl << "3) traffic monitor" << endl << "4) modify flowtable"
				<< endl << "5) add firewall" << endl << "6) bandwidth chart" << endl << "7) exit" << endl << "==>";
		int choice;
		int child;
		string dpid;
		string dl_dst,in_port;
		string scr,dst;
		cin >> choice;
		HTTP http;
		http.connect_server();
		cout << endl << endl;
		switch(choice)
		{
			
			case 1:
				cout << "keyin the dpid whose mactable you want to look up: ";
				cin >> dpid;
				while (dpid.size() < 16) dpid = ('0' + dpid);
				http.get_mactable(dpid);
				http.receive();
				http.handle_mactable();
				http.close_socket();
				break;
			case 2:
				cout << "keyin the dpid whose flowtable you want to look up: ";
				cin >> dpid;
				while (dpid.size() < 16) dpid = ('0' + dpid);
				http.get_flowtable(dpid);
				http.receive();
				http.handle_flowtable();
				http.close_socket();
				break;
			case 3:
				http.get_traffic_info();
				http.receive();
				http.handle_traffic();
				http.close_socket();
				break;
			case 4:
				cout << "keyin the dpid which you want to modify: ";
				cin >> dpid;
				cout << "keyin the mac address which is the destination you want to remove: ";
				cin >> dl_dst;
				cout << "keyin the port number which you want to block: ";
				cin >> in_port;
				http.post_flow_modify(dpid,dl_dst,in_port);
				http.close_socket();
				break;
			case 5:
				cout << "keyin the source mac address: ";
				cin >> scr;
				cout << "keyin the destination mac address: ";
				cin >> dst;
				http.post_firewall(scr,dst);
				http.receive();
				http.close_socket();
				break;
			case 6:
				if((child = vfork()) < 0) perror("fork error: ");
				else if (child == 0)
				{
					system("chromium-browser --disable-web-security --user-data-dir --app=\"http://127.0.0.1:8081\"");
					exit(0);
				}
				http.receive();
				http.close_socket();
				break;
			case 7:
				return 0;
			default:
				cout << "no such option" << endl;
				http.close_socket();
			
		}

	}




	//http.get_traffic_info();
	//http.get_flowtable("0000000000000001");
	//http.post_flow_modify("0000000000000001","00:00:00:00:00:02","2");
	//http.receive();
	//http.handle_flowtable();
	//http.post_firewall("00:00:00:00:00:04","00:00:00:00:00:08");
	//system("chromium-browser --disable-web-security --user-data-dir --app=\"http://127.0.0.1:8081\" &");
	
}
