import * as THREE from 'three';

import { GUI } from 'three/addons/libs/lil-gui.module.min.js';

const canvas = document.querySelector('#threejs-container');
const renderer = new THREE.WebGLRenderer({canvas});
const w = 500, h = 500


let scene, camera;
let geometry, mesh, material;
let mouse, center;

init();

function init() {

    const container = document.createElement( 'div' );
    document.body.appendChild( container );

    const info = document.createElement( 'div' );
    document.body.appendChild( info );

    camera = new THREE.PerspectiveCamera( 50, window.innerWidth / window.innerHeight, 1, 10000 );
    camera.position.set( 0, 0, 500 );

    scene = new THREE.Scene();
    center = new THREE.Vector3();
    center.z = - 1000;

    const video = document.getElementById( 'video' );

    const texture = new THREE.VideoTexture( video );
    texture.minFilter = THREE.NearestFilter;
    texture.generateMipmaps = false;
    const width = 640, height = 480;
    const nearClipping = 850, farClipping = 4000;
    geometry = new THREE.BufferGeometry();
    const vertices = new Float32Array( width * height * 3 );

    for ( let i = 0, j = 0, l = vertices.length; i < l; i += 3, j ++ ) {
        vertices[ i ] = j % width;
        vertices[ i + 1 ] = Math.floor( j / width );
    }

    geometry.setAttribute( 'position', new THREE.BufferAttribute( vertices, 3 ) );
    material = new THREE.ShaderMaterial( {

        uniforms: {
            'map': { value: texture },
            'width': { value: width },
            'height': { value: height },
            'nearClipping': { value: nearClipping },
            'farClipping': { value: farClipping },
            'pointSize': { value: 2 },
            'zOffset': { value: 1000 }
        },
        vertexShader: document.getElementById( 'vs' ).textContent,
        fragmentShader: document.getElementById( 'fs' ).textContent,
        blending: THREE.AdditiveBlending,
        depthTest: false,
        depthWrite: false,
        transparent: true
    } );

    mesh = new THREE.Points( geometry, material );
    scene.add( mesh );

    const gui = new GUI();
    gui.add( material.uniforms.nearClipping, 'value', 1, 10000, 1.0 ).name( 'nearClipping' );
    gui.add( material.uniforms.farClipping, 'value', 1, 10000, 1.0 ).name( 'farClipping' );
    gui.add( material.uniforms.pointSize, 'value', 1, 10, 1.0 ).name( 'pointSize' );
    gui.add( material.uniforms.zOffset, 'value', 0, 4000, 1.0 ).name( 'zOffset' );
    video.play();
    renderer.setPixelRatio( window.devicePixelRatio );
    renderer.setSize(w, h);
    renderer.setAnimationLoop( animate );
    mouse = new THREE.Vector3( 0, 0, 1 );
    document.addEventListener( 'mousemove', onDocumentMouseMove );
    window.addEventListener( 'resize', onWindowResize );
}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize( window.innerWidth, window.innerHeight );
}

function onDocumentMouseMove( event ) {
    mouse.x = ( event.clientX - window.innerWidth / 2 ) * 8;
    mouse.y = ( event.clientY - window.innerHeight / 2 ) * 8;
}

function animate() {
    camera.position.x += ( mouse.x - camera.position.x ) * 0.05;
    camera.position.y += ( - mouse.y - camera.position.y ) * 0.05;
    camera.lookAt( center );
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
