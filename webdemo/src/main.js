import { GUI } from 'three/addons/libs/lil-gui.module.min.js'
import { RGBDObject3D } from "./RGBDObject3D.js"
import { angles2euler } from "./utils.js"
import WebGlApp from "./WebGlApp.js"
import { WebRTCClient } from "./WebRTCClient.js";

let elVideo = document.getElementById('video')

let wegGlApp = new WebGlApp(document.querySelector('#threejs-container'))
const rgbdObject3D = new RGBDObject3D(elVideo)
rgbdObject3D.rotation.copy(angles2euler(0, 0, 90))
wegGlApp.scene.add(rgbdObject3D)

elVideo.play()

const gui = new GUI()
const maxRot = Math.PI
// gui.add( material.uniforms.nearClipping, 'value', 1, 10000, 1.0 ).name( 'nearClipping' )
// gui.add( material.uniforms.farClipping, 'value', 1, 10000, 1.0 ).name( 'farClipping' )
// gui.add( material.uniforms.pointSize, 'value', 1, 10, 1.0 ).name( 'pointSize' )
// gui.add( material.uniforms.zOffset, 'value', 0, 4000, 1.0 ).name( 'zOffset' )
gui.add(rgbdObject3D.rotation, 'x', -maxRot, maxRot, 0.01).name('Rotate X')
gui.add(rgbdObject3D.rotation, 'y', -maxRot, maxRot, 0.01).name('Rotate Y')
gui.add(rgbdObject3D.rotation, 'x', -maxRot, maxRot, 0.01).name('Rotate Z')

const elStartBtn = document.getElementById("startBtn")
let client = new WebRTCClient(elVideo)
const host = document.getElementById('host').value
elStartBtn.addEventListener("click", () => {
    elStartBtn.disabled = true;
    elStartBtn.innerText = "Connecting..."
    client.startStream(host)
        .then(_=> elStartBtn.innerText = "Connected")
        .catch(error => {
            elStartBtn.innerText = "Error (see console)"
            console.error(error)
        })
});

// Automatically start when the page loads
// elStartBtn.click()
