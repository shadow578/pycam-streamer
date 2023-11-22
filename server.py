from flask import Flask, Response
import cv2
import argparse
import time

def main():
    # parse cli args
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--listen",
                    help="Specify the address the server listens on. Default is 0.0.0.0",
                    type=str,
                    default="0.0.0.0")
    parser.add_argument('-p', '--port', 
                    help='Specify the port number for the server. Default is 8080.', 
                    type=int, 
                    default=8080)
    parser.add_argument('-d', '--device', 
                    help='Specify the device number as an index for CV2.VideoCapture. Default is 0.', 
                    type=int, 
                    default=0)
    parser.add_argument('-fh', '--flip_horizontal', 
                    help='Flip the captured video horizontally. Default is False.', 
                    type=bool,
                    default=False)
    parser.add_argument('-fv', '--flip_vertical', 
                    help='Flip the captured video vertically. Default is False.', 
                    type=bool,
                    default=False)
    parser.add_argument('-r', '--rotate', 
                    help='Rotate the captured image. Supports angles: 0, 90, 180, 270, -90. Default is 0.', 
                    type=int, 
                    default=0)
    parser.add_argument('-q', '--quality', 
                    help='JPEG quality for image encoding. Default is 90.', 
                    type=int, 
                    default=90)
    parser.add_argument('-fps', '--framerate', 
                    help='Target framerate for the server. 0 for unlimited. Default is 60.', 
                    type=int, 
                    default=60)
    parser.add_argument('-mf', '--manual_focus', 
                    help='manual focus value. use -1 for auto focus. Default is -1.', 
                    type=int, 
                    default=-1)
    args = parser.parse_args()

    # dump args
    print("starting server with the following args:")
    print(f"listen: {args.listen}")
    print(f'port: {args.port}')
    print(f'device: {args.device}')
    print(f'flip_horizontal: {args.flip_horizontal}')
    print(f'flip_vertical: {args.flip_vertical}')
    print(f'rotate: {args.rotate}')
    print(f'quality: {args.quality}')
    print(f'framerate: {args.framerate}'),
    print(f'manual_focus: {args.manual_focus}')

    ##
    ## Setup Flask + OpenCV
    ##

    app = Flask(__name__)

    camera = cv2.VideoCapture(args.device)
    if not camera.isOpened():
        raise RuntimeError('Error opening camera')

    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    if args.manual_focus >= 0:
        if camera.set(cv2.CAP_PROP_AUTOFOCUS, 0):
            if camera.set(cv2.CAP_PROP_FOCUS, args.manual_focus):
                print(f"set focus to {args.manual_focus}")
            else:
                print("failed to set focus")
        else:
            print("failed to disable autofocus")

    ##
    ## Flask Routes
    ##

    @app.route('/stream')
    def stream():
        return Response(capture_frame(single=False), mimetype='multipart/x-mixed-replace; boundary=frame')

    @app.route('/snapshot')
    def snapshot():
        return Response(capture_frame(single=True), mimetype='image/jpeg')

    ##
    ## Utility
    ##
    def capture_frame(single: bool = False):
        """
        Capture one or more frames from the camera.
        
        :param single: if True, capture a single frame and return it as a jpeg. otherwise, continuously capture frames and return them as a multipart/x-mixed-replace response.
        """

        while True:
            start_time = time.time()

            success, frame = camera.read()
            if not success:
                raise RuntimeError('Error capturing frame')
            
            # Perform image manipulations (flip and rotate as needed)
            if args.flip_horizontal:
                frame = cv2.flip(frame, 1)

            if args.flip_vertical:
                frame = cv2.flip(frame, 0)

            if args.rotate == 90:
                frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            elif args.rotate == 180:
                frame = cv2.rotate(frame, cv2.ROTATE_180)
            elif args.rotate == 270 or args.rotate == -90:
                frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

            # encode the frame as JPEG
            success, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), args.quality])
            if not success:
                raise RuntimeError('Error encoding frame')

            frame = buffer.tobytes()

            if single:
                # send single frame
                yield (frame)
                break
            else:
                # send multiple frames
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                
            # sleep to maintain target framerate
            if args.framerate > 0:
                elapsed_time = time.time() - start_time
                sleep_time = 1 / args.framerate - elapsed_time
                if sleep_time > 0:
                    time.sleep(sleep_time)

    # start flask
    app.run(host=args.listen, port=args.port)

if __name__ == "__main__":
    main()
