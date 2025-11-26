import * as THREE from 'three';
import { OrbitControls } from "three/addons";

import { GUI } from 'three/addons/libs/lil-gui.module.min.js';
import { RGBDObject3D } from "./RGBDObject3D.js";
import { angles2euler } from "./utils.js";

const canvas = document.querySelector('#threejs-container');
const renderer = new THREE.WebGLRenderer({canvas});
const w = 500, h = 500


let scene, camera;
let controls;


init();

function init() {
    camera = new THREE.PerspectiveCamera(50, w / h, 1, 10000);
    camera.position.set(0, 0, 500);

    scene = new THREE.Scene();
    const video = document.getElementById('video')

    const axesHelper = new THREE.AxesHelper(5);
    scene.add(axesHelper);

    const rgbdObject3D = new RGBDObject3D(video)
    rgbdObject3D.rotation.copy(angles2euler(0, 0, 90))
    scene.add(rgbdObject3D);

    const gui = new GUI();
    const maxRot = Math.PI;
    // gui.add( material.uniforms.nearClipping, 'value', 1, 10000, 1.0 ).name( 'nearClipping' );
    // gui.add( material.uniforms.farClipping, 'value', 1, 10000, 1.0 ).name( 'farClipping' );
    // gui.add( material.uniforms.pointSize, 'value', 1, 10, 1.0 ).name( 'pointSize' );
    // gui.add( material.uniforms.zOffset, 'value', 0, 4000, 1.0 ).name( 'zOffset' );
    gui.add(rgbdObject3D.rotation, 'x', -maxRot, maxRot, 0.01).name('Rotate X');
    gui.add(rgbdObject3D.rotation, 'y', -maxRot, maxRot, 0.01).name('Rotate Y');
    gui.add(rgbdObject3D.rotation, 'x', -maxRot, maxRot, 0.01).name('Rotate Z');

    video.play();
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(w, h);
    renderer.setAnimationLoop(animate);
    window.addEventListener('resize', onWindowResize);

    controls = new OrbitControls(camera, renderer.domElement);
}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

function animate() {
    controls.update();
    renderer.render(scene, camera);
}

const config = {
    // iceServers: [{ urls: "stun:stun.l.google.com:19302" }], STUN server needed?
};

const pc = new RTCPeerConnection(config);

async function startStream() {
    console.log("Starting connection...");

    pc.addTransceiver("video", {direction: "recvonly"}); // watching only

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
