using UnityEngine;
using System;
using System.Collections;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;

public class PlayerControllerScript: MonoBehaviour
{
	// 1. Declare Variables
	Thread receiveThread; //1
	UdpClient client; //2
	int port; //3
	int[] coord = new int[32];
	public GameObject sphere; //4
	bool updateCoord = false;
	// 2. Initialize variables
	void Start () 
	{
		port = 5065; //1 
		sphere = GameObject.Find("Sphere");
		InitUDP(); //4
	}

	// 3. InitUDP
	private void InitUDP()
	{
		print ("UDP Initialized");

		receiveThread = new Thread (new ThreadStart(ReceiveData)); //1 
		receiveThread.IsBackground = true; //2
		receiveThread.Start (); //3

	}

	// 4. Receive Data
	private void ReceiveData()
	{
		client = new UdpClient (port); //1
		while (true) //2
		{
			try
			{
				IPEndPoint anyIP = new IPEndPoint(IPAddress.Parse("0.0.0.0"), port); //3
				byte[] data = client.Receive(ref anyIP); //4

				string text = Encoding.UTF8.GetString(data); //5
				string[] strArray = text.Split(',');
				int[] coord1 = new int[32];
				for (int i = 1; i<strArray.Length-1;++i) {
					int x = Int32.Parse(strArray[i]);
					coord1[i-1] = x;
					// print("<<"+x);
				}
				if (updateCoord) {
					coord = coord1;
					updateCoord = false;
				}



			} catch(Exception e)
			{
				print (e.ToString()); //7
			}
		}
	}



	// 6. Check for variable value, and make the Player Jump!
	void Update () 
	{
		if (!updateCoord){
			for (int i=0; i<16;i++) {
				string obj = "Sphere (" + Convert.ToString(i+1)+")";
				// print(obj);
				// print(coord[2*i]/10);
				// print(coord[2*i+1]/10);
				GameObject spherei = sphere.transform.Find(obj).gameObject;
				if (coord[2*i] >0 && coord[2*i+1]>0) {	
					int x = coord[2*i]-320;
					int y = coord[2*i+1]-240;
					spherei.transform.position = new Vector3(x, y, 0.0f);
				}
				else
					spherei.transform.position = new Vector3(-1000.0f, -1000.0f, 0.0f);

				updateCoord = true;
			}
		}

		
	}
}
