import * as THREE from 'three'
import { OrbitControls, XRButton } from "three/addons"
import { VRButton } from 'three/addons/webxr/VRButton.js'

export default class WebGlApp {
    constructor(canvas) {
        this.canvas = canvas
        this.renderer = new THREE.WebGLRenderer({canvas})
        this.renderer.setPixelRatio(window.devicePixelRatio)
        this.renderer.setSize(this.width, this.height)
        this.renderer.setAnimationLoop(() => this.animate())
        window.addEventListener('resize', () => this.onWindowResize)

        this.camera = new THREE.PerspectiveCamera(75, this.width / this.height, 0.01, 1000)
        this.camera.position.set(0, 0, 0.1)

        this.scene = new THREE.Scene()

        // const axesHelper = new THREE.AxesHelper(1)
        // this.scene.add(axesHelper)

        this.controls = new OrbitControls(this.camera, this.renderer.domElement)

        document.body.appendChild(XRButton.createButton(this.renderer, {
            // requiredFeatures: ['hand-tracking']
        }))
        this.renderer.xr.enabled = true
        this.renderer.xr.setReferenceSpaceType('local')
    }

    onWindowResize() {
        this.camera.aspect = this.width / this.height
        this.camera.updateProjectionMatrix()
        this.renderer.setSize(this.width, this.height)
    }

    get width() {
        return this.canvas.clientWidth
    }

    get height() {
        return this.canvas.clientHeight
    }

    animate() {
        this.controls.update()
        this.renderer.render(this.scene, this.camera)
    }
}
