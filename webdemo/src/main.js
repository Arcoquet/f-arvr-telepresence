import * as THREE from 'three';


const canvas = document.querySelector('#threejs-container');
console.log(canvas.innerWidth);

const w = 500, h=500

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera( 75, w / h, 0.1, 1000 );

const renderer = new THREE.WebGLRenderer({canvas});
renderer.setSize( w, h );
renderer.setAnimationLoop( animate );

const geometry = new THREE.BoxGeometry( 1, 1, 1 );
const material = new THREE.MeshBasicMaterial( { color: 0x00ff00 } );
const cube = new THREE.Mesh( geometry, material );
scene.add( cube );

camera.position.z = 5;

function animate() {
    cube.rotation.x += 0.01;
    cube.rotation.y += 0.01;
    renderer.render( scene, camera );
}

const config = {
    // iceServers: [{ urls: "stun:stun.l.google.com:19302" }], STUN server needed?
};

const pc = new RTCPeerConnection(config);

async function startStream() {
    console.log("Starting connection...");

    pc.addTransceiver("video", { direction: "recvonly" }); // watching only

    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);

    // Send the offer to the Python server
    const response = await fetch("http://localhost:8080/offer", {
        method: "POST",
        body: JSON.stringify({sdp: pc.localDescription.sdp, type: pc.localDescription.type,}),
        headers: {"Content-Type": "application/json",},
    });

    const answer = await response.json();
    console.log(answer)

    await pc.setRemoteDescription(answer);
}

pc.ontrack = (event) => {
    console.log("Track received:", event.streams);
    const videoElement = document.getElementById("video");
    videoElement.srcObject = event.streams[0];
    videoElement.muted = true; //Browsers block autoplay with sound.
    videoElement.play().catch(e => console.error("Autoplay failed:", e));
};

// document.getElementById("startBtn").addEventListener("click", () => {
//     startStream().catch(console.error);
//     document.getElementById("startBtn").disabled = true;
//     document.getElementById("startBtn").innerText = "Connecting...";
// });

// Automatically start when the page loads
// startStream();
