import subprocess
import os
import gc
import shutil
import argparse

from WhisPlay import WhisPlayBoard

def get_ffmpeg_cmd(video_path, width, height):
    model = "generic"
    try:
        with open('/proc/device-tree/model', 'r') as f:
            model = f.read().lower()
    except:
        pass

    input_args = []
    vf_params = f'scale={width}:{height}:flags=neighbor'

    if 'zero 2' in model or 'raspberry pi 3' in model:
        print(f"Device: {model.strip()} | Mode: Multi-thread")
        input_args = ['-threads', '4']
    elif 'zero' in model:
        print("Device: Pi Zero/W | Mode: HW Accel")
        input_args = ['-vcodec', 'h264_v4l2m2m']
    elif 'raspberry pi 4' in model or 'raspberry pi 5' in model:
        print(f"Device: {model.strip()} | Mode: High-perf")
        input_args = ['-threads', '4']
        vf_params = f'scale={width}:{height}:flags=bicubic'

    return ['ffmpeg'] + input_args + [
        '-i', video_path,
        '-vf', vf_params,
        '-vcodec', 'rawvideo',
        '-pix_fmt', 'rgb565be',
        '-f', 'rawvideo',
        '-loglevel', 'quiet',
        '-'
    ]

def play_video(video_path):
    board = WhisPlayBoard()
    board.set_backlight(100)
    board.set_rgb(0, 255, 0)  # Green LED while playing

    width, height = board.LCD_WIDTH, board.LCD_HEIGHT
    frame_size = width * height * 2
    buffer = bytearray(frame_size)

    def start_process():
        cmd = get_ffmpeg_cmd(video_path, width, height)
        print(f"CMD: {' '.join(cmd)}")
        return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=frame_size)

    process = start_process()

    gc.collect()
    gc.disable()

    print(f"Playing (loop): {video_path}. Press Ctrl+C to exit.")
    print(f"Frame size: {frame_size}, Display: {width}x{height}")
    frame_count = 0
    try:
        while True:
            read = process.stdout.readinto(buffer)
            if read != frame_size:
                print(f"Read {read} bytes, expected {frame_size}, restarting...")
                # reached EOF or error -> restart the ffmpeg process to loop
                try:
                    process.kill()
                except Exception:
                    pass
                try:
                    process.wait(timeout=1)
                except Exception:
                    pass
                # restart
                process = start_process()
                continue
            frame_count += 1
            if frame_count <= 3 or frame_count % 100 == 0:
                print(f"Frame {frame_count}")
            board.draw_image(0, 0, width, height, list(buffer))
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        try:
            process.kill()
        except Exception:
            pass
        try:
            process.wait(timeout=1)
        except Exception:
            pass
        gc.enable()
        board.set_rgb(0, 0, 0)  # Turn off LED
        board.cleanup()
        print("Exit.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', '-f', default=os.path.join(project_root, 'example/data', 'whisplay_test.mp4'))
    args = parser.parse_args()
    VIDEO_FILE = args.file

    if not shutil.which("ffmpeg"):
        print("Error: ffmpeg not found in PATH.")
        sys.exit(1)

    if os.path.exists(VIDEO_FILE):
        try:
            play_video(VIDEO_FILE)
        except Exception as e:
            print(f"Error: failed to play '{VIDEO_FILE}': {e}")
            sys.exit(1)
    else:
        print(f"Error: {VIDEO_FILE} not found.")
        sys.exit(1)