# IPProjectChatRoom

##### **CSC573 - SPRING20 - CHAT ROOM COMMUNICATION WITH ENCRYPTION**

<br>

**Command to run server and client:<br>
python3 server.py IPAddress Port Password<br>
python3 client.py IPAddress Port Password<br>**
<br>

**Client Commands**
<ol>
<li>To get users currently connected<br>
    cmd: getusers</li>
<li>To send a message/file to all users.(Broadcast)<br>
    cmd(msg) : mbroadcast|Enter Your Message<br>
    cmd(file): fbroadcast|Filename</li>
<li>To send a message/file to single user.(Unicast) <br>
    cmd(msg) : municast|user|Enter Your Message<br>
    cmd(file): funicast|user|Filename</li>
<li>To send a message/file to multiple users.(Multicast)<br>
    cmd(msg) : mmulticast|user1|user2|user3|Enter Your Message<br>
    cmd(file): fmulticast|user1|user2|user3|Filename</li>
<li>To send a message/file to all users except one.(Blockcast)<br>
    cmd(msg) : mblockcast|user1|user2|Enter Your Message<br>
    cmd(file): fblockcast|user1|user2|Filename</li>
<li>To kick a user out of the chatroom(Need atleast 2 votes).<br>
    cmd: kick|user</li>
</ol>

**Team :**<br>
Abhishek Gadireddy<br>
Lakshmi Aishwarya Nellutla<br>
Lokesh Reddy Police<br>
Unith Mallavaram<br>
