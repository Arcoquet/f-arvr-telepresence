export class WebRTCClient {
    config = {
        // iceServers: [{ urls: "stun:stun.l.google.com:19302" }], STUN server needed?
    }

    elVideo = null

    constructor(elVideo, serverUrl) {
        this.elVideo = elVideo
        this.pc = new RTCPeerConnection(this.config)
        this.pc.ontrack = (event) => {
            console.log("Track received:", event.streams)
            this.elVideo.srcObject = event.streams[0]
            this.elVideo.play().catch(e => console.error("Autoplay failed:", e))
        };
    }

    async startStream(host, isHttps = false) {
        console.log("Starting connection...")

        this.pc.addTransceiver("video", {direction: "recvonly"}) // watching only

        const offer = await this.pc.createOffer()
        await this.pc.setLocalDescription(offer)

        // Send the offer to the Python server
        const protocol = isHttps ? 'https' : 'http'
        const response = await fetch(`${protocol}://${host}:8080/offer`, {
            method: "POST",
            body: JSON.stringify({
                sdp: this.pc.localDescription.sdp,
                type: this.pc.localDescription.type,
            }),
            headers: {"Content-Type": "application/json",},
        })

        const answer = await response.json()
        console.log(answer)

        await this.pc.setRemoteDescription(answer)
    }
}
