import * as THREE from "three";

// language=GLSL
const vert = `
    uniform sampler2D map;

    uniform float width;
    uniform float height;
    uniform vec2 wh;
    uniform float nearClipping, farClipping;
    uniform float pointSize;

    varying vec2 vUv;

    const float PI = 3.141592653589793;
    const float FOV_HORIZONTAL_DEG = 84.1;//kinect v2 FOV
    const float FOV_VERTICAL_DEG = 53.8;//kinect v2 FOV
    
    const float FOV_HORIZONTAL_RAD = FOV_HORIZONTAL_DEG * PI / 180.0;
    const float FOV_VERTICAL_RAD = FOV_VERTICAL_DEG * PI / 180.0;
    
    const float XtoZ = tan(FOV_HORIZONTAL_RAD / 2.0) * 2.0;
    const float YtoZ = tan(FOV_VERTICAL_RAD / 2.0) * 2.0; //float YtoZ = XtoZ * (height / width);
    const vec2 XYtoZ = vec2(XtoZ, YtoZ); //coud use ratio instead below 

    vec3 rgb2hsv(vec3 c) { // return [0-1, 0-1, 0-1]
        const float _Epsilon = 1.0e-10;
        vec4 K = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
        vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
        vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));
        float d = q.x - min(q.w, q.y);
        return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + _Epsilon)), d / (q.x + _Epsilon), q.x);
    }

    float getNormalizedDepth(vec2 depthvUv) {
        vec4 color = texture2D(map, depthvUv);
        //depth is grayscale
        float depth = (color.r + color.g + color.b) / 3.0;
        return depth;//[0-1]
    }

    void main() {
        vec2 depthvUv = position.xy / wh * vec2(1.0, 0.5);//depthvUv is lower video part
        vUv = depthvUv + vec2(0.0, 0.5);//colorvUv is upper video part

        float depth = getNormalizedDepth(depthvUv);
        if (depth > 0.99) return;

        float z = depth * (farClipping - nearClipping) + nearClipping; // in mm

        float fovRad = FOV_HORIZONTAL_DEG * (PI / 180.0);
        float f = wh.x / (2.0 * tan(fovRad / 2.0));

        vec4 pos = vec4(
        (position.xy - wh * 0.5) * z / f,
//        ( position.xy / wh - 0.5 ) * z * XYtoZ, //is that similar than above formula?
        - z,
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
    height = 1080/2;
    nearClipping = 500
    farClipping = 1500

    constructor(video) {
        super()
        const texture = new THREE.VideoTexture(video);
        texture.minFilter = THREE.NearestFilter;
        texture.generateMipmaps = false;
        return new THREE.Points(this.createGeo(), this.createMat(texture));
    }

    createGeo() {
        let geometry = new THREE.BufferGeometry();
        const vertices = new Float32Array(this.width * this.height * 3);
        for (let i = 0, j = 0, l = vertices.length; i < l; i += 3, j++) {
            vertices[i] = j % this.width;
            vertices[i + 1] = Math.floor(j / this.width);
        }
        geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));
        return geometry
    }

    createMat(texture) {
        return new THREE.ShaderMaterial({
            uniforms: {
                'map': {value: texture},
                'wh': {value: new THREE.Vector2(this.width, this.height)},
                'nearClipping': {value: this.nearClipping},
                'farClipping': {value: this.farClipping},
                'pointSize': {value: 2}
            },
            vertexShader: vert,
            fragmentShader: frag
        });
    }
}
