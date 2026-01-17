from templates.flip import create_flip_animation, create_quick_flip

# Horizontal flip between two emojis
frames = create_flip_animation(
    object1_data={'emoji': '😊', 'size': 120},
    object2_data={'emoji': '😂', 'size': 120},
    flip_axis='horizontal'
)

# Vertical flip
frames = create_flip_animation(flip_axis='vertical')

# Quick flip for emoji GIFs
frames = create_quick_flip('👍', '👎')