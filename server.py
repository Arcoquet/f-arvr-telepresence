import asyncio

import aiohttp_cors
from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription
import ssl

from DumbVideoStreamTrack import DumbStaticRGBD, DumbWebcamStreamTrack
from Kinect2StreamTrack import Kinect2StreamTrack
from utils import get_local_ip

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

    # video_track = DumbStaticRGBD(near, far) #send static color and depth pngs
    # video_track = DumbWebcamStreamTrack() #send color webcam
    video_track = Kinect2StreamTrack(near, far)

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

    near, far = 500, 1500  # in mm # will keep only range 0.5m-1.5m
    use_ssl = False #must be a valid ssl certificate :'( otherwise the fetch js call fail

    local_ip = get_local_ip()
    print(f"Local ip={local_ip}")

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

    ssl_context = None
    if use_ssl:
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain(certfile='./tmp_ssl/cert.pem', keyfile='./tmp_ssl/key.pem')
    web.run_app(app, host="0.0.0.0", port=8080, ssl_context=ssl_context)