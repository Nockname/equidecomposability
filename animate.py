import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random
from main import create_pair_of_triangles
import string

def animate_triangles(frames=180, interval=40, pause_frames=30):
    
    initial_triangle, target_triangle = create_pair_of_triangles(area=10000)
    initial_triangle.triangle_to_triangle(target_triangle)

    # prepare plot
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_aspect('equal')
    ax.grid(True)

    total_frames = frames + pause_frames

    def update(frame):
        # Hold the initial triangle for `pause_frames` frames (t=0). After
        # that, interpolate t from 0->1 over `frames` frames.
        if frame < pause_frames:
            t = 0.0
            status = f"Initial Triangle"
        else:
            t = (frame - pause_frames) / float(frames - 1)
            status = f"Transformation ({t * 100:.2f}%)"
        # remove previous patches and lines safely
        for p in ax.patches[:]:
            p.remove()
        for ln in ax.lines[:]:
            ln.remove()

        # Use the stored rotation and translation from each part directly
        for i, part in enumerate(initial_triangle.parts):
            # get transformed points using the part's stored rotation/translation
            # the amount parameter interpolates: 0 = no transform, 1 = full transform
            pts = part.get_transformed_points(t)

            poly = plt.Polygon(pts, closed=True, alpha=0.5, color=plt.cm.tab10(i % 10))
            ax.add_patch(poly)
            pts_closed = pts + [pts[0]]
            x, y = zip(*pts_closed)
            ax.plot(x, y, color='k')

        # show status (either pause counter or normalized t)
        ax.set_title(f"{status}")


    return animation.FuncAnimation(fig, update, frames=total_frames, interval=interval, repeat=False)


if __name__ == '__main__':
    
    animation = animate_triangles(frames=200, interval=10, pause_frames=100)
    video = animation.to_html5_video()

    animation.save(f"equidecomposability_animation.mp4", writer='ffmpeg')