from templates.kaleidoscope import apply_kaleidoscope, create_kaleidoscope_animation

# Apply to a single frame
kaleido_frame = apply_kaleidoscope(frame, segments=8)

# Or create animated kaleidoscope
frames = create_kaleidoscope_animation(
    base_frame=my_frame,  # or None for demo pattern
    num_frames=30,
    segments=8,
    rotation_speed=1.0
)

# Simple mirror effects (faster)
from templates.kaleidoscope import apply_simple_mirror

mirrored = apply_simple_mirror(frame, mode='quad')  # 4-way mirror
# modes: 'horizontal', 'vertical', 'quad', 'radial'