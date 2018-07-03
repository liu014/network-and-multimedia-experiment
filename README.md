# network-and-multimedia-experiment
The only purpose I open this repository is for the course demand. My python and javascript code don't have any reference value(I'd never learned that)

所有關於此project的操作皆運行於Linux 64bit(Ubuntu 14.04LTS)


此project需安裝的軟體至少為gcc編譯器、g++編譯器、python 2.7、mininet、ryu、node.js 10.5.0(then you need to install socket.io，建議利用npm、nvm)、
chromium-browser、ostinato


確認ryu的安裝完成後，Home directory會出現ryu directory，請將simple_switch_13.py、simple_switch_rest_13.py放置於絕對路徑/home/mininet/ryu/ryu/app之下，並以terminal在該位置輸入ryu-manager simple_switch_13.py產生新的.pyc檔


將sdn_app.cpp放置任意合理位置，並以terminal在該位置輸入g++ -o app sdn_app.cpp編譯產生app執行檔


將flowchart_server資料夾放置於合適位置，並確認將socket.io下載至該位置(node_modules資料夾產生於flowchart_server資料夾內)


首先以terminal到flowchart_server資料夾的位置，輸入node chart_server.js開啟伺服器。再以terminal到/home/mininet/ryu/ryu/app，輸入ryu-manager simple_switch_rest_13.py開啟伺服器。再開啟另一terminal輸入sudo mn --topo=tree,3 --switch=ovs,protocols=OpenFlow13 --mac --controller=remote開啟mininet網路。再以sdn_app.cpp所在位置，輸入./app執行應用程式。


應用程式的測試方法，應先測試add firewall功能(輸入5後，輸入00:00:00:00:00:04，再輸入00:00:00:00:00:08，到mininet的終端pingall測試)。
再來測試get mactable(輸入1後，輸入1)、測試get flowtable(輸入1後，輸入1)、測試traffic monitor(輸入3)
接著測試bandwidth chart(輸入6(也可利用瀏覽器輸入127.0.0.1:8081)，再到mininet終端輸入xterm h1，到新終端輸入sudo ostinato &，開啟ostinato後點開port Group，再點展開的第一個選項，可輸入測試檔test.pcap，將avg pps改成50000，點選apply，再點Port 0-0，接著發送封包，觀察瀏覽器的資訊)
關閉瀏覽器後，再測試modify flowtable(輸入5，再輸入00:00:00:00:00:02，再輸入2，到mininet終端利用pingall測試)
