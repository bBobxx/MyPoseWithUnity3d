using UnityEngine;
using System.Collections;

public class move : MonoBehaviour {
	private bool isMove=false;
	public int speed = 5;
	// Use this for initialization
	void Start () {
	
	}
	
	// Update is called once per frame
	void Update () {
		if(isMove) {
			transform.Translate(Vector3.left * speed * Time.deltaTime, Space.World);
			isMove=false;
		}
	}
	void OnCollisionEnter(Collision collision) {
         isMove = true;
    }
}
