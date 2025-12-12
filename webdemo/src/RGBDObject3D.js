import * as THREE from "three"


// language=GLSL
const vert = `
    uniform sampler2D map;

    uniform float width;
    uniform float height;
    uniform vec2 wh;
    uniform float nearClipping, farClipping;
    uniform float pointSize;

    uniform bool IS_DEPTH_HUE;     // RGBD mode
    uniform bool IS_MONODEPTH;     // MonoDepth mode

    varying vec2 vUv;

    const float PI = 3.141592653589793;
    const float FOV_HORIZONTAL_DEG = 84.1; // kinect v2 FOV
    const float INVALID_DEPTH = -2.0;

    float getNormalizedDepth(vec2 depthvUv) {
        vec4 color = texture2D(map, depthvUv);

        float depth;

        if(IS_MONODEPTH) {
            // Mode mono : on prend la depth map directement en grayscale
            depth = (color.r + color.g + color.b) / 3.0;
            if(depth < 0.01) return INVALID_DEPTH; // ignore si profondeur nulle
        }
        else if(IS_DEPTH_HUE) {
            // RGBD classique
            // garde tout ton code existant avec rgb2hsv
            const float _Epsilon = 1.0e-10;
            vec4 K = vec4(0.0, -1.0/3.0, 2.0/3.0, -1.0);
            vec4 p = mix(vec4(color.b, color.g, K.wz), vec4(color.g, color.b, K.xy), step(color.b, color.g));
            vec4 q = mix(vec4(p.xyw, color.r), vec4(color.r, p.yzx), step(p.x, color.r));
            float d = q.x - min(q.w, q.y);
            vec3 hsv = vec3(abs(q.z + (q.w - q.y)/(6.0*d+_Epsilon)), d/(q.x+_Epsilon), q.x);

            if(hsv.z < 0.8) return INVALID_DEPTH;
            depth = hsv.x;
        }
        else {
            // fallback : simple grayscale
            depth = (color.r + color.g + color.b) / 3.0;
            if(depth >= 0.996) return INVALID_DEPTH;
        }

        return depth;
    }

    void main() {
        vec2 depthvUv = position.xy / wh * vec2(1.0, 0.5); // depthvUv is lower video part
        vUv = depthvUv + vec2(0.0, 0.5); // colorvUv is upper video part

        float depth = getNormalizedDepth(depthvUv);
        if(depth == INVALID_DEPTH) return;

        float z = (depth * (farClipping - nearClipping) + nearClipping) / 1000.0; // z in meters

        float fovRad = FOV_HORIZONTAL_DEG * (PI / 180.0);
        float f = wh.x / (2.0 * tan(fovRad / 2.0));

        vec4 pos = vec4(
            (position.xy - wh * 0.5) * z / f,
            -z,
            1.0
        );

        gl_PointSize = pointSize;
        gl_Position = projectionMatrix * modelViewMatrix * pos;
    }
`


// language=GLSL
const frag = `
    uniform sampler2D map;
    varying vec2 vUv;
    void main() {
        vec4 color = texture2D(map, vUv);
        gl_FragColor = vec4(color.r, color.g, color.b, 1.0);
    }
`

export class RGBDObject3D extends THREE.Object3D {
    //size of the grid (number of vertices eq width * height) - could be different from color/depth jpg/video/stream resolution
    width = 1920/2 // matching the number of depth pixel we want to have in our render
    height = 1080/2
    nearClipping = 500
    farClipping = 1500

    constructor(video, mode = "rgbd") {
        super()
        this.mode = mode;
        const texture = new THREE.VideoTexture(video)
        texture.minFilter = THREE.NearestFilter
        texture.generateMipmaps = false
        const points = new THREE.Points(this.createGeo(), this.createMat(texture))
        points.frustumCulled = false
        this.add(points)

        const rgbdCameraHelper = new THREE.PerspectiveCamera(75, this.width / this.height) //dumb fov
        const cameraHelper = new THREE.CameraHelper(rgbdCameraHelper)
        this.add(cameraHelper)
    }

    createGeo() {
        let geometry = new THREE.BufferGeometry()
        const vertices = new Float32Array(this.width * this.height * 3)
        for (let i = 0, j = 0, l = vertices.length; i < l; i += 3, j++) {
            vertices[i] = j % this.width
            vertices[i + 1] = Math.floor(j / this.width)
        }
        geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3))
        return geometry
    }

    createMat(texture) {
        return new THREE.ShaderMaterial({
            uniforms: {
                'map': { value: texture },
                'wh': { value: new THREE.Vector2(this.width, this.height) },
                'nearClipping': { value: this.nearClipping },
                'farClipping': { value: this.farClipping },
                'pointSize': { value: 2 },
                'IS_DEPTH_HUE': { value: this.mode === "rgbd" },
                'IS_MONODEPTH': { value: this.mode === "mono" }
            },
            vertexShader: vert,
            fragmentShader: frag
        })
    }


    setMode(mode) {
        this.mode = mode
        this.children[0].material.uniforms.IS_DEPTH_HUE.value = mode === "rgbd"
        this.children[0].material.uniforms.IS_MONODEPTH.value = mode === "mono"
    }
}
