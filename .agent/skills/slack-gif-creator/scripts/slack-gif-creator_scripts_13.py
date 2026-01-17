from templates.slide import create_slide_animation, create_multi_slide

# Slide in from left with overshoot
frames = create_slide_animation(
    direction='left',
    slide_type='in',
    overshoot=True
)

# Slide across
frames = create_slide_animation(direction='left', slide_type='across')

# Multiple objects sliding in sequence
objects = [
    {'data': {'emoji': '🎯', 'size': 60}, 'direction': 'left', 'final_pos': (120, 240)},
    {'data': {'emoji': '🎪', 'size': 60}, 'direction': 'right', 'final_pos': (240, 240)}
]
frames = create_multi_slide(objects, stagger_delay=5)