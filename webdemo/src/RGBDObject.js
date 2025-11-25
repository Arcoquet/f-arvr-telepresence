import * as THREE from "three";

// language=GLSL
const vert = `
    uniform sampler2D map;

    uniform float width;
    uniform float height;
    uniform float nearClipping, farClipping;

    uniform float pointSize;
    uniform float zOffset;

    varying vec2 vUv;

    const float XtoZ = 1.11146; // tan( 1.0144686 / 2.0 ) * 2.0;
    const float YtoZ = 0.83359; // tan( 0.7898090 / 2.0 ) * 2.0;

    void main() {
        vUv = vec2( position.x / width, position.y / height );
        vec4 color = texture2D( map, vUv );
        float depth = ( color.r + color.g + color.b ) / 3.0;

        float z = ( 1.0 - depth ) * (farClipping - nearClipping) + nearClipping;

        vec4 pos = vec4(
            ( position.x / width - 0.5 ) * z * XtoZ,
            ( position.y / height - 0.5 ) * z * YtoZ,
            - z + zOffset,
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
        vec4 color = texture2D( map, vUv );
        gl_FragColor = vec4( color.r, color.g, color.b, 0.2 );
    }
    
    
`

export class RGBDObject {
    width = 640 // matching the number of depth pixel we want to have in our render
    height = 480;
    nearClipping = 850
    farClipping = 4000
    create3DObject(video) {
        const texture = new THREE.VideoTexture( video );
        texture.minFilter = THREE.NearestFilter;
        texture.generateMipmaps = false;
        return new THREE.Points( this.createGeo(), this.createMat(texture) );
    }

    createGeo() {
        let geometry = new THREE.BufferGeometry();
        const vertices = new Float32Array( this.width * this.height * 3 );
        for ( let i = 0, j = 0, l = vertices.length; i < l; i += 3, j ++ ) {
            vertices[ i ] = j % this.width;
            vertices[ i + 1 ] = Math.floor( j / this.width );
        }
        geometry.setAttribute( 'position', new THREE.BufferAttribute( vertices, 3 ) );
        return geometry
    }
    createMat(texture) {
        return new THREE.ShaderMaterial( {

            uniforms: {
                'map': { value: texture },
                'width': { value: this.width },
                'height': { value: this.height },
                'nearClipping': { value: this.nearClipping },
                'farClipping': { value: this.farClipping },
                'pointSize': { value: 2 },
                'zOffset': { value: 1000 }
            },
            vertexShader: vert,
            fragmentShader: frag,
            blending: THREE.AdditiveBlending,
            depthTest: false,
            depthWrite: false,
            transparent: true
        } );
    }
}
