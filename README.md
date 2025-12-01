# arvr-server

## Ubuntu
```shell
git clone https://github.com/OpenKinect/libfreenect2.git
cd libfreenect2
mkdir build
cd build
cmake ..
make
./bin/Protonect #must display a RGB-D feed
sudo make install

python server.py

pip install -r requirements.txt
#mamba env create -n arvr --file environment.yml
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
