# webcam server

a really simple webcam server that is kind of bad, but somehow still has more features than mjpeg-streamer.

## Usage

```bash
# install dependencies
pip install -r requirements.txt

# start the server
python3 server.py
```

### Options

| Short | Long                | Description                                                                     |
| ----- | ------------------- | ------------------------------------------------------------------------------- |
| `-p`  | `--port`            | Specify the port number for the server. Default is 8080.                        |
| `-d`  | `--device`          | Specify the device number as an index for CV2.VideoCapture. Default is 0.       |
| `-fh` | `--flip_horizontal` | Flip the captured video horizontally. Default is False.                         |
| `-fv` | `--flip_vertical`   | Flip the captured video vertically. Default is False.                           |
| `-r`  | `--rotate`          | Rotate the captured image. Supports angles: 0, 90, 180, 270, -90. Default is 0. |
