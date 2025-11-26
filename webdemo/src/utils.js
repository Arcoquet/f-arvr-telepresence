import * as THREE from "three";
import { DEG2RAD } from "three/src/math/MathUtils.js";

export function angles2euler(x, y, z) {
    return new THREE.Euler(x * DEG2RAD, y * DEG2RAD, z * DEG2RAD)
}
