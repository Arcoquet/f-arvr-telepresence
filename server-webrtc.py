import asyncio
import cv2
from aiohttp import web
import aiohttp_cors
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from av import VideoFrame

# Why WebRTC over WebSocket? WebRTC uses UDP and video compression (H.264 or VP8)


class WebcamStreamTrack(VideoStreamTrack):
    def __init__(self):
        super().__init__()
        # Open the first available webcam
        self.cap = cv2.VideoCapture(0)

    async def recv(self):
        pts, time_base = await self.next_timestamp()
        ret, frame = self.cap.read()
        if not ret:
            raise Exception("Could not read frame from webcam")

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        video_frame = VideoFrame.from_ndarray(frame, format="rgb24")
        video_frame.pts = pts
        video_frame.time_base = time_base
        return video_frame

    def stop(self):
        if self.cap.isOpened():
            self.cap.release()


async def offer(request):
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        print(f"Connection state is {pc.connectionState}")
        if pc.connectionState == "failed" or pc.connectionState == "closed":
            await pc.close()
            pcs.discard(pc)

    video_track = WebcamStreamTrack()
    pc.addTrack(video_track)
    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    return web.json_response({
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type
    })

pcs = set()


async def on_shutdown(app):
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()


if __name__ == "__main__":
    app = web.Application()

    # CORS needed by the js client
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })

    resource = cors.add(app.router.add_resource("/offer"))
    cors.add(resource.add_route("POST", offer))
    app.on_shutdown.append(on_shutdown)
    print("Server started at http://localhost:8080")
    web.run_app(app, host="0.0.0.0", port=8080)