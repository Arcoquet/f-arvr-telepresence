# arvr-server

## Useful links:

- [Git: arvr-server](https://gitlab.emi.u-bordeaux.fr/rmellet/arvr-server)
- [Git: arvr-client-unity](https://gitlab.emi.u-bordeaux.fr/rmellet/arvr-client-unity)
- [Demo video](https://gitlab.emi.u-bordeaux.fr/rmellet/arvr-client-unity/-/blob/main/Vidéo_démo.mp4)

## Ubuntu python server (tested on 22.04)

### Install libfreenect2

```shell
sudo apt install build-essential cmake pkg-config libusb-1.0-0-dev libturbojpeg0-dev libglfw3-dev
#install opencl depending of you graphics vendor eg: sudo apt install nvidia-opencl-dev
sudo cp ../platform/linux/udev/90-kinect2.rules /etc/udev/rules.d/ # and replug the kinect. to add access to the device without sudo
git clone https://github.com/OpenKinect/libfreenect2.git
cd libfreenect2
mkdir build && cd build
cmake ..
make
./bin/Protonect # must display a RGB-D feed
sudo make install
```

### Python libs

```shell
#pip install -r requirements.txt
#mamba env create -n arvr --file environment.yml

python server.py
```

## Demo JS client

```shell
cd webdemo
npm install
npm run dev
```

## Limitations

### SSL - WebXR

To run on MQ3 (immersive), the vite server must run in SSL (valid or invalid), so the python server also.
But the python cannot have easily a valid SSL certificate, which is required by the browser.
So to check on MQ3 either:

- run vite in http and python in http and check in non-immersive mode
- run vite in https with the `<source src="rgbdhue_combined.webm" />` static video and no python server

## Kinect troubleshooting

### libfreenect2 so missing

```shell
sudo ldconfig
ldconfig -p | grep libfreenect2
```

### install libfreenect2 from source

I had some numpy error though not related with numpy, so I installed from source

```shell
git clone https://github.com/r9y9/pylibfreenect2.git
cd pylibfreenect2
pip install Cython
python setup.py install
```
