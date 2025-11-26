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

pip install -r requirements.txt
#mamba env create -n arvr --file environment.yml
```




## Demo JS client

```shell
cd webdemo
npm install
npm run dev
```
