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
startStream();
