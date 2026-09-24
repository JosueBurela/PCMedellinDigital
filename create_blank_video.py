import base64

# This is a known tiny valid MP4 video (a few bytes) that is silent/blank.
# Actually, let's just make an extremely simple blank video using ffmpeg if installed,
# or just provide a base64 of a 1x1 blank gif? No, gifs don't always keep TVs awake.
# Let's check if ffmpeg is installed on the server.
